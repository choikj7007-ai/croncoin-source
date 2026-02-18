#!/usr/bin/env python3
# Copyright (c) 2025-present The CronCoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Generate mainnet_alt.json for mining_mainnet test.

Mines 2016 blocks against CronCoin's mainnet genesis block.
Blocks use 30-second intervals to trigger maximum (4x) difficulty increase.

Expected runtime: ~1-3 hours (single-threaded Python hashlib).
"""

import hashlib
import json
import os
import struct
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__))))

from test_framework.messages import (
    SEQUENCE_FINAL,
    ser_uint256,
    uint256_from_str,
)
from test_framework.blocktools import (
    DIFF_1_N_BITS,
    DIFF_1_TARGET,
    DIFF_4_N_BITS,
    DIFF_4_TARGET,
    create_coinbase,
)

# CronCoin mainnet genesis
GENESIS_HASH = "00000cd0be01895d578936772a1dbd4c85764821a448b50f040e1ecead0006fe"
GENESIS_TIME = 1739491200

# Block interval (seconds) - short to trigger max difficulty increase
BLOCK_INTERVAL = 30

# Coinbase script pubkey (see data/README.md)
COINBASE_SCRIPT_PUBKEY = "76a914eadbac7f36c37e39361168b7aaee3cb24a25312d88ac"


def mine_block(height, prev_hash_int, timestamp, nbits, target):
    """Mine a single block. Returns (block_hash_int, nonce)."""
    coinbase = create_coinbase(
        height=height,
        script_pubkey=bytes.fromhex(COINBASE_SCRIPT_PUBKEY),
        halving_period=175000,
    )
    coinbase.nLockTime = 0
    coinbase.vin[0].nSequence = SEQUENCE_FINAL

    # Merkle root for single-tx block is just the txid
    merkle_root = coinbase.txid_int

    # Build 76-byte header prefix (everything except nonce)
    header_prefix = struct.pack('<i', 0x20000000)
    header_prefix += ser_uint256(prev_hash_int)
    header_prefix += ser_uint256(merkle_root)
    header_prefix += struct.pack('<II', timestamp, nbits)

    # Pre-compute target as big-endian bytes for fast comparison
    target_bytes = target.to_bytes(32, 'big')

    # Grind nonce
    for nonce in range(0, 0x100000000):
        header = header_prefix + struct.pack('<I', nonce)
        h = hashlib.sha256(hashlib.sha256(header).digest()).digest()
        # Compare hash (reversed to big-endian) against target
        if h[::-1] <= target_bytes:
            # Compute block hash as integer
            block_hash = uint256_from_str(h)
            return block_hash, nonce

    raise RuntimeError(f"Failed to find nonce for block {height}")


def main():
    timestamps = []
    nonces = []

    prev_hash = int(GENESIS_HASH, 16)

    total_start = time.time()

    for height in range(1, 2017):
        timestamp = GENESIS_TIME + height * BLOCK_INTERVAL
        nbits = DIFF_1_N_BITS if height < 2016 else DIFF_4_N_BITS
        target = DIFF_1_TARGET if height < 2016 else DIFF_4_TARGET

        block_start = time.time()
        prev_hash, nonce = mine_block(height, prev_hash, timestamp, nbits, target)
        elapsed = time.time() - block_start

        timestamps.append(timestamp)
        nonces.append(nonce)

        if height % 100 == 0 or height == 1 or height == 2016:
            total_elapsed = time.time() - total_start
            print(f"Block {height:4d}/2016  nonce={nonce:10d}  "
                  f"block_time={elapsed:.1f}s  total={total_elapsed:.0f}s", flush=True)

    # Write output
    output_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'mainnet_alt.json')
    with open(output_path, 'w') as f:
        json.dump({'timestamps': timestamps, 'nonces': nonces}, f)

    total_elapsed = time.time() - total_start
    print(f"\nDone! Generated {len(timestamps)} blocks in {total_elapsed:.0f}s")
    print(f"Output: {output_path}")


if __name__ == '__main__':
    main()
