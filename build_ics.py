#!/usr/bin/env python3
"""Build events.ics from events.json. Drops past events; UIDs are stable so
Apple Calendar updates entries in place instead of duplicating them."""
import hashlib, json, sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).parent
cfg = json.loads((ROOT / "config.json").read_text())
tz = ZoneInfo(cfg["timezone"])
events = json.loads((ROOT / "events.json").read_text())


def esc(s):
    return (s or "").replace("\\", "\\\\").replace(";", r"\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    # RFC 5545: lines longer than 75 octets are folded.
    out, b = [], line.encode()
    while len(b) > 75:
        cut = 75
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut].decode())
        b = b" " + b[cut:]
    out.append(b.decode())
    return "\r\n".join(out)


def uid(e):
    key = f"{e['title'].strip().lower()}|{e['start'][:10]}|{(e.get('venue') or '').strip().lower()}"
    return hashlib.sha1(key.encode()).hexdigest()[:16] + "@local-events-feed"


now = datetime.now(tz)
kept, seen = [], set()
for e in events:
    all_day = len(e["start"]) == 10
    if all_day:
        start = date.fromisoformat(e["start"])
        end = date.fromisoformat(e["end"]) if e.get("end") else start
        if end < now.date():
            continue
    else:
        start = datetime.fromisoformat(e["start"]).replace(tzinfo=tz)
        end = datetime.fromisoformat(e["end"]).replace(tzinfo=tz) if e.get("end") else start + timedelta(hours=2)
        if end < now:
            continue
    u = uid(e)
    if u in seen:
        continue
    seen.add(u)
    kept.append(e)
    lines = ["BEGIN:VEVENT", f"UID:{u}", f"DTSTAMP:{now.astimezone(ZoneInfo('UTC')):%Y%m%dT%H%M%SZ}"]
    if all_day:
        lines += [f"DTSTART;VALUE=DATE:{start:%Y%m%d}", f"DTEND;VALUE=DATE:{end + timedelta(days=1):%Y%m%d}"]
    else:
        lines += [f"DTSTART;TZID={cfg['timezone']}:{start:%Y%m%dT%H%M%S}", f"DTEND;TZID={cfg['timezone']}:{end:%Y%m%dT%H%M%S}"]
    desc = "\n".join(x for x in [e.get("drive") and f"Drive from Cary: {e['drive']}", e.get("description"), e.get("price") and f"Price: {e['price']}", e.get("category") and f"Category: {e['category']}", e.get("url")] if x)
    # Show the drive time ("~15 min") in the title so it's visible in calendar views.
    summary = e["title"] + (f" ({e['drive'].split(',')[-1].strip()})" if e.get("drive") else "")
    lines += [f"SUMMARY:{esc(summary)}",f"LOCATION:{esc(', '.join(x for x in [e.get('venue'), e.get('address')] if x))}", f"DESCRIPTION:{esc(desc)}"]
    if e.get("url"):
        lines.append(f"URL:{e['url']}")
    lines.append("END:VEVENT")
    e["_ics"] = lines

cal = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//local-events-feed//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
       "X-WR-CALNAME:Local Events", f"X-WR-TIMEZONE:{cfg['timezone']}", "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
       "X-PUBLISHED-TTL:PT12H"]
for e in kept:
    cal += e.pop("_ics")
cal.append("END:VCALENDAR")
(ROOT / "events.ics").write_text("\r\n".join(fold(l) for l in cal) + "\r\n")
kept.sort(key=lambda e: e["start"])
(ROOT / "events.json").write_text(json.dumps(kept, indent=2) + "\n")
print(f"{len(kept)} upcoming events written to events.ics", file=sys.stderr)
