// Copyright (c) 2011-present The CronCoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef CRONCOIN_MAPPORT_H
#define CRONCOIN_MAPPORT_H

static constexpr bool DEFAULT_NATPMP = true;

void StartMapPort(bool enable);
void InterruptMapPort();
void StopMapPort();

#endif // CRONCOIN_MAPPORT_H
