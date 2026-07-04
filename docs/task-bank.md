# Silver Task Bank

Future tasks should be realistic, scoped, and tied to production behavior.

## Candidate Tasks

1. Prevent duplicate incidents when two workers process alerts with the same dedupe key.
2. Fix RBAC so viewers cannot assign incidents.
3. Ensure archived incidents are excluded from default incident search.
4. Add idempotency to workflow retries after transient failures.
5. Correct severity downgrade rules after an incident is acknowledged.
6. Fix timeline ordering when events are created in different time zones.
7. Rotate API keys without invalidating unrelated organization keys.
8. Prevent stale cached incident counts after status changes.
9. Add pagination stability for incident lists sorted by severity and update time.
10. Ensure failed notification jobs are visible in workflow run output.
11. Stop webhook signature validation from accepting expired timestamps.
12. Add audit records for manual severity changes.
13. Prevent cross-organization alert grouping by fingerprint.
14. Fix worker timeout handling for long AI triage requests.
15. Add integration tests for alert ingest and incident creation.

