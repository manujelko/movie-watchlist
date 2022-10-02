from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Movie:
    _id: str
    title: str
    director: str
    year: int
    cast: list[str] = field(default_factory=list)
    series: list[str] = field(default_factory=list)
    last_watched: Optional[datetime] = None
    rating: int = 0
    tags: list[str] = field(default_factory=list)
    description: Optional[str] = None
    video_link: Optional[str] = None
