from datetime import datetime, timedelta, timezone
import uuid

import jwt


payload = {
    "sub": "test",
    "jti": str(uuid.uuid4()),
    "exp": datetime.now(timezone.utc) + timedelta(hours=24)
}
print("before: ", payload)
token = jwt.encode(payload, "secret", algorithm="HS256")
decoded = jwt.decode(token, "secret", algorithms=["HS256"])
print("after: ", decoded)
