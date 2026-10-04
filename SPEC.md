# SpecCode specification

## Proof obligation

The only positive claim is: the exact proposed definition is semantically distinct from every ACTIVE definition in the exact committed namespace revision.

## Consensus boundary

The leader proposes `verdict`, `matched_code`, and a substantive finding. Validators independently accept only when the consequential verdict and matched code are semantically correct and the finding supports them. Free-form wording is not part of consensus equivalence. Only `DISTINCT` can create an ACTIVE code. Malformed output, ambiguity, missing candidate identity, disagreement or stale registry state cannot produce a positive state.

## Deterministic enforcement

- No deployer owner or global administration role.
- First authenticated creator owns only the exact unused namespace ID it creates.
- Namespace-scoped sender authorization.
- Complete candidate-set commitment.
- Exact proposal and registry revision binding.
- Maximum 16 immutable code slots per namespace; retired slots remain auditable and are never reused.
- Immutable activated definition.
- Quarantine/revision instead of verdict override.
- Exact ACTIVE code required on downstream records.
- Record ID replay protection.
- One rejection classification per exact namespace/specimen reference.

## Threat boundary

Definitions are untrusted quoted data. They may contain prompt injection, misleading language or invented claims. The prompt confines adjudication to semantic relations between definitions. The contract never treats a definition as an instruction or evidence of a physical specimen fact.
