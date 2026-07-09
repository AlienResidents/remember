---
type: Infrastructure
description: "{{- if .Values.ingress.enabled -}}"
resource: helm/remember/templates/ingress.yaml
timestamp: 2026-07-09T13:05:52Z
---

# ingress

Source path: `helm/remember/templates/ingress.yaml`

## Content

```yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "remember.fullname" . }}
  labels:
    {{- include "remember.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className }}
  {{- end }}
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "remember.fullname" $ }}
                port:
                  number: {{ if eq .path "/mcp" }}{{ $.Values.server.port }}{{ else if eq .path "/" }}{{ $.Values.webui.port }}{{ else }}{{ $.Values.server.port }}{{ end }}
          {{- end }}
    {{- end }}
{{- end }}

```
