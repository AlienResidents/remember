---
type: Infrastructure
description: "name: OKF Drift Detection"
resource: server/.github/workflows/okf-drift.yml
timestamp: 2026-07-09T13:05:52Z
---

# okf-drift

Source path: `server/.github/workflows/okf-drift.yml`

## Content

```yaml
name: OKF Drift Detection

on:
  push:
    paths:
      - 'okf/**'
  pull_request:
    paths:
      - 'okf/**'
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 06:00 UTC

jobs:
  detect-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Detect OKF drift
        run: ./okf/detect-drift.bash

```
