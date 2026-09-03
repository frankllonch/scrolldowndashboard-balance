# Decisions


## The screen is a depth counter

Screen-on events arrive while the screen is already on: 77 times in A, 411 in
B. Nothing says which off closes which on, and the choice moves the answer in
both directions. Over A: union 61.1 h, LIFO stack 64.9 h (+6 %), FIFO queue
56.7 h (−7 %), restart-on-every-on 53.0 h (−13 %). B spreads from 93.4 h to
155.1 h against 131.1 for the union.
On adds, off subtracts, the screen is on while the count is above zero. That
returns the union, which does not depend on a pairing, and it is what "the
screen was on" means.

## Two day conventions, deliberately

The calendar day cuts at midnight. The night runs 23:00 on day D to 06:00 on
D+1, because sleep does not cut at midnight and splitting one night over two
rows destroys the signal.
Known edge: the small hours of the first day belong to a night that predates
the file and are counted nowhere.

## The first unlock has a 06:00 floor

With the day cutting at midnight, a day that opens at 00:20 is the tail of the
night before, not the start of a working day. First unlock means the first from
06:00 onwards; the small hours are counted in the night band instead.

## Truncated days leave every view

B's file ends at 00:46 on the 31st, leaving 0.8 h of coverage. That day is out
of averages, rankings, the heatmap and blocks, though its events still count
towards the night of the 30th.
Without the filter B's mean screen time reads 261.8 min instead of 253.7.

## Browser time belongs to the domain

A URL visit takes the time off Chrome and gives it to the domain. Chrome is a
container, not a destination, which is why it shows 115 openings and 12 minutes
for A.

## App switches reset daily

Otherwise the first app of the morning counts as a switch from the last one of
the night: 0.83 false switches a day, 4.1 % of A's total.

## A silence budget, not a threshold

The failure mode of a channel aimed at a parent is not missing an event, it is
shouting until they stop reading. Two alerts per 30 days, a minimum gap of ten,
and candidates ranked by magnitude × persistence × actionability. A product,
not a sum: something huge but one day long should not get through.
`sensitive_spike` is detected on B and held. The phone blocked all 203
attempts, none opened, and the conversation left does not improve by arriving
today rather than on Sunday.

## The night carries 20 % of the index

Sixty minutes at 01:00 and sixty at 17:00 do not cost the same, and the night
is the cheapest lever: two hours less a day is a change of life, forty minutes
earlier is one change.

## Blocks do not score

A block means the filter acted and nothing opened. Docking points for the
attempt charges the user for the product working, and gives them a reason to
switch it off. Blocks feed the rules and the digest instead.

## An absolute anchor with a personal narrative beside it

The index is measured against fixed bands; the comparison against oneself, a
rolling 14-day median, sits next to it rather than inside it. A relative score
would give someone at a constant six hours a day full marks for consistency.

## `OTHER` is a gap, not a category

The stream labels a third of user A's attributed time and a fifth of user B's
`OTHER`: Gmail, Maps, the dialer, the calendar, ChatGPT, Wikipedia. That is
not a finding about their behaviour, it is a hole in the vocabulary.
`taxonomy.py` assigns six more categories on read, which drops `OTHER` to
0.4 % and 0.8 %, leaving only the browser container, whose time is reassigned
to the domain anyway.
It only ever moves something out of `OTHER`, and nothing it assigns is in
`DISTRACTING`, so no published figure moves: the CLI output is still
byte-identical. The files are never edited.

## The copy package is `copytext`, not `copy`

A top-level `copy/` package shadows the stdlib module of that name, and the
project root is on `sys.path`. Importing pandas then dies inside pyarrow with
`module 'copy' has no attribute 'deepcopy'`. Everything else about the rule
holds: one keyed catalogue, no user-visible string outside it.

## The plotly theme is hoisted out of the figures

Plotly writes the whole template into every figure it serialises. Across 59
figures that was 95 KB of the payload repeating itself, so the build strips it
and the page re-attaches one copy at plot time. 271 KB to 176 KB.

## The page is built, not mounted

`render/page.py` writes the acts into `docs/index.html` at build time rather
than leaving the browser to inject them. Part 2 also ships per profile in the
payload so the switch has something to swap, but the document that arrives is
already complete.
