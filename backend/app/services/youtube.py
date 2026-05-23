"""
YouTube Transcript Service
---------------------------
Fetches the full transcript of a YouTube video using its video ID.
The transcript is returned as a single concatenated string of all
spoken text, which can then be fed into the LLM for analysis.
"""

from youtube_transcript_api import YouTubeTranscriptApi


def fetch_transcript(video_id: str) -> str:
    """
    Fetch and concatenate the transcript for a YouTube video.

    Uses the youtube-transcript-api library which scrapes YouTube's
    auto-generated or manually uploaded captions.

    Args:
        video_id: The 11-character YouTube video ID (e.g., "dQw4w9WgXcQ").

    Returns:
        The full transcript as a single string.

    Raises:
        ValueError: If the transcript cannot be fetched (video not found,
                    no captions available, etc.).
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)

        # Each entry is a snippet with .text, .start, and .duration attributes.
        # We only need the text, joined into one continuous string.
        full_text = " ".join(snippet.text for snippet in transcript)
        return full_text.strip()
    except Exception as e:
        raise ValueError(f"Could not fetch transcript for video {video_id}: {str(e)}")

