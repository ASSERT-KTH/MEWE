

python3 -m rq3_execution_diversity.hash_all run_qr_str rq3_execution_diversity/results/qrcode/fmap.txt rq1\&2/results/qrcode/rq11_qrcode_.stability.json

python3 -m rq3_execution_diversity.hash_all run_qr rq3_execution_diversity/results/qrcode/fmap.txt rq1\&2/results/qrcode/rq11_qrcode_.stability.json

exit 0

python3 -m rq3_execution_diversity.analyze_traces_pop rq3_execution_diversity/results/libsodium/from_pops/crypto_aead_chacha20poly1305_ietf_decrypt_detached.result.json crypto_aead_chacha20poly1305_ietf_decrypt_detached instrumentedPureRandom libsodium rq3_execution_diversity/results/libsodium/fmap.txt rq1\&2/results/libsodium/rq11.stability.json bma ams

python3 -m rq3_execution_diversity.analyze_traces_pop rq3_execution_diversity/results/libsodium/from_pops/crypto_aead_chacha20poly1305_ietf_decrypt_detached.result.json crypto_aead_chacha20poly1305_ietf_decrypt_detached instrumentedPureRandom libsodium rq3_execution_diversity/results/libsodium/fmap.txt rq1\&2/results/libsodium/rq11.stability.json bma ams

python3 -m rq3_execution_diversity.analyze_traces_pop rq3_execution_diversity/results/libsodium/from_pops/bin2base64.result.json bin2base64 instrumentedPureRandom libsodium rq3_execution_diversity/results/libsodium/fmap.txt rq1\&2/results/libsodium/rq11.stability.json bma ams

python3 -m rq3_execution_diversity.analyze_traces_pop rq3_execution_diversity/results/libsodium/from_pops//crypto_aead_chacha20poly1305_ietf_encrypt_detached.result.json crypto_aead_chacha20poly1305_ietf_encrypt_detached instrumentedPureRandom libsodium rq3_execution_diversity/results/libsodium/fmap.txt rq1\&2/results/libsodium/rq11.stability.json bma ams

python3 -m rq3_execution_diversity.analyze_traces_pop rq3_execution_diversity/results/libsodium/from_pops/crypto_core_ed25519_scalar_random.result.json crypto_core_ed25519_scalar_random instrumentedPureRandom libsodium rq3_execution_diversity/results/libsodium/fmap.txt rq1\&2/results/libsodium/rq11.stability.json bma ams

python3 -m rq3_execution_diversity.analyze_traces_pop rq3_execution_diversity/results/libsodium/from_pops/crypto_core_ed25519_scalar_invert.result.json crypto_core_ed25519_scalar_invert instrumentedPureRandom libsodium rq3_execution_diversity/results/libsodium/fmap.txt rq1\&2/results/libsodium/rq11.stability.json bma ams

exit 0



