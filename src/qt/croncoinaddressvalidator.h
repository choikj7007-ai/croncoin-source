// Copyright (c) 2011-present The CronCoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef CRONCOIN_QT_CRONCOINADDRESSVALIDATOR_H
#define CRONCOIN_QT_CRONCOINADDRESSVALIDATOR_H

#include <QValidator>

/** Base58 entry widget validator, checks for valid characters and
 * removes some whitespace.
 */
class CronCoinAddressEntryValidator : public QValidator
{
    Q_OBJECT

public:
    explicit CronCoinAddressEntryValidator(QObject *parent);

    State validate(QString &input, int &pos) const override;
};

/** CronCoin address widget validator, checks for a valid croncoin address.
 */
class CronCoinAddressCheckValidator : public QValidator
{
    Q_OBJECT

public:
    explicit CronCoinAddressCheckValidator(QObject *parent);

    State validate(QString &input, int &pos) const override;
};

#endif // CRONCOIN_QT_CRONCOINADDRESSVALIDATOR_H
