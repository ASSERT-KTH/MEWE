

python3 -m rq1\&2.report_stability_simple_mul rresults/rq3/execution_paths/libsodium/bin2base64.result.json rq1\&2/results/libsodium/rq11_libsodium_.stability.json bin2base64 results/rq1/maps/sodium.txt

echo ""
echo ""

python3 -m rq1\&2.report_stability_simple_mul rresults/rq3/execution_paths/libsodium/crypto_aead_chacha20poly1305_ietf_decrypt_detached.result.json rq1\&2/results/libsodium/rq11_libsodium_.stability.json crypto_aead_chacha20poly1305_ietf_decrypt_detached results/rq1/maps/sodium.txt

echo ""
echo ""

python3 -m rq1\&2.report_stability_simple_mul rresults/rq3/execution_paths/libsodium/crypto_aead_chacha20poly1305_ietf_encrypt_detached.result.json rq1\&2/results/libsodium/rq11_libsodium_.stability.json crypto_aead_chacha20poly1305_ietf_encrypt_detached results/rq1/maps/sodium.txt


echo ""
echo ""

python3 -m rq1\&2.report_stability_simple_mul rresults/rq3/execution_paths/libsodium/crypto_core_ed25519_scalar_complement.result.json rq1\&2/results/libsodium/rq11_libsodium_.stability.json crypto_core_ed25519_scalar_complement results/rq1/maps/sodium.txt


echo ""
echo ""

python3 -m rq1\&2.report_stability_simple_mul rresults/rq3/execution_paths/libsodium/crypto_core_ed25519_scalar_invert.result.json rq1\&2/results/libsodium/rq11_libsodium_.stability.json crypto_core_ed25519_scalar_invert results/rq1/maps/sodium.txt

echo ""
echo ""

python3 -m rq1\&2.report_stability rq1\&2/results/qrcode/rq11_qrcode_.stability.json run_qr_str 1

echo ""
echo ""

python3 -m rq1\&2.report_stability_simple_mul_frommongo rq1\&2/results/qrcode/rq11_qrcode_.stability.json run_qr results/rq1/maps/qrcode.txt
