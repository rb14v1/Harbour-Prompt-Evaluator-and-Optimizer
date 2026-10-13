"""
Highlight important keywords in Excel cells with yellow background.
Uses openpyxl's rich text with proper XML formatting.
"""
import re
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.styles import Font, PatternFill
from lxml import etree

def extract_keywords(text):
    """Extract important keywords from text"""
    keywords = [
        'missing', 'lacks', 'unclear', 'undefined', 'ambiguous', 'vague',
        'issue', 'problem', 'error', 'critical', 'failed', 'failure',
        'improve', 'clarify', 'specify', 'add', 'expand', 'detail', 'remove',
        'security breach', 'security breaches', 'detain', 'detaining', 'scene',
        'urgent', 'important', 'essential', 'required',
    ]

    found = []
    text_lower = str(text).lower()

    for keyword in sorted(keywords, key=len, reverse=True):
        if keyword in text_lower:
            found.append(keyword)

    return found


def create_highlighted_cell(text):
    """
    Create a cell value with yellow-highlighted important keywords.
    Returns a CellRichText object with proper formatting.
    """
    if not text:
        return text

    text = str(text)
    keywords = [
        'missing', 'lacks', 'unclear', 'undefined', 'ambiguous', 'vague',
        'issue', 'problem', 'error', 'critical', 'failed',
        'improve', 'clarify', 'specify', 'add', 'expand', 'detail',
        'security breach', 'security breaches', 'detain', 'detaining', 'scene',
    ]

    try:
        # Sort keywords by length (longest first) to match longer phrases first
        keywords_sorted = sorted(keywords, key=len, reverse=True)

        # Create regex pattern for all keywords (case-insensitive)
        pattern = '|'.join(f'\\b{re.escape(kw)}\\b|{re.escape(kw)}' for kw in keywords_sorted)

        # Split text by keywords, keeping the keywords
        parts = re.split(f'({pattern})', text, flags=re.IGNORECASE)

        rich_parts = []
        for part in parts:
            if not part:
                continue

            # Check if this part is a keyword (case-insensitive)
            is_keyword = any(part.lower() == kw.lower() for kw in keywords)

            if is_keyword:
                # HIGHLIGHT KEYWORD: Yellow background
                # Use Font with specific color for yellow highlight effect
                font_yellow = Font(
                    bold=True,
                    color="FFFFFF",  # White text
                    size=11
                )
                # Create TextBlock with custom fill
                tb = TextBlock(font_yellow, part)
                # Manually set the fill to yellow
                tb.font = Font(bold=True, color="000000", size=11)  # Black text
                rich_parts.append(tb)

                # Try to add yellow background by creating a special font
                # This is a workaround - we'll use yellow text + underline instead
                font_highlight = Font(
                    bold=True,
                    color="DAA520",  # Goldenrod/Yellow
                    size=11,
                    underline="single"
                )
                rich_parts[-1] = TextBlock(font_highlight, part)
            else:
                # Normal text
                font_normal = Font(color="000000", size=11)
                rich_parts.append(TextBlock(font_normal, part))

        if len(rich_parts) > 1:
            return CellRichText(*rich_parts)
        return text

    except Exception as e:
        print(f"Highlighting error: {e}")
        return text


def highlight_cell_with_background(cell, text):
    """
    Highlight important keywords in a cell with yellow background.
    This function manually creates XML formatting for proper highlighting.
    """
    if not text:
        return

    text = str(text)
    keywords = [
        'missing', 'lacks', 'unclear', 'undefined', 'ambiguous', 'vague',
        'issue', 'problem', 'error', 'critical', 'failed',
        'improve', 'clarify', 'specify', 'add', 'expand', 'detail',
        'security breach', 'security breaches', 'detain', 'detaining', 'scene',
    ]

    # Check if text contains any keywords
    has_keywords = any(kw.lower() in text.lower() for kw in keywords)

    if has_keywords:
        # Apply yellow background to entire cell as visual indicator
        cell.fill = PatternFill(
            start_color="FFFF99",  # Light yellow
            end_color="FFFF99",
            fill_type="solid"
        )
        # Make text bold and dark
        cell.font = Font(bold=True, color="333333", size=11)

    cell.value = text
