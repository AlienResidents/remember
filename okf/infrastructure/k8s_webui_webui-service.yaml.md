---
type: Infrastructure
description: "apiVersion: v1"
resource: k8s/webui/webui-service.yaml
timestamp: 2026-07-10T02:44:32Z
---

# webui-service

Source path: `k8s/webui/webui-service.yaml`

## Content

```yaml
apiVersion: v1
kind: Service
metadata:
  name: remember-webui
  labels:
    app: remember-webui
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 3000
      protocol: TCP
      name: http
  selector:
    app: remember-webui

```
