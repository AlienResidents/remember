---
type: Infrastructure
description: "apiVersion: networking.k8s.io/v1"
resource: k8s/base/ingress.yaml
timestamp: 2026-07-09T13:05:52Z
---

# ingress

Source path: `k8s/base/ingress.yaml`

## Content

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: remember-ingress
  labels:
    app: remember
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - remember.example.com
      secretName: remember-tls
  rules:
    - host: remember.example.com
      http:
        paths:
          - path: /mcp
            pathType: Prefix
            backend:
              service:
                name: remember-server
                port:
                  number: 8000

```
