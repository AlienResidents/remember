---
type: Infrastructure
description: "apiVersion: apps/v1"
resource: k8s/webui/webui-deployment.yaml
timestamp: 2026-07-09T13:54:49Z
---

# webui-deployment

Source path: `k8s/webui/webui-deployment.yaml`

## Content

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: remember-webui
  labels:
    app: remember-webui
spec:
  replicas: 1
  selector:
    matchLabels:
      app: remember-webui
  template:
    metadata:
      labels:
        app: remember-webui
    spec:
      containers:
        - name: webui
          image: remember-server:latest
          command: ["python", "-m", "remember.web"]
          ports:
            - containerPort: 3000
              name: http
              protocol: TCP
          env:
            - name: REMEMBER_DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: remember-secret
                  key: database-url
            - name: REMEMBER_AUTH_DEV_MODE
              value: "false"
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 128Mi
          livenessProbe:
            httpGet:
              path: /healthz
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /healthz
              port: 3000
            initialDelaySeconds: 3
            periodSeconds: 5
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            readOnlyRootFilesystem: true
            allowPrivilegeEscalation: false
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}

```
