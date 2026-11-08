"""Shared API dependencies and helpers."""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from fastapi import Query

from app.schemas.common import Page


@dataclass
class Pagination:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
) -> Pagination:
    return Pagination(page=page, page_size=page_size)


def build_page(items: list, total: int, pg: Pagination) -> Page:
    return Page(
        items=items,
        total=total,
        page=pg.page,
        page_size=pg.page_size,
        pages=ceil(total / pg.page_size) if pg.page_size else 0,
    )
