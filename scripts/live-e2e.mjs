import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { createInterface } from "node:readline";
import { createAccount, createClient } from "../../CalScope/node_modules/genlayer-js/dist/index.js";
import { studionet } from "../../CalScope/node_modules/genlayer-js/dist/chains/index.js";

const CONTRACT = "0xA0839F5509930795B08fB639f2a9436e94DD9F0A";
const run = process.argv[2] || Date.now().toString().slice(-10);
const NAMESPACE = `sample-intake-${run}`;

async function readKeys() {
  const rl = createInterface({ input: process.stdin, terminal: false });
  const lines = [];
  return await new Promise((resolve, reject) => {
    rl.on("line", line => {
      const value = line.trim().replace(/^0x/, "");
      if (value) lines.push(value);
      if (lines.length === 2) { rl.close(); resolve(lines); }
    });
    rl.on("close", () => { if (lines.length < 2) reject(new Error("Two keys required on stdin")); });
  });
}

const [keyA, keyB] = await readKeys();
const walletA = createAccount(`0x${keyA}`);
const walletB = createAccount(`0x${keyB}`);
const clientA = createClient({ chain: studionet, account: walletA });
const clientB = createClient({ chain: studionet, account: walletB });

const ids = {
  baseProposal: `base-${run}`,
  duplicateProposal: `duplicate-${run}`,
  overlapProposal: `overlap-${run}`,
  conflictProposal: `conflict-${run}`,
  staleProposal: `stale-${run}`,
  secondDistinctProposal: `second-${run}`,
  record: `record-${run}`,
  replayRecord: `replay-${run}`,
  specimen: `specimen-${run}`,
};
const codes = {
  base: `CLOT_${run}`,
  duplicate: `FIBRIN_${run}`,
  overlap: `BLOOD_DAMAGE_${run}`,
  conflict: `CLOT_ACCEPT_${run}`,
  stale: `LEAK_${run}`,
  second: `ID_MISMATCH_${run}`,
};
const definitions = {
  base: "An anticoagulated whole-blood specimen contains a visible fibrin clot and is unsuitable for hematology analysis.",
  duplicate: "Visible clot material is present in anticoagulated whole blood, making the specimen unacceptable for hematology testing.",
  overlap: "A blood specimen contains clot, fibrin, or related material that may interfere with laboratory testing and requires rejection.",
  conflict: "An anticoagulated whole-blood specimen with a visible fibrin clot must be accepted as suitable for hematology analysis.",
  stale: "The primary specimen container is visibly leaking and cannot be safely processed by laboratory staff.",
  second: "The identity printed on the specimen container does not match the identity on the accompanying laboratory request.",
};

const reportTemplate = {
  contract: CONTRACT,
  network: "GenLayer StudioNet 61999",
  namespace: NAMESPACE,
  run,
  actors: { curator: walletA.address, recorder: walletB.address },
  ids,
  codes,
  transactions: [],
  assertions: [],
  final: {},
};
mkdirSync("docs/live-evidence", { recursive: true });
const path = `docs/live-evidence/studionet-${run}.json`;
const report = existsSync(path) ? JSON.parse(readFileSync(path, "utf8")) : reportTemplate;
const save = () => writeFileSync(path, `${JSON.stringify(report, null, 2)}\n`);
const check = (condition, label, details = {}) => {
  report.assertions.push({ label, pass: Boolean(condition), details }); save();
  if (!condition) throw new Error(`Assertion failed: ${label} ${JSON.stringify(details)}`);
};
const read = async (method, args = []) => JSON.parse(await clientA.readContract({ address: CONTRACT, functionName: method, args }));
const execution = tx => {
  const validators = tx.consensus_data?.validators || [];
  if (validators.some(v => v.vote === "agree" && v.execution_result === "SUCCESS")) return "SUCCESS";
  if (validators.some(v => v.vote === "agree" && v.execution_result === "ERROR")) return "ERROR";
  const leader = tx.consensus_data?.leader_receipt?.[0]?.genvm_result;
  return leader && !leader.error_code ? "SUCCESS" : leader?.error_code ? "ERROR" : "UNKNOWN";
};
const write = async (label, client, method, args, expected = "SUCCESS") => {
  const hash = await client.writeContract({ address: CONTRACT, functionName: method, args, value: 0n });
  process.stdout.write(`${label}: ${hash}\n`);
  let tx = {};
  for (let i = 0; i < 360; i++) {
    try {
      tx = await client.getTransaction({ hash });
    } catch (error) {
      process.stdout.write(`RPC poll retry ${i + 1}: ${String(error).slice(0, 120)}\n`);
      await new Promise(resolve => setTimeout(resolve, 2500));
      continue;
    }
    if (["FINALIZED", "CANCELED", "UNDETERMINED"].includes(tx.statusName)) break;
    await new Promise(resolve => setTimeout(resolve, 2500));
  }
  const result = execution(tx);
  report.transactions.push({ label, method, expected, hash, status: tx.statusName || "UNKNOWN", execution: result }); save();
  check(tx.statusName === "FINALIZED" && result === expected, `${label} finalized with ${expected}`, { hash, status: tx.statusName, execution: result });
  return hash;
};

const ensureProposal = async (label, proposalId, code, definition) => {
  const state = await read("get_proposal", [proposalId]);
  if (!state.exists) await write(label, clientA, "propose_code", [proposalId, NAMESPACE, code, definition]);
  return await read("get_proposal", [proposalId]);
};

