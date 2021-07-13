#python3 -m rq1\&2.report_stability rq1\&2/results/qrcode/rq11_qrcode_.stability.json

python3 -m rq1\&2.dfs_count2 rq1\&2/results/libsodium/rq11.stability.json rq3_execution_diversity/results/libsodium/fmap.txt file rq3_execution_diversity/results/libsodium/from_pops/bin2base64.result.json    bin2base64 


python3 -m rq1\&2.dfs_count2 rq1\&2/results/libsodium/rq11.stability.json rq3_execution_diversity/results/libsodium/fmap.txt file rq3_execution_diversity/results/libsodium/from_pops/crypto_aead_chacha20poly1305_ietf_decrypt_detached.result.json    crypto_aead_chacha20poly1305_ietf_decrypt_detached 



python3 -m rq1\&2.dfs_count2 rq1\&2/results/libsodium/rq11.stability.json rq3_execution_diversity/results/libsodium/fmap.txt file rq3_execution_diversity/results/libsodium/from_pops/crypto_aead_chacha20poly1305_ietf_encrypt_detached.result.json    crypto_aead_chacha20poly1305_ietf_encrypt_detached 



python3 -m rq1\&2.dfs_count2 rq1\&2/results/libsodium/rq11.stability.json rq3_execution_diversity/results/libsodium/fmap.txt file rq3_execution_diversity/results/libsodium/from_pops/crypto_core_ed25519_scalar_invert.result.json    crypto_core_ed25519_scalar_invert


python3 -m rq1\&2.dfs_count2 rq1\&2/results/libsodium/rq11.stability.json rq3_execution_diversity/results/libsodium/fmap.txt file rq3_execution_diversity/results/libsodium/from_pops/crypto_core_ed25519_scalar_random.result.json    crypto_core_ed25519_scalar_random


python3 -m rq1\&2.dfs_count2 rq1\&2/results/qrcode/rq11_qrcode_.stability.json rq3_execution_diversity/results/qrcode/fmap.txt db  run_qr

python3 -m rq1\&2.dfs_count2 rq1\&2/results/qrcode/rq11_qrcode_.stability.json rq3_execution_diversity/results/qrcode/fmap.txt db run_qr_str


exit 0

python3 -m rq1\&2.dfs_count rq1\&2/results/qrcode/rq11_qrcode_.stability.json run_qr 11
python3 -m rq1\&2.dfs_count rq1\&2/results/qrcode/rq11_qrcode_.stability.json run_qr_str 1


exit 0

python3 -m rq1\&2.report_stability_simple_mul rq3_execution_diversity/results/libsodium/from_pops/bin2base64.result.json rq1\&2/results/libsodium/rq11.stability.json bin2base64 rq3_execution_diversity/results/libsodium/fmap.txt

python3 -m rq1\&2.report_stability_simple_mul rq3_execution_diversity/results/libsodium/from_pops/crypto_aead_chacha20poly1305_ietf_decrypt_detached.result.json rq1\&2/results/libsodium/rq11.stability.json crypto_aead_chacha20poly1305_ietf_decrypt_detached rq3_execution_diversity/results/libsodium/fmap.txt
