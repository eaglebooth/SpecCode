import json
import pytest


def addr(value):
    return "0x" + bytes(value).hex()


BASE = "Specimen contains visible fibrin clot material in an anticoagulated whole-blood tube, making hematology analysis unsuitable."
DISTINCT = "Specimen identity on the tube does not match the identity on the accompanying laboratory request."
DUPLICATE = "Anticoagulated whole blood has visible clot material and cannot be accepted for hematology testing."
OVERLAP = "Blood sample has clot or fibrin material that may interfere with testing and requires rejection."


def deploy_ready(direct_deploy, direct_vm, curator, recorder):
    c = direct_deploy("contracts/spec_code.py")
    c.create_namespace("sample-intake")
    c.set_curator("sample-intake", addr(curator), True)
    c.set_recorder("sample-intake", addr(recorder), True)
    return c


def mock(direct_vm, verdict, matched_code="", finding="The proposed definition has a separate operational classification scope."):
    direct_vm.mock_llm(
        r"Classify one proposed laboratory specimen rejection-code definition",
        json.dumps({"verdict": verdict, "matched_code": matched_code, "finding": finding}),
    )
    direct_vm.mock_llm(
        r"Independently verify one proposed semantic-collision judgment",
        json.dumps({"valid": True}),
    )


def activate_base(c, vm, curator):
    with vm.prank(curator):
        c.propose_code("proposal-clotted", "sample-intake", "CLOTTED", BASE)
    mock(vm, "DISTINCT")
    assert c.assess_proposal("proposal-clotted") == "DISTINCT"


def test_schema_and_deployer_has_no_global_authority(direct_deploy, direct_vm, direct_owner, direct_alice):
    c = direct_deploy("contracts/spec_code.py")
    assert json.loads(c.get_contract_version()) == {
        "name": "SpecCode",
        "schema": "semantic-specimen-code-registry-v4",
        "version": 4,
    }
    with direct_vm.prank(direct_alice):
        c.create_namespace("sample-intake")
    namespace = json.loads(c.get_namespace("sample-intake"))
    assert namespace["authority"] == addr(direct_alice).lower()
    with direct_vm.expect_revert("NAMESPACE_AUTHORITY_REQUIRED"):
        c.set_curator("sample-intake", addr(direct_owner), True)


def test_namespace_ids_are_first_creator_claimed_and_not_overwritable(direct_deploy, direct_vm, direct_alice, direct_bob):
    c = direct_deploy("contracts/spec_code.py")
    with direct_vm.prank(direct_alice):
        c.create_namespace("hematology-lab-a")
    with direct_vm.prank(direct_bob), direct_vm.expect_revert("NAMESPACE_ALREADY_EXISTS"):
        c.create_namespace("hematology-lab-a")
    assert json.loads(c.get_namespace("hematology-lab-a"))["authority"] == addr(direct_alice).lower()


def test_distinct_code_activates_and_can_be_used(direct_deploy, direct_vm, direct_alice, direct_bob):
    c = deploy_ready(direct_deploy, direct_vm, direct_alice, direct_bob)
    activate_base(c, direct_vm, direct_alice)
    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        c.propose_code("proposal-mismatch", "sample-intake", "ID_MISMATCH", DISTINCT)
    mock(direct_vm, "DISTINCT")
    assert c.assess_proposal("proposal-mismatch") == "DISTINCT"
    code = json.loads(c.get_code("sample-intake", "ID_MISMATCH"))
    assert code["active"] is True and code["proposal_revision"] == 1
    with direct_vm.prank(direct_bob):
        receipt = c.record_rejection("record-001", "sample-intake", "specimen-001", "ID_MISMATCH")
    assert len(receipt) == 64
    assert json.loads(c.get_record("record-001"))["code"] == "ID_MISMATCH"


