"""
What the operator wants pushed forward.

Mountain trekking is the priority — Kilimanjaro and Meru are what the business
leads with — so that category sorts first everywhere and its flagship climbs
fill the featured row on the homepage.

Change the two lists below and re-run `python manage.py apply_priorities`.
Nothing else needs editing: the category order drives the navigation, the
homepage tiles and the tour index, and the featured list drives the homepage
row and the promoted panel in the Tours menu.
"""

# First in this list sorts first. Any category not named keeps its import order
# and follows the ones that are.
CATEGORY_ORDER = [
    "Trekking / Mountain Climbing",
    "Safari / Wildlife Tours",
    "Beach / Coastal Tours",
    "Cultural Tours",
    "Camping Tours",
    "Nature Tours",
    "Water Sports & Marine Activities",
]

# The homepage row, in the order they should appear. Mountains lead, then the
# safaris and the beach combination that most first-time visitors book.
FEATURED_SLUGS = [
    "mount-kilimanjaro-7-days-machame-route",
    "mount-kilimanjaro-lemosho-route",
    "mount-meru-3-days-trekking",
    "5-days-classic-tanzania-safari",
    "10-days-tanzania-safari-and-zanzibar-beach",
    "materuni-waterfall-and-village-hike",
]
