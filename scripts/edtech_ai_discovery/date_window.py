"""Publication date window helpers for EdTech–AI discovery (stdlib only)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone


@dataclass(frozen=True)
class PublicationWindow:
    start_date: date
    end_date: date
    mode: str  # rolling | fixed
    window_years: int | None
    search_executed_on: date

    def to_bundle_dict(self, executed_at_iso: str) -> dict:
        return {
            "executed_at": executed_at_iso,
            "search_executed_on": self.search_executed_on.isoformat(),
            "publication_window": {
                "start_date": self.start_date.isoformat(),
                "end_date": self.end_date.isoformat(),
                "mode": self.mode,
                "window_years": self.window_years,
                "anchors_on": "initial_publication_date",
                "uses_publication_date_not_citation": True,
            },
        }


def parse_iso_date(value: str) -> date:
    return date.fromisoformat(value.strip()[:10])


def subtract_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year - years)
    except ValueError:
        # Feb 29 → Feb 28
        return d.replace(year=d.year - years, day=28)


def resolve_publication_window(
    *,
    search_executed_on: date,
    window_years: int,
    fixed_start: date | None,
    fixed_end: date | None,
) -> PublicationWindow:
    if fixed_start and fixed_end:
        if fixed_start > fixed_end:
            raise ValueError("fixed_start_date must be on or before fixed_end_date")
        return PublicationWindow(
            start_date=fixed_start,
            end_date=fixed_end,
            mode="fixed",
            window_years=None,
            search_executed_on=search_executed_on,
        )
    start = subtract_years(search_executed_on, window_years)
    return PublicationWindow(
        start_date=start,
        end_date=search_executed_on,
        mode="rolling",
        window_years=window_years,
        search_executed_on=search_executed_on,
    )


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
