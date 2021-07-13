## Get original CF
`MATCH p=(start {name:'crypto_core_ed25519_scalar_complement_entry'})-[:ST*]->(k {name: 'crypto_core_ed25519_scalar_complement_end'}) return p`

## Results

### Original
|   |   |   |   |   |
|---|---|---|---|---|
|Name                                   | Nodes | Edges | Cyclomatic | Unique paths | 
| bin2base64 | 5 | 5 | 2 | 1 |
| crypto_aead_chacha20poly1305_ietf_decrypt_detached | 26 | 39 | 15 | 3 |
| crypto_aead_chacha20poly1305_ietf_encrypt_detached | 27 | 41 | 16 | 4 |
| crypto_core_ed25519_scalar_random | 10 | 12 | 4 | 2 |
| crypto_core_ed25519_scalar_invert | 10 | 15 | 7 | 1 |
| crypto_core_ed25519_scalar_complement | 7 | 9 | 4 | 1 |


### Wasm
|   |   |   |   |   |
|---|---|---|---|---|
|Name                                   | Nodes | Edges | Cyclomatic | Unique paths | 
| bin2base64 | 46 | 87 | 43 | 42 |
| crypto_aead_chacha20poly1305_ietf_decrypt_detached | 142 | 271 | 131 | 162 |
| crypto_aead_chacha20poly1305_ietf_encrypt_detached | 49 | 85 | 38 | 15 |
| crypto_core_ed25519_scalar_random | 77 | 146 | 71 | 2296 |
| crypto_core_ed25519_scalar_invert | 77 | 149 | 74 | 1148 |
| crypto_core_ed25519_scalar_complement | 62 | 119 | 59 | 56 |


### x86
|   |   |   |   |   |
|---|---|---|---|---|
|Name                                   | Nodes | Edges | Cyclomatic | Unique paths | 
| bin2base64 | 45 | 85 | 42 | 41 |
| crypto_aead_chacha20poly1305_ietf_decrypt_detached | 138 | 263 | 127 | 130 |
| crypto_aead_chacha20poly1305_ietf_encrypt_detached | 46 | 79 | 35 | 13 |
| crypto_core_ed25519_scalar_random | 77 | 146 | 71 | 2296 |
| crypto_core_ed25519_scalar_invert | 76 | 147 | 73 | 1107 |
| crypto_core_ed25519_scalar_complement | 62 | 119 | 59 | 56 |