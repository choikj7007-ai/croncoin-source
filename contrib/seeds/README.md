# CronCoin Seed Node Setup

This directory contains tools for managing the seed node infrastructure that enables new CronCoin nodes to discover peers on the network.

## Overview

CronCoin uses two mechanisms for peer discovery:

1. **DNS Seeds** (`vSeeds`): DNS hostnames that resolve to IP addresses of active nodes. Queried first on startup.
2. **Fixed Seeds** (`chainparamsseeds.h`): Hardcoded node IPs compiled into the binary. Used as fallback when DNS seeds are unreachable.

## Quick Start: Adding Your First Seed Nodes

### Step 1: Add node IPs to the seed list

Edit `nodes_main.txt` and add your running `croncoind` node IPs:

```
# IPv4
203.0.113.10:9333
198.51.100.20:9333

# IPv6
[2001:db8::1]:9333

# Tor v3
youronion...xyz.onion:9333

# I2P
youraddress...xyz.b32.i2p:0
```

### Step 2: Generate the C++ header

```bash
cd contrib/seeds
python3 generate-seeds.py . > ../../src/chainparamsseeds.h
```

### Step 3: Rebuild croncoind

```bash
cd ../../build
cmake --build .
```

The new binary will include your fixed seed nodes.

## Setting Up DNS Seeds

DNS seeds provide dynamic peer discovery. Each DNS seed is a server that responds to DNS queries with IP addresses of active CronCoin nodes.

### Option A: Using bitcoin-seeder (Recommended)

[bitcoin-seeder](https://github.com/sipa/bitcoin-seeder) can be adapted for CronCoin:

1. Fork and modify bitcoin-seeder:
   - Change the network magic bytes to `0xc1 0xc2 0xc3 0xc4`
   - Change the default port to `9333`
   - Update the protocol version if needed

2. Run the seeder on a server with a static IP:
   ```bash
   ./dnsseed -h seed1.yourdomain.com -n ns1.yourdomain.com -m your@email.com -p 9333
   ```

3. Configure DNS records:
   ```
   seed1.yourdomain.com.    NS    ns1.yourdomain.com.
   ns1.yourdomain.com.      A     <your-server-ip>
   ```

### Option B: Static DNS Records (Simple)

For a small network, you can use static A/AAAA records:

```
seed1.yourdomain.com.    A      203.0.113.10
seed1.yourdomain.com.    A      198.51.100.20
seed1.yourdomain.com.    AAAA   2001:db8::1
```

### Updating chainparams.cpp

Once DNS seeds are ready, update `src/kernel/chainparams.cpp`:

```cpp
// Replace placeholder domains with your actual domains
vSeeds.emplace_back("seed1.yourdomain.com.");
vSeeds.emplace_back("seed2.yourdomain.com.");
vSeeds.emplace_back("seed3.yourdomain.com.");
```

Search for `croncoin.example` to find all placeholder entries.

## Network Ports

| Network  | Default Port |
|----------|-------------|
| Mainnet  | 9333        |
| Testnet  | 19333       |
| Testnet4 | 49333       |
| Signet   | 39333       |
| Regtest  | 19444       |

## Bootstrap Without Seeds

Before DNS seeds and fixed seeds are configured, nodes can connect using:

```bash
# Connect to a specific node
croncoind -seednode=203.0.113.10:9333

# Or add a persistent peer
croncoind -addnode=203.0.113.10:9333

# Multiple nodes
croncoind -seednode=203.0.113.10:9333 -seednode=198.51.100.20:9333
```

## File Reference

| File | Purpose |
|------|---------|
| `nodes_main.txt` | Mainnet seed node IPs (input for generate-seeds.py) |
| `nodes_test.txt` | Testnet seed node IPs |
| `nodes_testnet4.txt` | Testnet4 seed node IPs |
| `nodes_signet.txt` | Signet seed node IPs |
| `generate-seeds.py` | Converts node lists to C++ header (BIP155 format) |
| `makeseeds.py` | Filters raw DNS crawler data into node lists |
| `../../src/chainparamsseeds.h` | Auto-generated C++ header with compiled seed data |

## Advanced: Using makeseeds.py with a DNS Crawler

When the CronCoin network has many nodes, use a DNS crawler to automatically discover and filter healthy nodes:

```bash
# 1. Collect crawler data (from your own crawler)
# Output format: one line per node with address, port, services, blocks, uptime, etc.

# 2. Filter with makeseeds.py
python3 makeseeds.py -a asmap-filled.dat -s seeds_main.txt > nodes_main.txt
python3 makeseeds.py -a asmap-filled.dat -s seeds_test.txt -m 1000 > nodes_test.txt

# 3. Generate C++ header
python3 generate-seeds.py . > ../../src/chainparamsseeds.h
```
