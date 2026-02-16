# Various test vectors

## mainnet_alt.json

For easier testing the difficulty is maximally increased in the first (and only)
retarget period, by producing blocks 30 seconds apart (vs the 3-minute target).
This triggers the maximum 4x difficulty increase at the first retarget (block 2016).

The alternate mainnet chain was generated using the Python generation script:

```sh
python3 test/functional/generate_mainnet_alt.py
```

This mines 2016 blocks against CronCoin's mainnet genesis (nTime=1739491200,
nBits=0x1e0fffff) using Python's `hashlib` for SHA256d proof-of-work grinding.
Expected runtime is ~1-3 hours (single-threaded).

The payout address is derived from first BIP32 test vector master key:

```
pkh(xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi/44h/0h/0h/<0;1>/*)#fkjtr0yn
```

It uses `pkh()` because `tr()` outputs at low heights are not spendable (`unexpected-witness`).

This makes each block deterministic except for its nonce, which is stored in
`mainnet_alt.json` along with timestamps and used to reconstruct the chain
without having to redo the proof-of-work.

Timestamps are fixed at 30-second intervals from genesis (genesis_time + height * 30),
so the nonce is the only field that needs grinding. At CronCoin's difficulty 1
(~2^20 hashes/block), each block takes a few seconds in Python.