const ensureAssessment = async (label, proposalId) => {
  const state = await read("get_proposal", [proposalId]);
  if (state.status === "PENDING_ASSESSMENT") await write(label, clientB, "assess_proposal", [proposalId]);
  return await read("get_proposal", [proposalId]);
};

const version = await read("get_contract_version");
check(version.name === "SpecCode" && version.schema === "semantic-specimen-code-registry-v4", "deployed SpecCode V4 identity", version);
let initial = await read("get_namespace", [NAMESPACE]);
if (!initial.exists) {
  await write("wallet A creates independent namespace", clientA, "create_namespace", [NAMESPACE]);
  await write("wallet A enables itself as curator", clientA, "set_curator", [NAMESPACE, walletA.address, true]);
  await write("wallet A enables wallet B as recorder", clientA, "set_recorder", [NAMESPACE, walletB.address, true]);
  initial = await read("get_namespace", [NAMESPACE]);
}
check(initial.exists && initial.authority === walletA.address.toLowerCase(), "wallet A owns exact namespace without deployer involvement", initial);

let baseState = await read("get_proposal", [ids.baseProposal]);
if (!baseState.exists) {
  await write("curator proposes base code", clientA, "propose_code", [ids.baseProposal, NAMESPACE, codes.base, definitions.base]);
  baseState = await read("get_proposal", [ids.baseProposal]);
}
if (baseState.status === "PENDING_ASSESSMENT") {
  await write("assess base as distinct", clientB, "assess_proposal", [ids.baseProposal]);
}
const base = await read("get_proposal", [ids.baseProposal]);
check(base.status === "ACTIVE" && base.verdict === "DISTINCT", "base code activated by consensus", base);

let record = await read("get_record", [ids.record]);
if (!record.exists) {
  await write("recorder creates exact rejection record", clientB, "record_rejection", [ids.record, NAMESPACE, ids.specimen, codes.base]);
  record = await read("get_record", [ids.record]);
}
check(record.exists && record.code === codes.base && record.specimen_ref === ids.specimen, "record exact readback", record);
await write("reject record-id replay", clientB, "record_rejection", [ids.record, NAMESPACE, `other-${run}`, codes.base], "ERROR");
await write("reject specimen replay under new record id", clientB, "record_rejection", [ids.replayRecord, NAMESPACE, ids.specimen, codes.base], "ERROR");
await write("reject curator acting as recorder", clientA, "record_rejection", [`wrong-${run}`, NAMESPACE, `wrong-${run}`, codes.base], "ERROR");
await write("reject recorder acting as curator", clientB, "propose_code", [`forged-${run}`, NAMESPACE, `FORGED_${run}`, definitions.second], "ERROR");

await ensureProposal("curator proposes semantic duplicate", ids.duplicateProposal, codes.duplicate, definitions.duplicate);
const duplicate = await ensureAssessment("assess duplicate", ids.duplicateProposal);
check(duplicate.status === "QUARANTINED" && duplicate.verdict === "DUPLICATE" && duplicate.matched_code === codes.base, "duplicate quarantined", duplicate);

await ensureProposal("curator proposes overlap", ids.overlapProposal, codes.overlap, definitions.overlap);
const overlap = await ensureAssessment("assess overlap", ids.overlapProposal);
check(overlap.status === "QUARANTINED" && overlap.verdict === "OVERLAPPING", "overlap quarantined", overlap);

await ensureProposal("curator proposes conflict", ids.conflictProposal, codes.conflict, definitions.conflict);
const conflict = await ensureAssessment("assess conflict", ids.conflictProposal);
check(conflict.status === "QUARANTINED" && conflict.verdict === "CONFLICTING", "conflict quarantined", conflict);

await ensureProposal("curator seals proposal that will become stale", ids.staleProposal, codes.stale, definitions.stale);
await ensureProposal("curator proposes second distinct code", ids.secondDistinctProposal, codes.second, definitions.second);
const second = await ensureAssessment("assess second distinct code", ids.secondDistinctProposal);
check(second.status === "ACTIVE" && second.verdict === "DISTINCT", "second distinct code activated", second);
const staleBefore = await read("get_proposal", [ids.staleProposal]);
if (staleBefore.status === "PENDING_ASSESSMENT") await write("reject stale candidate-set assessment", clientB, "assess_proposal", [ids.staleProposal], "ERROR");
const staleAfter = await read("get_proposal", [ids.staleProposal]);
check(JSON.stringify(staleBefore) === JSON.stringify(staleAfter) && staleAfter.status === "PENDING_ASSESSMENT", "stale rejection preserved complete proposal state", { before: staleBefore, after: staleAfter });

let retiredBase = await read("get_code", [NAMESPACE, codes.base]);
if (retiredBase.active) {
  await write("namespace authority retires base code", clientA, "retire_code", [NAMESPACE, codes.base]);
  retiredBase = await read("get_code", [NAMESPACE, codes.base]);
}
check(retiredBase.exists && retiredBase.active === false, "retired code canonical readback", retiredBase);
await write("reject recorder retiring active code", clientB, "retire_code", [NAMESPACE, codes.second], "ERROR");
const finalNamespace = await read("get_namespace", [NAMESPACE]);
const stats = await read("get_stats");
check(stats.active_codes >= 1 && stats.records >= 1, "canonical final counters", stats);
check(stats.active_codes === finalNamespace.active_count, "global and namespace active-code counters agree", {
  global_active_codes: stats.active_codes,
  namespace_active_count: finalNamespace.active_count,
});
report.final = { version, initial, base, record, duplicate, overlap, conflict, second, stale: staleAfter, retiredBase, namespace: finalNamespace, stats };
save();
process.stdout.write(`Evidence: ${path}\n`);
