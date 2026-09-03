"""
Layer 0 · raw events to clean structures.

Everything known about the stream lives here; the rest of the code
consumes `Timeline` and never touches an event again. The screen is a
depth counter, days and nights cut at different hours, and truncated days
leave every view: DECISIONS.md says why for each.
"""

from __future__ import annotations

import json
from bisect import bisect_left
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from .taxonomy import refine

# ---------------------------------------------------------------------------
# Schema vocabulary
# ---------------------------------------------------------------------------

SCREEN_ON = "SCREEN_ON"
SCREEN_OFF = "SCREEN_OFF"
USER_PRESENT = "USER_PRESENT"
APP_FOREGROUND = "APP_FOREGROUND"
URL_VISIT = "URL_VISIT"
BLOCK = "BLOCK"

CATEGORIES = [
    "ADULT", "GAMBLING", "SOCIAL_MEDIA", "MESSAGING", "GAMING",
    "ENTERTAINMENT", "NEWS", "SHOPPING", "OTHER",
    # Not in the files. `taxonomy.py` assigns these on read, to the apps and
    # domains the stream left as OTHER.
    "CALLS", "NAVIGATION", "PRODUCTIVITY", "AI_TOOLS", "REFERENCE",
    "LEARNING",
]

#: "Sensitive" categories: the only ones that can justify notifying a
#: an alert. The rest are ordinary distraction.
SENSITIVE = {"ADULT", "GAMBLING"}

#: Categories treated as "distraction" for scoring purposes.
DISTRACTING = {"SOCIAL_MEDIA", "ENTERTAINMENT", "GAMING"}

#: Human-readable name per package. Cosmetic only (never leaves the device).
APP_LABELS = {
    "com.whatsapp": "WhatsApp",
    "com.android.chrome": "Chrome",
    "com.spotify.music": "Spotify",
    "com.google.android.gm": "Gmail",
    "com.google.android.apps.maps": "Maps",
    "com.google.android.dialer": "Phone",
    "com.google.android.calendar": "Calendar",
    "com.google.android.youtube": "YouTube",
    "com.netflix.mediaclient": "Netflix",
    "com.facebook.katana": "Facebook",
    "com.twitter.android": "X / Twitter",
    "com.instagram.android": "Instagram",
    "com.zhiliaoapp.musically": "TikTok",
    "com.snapchat.android": "Snapchat",
    "com.google.android.apps.messaging": "Messages",
    "org.telegram.messenger": "Telegram",
    "com.amazon.kindle": "Kindle",
    "com.roblox.client": "Roblox",
    "com.supercell.clashofclans": "Clash of Clans",
    "com.duolingo": "Duolingo",
    "com.google.android.keep": "Keep",
    "com.microsoft.office.outlook": "Outlook",
    "com.reddit.frontpage": "Reddit",
}


def app_label(package: str) -> str:
    return APP_LABELS.get(package, package.split(".")[-1].title())


# ---------------------------------------------------------------------------
# Time
# ---------------------------------------------------------------------------

def to_dt(ms: int) -> datetime:
    """epoch millis → local wall-clock time (the clock arrives normalised to UTC)."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).replace(tzinfo=None)


def day_of(ms: int) -> date:
    return to_dt(ms).date()


def midnight_ms(d: date) -> int:
    return int(datetime.combine(d, time.min).replace(tzinfo=timezone.utc).timestamp() * 1000)


# ---------------------------------------------------------------------------
# Structures
# ---------------------------------------------------------------------------

@dataclass
class Interval:
    """One screen-on stretch, already clipped to a single day."""
    start_ms: int
    end_ms: int
    day: date
    pickups: int = 0          # real unlocks inside the stretch
    glances: int = 0          # SCREEN_ON with no unlock inside the stretch

    @property
    def seconds(self) -> float:
        return (self.end_ms - self.start_ms) / 1000

    @property
    def is_pickup(self) -> bool:
        return self.pickups > 0


@dataclass
class Usage:
    """A slice of time attributed to an app or a domain."""
    start_ms: int
    end_ms: int
    day: date
    kind: str                 # 'app' | 'site'
    key: str                  # package_name | url_domain
    category: str

    @property
    def seconds(self) -> float:
        return (self.end_ms - self.start_ms) / 1000


@dataclass
class Block:
    ts_ms: int
    day: date
    block_type: str           # APP | URL | NUDITY
    category: str
    target: str               # package or domain


@dataclass
class Timeline:
    """Everything derived from one user's stream, already clean."""
    user: str
    events: list[dict]
    intervals: list[Interval]
    usages: list[Usage]
    blocks: list[Block]
    days: list[date]
    anomalies: Counter = field(default_factory=Counter)


# ---------------------------------------------------------------------------
# Reconstruction
# ---------------------------------------------------------------------------

#: If an app sits "in the foreground" longer than this with no event closing
#: it, we assume the `SCREEN_OFF` was lost and cut. The cap sits above the
#: longest screen stretch observed (21.9 min in `user_a`, 32.6 min in
#: `user_b`), so today it truncates nothing real: it is a safety net, not a
#: business rule.
MAX_FOREGROUND_S = 45 * 60


