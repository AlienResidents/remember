---
type: Infrastructure
description: "apiVersion: v1"
resource: helm/remember/templates/service.yaml
timestamp: 2026-07-09T01:43:38Z
---

# service

Source path: `helm/remember/templates/service.yaml`

## Content

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "remember.fullname" . }}
  labels:
    {{- include "remember.labels" . | nindent 4 }}
spec:
  type: ClusterIP
  ports:
    - port: {{ .Values.server.port }}
      targetPort: http
      protocol: TCP
      name: http
    {{- if .Values.webui.enabled }}
    - port: {{ .Values.webui.port }}
      targetPort: webui
      protocol: TCP
      name: webui
    {{- end }}
  selector:
    {{- include "remember.selectorLabels" . | nindent 4 }}

```
