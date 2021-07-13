# Experiment on internet computing

The main idea is to use the dns targeting mechanism to send a different job to each PoP machine. For example, if we think about a map-reduce algorithm, we send a map operation to each available machine and we create a backend third-service for reducing.

## Backend send result

```rs

const BACKEND_NAME: &str = "third-service.com";

(&Method::GET, path) => {
    Ok(req.send(BACKEND_NAME)?)
}

```

## Use case, DTW

Send a DTW job task to each machine. In theory with 2000 machines the execution time should be decreased considerably. Test the approach with three strategies, 

1) load balancer relying.
    Call the service endpoint and rely on load balancing strategy to use the resources. Preliminary results: 67s for 100 traces between 50 and 1000 symbols per trace

2) manual redirection mechanism to PoP machines.
    Use Fastly dns to hit PoP machine with specific Job. Preliminary results: 26.48 for 100 traces between 50 and 1000 symbols per trace