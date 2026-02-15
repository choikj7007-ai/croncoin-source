#!/usr/bin/env python3
# Copyright (c) 2023-present The CronCoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test validateaddress for main chain"""

from test_framework.test_framework import CronCoinTestFramework

from test_framework.util import assert_equal

INVALID_DATA = [
    # BIP 173
    (
        "tc1qw508d6qejxtdg4y5r3zarvary0c5xw7kg3g4ty",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # Invalid hrp
        [],
    ),
    ("crn1qw508d6qejxtdg4y5r3zarvary0c5xw7k0p6nwq", "Invalid Bech32 checksum", [42]),
    (
        "CRN13W508D6QEJXTDG4Y5R3ZARVARY0C5XW7KSNUVVM",
        "Version 1+ witness address must use Bech32m checksum",
        [],
    ),
    (
        "crn1rw54ac436",
        "Version 1+ witness address must use Bech32m checksum",  # Invalid program length
        [],
    ),
    (
        "crn10w508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7kw5x4ztsy",
        "Version 1+ witness address must use Bech32m checksum",  # Invalid program length
        [],
    ),
    (
        "CRN1QR508D6QEJXTDG4Y5R3ZARVARYVXZ9ZEF",
        "Invalid Bech32 v0 address program size (16 bytes), per BIP141",
        [],
    ),
    (
        "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sL5k7",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Mixed case
        [],
    ),
    (
        "CRN1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7K0P6NWy",
        "Invalid character or mixed case",  # crn, Mixed case
        [42],
    ),
    (
        "crn1zw508d6qejxtdg4y5r3zarvaryvq0uvmtr",
        "Version 1+ witness address must use Bech32m checksum",  # Wrong padding
        [],
    ),
    (
        "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3pjxtptv",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Non-zero padding in 8-to-5 conversion
        [],
    ),
    ("crn1dmwdkd", "Empty Bech32 data section", []),
    # BIP 350
    (
        "tc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vq5zuyut",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # Invalid human-readable part
        [],
    ),
    (
        "crn1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqrz2ghr",
        "Version 1+ witness address must use Bech32m checksum",  # Invalid checksum (Bech32 instead of Bech32m)
        [],
    ),
    (
        "tb1z0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqglt7rf",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Invalid checksum (Bech32 instead of Bech32m)
        [],
    ),
    (
        "CRN1S0XLXVLHEMJA6C4DQV22UAPCTQUPFHLXM9H8Z3K2E72Q4K9HCZ7VQQAQ0L3",
        "Version 1+ witness address must use Bech32m checksum",  # Invalid checksum (Bech32 instead of Bech32m)
        [],
    ),
    (
        "crn1qw508d6qejxtdg4y5r3zarvary0c5xw7k6a2ltx",
        "Version 0 witness address must use Bech32 checksum",  # Invalid checksum (Bech32m instead of Bech32)
        [],
    ),
    (
        "tb1q0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vq24jc47",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Invalid checksum (Bech32m instead of Bech32)
        [],
    ),
    (
        "crn1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqk7oyjp",
        "Invalid Base 32 character",  # Invalid character in checksum
        [59],
    ),
    (
        "CRN130XLXVLHEMJA6C4DQV22UAPCTQUPFHLXM9H8Z3K2E72Q4K9HCZ7VQ22QX8D",
        "Invalid Bech32 address witness version",
        [],
    ),
    ("crn1pw5y9670p", "Invalid Bech32 address program size (1 byte)", []),
    (
        "crn1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7v8n0nx0muaewav255gczg8",
        "Invalid Bech32 address program size (41 bytes)",
        [],
    ),
    (
        "CRN1QR508D6QEJXTDG4Y5R3ZARVARYVXZ9ZEF",
        "Invalid Bech32 v0 address program size (16 bytes), per BIP141",
        [],
    ),
    (
        "tb1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vq47Zagq",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Mixed case
        [],
    ),
    (
        "crn1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7v07qdk4hvh",
        "Invalid padding in Bech32 data section",  # zero padding of more than 4 bits
        [],
    ),
    (
        "tb1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vpggkg4j",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Non-zero padding in 8-to-5 conversion
        [],
    ),
    ("crn1dmwdkd", "Empty Bech32 data section", []),
]
VALID_DATA = [
    # BIP 350
    (
        "CRN1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7K0P6NWY",
        "0014751e76e8199196d454941c45d1b3a323f1433bd6",
    ),
    # (
    #   "tcrn1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q...",
    #   "00201863143c14c5166804bd19203356da136c985678cd4d27a1b8c6329604903262",
    # ),
    (
        "crn1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qvs8dvl",
        "00201863143c14c5166804bd19203356da136c985678cd4d27a1b8c6329604903262",
    ),
    (
        "crn1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7kg90784",
        "5128751e76e8199196d454941c45d1b3a323f1433bd6751e76e8199196d454941c45d1b3a323f1433bd6",
    ),
    ("CRN1SW50Q3T3DEC", "6002751e"),
    ("crn1zw508d6qejxtdg4y5r3zarvaryv7rt3yc", "5210751e76e8199196d454941c45d1b3a323"),
    # (
    #   "tcrn1qqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvses...",
    #   "0020000000c4a5cad46221b2a187905e5266362b99d5e91c6ce24d165dab93e86433",
    # ),
    (
        "crn1qqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvsesqx0rd9",
        "0020000000c4a5cad46221b2a187905e5266362b99d5e91c6ce24d165dab93e86433",
    ),
    # (
    #   "tcrn1pqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvses...",
    #   "5120000000c4a5cad46221b2a187905e5266362b99d5e91c6ce24d165dab93e86433",
    # ),
    (
        "crn1pqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvses23024e",
        "5120000000c4a5cad46221b2a187905e5266362b99d5e91c6ce24d165dab93e86433",
    ),
    (
        "crn1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqk76yjp",
        "512079be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798",
    ),
    # PayToAnchor(P2A)
    (
        "crn1pfeesf9wf9r",
        "51024e73",
    ),
]


class ValidateAddressMainTest(CronCoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.chain = ""  # main
        self.num_nodes = 1
        self.extra_args = [["-prune=899"]] * self.num_nodes

    def check_valid(self, addr, spk):
        info = self.nodes[0].validateaddress(addr)
        assert_equal(info["isvalid"], True)
        assert_equal(info["scriptPubKey"], spk)
        assert "error" not in info
        assert "error_locations" not in info

    def check_invalid(self, addr, error_str, error_locations):
        res = self.nodes[0].validateaddress(addr)
        assert_equal(res["isvalid"], False)
        assert_equal(res["error"], error_str)
        assert_equal(res["error_locations"], error_locations)

    def test_validateaddress(self):
        for (addr, error, locs) in INVALID_DATA:
            self.check_invalid(addr, error, locs)
        for (addr, spk) in VALID_DATA:
            self.check_valid(addr, spk)

    def run_test(self):
        self.test_validateaddress()


if __name__ == "__main__":
    ValidateAddressMainTest(__file__).main()
