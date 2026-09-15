import base64
import json
import re

from harness.observability.redaction.entropy_detector import EntropyDetector
from harness.observability.redaction.secret_redactor import SecretRedactor


class DefaultSecretRedactor(SecretRedactor):
    
    def __init__(self, entropy_detector: EntropyDetector):
        self.entropy_detector = entropy_detector
    
    def redact(self, text: str) -> str:
        redacted = text
        
        if "API_KEY" in redacted:
            redacted = re.sub(
                r'API_KEY=[a-zA-Z0-9_-]+', 
                'API_KEY=[REDACTED.API_KEY]', 
                redacted,
                )
        
        if "Authorization:" in redacted:
            redacted = re.sub(
                r"Authorization:\s+Bearer\s+[a-zA-Z0-9._~+/=-]+",
                "Authorization: Bearer [REDACTED.BEARER_TOKEN]",
                redacted,
            )
        
        if "-----BEGIN" in redacted:
            redacted = re.sub(
                r"-----BEGIN([A-Z ]*)PRIVATE KEY-----.*?-----END\1PRIVATE KEY-----",
                "[REDACTED.PRIVATE_KEY]",
                redacted,
                flags=re.DOTALL,
            )
        
        if "." in redacted:
            redacted = re.sub(
                r"[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
                self._replace_jwt,
                redacted,
                )
        
        for candidate in self._extract_candidates(redacted):
            entropy = self.entropy_detector.entropy(candidate)
            
            if entropy >= 4.0 and self._has_multiple_character_classes(candidate):
                        
                    redacted = redacted.replace(
                        candidate,
                        "[REDACTED.SECRET]",
                    )
                
            
        return redacted


    def _is_jwt(self, value: str) -> bool:
        values = value.split(".")
        
        if len(values) != 3:
            return False
        
        padding = "=" * (-len(values[0]) % 4)
        
        try:
            header = base64.urlsafe_b64decode(values[0] + padding)
        except Exception:
            return False
        try:
            header = json.loads(header.decode("utf-8"))
        except Exception:
            return False
        if not isinstance(header, dict):
            return False
        
        if "alg" not in header:
            return False
        
        return True


    def _replace_jwt(self, match):
        candidate = match.group(0)
        
        if self._is_jwt(candidate):
            return "[REDACTED.JWT]"
        
        return candidate


    def _extract_candidates(self, text: str) -> list[str]:
        return re.findall(
            r"(?<![A-Za-z0-9_+/=\-!@#$%^&*.])[A-Za-z0-9_+/=\-!@#$%^&*]{20,}(?![A-Za-z0-9_+/=\-!@#$%^&*.])",
            text,
        )


    def _has_multiple_character_classes(self, candidate: str) -> bool:
        if len(candidate) <= 1:
            return False
        
        first = candidate[0]
        first_type = (
            "lowercase" if first.islower()
            else "uppercase" if first.isupper()
            else "digit" if first.isdigit()
            else "special"
        )
        
        return any(
            ("lowercase" if c.islower()
                else "uppercase" if c.isupper()
                else "digit" if c.isdigit()
                else "special") != first_type
            for c in candidate
        )