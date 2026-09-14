# Maelekezo mapya ya client — yaliyofanyika

Baada ya ku-copy faili:

```bash
python manage.py migrate
python manage.py seed_camp_coords      # coordinates za camps
python manage.py seed_client_requests  # packages mpya + mpangilio wa day trips
python manage.py collectstatic --no-input
```

---

## 1. Map ya kupanda Kilimanjaro

Kila package ya kupanda sasa ina **map ya juu ya mlima** juu ya ile chati ya
urefu iliyokuwepo. Map inaonyesha njia kutoka gate hadi Uhuru Peak.

- Njia ya **kupanda** ni mstari mzito
- Njia ya **kushuka** ni mstari wa vitone — Rongai inapanda kutoka kaskazini
  kisha inashuka Marangu, Machame inashuka Mweka. Bila kutofautisha, mstari wa
  kushuka unavuka wa kupanda na inaonekana kama kosa la kuchora
- Background ni pete za contour: Kibo katikati, Mawenzi mashariki, Shira
  magharibi
- Kila route ina **zoom yake** — Lemosho inaanza mbali magharibi, Rongai
  kaskazini; frame moja ingefanya kila njia ionekane ndogo katikati

Mount Meru haina map — iko nje ya eneo la map hii. Inabaki na chati ya urefu
tu, na hii inajitokeza yenyewe bila kuandika sheria maalum.

### Coordinates ni za makadirio — hili ni muhimu

Nilitafuta kwa bidii. **Hakuna chanzo cha umma chenye coordinates za camps
zote.** Mbili tu ndizo zilizo za uhakika:

| Mahali | Coordinates | Chanzo |
|---|---|---|
| Uhuru Peak | 3.0758°S, 37.3533°E | imechapishwa sana |
| Barafu Camp | 3°5'58.89"S, 37°22'41.41"E | imechapishwa kwa sekunde |

Nyingine **51 zimekadiriwa** kutoka hizo mbili pamoja na mpangilio wa mlima
unaojulikana. Hata KINAPA wenyewe wanasema markers za map yao ni za makadirio.

Kwa hiyo:

- `ClimbStage` sasa ina `latitude`, `longitude`, na **`coords_verified`**
- Camp isiyohakikiwa ina duara la vitone kwenye map
- Route yenye camp yoyote isiyohakikiwa inaonyesha maandishi chini:
  *"Camp positions are approximate and drawn for orientation, not navigation."*
- Maandishi hayo **yanatoweka yenyewe** camps zote za route zikishahakikiwa.
  Hakuna wa kukumbuka kurudi kufuta

**`kilimanjaro-camps-for-guides.csv`** iko kwenye zip hii — camps 53. Ipe
waongozaji wajaze safu ya mwisho, kisha sahihisha kwenye admin na tick
"coords verified". Ku-export upya: `manage.py export_camp_coords > camps.csv`.

`seed_camp_coords` **haiharibu** camp iliyohakikiwa ukiirun tena. Marekebisho
ya waongozaji yanabaki hata baada ya deploy.

---

## 2. Packages alizoomba

| Package | Hali |
|---|---|
| Kilimanjaro Foothills Bike Tour | **Haijachapishwa** — inasubiri bei |
| Moshi Town Tour | **Haijachapishwa** — inasubiri bei |
| Moshi Town & Chemka Hot Springs Day Trip | **Haijachapishwa** — inasubiri bei |
| Maasai Boma Day & Overnight Camp | **Haijachapishwa** — inasubiri bei |

Zimeundwa **bila kuchapishwa** kwa makusudi. Hatuna bei kutoka kwake kwa
yoyote kati ya hizi. Package isiyochapishwa ni pengo; package iliyochapishwa
yenye bei ya kubuni ni malalamiko na huenda hasara. Weka `price_from` kwenye
admin na tick "published".

**Muulize bei za hizi nne.**

Maelezo ya Maasai ni yale aliyoyatoa mwenyewe: siku nzima kwenye boma, kutafuta
kuni pamoja nao, kupika na kula nao, na kulala kambini kando ya boma. Sikuongeza
chochote asichokisema.

---

## 3. Day trips alizosema "umesahau"

Zilikuwepo zote. Tatizo lilikuwa **mpangilio** — homepage inaonyesha 6 tu, na
zilizoonekana zilikuwa safari za national parks. Materuni, coffee na Maasai
zilikuwa chini.

Sasa zinazoonekana kwanza ni:

