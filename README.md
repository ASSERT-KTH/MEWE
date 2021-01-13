## Fastly4Edge

This repo contains a research experiment for edge computing using the Fastly's Compute@Edge service. The code in the repo is an example of running custom Wasm binaries as a Fastly service. Go to [this post](https://www.jacarte.net/blog/2021/HandMadeWasmDeploInFastly/) to read more about how this example works.

### Prerequisites

- [fastly compute CLI tool](https://developer.fastly.com/learning/compute/)
- [Rust nightly](https://www.oreilly.com/library/view/rust-programming-by/9781788390637/e07dc768-de29-482e-804b-0274b4bef418.xhtml)
- A Fastly Compute@Edge account

## How to run it

`bash deploy.sh <service_id>`