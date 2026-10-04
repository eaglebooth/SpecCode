# StudioNet deployment

- Network: GenLayer StudioNet, chain ID `61999`
- Contract: [`0xA0839F5509930795B08fB639f2a9436e94DD9F0A`](https://explorer-studio.genlayer.com/address/0xA0839F5509930795B08fB639f2a9436e94DD9F0A)
- Schema: `semantic-specimen-code-registry-v4`
- Version: `4`
- Deployer role: none after construction

## Initial canonical readback

```json
{"name":"SpecCode","schema":"semantic-specimen-code-registry-v4","version":4}
{"active_codes":0,"namespaces":0,"records":0}
```

This record proves deployed identity and initial state only. It is not lifecycle evidence. Live write evidence must record finalized transaction hashes and exact post-state readback.

## Superseded deployments

Contract `0x13123DfED868dEC6C4FCfeef5cccB0A4bDB7dc18` is not submission evidence. Two semantic calls ended `UNDETERMINED` because V1 required strict equality over free-form finding prose. No positive state was created.

Contract `0xe8Ed3F6D29eF255855d17b9b647F318C07a8eE3b` is the V3 evidence deployment. Its live run exposed that retirement updated the namespace counter but not the global active-code counter. V4 fixes that invariant and adds a regression test.
