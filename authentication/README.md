# authentication/

JWT auth, 2FA, RBAC, and the encrypted credential vault, built out in
**Phase 2**.

```
authentication/
  jwt.py          Access/refresh token issuance & verification
  password.py     Password hashing (bcrypt via passlib)
  totp.py         TOTP-based 2FA enrollment/verification (pyotp)
  rbac.py         Role-based access control (admin / trader / viewer)
  vault.py        Fernet/AES-GCM encryption for broker credentials & API
                  keys, keyed from CREDENTIAL_ENCRYPTION_KEY (never stored
                  in plaintext in the database)
  rate_limit.py   Redis-backed rate limiting for auth endpoints
```
