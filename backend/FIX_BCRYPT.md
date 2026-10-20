# Fix for Bcrypt/Passlib Compatibility Issue

If you're getting an error like:
```
AttributeError: module 'bcrypt' has no attribute '__about__'
ValueError: password cannot be longer than 72 bytes
```

This is a compatibility issue between `passlib` and newer versions of `bcrypt` (4.0.0+).

## Quick Fix

**Step 1:** Stop the backend server (Ctrl+C)

**Step 2:** Uninstall and reinstall bcrypt with compatible version:

```bash
pip uninstall bcrypt -y
pip install "bcrypt>=3.2.0,<4.0.0"
```

**Step 3:** Restart the backend:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

## Alternative Fix (if above doesn't work)

If the issue persists, reinstall all dependencies:

```bash
pip uninstall bcrypt passlib -y
pip install -r requirements.txt
```

## Why This Happens

- `passlib` 1.7.4 expects bcrypt < 4.0.0
- Newer bcrypt versions (4.0.0+) removed some internal attributes that passlib relies on
- The fix pins bcrypt to a compatible version (< 4.0.0)

## Verification

After fixing, try registering a user again. The error should be gone.

