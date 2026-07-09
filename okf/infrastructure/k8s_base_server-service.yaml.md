---
type: Infrastructure
description: "apiVersion: v1"
resource: k8s/base/server-service.yaml
timestamp: 2026-07-09T14:09:53Z
---

# server-service

Source path: `k8s/base/server-service.yaml`

## Content

```yaml
apiVersion: v1
kind: Service
metadata:
  name: remember-server
  labels:
    app: remember
    component: server
spec:
  type: ClusterIP
  ports:
    - port: 8000
      targetPort: 8000
      protocol: TCP
      name: http
  selector:
    app: remember
    component: server

```
