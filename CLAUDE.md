# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-script scraper (`main.py`) that turns the events agenda of the Facultad de Derecho (UBA) website into an iCalendar feed. It fetches the agenda listing page, follows each event link to scrape its description, and writes two files to `OUT_DIR`:

- `agenda.ics`: the calendar feed
- `index.html`: a minimal Spanish-language table of events linking to `agenda.ics`

There are no tests, linter config, or build step.

## Commands

```sh
pipenv install              # Python 3.9, deps in Pipfile
pipenv run python main.py   # scrape and write ./out/
```

Environment overrides: `OUT_DIR` (default `./out`), `BASE_URL` (default `http://www.derecho.uba.ar/`, prefixed to each event's relative `href`), `IN_URL` (default `http://www.derecho.uba.ar/agenda/`).

The script runs at import time (no `main()` guard) and needs network access to the live site. Each run deletes and recreates `OUT_DIR`.

## Scraping assumptions (break if the site's HTML changes)

- Events are `<article class="item-agenda">` on the listing page. The start time comes from the `datetime` attribute of the inner `<time>`, the title and link from the first `<a>`.
- Times are naive local times. The script appends a hardcoded `-03:00` (Argentina) offset. Every event gets a fixed 2-hour duration.
- The description is the `<div class="list-aviso">` on the event page, converted to Markdown with `markdownify`. If that div is missing, the event URL is used instead.

## Deployment

`.github/workflows/run.yml` runs on every push and daily at 03:00 UTC. On `main` it publishes `./out` to the `gh-pages` branch using `peaceiris/actions-gh-pages` and the `DEPLOY_KEY` secret. The published `agenda.ics` is the feed users subscribe to, so changes to event UIDs or the output path affect existing subscribers.

`python-dateutil` is imported directly but only installed as a transitive dependency of `ics` (via `arrow`). It is not listed in `Pipfile`.
