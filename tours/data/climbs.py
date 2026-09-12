"""
Camp-by-camp altitude profiles for the mountain routes.

Altitudes are the figures published on the park boards and used across the
trekking industry, in metres above sea level. They are approximate — a camp is
an area, not a point — and every one is editable in the admin, so a guide who
knows better can correct it without touching this file.

`day` is the trekking day the stage falls on, so the profile can be read
alongside the itinerary on the same page.
"""

CLIMBS = [
    {
        "name": "Marangu Route",
        "mountain": "Mount Kilimanjaro",
        "summary": "The only route with hut accommodation. A gentle gradient, "
                   "but the same path up and down.",
        "stages": [
            ("Marangu Gate", 1860, 1),
            ("Mandara Hut", 2700, 1),
            ("Horombo Hut", 3720, 2),
            ("Kibo Hut", 4703, 3),
            ("Uhuru Peak", 5895, 4),
            ("Horombo Hut", 3720, 4),
            ("Marangu Gate", 1860, 5),
        ],
    },
    {
        "name": "Machame Route",
        "mountain": "Mount Kilimanjaro",
        "summary": "The busiest route, and the most varied. Climbs high to Lava "
                   "Tower then drops to Barranco — hard work, good for acclimatising.",
        "stages": [
            ("Machame Gate", 1800, 1),
            ("Machame Camp", 2835, 1),
            ("Shira Camp", 3750, 2),
            ("Lava Tower", 4630, 3),
            ("Barranco Camp", 3960, 3),
            ("Karanga Camp", 3995, 4),
            ("Barafu Camp", 4640, 5),
            ("Uhuru Peak", 5895, 6),
            ("Mweka Camp", 3100, 6),
        ],
    },
    {
        "name": "Lemosho Route",
        "mountain": "Mount Kilimanjaro",
        "summary": "Approaches from the west through forest and the Shira Plateau. "
                   "Longer, quieter, and the best acclimatisation of the popular routes.",
        "stages": [
            ("Lemosho Gate", 2100, 1),
            ("Mti Mkubwa", 2780, 1),
            ("Shira 1 Camp", 3505, 2),
            ("Shira 2 Camp", 3850, 3),
            ("Barranco Camp", 3960, 4),
            ("Karanga Camp", 3995, 5),
            ("Barafu Camp", 4640, 6),
            ("Uhuru Peak", 5895, 7),
            ("Mweka Camp", 3100, 7),
        ],
    },
    {
        "name": "Rongai Route",
        "mountain": "Mount Kilimanjaro",
        "summary": "The only approach from the north, near the Kenyan border. "
                   "Drier, quieter, and it descends by Marangu.",
        "stages": [
            ("Rongai Gate", 1950, 1),
            ("Simba Camp", 2625, 1),
            ("Kikelewa Camp", 3600, 2),
            ("Mawenzi Tarn", 4315, 3),
            ("Kibo Hut", 4703, 4),
            ("Uhuru Peak", 5895, 5),
            ("Horombo Hut", 3720, 5),
            ("Marangu Gate", 1860, 6),
        ],
    },
    {
        "name": "Umbwe Route",
        "mountain": "Mount Kilimanjaro",
        "summary": "The steepest and shortest way up. Very little acclimatisation "
                   "before Barranco — for experienced, fit trekkers only.",
        "stages": [
            ("Umbwe Gate", 1600, 1),
            ("Umbwe Cave Camp", 2940, 1),
            ("Barranco Camp", 3960, 2),
            ("Karanga Camp", 3995, 3),
            ("Barafu Camp", 4640, 4),
            ("Uhuru Peak", 5895, 5),
            ("Mweka Camp", 3100, 5),
        ],
    },
    {
        "name": "Northern Circuit",
        "mountain": "Mount Kilimanjaro",
        "summary": "The longest route on the mountain. Crosses the quiet northern "
                   "slopes, with the most time to acclimatise of any itinerary.",
        "stages": [
            ("Lemosho Gate", 2100, 1),
            ("Mti Mkubwa", 2780, 1),
            ("Shira 1 Camp", 3505, 2),
            ("Shira 2 Camp", 3850, 3),
            ("Lava Tower", 4630, 4),
            ("Moir Hut", 4200, 4),
            ("Buffalo Camp", 4020, 5),
            ("Third Cave", 3800, 6),
            ("School Hut", 4800, 7),
            ("Uhuru Peak", 5895, 8),
            ("Mweka Camp", 3100, 8),
        ],
    },
    {
        "name": "Mount Meru",
        "mountain": "Mount Meru",
        "summary": "Tanzania's second mountain, inside Arusha National Park. "
                   "An armed ranger walks with you through the lower forest.",
        "stages": [
            ("Momella Gate", 1500, 1),
            ("Miriakamba Hut", 2514, 1),
            ("Saddle Hut", 3570, 2),
            ("Socialist Peak", 4566, 3),
            ("Miriakamba Hut", 2514, 3),
            ("Momella Gate", 1500, 4),
        ],
    },
]

# Which package titles map onto which climb, where the package's own `route`
# field does not already say. Kilimanjaro packages carry a route; the Meru ones
# do not, because the mountain has only one way up.
TITLE_HINTS = {
    "Mount Meru": ["mount meru"],
}
