

python3 -m rq1\&2.report_stability_simple_mul rq3_execution_diversity/results/libsodium/from_pops/bin2base64.result.json rq1\&2/results/libsodium/rq11_libsodium_.stability.json bin2base64 rq3_execution_diversity/results/libsodium/fmap.txt

echo ""
echo ""

python3 -m rq1\&2.report_stability_simple_mul rq3_execution_diversity/results/libsodium/from_pops/crypto_aead_chacha20poly1305_ietf_decrypt_detached.result.json rq1\&2/results/libsodium/rq11_libsodium_.stability.json crypto_aead_chacha20poly1305_ietf_decrypt_detached rq3_execution_diversity/results/libsodium/fmap.txt

echo ""
echo ""

python3 -m rq1\&2.report_stability_simple_mul rq3_execution_diversity/results/libsodium/from_pops/crypto_aead_chacha20poly1305_ietf_encrypt_detached.result.json rq1\&2/results/libsodium/rq11_libsodium_.stability.json crypto_aead_chacha20poly1305_ietf_encrypt_detached rq3_execution_diversity/results/libsodium/fmap.txt


echo ""
echo ""

python3 -m rq1\&2.report_stability_simple_mul rq3_execution_diversity/results/libsodium/from_pops/crypto_core_ed25519_scalar_complement.result.json rq1\&2/results/libsodium/rq11_libsodium_.stability.json crypto_core_ed25519_scalar_complement rq3_execution_diversity/results/libsodium/fmap.txt


echo ""
echo ""

python3 -m rq1\&2.report_stability_simple_mul rq3_execution_diversity/results/libsodium/from_pops/crypto_core_ed25519_scalar_invert.result.json rq1\&2/results/libsodium/rq11_libsodium_.stability.json crypto_core_ed25519_scalar_invert rq3_execution_diversity/results/libsodium/fmap.txt

echo ""
echo ""

python3 -m rq1\&2.report_stability rq1\&2/results/qrcode/rq11_qrcode_.stability.json run_qr_str 1

echo ""
echo ""

python3 -m rq1\&2.report_stability_simple_mul_frommongo rq1\&2/results/qrcode/rq11_qrcode_.stability.json run_qr rq3_execution_diversity/results/qrcode/fmap.txt
