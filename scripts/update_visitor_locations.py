#!/usr/bin/env python3
"""Fetch GoatCounter country stats and write a JSON payload for the map."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="files/visitor-locations.json")
    parser.add_argument("--site-code", default=os.environ.get("GOATCOUNTER_SITE_CODE", "zhengzhou"))
    parser.add_argument("--api-token", default=os.environ.get("GOATCOUNTER_API_TOKEN", ""))
    parser.add_argument("--start", default="2000-01-01T00:00:00Z")
    parser.add_argument("--end", default="")
    parser.add_argument("--limit", type=int, default=200)
    return parser.parse_args()


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_url(site_code: str, start: str, end: str, limit: int) -> str:
    params = {"start": start, "limit": str(limit)}
    if end:
        params["end"] = end
    return f"https://{site_code}.goatcounter.com/api/v0/stats/locations?{urllib.parse.urlencode(params)}"


def write_payload(output_path: pathlib.Path, payload: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def empty_payload(site_code: str, message: str) -> dict:
    return {
        "updated_at": utc_now_iso(),
        "site_code": site_code,
        "source": "GoatCounter",
        "message": message,
        "total": 0,
        "locations": [],
    }


def fetch_locations(api_token: str, site_code: str, start: str, end: str, limit: int) -> dict:
    if not api_token:
        return empty_payload(site_code, "Visitor map will appear after the next scheduled update.")

    request = urllib.request.Request(
        build_url(site_code, start, end, limit),
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
        return {
            "updated_at": utc_now_iso(),
            "site_code": site_code,
            "source": "GoatCounter",
            "error": f"{exc.__class__.__name__}: {exc}",
            "total": 0,
            "locations": [],
        }

    rows = payload.get("stats") or payload.get("hits") or []
    
    # Keep Plotly's recognized location name separate from the public display name.
    display_name_mapping = {
        "Taiwan": {"name": "Taiwan, China", "zh_name": "中国台湾"},
        "Hong Kong": {"name": "Hong Kong, China", "zh_name": "中国香港"},
        "Macau": {"name": "Macau, China", "zh_name": "中国澳门"},
        "Macao": {"name": "Macao, China", "zh_name": "中国澳门"},
    }
    
    locations = []
    for row in rows:
        name = row.get("name") or row.get("id")
        count = row.get("count", 0)
        if not name or not count:
            continue
        mapped_name = display_name_mapping.get(name)
        item = {"name": mapped_name["name"] if mapped_name else name, "count": int(count)}
        if mapped_name:
            item["zh_name"] = mapped_name["zh_name"]
        if name in display_name_mapping:
            item["plotly_name"] = name
        location_id = row.get("id")
        if isinstance(location_id, str) and len(location_id) == 2:
            item["country_code"] = location_id.upper()
        locations.append(item)

    locations.sort(key=lambda item: item["count"], reverse=True)

    return {
        "updated_at": utc_now_iso(),
        "site_code": site_code,
        "source": "GoatCounter",
        "total": payload.get("total", sum(item["count"] for item in locations)),
        "locations": locations,
    }


def main() -> int:
    args = parse_args()
    payload = fetch_locations(args.api_token, args.site_code, args.start, args.end, args.limit)
    write_payload(pathlib.Path(args.output), payload)
    if payload.get("error"):
        print(payload["error"], file=sys.stderr)
    else:
        print(f"Wrote {args.output} with {len(payload.get('locations', []))} locations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
