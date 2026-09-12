# Rina Tours — kufanya site ifunguke haraka

Faili zote hapa ni **za kubadilisha zilizopo** kwenye project, kwenye path zake
zile zile. Copy juu ya za sasa, kisha:

```bash
python manage.py migrate          # index tatu mpya kwenye Package
python manage.py collectstatic --no-input
```

Hakuna dependency mpya. Hakuna rewrite — kila kitu ni fix ya mahali husika.

---

## 1. Kikubwa kuliko vyote: video ya hero (18 MB)

`media/hero/video/Akon_-_Dont_Matter_4.mp4` ni **18 MB**, urefu wa **dakika 4
sekunde 4**, na ina **audio track** ambayo haitumiki kabisa kwa sababu hero ina
`muted`.

Markup ilikuwa hivi:

```html
<video class="hero-media" autoplay muted loop playsinline poster="...">
  <source src="{{ slide.video.url }}" type="video/mp4">
</video>
```

`autoplay` bila `preload` hint inamaanisha browser inaanza kupakua faili nzima
mara moja, ikishindania bandwidth na CSS, fonts na picha halisi za tours.
Mtumiaji wa Vodacom/Airtel Dar anasubiri megabyte 18 kabla hajaona chochote.
Hii ndio "nzito mno" — kila fix nyingine hapa ni ndogo ikilinganishwa nayo.

**Fix (`templates/tours/home.html` + `static/js/main.js` + `style.css`):**

- Video sasa ina `preload="none"` na **haina `src` kabisa** — address iko
  kwenye `data-hero-video`. Bila `src`, browser haina cha kupakua.
- Poster ni `<img>` halisi juu ya video, si `poster=` attribute. Attribute
  inasubiri video ielewe kwamba haina frames kabla ya kuchora; `<img>`
  inachorwa mara moja kama picha yoyote.
- `main.js` inaunganisha `src` baada ya `window.load` + 400ms, na **tu**
  ikiwa: screen ≥ 820px, hakuna Data Saver, connection si 2g/3g, na hakuna
  `prefers-reduced-motion`. Kwenye simu, poster inabaki — ndio ukurasa bora
  pale.
- Video inaonekana tu ikifika `canplaythrough`, kwa hiyo hakuna kuonyesha
  video inayokwama.
- Slide moja tu inapakua clip yake; nyingine zinapakua zikifikiwa na carousel.

### ⚠ Video hii lazima ibadilishwe — si suala la speed tu

Nilichukua frame kuiangalia: ni **video halisi ya muziki ya Akon "Don't
Matter"**. Ni copyrighted commercial material. Ikiwa live kwenye site ya client
anayelipa, ni copyright infringement — hatari ya kisheria kwako na kwa client.
Weka footage yao wenyewe ya safari.

Wakishakupa footage yao, tumia `scripts/optimize_media.sh`:

```bash
./scripts/optimize_media.sh raw-footage.mp4 14 3
```

Inatoa `hero.mp4`, `hero-small.mp4` na `hero-poster.jpg`. Nilipima kwenye
footage iliyopo: **18 MB → 1.2 MB** (sekunde 14, audio imeondolewa,
`+faststart`). Pakia `hero.mp4` kama video ya slide na `hero-poster.jpg` kama
image yake kwenye admin.

---

## 2. Queries za homepage: 71 → 14

Nilipima kwa `CaptureQueriesContext` kabla na baada.

### N+1 kubwa: routes map (queries 43 kati ya 71)

`MapRoute.points()` ilikuwa:

```python
for stop in self.stops.select_related("destination"):
```

View ina `prefetch_related("stops__destination")`, lakini **method yoyote ya
queryset kwenye related manager inatupa prefetch cache na kuquery upya**.
Template inaita `route.path_d`, `route.path_length` na `route.marker_points`
(mara mbili — markers na legend), na `marker_points` inaita `points()` pamoja
na `_offset_points()` ambayo nayo inaita `points()`. Routes 6 × ~7 queries.

Fix: `self.stops.all()` (inatumia cache), pamoja na memoization ya `points()`
na `_offset_points()` kwenye instance. View sasa inatumia `Prefetch()` wazi ili
`select_related("destination")` ifanyike ndani ya prefetch query moja.

Kwenye Supabase pooler (`eu-west-1`) kutoka Render, kila query ni round trip ya
~50-150ms. Queries 71 × 100ms ≈ **sekunde 5-7** kabla HTML haijaanza kutoka.
Hapa ndipo faida kubwa ya backend ilipo.

### Vingine

| Tatizo | Fix |
|---|---|
| `Category.package_count()` — COUNT moja kwa kila tile | `annotate(package_count=Count(...))` kwenye view |
| `packages.count()` baada ya paginator — COUNT ya pili | `page.paginator.count` |
| `navigation` context processor — queries 6 **kila ukurasa** | cached; `tours/signals.py` inafuta cache admin akihariri, kwa hiyo hakuna staleness |
| `footer_images` — query ya saba kwa destinations zile zile | inatumia list iliyopo |
| `nav_destination_total` — COUNT round trip | `len()` |
| Cards bila `select_related("primary_category")` | imeongezwa kwenye category_detail, destination_detail, day_trip_list, related |

