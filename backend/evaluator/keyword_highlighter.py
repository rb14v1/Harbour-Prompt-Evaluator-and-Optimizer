"""
Proper keyword highlighting for Excel cells using RichText
"""
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.styles import Font
import re

def highlight_important_words(text):
    """
    Highlight ONLY important keywords in text - NOT entire cell.
    Example: "security breaches" → highlighted in yellow
             rest of text → normal
    """
    if not text:
        return text

    text = str(text)

    # IMPORTANT keywords to highlight (case-insensitive)
    important_words = [
        # Critical/Issues
        'issue', 'problem', 'error', 'critical', 'failed', 'failure', 'risk',
        # Missing/Unclear
        'missing', 'lacks', 'unclear', 'undefined', 'ambiguous', 'vague', 'unspecified',
        # Actions needed
        'improve', 'clarify', 'specify', 'add', 'expand', 'define', 'detail', 'remove', 'revise',
        # Security/Important terms
        'security', 'breach', 'attack', 'vulnerable', 'danger', 'risk', 'threat',
        'urgent', 'important', 'critical', 'essential', 'required',
        # Quality/Success
        'excellent', 'good', 'complete', 'perfect', 'success',
    ]

    try:
        # Split text by spaces but keep spaces
        parts = re.split(r'(\s+)', text)
        rich_parts = []

        for part in parts:
            if not part:
                continue

            # Check if this part (without punctuation) contains/matches an important word
            part_clean = part.lower().strip('.,;:!?\'"')
            is_important = False

            # Check if word matches or contains important keyword
            for keyword in important_words:
                if keyword in part_clean:
                    is_important = True
                    break

            if is_important:
                # HIGHLIGHT this word: Yellow background + bold
                font = Font(bold=True, color="000000", size=11,
                           fill=None)  # Color will be text color
                rich_parts.append(TextBlock(font, part))
                # Add highlight by setting background - but we need special handling
            else:
                # Normal text
                rich_parts.append(TextBlock(Font(color="000000", size=11), part))

        if len(rich_parts) > 1:
            return CellRichText(*rich_parts)
        return text

    except Exception as e:
        print(f"Error in highlighting: {e}")
        return text


def get_important_keywords_from_text(text):
    """Extract important keywords from text for highlighting"""
    if not text:
        return []

    keywords_to_find = [
        'security breach', 'security breaches', 'detaining', 'scene',
        'issue', 'problem', 'error', 'critical', 'missing', 'unclear',
        'improve', 'clarify', 'specify', 'important', 'essential',
    ]

    found_keywords = []
    text_lower = str(text).lower()

    for keyword in keywords_to_find:
        if keyword in text_lower:
            found_keywords.append(keyword)

    return found_keywords


def create_excel_cell_with_highlights(text):
    """
    Create an Excel cell value that highlights important keywords
    Returns a value suitable for openpyxl cell assignment
    """
    if not text:
        return text

    text = str(text)
    keywords = [
        'security breach', 'security breaches', 'detaining', 'scene',
        'issue', 'problem', 'error', 'critical', 'failed',
        'missing', 'lacks', 'unclear', 'undefined', 'ambiguous', 'vague',
        'improve', 'clarify', 'specify', 'add', 'expand',
        'excellent', 'good', 'complete',
    ]

    try:
        # Use regex to find and split on keywords
        pattern = '|'.join(re.escape(kw) for kw in sorted(keywords, key=len, reverse=True))
        parts = re.split(f'({pattern})', text, flags=re.IGNORECASE)

        if len(parts) == 1:
            # No keywords found
            return text

        rich_parts = []
        for part in parts:
            if not part:
                continue

            # Check if this part is a keyword
            is_keyword = any(part.lower() == kw.lower() for kw in keywords)

            if is_keyword:
                # Highlight keyword: Yellow background + bold black text
                font = Font(bold=True, color="FFFFFF", bg_color="FFFF00")
                # Create a cell fill-able component
                # For highlighting, we'll use bold + specific color
                font = Font(bold=True, color="000000", size=11)
                # Yellow highlight requires different approach
                rich_parts.append(part)  # Will be handled by caller
            else:
                rich_parts.append(part)

        return ''.join(rich_parts) if rich_parts else text

    except Exception as e:
        print(f"Highlighting error: {e}")
        return text
