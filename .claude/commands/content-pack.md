# /content-pack — pachet de conținut CopyStack

Generate an inbound content pack via the `content-marketer` agent.

- With $ARGUMENTS (an idea, e.g. `/content-pack 3 greșeli în reclamele de Black Friday`): produce one full pack for that idea.
- Without arguments: first propose 6 ideas (distributed across the brand pillars in `outreach/VOICE.md` — AI slop vs. artizanat, copy = bani, educație concretă, proces transparent), let the user pick, then produce the pack.

Save output to `outreach/content/<slug>.md`. If the user asks for a calendar, generate packs for a week (3 posts: 2 educație, 1 poziționare) and a posting-order table with best RO posting times (12:00–13:00 și 19:00–21:00 EET ca punct de pornire, de testat).
