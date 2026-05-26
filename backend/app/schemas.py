from pydantic import BaseModel, Field


class PageContent(BaseModel):
    page_content: str
    page_url: str = ""


class SourceExcerpt(BaseModel):
    text: str
    relevance: float = 0.0


class AskRequest(PageContent):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceExcerpt] = []


class SummarizeRequest(PageContent):
    pass


class SummarizeResponse(BaseModel):
    key_points: list[str] = Field(default_factory=list)
    insights: list[str] = Field(default_factory=list)
    takeaway: str = ""


class ELI5Request(PageContent):
    pass


class ELI5Response(BaseModel):
    explanation: str


class KeypointsRequest(PageContent):
    pass


class KeypointsResponse(BaseModel):
    keypoints: list[str] = Field(default_factory=list)


class DebateRequest(PageContent):
    pass


class DebateResponse(BaseModel):
    arguments_for: list[str] = Field(default_factory=list)
    arguments_against: list[str] = Field(default_factory=list)
    verdict: str = ""


class NotesSection(BaseModel):
    heading: str
    bullets: list[str] = Field(default_factory=list)
    key_terms: list[str] = Field(default_factory=list)


class NotesRequest(PageContent):
    pass


class NotesResponse(BaseModel):
    title: str = ""
    sections: list[NotesSection] = Field(default_factory=list)


class CuriosityRequest(PageContent):
    pass


class CuriosityResponse(BaseModel):
    questions: list[str] = Field(default_factory=list)


class YouTubeTranscriptRequest(BaseModel):
    video_id: str


class YouTubeTranscriptResponse(BaseModel):
    transcript: str
    video_id: str


class HighlightActionRequest(BaseModel):
    selected_text: str
    action: str
    page_context: str = ""


class HighlightActionResponse(BaseModel):
    result: str
