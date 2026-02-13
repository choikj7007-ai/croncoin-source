// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-present The CronCoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef CRONCOIN_CONSENSUS_AMOUNT_H
#define CRONCOIN_CONSENSUS_AMOUNT_H

#include <cstdint>

/** Amount in cros (Can be negative) */
typedef int64_t CAmount;

/** The amount of cros in one CRN. */
static constexpr CAmount COIN = 1000;

/** No amount larger than this (in cros) is valid.
 *
 * Note that this constant is *not* the total money supply, which in Cron Coin
 * currently happens to be less than 210,000,000,000 CRN for various reasons, but
 * rather a sanity check. As this sanity check is used by consensus-critical
 * validation code, the exact value of the MAX_MONEY constant is consensus
 * critical; in unusual circumstances like a(nother) overflow bug that allowed
 * for the creation of coins out of thin air modification could lead to a fork.
 * */
static constexpr CAmount MAX_MONEY = 210000000000LL * COIN;
inline bool MoneyRange(const CAmount& nValue) { return (nValue >= 0 && nValue <= MAX_MONEY); }

#endif // CRONCOIN_CONSENSUS_AMOUNT_H
