# Authentication And Authorization

SentinelFlow uses email/password login with JWT bearer tokens for the API.
Every authenticated user belongs to one or more organizations through a
membership record.

## Roles

- `owner` can manage organization settings, workflows, and incidents.
- `admin` can manage workflows and incidents.
- `responder` can work incidents and assignments.
- `viewer` can read incidents but cannot mutate response state.

## Token Flow

1. A user registers with an organization name.
2. The API creates the user, organization, and owner membership.
3. Login returns an access token and refresh token.
4. Protected endpoints accept only access tokens (refresh tokens are rejected) and load the current user.
5. Organization-scoped endpoints check membership before applying RBAC.
6. `POST /auth/refresh` exchanges a refresh token for a new pair; the dashboard does this automatically on a 401.

## Security Notes

- Passwords are stored with bcrypt; tokens are HS256 JWTs signed with `JWT_SECRET` (32+ characters required in production).
- Login runs a bcrypt check even for unknown emails so timing doesn't reveal accounts, and failed logins are throttled per email and IP.
- Duplicate registrations return 409.
- API keys are scoped to a single organization and stored hashed.

