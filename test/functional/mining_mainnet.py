#!/usr/bin/env python3
# Copyright (c) 2025-present The CronCoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test mining on an alternate mainnet

Test mining related RPCs on mainnet, which has different consensus rules
than regtest (difficulty adjustment, 180-second minimum block interval).

It uses an alternate mainnet chain. See data/README.md for how it was generated.

Mine one retarget period worth of blocks at the target spacing (180s).
Due to Bitcoin's off-by-one in difficulty calculation (2015 intervals for
2016 blocks), difficulty increases very slightly (~0.05%) after retarget
even with exactly target-spaced blocks. Verify this using getmininginfo.

"""

from test_framework.test_framework import CronCoinTestFramework
from test_framework.util import (
    assert_equal,
)
from test_framework.blocktools import (
    DIFF_1_N_BITS,
    DIFF_1_TARGET,
    create_coinbase,
    nbits_str,
    target_str
)

from test_framework.messages import (
    CBlock,
    SEQUENCE_FINAL,
    uint256_from_compact,
)

import json
import os

# See data/README.md
COINBASE_SCRIPT_PUBKEY="76a914eadbac7f36c37e39361168b7aaee3cb24a25312d88ac"

class MiningMainnetTest(CronCoinTestFramework):

    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = "" # main

    def add_options(self, parser):
        parser.add_argument(
            '--datafile',
            default='data/mainnet_alt.json',
            help='Block data file (default: %(default)s)',
        )

    def mine(self, height, prev_hash, blocks, node, nbits=DIFF_1_N_BITS):
        self.log.debug(f"height={height}")
        block = CBlock()
        block.nVersion = 0x20000000
        block.hashPrevBlock = int(prev_hash, 16)
        block.nTime = blocks['timestamps'][height - 1]
        block.nBits = nbits
        block.nNonce = blocks['nonces'][height - 1]
        block.vtx = [create_coinbase(height=height, script_pubkey=bytes.fromhex(COINBASE_SCRIPT_PUBKEY), halving_period=175000)]
        # The alternate mainnet chain was mined with non-timelocked coinbase txs.
        block.vtx[0].nLockTime = 0
        block.vtx[0].vin[0].nSequence = SEQUENCE_FINAL
        block.hashMerkleRoot = block.calc_merkle_root()
        block_hex = block.serialize(with_witness=False).hex()
        self.log.debug(block_hex)
        assert_equal(node.submitblock(block_hex), None)
        prev_hash = node.getbestblockhash()
        assert_equal(prev_hash, block.hash_hex)
        return prev_hash


    EXPECTED_GENESIS_HASH = "00000cd0be01895d578936772a1dbd4c85764821a448b50f040e1ecead0006fe"

    def run_test(self):
        node = self.nodes[0]
        # Clear disk space warning
        node.stderr.seek(0)
        node.stderr.truncate()

        genesis_hash = node.getbestblockhash()
        assert_equal(genesis_hash, self.EXPECTED_GENESIS_HASH)

        self.log.info("Load alternative mainnet blocks")
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.options.datafile)
        prev_hash = genesis_hash
        blocks = None
        with open(path) as f:
            blocks = json.load(f)
            n_blocks = len(blocks['timestamps'])
            assert_equal(n_blocks, 2016)

        # Mine up to the last block of the first retarget period
        for i in range(2015):
            prev_hash = self.mine(i + 1, prev_hash, blocks, node)

        assert_equal(node.getblockcount(), 2015)

        self.log.info("Check difficulty with getmininginfo")
        mining_info = node.getmininginfo()
        assert_equal(mining_info['difficulty'], 1)
        assert_equal(mining_info['bits'], nbits_str(DIFF_1_N_BITS))
        assert_equal(mining_info['target'], target_str(DIFF_1_TARGET))

        # Due to Bitcoin's off-by-one in difficulty calculation (actual timespan
        # covers 2015 intervals but target timespan assumes 2016), difficulty
        # increases very slightly even with exactly target-spaced blocks.
        assert_equal(mining_info['next']['height'], 2016)
        next_difficulty = float(mining_info['next']['difficulty'])
        self.log.info(f"Next difficulty after retarget: {next_difficulty}")
        assert next_difficulty > 1.0, f"Expected difficulty > 1, got {next_difficulty}"
        assert next_difficulty < 1.001, f"Expected difficulty < 1.001, got {next_difficulty}"

        # Get the retarget nBits from the node for block 2016
        next_nbits = int(mining_info['next']['bits'], 16)
        next_target = uint256_from_compact(next_nbits)

        # Mine first block of the second retarget period with retarget nBits
        height = 2016
        prev_hash = self.mine(height, prev_hash, blocks, node, nbits=next_nbits)
        assert_equal(node.getblockcount(), height)

        mining_info = node.getmininginfo()
        assert_equal(float(mining_info['difficulty']), next_difficulty)

        self.log.info("getblock RPC should show historical target")
        block_info = node.getblock(node.getblockhash(1))

        assert_equal(block_info['difficulty'], 1)
        assert_equal(block_info['bits'], nbits_str(DIFF_1_N_BITS))
        assert_equal(block_info['target'], target_str(DIFF_1_TARGET))


if __name__ == '__main__':
    MiningMainnetTest(__file__).main()
