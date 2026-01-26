"""
Study Service for generating learning recommendations.
This uses mock data - integrate with YouTube API and AI for production.
"""
from typing import List
from app.schemas.study import (
    Resource, 
    YouTubeVideo, 
    VideoSummary,
    StudyRecommendationResponse
)
from app.services.ai_service import generate_summary


# Mock resource database
RESOURCES_DB = {
    "python": {
        "Variable Scope in Python": [
            Resource(
                title="Python Variable Scope Explained",
                url="https://realpython.com/python-scope-legb-rule/",
                description="Comprehensive guide to LEGB rule and variable scope in Python",
                type="article"
            ),
            Resource(
                title="Python Official Documentation - Scopes",
                url="https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces",
                description="Official Python documentation on scopes and namespaces",
                type="documentation"
            ),
        ],
        "Data Types in Python": [
            Resource(
                title="Python Data Types Tutorial",
                url="https://www.w3schools.com/python/python_datatypes.asp",
                description="Learn about built-in data types in Python",
                type="tutorial"
            ),
        ],
        "Error Handling with try/except": [
            Resource(
                title="Python Exception Handling",
                url="https://realpython.com/python-exceptions/",
                description="Master exception handling in Python",
                type="article"
            ),
        ],
        "default": [
            Resource(
                title="Python Tutorial - W3Schools",
                url="https://www.w3schools.com/python/",
                description="Comprehensive Python tutorial for beginners",
                type="tutorial"
            ),
            Resource(
                title="Python Documentation",
                url="https://docs.python.org/3/",
                description="Official Python documentation",
                type="documentation"
            ),
        ]
    }
}

# Mock YouTube videos
YOUTUBE_VIDEOS_DB = {
    "python": {
        "Variable Scope in Python": [
            YouTubeVideo(
                title="Python Variable Scope - Complete Guide",
                url="https://www.youtube.com/watch?v=example1",
                channel="Corey Schafer",
                thumbnail="https://img.youtube.com/vi/example1/mqdefault.jpg",
                duration="15:32"
            ),
            YouTubeVideo(
                title="Understanding LEGB Rule in Python",
                url="https://www.youtube.com/watch?v=example2",
                channel="Tech With Tim",
                thumbnail="https://img.youtube.com/vi/example2/mqdefault.jpg",
                duration="12:45"
            ),
        ],
        "default": [
            YouTubeVideo(
                title="Python Full Course for Beginners",
                url="https://www.youtube.com/watch?v=example3",
                channel="Programming with Mosh",
                thumbnail="https://img.youtube.com/vi/example3/mqdefault.jpg",
                duration="6:00:00"
            ),
            YouTubeVideo(
                title="Python Tutorial - Complete Guide",
                url="https://www.youtube.com/watch?v=example4",
                channel="freeCodeCamp",
                thumbnail="https://img.youtube.com/vi/example4/mqdefault.jpg",
                duration="4:26:52"
            ),
        ]
    }
}


def get_study_recommendations(topics: List[str], language: str = "python") -> StudyRecommendationResponse:
    """Get study recommendations for given topics."""
    
    all_resources = []
    all_videos = []
    
    lang_resources = RESOURCES_DB.get(language, RESOURCES_DB.get("python", {}))
    lang_videos = YOUTUBE_VIDEOS_DB.get(language, YOUTUBE_VIDEOS_DB.get("python", {}))
    
    for topic in topics:
        # Get resources for topic
        topic_resources = lang_resources.get(topic, lang_resources.get("default", []))
        all_resources.extend(topic_resources)
        
        # Get videos for topic
        topic_videos = lang_videos.get(topic, lang_videos.get("default", []))
        all_videos.extend(topic_videos)
    
    # Remove duplicates and limit to top 5
    seen_urls = set()
    unique_resources = []
    for r in all_resources:
        if r.url not in seen_urls:
            seen_urls.add(r.url)
            unique_resources.append(r)
    
    seen_video_urls = set()
    unique_videos = []
    for v in all_videos:
        if v.url not in seen_video_urls:
            seen_video_urls.add(v.url)
            unique_videos.append(v)
    
    # Generate summary for best video (mock)
    best_video_summary = None
    if unique_videos:
        summary_data = generate_summary("Mock transcript for video")
        best_video_summary = VideoSummary(
            title=unique_videos[0].title,
            topics=summary_data["topics"],
            summary=summary_data["summary"],
            key_points=summary_data["key_points"]
        )
    
    return StudyRecommendationResponse(
        topics=topics,
        resources=unique_resources[:5],
        youtube_videos=unique_videos[:5],
        best_video_summary=best_video_summary
    )
