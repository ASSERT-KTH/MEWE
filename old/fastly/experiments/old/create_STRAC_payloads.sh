# Create STRAC payloads for fixed EDGE



# python3 -m rq3_execution_diversity.analyze_traces_pop rresults/rq3/execution_paths/libsodium/bin2base64.result.json bin2base64 instrumentedPureRandom libsodium results/rq1/maps/sodium.txt rq1\&2/results/libsodium/rq11.stability.json bma ams


python3 -m rq3_execution_diversity.analyze_traces rresults/rq3/execution_paths/libsodium/crypto_aead_chacha20poly1305_ietf_decrypt_detached.result.json crypto_aead_chacha20poly1305_ietf_decrypt_detached instrumentedPureRandom libsodium results/rq1/maps/sodium.txt rq1\&2/results/libsodium/rq11.stability.json

python3 -m rq3_execution_diversity.analyze_traces rresults/rq3/execution_paths/libsodium/bin2base64.result.json bin2base64 instrumentedPureRandom libsodium results/rq1/maps/sodium.txt rq1\&2/results/libsodium/rq11.stability.json


python3 -m rq3_execution_diversity.analyze_traces rresults/rq3/execution_paths/libsodium/crypto_aead_chacha20poly1305_ietf_encrypt_detached.result.json crypto_aead_chacha20poly1305_ietf_encrypt_detached instrumentedPureRandom libsodium results/rq1/maps/sodium.txt rq1\&2/results/libsodium/rq11.stability.json



python3 -m rq3_execution_diversity.analyze_traces rresults/rq3/execution_paths/libsodium/crypto_core_ed25519_scalar_random.result.json crypto_core_ed25519_scalar_random instrumentedPureRandom libsodium results/rq1/maps/sodium.txt rq1\&2/results/libsodium/rq11.stability.json


python3 -m rq3_execution_diversity.analyze_traces rresults/rq3/execution_paths/libsodium/crypto_core_ed25519_scalar_invert.result.json crypto_core_ed25519_scalar_invert instrumentedPureRandom libsodium results/rq1/maps/sodium.txt rq1\&2/results/libsodium/rq11.stability.json

