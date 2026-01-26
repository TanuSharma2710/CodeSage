from pydantic import BaseModel
from typing import List, Optional


class Resource(BaseModel):
    title: str
    url: str
    description: str
    type: str  # article, documentation, tutorial


class YouTubeVideo(BaseModel):
    title: str
    url: str
    channel: str
    thumbnail: Optional[str] = None
    duration: Optional[str] = None


class VideoSummary(BaseModel):
    title: str
    topics: List[str]
    summary: str
    key_points: List[str]


class StudyRecommendationRequest(BaseModel):
    topics: List[str]
    language: str = "python"


class StudyRecommendationResponse(BaseModel):
    topics: List[str]
    resources: List[Resource]
    youtube_videos: List[YouTubeVideo]
    best_video_summary: Optional[VideoSummary] = None
