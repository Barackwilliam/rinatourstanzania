"""
Tours the client asked for after the first content pass.

Prices and durations here are placeholders where the client did not give one —
every package marked `needs_pricing` is created UNPUBLISHED so nothing goes
live with a made-up figure on it. Fill the price in the admin and tick
'published'.

The Maasai copy is the client's own description, tidied but not embellished:
a visit to the bomas, the whole day with the family, camping alongside, and
taking part in the work — collecting firewood, cooking, and eating together.
"""

PACKAGES = [
    {
        "title": "Kilimanjaro Foothills Bike Tour",
        "slug": "kilimanjaro-foothills-bike-tour",
        "primary_category": "Nature Tours",
        "categories": ["Nature Tours", "Cultural Tours"],
        "duration_days": 1,
        "duration_text": "",
        "starting_point": "Moshi",
        "destinations": ["Moshi", "Materuni"],
        "needs_pricing": True,
        "short_description": (
            "Ride the lanes through the coffee shambas on Kilimanjaro's lower "
            "slopes, with the mountain above you the whole way."),
        "description": (
            "A cycling day on the southern foothills, starting from Moshi and "
            "climbing gently through Chagga farmland — coffee and banana "
            "shambas, irrigation furrows centuries old, and villages where the "
            "road is still the meeting place.\n\n"
            "The gradient is steady rather than steep, and the support vehicle "
            "follows the whole route, so anyone comfortable on a bicycle for a "
            "few hours can ride it. We stop where it is worth stopping.\n\n"
            "On a clear morning Kibo stands over the whole ride."),
        "highlights": (
            "Coffee and banana shambas on the lower slopes\n"
            "Chagga villages and the old irrigation furrows\n"
            "Kilimanjaro in view for most of the ride\n"
            "Support vehicle the whole way\n"
            "Mountain bike and helmet provided"),
        "includes": (
            "Mountain bike and helmet\n"
            "Guide\n"
            "Support vehicle\n"
            "Drinking water\n"
            "Lunch"),
        "excludes": "Tips\nPersonal items",
        "best_for": "Anyone comfortable on a bike for a few hours. No racing.",
    },
    {
        "title": "Moshi Town Tour",
        "slug": "moshi-town-tour",
        "primary_category": "Cultural Tours",
        "categories": ["Cultural Tours"],
        "duration_days": 1,
        "duration_text": "Half day",
        "starting_point": "Moshi",
        "destinations": ["Moshi"],
        "needs_pricing": True,
        "short_description": (
            "The town at the foot of the mountain on foot — the market, the "
            "coffee houses, and the streets most visitors only drive through."),
        "description": (
            "Moshi is where every Kilimanjaro climb begins and ends, and almost "
            "nobody looks at it. This is a walking half-day through the town "
            "itself.\n\n"
            "The central market for produce, spices and fabric; the old German "
            "and Asian quarters and what is left of their architecture; the "
            "coffee houses that made the town's name; and the clock tower with "
            "the mountain behind it.\n\n"
            "Easy to combine with a hot springs afternoon — ask when you book."),
        "highlights": (
            "Moshi central market\n"
            "Old town architecture\n"
            "Coffee houses and a tasting\n"
            "Clock tower, with Kilimanjaro behind it\n"
            "Can be combined with Chemka Hot Springs"),
        "includes": "Guide\nDrinking water\nCoffee tasting",
        "excludes": "Lunch\nPurchases at the market\nTips",
        "best_for": "A spare half day before or after a climb.",
    },
    {
        "title": "Moshi Town & Chemka Hot Springs Day Trip",
        "slug": "moshi-town-chemka-hot-springs-day-trip",
        "primary_category": "Cultural Tours",
        "categories": ["Cultural Tours", "Nature Tours"],
        "duration_days": 1,
        "starting_point": "Moshi",
        "destinations": ["Moshi"],
        "needs_pricing": True,
        "short_description": (
            "Moshi in the morning, then the turquoise water at Chemka in the "
            "afternoon — the two things worth doing on a free day here."),
        "description": (
            "The pairing the client asked for, as one day.\n\n"
            "Morning in Moshi: the market, the old quarters, the coffee. Then "
            "out to Chemka — Kikuletwa — where spring water comes up through "
            "the rock warm and astonishingly clear, under fig trees with roots "
            "hanging into the pool.\n\n"
            "Swim, eat, and come back in the late afternoon."),
        "highlights": (
            "Moshi market and old town in the morning\n"
            "Chemka (Kikuletwa) hot springs in the afternoon\n"
            "Swimming in clear spring water\n"
            "Lunch at the springs\n"
            "Back in Moshi by evening"),
        "includes": "Transport\nGuide\nEntry fees\nLunch\nDrinking water",
        "excludes": "Tips\nPersonal items",
        "best_for": "A free day between flights, or after a climb.",
    },
    {
        "title": "Maasai Boma Day & Overnight Camp",
        "slug": "maasai-boma-day-overnight-camp",
        "primary_category": "Cultural Tours",
        "categories": ["Cultural Tours", "Camping Tours"],
        "duration_days": 2,
        "duration_nights": 1,
        "starting_point": "Moshi",
        "needs_pricing": True,
        "short_description": (
            "A full day inside a Maasai boma and a night camped alongside it — "
            "not a visit, a day spent with the family."),
        "description": (
            "Most Maasai village tours are an hour: a dance, a photograph, a "
            "stall of beadwork. This is the client's own idea of what the day "
            "should be instead.\n\n"
            "You arrive in the morning and stay. You go out with the family to "
            "collect firewood. You help cook, and you eat what is cooked, with "
            "them, not served separately. You sit through the afternoon and the "
            "evening as the herds come back in.\n\n"
            "You camp beside the boma rather than driving back to a lodge, and "
            "you leave after breakfast the next day.\n\n"
            "This is a real household, not a set. Come prepared to be a guest "
            "and to be useful."),
        "highlights": (
            "The whole day with one family, not an hour\n"
            "Collecting firewood with the household\n"
            "Cooking and eating together\n"
            "Camping beside the boma overnight\n"
            "The herds coming in at dusk"),
        "includes": (
            "Transport from Moshi\n"
            "Guide and translation\n"
            "Camping equipment\n"
            "All meals\n"
            "Community fee to the boma"),
        "excludes": "Tips\nPersonal items\nAlcohol",
        "best_for": "Travellers who want time rather than a photo stop.",
        "important_note": (
            "This is someone's home. Photographs are welcome once you have "
            "asked; the guide will tell you when it is right to ask. Facilities "
            "are what the boma has — there is no plumbing."),
    },
]

# Existing day trips the client specifically named as missing. They are already
# on the site; they were simply below the fold everywhere they appeared, so the
# seeding command lifts them by setting `order`.
#
# Matched on KEYWORDS, not on exact titles. Titles are generated by the content
# import and differ between one run of it and the next — matching the full
# string worked against one database and silently found nothing against
# another, which is exactly the failure that is easy to miss because the
# command still reports success.
#
# Restricted to day trips, so "coffee" cannot pull in a multi-day tour.
PROMOTE_DAY_TRIP_KEYWORDS = [
    "materuni",     # the waterfalls he named
    "waterfall",    # Sanje too — he asked for waterfalls generally
    "coffee",       # coffee tours, incl. Chagga Culture & Coffee
    "maasai",       # the village/boma trips
    "chemka",       # hot springs
    "hot spring",
]
