from typing import Optional

from pydantic import BaseModel, Field


class PostSearch(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=500
    )


class SearchResponse(BaseModel):
    query: str
    results: list


class HealthResponse(BaseModel):
    status: str
    database: str