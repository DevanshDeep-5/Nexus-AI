import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    text: str
    index: int
    start_char: int
    end_char: int


def clean_text(raw_text: str) -> str:
    """Remove common noise from webpage text."""
    text = re.sub(r'\n{3,}', '\n\n', raw_text)
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # Remove cookie/newsletter noise
    text = re.sub(r'(Cookie|cookie)\s*(policy|consent|settings).*?\n', '', text)
    text = re.sub(r'(Subscribe|Sign up|Newsletter).*?\n', '', text, flags=re.IGNORECASE)

    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()


def truncate_text(text: str, max_length: int) -> str:
    """Cut text to max_length, trying to break at a word boundary."""
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]
    last_space = truncated.rfind(' ')

    # Only break at word boundary if the space is in the last 20% of the text
    if last_space > max_length * 0.8:
        truncated = truncated[:last_space]

    return truncated + "\n\n[Content truncated due to length]"


def chunk_text(text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> list[TextChunk]:
    """Split text into overlapping chunks for RAG."""
    if not text.strip():
        return []

    separators = ['\n\n', '\n', '. ', ', ', ' ']
    chunks: list[TextChunk] = []

    def _split(text: str, sep_idx: int = 0) -> list[str]:
        if len(text) <= chunk_size:
            return [text] if text.strip() else []

        # Hard split if no more separators to try
        if sep_idx >= len(separators):
            result = []
            for i in range(0, len(text), chunk_size - chunk_overlap):
                piece = text[i:i + chunk_size]
                if piece.strip():
                    result.append(piece)
            return result

        sep = separators[sep_idx]
        parts = text.split(sep)
        result = []
        current = ""

        for part in parts:
            candidate = current + sep + part if current else part

            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current.strip():
                    result.append(current)

                if len(part) > chunk_size:
                    result.extend(_split(part, sep_idx + 1))
                    current = ""
                else:
                    current = part

        if current.strip():
            result.append(current)

        return result

    raw_chunks = _split(text)

    char_pos = 0
    for i, chunk in enumerate(raw_chunks):
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
