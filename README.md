# Rina Tours Tanzania

Django site for a Tanzanian tour operator. 174 tours across 7 categories,
Postgres on Supabase, media in a Supabase Storage bucket, deployed on Render.

Built by JamiiTek Digital Agency.

---

## Quick start

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Windows (CMD)**

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Then fill in `.env`. `SECRET_KEY` has no default and the app will not start
without one — generate a good value with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Leave `DATABASE_URL` blank for now and the site runs on local SQLite.

The rest is the same on every platform:

```bash
python manage.py migrate
python manage.py import_packages      # loads all 174 tours
python manage.py seed_map             # destination coordinates + routes map
python manage.py createsuperuser
python manage.py runserver
```

**One gotcha with `.env`:** a comment has to be on its own line. `python-decouple`
does not strip anything after a value, so `MAX_VIDEO_UPLOAD_MB=45  # note` is
read as the string `45  # note` and the app fails to start.

Site at `http://127.0.0.1:8000/`, dashboard at `/admin/`.

---

## Loading the client's content

```bash
python manage.py import_packages          # create or update
python manage.py import_packages --reset  # wipe tours first, then load
```

Source of truth is `tours/data/packages.json`, generated from the client's
original text files by `content/parse.py` (kept alongside this project, not
inside it). When the client sends corrected copy, re-run the parser and then
`import_packages` — packages are matched on slug and updated in place, so
nothing duplicates and no admin edits to unrelated fields are lost.

**Destination names.** The client's files used 93 different strings for about
45 real places — `Serengeti`, `Serengeti National Park`, `Ngorongoro`,
`Ngorongoro Crater` and `Ngorongoro Conservation Area` all appeared as separate
destinations. `tours/data/destinations.py` maps every spelling onto one
canonical place. If the importer reports an unmatched string, add it there as
an alias rather than letting a duplicate destination through.

---

## Media: the Supabase bucket

Render wipes its disk on every deploy, so uploads cannot live there. Everything
uploaded through the admin goes to a Supabase Storage bucket instead.

**One-time setup in Supabase**

1. Storage -> New bucket -> name it `media`, tick **Public bucket**
2. Storage -> S3 Access Keys -> New access key (the secret is shown once)
3. Project Settings -> General -> Reference ID -> this is `SUPABASE_PROJECT_REF`
4. Note the region on the S3 panel, e.g. `eu-central-1`

Put those in `.env` and in Render's environment variables, then:

```bash
python manage.py check_storage
```

It uploads a test file, prints its public URL and deletes it. Open the URL — if
it fails, the bucket is not public.

Leave `SUPABASE_PROJECT_REF` blank locally and uploads go to `./media/`, so you
can develop without touching the bucket.

**Video.** `MAX_VIDEO_UPLOAD_MB` is set to 45 because Supabase's free tier caps
a single file at 50 MB. Raise it once the client is on a paid plan. Hero clips
should be H.264 mp4, 1080p, no audio track, 8-15 seconds, under 6 MB — a raw
phone video will be 80 MB and will make the homepage unusable on Tanzanian
mobile data.

---

## Content model

Everything is editable at `/admin/`.

- **Categories** — the 7 tour types. A tour can belong to several: Usambara
  Mountains is legitimately trekking, nature *and* camping. `categories` is
  many-to-many so there is one page per tour rather than three near-identical
  pages competing in search. `primary_category` drives the breadcrumb.
- **Destinations** — one row per real place, with `aliases` recording the other
  spellings the client uses.
- **Packages** — title, duration, price, copy, itinerary, gallery, video. Day
  trips are just packages with `duration_days = 1`; there is no separate model.
- **Hero slides** — homepage carousel, image or muted looping video.
- **Transfer services**, **Team**, **FAQs**, **Testimonials**
- **Contact messages** — every enquiry, linked to the tour it came from. Tick
  `handled` once followed up.

### Two fields worth understanding

**`price_basis`** — most tours are per person, but the two honeymoon packages
are priced per couple, the family safari is per adult, and the private dhow
cruise is per boat. The site renders the basis alongside the figure. Do not
change these to "per person" to make the listing look tidy; it would understate
the honeymoon packages by half.

**`duration_text`** — sunset cruises, jet ski and flyboard sessions are sold in
hours, not days. Those have `duration_days` blank and the wording in
`duration_text` instead, so they don't display as "0 days".

---

## Known content gaps

The client's source files are incomplete. The admin list shows a **ready to
sell** column; it is unticked wherever Includes/Excludes or the short
description is missing.

- 115 of 174 tours have no Includes or Excludes list
- 85 have no "Best for" line
- Roughly half the multi-day tours have no day-by-day itinerary
- Safari / Wildlife is the only category with no category description supplied

Everything is imported as `published=True` so the client can see the whole
catalogue. Untick `published` on anything that should not be publicly visible
until the copy arrives. `content/rina-tours-content-report.txt` has the full
per-tour list to send back to the client.

---

## The routes map

The homepage draws Tanzania in SVG with a coloured line per journey.

**Setup** — run once after `import_packages`:

```bash
python manage.py seed_map
```

That writes latitude and longitude onto all 55 destinations and builds the six
routes. Re-running is safe: it never overwrites coordinates that are already
set, so a correction made in the admin survives. Pass `--overwrite` if you do
want the file values to win.

**How it fits together**

- `tours/data/tanzania_map.py` holds the country outline (mainland, Unguja,
  Pemba, Mafia) and the `project()` function. The outline was simplified from
  public boundary data and projected once with that same function, so a marker
  placed from a real latitude and longitude lands in the right spot. Change the
  projection and the outline and the markers move together.
