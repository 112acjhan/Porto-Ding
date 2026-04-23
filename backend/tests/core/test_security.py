import pytest
import logging
from app.core.security import SecurityManager

# Fixtures
@pytest.fixture
def security_manager():
    return SecurityManager()

@pytest.fixture
def sample_master_json():
    return {
        "fic_id" : "TICKET-101",
        "extracted_entities" :{
            "user_name": "Ahmad",
            "user_ic": "950101-14-5566",
            "bank_num": "164052334455",
        },
        "security_flags": {
            "pii_detected" : True,
            "pii_types" : ["IC_NUMBER", "BANK_ACCOUNT"]
        }
    }

# test: mask_value 
def test_mask_value_ic(security_manager):
    result = security_manager.mask_value("950101-14-5566", "IC_NUMBER")
    assert result == "XXXXXX-XX-5566"

def test_mask_value_bank(security_manager):
    result = security_manager.mask_value("164052334455", "BANK_ACCOUNT")
    assert security_manager.mask_value("", "BANK_ACCOUNT") == ""

def test_mask_value_empty_or_invalid(security_manager):
    assert security_manager.mask_value(None, "IC_NUMBER") is None
    assert security_manager.mask_value("" , "BANK_ACCOUNT") == ""

# test: apply_role_based_censorship
def test_censorship_manager_view(security_manager, sample_master_json):
    result = security_manager.apply_role_based_censorship(sample_master_json, "MANAGER")

    assert result["extracted_entities"]["user_ic"] == "950101-14-5566"
    assert result["extracted_entities"]["bank_num"] == "164052334455"
    assert "access_restricted" not in result.get("security_flags", {})

def test_censorship_staff_view_with_pii(security_manager, sample_master_json):
    result = security_manager.apply_role_based_censorship(sample_master_json, "STAFF")

    entities = result["extracted_entities"]
    flags = result["security_flags"]

    assert entities["user_name"] == "Ahmad"

    assert entities["user_ic"] == "XXXXXX-XX-5566"
    assert entities["bank_num"] == "XXXX-XXXX-4455"

    assert flags["access_restricted"] is True

def test_censorship_staff_view_no_pii(security_manager, sample_master_json):
    sample_master_json["security_flags"]["pii_detected"] = False

    result = security_manager.apply_role_based_censorship(sample_master_json, "STAFF")

    assert result["extracted_entities"]["user_ic"] == "950101-14-5566"
    assert "access_restricted" not in result.get("security_flags", {})

# test: log_audit_event
def test_log_audit_event(security_manager, caplog):
    with caplog.at_level(logging.INFO):
        security_manager.log_audit_event("Staff_01", "VIEW", "DOC-123", "SUCCESS")

        assert "AUDIT_LOG" in caplog.text
        assert "Staff_01" in caplog.text
        assert "DOC-123" in caplog.text