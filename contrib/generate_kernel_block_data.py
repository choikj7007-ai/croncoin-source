#!/usr/bin/env python3
# Copyright (c) The CronCoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit.
"""Generate regtest block data for kernel tests.

Starts a croncoind node in regtest mode, mines 200 blocks,
creates transactions, mines 6 more blocks (total 206),
then outputs a C++ header file with serialized block hex data.

The test at test_kernel.cpp expects:
- 206 blocks (indices 0-205 in the array, heights 1-206)
- Block at height 201 should have multiple non-coinbase transactions
- Block at height 206 (tip) must have exactly 1 non-coinbase tx
  whose last spent output was confirmed at height 205
- The spent output amount is checked by the test

Usage:
    python3 contrib/generate_kernel_block_data.py > src/test/kernel/block_data.h
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import shutil
from decimal import Decimal

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.dirname(SCRIPT_DIR)
CRONCOIND = os.path.join(SOURCE_DIR, "build", "bin", "croncoind")
CRONCOIN_CLI = os.path.join(SOURCE_DIR, "build", "bin", "croncoin-cli")

# CronCoin constants
COIN = 1000
BLOCK_REWARD = 600000 * COIN  # 600,000,000 cros


def cli(*args, datadir=None):
    """Run croncoin-cli with the given arguments and return stdout."""
    cmd = [CRONCOIN_CLI, "-regtest"]
    if datadir:
        cmd.append(f"-datadir={datadir}")
    cmd.extend(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(
            f"croncoin-cli {' '.join(args)} failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    return result.stdout.strip()


def cli_json(*args, datadir=None):
    """Run croncoin-cli and parse JSON output."""
    output = cli(*args, datadir=datadir)
    return json.loads(output)


def wait_for_node(datadir, timeout=30):
    """Wait for the node to be ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            cli("getblockchaininfo", datadir=datadir)
            return True
        except (RuntimeError, subprocess.TimeoutExpired):
            time.sleep(0.5)
    raise RuntimeError("Node did not become ready in time")