- `tours/data/coordinates.py` holds the coordinates and the route definitions.
- `MapRoute` and `RouteStop` are ordinary models — the client can add a route,
  reorder its stops or change its colour in the admin without touching code.

**Why routes are separate from packages.** The map wants six clean lines, not
174 tours drawn on top of each other. A route mirrors a real package and the
legend links through to it, but the two are edited independently.

Routes are drawn as curves through their stops, and each is nudged slightly to
one side of the straight line. Several journeys share the same legs — Arusha to
Serengeti is on three of them — and without that offset only the last line
drawn would be visible.

The lines draw themselves once, the first time the map scrolls into view.
Selecting a legend entry dims the others so one journey can be followed across
the country. Both respect `prefers-reduced-motion`.

---

## Look and feel

Restrained rather than decorated. Colour comes from the landscape — a deep
canopy green, dry-grass gold, an ivory paper ground — and the accents are thin
gold rules, not ornament.

One texture is generated rather than drawn:

```bash
python3 scripts/gen_motifs.py
```

That writes `static/img/shuka.svg` and `static/css/motifs.css`, which defines
`--shuka`: the checked weave of a Maasai shuka reduced to near-invisible white
hairlines. It sits on the dark green panels — header, page heads, footer — so
they read as cloth rather than as flat printed bars. It is a texture you should
not notice; if you can see the grid, the opacity is too high. Edit the script
and re-run it, never `motifs.css` directly.

Each category owns a colour (`Category.bead_colour`, editable in the admin).
It appears as a short rule beside the category in the navigation, on every tour
card, and along the bottom of its tile — enough for a visitor to learn the
colour and scan for it, without turning into decoration.

An earlier version used literal Maasai beadwork as trim. It was dropped: at
small sizes it read as something stuck onto the page rather than part of it.

## The navigation

Two dropdowns: **Tours**, grouped by experience with a promoted tour panel, and
**Destinations**, grouped by region — 51 places under six headings rather than
one column of 51.

They open on `:hover` in CSS, so the panel appears the instant the pointer
arrives with no script in the way. An invisible strip under each trigger bridges
the gap to the panel; without it the menu flickers shut when the pointer travels
diagonally. JavaScript covers only what CSS cannot: taps, keyboard, `Escape`,
and keeping `aria-expanded` truthful.

Counts and starting prices in the menu come from annotated queries in
`tours/context_processors.py`, so the whole menu costs two queries rather than
one per row.

## The hero

`python manage.py seed_hero` creates three starter slides. They carry no
photographs, so the hero falls back to tonal green panels — the carousel is
visibly working, and the moment an image is attached to a slide in the admin
that slide becomes the real thing with no code change.

Slides crossfade, and the visible one drifts slowly (a scale-and-pan). That
drift is what keeps a still photograph from reading as a placeholder. It runs
only on the active slide. The carousel pauses on hover, pauses when the tab is
hidden, and does not run at all under `prefers-reduced-motion`.

**Images are the missing ingredient.** The structure is built and the fallbacks
are deliberate rather than broken, but no amount of layout substitutes for
photography. Hero images want to be wide and dark enough for white type to sit
on — roughly 2400x1400, under 400 KB each.

## The footer

Whatever destination photographs exist drift behind the footer at 17% opacity
on a slow crossfade, under a green wash. With no images the layer is skipped
entirely and the footer stays flat green. It reuses imagery already uploaded
rather than asking the client for more.

## Interaction

Sections settle into place once as they enter the viewport. Cards lift and their
photograph pushes in slightly behind the frame. The header thins and gains a
blur once the page scrolls, driven by a sentinel element rather than a scroll
listener, so nothing runs on every frame.

All of it is suppressed under `prefers-reduced-motion`, and anything that is
never observed stays visible — content is never trapped behind an animation.

## The mobile menu

The drawer slides in from the left and is driven entirely by a checkbox, so it
responds to the first tap without waiting for JavaScript to parse. It animates
`transform` and `opacity` only — both handled by the compositor — so it stays
smooth on a mid-range phone on a slow connection.

It is laid out as a panel in its own right rather than the desktop nav squeezed
narrow: a deep green header carrying the brand, generously spaced rows with a
gold edge marking the active one, the enquiry call-to-action as a real button,
and a contact block closing it off. That block hides itself when no phone,
WhatsApp or email is set, so an unconfigured site does not show an empty band.

JavaScript adds only what CSS cannot: locking the page behind the drawer,
closing on Escape, closing after a link is tapped, and giving the burger label
keyboard behaviour. With JS blocked the drawer still opens and closes.

Inside the drawer the Tours dropdown becomes an accordion. On desktop the same
markup is an absolutely-positioned mega menu.

---

## Deploying to Render

1. Push to a GitHub repo — check `.env` is not committed
2. Render -> New -> Web Service -> connect the repo (it reads `render.yaml`)
3. Fill in every `sync: false` variable in the dashboard: `DATABASE_URL`, the
   four Supabase Storage values, and the `SITE_*` branding
4. Deploy. `build.sh` runs `collectstatic` and `migrate` on every deploy
5. From the Render shell, once:
   ```bash
   python manage.py createsuperuser
   python manage.py import_packages
   python manage.py seed_map
   ```

---

## Security

- `.env` is git-ignored. Never commit real credentials.
- `SECRET_KEY` has no default, so the app refuses to start without one. That is
  deliberate — it stops a placeholder key reaching production.
- `DEBUG` defaults to `False`. HTTPS redirect, HSTS and secure cookies switch on
  automatically outside local dev.
- If a database password is ever pasted into a repo, a chat or a document,
  rotate it in Supabase immediately. Editing the file does not help — git
  history keeps the old value.
