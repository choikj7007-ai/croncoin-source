Cron Coin Core integration/staging tree
=====================================

What is Cron Coin Core?
---------------------

Cron Coin Core connects to the Cron Coin peer-to-peer network to download and fully
validate blocks and transactions. It also includes a wallet and graphical user
interface, which can be optionally built.

Cron Coin is a cryptocurrency forked from Bitcoin Core with the following specifications:
- Symbol: CRN
- Smallest unit: cros (1 CRN = 1,000 cros)
- Maximum supply: 210,000,000,000 CRN
- Block reward: 500,000 CRN
- Halving interval: 210,000 blocks
- Block time: 10 minutes
- Difficulty adjustment: every 2,016 blocks (~2 weeks)

Further information about Cron Coin Core is available in the [doc folder](/doc).

Network Specifications
----------------------

| Parameter | Mainnet | Testnet | Testnet4 | Signet | Regtest |
|---|---|---|---|---|---|
| Default Port | 9333 | 19333 | 49333 | 39333 | 19444 |
| Bech32 Prefix | `crn` | `tcrn` | `tcrn` | `tcrn` | `crnrt` |
| Base58 Pubkey Prefix | 28 (C...) | 111 | 111 | 111 | - |
| Message Start | `c1c2c3c4` | `d1d2d3d4` | `e1e2e3e4` | dynamic | `fabfb5da` |

### Address Format

| Type | Example Prefix |
|---|---|
| P2PKH (Legacy) | `C...` |
| P2WPKH (Bech32) | `crn1...` |
| P2TR (Taproot) | `crn1p...` |
| Regtest Bech32 | `crnrt1...` |

### DNS Seeds

New nodes discover peers via DNS seed servers at `croncoin.org`:

| Network | DNS Seed Hostname |
|---|---|
| Mainnet | `seed1.croncoin.org`, `seed2.croncoin.org`, `seed3.croncoin.org` |
| Testnet | `testnet-seed.croncoin.org` |
| Testnet4 | `testnet4-seed.croncoin.org` |
| Signet | `signet-seed.croncoin.org` |

Nodes can also bootstrap manually without DNS seeds:

```bash
croncoind -seednode=<ip>:9333
croncoind -addnode=<ip>:9333
```

For details on setting up DNS seed infrastructure, see [contrib/seeds/README.md](/contrib/seeds/README.md).

Fee Structure
-------------

All fee values are denominated in **cros** (1 CRN = 1,000 cros). Fee rates are expressed in **cros/kvB** (cros per kilovirtual-byte).

### Relay & Mining Fees

| Parameter | Value (cros/kvB) | Value (CRN/kvB) | Description |
|---|---|---|---|
| Min Relay Fee | 1 | 0.001 | Minimum fee rate to relay a transaction (`-minrelaytxfee`) |
| Incremental Relay Fee | 1 | 0.001 | Minimum fee bump for mempool eviction/RBF (`-incrementalrelayfee`) |
| Block Min Tx Fee | 1 | 0.001 | Minimum fee rate for inclusion in a mined block (`-blockmintxfee`) |
| Dust Relay Fee | 3 | 0.003 | Fee rate used to calculate dust threshold |

### Wallet Fees

| Parameter | Value (cros/kvB) | Value (CRN/kvB) | Description |
|---|---|---|---|
| Min Tx Fee | 1 | 0.001 | Minimum wallet fee rate (`-mintxfee`) |
| Discard Fee | 10 | 0.01 | Fee rate below which change is discarded (`-discardfee`) |
| Consolidate Fee Rate | 10 | 0.01 | Fee rate for UTXO consolidation (`-consolidatefeerate`) |
| Wallet Incremental Fee | 5 | 0.005 | Recommended minimum fee bump for wallet RBF |
| Fallback Fee | 0 | 0 | Fallback when fee estimation unavailable; 0 = disabled (`-fallbackfee`) |
| Pay Tx Fee | 0 | 0 | User-specified fee rate; 0 = auto-estimate (`-paytxfee`) |

### Fee Limits

| Parameter | Value (cros) | Value (CRN) | Description |
|---|---|---|---|
| Max Tx Fee | 100,000 | 100 | Maximum total fee per transaction (`-maxtxfee`) |
| High Fee Warning | 10 cros/kvB | 0.01 CRN/kvB | Fee rate threshold that triggers a high-fee warning |
| Max Raw Tx Fee Rate | 100,000 cros/kvB | 100 CRN/kvB | Maximum fee rate for `sendrawtransaction` |

### Dust Thresholds

A transaction output is considered "dust" if the cost to spend it exceeds its value. With `DUST_RELAY_TX_FEE = 3 cros/kvB`:

