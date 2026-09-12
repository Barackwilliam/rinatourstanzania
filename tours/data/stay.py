"""
The operator's own accommodation and their transfer prices, as supplied.

Everything here came from the client directly. Two things are worth flagging
rather than guessing at:

  * The airport transfer was written as "$ to 70 dollar per trip". That reads
    as either a flat 70 or a range with the lower figure missing, so it is
    entered as a flat 70 and should be confirmed.
  * "9 to 15 minutes" for 13 km is the client's own figure and is kept as
    written rather than rounded to something that sounds more plausible.
"""

ACCOMMODATION = {
    "name": "Our guest house",
    "slug": "guest-house",
    "tagline": "Green, quiet, and in sight of both mountains.",
    "location": "Near Kilimanjaro International Airport",
    "price_from": 60,
    "currency": "USD",
    "board_basis": "Bed & breakfast",
    "description": (
        "We keep our own guest house so travellers arriving late or leaving early "
        "have somewhere settled to be, thirteen kilometres from Kilimanjaro "
        "International Airport.\n\n"
        "The grounds are kept green and the mature trees left standing, which is "
        "what brings the birds. On a clear morning you can see Kilimanjaro and "
        "Meru from the same spot.\n\n"
        "The kitchen is open to guests. Cook for yourself if you would rather, or "
        "make coffee and tea whenever you want it."
    ),
    "features": [
        ("Both mountains in view",
         "Kilimanjaro and Meru are visible from the grounds on a clear day."),
        ("Thirteen kilometres from the airport",
         "Nine to fifteen minutes by road, transfer arranged by us."),
        ("Kitchen open to guests",
         "Cook for yourself if you prefer. There is no charge for using it."),
        ("Coffee and tea",
         "USD 3 per cup, made in the guest kitchen."),
        ("Kept green",
         "Mature trees left standing rather than cleared."),
        ("Birdlife",
         "The trees and quiet bring a wide range of birds into the grounds."),
    ],
}

TRANSFERS = [
    {
        "name": "Kilimanjaro Airport transfer",
        "slug": "kilimanjaro-airport-transfer",
        "route_from": "Kilimanjaro International Airport",
        "route_to": "our guest house",
        "distance_km": 13,
        "duration_text": "9-15 minutes",
        "price_from": 70, "price_basis": "trip",
        "description": "Met at arrivals and driven straight to the guest house. "
                       "Booked both ways for departures.",
        "icon": "plane",
    },
    {
        "name": "Taxi to Moshi",
        "slug": "taxi-to-moshi",
        "route_from": "Guest house", "route_to": "Moshi town",
        "price_from": 70, "price_basis": "trip",
        "description": "A town run into Moshi and back.",
        "icon": "car",
    },
    {
        "name": "Taxi to Arusha",
        "slug": "taxi-to-arusha",
        "route_from": "Guest house", "route_to": "Arusha",
        "price_from": 75, "price_basis": "trip",
        "description": "A town run into Arusha and back.",
        "icon": "car",
    },
    {
        "name": "Taxi for the day",
        "slug": "taxi-for-the-day",
        "route_from": "", "route_to": "Wherever you need to go",
        "duration_text": "Morning to evening",
        "price_from": 120, "price_to": 180, "price_basis": "day",
        "description": "A car and driver for the whole day. The price depends on "
                       "the distance covered and where you go.",
        "icon": "clock",
    },
]
