"""
Plan-view map of Mount Kilimanjaro, for drawing a climb route from gate to
summit.

This is the companion to the altitude profile. The profile answers "how steep
is it"; this answers "which way round the mountain do I actually walk", which
is the question someone comparing Rongai with Machame is really asking.

=============================================================================
ABOUT THE COORDINATES — READ THIS BEFORE TRUSTING THEM
=============================================================================

Only three positions below are taken from a published source:

    Uhuru Peak       3.0758 S, 37.3533 E   (summit, widely published)
    Barafu Camp      3.0997 S, 37.3782 E   (published to the second)
    Park bounds      2.83-3.17 S, 37.17-37.67 E

Everything else is INTERPOLATED from those anchors plus the known layout of
the mountain: which side each gate sits on, Kibo at the centre, Mawenzi to
the east, the Shira plateau to the west, and the southern circuit running
Barranco - Karanga - Barafu below the Kibo cone.

They are good enough to show the SHAPE of a route — that Rongai comes over
the north, that Machame swings west then round the south — and they are not
good enough to navigate by. No public source publishes a full camp-by-camp
coordinate table for all seven routes; even KINAPA's own interactive map
states its marker positions are approximate and for orientation only.

Every one of these is editable in the admin, and each stage carries a
`coords_verified` flag. The intent is that Rina's own mountain guides — who
have walked these camps with a GPS in their pocket — correct them, tick the
box, and the "positions approximate" notice disappears from the map by
itself. Run `manage.py export_camp_coords` to get the list to hand them.

Same policy as the altitudes in climbs.py: seed something sensible, let the
people who actually know the mountain fix it without touching this file.
"""

# --- Projection ---------------------------------------------------------------
# A plain equirectangular fit to a box around the mountain. At 3 degrees south
# the longitude/latitude distortion is under a tenth of a percent, so there is
# nothing here worth a real projection library.

WEST, EAST = 36.95, 37.62
NORTH, SOUTH = -2.88, -3.32

WIDTH, HEIGHT = 760, 520
VIEWBOX = f"0 0 {WIDTH} {HEIGHT}"


def project(lon, lat):
    """Longitude/latitude to SVG x/y inside the VIEWBOX above."""
    x = (lon - WEST) / (EAST - WEST) * WIDTH
    y = (lat - NORTH) / (SOUTH - NORTH) * HEIGHT
    return round(x, 1), round(y, 1)


# --- The mountain itself ------------------------------------------------------
# Concentric rings standing in for contour lines, so a route has something to
# read against. Each entry is (centre_lon, centre_lat, radius_lon, radius_lat)
# and they are drawn as ellipses, faintest first.
#
# Kibo is close to circular; the Shira plateau spreads west; Mawenzi is a
# smaller mass east of Kibo across the saddle.

KIBO = (37.3533, -3.0700)

CONTOURS = [
    # outer forest and moorland belt
    (37.3300, -3.0800, 0.290, 0.215),
    (37.3350, -3.0780, 0.235, 0.175),
    # moorland into alpine desert
    (37.3450, -3.0740, 0.175, 0.130),
    (37.3500, -3.0720, 0.120, 0.090),
    # the Kibo cone
    (37.3533, -3.0700, 0.072, 0.054),
    (37.3533, -3.0700, 0.038, 0.028),
    # crater rim
    (37.3533, -3.0690, 0.018, 0.013),
]

# Mawenzi, the jagged eastern cone
MAWENZI = (37.4550, -3.1000, 0.036, 0.027)

# The Shira plateau, west of Kibo
SHIRA_PLATEAU = (37.2100, -3.0800, 0.085, 0.055)


# --- Camp, hut and gate positions ---------------------------------------------
# name -> (longitude, latitude). Names must match ClimbStage.name exactly; the
# seeding command matches on name and leaves anything it does not recognise
# without coordinates, so a camp added later simply will not plot until someone
# gives it a position.

CAMP_COORDS = {
    # --- verified ---------------------------------------------------------
    "Uhuru Peak": (37.3533, -3.0758),
    "Barafu Camp": (37.3782, -3.0997),

    # --- gates (approximate) ----------------------------------------------
    "Marangu Gate": (37.5175, -3.2325),
    "Machame Gate": (37.2536, -3.1828),
    "Umbwe Gate": (37.3000, -3.2167),
    "Lemosho Gate": (37.0500, -3.0333),
    "Rongai Gate": (37.5667, -2.9333),
    "Mweka Gate": (37.3500, -3.2333),

    # --- Marangu (south-east) ---------------------------------------------
    "Mandara Hut": (37.5136, -3.1997),
    "Horombo Hut": (37.4869, -3.1181),
    "Kibo Hut": (37.3950, -3.0700),

    # --- Machame / Lemosho southern circuit -------------------------------
    "Machame Camp": (37.2667, -3.1500),
    "Shira Camp": (37.2333, -3.1000),
    "Lava Tower": (37.3100, -3.0750),
    "Barranco Camp": (37.3372, -3.0958),
    "Karanga Camp": (37.3583, -3.1000),
    "Mweka Camp": (37.3500, -3.1667),

    # --- Lemosho / Shira plateau (west) -----------------------------------
    "Mti Mkubwa": (37.0833, -3.0333),
    "Shira 1 Camp": (37.1833, -3.0667),
    "Shira 2 Camp": (37.2167, -3.0833),

    # --- Rongai (north) ---------------------------------------------------
    "Simba Camp": (37.5333, -2.9667),
    "Kikelewa Camp": (37.4833, -3.0167),
    "Mawenzi Tarn": (37.4500, -3.1000),

    # --- Umbwe (south, steep) ---------------------------------------------
    "Umbwe Cave Camp": (37.3000, -3.1833),

    # --- Northern Circuit -------------------------------------------------
    "Moir Hut": (37.3167, -3.0333),
    "Buffalo Camp": (37.3667, -3.0000),
    "Third Cave": (37.4167, -3.0167),
    "School Hut": (37.3833, -3.0500),
}

# Positions taken from a published source rather than interpolated. Seeded with
# coords_verified already ticked, so the map does not flag them.
VERIFIED = {"Uhuru Peak", "Barafu Camp"}

# Mount Meru sits ~60 km west and will not fit in the box above. Its packages
# keep the altitude profile only; a Meru map would need its own projection.
MERU_STAGES = {
    "Momella Gate", "Miriakamba Hut", "Saddle Hut", "Socialist Peak",
}


# --- Labels for the map -------------------------------------------------------
# Placed clear of the shapes they name: Kibo above its cone, Mawenzi below its
# mass, Shira above the plateau. Checked against a render rather than guessed —
# a label sitting on top of the thing it names is worse than no label.
LANDMARKS = [
    ("Kibo", 37.3533, -3.0250),
    ("Mawenzi", 37.4550, -3.1480),
    ("Shira Plateau", 37.2100, -3.0100),
]

# Moshi is deliberately not labelled. It sits well south of the park boundary,
# so the label floated in empty space with nothing to attach to and read as a
# mistake rather than as orientation.
