# /outreach — pipeline de prospectare CopyStack

Orchestrate the full outreach pipeline for the prospects in `outreach/prospects.csv` (or the file given in $ARGUMENTS).

## Steps

1. **Load the list.** Read the CSV (columns expected: company, website, city, industry, contact, status — tolerate missing columns; ignore rows where status is `done` or `replied`). If the file doesn't exist, show `outreach/prospects-template.csv` and stop, asking the user to fill it.
2. **Pick the batch.** Default: next 5 rows with empty status (ask the user if they want a different batch size — research with web search is slow, so batches keep it manageable).
3. **For each prospect, run agents in sequence:**
   a. `prospect-researcher` → save dossier to `outreach/done/<slug>/dossier.md`
   b. `outreach-writer` (input: that dossier) → save to `outreach/done/<slug>/mesaje.md`
   c. `follow-up-sequencer` (input: dossier + mesaje) → save to `outreach/done/<slug>/follow-up.md`
   Run the researcher for different prospects in parallel when possible; writers depend on their own dossier only.
4. **Update the CSV** — set status to `ready` for processed rows.
5. **Report** — table: company | punctul de durere | serviciul de intrare | unde sunt fișierele. Remind the user: messages are drafts to send manually — review the first sentence of each (the personalization) before sending.

Quality gate: spot-check one generated email against `outreach/VOICE.md`'s banned list before reporting success.
