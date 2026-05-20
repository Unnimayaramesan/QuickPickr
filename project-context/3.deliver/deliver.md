# QuickPickr — Deliver (Phase 3 epic artifact)

Deployment strategy, environments, rollback, and rollout status live in **[deployment-plan.md](./deployment-plan.md)**.

**Quick commands**

| Tier | Command |
|------|---------|
| Local native | `npm run dev` (see [README](../../README.md)) |
| Docker Compose | `docker compose up --build` or [`scripts/deploy/compose-up.ps1`](../../scripts/deploy/compose-up.ps1) |
| GCP example | [`scripts/deploy/cloud-run-query-service.example.sh`](../../scripts/deploy/cloud-run-query-service.example.sh) |

---

## Audit

| UTC | Persona | Action |
|-----|---------|--------|
| 2026-05-21 | DevOps | deliver.md + deployment-plan.md v1.0 |
