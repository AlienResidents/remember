---
type: Infrastructure
description: "repos:"
resource: server/.pre-commit-config.yaml
timestamp: 2026-07-09T14:09:53Z
---

# .pre-commit-config

Source path: `server/.pre-commit-config.yaml`

## Content

```yaml
repos:
  - repo: local
    hooks:
      - id: okf-drift-detect
        name: OKF drift detection
        entry: okf/detect-drift.bash
        language: script
        files: '^okf/.*\.md$'
        pass_filenames: false
        description: Check OKF knowledge bundle for broken references and drift

```
