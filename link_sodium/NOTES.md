## In order to link bitcode files

- `export RUSTFLAGS="-C link-args=/Users/javierca/Documents/Develop/fastly4edge/link_sodium/src/lib/babbage2.bc"`

For directory
- `export RUSTFLAGS='-L /Users/javierca/Documents/Develop/fastly4edge/sodium'`

Bindgen

- `https://github.com/maidsafe/rust_sodium/blob/master/rust_sodium-sys/src/bindgen.rs`

- In order to avoid duplications, we need to provide our own mangle

- Provide the variants in the build.rs file


# Example, base64

```
extern "C" {
    pub fn sodium_bin2base64(
        b64: *mut libc::c_char,
        b64_maxlen: usize,
        bin: *const libc::c_uchar,
        bin_len: usize,
        variant: libc::c_int,
    ) -> *mut libc::c_char;
}
```

6JqFi5YU9htybHrPOsjpB9

# TODO

It seems that memory allocation type of operations affects the performance, security and stability of the service.


## Results for meeting 1

- codel-model flag does not do anything.
- explicitly setting inlining avoid the merging as a different function.
    - Still, the debloating is happening https://stackoverflow.com/questions/37494874/why-empty-functions-arent-removed-as-dead-code-in-llvm-ir 
### Sizes:

- No inlining in variants: 12 528 517, 840413
- Original:    12 323 002, 660841
- No inlining for all functions: 12481056, 792093
The only reason why no  inlining is giving less size than inlining is in case (when the number of function*number of calls) is larger. For example,

FA(){
    a1
    a2
    a3
}

FB(){
    FA()
    FA()
    FA()
}

FB(){
    a1
    a2
    a3
    a1
    a2
    a3
    a1
    a2
    a3
}

the all inline FB is larger than call the functions three times.

If...variants size is less thant he original then is better to inline for sake of performance
If...variants are larger, then is better no avoid inlining.


## Shannon entropy

### Deterministic dispatcher

crypto_aead_chacha20poly1305_ietf_encrypt_detached Entropy 1.0438576772312957
crypto_aead_chacha20poly1305_ietf_decrypt_detached Entropy 1.3222995864965876
crypto_core_ed25519_scalar_invert Entropy 0.9725370837821966
crypto_core_ed25519_scalar_complement Entropy 1.3476284393379812
crypto_core_ed25519_scalar_random Entropy 2.754407168984555
sodium_increment Entropy 2.7696770127299146
sodium_memcmp Entropy 2.777472321564674
sodium_is_zero Entropy 2.7696770127299146
sodium_add Entropy 2.563039774229589
bin2base64 Entropy 1.5031822220748308

### Hash based dispatcher

crypto_aead_chacha20poly1305_ietf_encrypt_detached Entropy 1.0409184798501576
crypto_aead_chacha20poly1305_ietf_decrypt_detached Entropy 1.314123503603944
crypto_core_ed25519_scalar_invert Entropy 0.9721243048809954
crypto_core_ed25519_scalar_complement Entropy 1.283468525112976
crypto_core_ed25519_scalar_random Entropy 2.552439513170005
sodium_increment Entropy 1.871438213579811
sodium_memcmp Entropy 1.8873569986737655
sodium_is_zero Entropy 1.8607744108019655
sodium_add Entropy 1.725780094995788
bin2base64 Entropy 1.4564768293644237

### System random dispatcher

TODO

### Notes
- If the number of variants is low, is quite probable that the entropy is the same
- The entropy increases with the deterministic dispatcher if the number of variants is high. For example, bin2base64, sodium_memcmp, 