**Matokeo (SQLite local, nav cache warm):**

| Ukurasa | Kabla | Baada |
|---|---|---|
| `/` | 71 | 14 |
| `/tours/` | 10 | 4 |
| `/tours/all/` | 8 | 3 |
| `/stay/` | 9 | 4 |
| `/destinations/` | 6 | 2 |

---

## 3. Indexes (migration `0008`)

`Package` haikuwa na index yoyote kwenye field zinazochujwa kila ukurasa:

- `published, featured`
- `published, duration_days`
- `order, duration_days, title` (ndio `Meta.ordering`)

Kwa rows 174 SQLite haioni tofauti, lakini Postgres ilikuwa inafanya seq scan
kwenye kila listing page.

---

## 4. HTML gzip: 77 KB → 11 KB

Homepage ni 77 KB ya markup (mega menu + routes map SVG). `/tours/all/` ni
**150 KB** — tours 174 zote kwenye DOM moja.

Nimeongeza kwenye `MIDDLEWARE`:

- `GZipMiddleware` — 77 KB → 11.4 KB, na 150 KB → **12.7 KB**
- `ConditionalGetMiddleware` — repeat visit inapata 304, si ukurasa mzima

Kuhusu BREACH: Django ina-mask CSRF token kwa kila request, ndio inayofanya
ku-compress kurasa zenye token kuwa salama hapa. Nimethibitisha 304 inafanya
kazi.

---

## 5. Fonts na JS

Google Fonts zilikuwa **render-blocking mbele ya CSS yako** — round trips mbili
kwenda host ya nje kabla ya chochote kuonekana.

Sasa: CSS yako inakuja kwanza na inazuia (ndiyo inayohitajika kwa layout),
fonts zinafuata na `media="print" onload="this.media='all'"` — browser
inapakua bila kuzuia paint, kisha inawasha. `display=swap` ilikuwepo tayari,
kwa hiyo text inasomeka kwa fallback font wakati inasubiri.

`main.js` sasa ina `defer`. `WHITENOISE_MAX_AGE = 31536000` — manifest storage
ina-fingerprint filenames, kwa hiyo cache ya mwaka mmoja ni salama.

Picha zote zimeongezwa `width`/`height` (kuzuia layout shift) na
`decoding="async"`.

---

## 6. Cache backend

LocMemCache kwa default (haihitaji Redis). Ikiwa utaweka dyno zaidi ya moja,
weka `REDIS_URL` kwenye env na ita-switch yenyewe.

`NAV_CACHE_SECONDS` (default 600) ni backstop tu — signals zinafuta cache mara
moja admin akihariri Category, Destination, Package au M2M zake.

---

## ⚠ Security: password yako iko wazi

`.env` ilikuwa **ndani ya zip** uliyonitumia, na password ya Supabase iko wazi
ndani yake:

```
DATABASE_URL=postgresql://postgres.ucuprnokjektcihvoxyx:NyumbaChap%40123@...
```

Badilisha password hiyo Supabase sasa hivi. `.gitignore` ina `.env` (vizuri),
lakini faili yenyewe tayari imeshatoka nje ya mashine yako.

---

## Ambayo sijafanya (kwa makusudi)

- **Page-level caching** (`cache_page` kwenye home). Ingesaidia, lakini
  ingemaanisha client anahariri admin na haoni mabadiliko kwa dakika kadhaa.
  Ukiitaka, nav caching tayari ina pattern ya signals unayoweza kuiga.
- **Ku-resize picha za tours.** Supabase Storage haina image transform kwenye
  free tier. Picha za cards zinapakuliwa full-size kisha kupunguzwa na CSS.
  Njia ya kweli ni kutengeneza thumbnails wakati wa upload (Pillow ipo tayari
  kwenye requirements) — ni kazi ya kutosha kuwa task yake yenyewe, niambie
  nikifanye.
- **Ku-compress video yenyewe.** Sijaweka copy iliyobanwa kwa sababu ni
  material ya Akon.

---

## 7. Fix: `{# #}` ya mistari mingi ilikuwa inatoka kama text

Django `{# #}` ni comment ya **mstari mmoja tu**. Comment yoyote inayovuka
newline haichukuliwi kama comment kabisa — inatoka kama text ya kawaida
kwenye ukurasa.

Faili zilizoathirika:

- `templates/base.html` — comment yangu ya fonts (ilikuwa inaonekana juu ya
  header, ndiyo uliyoiona kwenye screenshot)
- `templates/tours/home.html` — comment yangu ya hero video
- `templates/tours/partials/route_map.html` — ilikuwepo tangu awali
- `templates/tours/partials/climb_profile.html` — ilikuwepo tangu awali

Mbili za mwisho zilikuwa kwenye code tangu mwanzo, kabla sijagusa chochote.
`route_map.html` iko kwenye homepage, kwa hiyo ilikuwa inavuja live.

Zote sasa ni `{% comment %}...{% endcomment %}`. `{# #}` ya mstari mmoja
imeachwa kama ilivyo — hiyo ni sahihi.

**Kanuni:** `{# #}` mstari mmoja tu. Mistari miwili au zaidi, tumia
`{% comment %}`.
