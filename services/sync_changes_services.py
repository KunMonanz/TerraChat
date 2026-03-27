import logging
from typing import Any, Dict, Tuple
from collections import defaultdict

from tortoise import transactions, Tortoise
from models.local.changes_model import Changes
from db.tortoise_config import TORTOISE_ORM

logger = logging.getLogger(__name__)


class SyncService:
    HANDLER_MAP = {
        "CREATE": "_handle_create",
        "UPDATE": "_handle_update",
        "DELETE": "_handle_delete",
    }

    def __init__(self):
        self._model_cache: Dict[str, Tuple[Any, str]] = {}

    async def sync(self, user_id: str, cloud_user_id: str) -> dict[str, int]:
        stats = {"success": 0, "failed": 0}

        pending = await Changes.filter(
            user_id=user_id,
            used=False
        ).order_by("created_at")

        if not pending:
            return stats

        # Group by DB connection
        groups = defaultdict(list)

        for change in pending:
            try:
                model_class, connection_name = await self._resolve_model(change.model)
                groups[connection_name].append((change, model_class))
            except Exception as e:
                logger.error(f"Resolve error {change.id}: {e}")
                stats["failed"] += 1

        successful_ids = []

        # Process per DB (no fake atomicity across DBs)
        for connection_name, items in groups.items():
            for change, model_class in items:
                try:
                    handler_name = self.HANDLER_MAP.get(change.change_type)
                    if not handler_name:
                        raise ValueError(
                            f"Unknown change_type: {change.change_type}"
                        )

                    payload = change.payload.copy()
                    payload = self._remap_user_id(
                        payload, user_id, cloud_user_id)

                    handler = getattr(self, handler_name)
                    await handler(model_class, payload, change.model)

                    successful_ids.append(change.id)
                    stats["success"] += 1

                except Exception as e:
                    logger.error(f"Sync failed {change.id}: {e}")
                    stats["failed"] += 1

        # Persist success
        if successful_ids:
            await Changes.filter(id__in=successful_ids).update(used=True)

        return stats

    # ---------------------------
    # Handlers
    # ---------------------------

    async def _handle_create(self, model_class, payload: dict, model_name: str):
        pk_field = model_class._meta.pk_attr
        pk_value = payload.get(pk_field)

        # Try update first (idempotent behavior)
        if pk_value:
            exists = await model_class.filter(**{pk_field: pk_value}).exists()
            if exists:
                update_data = {k: v for k,
                               v in payload.items() if k != pk_field}
                await model_class.filter(**{pk_field: pk_value}).update(**update_data)
                return

        # fallback create
        await model_class.create(**payload)

    async def _handle_update(self, model_class, payload: dict, model_name: str):
        payload = payload.copy()

        pk_field = model_class._meta.pk_attr
        pk_value = payload.pop(pk_field, None) or payload.pop("id", None)

        if not pk_value:
            raise ValueError(
                f"Missing PK '{pk_field}' for model '{model_name}'"
            )

        await model_class.filter(**{pk_field: pk_value}).update(**payload)

    async def _handle_delete(self, model_class, payload: dict, model_name: str):
        pk_field = model_class._meta.pk_attr
        pk_value = payload.get(pk_field) or payload.get("id")

        if not pk_value:
            raise ValueError(
                f"Payload missing PK for delete on '{model_name}'"
            )

        if "is_deleted" in model_class._meta.fields_map:
            # Soft delete
            await model_class.filter(**{pk_field: pk_value}).update(
                is_deleted=True
            )
        else:
            # Hard delete
            await model_class.filter(**{pk_field: pk_value}).delete()

    # ---------------------------
    # Utilities
    # ---------------------------

    def _remap_user_id(
        self,
        payload: dict,
        local_user_id: str,
        cloud_user_id: str
    ) -> dict:
        for field in ("user_id", "user", "created_by", "owner_id"):
            if field in payload and str(payload[field]) == local_user_id:
                payload[field] = cloud_user_id
        return payload

    async def _resolve_model(self, model_name: str) -> tuple:
        # Cache lookup
        if model_name in self._model_cache:
            return self._model_cache[model_name]

        for app_name, app_models in Tortoise.apps.items():
            for cls_name, model_class in app_models.items():
                if (
                    cls_name.lower() == model_name.lower()
                    or model_class._meta.db_table == model_name
                ):
                    connection_name = TORTOISE_ORM["apps"][app_name]["default_connection"]

                    self._model_cache[model_name] = (
                        model_class, connection_name)
                    return model_class, connection_name

        raise ValueError(f"Model '{model_name}' not found")
