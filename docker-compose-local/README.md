# docker-compose-local

A docker-compose file for deploying the application to a local environment.

The cluster must be provided with a `backend.env` with the following fields:

`DB_USERNAME`
`DB_PASSWORD`
`DB_HOST`
`DB_PORT`
`DB_NAME`
`ENCRYPT_SECRET_KEY`
`JWT_SECRET_KEY`
