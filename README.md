Cron Coin Core
=====================================

Cron Coin Core란?
---------------------

Cron Coin Core는 Cron Coin P2P 네트워크에 연결하여 블록과 트랜잭션을 다운로드하고
완전히 검증하는 풀 노드 소프트웨어입니다. 지갑과 그래픽 사용자 인터페이스(GUI)도
포함되어 있으며, 선택적으로 빌드할 수 있습니다.

Cron Coin은 Bitcoin Core에서 포크된 암호화폐로, 다음과 같은 사양을 갖습니다:
- 심볼: CRN
- 최소 단위: cros (1 CRN = 1,000 cros)
- 최대 공급량: 210,000,000,000 CRN
- 블록 보상: 600,000 CRN
- 반감기 주기: 175,000 블록
- 블록 생성 시간: 3분
- 난이도 조정: 2,016 블록마다 (~4.2일)

자세한 정보는 [doc 폴더](/doc)를 참고하세요.

제네시스 블록
----------------------

모든 네트워크의 제네시스 블록은 2025년 2월 14일(UTC)에 생성되었으며, 코인베이스에 다음 메시지가 포함되어 있습니다:

> **"CronCoin 14/Feb/2026 A new era of scheduled digital currency begins"**

### 제네시스 블록 공통 정보

| 항목 | 값 |
|---|---|
| 코인베이스 메시지 | `CronCoin 14/Feb/2026 A new era of scheduled digital currency begins` |
| 머클 루트 | `95e88b0bfe31e6ee9f09204dfd6d06b6c3c526b18288a639f8f52510ada0d02b` |
| 블록 보상 | 600,000 CRN |
| 버전 | 1 |
| 이전 블록 해시 | `0000000000000000000000000000000000000000000000000000000000000000` |

### 네트워크별 제네시스 블록 해시

| 네트워크 | 블록 해시 | nTime | nNonce | nBits |
|---|---|---|---|---|
| **메인넷** | `00000cd0be01895d578936772a1dbd4c85764821a448b50f040e1ecead0006fe` | 1739491200 | 2045846 | `1e0fffff` |
| **테스트넷** | `00000a10d36a2c7bfb0b5c909d51eeb0ce1fb75922a8b44740ae90d65b079e7d` | 1739491201 | 827754 | `1e0fffff` |
| **테스트넷4** | `000007d6e85fdc251f97c26d62656086984545ea0118f83ed93839d88bc5df80` | 1739491202 | 737785 | `1e0fffff` |
| **시그넷** | `0000011a4af9e2e6bb635ed017c599146f28c9dcbd6ceb2b3b410d8bd1145cd9` | 1739491200 | 2236221 | `1e0377ae` |
| **레그테스트** | `2454c267ddbca62ff21f2d3b81e8756c274d5ec00d3a8bb246f336801c596f55` | 1739491200 | 1 | `207fffff` |

### 제네시스 코인베이스 트랜잭션 구조

제네시스 블록의 코인베이스 트랜잭션은 2개의 출력을 가집니다:

| 출력 | 값 | 내용 |
|---|---|---|
| `vout[0]` | 600,000 CRN | 블록 보상 (P2PK 스크립트) |
| `vout[1]` | 0 CRN | OP_RETURN 메타데이터: `CRN:R=1:P=1:T=2025-02-14 00:00:H=0` |

블록 메타데이터 (OP_RETURN)
----------------------

CronCoin의 고유 기능으로, **모든 블록의 코인베이스 트랜잭션에 사람이 읽을 수 있는 메타데이터가 OP_RETURN 출력으로 기록**됩니다. 이 메타데이터는 블록체인 탐색기나 RPC를 통해 누구나 조회할 수 있습니다.

### 메타데이터 형식

```
CRN:R=<숫자>:P=<짝홀>:T=<시각>:H=<높이>
```

| 필드 | 설명 | 예시 |
|---|---|---|
| `R` | 의사난수 (1~6) | `R=3` |
| `P` | R의 짝홀 표시 (짝수=0, 홀수=1) | `P=1` |
| `T` | 블록 생성 시각 (UTC, `YYYY-MM-DD HH:MM`) | `T=2026-02-19 09:30` |
| `H` | 블록 높이 (10진수) | `H=102` |

### 예시

```
CRN:R=3:P=1:T=2026-02-19 09:30:H=102
CRN:R=4:P=0:T=2026-02-19 09:33:H=103
CRN:R=1:P=1:T=2025-02-14 00:00:H=0      (제네시스 블록)
```

### 기술 상세

