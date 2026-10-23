---
title: Deploy Runbook
department: Engineering
classification: internal
---
# Deploy Runbook

## Deploy windows
- Deploys are allowed Monday to Thursday, 09:00–16:00 Helsinki time.
- Deploy freeze on Fridays after 14:00 and on public holidays.

## How to deploy
Run `nwctl deploy --service <name> --env production` after the pull request is merged and CI is green.

## How to roll back
Run `nwctl rollback --service <name>` to return to the previous release. Rollbacks are always allowed, even during a freeze.

## Checks
Watch the service dashboard for 15 minutes after every production deploy.
