#python3 -m rq1o2.report_stability rq1o2/results/qrcode/rq11_qrcode_.stability.json

python3 -m rq1o2.dfs_count2 results/rq2/preservation/qrcode/rq11_qrcode_.stability.json results/rq1/maps/qrcode.txt db  run_qr

python3 -m rq1o2.dfs_count2 results/rq2/preservation/qrcode/rq11_qrcode_.stability.json results/rq1/maps/qrcode.txt db run_qr_str

python3 -m rq1o2.dfs_count2 results/rq2/preservation/libsodium/rq11.stability.json results/rq1/maps/sodium.txt file results/rq3/execution_paths/libsodium/bin2base64.result.json    bin2base64 


python3 -m rq1o2.dfs_count2 results/rq2/preservation/libsodium/rq11.stability.json results/rq1/maps/sodium.txt file results/rq3/execution_paths/libsodium/crypto_aead_chacha20poly1305_ietf_decrypt_detached.result.json    crypto_aead_chacha20poly1305_ietf_decrypt_detached 



python3 -m rq1o2.dfs_count2 results/rq2/preservation/libsodium/rq11.stability.json results/rq1/maps/sodium.txt file results/rq3/execution_paths/libsodium/crypto_aead_chacha20poly1305_ietf_encrypt_detached.result.json    crypto_aead_chacha20poly1305_ietf_encrypt_detached 



python3 -m rq1o2.dfs_count2 results/rq2/preservation/libsodium/rq11.stability.json results/rq1/maps/sodium.txt file results/rq3/execution_paths/libsodium/crypto_core_ed25519_scalar_invert.result.json    crypto_core_ed25519_scalar_invert


python3 -m rq1o2.dfs_count2 results/rq2/preservation/libsodium/rq11.stability.json results/rq1/maps/sodium.txt file results/rq3/execution_paths/libsodium/crypto_core_ed25519_scalar_random.result.json    crypto_core_ed25519_scalar_random
