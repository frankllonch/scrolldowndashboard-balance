/**
 * Wording a number.
 *
 * All of this used to happen in Python, which meant the document carried both
 * `first_pickup_h` and `first_pickup_clock` — the same fact twice, once as a
 * number and once as a decision about how to say it. Now it crosses once.
 */

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"] as const;

/** What to say where a metric genuinely does not exist. User A has no night
 *  band at all, and printing 0 would be a claim the data does not make. */
const NO_USE = "no use";

function pad(n: number): string {
  return n < 10 ? `0${n}` : String(n);
}

/**
 * An hour of the day as a clock face.
 *
 * The axis runs past 24 so the small hours sit above the evening rather than
 * dropping to the floor, so 25.5 is 01:30 the next morning.
 */
export function clock(hours: number | null | undefined): string {
  if (hours === null || hours === undefined || !Number.isFinite(hours)) {
    return NO_USE;
  }
  return clockOf(Math.floor(hours), Math.floor((hours % 1) * 60));
}

/**
 * A clock face from an epoch millisecond.
 *
 * UTC, because the core reads every timestamp as UTC and drops the zone
 * (`analysis/events.py`). This is the exact form: `clock()` on a decimal hour
 * truncates, and 21.8833 h is 21:53, not 21:52.
 */
export function clockAt(ms: number | null | undefined): string {
  if (ms === null || ms === undefined) return NO_USE;
  const at = new Date(ms);
  return clockOf(at.getUTCHours(), at.getUTCMinutes());
}

/**
 * A clock face from an hour and a minute.
 *
 * Where both are already known, this is the one to use: going through the
 * float above and truncating back out loses a minute to binary rounding.
 */
export function clockOf(hours: number, minutes: number): string {
  return `${pad(((hours % 24) + 24) % 24)}:${pad(minutes)}`;
}

/** Minutes as hours and minutes: "2h 02m", or "47 min" under the hour. */
export function hm(minutes: number | null | undefined): string {
  if (minutes === null || minutes === undefined || !Number.isFinite(minutes)) {
    return NO_USE;
  }
  const total = Math.round(minutes);
  const h = Math.floor(total / 60);
  return h ? `${h}h ${pad(total % 60)}m` : `${total} min`;
}

/** An ISO day as "18 May". Locale-independent on purpose: the page is in one
 *  language and a browser locale would make the same build read differently. */
export function shortDate(day: string): string {
  const [, month, dayOfMonth] = day.split("-");
  const index = Number(month) - 1;
  return `${Number(dayOfMonth)} ${MONTHS[index] ?? month}`;
}

/** 1st, 2nd, 3rd, 4th. The teens are all -th, which is the case a lookup on
 *  the last digit alone gets wrong. */
export function ordinal(n: number): string {
  const whole = Math.trunc(n);
  if (whole % 100 >= 10 && whole % 100 <= 20) return `${whole}th`;
  const suffix = { 1: "st", 2: "nd", 3: "rd" }[whole % 10] ?? "th";
  return `${whole}${suffix}`;
}

/** A number that may not exist. */
export function maybe(value: number | null | undefined, digits = 0,
                      unit = ""): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return NO_USE;
  }
  return `${value.toFixed(digits)}${unit ? ` ${unit}` : ""}`.trim();
}

export function pct(share: number, digits = 0): string {
  return `${(share * 100).toFixed(digits)} %`;
}

export function thousands(value: number, digits = 0): string {
  return value.toLocaleString("en", { minimumFractionDigits: digits,
                                      maximumFractionDigits: digits });
}

/**
 * A centred rolling mean, matching `pandas.rolling(w, min_periods, center)`.
 *
 * Only odd windows: a centred even window has no centre, and pandas resolves
 * that by leaning one way, which is not a behaviour worth reproducing from
 * memory. Both callers use 7.
 */
export function rollingMean(values: Array<number | null>, window: number,
                            minPeriods = 2): Array<number | null> {
  if (window % 2 === 0) {
    throw new Error(`rollingMean expects an odd window, got ${window}`);
  }
  const half = (window - 1) / 2;
  return values.map((_, i) => {
    let sum = 0;
    let seen = 0;
    for (let j = Math.max(0, i - half); j <= Math.min(values.length - 1, i + half); j++) {
      const v = values[j];
      if (v !== null && v !== undefined && Number.isFinite(v)) {
        sum += v;
        seen += 1;
      }
    }
    return seen >= minPeriods ? sum / seen : null;
  });
}
