# SpecCode V4 — Live StudioNet Evidence

This document records a reproducible live run against the reviewed V4 source. It is derived from the canonical machine-readable evidence in [`live-evidence/studionet-1087145256.json`](live-evidence/studionet-1087145256.json).

## Deployment and actors

- Network: GenLayer StudioNet (`61999`)
- Contract: [`0xA0839F5509930795B08fB639f2a9436e94DD9F0A`](https://explorer-studio.genlayer.com/address/0xA0839F5509930795B08fB639f2a9436e94DD9F0A)
- Schema readback: `semantic-specimen-code-registry-v4`, version `4`
- Run: `1087145256`
- Namespace: `sample-intake-1087145256`
- Namespace authority / curator: `0xeb57bc7125fa60d7482CE12058397369AB3581f8`
- Recorder: `0x2da5393d7BBb9A037dc3abB56DbbC5C150fc843f`
- Deploy wallet involvement after deployment: none

## Finalized transactions

Every transaction below reached `FINALIZED`. Success and error outcomes are both intentional and were checked before the runner recorded the assertion.

| Scenario | Expected / actual | Explorer |
|---|---|---|
| Wallet A creates independent namespace | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0x7619fea4ba3c775c7522e56e2216f275c150381cdf94f67f1088c2fcb825daf0) |
| Wallet A enables itself as curator | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0x5f2493f1bee5927e7d24e6ab2e72c92132e0de2381d87cc11577d716e094cab5) |
| Wallet A enables wallet B as recorder | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0x89f22670be87ca359c112e48c967c1a1dd5f9136304631fbbdeb128a820c7a38) |
| Curator proposes base code | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0xb84dfaa430250fe0831ef83dc7b567c804887f1a07d8fb95e567febcbc2d18da) |
| Consensus assesses base as `DISTINCT` | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0xcd4506f6f6b7011f34d29e5e088731b49719ca026d11bf7ec56d227b283cc792) |
| Recorder creates exact rejection record | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0x75a4e3c1a82bef52e2b5f63e9a55cf51c0755c36866d40d28d92ca094b464722) |
| Reject record-ID replay | ERROR / ERROR | [transaction](https://explorer-studio.genlayer.com/tx/0x5996d2dbc4d4b88037f6254fa376bd5ef0bfaf7cf787a26f05ce217e6af29691) |
| Reject specimen replay under another record ID | ERROR / ERROR | [transaction](https://explorer-studio.genlayer.com/tx/0x7a51f6ce20cd3f54c745bc76ad95c42e70b6b03d8d1cee4615a22c4ec37b7c11) |
| Reject curator acting as recorder | ERROR / ERROR | [transaction](https://explorer-studio.genlayer.com/tx/0xa9afedb7ae41dca0888e8551b49edd10e459898fc4155ee4dff2555571556357) |
| Reject recorder acting as curator | ERROR / ERROR | [transaction](https://explorer-studio.genlayer.com/tx/0xeb9e5d5a2a48f7face9cb6b63be8bd1e2cc0e34eda5ee31ae14c0852b2ef6d95) |
| Propose semantic duplicate | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0xa656fa571423e84f5f9eab7b81f439cc5d63add6b443d9438662350691d1470e) |
| Consensus returns `DUPLICATE` and quarantines | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0xb41c30aa99f31da2ce66405eb5c129ae7ca3c1c38e0441467839ee3dc9eaa1b3) |
| Propose overlapping definition | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0x962c669be3f484f0f5a6c38613610136d08e1749f2d5afdb2fe7133c880fb0c5) |
| Consensus returns `OVERLAPPING` and quarantines | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0x8c77aca7d840048a0d47f5e724da4f218c196ad8922a1fa0dfccf8194784d456) |
| Propose conflicting definition | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0x13bde83725b57ad6c28787add30f37ff937cd7da6f4052699744ad423305d0ea) |
| Consensus returns `CONFLICTING` and quarantines | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0xe009c8abfb6d9ddc723f3e9956d1c9da773a776697bb1aaa487b8d2f4b25292e) |
| Seal proposal that will become stale | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0xacfb9fa042f58c990f6f4c349986e6a19d3838f9ccda70a246bc8765407bd792) |
| Propose second distinct code | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0x17e9efa4606b0eb806774b6c07d064d71d54cfca2a5ced16a6c8d91f52ab7141) |
| Consensus activates second distinct code | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0xe6069bcfe09bfb9f47b88dcfabc5d1170eb96bd553deee6a8e04dc68ee472501) |
| Reject stale candidate-set assessment | ERROR / ERROR | [transaction](https://explorer-studio.genlayer.com/tx/0xb16f05d0d381171f21a0454338caf69dd7fc8df562064afa04008e5df0e8b517) |
| Namespace authority retires base code | SUCCESS / SUCCESS | [transaction](https://explorer-studio.genlayer.com/tx/0x2e1850df0c5d640afbd1c951b2a385e35da229fd1fd9c9078c6e14978cf3f333) |
| Reject recorder attempting retirement | ERROR / ERROR | [transaction](https://explorer-studio.genlayer.com/tx/0x9aeee799dd52f82e027def9c010a1645d5d46b40bcd8e6b79b11dee985ce8831) |

## Canonical final state

```json
{
  "contract_version": {
    "name": "SpecCode",
    "schema": "semantic-specimen-code-registry-v4",
    "version": 4
  },
  "namespace": {
    "namespace_id": "sample-intake-1087145256",
    "authority": "0xeb57bc7125fa60d7482ce12058397369ab3581f8",
    "active_count": 1,
    "code_slot_count": 2,
    "proposal_count": 6,
    "record_count": 1,
    "revision": 4
  },
  "global_stats": {
    "active_codes": 1,
    "namespaces": 1,
    "records": 1
  }
}
```

The V4 retirement invariant is directly demonstrated: the namespace has one active code and the global counter also reports one. The stale proposal remains `PENDING_ASSESSMENT` with its original candidate digest, proving that the rejected stale assessment did not partially mutate state.

## Local verification

The reviewed source passes all 14 behavioral tests, GenVM lint, and GenVM validation. Tests include authorization separation, semantic outcome transitions, stale candidate-set rejection, replay prevention, retirement behavior, and synchronized active-code counters.
