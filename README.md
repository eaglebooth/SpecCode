# SpecCode

SpecCode is a contract-only GenLayer registry for laboratory specimen rejection-code vocabularies. Validator consensus determines whether a proposed definition is semantically distinct from every active definition in the exact namespace revision. Deterministic contract logic alone controls registry admission and downstream record creation.

The current reviewed source is schema `semantic-specimen-code-registry-v4`. V4 gives the deployer no owner, administrator, registry or testing role. Any wallet may create an unclaimed namespace; that authenticated creator becomes authority only for that namespace. Validators independently verify consequential `verdict` and `matched_code` fields without requiring identical free-form finding prose. V4 also keeps namespace and global active-code counters synchronized when a code is retired.

- Superseded StudioNet V3 evidence deployment: [0xe8Ed3F6D29eF255855d17b9b647F318C07a8eE3b](https://explorer-studio.genlayer.com/address/0xe8Ed3F6D29eF255855d17b9b647F318C07a8eE3b)
- StudioNet V4: [0xA0839F5509930795B08fB639f2a9436e94DD9F0A](https://explorer-studio.genlayer.com/address/0xA0839F5509930795B08fB639f2a9436e94DD9F0A)
- Deployment record: [docs/STUDIONET_DEPLOYMENT.md](docs/STUDIONET_DEPLOYMENT.md)

## Why GenLayer

Exact string checks cannot detect when differently worded rejection codes are duplicates, dangerously overlapping, or contradictory. GenLayer adjudicates that bounded semantic relation; it does not receive registry or execution authority.

## Authority and evidence

- The deployer receives no operational authority.
- Any wallet may claim a previously unused namespace ID and becomes authority only for that namespace.
- Namespace authority registers curator and recorder addresses.
- A proposal is authoritative only because it was submitted by an enabled curator through `message.sender`.
- The comparison evidence is the complete bounded ACTIVE vocabulary stored on-chain.
- Markdown is documentation, never authority.

## Lifecycle

```text
PENDING_ASSESSMENT ── DISTINCT ──→ ACTIVE ── authority ──→ RETIRED
        ├── DUPLICATE / OVERLAPPING / CONFLICTING ──→ QUARANTINED
        └── malformed / ambiguous / unsafe ─────────→ UNRESOLVED

QUARANTINED or UNRESOLVED ── new immutable revision ──→ PENDING_ASSESSMENT
```

Only an exact ACTIVE code revision can be used by an enabled recorder through `record_rejection`. The contract does not claim to diagnose specimens, validate medical correctness, or observe physical laboratory work.

## Review path

1. Deploy contract; the deployer takes no further action.
2. Wallet A creates an unused namespace and becomes its namespace authority.
3. Wallet A enables a curator and Wallet B as recorder.
4. Curator proposes a rejection code definition.
5. Any wallet calls `assess_proposal`.
6. A `DISTINCT` verdict activates the exact proposal revision.
7. Recorder calls `record_rejection` with that active code.
8. Duplicate, overlapping, conflicting, stale and retired paths fail closed.

## Local verification

```powershell
python -m pytest -q -p no:cacheprovider
python -X utf8 -m genvm_linter.cli check contracts\spec_code.py
```

## Demonstrated boundary

| Demonstrated | Not claimed |
|---|---|
| Semantic distinctness against complete bounded on-chain vocabulary | Medical correctness |
| Sender-authorized namespace roles | External identity verification |
| Exact proposal and registry revision binding | Physical specimen condition |
| Active-code-only downstream records | Laboratory execution |