| Output Type | Dust Threshold |
|---|---|
| P2PKH | ~0.546 cros |
| P2WPKH (Bech32) | ~0.294 cros |
| P2TR (Taproot) | ~0.330 cros |

### Fee Quantization Note

Because `COIN = 1000`, the smallest expressible fee is 1 cro. For small transactions (~100 vB), the effective minimum fee rate becomes ~10 cros/kvB rather than the configured 1 cro/kvB. This is an inherent property of the 3-decimal-place precision and does not affect typical transaction sizes.

License
-------

Cron Coin Core is released under the terms of the MIT license. See [COPYING](COPYING) for more
information or see https://opensource.org/license/MIT.

Development Process
-------------------

The `master` branch is regularly built (see `doc/build-*.md` for instructions) and tested, but it is not guaranteed to be
completely stable.

The contribution workflow is described in [CONTRIBUTING.md](CONTRIBUTING.md)
and useful hints for developers can be found in [doc/developer-notes.md](doc/developer-notes.md).

Testing
-------

### Automated Testing

Developers are strongly encouraged to write [unit tests](src/test/README.md) for new code, and to
submit new unit tests for old code. Unit tests can be compiled and run
(assuming they weren't disabled during the generation of the build system) with: `ctest`. Further details on running
and extending unit tests can be found in [/src/test/README.md](/src/test/README.md).

There are also [regression and integration tests](/test), written
in Python.
These tests can be run (if the [test dependencies](/test) are installed) with: `build/test/functional/test_runner.py`
(assuming `build` is your build directory).

All 283 functional tests pass (264 passed, 19 skipped).

### Manual Quality Assurance (QA) Testing

Changes should be tested by somebody other than the developer who wrote the
code. This is especially important for large or high-risk changes. It is useful
to add a test plan to the pull request description if testing the changes is
not straightforward.

Mainnet Launch Roadmap
----------------------

### Phase 1: Critical (Must complete before launch)

- [x] **DNS Seed Nodes**: DNS seed hostnames configured at `croncoin.org` (seed1/2/3, testnet-seed, testnet4-seed, signet-seed). Set up DNS seeder servers and populate `contrib/seeds/nodes_main.txt` with node IPs.
- [ ] **Deploy Seed Nodes**: Deploy 4-6+ geographically distributed seed nodes running `croncoind` with stable uptime.
- [ ] **Full Build Verification**: Verify `croncoind`, `croncoin-cli`, `croncoin-qt` build cleanly on Linux, macOS, and Windows. Publish reproducible build instructions.
- [ ] **Security Audit**: Audit P2P message handling, port isolation from Bitcoin network, and peer discovery bootstrapping.
- [ ] **Genesis Block Finalization**: Confirm mainnet genesis block parameters are final. Current genesis: `00000b336ddeb4eb1fe10cf0056d5fdc8ce5ebc7e8a3de01a6906f2a04bc87fa` (Feb 14, 2026).

### Phase 2: Important (Before public release)

- [ ] **Release Binary Builds**: Build signed release binaries for all target platforms (Linux x86_64/ARM64, macOS, Windows).
- [ ] **Docker Image**: Create and publish official `croncoind` Docker image for easy node deployment.
- [ ] **Node Operator Documentation**: Write mainnet setup guide, configuration best practices, and RPC API reference.
- [ ] **Mining Documentation**: Publish mining setup guide including `getblocktemplate` usage and pool configuration.
- [ ] **Block Explorer**: Deploy a public block explorer for the CronCoin network.
- [ ] **Version Finalization**: Set release version (currently `1.0.0-rc0` in CMakeLists.txt), create release tags and notes.
- [ ] **Wallet Guide**: Document wallet creation, backup/restore, and multi-sig setup.

### Phase 3: Ecosystem (Post-launch)

- [ ] **Mining Pool Software**: Adapt or deploy mining pool software compatible with CronCoin.
- [ ] **Network Monitoring**: Set up dashboards for network health (hashrate, node count, mempool stats).
- [ ] **Exchange Listing Preparation**: Prepare integration documentation for exchanges (RPC endpoints, confirmation requirements, address formats).
- [ ] **Mobile Wallet**: Develop or adapt a lightweight mobile wallet (SPV or Electrum-based).
- [ ] **Electrum Server**: Deploy ElectrumX/Fulcrum server adapted for CronCoin to support lightweight wallets.
- [ ] **Testnet Faucet**: Set up a public testnet faucet for developers.
- [ ] **Developer SDK/Libraries**: Publish CronCoin libraries for popular languages (Python, JavaScript, Go) for address generation, transaction building, and RPC interaction.
