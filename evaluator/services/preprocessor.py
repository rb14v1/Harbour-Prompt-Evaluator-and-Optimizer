import re
from typing import Dict, Any

class Preprocessor:
    """
    Cleans and normalizes prompt text while strictly preserving original meaning and raw prompt.
    """

    @staticmethod
    def process(original_prompt: str) -> Dict[str, str]:
        if not original_prompt:
            return {
                "original_prompt": "",
                "processed_prompt": ""
            }

        # Preserve exact original
        raw = original_prompt

        # 1. Normalize line endings
        text = raw.replace("\r\n", "\n").replace("\r", "\n")

        # 2. Strip surrounding whitespace
        text = text.strip()

        # 3. Collapse multiple consecutive empty lines to maximum of 2
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 4. Normalize trailing spaces on each line
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)

        # 5. Fix common encoding artifacts or weird quotes/spaces
        text = text.replace('\u00a0', ' ')
        text = text.replace('“', '"').replace('”', '"')
        text = text.replace('‘', "'").replace('’', "'")

        # 6. Normalize multiple horizontal whitespace within lines (preserve indentation of code/bullets)
        cleaned_lines = []
        for line in text.split('\n'):
            # If line starts with spaces or tabs (indentation), preserve leading spaces, collapse internal multiple spaces
            leading_match = re.match(r'^(\s*)', line)
            leading = leading_match.group(1) if leading_match else ''
            rest = line[len(leading):]
            normalized_rest = re.sub(r'[ \t]{2,}', ' ', rest)
            cleaned_lines.append(f"{leading}{normalized_rest}")

        processed_prompt = '\n'.join(cleaned_lines).strip()

        return {
            "original_prompt": raw,
            "processed_prompt": processed_prompt
        }
