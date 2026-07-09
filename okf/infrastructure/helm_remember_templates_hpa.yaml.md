---
type: Infrastructure
description: "{{- if .Values.server.autoscaling.enabled }}"
resource: helm/remember/templates/hpa.yaml
timestamp: 2026-07-09T14:09:52Z
---

# hpa

Source path: `helm/remember/templates/hpa.yaml`

## Content

```yaml
{{- if .Values.server.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "remember.fullname" . }}
  labels:
    {{- include "remember.labels" . | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "remember.fullname" . }}
  minReplicas: {{ .Values.server.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.server.autoscaling.maxReplicas }}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.server.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .Values.server.autoscaling.targetMemoryUtilizationPercentage }}
{{- end }}

```