def main():
    tmpdir = tempfile.mkdtemp(prefix="croncoin_blockdata_")
    node_started = False

    try:
        # Start croncoind in daemon mode
        sys.stderr.write(f"Starting croncoind with datadir={tmpdir}\n")
        subprocess.run(
            [
                CRONCOIND,
                "-regtest",
                f"-datadir={tmpdir}",
                "-daemon=1",
                "-server=1",
                "-txindex=1",
                "-listen=0",
                "-listenonion=0",
                "-rpcallowip=127.0.0.1",
                "-fallbackfee=0.01",
                "-minrelaytxfee=0.001",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        node_started = True

        wait_for_node(tmpdir)
        sys.stderr.write("Node is ready\n")

        # Create a wallet
        cli("createwallet", "test_wallet", datadir=tmpdir)
        sys.stderr.write("Wallet created\n")

        # Get an address for mining
        mining_addr = cli("getnewaddress", "", "bech32", datadir=tmpdir)
        sys.stderr.write(f"Mining address: {mining_addr}\n")

        # Mine 200 blocks in batches
        sys.stderr.write("Mining 200 blocks...\n")
        batch_size = 25
        for batch_start in range(0, 200, batch_size):
            count = min(batch_size, 200 - batch_start)
            cli("generatetoaddress", str(count), mining_addr, datadir=tmpdir)
            if (batch_start + count) % 50 == 0 or batch_start + count == 200:
                sys.stderr.write(f"  Mined {batch_start + count} blocks\n")
        sys.stderr.write("200 blocks mined\n")

        # Verify block count
        block_count = int(cli("getblockcount", datadir=tmpdir))
        sys.stderr.write(f"Block count: {block_count}\n")
        assert block_count == 200, f"Expected 200 blocks, got {block_count}"

        balance = cli("getbalance", datadir=tmpdir)
        sys.stderr.write(f"Wallet balance: {balance} CRN\n")

        # Strategy for blocks 201-206:
        # Block 201: many non-coinbase txs (send coins around)
        # Block 202-204: coinbase only (no txs needed)
        # Block 205: create a tx that produces an output we can spend in block 206
        # Block 206: exactly 1 non-coinbase tx spending output from block 205
        #
        # The test checks:
        # - block_spent_outputs.Count() == 1 for tip (206)
        # - The last coin from the spent outputs has coin_height == 205
        # - !coin.IsCoinbase()
        # - output.Amount() == <some value>

        # Create many transactions for block 201
        sys.stderr.write("Creating transactions for block 201...\n")
        num_txs = 20
        for i in range(num_txs):
            dest_addr = cli("getnewaddress", "", "bech32", datadir=tmpdir)
            txid = cli("sendtoaddress", dest_addr, "100.0", datadir=tmpdir)
            if i == 0 or i == num_txs - 1:
                sys.stderr.write(f"  tx {i+1}: {txid}\n")

        mempool_size = cli_json("getmempoolinfo", datadir=tmpdir)["size"]
        sys.stderr.write(f"  Mempool size: {mempool_size}\n")

        # Mine block 201
        cli("generatetoaddress", "1", mining_addr, datadir=tmpdir)
        block_count = int(cli("getblockcount", datadir=tmpdir))
        sys.stderr.write(f"Block 201 mined (height {block_count})\n")

        # Mine blocks 202-204 (coinbase only)
        cli("generatetoaddress", "3", mining_addr, datadir=tmpdir)
        block_count = int(cli("getblockcount", datadir=tmpdir))
        sys.stderr.write(f"Blocks 202-204 mined (height {block_count})\n")

        # Create a transaction for block 205
        # This transaction's output will be spent in block 206
        dest_addr_205 = cli("getnewaddress", "", "bech32", datadir=tmpdir)
        send_amount = "100.0"  # 100 CRN = 100,000 cros
        txid_205 = cli("sendtoaddress", dest_addr_205, send_amount, datadir=tmpdir)
        sys.stderr.write(f"Transaction for block 205: {txid_205}\n")

        # Mine block 205
        cli("generatetoaddress", "1", mining_addr, datadir=tmpdir)
        block_count = int(cli("getblockcount", datadir=tmpdir))
        sys.stderr.write(f"Block 205 mined (height {block_count})\n")

        # Now create a transaction for block 206 that spends the output from block 205
        # The output from txid_205 going to dest_addr_205 should be spendable
        # (it has 1 confirmation which is enough for non-coinbase outputs)
        dest_addr_206 = cli("getnewaddress", "", "bech32", datadir=tmpdir)
        txid_206 = cli("sendtoaddress", dest_addr_206, "50.0", datadir=tmpdir)
        sys.stderr.write(f"Transaction for block 206: {txid_206}\n")

        # Verify the tx for block 206 spends from something confirmed at height 205
        tx_206_info = cli_json("getrawtransaction", txid_206, "true", datadir=tmpdir)
        for vin in tx_206_info["vin"]:
            prev_txid = vin["txid"]
            prev_vout = vin["vout"]
            prev_tx = cli_json("getrawtransaction", prev_txid, "true", datadir=tmpdir)
            if "blockhash" in prev_tx:
                prev_block = cli_json("getblock", prev_tx["blockhash"], "1", datadir=tmpdir)
                prev_height = prev_block["height"]
            else:
                prev_height = "mempool"
            amount = prev_tx["vout"][prev_vout]["value"]
            sys.stderr.write(
                f"  Spends {prev_txid[:16]}...:{prev_vout} "
                f"(height={prev_height}, amount={amount} CRN)\n"
            )

        # Mine block 206
        cli("generatetoaddress", "1", mining_addr, datadir=tmpdir)
        block_count = int(cli("getblockcount", datadir=tmpdir))
        sys.stderr.write(f"Block 206 mined (height {block_count})\n")
        assert block_count == 206, f"Expected 206 blocks, got {block_count}"

        # Verify mempool is empty
        mempool_size = cli_json("getmempoolinfo", datadir=tmpdir)["size"]
        sys.stderr.write(f"Mempool size after mining: {mempool_size}\n")

        # Collect all block hex data (blocks 1-206, excluding genesis)
        genesis_hash = cli("getblockhash", "0", datadir=tmpdir)
        sys.stderr.write(f"\nGenesis hash: {genesis_hash}\n")

        block_hexes = []
        for height in range(1, 207):
            block_hash = cli("getblockhash", str(height), datadir=tmpdir)
            raw_hex = cli("getblock", block_hash, "0", datadir=tmpdir)
            block_hexes.append(raw_hex)
            if height % 50 == 0 or height > 200:
                sys.stderr.write(f"  Block {height}: hash={block_hash}, hex_len={len(raw_hex)}\n")

        # Report block details for blocks 201-206
        sys.stderr.write("\nBlock details for 201-206:\n")
        for h in range(201, 207):
            bh = cli("getblockhash", str(h), datadir=tmpdir)
            bi = cli_json("getblock", bh, "1", datadir=tmpdir)
            sys.stderr.write(f"  Block {h}: {len(bi['tx'])} txs\n")

        # Analyze block 206 for the test assertions
        block_206_hash = cli("getblockhash", "206", datadir=tmpdir)
        block_206_info = cli_json("getblock", block_206_hash, "2", datadir=tmpdir)
        sys.stderr.write(f"\nBlock 206 (tip) analysis:\n")
        sys.stderr.write(f"  Total txs: {len(block_206_info['tx'])}\n")
        non_coinbase_count = 0
        for tx in block_206_info["tx"]:
            is_coinbase = "coinbase" in tx["vin"][0] if tx["vin"] else False
            if not is_coinbase:
                non_coinbase_count += 1
                sys.stderr.write(f"  Non-coinbase tx: {tx['txid']}\n")
                for vin in tx["vin"]:
                    prev_txid = vin["txid"]
                    prev_vout = vin["vout"]
                    prev_tx = cli_json("getrawtransaction", prev_txid, "true", datadir=tmpdir)
                    if "blockhash" in prev_tx:
                        prev_block = cli_json("getblock", prev_tx["blockhash"], "1", datadir=tmpdir)
                        prev_height = prev_block["height"]
                    else:
                        prev_height = "unconfirmed"
                    amount_crn = prev_tx["vout"][prev_vout]["value"]
                    amount_cros = int(round(Decimal(str(amount_crn)) * COIN))
                    sys.stderr.write(
                        f"    Input: {prev_txid[:16]}...:{prev_vout} "
                        f"height={prev_height} amount={amount_crn} CRN ({amount_cros} cros)\n"
                    )
        sys.stderr.write(f"  Non-coinbase tx count: {non_coinbase_count}\n")

        sys.stderr.write("\nKey info for test assertions:\n")
        sys.stderr.write(f"  COIN = {COIN}\n")
        sys.stderr.write(f"  Block reward = {BLOCK_REWARD} cros ({BLOCK_REWARD // COIN} CRN)\n")
        sys.stderr.write(f"  Genesis hash = {genesis_hash}\n")
        sys.stderr.write(f"  Total blocks = {len(block_hexes)}\n")
        sys.stderr.write("  The test checks output.Amount() at line 1135 - update this value!\n")

        # Output the C++ header
        print("// Copyright (c) The CronCoin Core developers")
        print("// Distributed under the MIT software license, see the accompanying")
        print("// file COPYING or https://opensource.org/license/mit.")
        print("")
        print("#ifndef CRONCOIN_TEST_KERNEL_BLOCK_DATA_H")
        print("#define CRONCOIN_TEST_KERNEL_BLOCK_DATA_H")
        print("#include <array>")
        print("#include <string_view>")
        print(f"inline constexpr std::array<std::string_view, {len(block_hexes)}> REGTEST_BLOCK_DATA {{")
        for i, hex_data in enumerate(block_hexes):
            comma = ","
            print(f'"{hex_data}"{comma}')
        print("};")
        print("#endif // CRONCOIN_TEST_KERNEL_BLOCK_DATA_H")

        sys.stderr.write(f"\nGenerated header with {len(block_hexes)} blocks\n")

    finally:
        # Clean up
        if node_started:
            try:
                cli("stop", datadir=tmpdir)
                time.sleep(3)
            except Exception:
                pass
            sys.stderr.write("Node stopped\n")

        # Clean up temp directory
        try:
            shutil.rmtree(tmpdir)
            sys.stderr.write(f"Cleaned up {tmpdir}\n")
        except Exception as e:
            sys.stderr.write(f"Warning: could not clean up {tmpdir}: {e}\n")


if __name__ == "__main__":
    main()
