---
type: Infrastructure
description: "apiVersion: apps/v1"
resource: k8s/base/server-deployment.yaml
timestamp: 2026-07-09T13:05:52Z
---

# server-deployment

Source path: `k8s/base/server-deployment.yaml`

## Content

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: remember-server
  labels:
    app: remember
    component: server
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: remember
      component: server
  template:
    metadata:
      labels:
        app: remember
        component: server
    spec:
      containers:
        - name: server
          image: remember-server:latest
          ports:
            - containerPort: 8000
              name: http
              protocol: TCP
          env:
            - name: REMEMBER_DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: remember-secrets
                  key: database-url
            - name: REMEMBER_AUTH_DEV_MODE
              value: "false"
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8000
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

```
