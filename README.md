## MEWE research repository

### Folders structure:
 - experiments: scripts for experimentation reproduction
 - link_sodium, link_captcha, link_image, link_qrcode: MEWE pipelines. 
 - crow-linker: The MEWE mulrivariant generator.
 
 ### MEWE multivariants:

Each pipeline folder contains the corresponding bash script to collect intermediate bitcodes from rustc (e.g. ./rust/build.py). The collected intermediate bitcodes need to be sent to CROW for diversification. After collecting the diversified modules, run thee script `build_multivariant.sh <original bitcode> <crow-linker binary folder> <diversified bitcodes folder> `. The final step is to run the examples. Inside the folder `rust/example`, run the script `build.sh` and collect the Wasm binary.
