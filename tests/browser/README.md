# Browser checks

The experience criteria cannot be asserted from source. These drive the built
page in Chromium and report what they saw.

```bash
python build.py
python -m http.server -d dist 8533 &
make browser
```

| Script | What it drives |
|---|---|
| `check_interaction.py` | both sliders, the fork, the pill, `?profile=B` |
| `check_switching.py` | switching mid-scroll: position and slider state held |
| `check_the_other_one.py` | act 10 offering only the unread profile |
| `check_motion.py` | reveal guards, the rail, act 06's surface, reduced motion |
| `check_mobile.py` | 375×812: overflow, reflow, touch targets, screenshots |
