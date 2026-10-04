# Threat model

| Threat | Control |
|---|---|
| Deployer privilege or test dependence | Constructor grants no operational role; test wallets create and administer their own namespace |
| Namespace takeover | First-creator binding; an existing namespace ID cannot be overwritten |
| Unauthorized proposal | Namespace-scoped curator mapping bound to `message.sender` |
| Hidden unfavorable comparator | Contract supplies complete bounded ACTIVE vocabulary |
| Verdict reuse | Proposal ID, proposal revision, registry revision and candidate digest binding |
| Registry changes during assessment | Exact registry revision prerequisite |
| Prompt injection in definition | Quoted untrusted-data prompt and closed output schema |
| Hallucinated matched code | Deterministic active-code membership check |
| Malformed or uncertain model output | `UNRESOLVED`, never ACTIVE |
| Duplicate activation | Exact namespace/code existence check |
| Use after retirement | `active` recheck in downstream write |
| Record replay | Globally unique record ID plus namespace/specimen uniqueness |

## Residual limits

The contract cannot establish medical correctness, laboratory identity, physical specimen condition, or completeness beyond the bounded on-chain namespace. Namespace authority selection is explicit operational trust.
