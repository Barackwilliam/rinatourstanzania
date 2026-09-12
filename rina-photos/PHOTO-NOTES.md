# Picha za client — zilizoandaliwa

Picha 19, zimepangwa kwa folder moja kwa kila tour. **Watermark ya "CAMON 40
Pro" imeondolewa** kwenye picha sita zilizokuwa nayo.

## Jinsi ya kuzipakia

Project tayari ina command ya hili (`import_photos`) — inapunguza ukubwa,
**inaondoa EXIF** (picha za simu zina GPS ndani yake; picha ya nyumba ya
kulala ingemwambia yeyote mahali jengo lilipo), na inapakia Supabase.

Run kila mstari mmoja mmoja:

```
python manage.py import_photos stay rina-photos/stay
python manage.py import_photos package mount-kilimanjaro-machame-route rina-photos/package--mount-kilimanjaro-machame-route
python manage.py import_photos package materuni-village-and-coffee-experience rina-photos/package--materuni-village-and-coffee-experience
python manage.py import_photos package materuni-waterfall-and-village-hike rina-photos/package--materuni-waterfall-and-village-hike
python manage.py import_photos package chagga-culture-and-coffee-tour rina-photos/package--chagga-culture-and-coffee-tour
python manage.py import_photos package maasai-boma-day-overnight-camp rina-photos/package--maasai-boma-day-overnight-camp
python manage.py import_photos package kilimanjaro-foothills-bike-tour rina-photos/package--kilimanjaro-foothills-bike-tour
```

Ongeza `--dry-run` mwishoni kuona kwanza bila kupakia.

Faili `01-` ndiyo inakuwa picha kuu; nyingine zinaingia kwenye gallery kwa
mpangilio huo.

---

## ⚠ Muhimu: "bike tours" ni PIKIPIKI, si baiskeli

Picha mbili za bike tour zinaonyesha **pikipiki** — Bajaj Boxer na Boxer 150,
wageni wamekaa nyuma ya madereva wa kienyeji, kofia ngumu, njia ya vumbi
katikati ya nyika ya miiba na miti ya Maasai. Si baiskeli hata kidogo.

Package niliyoiandika inasema "mountain bike na helmet", "coffee shamba za
Chagga", "gari la msaada linafuata". **Yote si sahihi.** Ningeiacha hivyo,
mteja angelipia akitegemea kuendesha baiskeli kwenye miteremko ya kahawa na
akaletewa pikipiki ya kukodi kwenye nyika — hiyo ni malalamiko, au refund.

Muulize client:

1. Ni pikipiki au baiskeli? Kama ni zote mbili, ni packages mbili tofauti
2. Mgeni anaendesha mwenyewe au anakaa nyuma ya dereva? Picha zinaonyesha
   wanakaa nyuma
3. Njia ni ipi? Picha zinaonyesha nyika kavu yenye miiba, si miteremko ya
   kahawa
4. Inachukua muda gani, na bei?

Nikijua majibu nitaandika upya package na maelezo sahihi. Kwa sasa picha
zimewekwa kwenye folder yake, lakini **usiipakie mpaka maelezo yarekebishwe** —
picha sahihi juu ya maelezo yasiyo sahihi ni mbaya zaidi kuliko kukosa picha.

---

## Zilizo na uhakika mkubwa

Hizi zina ushahidi ndani ya picha yenyewe:

| Picha | Ushahidi |
|---|---|
| `01-machame-camp-sign` | Bango linasomeka "MACHAME CAMP, ELEVATION 2835M" pamoja na umbali hadi Shira, Lava Tower, Barranco, Karanga, Barafu, Uhuru |
| `01-roasted-coffee-bowl` | Bango "Good COFFEE takes time — MATERUNI ORG" |
| `02-ground-coffee-tasting` | Unga wa kahawa mkononi, nyumba za Kichagga nyuma |
| `01-waterfall` / `02-waterfall-group` | Maporomoko marefu, mwamba wa lava, mimea ya milimani — inalingana na Materuni |
| `01-exterior-garden` | Jengo jeupe, bustani ya kijani, miti — inalingana na maelezo yake ya "green and well preserved trees" |

## Zinazohitaji uthibitisho wake

| Picha | Kwa nini |
|---|---|
| `02-alpine-traverse`, `03-moorland-forest` | Ni Kilimanjaro bila shaka — moorland yenye lichen na eneo la miamba. Lakini sijui kama ni Machame au Lemosho; njia zinapitana. Nimeziweka Machame kwa sababu picha ya bango ni ya Machame na zinaonekana za safari moja |
| `01-ndizi-na-nyama` | Chakula cha kienyeji — ndizi na nyama, kachumbari. Niliiweka Chagga Culture & Coffee Tour, lakini inaweza kuwa chakula cha kambi ya safari yoyote |
| `04-climb-briefing` | Wageni wamezunguka meza na **map ya Kilimanjaro** — inaonekana ni briefing kabla ya kupanda. Nimeiweka kwenye stay kwa sababu ni chumba kile kile cha picha nyingine |
| Picha zote za `stay` | Ni chumba na jengo moja, lakini **sijui kama ni mali yao** au mahali walipofikia. Thibitisha kabla ya kuzipakia |

## Picha ambazo hazipo bado

Hakuna picha ya: safari ya wanyama, Serengeti, Ngorongoro, Chemka hot springs,
Moshi town, gari la safari, au wafanyakazi wake. Hizo ndizo tours zinazouzwa
zaidi — muulize azipeleke.
