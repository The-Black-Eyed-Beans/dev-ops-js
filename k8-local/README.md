# k8-local 

Configuration files for a kubernetes cluster that can be deployed locally.

These deployment files should be applied to an existing cluster, which can be created using a tool like minikube. The cluster is also expecting a `secret.yaml`. The secret should belong to the namespace `eks-js` and use the name `secret`. It should provide base64 encoded values following fields satisfied:

`username`
`password`
`ENCRYPT_SECRET_KEY`
`JWT_SECRET_KEY`
