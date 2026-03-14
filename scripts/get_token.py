from src.api.auth import create_access_token
from datetime import timedelta

# Create a master token for CLI tests
token = create_access_token(
    data={"sub": "admin_cli", "tenant_id": "PDS"}, # Mocking Sovereign local user
    expires_delta=timedelta(minutes=60)
)

print(token)
