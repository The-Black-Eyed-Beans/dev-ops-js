# docker-compose-ecs-js

A docker-compose file for deploying the application to Amazon's Elastic Container Service.

The cluster should be deployed within an AWS ECS context with proper credentials and specified region. The cluster must be provided with a `backend.env` with the following fields:

`DB_USERNAME`
`DB_PASSWORD!`
`DB_HOST`
`DB_PORT`
`DB_NAME`
`ENCRYPT_SECRET_KEY`
`JWT_SECRET_KEY`