- Chagga Culture & Coffee Tour
- Chemka Hot Springs Nature Escape
- Maasai Boma Cultural Experience
- Maasai Village Cultural Experience
- Materuni Village & Coffee Experience
- Materuni Waterfall & Kilimanjaro Foothills Hike

Kidokezo: `order` ni `PositiveIntegerField`, kwa hiyo huwezi kwenda chini ya 0
ambapo kila kitu kilikuwa. Command inashusha day trips nyingine hadi 5 kwanza,
kisha inaweka hizi kwenye 0.

---

## 4. Transfer fee

$70 per trip — **ilikuwa tayari sahihi**. Hakuna kilichobadilishwa.

Vivyo hivyo taxi Moshi $70, Arusha $75, siku nzima $120–$180, accommodation $60
BB, km 13 kutoka KIA, dakika 9–15, kitchen, chai/kahawa $3, kupika mwenyewe,
mazingira ya kijani, ndege, view ya Kilimanjaro na Meru — **yote yalikuwemo
tayari** kwenye `/stay/`. Hakuna cha kuongeza.

Kama hajayaona, angalia kama anaangalia deploy ya zamani.

---

## Sahihisho: promotion ya day trips ilikuwa dhaifu

Toleo la kwanza lilikuwa linatafuta day trips kwa **title kamili**. Titles
zinatengenezwa na `import_packages`, na zinatofautiana kati ya run moja na
nyingine — kwa hiyo orodha iliyofanya kazi kwenye database moja ilikuta
hakuna kitu kwenye nyingine, na command bado iliripoti mafanikio.

Sasa inatafuta kwa **keywords** (`materuni`, `waterfall`, `coffee`, `maasai`,
`chemka`, `hot spring`), imezuiliwa kwa day trips tu ili "coffee" isivute tour
ya siku nyingi. Command sasa **inaorodhesha kila tour iliyoinuliwa**, na
ikikosa zote inatoa error wazi badala ya kunyamaza.

Run tena:

```bash
python manage.py seed_client_requests
```

---

## 5. Bei ya kupanda Kilimanjaro

```bash
python manage.py set_climb_price                # dry run — inaonyesha tu
python manage.py set_climb_price --apply        # inapandisha zilizo chini ya $1746
python manage.py set_climb_price --apply --flat # inaweka ZOTE $1746
```

Dry run ndio default kwa makusudi — hii inahariri bei za live kwa wingi.

Bei za sasa ni $1,500 hadi $2,200 kwa siku 6 hadi 9. Mode mbili kwa sababu
"bei ianze $1746" na "kila kupanda ni $1746" ni maagizo tofauti:

- **Floor (default)** — zilizo chini ya $1746 zinapanda, zilizo juu zinabaki.
  Marangu, Machame na Umbwe zinapanda; Lemosho, Rongai, 8-day na Northern
  Circuit zinabaki. Bei ya chini kabisa inakuwa $1746, ndiyo maana ya "from"
- **`--flat`** — zote zinakuwa $1746, ikiwemo **kushusha** Northern Circuit ya
  siku 9 kutoka $2,200 na Lemosho ya siku 8 kutoka $2,000

Command inaonya wazi kabla ya kushusha bei yoyote. Siku 9 ina park fees zaidi,
crew days zaidi na chakula zaidi kuliko siku 6 — kuiuza kwa bei ya siku 6 ni
hasara kwa kila mteja anayeinunua.

Kubadilisha kiasi: `--price 1850`. Kwa Meru: `--mountain "Mount Meru"`.

Haiguswi day hikes za foothills — zina "Kilimanjaro" kwenye title lakini si
kupanda mlima. Kama ningelinganisha kwa title, matembezi ya $80 yangekuwa
$1,746.

### Kurudisha bei baada ya `--flat`

`--flat` inaweka **zote** $1746, ikiwemo kushusha ndefu. Kurudisha:

```bash
python manage.py restore_climb_prices          # dry run
python manage.py restore_climb_prices --apply  # rudisha bei za zamani
python manage.py set_climb_price --apply       # kisha weka $1746 kama floor
```

Matokeo: Marangu, Machame na Umbwe zinakuwa $1,746. Rongai na Machame-7
zinabaki $1,750, Lemosho $1,800, Lemosho-8 $2,000, Northern Circuit $2,200.
Bei ya chini kabisa ni $1,746 — ndiyo "from $1746".

Bei za zamani zimehifadhiwa ndani ya command hiyo.

---

## 6. Sahihisho mbili za `import_photos`

### Bug: `'str' object has no attribute 'save'`

