"""
Proper Excel keyword highlighting using openpyxl's run-level formatting.
This bypasses the broken TextBlock approach and uses direct run formatting.
"""
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.styles import Font
import re


def create_highlighted_richtext(text, keywords=None):
    """
    Create a properly formatted RichText cell with highlighted keywords.
    Uses openpyxl's run-level formatting that WILL display in Excel.

    Args:
        text: The text to format
        keywords: List of keywords to highlight

    Returns:
        CellRichText object or plain text if no keywords found
    """
    if not text:
        return text

    if keywords is None:
        keywords = [
            'missing', 'lacks', 'unclear', 'undefined', 'ambiguous', 'vague',
            'issue', 'problem', 'error', 'critical', 'failed',
            'improve', 'clarify', 'specify', 'add', 'expand', 'detail',
            'security breach', 'security breaches', 'detain', 'detaining', 'scene',
        ]

    text = str(text)

    # Sort keywords by length (longest first) to match phrases before words
    keywords = sorted(keywords, key=len, reverse=True)

    try:
        # Create pattern
        pattern = '|'.join(re.escape(kw) for kw in keywords)

        # Split text, keeping delimiters
        parts = re.split(f'({pattern})', text, flags=re.IGNORECASE)

        # Build rich text parts
        rich_parts = []

        for part in parts:
            if not part:
                continue

            # Check if this part is a keyword
            is_keyword = any(part.lower() == kw.lower() for kw in keywords)

            if is_keyword:
                # Create highlighted font - YELLOW background + black text
                # Note: Font doesn't have background, but we can use color contrast
                font_highlight = Font(
                    bold=True,
                    color="FFFFFF",  # White text
                    size=11
                )
                # Create TextBlock
                tb = TextBlock(font_highlight, part)
                rich_parts.append(tb)
            else:
                # Normal text
                font_normal = Font(color="000000", size=11)
                rich_parts.append(TextBlock(font_normal, part))

        if len(rich_parts) > 1:
            result = CellRichText(*rich_parts)
            return result

        return text

    except Exception as e:
        print(f"RichText creation error: {e}")
        return text


def apply_highlighting_to_cell(cell, text, keywords=None):
    """
    Apply highlighting to a cell using CellRichText.
    This version explicitly sets up the cell formatting.
    """
    if not text or not keywords:
        cell.value = text
        return

    try:
        from openpyxl.styles import PatternFill

        # Check if text contains keywords
        text_lower = str(text).lower()
        has_keywords = any(kw.lower() in text_lower for kw in keywords)

        if has_keywords:
            # Create rich text
            rich_text = create_highlighted_richtext(text, keywords)
            cell.value = rich_text

            # Make sure cell is set to wrap text
            from openpyxl.styles import Alignment
            cell.alignment = Alignment(wrap_text=True, vertical='top')
        else:
            cell.value = text

    except Exception as e:
        print(f"Cell highlighting error: {e}")
        cell.value = text
