# Copyright (c) 2023-present The CronCoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

function(generate_setup_nsi)
  set(abs_top_srcdir ${PROJECT_SOURCE_DIR})
  set(abs_top_builddir ${PROJECT_BINARY_DIR})
  set(CLIENT_URL ${PROJECT_HOMEPAGE_URL})
  set(CLIENT_TARNAME "croncoin")
  set(CRONCOIN_WRAPPER_NAME "croncoin")
  set(CRONCOIN_GUI_NAME "croncoin-qt")
  set(CRONCOIN_DAEMON_NAME "croncoind")
  set(CRONCOIN_CLI_NAME "croncoin-cli")
  set(CRONCOIN_TX_NAME "croncoin-tx")
  set(CRONCOIN_WALLET_TOOL_NAME "croncoin-wallet")
  set(CRONCOIN_TEST_NAME "test_croncoin")
  set(EXEEXT ${CMAKE_EXECUTABLE_SUFFIX})
  configure_file(${PROJECT_SOURCE_DIR}/share/setup.nsi.in ${PROJECT_BINARY_DIR}/croncoin-win64-setup.nsi USE_SOURCE_PERMISSIONS @ONLY)
endfunction()
