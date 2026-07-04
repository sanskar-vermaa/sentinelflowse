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
4. Protected endpoints decode the bearer token and load the current user.
5. Organization-scoped endpoints check membership before applying RBAC.

## Security Notes

- Passwords are stored with bcrypt.
- AI triage and workflow automation must never bypass RBAC.
- Future API key access is scoped to a single organization.

