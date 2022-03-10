# dev-ops-js

This folder contains infrastructure for deploying the application to a cloud environment, or for testing deployments locally. Individual folders contain their own READMEs explaining their purpose, and are also summarized here:

### data-producers

Scripts for populating the application with dummy data.

### docker-compose-ecs-js

A docker-compose file for deploying the application to Amazon's Elastic Container Service. Requires an established ECS context with the proper credentials, as well as an env file.

### docker-compose-local

A docker-compose file for deploying the application to a local environment. Requires an env file.

### k8-cloud

Configuration files for a kubernetes cluster that can be hosted on AWS. Requires eksctl with proper credentials, as well as a secret.yaml

### k8-local

Configuration files for a kubernetes cluster that can be run locally. Requires an exisitng cluster (created with minikube, for example), as well as a secret.yaml