@pytest.mark.parametrize(
    "verdict,definition",
    [("DUPLICATE", DUPLICATE), ("OVERLAPPING", OVERLAP), ("CONFLICTING", "Clotted anticoagulated blood must be accepted as suitable for routine hematology analysis.")],
)
def test_collision_verdicts_quarantine_and_block_use(direct_deploy, direct_vm, direct_alice, direct_bob, verdict, definition):
    c = deploy_ready(direct_deploy, direct_vm, direct_alice, direct_bob)
    activate_base(c, direct_vm, direct_alice)
    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        c.propose_code("proposal-new", "sample-intake", "NEW_CODE", definition)
    mock(direct_vm, verdict, "CLOTTED", "The proposal collides with the active CLOTTED classification scope.")
    assert c.assess_proposal("proposal-new") == verdict
    proposal = json.loads(c.get_proposal("proposal-new"))
    assert proposal["status"] == "QUARANTINED" and proposal["matched_code"] == "CLOTTED"
    assert "collides" in proposal["finding"] and len(proposal["finding_digest"]) == 64
    with direct_vm.prank(direct_bob), direct_vm.expect_revert("ACTIVE_CODE_REQUIRED"):
        c.record_rejection("record-bad", "sample-intake", "specimen-bad", "NEW_CODE")
    assert json.loads(c.get_record("record-bad")) == {"exists": False}


def test_malformed_model_output_fails_closed(direct_deploy, direct_vm, direct_alice, direct_bob):
    c = deploy_ready(direct_deploy, direct_vm, direct_alice, direct_bob)
    with direct_vm.prank(direct_alice):
        c.propose_code("proposal-malformed", "sample-intake", "LABEL_DAMAGE", DISTINCT)
    direct_vm.mock_llm(r"Classify one proposed laboratory specimen rejection-code definition", '{"verdict":"DISTINCT","extra":true}')
    direct_vm.mock_llm(r"Independently verify one proposed semantic-collision judgment", '{"valid":true}')
    assert c.assess_proposal("proposal-malformed") == "UNRESOLVED"
    assert json.loads(c.get_proposal("proposal-malformed"))["status"] == "UNRESOLVED"
    assert json.loads(c.get_code("sample-intake", "LABEL_DAMAGE")) == {"exists": False}


def test_validator_independently_accepts_or_rejects_consequential_judgment(direct_deploy, direct_vm, direct_alice, direct_bob):
    c = deploy_ready(direct_deploy, direct_vm, direct_alice, direct_bob)
    with direct_vm.prank(direct_alice):
        c.propose_code("proposal-validated", "sample-intake", "ID_MISMATCH", DISTINCT)
    mock(direct_vm, "DISTINCT")
    assert c.assess_proposal("proposal-validated") == "DISTINCT"
    assert direct_vm.run_validator() is True
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"Independently verify one proposed semantic-collision judgment", json.dumps({"valid": False}))
    assert direct_vm.run_validator() is False


def test_unknown_matched_code_becomes_unresolved(direct_deploy, direct_vm, direct_alice, direct_bob):
    c = deploy_ready(direct_deploy, direct_vm, direct_alice, direct_bob)
    activate_base(c, direct_vm, direct_alice)
    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        c.propose_code("proposal-ghost", "sample-intake", "GHOST_SCOPE", DUPLICATE)
    mock(direct_vm, "DUPLICATE", "NOT_ACTIVE", "The proposal appears to match a code absent from the committed candidate set.")
    assert c.assess_proposal("proposal-ghost") == "UNRESOLVED"
    assert json.loads(c.get_proposal("proposal-ghost"))["status"] == "UNRESOLVED"


def test_stale_registry_revision_rejects_without_mutation(direct_deploy, direct_vm, direct_alice, direct_bob):
    c = deploy_ready(direct_deploy, direct_vm, direct_alice, direct_bob)
    with direct_vm.prank(direct_alice):
        c.propose_code("proposal-stale", "sample-intake", "ID_MISMATCH", DISTINCT)
        c.propose_code("proposal-base", "sample-intake", "CLOTTED", BASE)
    mock(direct_vm, "DISTINCT")
    assert c.assess_proposal("proposal-base") == "DISTINCT"
    before = json.loads(c.get_proposal("proposal-stale"))
    with direct_vm.expect_revert("REGISTRY_REVISION_CHANGED"):
        c.assess_proposal("proposal-stale")
    after = json.loads(c.get_proposal("proposal-stale"))
    assert before == after and after["status"] == "PENDING_ASSESSMENT"


