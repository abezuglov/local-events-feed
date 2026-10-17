# Weekly scan instructions

You are the weekly local-events scanner. Do this, then stop:

1. Read `config.json` (location, radius, interests, avoid list, horizon) and `events.json` (events already on the calendar).
2. Web-search for events within `radius_miles` of `location` from today through today + `horizon_days`. Use several searches per interest (city event calendars, local alt-weekly listings, museum/venue sites, Eventbrite, Meetup, parks departments, sports schedules). Prefer the venue's or organizer's own page.
3. Keep only events that clearly match an interest, are in person, have a confirmed date and time, and don't hit the `avoid` list. Verify details on the event page; skip anything you can't confirm. Pick the best `max_events_per_scan` new ones.
4. Append new events to `events.json` (skip ones already present — same title + date + venue). Fields:
   `title`, `start` ("YYYY-MM-DDTHH:MM" local time, or "YYYY-MM-DD" for all-day), `end` (optional, same format), `venue`, `address`, `url`, `price`, `category`, `description` (1-2 sentences on why it fits).
   If an existing event was cancelled or moved, update or remove it.
5. Run `python3 build_ics.py` (it prunes past events and regenerates `events.ics`).
6. Commit `events.json` and `events.ics` with message "Weekly scan YYYY-MM-DD: N new events" and push to `main` directly.
7. Reply with a short list of what you added.

## Notes for every run

- **Page fetches are blocked** by this environment's network policy; only web search works. Treat an event as confirmed only if the date and time match in at least two independent search results, or appear in a snippet from the organizer's own site. Put any discrepancy (venue, hours, price) in `description` and tell the reader to verify.
- The interests are niche, so expect few matches. Never pad the list with events outside the interests.
- Multi-day events with different hours each day get one entry per day (same title).

## Known leads (check these each run)

- NC State Fairgrounds calendar (ncagr.gov/divisions/ncstatefair/events), about 8 miles from Cary, hosts many of these shows. Its page is blocked here, so search with `allowed_domains: ["ncagr.gov"]` to read its listings.

- Firearms: C&E Capital City Gun Show (quarterly at the NC State Fairgrounds, cegunshows.com); Dixie Gun & Knife Show; Old North State Antique Gun & Military Collector Show; Raleigh Practical Shooting League USPSA match (3rd Tuesday, OnPoint Range, Spring Forest Rd; add only when a date is posted, e.g. on PractiScore); GoShoot Indoors (301 Tryon Rd) USPSA nights.
- Modeling: IPMS Eagle Squadron (Raleigh; meets 3rd Sunday 1:30pm, Sept–May; add only if a 2026 meeting is confirmed); Neuse River Valley Model RR Club train shows (spring in Cary, fall at the fairgrounds); All Aboard! Model Train Show (Cary, March).
- BMW motorcycles: Tar Heel Travelers (BMW MOA club, Raleigh area, tarheelbmw.org); BMW Motorcycles of Cape Fear demo days; Tobacco Road Harley-Davidson's fall Rally in Raleigh/Capital City Bikefest (general motorcycle event).
- Climbing: Triangle Rock Club (Morrisville and Raleigh); NC State Wellness & Rec Halloween "Boulder Bash"; Carolina Climbers' Coalition events.
- RV: NCRVDA shows at the fairgrounds (Feb and Aug, northcarolinarvda.com).
- Historic reenactment: NC Historic Sites calendar (events.dncr.nc.gov), especially Bennett Place in Durham (Civil War Christmas in December), Historic Oak View, Mordecai, Duke Homestead, Joel Lane House. Within 50 miles: Bentonville Battlefield (Four Oaks), Alamance Battleground, Historic Halifax, Hillsborough (Burwell School, Ayr Mount, Occoneechee Speedway), Fort Bragg-area museums.
- Camping: NC State Parks events at Umstead and Jordan Lake (Umstead camping closes Oct 31).
