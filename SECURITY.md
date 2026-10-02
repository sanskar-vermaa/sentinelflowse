# Security policy

## Reporting

Please use GitHub's **Report a vulnerability** button on the Security tab rather than a public issue.

## Design

- **Tenancy:** every record carries `organization_id`; every query filters by it, and membership plus role are checked on each request.
- **Passwords:** bcrypt. Login runs a hash check even for unknown emails and is throttled per email and IP.
- **Tokens:** HS256 JWTs with required `exp`, `sub` and `type`. Access tokens last 30 minutes; refresh tokens only work at `/auth/refresh`.
- **API keys:** random 256-bit secrets shown once, stored as bcrypt hashes, scoped to one organization.
- **Configuration:** `APP_ENV=production` refuses to start with a weak `JWT_SECRET` and hides the interactive docs.
- **Headers:** nosniff, frame denial, no-referrer and no-store on API responses; CORS limited to `WEB_ORIGIN`.
- **AI:** incident data sent to Gemini is labelled as data; output is advisory and never changes incident state.

## Known limitations

- The login throttle is in-process; with several API instances, add a gateway limit or move it to Redis.
- The dashboard keeps tokens in `localStorage`.