Command ilikuwa inafanya `owner.image.save(...)`. Lakini `Package` na
`Destination` zina **field mbili**: `image` (URLField — kwa picha iliyo host
mahali pengine) na `image_upload` (ImageField — faili halisi). `hasattr(owner,
"image")` ilikuwa kweli kwa zote, kwa hiyo command ilishika URLField na
kuita `.save()` juu ya string.

Ndiyo maana `stay` ilifanya kazi lakini `package` zote zilianguka —
`Accommodation` ina ImageField tu.

Sasa inaangalia **aina ya field**, si jina lake. Itafanya kazi hata kwa model
zitakazoongezwa baadaye.

### Command mpya: `find_package`

```
python manage.py find_package materuni
python manage.py find_package coffee --day-trips
python manage.py find_package --unpublished
```

Inaonyesha slug, siku, bei na kama imechapishwa.

Slugs zinatengenezwa na `import_packages` kutoka kwenye titles, kwa hiyo
zinatofautiana kati ya import moja na nyingine na kati ya database moja na
nyingine. Nimekuwa nikizichukua kutoka DB yangu na kukupa — ndiyo maana
ulipata "No package with slug". Tumia command hii badala ya kunukuu slug
kutoka kwenye document.

---

## 7. Homepage: accommodation, contact, na tours za leo

### Weka hizi kwenye `.env` — bila hizo hakuna namba popote

**Hili ndilo tatizo kubwa nililolikuta:** `.env` yako ina `SITE_EMAIL=`,
`SITE_WHATSAPP=`, `SITE_PHONE_PRIMARY=` **tupu**. Templates zote — header,
footer, contact page, kitufe cha WhatsApp, hata schema.org ya Google — tayari
zinasoma settings hizo. Zilikuwa hazionyeshi chochote kwa sababu hazina data,
si kwa sababu hazipo.

```
SITE_PHONE_PRIMARY=+255 681 965 636
SITE_WHATSAPP=255767753553
SITE_WHATSAPP_DISPLAY=0767 753 553
SITE_EMAIL=info@rinatourstanzania.com
SITE_EMAIL_SECONDARY=rngelula43@gmail.com
```

Kwenye Render ziweke kwenye Environment.

Mbili ni mpya:

- `SITE_EMAIL_SECONDARY` — alitoa email mbili; ilikuwa inachukua moja tu
- `SITE_WHATSAPP_DISPLAY` — `wa.me` inahitaji tarakimu na country code bila
  `+` (`255767753553`), lakini mgeni hapaswi kuonyeshwa hivyo. Sasa link
  inatumia `255767753553` na maandishi yanaonyesha `0767 753 553`

### Sehemu mbili mpya kwenye homepage

**"Where you'll stay"** — guest house sasa iko homepage, si kwenye nav tu:
bei kwa mtu BB, km 13 kutoka KIA na dakika 9–15, kitchen wazi, view ya
Kilimanjaro na Meru.

**Contact kwenye CTA band** — WhatsApp, simu na email zote mbili ziko chini ya
homepage moja kwa moja, hakuna haja ya click nyingine. Ina `id="contact"` kwa
hiyo link ya `#contact` inafanya kazi.

### Tours za leo homepage — command mpya

```
python manage.py feature_new_tours
python manage.py feature_new_tours --apply
```

Homepage inaonyesha tours zilizo `featured` **na** `published`. Tours nne za
leo ni zote mbili hapana, kwa sababu **hazina bei**.

Command **haitachapisha tour isiyo na bei**. Tour homepage isiyo na bei
haimpi mgeni cha kufanya, na inamletea Rina email ngumu. Weka bei kwenye
admin kisha run tena.

`--force` ipo kama unataka kweli, lakini sipendekezi.

### ⚠ Bike tour bado haipaswi kuchapishwa

Picha ni **pikipiki**, maelezo ya package yanasema **baiskeli za mlimani**.
Usiichapishe mpaka client ajibu. Soma `PHOTO-NOTES.md` kwenye zip ya picha.

---

## 8. Sahihisho: map ya mlima ilikuwa doa jeusi kwenye simu

Bugs mbili, zote za aina moja — kitu muhimu kilitegemea kitu kinachoweza
kushindikana.

### Bug 1: pete zote zilichorwa kwa opacity 1

CSS ilikuwa:

```css
opacity: calc(0.045 + var(--ring, 0) * 0.022);
```

Browser isipoisoma `calc()` yenye custom property, opacity inarudi `1`. Pete
saba za rangi `#2E1B12` zikijipanga juu ya nyingine kwa opacity kamili =
**weusi mtupu**.

