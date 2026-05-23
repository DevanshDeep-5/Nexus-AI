"""
Text Processing Utilities
--------------------------
Provides helper functions for cleaning, truncating, and chunking
raw webpage text before it's sent to the LLM or embedding model.

The main functions are:
  - clean_text():    Removes noise (ads, cookie banners, excess whitespace)
  - truncate_text(): Cuts text to a max length to respect token limits
  - chunk_text():    Splits long text into overlapping chunks for RAG retrieval
"""

import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    """
    Represents one chunk of text extracted from a page.

    Attributes:
        text:       The actual text content of this chunk.
        index:      The chunk's position in the sequence (0-based).
        start_char: The starting character offset in the original text.
        end_char:   The ending character offset in the original text.
    """
    text: str
    index: int
    start_char: int
    end_char: int


def clean_text(raw_text: str) -> str:
    """
    Remove common noise patterns from extracted webpage text.

    This handles:
      - Excessive newlines (3+ collapsed to 2)
      - Excessive spaces/tabs (collapsed to single space)
      - Cookie consent / privacy policy lines
      - Newsletter signup prompts

    Args:
        raw_text: The raw text extracted from the webpage DOM.

    Returns:
        Cleaned text with noise removed.
    """
    # Collapse excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', raw_text)
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # Remove common noise patterns found on most websites
    text = re.sub(r'(Cookie|cookie)\s*(policy|consent|settings).*?\n', '', text)
    text = re.sub(r'(Subscribe|Sign up|Newsletter).*?\n', '', text, flags=re.IGNORECASE)

    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()


def truncate_text(text: str, max_length: int) -> str:
    """
    Truncate text to a maximum character length, breaking at a word boundary.

    This prevents sending excessively long content to the LLM, which would
    exceed token limits and cause API errors.

    Args:
        text:       The text to potentially truncate.
        max_length: Maximum allowed character count.

    Returns:
        The original text if it's short enough, or a truncated version
        with a "[Content truncated]" notice appended.
    """
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]

    # Try to break at the last space to avoid cutting mid-word.
    # Only do this if the last space is in the final 20% of the text,
    # otherwise we'd lose too much content.
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:
        truncated = truncated[:last_space]

    return truncated + "\n\n[Content truncated due to length]"


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> list[TextChunk]:
    """
    Split text into overlapping chunks using recursive character splitting.

    The algorithm tries to split on natural boundaries in this priority order:
      1. Paragraph breaks (\\n\\n)
      2. Line breaks (\\n)
      3. Sentence endings ('. ')
      4. Clause boundaries (', ')
      5. Word boundaries (' ')
      6. Hard character split (as last resort)

    Overlap between chunks ensures that context isn't lost at boundaries,
    which improves retrieval accuracy in the RAG pipeline.

    Args:
        text:          The cleaned text to split.
        chunk_size:    Target maximum characters per chunk.
        chunk_overlap: Number of characters to overlap between adjacent chunks.

    Returns:
        List of TextChunk objects with position metadata.
    """
    if not text.strip():
        return []

    # Ordered list of separators to try, from most preferred to least
    separators = ['\n\n', '\n', '. ', ', ', ' ']
    chunks: list[TextChunk] = []

    def _split_recursive(text: str, sep_idx: int = 0) -> list[str]:
        """Recursively split text using progressively finer separators."""

        # Base case: text fits in one chunk
        if len(text) <= chunk_size:
            return [text] if text.strip() else []

        # If we've exhausted all separators, force-split at chunk_size
        if sep_idx >= len(separators):
            result = []
            for i in range(0, len(text), chunk_size - chunk_overlap):
                piece = text[i:i + chunk_size]
                if piece.strip():
                    result.append(piece)
            return result

        # Try splitting on the current separator
        sep = separators[sep_idx]
        parts = text.split(sep)
        result = []
        current = ""

        for part in parts:
            # Try adding this part to the current accumulator
            candidate = current + sep + part if current else part

            if len(candidate) <= chunk_size:
                # Still fits — keep accumulating
                current = candidate
            else:
                # Doesn't fit — save current and start fresh
                if current.strip():
                    result.append(current)

                # If this single part is too long, split it with a finer separator
                if len(part) > chunk_size:
                    result.extend(_split_recursive(part, sep_idx + 1))
                    current = ""
                else:
                    current = part

        # Don't forget the last accumulated text
        if current.strip():
            result.append(current)

        return result

    # Split the text into raw chunks
    raw_chunks = _split_recursive(text)

    # Build TextChunk objects with character position metadata
    char_pos = 0
    for i, chunk in enumerate(raw_chunks):
        # Find this chunk's position in the original text
        start = text.find(chunk, max(0, char_pos - chunk_overlap))
        if start == -1:
            start = char_pos
        end = start + len(chunk)

        chunks.append(TextChunk(
            text=chunk.strip(),
            index=i,
            start_char=start,
            end_char=end,
        ))
        char_pos = end

    return chunks
