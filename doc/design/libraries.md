# Libraries

| Name                     | Description |
|--------------------------|-------------|
| *libcroncoin_cli*         | RPC client functionality used by *croncoin-cli* executable |
| *libcroncoin_common*      | Home for common functionality shared by different executables and libraries. Similar to *libcroncoin_util*, but higher-level (see [Dependencies](#dependencies)). |
| *libcroncoin_consensus*   | Consensus functionality used by *libcroncoin_node* and *libcroncoin_wallet*. |
| *libcroncoin_crypto*      | Hardware-optimized functions for data encryption, hashing, message authentication, and key derivation. |
| *libcroncoin_kernel*      | Consensus engine and support library used for validation by *libcroncoin_node*. |
| *libcroncoinqt*           | GUI functionality used by *croncoin-qt* and *croncoin-gui* executables. |
| *libcroncoin_ipc*         | IPC functionality used by *croncoin-node* and *croncoin-gui* executables to communicate when [`-DENABLE_IPC=ON`](multiprocess.md) is used. |
| *libcroncoin_node*        | P2P and RPC server functionality used by *croncoind* and *croncoin-qt* executables. |
| *libcroncoin_util*        | Home for common functionality shared by different executables and libraries. Similar to *libcroncoin_common*, but lower-level (see [Dependencies](#dependencies)). |
| *libcroncoin_wallet*      | Wallet functionality used by *croncoind* and *croncoin-wallet* executables. |
| *libcroncoin_wallet_tool* | Lower-level wallet functionality used by *croncoin-wallet* executable. |
| *libcroncoin_zmq*         | [ZeroMQ](../zmq.md) functionality used by *croncoind* and *croncoin-qt* executables. |

## Conventions

- Most libraries are internal libraries and have APIs which are completely unstable! There are few or no restrictions on backwards compatibility or rules about external dependencies. An exception is *libcroncoin_kernel*, which, at some future point, will have a documented external interface.

- Generally each library should have a corresponding source directory and namespace. Source code organization is a work in progress, so it is true that some namespaces are applied inconsistently, and if you look at [`add_library(croncoin_* ...)`](../../src/CMakeLists.txt) lists you can see that many libraries pull in files from outside their source directory. But when working with libraries, it is good to follow a consistent pattern like:

  - *libcroncoin_node* code lives in `src/node/` in the `node::` namespace
  - *libcroncoin_wallet* code lives in `src/wallet/` in the `wallet::` namespace
  - *libcroncoin_ipc* code lives in `src/ipc/` in the `ipc::` namespace
  - *libcroncoin_util* code lives in `src/util/` in the `util::` namespace
  - *libcroncoin_consensus* code lives in `src/consensus/` in the `Consensus::` namespace

## Dependencies

- Libraries should minimize what other libraries they depend on, and only reference symbols following the arrows shown in the dependency graph below:

<table><tr><td>

```mermaid

%%{ init : { "flowchart" : { "curve" : "basis" }}}%%

graph TD;

croncoin-cli[croncoin-cli]-->libcroncoin_cli;

croncoind[croncoind]-->libcroncoin_node;
croncoind[croncoind]-->libcroncoin_wallet;

croncoin-qt[croncoin-qt]-->libcroncoin_node;
croncoin-qt[croncoin-qt]-->libcroncoinqt;
croncoin-qt[croncoin-qt]-->libcroncoin_wallet;

croncoin-wallet[croncoin-wallet]-->libcroncoin_wallet;
croncoin-wallet[croncoin-wallet]-->libcroncoin_wallet_tool;

libcroncoin_cli-->libcroncoin_util;
libcroncoin_cli-->libcroncoin_common;

libcroncoin_consensus-->libcroncoin_crypto;

libcroncoin_common-->libcroncoin_consensus;
libcroncoin_common-->libcroncoin_crypto;
libcroncoin_common-->libcroncoin_util;

libcroncoin_kernel-->libcroncoin_consensus;
libcroncoin_kernel-->libcroncoin_crypto;
libcroncoin_kernel-->libcroncoin_util;

libcroncoin_node-->libcroncoin_consensus;
libcroncoin_node-->libcroncoin_crypto;
libcroncoin_node-->libcroncoin_kernel;
libcroncoin_node-->libcroncoin_common;
libcroncoin_node-->libcroncoin_util;

libcroncoinqt-->libcroncoin_common;
libcroncoinqt-->libcroncoin_util;

libcroncoin_util-->libcroncoin_crypto;

libcroncoin_wallet-->libcroncoin_common;
libcroncoin_wallet-->libcroncoin_crypto;
libcroncoin_wallet-->libcroncoin_util;

libcroncoin_wallet_tool-->libcroncoin_wallet;
libcroncoin_wallet_tool-->libcroncoin_util;

classDef bold stroke-width:2px, font-weight:bold, font-size: smaller;
class croncoin-qt,croncoind,croncoin-cli,croncoin-wallet bold
```
</td></tr><tr><td>

**Dependency graph**. Arrows show linker symbol dependencies. *Crypto* lib depends on nothing. *Util* lib is depended on by everything. *Kernel* lib depends only on consensus, crypto, and util.

</td></tr></table>

- The graph shows what _linker symbols_ (functions and variables) from each library other libraries can call and reference directly, but it is not a call graph. For example, there is no arrow connecting *libcroncoin_wallet* and *libcroncoin_node* libraries, because these libraries are intended to be modular and not depend on each other's internal implementation details. But wallet code is still able to call node code indirectly through the `interfaces::Chain` abstract class in [`interfaces/chain.h`](../../src/interfaces/chain.h) and node code calls wallet code through the `interfaces::ChainClient` and `interfaces::Chain::Notifications` abstract classes in the same file. In general, defining abstract classes in [`src/interfaces/`](../../src/interfaces/) can be a convenient way of avoiding unwanted direct dependencies or circular dependencies between libraries.

- *libcroncoin_crypto* should be a standalone dependency that any library can depend on, and it should not depend on any other libraries itself.

- *libcroncoin_consensus* should only depend on *libcroncoin_crypto*, and all other libraries besides *libcroncoin_crypto* should be allowed to depend on it.

- *libcroncoin_util* should be a standalone dependency that any library can depend on, and it should not depend on other libraries except *libcroncoin_crypto*. It provides basic utilities that fill in gaps in the C++ standard library and provide lightweight abstractions over platform-specific features. Since the util library is distributed with the kernel and is usable by kernel applications, it shouldn't contain functions that external code shouldn't call, like higher level code targeted at the node or wallet. (*libcroncoin_common* is a better place for higher level code, or code that is meant to be used by internal applications only.)

- *libcroncoin_common* is a home for miscellaneous shared code used by different Cron Coin Core applications. It should not depend on anything other than *libcroncoin_util*, *libcroncoin_consensus*, and *libcroncoin_crypto*.

- *libcroncoin_kernel* should only depend on *libcroncoin_util*, *libcroncoin_consensus*, and *libcroncoin_crypto*.

- The only thing that should depend on *libcroncoin_kernel* internally should be *libcroncoin_node*. GUI and wallet libraries *libcroncoinqt* and *libcroncoin_wallet* in particular should not depend on *libcroncoin_kernel* and the unneeded functionality it would pull in, like block validation. To the extent that GUI and wallet code need scripting and signing functionality, they should be able to get it from *libcroncoin_consensus*, *libcroncoin_common*, *libcroncoin_crypto*, and *libcroncoin_util*, instead of *libcroncoin_kernel*.

- GUI, node, and wallet code internal implementations should all be independent of each other, and the *libcroncoinqt*, *libcroncoin_node*, *libcroncoin_wallet* libraries should never reference each other's symbols. They should only call each other through [`src/interfaces/`](../../src/interfaces/) abstract interfaces.

## Work in progress

- Validation code is moving from *libcroncoin_node* to *libcroncoin_kernel* as part of [The libcroncoink Project #27587](https://github.com/croncoin/croncoin/issues/27587)
