---
type: Infrastructure
description: "apiVersion: autoscaling/v2"
resource: k8s/base/hpa.yaml
timestamp: 2026-07-09T13:05:52Z
---

# hpa

Source path: `k8s/base/hpa.yaml`

## Content

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: remember-server-hpa
  labels:
    app: remember
    component: server
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: remember-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80

```
