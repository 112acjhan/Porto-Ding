import json
from typing import Any

from openai import OpenAI

from app.core.config import settings


class GLMService:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.ZAI_API_KEY,
            base_url="https://api.ilmu.ai/v1",
        )
        self.model = settings.MODEL_NAME

    def is_configured(self) -> bool:
        return bool(settings.ZAI_API_KEY)

    async def classify_message(self, scrubbed_request_text: str) -> dict[str, Any]:
        system_prompt = (
            "You classify SME operations messages into ticket intents. "
            "Return JSON only with these keys: intent_category, formal_summary, query, security_flags. "
            "intent_category must be one of ORDER_PLACEMENT, STOCK_PROCUREMENT, REFUND. "
            "security_flags must be an object with pii_detected and pii_types."
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": scrubbed_request_text},
            ],
            temperature=0,
        )

        assistant_message = response.choices[0].message.content or ""
        return self._parse_classifier_payload(assistant_message, scrubbed_request_text)

    def _parse_classifier_payload(
        self,
        assistant_message: str,
        scrubbed_request_text: str,
    ) -> dict[str, Any]:
        try:
            return json.loads(assistant_message)
        except json.JSONDecodeError:
            json_object_start = assistant_message.find("{")
            json_object_end = assistant_message.rfind("}")
            if json_object_start != -1 and json_object_end != -1:
                candidate_json = assistant_message[json_object_start : json_object_end + 1]
                try:
                    return json.loads(candidate_json)
                except json.JSONDecodeError:
                    pass

        return {
            "intent_category": "REFUND",
            "formal_summary": scrubbed_request_text,
            "query": scrubbed_request_text,
            "security_flags": {"pii_detected": False, "pii_types": []},
            "raw_model_output": assistant_message,
        }
