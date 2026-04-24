import copy
import logging
import re
from typing import Any, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SecurityManager")


class SecurityManager:
    def __init__(self):
        # PII Patterns for Malaysian Context
        self.patterns = {
            "IC_NUMBER": r'\d{6}-\d{2}-\d{4}',
            "BANK_ACCOUNT": r'\d{10,16}',
            # "PHONE_NUMBER": r'(\+?6?01)[0-46-9]-?\d{7,8}'
        }

    def regex_scrub(self, raw_text: str) -> str:
        if not isinstance(raw_text, str):
            return ""

        scrubbed_text = raw_text
        scrubbed_text = re.sub(
            self.patterns["IC_NUMBER"],
            lambda matched_value: self.mask_value(matched_value.group(0), "IC_NUMBER"),
            scrubbed_text,
        )
        scrubbed_text = re.sub(
            self.patterns["BANK_ACCOUNT"],
            lambda matched_value: self.mask_value(matched_value.group(0), "BANK_ACCOUNT"),
            scrubbed_text,
        )

        return scrubbed_text


    def mask_value(self, value: str, pii_type: str) -> str:
        if not value or not isinstance(value, str):
            return value
            
        if pii_type == "IC_NUMBER" and len(value) >= 12:
            return f"XXXXXX-XX-{value[-4:]}"
        elif pii_type == "BANK_ACCOUNT" and len(value) >= 4:
            return f"XXXX-XXXX-{value[-4:]}"
        elif pii_type == "PHONE_NUMBER" and len(value) >= 4:
            return f"XXXX-XXX{value[-3:]}"
        return "[REDACTED]"


    def apply_role_based_censorship(self, master_json: Dict[str, Any], user_role: str) -> Dict[str, Any]:
        if user_role == "MANAGER":
            return copy.deepcopy(master_json)
        
        censored_data = copy.deepcopy(master_json)
        
        if master_json.get("security_flags", {}).get("pii_detected"):
            entities = censored_data.get("extracted_entities", {})
            
            pii_types = master_json["security_flags"].get("pii_types", [])
            
            for key, value in entities.items():
                if "ic" in key.lower():
                    entities[key] = self.mask_value(str(value), "IC_NUMBER")
                elif "bank" in key.lower():
                    entities[key] = self.mask_value(str(value), "BANK_ACCOUNT")
            
            # Flag for "Request Access" button in frontend UI
            censored_data["security_flags"]["access_restricted"] = True
            
        return censored_data

    # For future postgreSQL integration
    def log_audit_event(self, user_id: str, action: str, doc_id: str, status: str):
        """Records security events for the Log System"""
        log_entry = {
            "user": user_id,
            "action": action,
            "document": doc_id,
            "status": status
        }
        logger.info(f"AUDIT_LOG | {log_entry}")


if __name__ == "__main__":
    # Create the manager instance
    sm = SecurityManager()

    # 1. Mock Data (The "Master JSON" from your DB/LLM)
    test_data = {
        "doc_id": "TICKET-101",
        "extracted_entities": {
            "user_name": "Ahmad",
            "user_ic": "950101-14-5566",
            "bank_num": "164052334455"
        },
        "security_flags": {
            "pii_detected": True,
            "pii_types": ["IC_NUMBER", "BANK_ACCOUNT"]
        }
    }

    print("--- TESTING ROLE-BASED ACCESS ---")

    # 2. Test Staff View (Should be masked)
    staff_view = sm.apply_role_based_censorship(test_data, user_role="STAFF")
    print(f"\n[STAFF VIEW]:")
    print(f"IC: {staff_view['extracted_entities']['user_ic']}")
    print(f"Restricted: {staff_view['security_flags'].get('access_restricted')}")

    # 3. Test Manager View (Should be full)
    manager_view = sm.apply_role_based_censorship(test_data, user_role="MANAGER")
    print(f"\n[MANAGER VIEW]:")
    print(f"IC: {manager_view['extracted_entities']['user_ic']}")

    # 4. Test Audit Logging
    print("\n--- TESTING AUDIT LOG ---")
    sm.log_audit_event(user_id="Staff_01", action="VIEW_TICKET", doc_id="TICKET-101", status="SUCCESS")
