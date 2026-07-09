---
type: Infrastructure
description: "  replicaCount: 2"
resource: helm/remember/values.yaml
timestamp: 2026-07-09T14:09:52Z
---

# values

Source path: `helm/remember/values.yaml`

## Content

```yaml
# Default values for remember.
# This is a YAML-formatted file.

server:
  replicaCount: 2
  image:
    repository: remember-server
    pullPolicy: IfNotPresent
    tag: ""  # Overrides the image tag whose default is the chart appVersion.
  port: 8000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
  pdb:
    enabled: true
    minAvailable: 1

auth:
  devMode: false
  github:
    enabled: false
    clientId: ""
    clientSecret: ""
  apiKey:
    enabled: true
  providers: []  # Additional auth providers

database:
  url: ""  # Override with full connection string
  # Or use external database:
  # host: ""
  # port: 5432
  # name: remember
  # user: ""
  # password: ""

ingress:
  enabled: true
  className: nginx
  annotations: {}
  hosts:
    - host: remember.local
      paths:
        - path: /mcp
          pathType: Prefix
  tls: []
  #  - secretName: remember-tls
  #    hosts:
  #      - remember.local

# Additional environment variables
env: {}
#  REMEMBER_SEARCH_TYPE: fulltext
#  REMEMBER_STALENESS_THRESHOLD_DAYS: "90"

# Web UI
defaultIndex: true
webui:
  enabled: true
  replicaCount: 1
  image:
    repository: remember-server
    pullPolicy: IfNotPresent
    tag: ""
  port: 3000
  resources:
    limits:
      cpu: 200m
      memory: 128Mi
    requests:
      cpu: 50m
      memory: 64Mi
  ingress:
    enabled: false
    className: nginx
    annotations: {}
    hosts:
      - host: remember.local
        paths:
          - path: /
            pathType: Prefix
    tls: []

# Node selector
nodeSelector: {}

# Tolerations
tolerations: []

# Affinity
affinity: {}

```
