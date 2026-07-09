---
type: Infrastructure
description: "{{- if .Values.server.pdb.enabled }}"
resource: helm/remember/templates/pdb.yaml
timestamp: 2026-07-09T14:09:52Z
---

# pdb

Source path: `helm/remember/templates/pdb.yaml`

## Content

```yaml
{{- if .Values.server.pdb.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ include "remember.fullname" . }}
  labels:
    {{- include "remember.labels" . | nindent 4 }}
spec:
  minAvailable: {{ .Values.server.pdb.minAvailable }}
  selector:
    matchLabels:
      {{- include "remember.selectorLabels" . | nindent 6 }}
{{- end }}

```
