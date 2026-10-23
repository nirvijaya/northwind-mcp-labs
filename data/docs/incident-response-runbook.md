---
title: Incident Response Runbook
department: Engineering
classification: internal
---
# Incident Response Runbook

## Severity levels
- Sev1: customer-facing outage or data loss. Page the on-call engineer within 5 minutes.
- Sev2: major feature degraded. Notify on-call within 30 minutes.
- Sev3: minor issue. Create a ticket; no page.

## During a Sev1
1. Open an incident channel named #inc-YYYYMMDD-short-name.
2. Assign an incident commander.
3. Update the public status page every 30 minutes.
4. Follow the Deploy Runbook if a rollback is needed.

## After
Write a blameless postmortem within 5 business days.
