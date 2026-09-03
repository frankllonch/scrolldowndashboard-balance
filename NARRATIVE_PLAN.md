# Narrative rewrite — pending work

Steps 1–3 are done (commit `ef420fa` restored the source of truth; the "who is user B"
investigation is finished). What follows is steps 4–10, saved to pick up later.

## Open questions before writing

1. **Person B's framing.** The draft text describes "a teenager with a phone addiction,
   gaming gambling or pornography". The data does not support it: r(usage, blocks) = 0.954,
   B's inventory is Spotify / WhatsApp / Maps / Gmail / Calendar / Kindle / El País / BBC,
   social media totals under 20 minutes, and every "leak" app first opened on 18 May — one
   day when the filter stopped. Decide which story the page tells before any copy is written.
2. **Code navigation.** Which part was hard to navigate ("costa navegar codi")? Needed to
   know what to restructure.

## 4. Cover and product intro
New opening that says what Balance is and what the page is for, in the user's own words.

## 5. Summary at the top
"summary al inici" — the headline numbers and the conclusion before the scroll starts,
so the reader knows what they are looking at ("no se que estic veient").

## 6. Person A / Person B lines
Rewrite both, per the supplied text, once question 1 is settled.

## 7. Wellbeing score
Explain what it is and how it is computed. Answer, in the copy: "a more concentrated use in
fewer apps means what?" and "how do we measure distraction? more apps more distracted?".
Also the act about the index falling 60 → 40.

## 8. Per-chart explanations
A short plain explanation under every chart (~26 of them). Kill the phrases that mean
nothing to a reader: "the week has no edges", "best stretch" vs "longest break",
"what the phone said".

## 9. A/B switch
More noticeable, with a distinct colour per user, and the labels legible.

## 10. Structure and bugs
- Weekday ordering: the week starts on Friday, it should start on Monday.
- Scene-to-scene continuity: each section should hand the reader to the next.
- Rebuild act 09; expand act 12.
- "why is Netflix and YouTube let through?" — answer it in the copy (18 May, filter outage).

## Constraint
`docs/` is build output. `build.py` regenerates it from `site/` and `render/`, so hand edits
to `docs/style.css`, `docs/app.js` or `docs/index.html` are lost. Edit `site/` instead.