- **위치**: 각 블록 코인베이스 트랜잭션의 마지막 `vout` (OP_RETURN 출력, 값 = 0)
- **난수 생성**: 이전 블록 해시의 첫 번째 바이트를 시드로 사용하여 결정론적으로 생성 (`prevBlockHash[0] % 6 + 1`). 제네시스 블록은 이전 블록이 없으므로 고정값 `R=1`을 사용합니다.
- **합의 규칙**: OP_RETURN은 표준 출력 유형이므로 별도의 합의 규칙 변경 없이 동작합니다.
- **UTXO 영향 없음**: OP_RETURN 출력은 소비 불가능(provably unspendable)하므로 UTXO 셋에 포함되지 않습니다.
- **Witness commitment와 충돌 없음**: Witness commitment는 `0xaa21a9ed` 마커로 구분되므로 메타데이터 OP_RETURN과 충돌하지 않습니다.

### RPC로 메타데이터 확인하기

```bash
# 블록 해시로 코인베이스 트랜잭션의 OP_RETURN 확인
croncoin-cli getblock <blockhash> 2

# 코인베이스의 vout 중 OP_RETURN 출력의 hex를 ASCII로 디코딩
echo "<hex값>" | xxd -r -p
```

네트워크 사양
----------------------

| 항목 | 메인넷 | 테스트넷 | 테스트넷4 | 시그넷 | 레그테스트 |
|---|---|---|---|---|---|
| 기본 포트 | 9333 | 19333 | 49333 | 39333 | 19444 |
| Bech32 접두사 | `crn` | `tcrn` | `tcrn` | `tcrn` | `crnrt` |
| Base58 공개키 접두사 | 28 (C...) | 111 | 111 | 111 | - |
| 메시지 시작 바이트 | `c1c2c3c4` | `d1d2d3d4` | `e1e2e3e4` | 동적 | `fabfb5da` |

### 주소 형식

| 유형 | 접두사 예시 |
|---|---|
| P2PKH (레거시) | `C...` |
| P2WPKH (Bech32) | `crn1...` |
| P2TR (탭루트) | `crn1p...` |
| 레그테스트 Bech32 | `crnrt1...` |

### DNS 시드 노드

새로운 노드는 `croncoin.org`의 DNS 시드 서버를 통해 피어를 탐색합니다:

| 네트워크 | DNS 시드 호스트네임 |
|---|---|
| 메인넷 | `seed1.croncoin.org`, `seed2.croncoin.org`, `seed3.croncoin.org` |
| 테스트넷 | `testnet-seed.croncoin.org` |
| 테스트넷4 | `testnet4-seed.croncoin.org` |
| 시그넷 | `signet-seed.croncoin.org` |

DNS 시드 없이 수동으로 부트스트랩할 수도 있습니다:

```bash
croncoind -seednode=<IP>:9333
croncoind -addnode=<IP>:9333
```

DNS 시드 인프라 구축에 대한 자세한 내용은 [contrib/seeds/README.md](/contrib/seeds/README.md)를 참고하세요.

### DNS 레코드 설정

`croncoin.org` 도메인에서 다음 DNS 레코드를 설정해야 합니다.

**방법 A: DNS 시더(Seeder) 사용 (권장)**

