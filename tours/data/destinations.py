"""
Canonical destination list, with every spelling the client used mapped onto it.

The source content had 93 distinct destination strings for roughly 45 real
places — 'Serengeti', 'Serengeti National Park', 'Ngorongoro', 'Ngorongoro
Crater' and 'Ngorongoro Conservation Area' were all being written as separate
places. Left alone, the destination filter would show the same park several
times. This table is the single source of truth for the importer.

Format:  canonical name -> (region, [aliases as written by the client])
"""

CANONICAL = {
    # --- Northern circuit ---------------------------------------------------
    "Serengeti National Park": ("northern", ["Serengeti"]),
    "Ngorongoro Crater": ("northern", [
        "Ngorongoro", "Ngorongoro Conservation Area"]),
    "Ngorongoro Highlands": ("northern", []),
    "Tarangire National Park": ("northern", ["Tarangire"]),
    "Lake Manyara National Park": ("northern", ["Lake Manyara"]),
    "Arusha National Park": ("northern", []),
    "Empakai Crater": ("northern", []),
    "Lake Natron": ("northern", []),
    "Lake Eyasi": ("northern", []),
    "Mto wa Mbu": ("northern", []),
    "Karatu": ("northern", []),
    "Arusha": ("northern", ["Arusha City"]),

    # --- Southern circuit ---------------------------------------------------
    "Mikumi National Park": ("southern", ["Mikumi"]),
    "Nyerere National Park": ("southern", []),
    "Ruaha National Park": ("southern", []),
    "Udzungwa Mountains National Park": ("southern", [
        "Udzungwa", "Udzungwa Mountains"]),
    "Sanje Waterfalls": ("southern", []),
    "Uluguru Mountains": ("southern", []),
    "Morogoro": ("southern", []),

    # --- Western ------------------------------------------------------------
    "Rubondo Island National Park": ("western", []),
    "Lake Victoria": ("western", []),
    "Mwanza": ("western", []),
    "Sukuma Community": ("western", []),

    # --- Mountains & highlands ---------------------------------------------
    "Mount Kilimanjaro": ("mountain", []),
    "Kilimanjaro Foothills": ("mountain", [
        "Mount Kilimanjaro Foothills", "Kilimanjaro Region"]),
    "Mount Meru": ("mountain", []),
    "Mount Hanang": ("mountain", []),
    "Ol Doinyo Lengai": ("mountain", []),
    "Usambara Mountains": ("mountain", ["Usambara", "Lushoto"]),
    "Pare Mountains": ("mountain", []),
    "Materuni": ("mountain", [
        "Materuni Village", "Materuni Village, Kilimanjaro", "Materuni, Kilimanjaro"]),
    "Chemka Hot Springs": ("mountain", []),
    "Lake Chala": ("mountain", []),
    "Moshi": ("mountain", []),

    # --- Coast --------------------------------------------------------------
    "Saadani National Park": ("coastal", ["Saadani", "Saadani River"]),
    "Bagamoyo": ("coastal", []),
    "Pangani": ("coastal", []),
    "Tanga": ("coastal", ["Tanga Coast", "Tanga & Amboni Caves"]),
    "Mikindani": ("coastal", ["Mtwara Coast", "Mtwara"]),
    "Dar es Salaam": ("coastal", ["Dar es Salaam Coast"]),
    "Bongoyo Island": ("coastal", ["Bongoyo"]),
    "Mbudya Island": ("coastal", []),

    # --- Zanzibar -----------------------------------------------------------
    "Zanzibar": ("zanzibar", [
        "Zanzibar Coast", "Zanzibar Local Village", "Zanzibar Diving Sites",
        "Zanzibar Marine Areas"]),
    "Stone Town": ("zanzibar", [
        "Stone Town & Forodhani", "Stone Town Local Market"]),
    "Nungwi": ("zanzibar", []),
    "Kendwa": ("zanzibar", []),
    "Paje": ("zanzibar", ["Paje Beach", "East Coast"]),
    "Kizimkazi": ("zanzibar", []),
    "Prison Island": ("zanzibar", []),
    "Nakupenda Sandbank": ("zanzibar", []),
    "Mnemba Island": ("zanzibar", ["Mnemba Island Marine Area", "Matemwe"]),
    "Menai Bay": ("zanzibar", ["Menai Bay Conservation Area"]),
    "Jozani Forest": ("zanzibar", []),
    "Zanzibar Spice Farms": ("zanzibar", []),
    "Zanzibar Mangroves": ("zanzibar", ["Zanzibar Mangrove Areas"]),
}

# Strings in the source that are regions or marketing phrases, not places.
# They are skipped rather than becoming fake destinations.
IGNORE = {
    "Northern Tanzania",
    "Northern Tanzania & Coast",
    "Northern & Coastal Tanzania",
    "Tanzania Mainland",
    "Tanzania Cultural & Heritage Destinations",
    "Selected Nature Area",
    "Usambara / Selected Nature Area",
    "Nearby Islands",
    "Indian Ocean",
    "Coast",
    "Maasai Village",
    "Maasai Boma",
    "Maasai Community & Nature Area",
    "Iraqw Community",
    "Chagga Cultural Experience",
}


def lookup():
    """Return {lowercased alias or name: canonical name}."""
    table = {}
    for name, (_region, aliases) in CANONICAL.items():
        table[name.lower()] = name
        for alias in aliases:
            table[alias.lower()] = name
    return table
