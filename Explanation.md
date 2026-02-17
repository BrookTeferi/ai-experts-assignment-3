# Bug Explanation

## What was the bug?

When `oauth2_token` is a dictionary (not `None` and not an `OAuth2Token` instance), the code does not refresh the token before making API requests. This causes API requests to fail authentication because no Authorization header is set when the token is a dict.

## Why did it happen?

The refresh condition in `app/http_client.py` was:
```python
if not self.oauth2_token or (isinstance(self.oauth2_token, OAuth2Token) and self.oauth2_token.expired):
```

When `oauth2_token` is a dict:
- `not self.oauth2_token` evaluates to `False` (dicts are truthy)
- `isinstance(self.oauth2_token, OAuth2Token)` is `False`
- The entire condition evaluates to `False`, so refresh never happens
- The subsequent `isinstance` check also fails, so no Authorization header is added

## Why does your fix solve it?

The fix changes the condition to:
```python
if not self.oauth2_token or not isinstance(self.oauth2_token, OAuth2Token) or self.oauth2_token.expired:
```

Now the logic correctly handles three cases:
1. Token is `None` → refresh
2. Token is not an `OAuth2Token` instance (i.e., it's a dict) → refresh
3. Token is an `OAuth2Token` and expired → refresh

This ensures that any non-`OAuth2Token` value (including dicts) triggers a refresh, which is the intended behavior.

## One realistic case / edge case your tests still don't cover

The tests don't cover the case where `oauth2_token` is set to an unexpected type other than `None`, `dict`, or `OAuth2Token` (e.g., a string, integer, or custom object). While the fix would refresh in these cases (which is likely the desired behavior), there's no explicit test verifying this behavior. In a production system, you might want to add validation or logging when encountering unexpected token types.
