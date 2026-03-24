# Run this once as a management script or temporary endpoint
from models.local.changes_model import Changes


async def purge_bad_changes():
    # Delete user UPDATE changes missing 'id' in payload
    bad_user_updates = await Changes.filter(
        model="users",
        change_type="UPDATE",
        used=False,
    )
    for change in bad_user_updates:
        if "id" not in change.payload:
            await change.delete()
            print(f"Deleted bad user change: {change.id}")

    # Delete question CREATE changes missing 'user_id' in payload
    bad_question_creates = await Changes.filter(
        model="questions",
        change_type="CREATE",
        used=False,
    )
    for change in bad_question_creates:
        if "user_id" not in change.payload:
            await change.delete()
            print(f"Deleted bad question change: {change.id}")
