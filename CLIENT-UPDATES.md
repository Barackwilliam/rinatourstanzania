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
