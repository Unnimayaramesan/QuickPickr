from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=120)
    pincode: str = Field(..., pattern=r"^[1-9][0-9]{5}$")


class RowStatus(str, Enum):
    available = "available"
    unavailable = "unavailable"
    error = "error"


class SearchResultRow(BaseModel):
    retailer: str
    retailerDisplayName: str
    title: str = ""
    packSize: str = ""
    imageUrl: str = ""
    finalPriceInr: float | None = None
    unitPriceLabel: str | None = None
    matchConfidence: Literal["high", "low"] = "high"
    status: RowStatus
    crawledAt: str | None = None
    buyUrl: str | None = None
    message: str | None = None


class SearchMeta(BaseModel):
    cacheHit: bool = False
    latencyMs: int = 0
    vertexServingConfig: str | None = None


class SearchResponse(BaseModel):
    query: str
    pincode: str
    searchedAt: str
    results: list[SearchResultRow]
    meta: SearchMeta


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "error"]
    vertexConfigured: bool
    credentialsPathSet: bool
    servingConfig: str | None = None
    message: str | None = None
