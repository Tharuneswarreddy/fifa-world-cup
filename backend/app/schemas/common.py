"""Shared/common response schemas."""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class Provenance(BaseModel):
    source: str | None = None
    license: str | None = None
    confidence: str | None = None
    note: str | None = None