def test_only_registered_curator_can_propose(direct_deploy, direct_vm, direct_alice, direct_bob):
    c = deploy_ready(direct_deploy, direct_vm, direct_alice, direct_bob)
    before = json.loads(c.get_namespace("sample-intake"))
    with direct_vm.prank(direct_bob), direct_vm.expect_revert("REGISTERED_CURATOR_REQUIRED"):
        c.propose_code("proposal-forged", "sample-intake", "FORGED", DISTINCT)
    assert json.loads(c.get_namespace("sample-intake")) == before
    assert json.loads(c.get_proposal("proposal-forged")) == {"exists": False}


def test_revision_requires_original_curator_and_new_assessment(direct_deploy, direct_vm, direct_alice, direct_bob):
    c = deploy_ready(direct_deploy, direct_vm, direct_alice, direct_bob)
    activate_base(c, direct_vm, direct_alice)
    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        c.propose_code("proposal-revise", "sample-intake", "CELL_DAMAGE", DUPLICATE)
    mock(direct_vm, "DUPLICATE", "CLOTTED", "The original definition duplicates the active CLOTTED scope.")
    assert c.assess_proposal("proposal-revise") == "DUPLICATE"
    with direct_vm.prank(direct_bob), direct_vm.expect_revert("PROPOSAL_CURATOR_REQUIRED"):
        c.revise_proposal("proposal-revise", DISTINCT)
    with direct_vm.prank(direct_alice):
        c.revise_proposal("proposal-revise", DISTINCT)
    revised = json.loads(c.get_proposal("proposal-revise"))
    assert revised["revision"] == 2 and revised["status"] == "PENDING_ASSESSMENT" and revised["verdict"] == ""
    assert revised["finding"] == "" and revised["finding_digest"] == ""


def test_retired_code_cannot_be_used(direct_deploy, direct_vm, direct_alice, direct_bob):
    c = deploy_ready(direct_deploy, direct_vm, direct_alice, direct_bob)
    activate_base(c, direct_vm, direct_alice)
    c.retire_code("sample-intake", "CLOTTED")
    namespace = json.loads(c.get_namespace("sample-intake"))
    assert namespace["active_count"] == 0 and namespace["code_slot_count"] == 1
    assert json.loads(c.get_stats()) == {"namespaces": 1, "active_codes": 0, "records": 0}
    with direct_vm.prank(direct_bob), direct_vm.expect_revert("ACTIVE_CODE_REQUIRED"):
        c.record_rejection("record-retired", "sample-intake", "specimen-retired", "CLOTTED")
    assert json.loads(c.get_record("record-retired")) == {"exists": False}


def test_record_replay_and_wrong_recorder_fail_closed(direct_deploy, direct_vm, direct_alice, direct_bob):
    c = deploy_ready(direct_deploy, direct_vm, direct_alice, direct_bob)
    activate_base(c, direct_vm, direct_alice)
    with direct_vm.prank(direct_alice), direct_vm.expect_revert("REGISTERED_RECORDER_REQUIRED"):
        c.record_rejection("record-001", "sample-intake", "specimen-001", "CLOTTED")
    with direct_vm.prank(direct_bob):
        c.record_rejection("record-001", "sample-intake", "specimen-001", "CLOTTED")
    before = json.loads(c.get_record("record-001"))
    with direct_vm.prank(direct_bob), direct_vm.expect_revert("RECORD_ALREADY_EXISTS"):
        c.record_rejection("record-001", "sample-intake", "specimen-other", "CLOTTED")
    assert json.loads(c.get_record("record-001")) == before
    with direct_vm.prank(direct_bob), direct_vm.expect_revert("SPECIMEN_ALREADY_RECORDED"):
        c.record_rejection("record-002", "sample-intake", "specimen-001", "CLOTTED")
    assert json.loads(c.get_record("record-002")) == {"exists": False}
    assert json.loads(c.get_stats()) == {"namespaces": 1, "active_codes": 1, "records": 1}
