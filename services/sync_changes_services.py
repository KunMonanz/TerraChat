import logging
from typing import Any
from tortoise import transactions, Tortoise
from db.tortoise_config import TORTOISE_ORM
from models.local.changes_model import Changes

logger = logging.getLogger(__name__)


class SyncService:
    HANDLER_MAP = {
        "CREATE": "_handle_create",
        "UPDATE": "_handle_update",
        "DELETE": "_handle_delete",
    }

    def __init__(
        self,
        local_to_cloud_user_id: dict[str, str] | None = None
    ):
        self.local_to_cloud_user_id = local_to_cloud_user_id or {}

    async def sync(
        self,
        user_id: str,
        cloud_user_id: str
    ) -> dict[str, int]:
        stats = {
            "success": 0,
            "failed": 0
        }
        self.local_to_cloud_user_id[user_id] = cloud_user_id

        pending = await Changes.filter(
            user_id=user_id,
            used=False
        ).order_by("created_at")

        if not pending:
            return stats

        # Group changes by their target connection (sqlite vs postgres)
        # so we can batch them per-connection in one transaction
        from collections import defaultdict
        groups: dict[str, list[Changes]] = defaultdict(list)

        for change in pending:
            try:
                model_class, connection_name = await self._resolve_model(change.model)
                groups[connection_name].append((change, model_class))
            except Exception as e:
                logger.error(
                    f"Failed to resolve model for change {change.id}: {e}")
                stats["failed"] += 1

        # Process each connection group in a single transaction
        for connection_name, items in groups.items():
            async with transactions.in_transaction(connection_name):
                for change, model_class in items:
                    try:
                        handler_name = self.HANDLER_MAP.get(change.change_type)
                        if not handler_name:
                            raise ValueError(
                                f"Unknown change_type: {change.change_type}"
                            )

                        payload = self._remap_user_id(change.payload.copy())
                        handler = getattr(self, handler_name)
                        await handler(model_class, payload, change.model)

                        change.used = True
                        stats["success"] += 1

                    except Exception as e:
                        logger.error(f"Failed to sync change {change.id}: {e}")
                        stats["failed"] += 1

        # Bulk-mark all successful changes as used in one query
        success_ids = [
            change.id
            for change, _ in [item for group in groups.values() for item in group]
            if change.used
        ]
        if success_ids:
            await Changes.filter(id__in=success_ids).update(used=True)

        return stats

    def _remap_user_id(self, payload: dict) -> dict:
        for field in ("user_id", "user", "created_by", "owner_id"):
            if field in payload:
                local_uid = str(payload[field])
                if local_uid in self.local_to_cloud_user_id:
                    payload[field] = self.local_to_cloud_user_id[local_uid]
                else:
                    logger.warning(
                        f"No cloud mapping found for {field}={local_uid}")
        return payload

    async def _handle_create(
        self,
        model_class,
        payload: dict[str, Any],
        model_name: str
    ) -> None:
        pk_field = model_class._meta.pk_attr
        pk_value = payload.get(pk_field)

        if pk_value and await model_class.filter(**{pk_field: pk_value}).exists():
            update_data = {k: v for k, v in payload.items() if k != pk_field}
            await model_class.filter(**{pk_field: pk_value}).update(**update_data)
            return

        unique_fields = [
            f.model_field_name
            for f in model_class._meta.fields_map.values()
            if getattr(f, "unique", False) and f.model_field_name != pk_field
        ]
        for uf in unique_fields:
            if uf in payload and await model_class.filter(**{uf: payload[uf]}).exists():
                update_data = {
                    k: v for k,
                    v in payload.items() if k != pk_field
                }
                await model_class.filter(**{uf: payload[uf]}).update(**update_data)
                logger.debug(f"Upserted {model_name} by unique field '{uf}'")
                return

        await model_class.create(**payload)

    async def _handle_update(
        self,
        model_class,
        payload: dict[str, Any],
        model_name: str
    ) -> None:
        payload = payload.copy()
        pk_field = model_class._meta.pk_attr

        pk_value = payload.pop(pk_field, None) or payload.pop("id", None)
        if not pk_value:
            raise ValueError(
                f"Payload missing PK '{pk_field}' for model '{model_name}'. "
                f"Keys present: {list(payload.keys())}"
            )

        await model_class.filter(**{pk_field: pk_value}).update(**payload)

    async def _handle_delete(
        self,
        model_class,
        payload: dict[str, Any],
        model_name: str
    ) -> None:

        pk_field = model_class._meta.pk_attr
        pk_value = payload.get(pk_field) or payload.get("id")
        if not pk_value:
            raise ValueError(
                f"Payload missing PK for delete on '{model_name}'")
        await model_class.filter(**{pk_field: pk_value}).delete()

    async def _resolve_model(self, model_name: str) -> tuple:
        for app_name, app_models in Tortoise.apps.items():
            for cls_name, model_class in app_models.items():
                if (
                    cls_name.lower() == model_name.lower()
                    or model_class._meta.db_table == model_name
                ):
                    connection_name = TORTOISE_ORM["apps"][app_name]["default_connection"]
                    return model_class, connection_name
        raise ValueError(f"Model '{model_name}' not found in registered apps")
