import time
from app.http_client import Client

# This should fail - no Authorization header added
c = Client()
c.oauth2_token = {"access_token": "valid", "expires_at": int(time.time()) + 3600}

resp = c.request("GET", "/me", api=True)
print("Authorization header:", resp["headers"].get("Authorization"))
# Expected: "Bearer valid" 
# Actual: None (BUG!)
