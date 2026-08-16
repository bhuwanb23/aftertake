"""All AfterTake data shapes, defined in one place (Phase 0 Step 9).

Both the API layer and the agent layer import from here.
Never define a data shape anywhere else.
"""
from pydantic import BaseModel, Field


# --- Schema 1: Source Video ------------------------------------------------
class Performance(BaseModel):
    """Real performance metrics for one catalog video. Null = unknown, not zero."""
    views: int
    likes: int
    comments: int
    shares: int | None = None
    ctr: float | None = Field(default=None, description="Click-through rate, 0.0-100.0")
    avg_retention: float | None = Field(default=None, description="Avg % of video watched, 0.0-100.0")
    watch_time_hours: float


class Thumbnail(BaseModel):
    """Thumbnail reference for one catalog video. description is how the DNA
    agent learns visual style without doing image analysis."""
    url: str = ""
    description: str = ""


class SourceVideo(BaseModel):
    """One past video from the creator's catalog. Raw input to the DNA agent."""
    id: str
    title: str
    description: str = ""
    transcript: str = ""
    duration_seconds: int
    published_at: str  # ISO date (YYYY-MM-DD)
    platform: str = "youtube"  # youtube | tiktok | instagram | linkedin
    performance: Performance
    thumbnail: Thumbnail = Thumbnail()
    tags: list[str] = []
    category: str = ""