def _screen_intervals(events: list[dict], anomalies: Counter) -> list[Interval]:
    """Union of screen-on stretches, split at midnight.

    Depth counter: ON adds, OFF subtracts. The screen is on while depth > 0.
    Pickups and glances are attributed to the open stretch.
    """
    raw: list[Interval] = []
    depth = 0
    start = None
    pickups = glances = 0
    pending_on = False           # a SCREEN_ON is awaiting its verdict

    for e in events:
        t = e["event_type"]
        ts = e["timestamp_millis"]

        if t == SCREEN_ON:
            if pending_on:       # the previous ON died without an unlock → glance
                glances += 1
            pending_on = True
            if depth == 0:
                start = ts
                pickups = glances = 0
            depth += 1

        elif t == USER_PRESENT:
            if depth == 0:
                # Unlock with no preceding SCREEN_ON. Does not happen in the
                # two sample files, but it is physically possible if the ON is
                # lost.
                anomalies["USER_PRESENT with no SCREEN_ON"] += 1
                depth, start, pickups, glances = 1, ts, 0, 0
            if pending_on:
                pickups += 1
                pending_on = False
            else:
                anomalies["duplicate USER_PRESENT in stretch"] += 1

        elif t == SCREEN_OFF:
            if depth == 0:
                anomalies["SCREEN_OFF while screen already off"] += 1
                continue
            if pending_on:
                glances += 1
                pending_on = False
            depth -= 1
            if depth == 0:
                raw.append(Interval(start, ts, day_of(start), pickups, glances))

    if depth > 0:                # the file ends with the screen still on
        anomalies["stretch left open at end of file"] += 1
        last = events[-1]["timestamp_millis"]
        raw.append(Interval(start, last, day_of(start), pickups, glances))

    return _split_midnight(raw)


def _split_midnight(intervals: list[Interval]) -> list[Interval]:
    """Splits any stretch crossing midnight. Pickups go to the day the unlock
    happened, that is, to the first piece."""
    out: list[Interval] = []
    for iv in intervals:
        cur = iv
        while True:
            next_midnight = midnight_ms(cur.day + timedelta(days=1))
            if cur.end_ms <= next_midnight:
                out.append(cur)
                break
            out.append(Interval(cur.start_ms, next_midnight, cur.day,
                                cur.pickups, cur.glances))
            cur = Interval(next_midnight, cur.end_ms,
                           day_of(next_midnight), 0, 0)
    return out


def _screen_on_lookup(intervals: list[Interval]):
    """Returns a lookup for "which stretch encloses this instant", by bisection."""
    starts = [iv.start_ms for iv in intervals]

    def enclosing(ts: int) -> Interval | None:
        i = bisect_left(starts, ts + 1) - 1
        if i < 0:
            return None
        iv = intervals[i]
        return iv if iv.start_ms <= ts <= iv.end_ms else None

    return enclosing


def _usages(events: list[dict], intervals: list[Interval],
            anomalies: Counter) -> list[Usage]:
    """Atribuye tiempo a apps y a dominios a partir del orden de los eventos.

    An app is "in front" from its `APP_FOREGROUND` until the next foreground
    change, a `BLOCK`, a `SCREEN_ON` or the screen going off. A `URL_VISIT`
    occupies the browser: its time is taken off the app and attributed to the
    domain, because Chrome is a container and not a destination.

    A `SCREEN_ON` closes the foreground even if the screen stays on (the
    overlap case): the user went back to the lock screen, and crediting that
    time to the previous app would be inventing it. The cost is that some time
    goes unattributed, which is why coverage does not reach 100 %: 86 % in
    `user_a`, 67 % in `user_b`.
    """
    enclosing = _screen_on_lookup(intervals)
    out: list[Usage] = []

    # events that "close" the current foreground
    closers = {APP_FOREGROUND, URL_VISIT, BLOCK, SCREEN_OFF, SCREEN_ON}
    open_ev: dict | None = None   # {'kind','key','category','ts'}

    def close(at_ms: int):
        nonlocal open_ev
        if open_ev is None:
            return
        end = min(at_ms, open_ev["limit"])
        if end > open_ev["ts"]:
            out.append(Usage(open_ev["ts"], end, day_of(open_ev["ts"]),
                             open_ev["kind"], open_ev["key"], open_ev["category"]))
        open_ev = None

    for e in events:
        t = e["event_type"]
        ts = e["timestamp_millis"]

        if t in closers:
            close(ts)

        if t in (APP_FOREGROUND, URL_VISIT):
            iv = enclosing(ts)
            if iv is None:
                # happens with the screen off: background music, sync.
                anomalies[f"{t} with screen off"] += 1
                continue
            open_ev = {
                "kind": "app" if t == APP_FOREGROUND else "site",
                "key": e["package_name"] if t == APP_FOREGROUND else e["url_domain"],
                "category": refine(
                    e["package_name"] if t == APP_FOREGROUND else e["url_domain"],
                    e["category"]),
                "ts": ts,
                "limit": min(iv.end_ms, ts + MAX_FOREGROUND_S * 1000),
            }

    close(events[-1]["timestamp_millis"])
    return [u for u in out if u.seconds > 0]


def _blocks(events: list[dict]) -> list[Block]:
    return [
        Block(e["timestamp_millis"], day_of(e["timestamp_millis"]),
              e["block_type"] or "APP", e["category"] or "OTHER",
              e["package_name"] or e["url_domain"] or "desconocido")
        for e in events if e["event_type"] == BLOCK
    ]


def load(path: str | Path, user: str) -> Timeline:
    events = json.loads(Path(path).read_text())
    events.sort(key=lambda e: (e["timestamp_millis"], e["id"]))

    anomalies: Counter = Counter()
    intervals = _screen_intervals(events, anomalies)
    usages = _usages(events, intervals, anomalies)
    blocks = _blocks(events)

    first, last = day_of(events[0]["timestamp_millis"]), day_of(events[-1]["timestamp_millis"])
    days = [first + timedelta(days=i) for i in range((last - first).days + 1)]

    return Timeline(user, events, intervals, usages, blocks, days, anomalies)
