"""
Latitude / longitude for every canonical destination, so it can be plotted on
the routes map. Decimal degrees; latitude is negative south of the equator.

These are approximate centre points for the park, town or island — good enough
to place a marker on a country-scale map, not survey coordinates.
"""

COORDINATES = {
    # --- Northern circuit ---------------------------------------------------
    "Serengeti National Park":        (-2.33, 34.83),
    "Ngorongoro Crater":              (-3.20, 35.58),
    "Ngorongoro Highlands":           (-3.15, 35.50),
    "Tarangire National Park":        (-4.00, 36.00),
    "Lake Manyara National Park":     (-3.50, 35.82),
    "Arusha National Park":           (-3.25, 36.83),
    "Empakai Crater":                 (-2.93, 35.83),
    "Lake Natron":                    (-2.42, 36.00),
    "Lake Eyasi":                     (-3.65, 35.10),
    "Mto wa Mbu":                     (-3.37, 35.85),
    "Karatu":                         (-3.34, 35.67),
    "Arusha":                         (-3.37, 36.68),

    # --- Southern circuit ---------------------------------------------------
    "Mikumi National Park":           (-7.40, 37.10),
    "Nyerere National Park":          (-8.00, 37.80),
    "Ruaha National Park":            (-7.70, 34.55),
    "Udzungwa Mountains National Park": (-7.80, 36.55),
    "Sanje Waterfalls":               (-7.84, 36.89),
    "Uluguru Mountains":              (-7.05, 37.68),
    "Morogoro":                       (-6.82, 37.66),

    # --- Western ------------------------------------------------------------
    "Rubondo Island National Park":   (-2.30, 31.85),
    "Lake Victoria":                  (-2.00, 32.90),
    "Mwanza":                         (-2.52, 32.90),
    "Sukuma Community":               (-2.80, 33.20),

    # --- Mountains & highlands ---------------------------------------------
    "Mount Kilimanjaro":              (-3.07, 37.35),
    "Kilimanjaro Foothills":          (-3.20, 37.30),
    "Mount Meru":                     (-3.24, 36.75),
    "Mount Hanang":                   (-4.43, 35.40),
    "Ol Doinyo Lengai":               (-2.76, 35.91),
    "Usambara Mountains":             (-4.70, 38.30),
    "Pare Mountains":                 (-4.30, 37.90),
    "Materuni":                       (-3.22, 37.30),
    "Chemka Hot Springs":             (-3.42, 37.30),
    "Lake Chala":                     (-3.32, 37.70),
    "Moshi":                          (-3.35, 37.34),

    # --- Coast --------------------------------------------------------------
    "Saadani National Park":          (-6.02, 38.78),
    "Bagamoyo":                       (-6.44, 38.90),
    "Pangani":                        (-5.43, 38.98),
    "Tanga":                          (-5.07, 39.10),
    "Mikindani":                      (-10.28, 40.12),
    "Dar es Salaam":                  (-6.82, 39.28),
    "Bongoyo Island":                 (-6.68, 39.30),
    "Mbudya Island":                  (-6.66, 39.24),

    # --- Zanzibar -----------------------------------------------------------
    "Zanzibar":                       (-6.16, 39.20),
    "Stone Town":                     (-6.16, 39.19),
    "Nungwi":                         (-5.73, 39.29),
    "Kendwa":                         (-5.76, 39.29),
    "Paje":                           (-6.27, 39.53),
    "Kizimkazi":                      (-6.44, 39.47),
    "Prison Island":                  (-6.13, 39.16),
    "Nakupenda Sandbank":             (-6.14, 39.17),
    "Mnemba Island":                  (-5.82, 39.39),
    "Menai Bay":                      (-6.36, 39.30),
    "Jozani Forest":                  (-6.27, 39.42),
    "Zanzibar Spice Farms":           (-6.10, 39.28),
    "Zanzibar Mangroves":             (-6.20, 39.35),
}


# The lines drawn on the homepage map. Each is a real journey shape the
# operator sells; the colours are chosen to stay apart from one another and
# to read against the ivory map background.
ROUTES = [
    {
        "name": "Northern circuit safari",
        "slug": "northern-circuit",
        "colour": "#9E2B25",
        "summary": "Arusha, Tarangire, Serengeti and the Ngorongoro Crater.",
        "package_slug": "5-days-classic-tanzania-safari",
        "stops": ["Arusha", "Tarangire National Park", "Lake Manyara National Park",
                  "Serengeti National Park", "Ngorongoro Crater"],
    },
    {
        "name": "Bush to beach",
        "slug": "bush-to-beach",
        "colour": "#B98431",
        "summary": "Northern parks first, then the Indian Ocean.",
        "package_slug": "10-days-tanzania-safari-and-zanzibar-beach",
        "stops": ["Arusha", "Tarangire National Park", "Serengeti National Park",
                  "Ngorongoro Crater", "Dar es Salaam", "Stone Town", "Nungwi"],
    },
    {
        "name": "Kilimanjaro & Zanzibar",
        "slug": "kilimanjaro-zanzibar",
        "colour": "#2F6F5E",
        "summary": "Africa's highest peak, then recovery on the coast.",
        "package_slug": "mount-kilimanjaro-7-days-machame-route",
        "stops": ["Moshi", "Mount Kilimanjaro", "Dar es Salaam", "Stone Town", "Paje"],
    },
    {
        "name": "Southern parks",
        "slug": "southern-parks",
        "colour": "#3E5C8A",
        "summary": "Mikumi, Nyerere and Ruaha, out of Dar es Salaam.",
        "package_slug": "3-days-nyerere-wildlife-and-boat-safari",
        "stops": ["Dar es Salaam", "Mikumi National Park", "Nyerere National Park",
                  "Ruaha National Park"],
    },
    {
        "name": "Coast & islands",
        "slug": "coast-islands",
        "colour": "#00767F",
        "summary": "Saadani, the old Swahili ports and Zanzibar.",
        "package_slug": "saadani-and-zanzibar-combination",
        "stops": ["Dar es Salaam", "Bagamoyo", "Saadani National Park", "Pangani",
                  "Tanga", "Stone Town"],
    },
    {
        "name": "Mountains & highlands",
        "slug": "mountains-highlands",
        "colour": "#6B4E9E",
        "summary": "Meru, the Usambaras and the Udzungwa forests.",
        "package_slug": "usambara-mountains-trekking",
        "stops": ["Arusha", "Mount Meru", "Pare Mountains", "Usambara Mountains",
                  "Udzungwa Mountains National Park"],
    },
]
