

bash build_template.sh ../../multivariant/allinone.multivariant.i.bc ../../4Deploy/qrcode_multivariant_instrumented_str.wasm templates/instrumented_str.rs

bash build_template.sh ../../multivariant/allinone.multivariant.i.bc ../../4Deploy/qrcode_multivariant_instrumented.wasm templates/instrumented.rs


bash build_template.sh ../../multivariant/allinone.multivariant.bc ../../4Deploy/qrcode_multivariant_str.wasm templates/main.rs


bash build_template.sh ../../multivariant/allinone.multivariant.bc ../../4Deploy/qrcode_multivariant.wasm templates/main_bytes.rs

bash build_template.sh ../../multivariant/all.bc ../../4Deploy/qrcode_original_str.wasm templates/main.rs


bash build_template.sh ../../multivariant/all.bc ../../4Deploy/qrcode_original.wasm templates/main_bytes.rs