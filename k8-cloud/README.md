# k8-cloud 

Configuration files for a kubernetes cluster that can be hosted on AWS.

This cluster should be deployed via eksctl, with credentials provided. The cluster is also expecting a `secret.yaml`. The secret should belong to the namespace `eks-js` and use the name `secret`. It should provide base64 encoded values following fields satisfied:

`username`
`password`
`ENCRYPT_SECRET_KEY`
`JWT_SECRET_KEY`
