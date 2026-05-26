from youtube_transcript_api import YouTubeTranscriptApi


def fetch_transcript(video_id: str) -> str:
    """Fetch the transcript for a YouTube video and return it as one string."""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        return " ".join(snippet.text for snippet in transcript).strip()
    except Exception as e:
        raise ValueError(f"Could not fetch transcript for video {video_id}: {str(e)}")
