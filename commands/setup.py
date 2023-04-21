import base64
from datetime import datetime, timezone
import hashlib
import secrets


def cmd_setup(**kwargs):
    created_at = int(datetime.now(timezone.utc).timestamp() * 1000)
    token_bytes = secrets.token_bytes(64)
    token_digest = hashlib.sha256()
    token_digest.update(token_bytes)
    token_digest_hex = token_digest.hexdigest()
    token = base64.b64encode(token_bytes).decode("ascii")

    print(f"""Following the instructions below will create your first access token in order to use the Build Center API.

Executing the following SQL statement in your Build Center database will save the access token with full admin privileges.

    insert into access_token (uuid, value_digest, created_at, enabled, access) values (
        'initial', unhex('{token_digest_hex}'),
        {created_at}, 1, 7);

This is your access token:

    {token}

You can use this token with the Build Center CLI tool by setting the BC_TOKEN environment variable.
""")
