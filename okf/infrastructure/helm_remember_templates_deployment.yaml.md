---
type: Infrastructure
description: "apiVersion: apps/v1"
resource: helm/remember/templates/deployment.yaml
timestamp: 2026-07-09T01:43:38Z
---

# deployment

Source path: `helm/remember/templates/deployment.yaml`

## Content

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "remember.fullname" . }}
  labels:
    {{- include "remember.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.server.replicaCount }}
  {{- end }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      {{- include "remember.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "remember.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: server
          image: "{{ .Values.server.image.repository }}:{{ .Values.server.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.server.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.server.port }}
              name: http
              protocol: TCP
          env:
            - name: REMEMBER_DATABASE_URL
              value: {{ .Values.database.url | quote }}
            - name: REMEMBER_AUTH_DEV_MODE
              value: {{ .Values.auth.devMode | quote }}
            {{- range $key, $value := .Values.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
          resources:
            {{- toYaml .Values.server.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 10
            periodSeconds: 30
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          securityContext:
            runAsNonRoot: true
            runAsUser: 65534
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
        {{- if .Values.webui.enabled }}
        - name: webui
          image: "{{ .Values.webui.image.repository }}:{{ .Values.webui.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.webui.image.pullPolicy }}
          command: ["python", "-m", "remember.web"]
          ports:
            - containerPort: {{ .Values.webui.port }}
              name: webui
              protocol: TCP
          env:
            - name: REMEMBER_DATABASE_URL
              value: {{ .Values.database.url | quote }}
            - name: REMEMBER_AUTH_DEV_MODE
              value: {{ .Values.auth.devMode | quote }}
            {{- range $key, $value := .Values.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
          resources:
            {{- toYaml .Values.webui.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: /healthz
              port: webui
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /healthz
              port: webui
            initialDelaySeconds: 3
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 3
          securityContext:
            runAsNonRoot: true
            runAsUser: 65534
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
        {{- end }}

```