Sasa opacity inahesabiwa Python kwenye view na kuandikwa kama attribute ya
SVG (`fill-opacity="0.089"`). Namba iliyo ndani ya markup haiwezi kushindwa
kusomeka.

### Bug 2: mstari wa njia haukuonekana kabisa

`.climb-map-route` ilikuwa na `stroke-dashoffset` kamili, ikisubiri class
`is-drawing`. Lakini **hakuna kitu kilichokuwa kinaiongeza kwenye section
hii** — `main.js` inaiongeza kwenye `.routes-map` na `.climb-figure` tu.

Kwa hiyo mstari ulikuwa hauonekani kwenye kila ukurasa wa kupanda mlima, si
kwenye simu tu.

Sasa mstari unachorwa **kikamilifu kwa default**. JS inaongeza `is-ready`
kisha `is-drawing` ili kuanzisha animation. Script ikishindwa kufanya kazi,
unapoteza animation — si mchoro.

### Kanuni

Nilichojifunza hapa: kitu chenye maana kisiwe kwenye CSS inayoweza
kushindikana wala kisisubiri JS. Rangi na nafasi za mchoro sasa ziko kwenye
markup; CSS ina mapambo tu.

Nilikuwa nimeona doa jeusi hili kwenye render yangu mapema nikadhani ni
tatizo la tool ya kurender. Lilikuwa ni bug halisi.

Faili: `tours/views.py`, `templates/tours/partials/climb_map.html`,
`static/css/style.css`, `static/js/main.js`. Baada ya copy:

```
python manage.py collectstatic --no-input
```

---

## 9. Logo ya RTZ

Logo inatumika **kama walivyoitoa** — imepunguzwa ukubwa tu, haijakatwa wala
kubadilishwa.

| Faili | Inatumika wapi |
|---|---|
| `rtz-logo-128.png` | Header (64px desktop, 52px simu) |
| `rtz-logo-32.png` | Favicon |
| `rtz-logo-180.png` | Apple touch icon |
| `og-image.png` | Link ikishirikiwa WhatsApp au Facebook |

### Nilichokosea mara ya kwanza

Nilikuwa nimeikata logo — nikaondoa `www.rinatourstanzania.com` na swoosh —
ili herufi RTZ zisomeke kwenye badge ya 40px. Ilifanya badge isomeke na
**ikaharibu logo**. Anwani ya tovuti na swoosh ni sehemu ya mchoro aliouchora
mwenye brand. Kuamua kuziondoa ni uamuzi wa brand, si wa developer. Mwenye
website alikuwa sahihi kulalamika.

Njia sahihi ilikuwa kuipa logo nafasi, si kuikata ili itoshee nafasi ndogo.

### Ukubwa

Badge la zamani lilikuwa 40px — dogo mno kwa logo yenye maandishi ndani yake.
Sasa:

- **Desktop:** 64px, header imeongezwa hadi 92px ili iitoshee
- **Simu:** 52px, header 76px. Tagline "Tanzania, at your pace" inajificha
  kwenye simu ili kutoa nafasi — logo na jina zinatosha hapo

Hakuna `border-radius` kubwa — mchoro tayari una ukingo wake wa mraba.

### Favicon na og:image hazikuwepo kabisa

Site ilikuwa **haina favicon** — tab ya browser ilionyesha ikoni tupu — na
haina `og:image`, kwa hiyo link ikishirikiwa WhatsApp ilionekana kadi tupu.
Kwa kuwa maulizo mengi ya Rina yanaanzia WhatsApp, hilo lilikuwa linagharimu.

Kwenye favicon ya 32px anwani ya tovuti haisomeki — ni logo nzima
iliyopunguzwa, kwa hiyo herufi RTZ zinaonekana na anwani inakuwa mstari wa
dhahabu. Hiyo ni kawaida kwa favicon yoyote yenye maandishi. Kama mwenye
brand anapendelea ikoni ya herufi tu kwenye 32px, aniambie — lakini
sitaikata tena bila yeye kusema.

Baada ya copy:

```
python manage.py collectstatic --no-input
```

---

## 10. Logo kubwa, WhatsApp icon, bei mpya

### Logo — ukubwa umepimwa, si kukisiwa

Nilirender logo kwa ukubwa tofauti nikaangalia ni wapi
`www.rinatourstanzania.com` inaanza kusomeka:

| Ukubwa | Anwani |
|---|---|
| 64px | haisomeki |
| 96px | mstari wa dhahabu |
| **112px** | inasomeka |
| **128px** | wazi kabisa |

