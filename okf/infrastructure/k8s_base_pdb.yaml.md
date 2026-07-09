---
type: Infrastructure
description: "apiVersion: policy/v1"
resource: k8s/base/pdb.yaml
timestamp: 2026-07-09T14:09:52Z
---

# pdb

Source path: `k8s/base/pdb.yaml`

## Content

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: remember-server-pdb
  labels:
    app: remember
    component: server
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: remember
      component: server

```
