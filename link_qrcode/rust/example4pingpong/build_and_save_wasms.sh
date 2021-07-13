
bash build_template.sh ../../multivariant/allinone.multivariant.bc ../../4Deploy/qrcode_multivariant_ping.wasm templates/main_ping.rs
bash build_template.sh ../../multivariant/allinone.multivariant.bc ../../4Deploy/qrcode_multivariant_pong.wasm templates/main_pong.rs

bash build_template.sh ../../multivariant/all.bc ../../4Deploy/qrcode_original_ping.wasm templates/main_ping.rs
bash build_template.sh ../../multivariant/all.bc ../../4Deploy/qrcode_original_pong.wasm templates/main_pong.rs