Kwa hiyo: **128px laptop, 104px simu.**

Lakini 128px ya sticky header ni kubwa mno kubeba ukurasa mzima — kwenye simu
ingekula robo ya skrini kila wakati. Kwa hiyo logo **inapungua ukisogeza
chini**: 128px mwanzoni ambapo mtu anaisoma, 60px baada ya kupita skrini ya
kwanza.

Ukubwa mkubwa ndio default ya CSS; JS inaongeza tu class ya kupunguza. Script
ikishindwa kufanya kazi, mtumiaji anabaki na logo inayosomeka — hapotezi
kitu. (Hii ndiyo kanuni ile ile iliyoshindikana kwenye map ya mlima.)

Kwenye simu chini ya 420px, jina linakuwa "Rina Tours" badala ya "Rina Tours
Tanzania" — logo na jina kamili haviwezi kutoshea, na logo ndiyo yenye anwani.

### WhatsApp icon

Icon ya WhatsApp sasa iko pembeni ya namba kila mahali inapoonekana: header
bar, footer, contact page na homepage. Ni SVG iliyoandikwa ndani ya HTML —
haina request ya ziada, na ina rangi ya kijani ya WhatsApp (`#25D366`) ili
itambulike papo hapo.

Namba **0767 753 553** ndiyo ya WhatsApp — ndiyo iliyo kwenye
`SITE_WHATSAPP_DISPLAY`, na link inaenda `wa.me/255767753553`.

### Bei

```
python manage.py set_stay_price --apply
python manage.py restore_climb_prices --apply
python manage.py set_climb_price --price 1846 --apply
```

Accommodation: $60 -> **$80** kwa mtu.

Kilimanjaro: **floor ya $1846**. Lazima urun `restore_climb_prices` kwanza —
bei zilikuwa zote $1746 baada ya `--flat`, kwa hiyo floor ingeziweka zote
$1846 na kupoteza tofauti ya urefu tena. Baada ya restore:

| Route | Siku | Bei |
|---|---|---|
| Marangu, Machame, Umbwe | 6 | $1,846 |
| Machame 7, Rongai, Lemosho | 7 | $1,846 |
| Lemosho 8 | 8 | $2,000 |
| Northern Circuit | 9 | $2,200 |

Bei ya chini kabisa ni $1,846, na ndefu zinabaki juu yake.

Baada ya copy:

```
python manage.py collectstatic --no-input
```

---

## 11. Logo kubwa zaidi, WhatsApp green, namba ya simu

### Kwa nini logo ilikuwa bado ndogo

Si kwamba ukubwa haukuwekwa. Project **ilikuwa tayari na mfumo wa kupunguza
header** — class `is-stuck`, ikibana header hadi 66px ukisogeza chini. Mimi
nikaongeza mfumo wa pili (`is-compact`) bila kuuona. Zikagongana: `is-stuck`
ilibana bar hadi 66px **bila kugusa logo**, kwa hiyo logo ya 128px ilikuwa
inabanwa ndani ya nafasi ya 66px.

Sasa kuna mfumo mmoja tu. Nimeondoa `is-compact` yangu na JS yake, na
nikaongeza ukubwa wa logo kwenye `is-stuck` iliyokuwepo. Header ya `is-stuck`
sasa ni 82px badala ya 66px ili logo iliyopungua itoshee.

### Ukubwa mpya

| | Mwanzoni | Ukisogeza chini |
|---|---|---|
| Laptop | **168px** | 64px |
| Simu | **132px** | 56px |

Anwani `www.rinatourstanzania.com` inasomeka vizuri kwa vipimo vyote viwili.

### WhatsApp icon

- Kijani `#25D366` sasa kimeandikwa **ndani ya SVG path yenyewe**, si kupitia
  CSS. Ilikuwa `fill="currentColor"` ikitegemea rule ya CSS kuifikia — na
  rule ya CSS inayoweza kutofika ndilo tatizo lililotufanya map ya mlima iwe
  doa jeusi. Rangi yenye maana haipaswi kutegemea stylesheet
- Ndogo: `0.82em`, ni alama pembeni ya namba, si kitufe

### Namba mbili zinatofautishwa

- **0767 753 553** — WhatsApp, yenye icon ya kijani
- **+255 681 965 636** — sasa ina maandishi madogo *"local line, calls only"*

Bila hivyo mgeni wa nje anajaribu WhatsApp kwenye namba ya simu ya kawaida,
haipokelewi, anadhani hakuna anayejibu.

Baada ya copy:

```
python manage.py collectstatic --no-input
```
