import json
from pathlib import Path

import pytest

from praxistimate.audit import audit_manifest, load_rules, bundled_rules_path


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def rules():
    return load_rules(bundled_rules_path())


def test_valid_manifest(rules, tmp_path):
    manifest = json.loads((FIXTURES / "valid.json").read_text())
    violations = audit_manifest(manifest, rules)
    assert violations == []


def test_kim_eol(rules):
    manifest = json.loads((FIXTURES / "kim_eol.json").read_text())
    violations = audit_manifest(manifest, rules)
    codes = {v.code for v in violations}
    assert "KIM_VERSION_EOL" in codes


def test_epa_not_ready(rules):
    manifest = json.loads((FIXTURES / "epa_bad.json").read_text())
    violations = audit_manifest(manifest, rules)
    assert any(v.code == "EPA_NOT_READY" for v in violations)