DNS 시더는 네트워크를 크롤링하여 활성 노드 IP를 자동으로 응답하는 서버입니다.
[bitcoin-seeder](https://github.com/sipa/bitcoin-seeder)를 CronCoin용으로 수정하여 사용합니다.

각 시드 호스트네임마다 NS 레코드와 시더 서버 A 레코드를 설정합니다:

```
; 메인넷 시드 (3개)
seed1.croncoin.org.    NS    ns-seed1.croncoin.org.
seed2.croncoin.org.    NS    ns-seed2.croncoin.org.
seed3.croncoin.org.    NS    ns-seed3.croncoin.org.
ns-seed1.croncoin.org. A     <시더서버1-IP>
ns-seed2.croncoin.org. A     <시더서버2-IP>
ns-seed3.croncoin.org. A     <시더서버3-IP>

; 테스트넷 시드
testnet-seed.croncoin.org.   NS    ns-testnet.croncoin.org.
ns-testnet.croncoin.org.     A     <테스트넷-시더서버-IP>

; 테스트넷4 시드
testnet4-seed.croncoin.org.  NS    ns-testnet4.croncoin.org.
ns-testnet4.croncoin.org.    A     <테스트넷4-시더서버-IP>

; 시그넷 시드
signet-seed.croncoin.org.    NS    ns-signet.croncoin.org.
ns-signet.croncoin.org.      A     <시그넷-시더서버-IP>
```

**방법 B: 정적 A 레코드 (간단)**

소규모 네트워크에서는 노드 IP를 직접 A/AAAA 레코드로 등록할 수 있습니다:

```
seed1.croncoin.org.    A      <노드1-IP>
seed1.croncoin.org.    A      <노드2-IP>
seed1.croncoin.org.    A      <노드3-IP>
seed1.croncoin.org.    AAAA   <노드-IPv6>
seed2.croncoin.org.    A      <노드4-IP>
seed3.croncoin.org.    A      <노드5-IP>
```

> 초기 런칭 시에는 방법 B로 시작하고, 네트워크가 성장하면 방법 A(DNS 시더)로 전환하는 것을 권장합니다.

수수료 구조
-------------

모든 수수료 값은 **cros** 단위입니다 (1 CRN = 1,000 cros). 수수료율은 **cros/kvB** (킬로가상바이트당 cros)로 표시됩니다.

### 중계 및 채굴 수수료

| 항목 | 값 (cros/kvB) | 값 (CRN/kvB) | 설명 |
|---|---|---|---|
| 최소 중계 수수료 | 1 | 0.001 | 트랜잭션 중계에 필요한 최소 수수료율 (`-minrelaytxfee`) |
| 증분 중계 수수료 | 1 | 0.001 | 멤풀 교체/RBF에 필요한 최소 수수료 증가분 (`-incrementalrelayfee`) |
| 블록 최소 수수료 | 1 | 0.001 | 채굴 블록에 포함되기 위한 최소 수수료율 (`-blockmintxfee`) |
| 더스트 중계 수수료 | 3 | 0.003 | 더스트 임계값 계산에 사용되는 수수료율 |

### 지갑 수수료

| 항목 | 값 (cros/kvB) | 값 (CRN/kvB) | 설명 |
|---|---|---|---|
| 최소 트랜잭션 수수료 | 1 | 0.001 | 지갑의 최소 수수료율 (`-mintxfee`) |
| 폐기 수수료 | 10 | 0.01 | 이 수수료율 이하의 잔돈은 폐기됨 (`-discardfee`) |
| 통합 수수료율 | 10 | 0.01 | UTXO 통합 시 수수료율 (`-consolidatefeerate`) |
| 지갑 증분 수수료 | 5 | 0.005 | 지갑 RBF에 권장되는 최소 수수료 증가분 |
| 대체 수수료 | 0 | 0 | 수수료 추정 불가 시 대체값; 0 = 비활성 (`-fallbackfee`) |
| 지불 수수료 | 0 | 0 | 사용자 지정 수수료율; 0 = 자동 추정 (`-paytxfee`) |

### 수수료 한도

| 항목 | 값 (cros) | 값 (CRN) | 설명 |
|---|---|---|---|
| 최대 트랜잭션 수수료 | 100,000 | 100 | 트랜잭션당 최대 수수료 (`-maxtxfee`) |
| 높은 수수료 경고 | 10 cros/kvB | 0.01 CRN/kvB | 높은 수수료 경고가 표시되는 임계값 |
| 최대 원시 트랜잭션 수수료율 | 100,000 cros/kvB | 100 CRN/kvB | `sendrawtransaction`의 최대 수수료율 |

### 더스트 임계값

트랜잭션 출력의 사용 비용이 그 가치를 초과하면 "더스트"로 간주됩니다. `DUST_RELAY_TX_FEE = 3 cros/kvB` 기준:

| 출력 유형 | 더스트 임계값 |
|---|---|
| P2PKH | ~0.546 cros |
| P2WPKH (Bech32) | ~0.294 cros |
| P2TR (탭루트) | ~0.330 cros |

### 수수료 양자화 참고

`COIN = 1000`이므로 표현 가능한 최소 수수료는 1 cro입니다. 작은 트랜잭션(~100 vB)의 경우 실질 최소 수수료율이 설정된 1 cros/kvB 대신 ~10 cros/kvB가 됩니다. 이는 소수점 3자리 정밀도의 고유한 특성이며, 일반적인 크기의 트랜잭션에는 영향을 주지 않습니다.

라이선스
-------

Cron Coin Core는 MIT 라이선스 조건에 따라 배포됩니다. 자세한 내용은 [COPYING](COPYING) 또는
https://opensource.org/license/MIT 를 참고하세요.

개발 프로세스
-------------------

`master` 브랜치는 정기적으로 빌드되고 테스트되지만 (빌드 방법은 `doc/build-*.md` 참고),
완전히 안정적임을 보장하지는 않습니다.

기여 방법은 [CONTRIBUTING.md](CONTRIBUTING.md)에 설명되어 있으며,
개발자를 위한 유용한 정보는 [doc/developer-notes.md](doc/developer-notes.md)에서 확인할 수 있습니다.

테스트
-------

### 자동화 테스트

새 코드에 대한 [단위 테스트](src/test/README.md) 작성을 강력히 권장하며,
기존 코드에 대한 단위 테스트 추가도 권장합니다. 단위 테스트는 다음 명령으로 컴파일 및 실행할 수 있습니다: `ctest`.
자세한 내용은 [/src/test/README.md](/src/test/README.md)를 참고하세요.

Python으로 작성된 [회귀 및 통합 테스트](/test)도 있습니다.
[테스트 의존성](/test)이 설치되어 있다면 다음 명령으로 실행할 수 있습니다: `build/test/functional/test_runner.py`
(`build`는 빌드 디렉토리입니다).

전체 283개 기능 테스트 통과 (264개 통과, 19개 건너뜀).

### 수동 품질 보증(QA) 테스트

변경 사항은 코드를 작성한 개발자가 아닌 다른 사람이 테스트해야 합니다.
이는 대규모 또는 고위험 변경에 특히 중요합니다.
테스트가 직관적이지 않은 경우 풀 리퀘스트 설명에 테스트 계획을 추가하는 것이 좋습니다.

메인넷 런칭 로드맵
----------------------

### 1단계: 필수 (런칭 전 반드시 완료)

- [x] **DNS 시드 노드 구성**: `croncoin.org` 도메인에 DNS 시드 호스트네임 설정 완료 (seed1/2/3, testnet-seed, testnet4-seed, signet-seed). DNS 시더 서버를 배포하고 `contrib/seeds/nodes_main.txt`에 노드 IP를 등록해야 합니다.
- [ ] **시드 노드 배포**: 지리적으로 분산된 4~6개 이상의 시드 노드에 `croncoind`를 배포하고 안정적인 운영을 보장합니다.
- [ ] **전체 빌드 검증**: `croncoind`, `croncoin-cli`, `croncoin-qt`가 Linux, macOS, Windows에서 정상적으로 빌드되는지 확인합니다. 재현 가능한 빌드 방법을 공개합니다.
- [ ] **보안 감사**: P2P 메시지 처리, 비트코인 네트워크와의 포트 격리, 피어 탐색 부트스트래핑을 감사합니다.
- [x] **제네시스 블록 확정**: 메인넷 제네시스 블록 파라미터가 최종 확정되었습니다. 제네시스 해시: `00000cd0be01895d578936772a1dbd4c85764821a448b50f040e1ecead0006fe`. OP_RETURN 메타데이터 포함.

### 2단계: 중요 (공개 릴리스 전)

- [ ] **릴리스 바이너리 빌드**: 모든 대상 플랫폼(Linux x86_64/ARM64, macOS, Windows)용 서명된 릴리스 바이너리를 빌드합니다.
- [ ] **Docker 이미지**: 공식 `croncoind` Docker 이미지를 생성하고 공개합니다.
- [ ] **노드 운영 문서**: 메인넷 설정 가이드, 구성 모범 사례, RPC API 레퍼런스를 작성합니다.
- [ ] **채굴 문서**: `getblocktemplate` 사용법 및 풀 설정을 포함한 채굴 가이드를 작성합니다.
- [ ] **블록 탐색기**: CronCoin 네트워크용 공개 블록 탐색기를 배포합니다.
- [ ] **버전 확정**: 릴리스 버전을 설정합니다 (현재 `1.0.0-rc0`). 릴리스 태그 및 릴리스 노트를 생성합니다.
- [ ] **지갑 가이드**: 지갑 생성, 백업/복원, 다중 서명 설정 문서를 작성합니다.

### 3단계: 생태계 (런칭 후)

- [ ] **채굴 풀 소프트웨어**: CronCoin과 호환되는 채굴 풀 소프트웨어를 적용 또는 배포합니다.
- [ ] **네트워크 모니터링**: 네트워크 상태(해시레이트, 노드 수, 멤풀 통계) 대시보드를 구축합니다.
- [ ] **거래소 상장 준비**: 거래소 연동을 위한 문서를 준비합니다 (RPC 엔드포인트, 확인 요구사항, 주소 형식).
- [ ] **모바일 지갑**: SPV 또는 Electrum 기반의 경량 모바일 지갑을 개발합니다.
- [ ] **Electrum 서버**: 경량 지갑 지원을 위해 CronCoin용 ElectrumX/Fulcrum 서버를 배포합니다.
- [ ] **테스트넷 파우셋**: 개발자를 위한 공개 테스트넷 파우셋을 구축합니다.
- [ ] **개발자 SDK/라이브러리**: 주요 언어(Python, JavaScript, Go)용 CronCoin 라이브러리를 공개합니다 (주소 생성, 트랜잭션 빌드, RPC 연동).
