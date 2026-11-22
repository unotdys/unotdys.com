#!/usr/bin/env python3
"""Builds stores.json for the Downtown Palo Alto timeline map.
Edit STORES below, then run: python3 build_data.py
Geocodes addresses with OpenStreetMap Nominatim (cached in geocache.json).
approx=True means the open/close years are estimates and need checking."""
import json, os, time, urllib.parse, urllib.request

CUR = 2026  # "end": None means still open
STORES = [
  # name, address, start, end, category, approx, note
  ("Palo Alto Furniture Co.", "300 University Ave", 1900, 1923, "retail", True, "First big tenant of the corner building at University & Bryant, which opened in 1900."),
  ("J.C. Penney", "300 University Ave", 1924, 1972, "retail", True, "Penney's opened here in 1924 and was run for two decades by Merrill Vanderpool."),
  ("Walgreens (and Subway)", "300 University Ave", 1973, 2007, "retail", False, "Walgreens from 1973; the 1900 building burned in an arson fire in July 2007 and was demolished."),
  ("Varsity Theatre (original)", "263 University Ave", 1912, 1927, "entertainment", False, "Palo Alto's first Varsity, opened March 1912, showing stage shows and films."),
  ("Stanford Theatre", "221 University Ave", 1925, None, "entertainment", False, "Opened June 9, 1925. Restored by the Packard family (1987-89); still shows classic films."),
  ("Varsity Theatre", "456 University Ave", 1927, 1994, "entertainment", False, "Reid Brothers movie palace. Revival house and music venue in the 1970s."),
  ("Borders Books", "456 University Ave", 1995, 2011, "retail", True, "Bookstore in the converted Varsity Theatre; closed when Borders liquidated in 2011."),
  ("HanaHaus & Blue Bottle Coffee", "456 University Ave", 2015, 2024, "food", False, "Co-working cafe in the old Varsity; closure announced Sept 2024."),
  ("Liddicoat's Market", "340 University Ave", 1924, 1977, "food", True, "Grocery and lunch market; building dates to 1923-24."),
  ("Z Gallerie", "340 University Ave", 1980, 2010, "retail", True, "Home furnishings store in the old Liddicoat's building."),
  ("Apple Store (current)", "340 University Ave", 2012, None, "retail", False, "Opened Oct 27, 2012 as a prototype glass-front store."),
  ("Swain's Music", "451 University Ave", 1950, 2000, "retail", True, "Music store; locals say Jerry Garcia rented instruments here."),
  ("Apple Store (first)", "451 University Ave", 2001, 2012, "retail", False, "Opened Oct 2001, one of Apple's first stores and Steve Jobs's local store."),
  ("Shoe Palace", "451 University Ave", 2013, None, "retail", True, "Took over the original Apple Store space."),
  ("Chimaera Books & Music", "165 University Ave", 1980, 2000, "retail", True, "Ground-floor bookstore in the 'lucky building' until 2000."),
  ("Google (first office)", "165 University Ave", 1999, 1999, "tech", False, "Google's first real office, 1999, after Logitech. Later tenants: PayPal, Danger, Milo."),
  ("PayPal", "165 University Ave", 1999, 2000, "tech", True, "Early PayPal offices upstairs in the 'lucky building'."),
  ("Facebook (first office)", "471 Emerson St", 2004, 2005, "tech", True, "Facebook's first Palo Alto office."),
  ("Facebook", "156 University Ave", 2005, 2009, "tech", True, "Facebook's downtown HQ before moving to the Stanford Research Park."),
  ("Peninsula Creamery", "566 Emerson St", 1923, None, "food", False, "Diner and soda fountain since 1923."),
  ("Bell's Books", "536 Emerson St", 1935, None, "retail", False, "New and used bookstore, family-run since 1935."),
  ("University Art", "267 Hamilton Ave", 1964, 2017, "retail", True, "Art supply and framing store."),
  ("Palo Alto Sport Shop & Toy World", "526 Waverley St", 1930, 2015, "retail", True, "Sporting goods and toys from 1930."),
  ("Gotham Shop", "520 Ramona St", 1925, 1940, "retail", True, "First building of the Ramona Street architectural district (Pedro de Lemos, 1925)."),
  ("Cardinal Hotel", "235 Hamilton Ave", 1924, None, "hotel", True, "Palo Alto's first non-frame hotel."),
  ("Hotel President", "488 University Ave", 1929, None, "hotel", True, "1929 hotel, long used as apartments; reopened as a hotel (now Graduate by Hilton Palo Alto)."),
  ("Shady Lane", "441 University Ave", 1975, 2015, "retail", True, "Craft store, gallery and gift shop; moved to Menlo Park in 2015."),
  ("St. Michael's Alley", "436 University Ave", 1959, 1977, "food", True, "Early coffeehouse and folk venue; later moved."),
  ("Coupa Cafe", "538 Ramona St", 2004, None, "food", True, "Venezuelan cafe, a startup meeting spot."),
  ("Il Fornaio", "520 Cowper St", 1987, None, "food", True, "In the Garden Court Hotel."),
  ("Evvia Estiatorio", "420 Emerson St", 1995, None, "food", True, "Greek restaurant."),
  ("Pizza A Go-Go", "220 University Ave", 1988, 2007, "food", True, "Pizza by the slice, open late on weekends. Business records give 1988 as its start; it later moved to 335 University Ave."),
  ("Copeland's Sports", "375 University Ave", 1990, 2002, "retail", True, "Sporting goods store at University & Waverley, remembered open in the early 1990s. The Cheesecake Factory replaced it after a 2003 renovation."),
  ("The Cheesecake Factory", "375 University Ave", 2003, 2018, "food", False, "Opened in late 2003 in the former Copeland's building; closed May 26, 2018."),
  ("Roger's Deli", "Ramona St near University Ave", 1990, 1995, "food", True, "Deli on Ramona, around the corner from Peninsula Beauty Supply, remembered open in the early 1990s. Exact address and years unknown; pin placement approximate."),
  ("Stars Palo Alto", "265 Lytton Ave", 1995, 1997, "food", False, "Jeremiah Tower's Palo Alto branch of San Francisco's Stars, in the former Gatehouse restaurant building. Became Spago in late 1997."),
  ("Spago Palo Alto", "265 Lytton Ave", 1997, 2009, "food", True, "Wolfgang Puck's Spago took over the Stars space, opening Dec 15, 1997, and lasted about a dozen years."),
  ("Osteria Toscana", "247 Hamilton Ave", 1986, None, "food", False, "Tuscan restaurant on the ground floor of the Cardinal Hotel, at Hamilton & Ramona, since 1986."),
  ("Nobu Palo Alto", "180 Hamilton Ave", 2017, None, "food", True, "Nobu Matsuhisa's restaurant in the Epiphany Hotel."),
  ("Reach Fitness", "707 High St", None, None, "fitness", False, "Gym on High Street near Homer."),
  ("TAVERNA", "800 Emerson St", 2018, None, "food", False, "Greek restaurant at Emerson & Homer, across from Whole Foods, open since April 2018."),
  ("Gordon Biersch Brewery Restaurant", "640 Emerson St", 1988, 2016, "food", True, "Brewery-restaurant on Emerson; reinvented as Dan Gordon's in 2016."),
  ("Dan Gordon's", "640 Emerson St", 2016, 2022, "food", True, "Dan Gordon's reboot of the Gordon Biersch space; Meyhouse is there now."),
  ("Aquarius Theatre", "430 Emerson St", 1969, None, "entertainment", False, "Twin-screen arthouse cinema; opened Oct 1, 1969 with Medium Cool and The Rain People. Run by Landmark Theatres since 1985; renovated in 2015 with larger screens and recliners."),
  ("Palo Alto Post Office", "380 Hamilton Ave", 1932, None, "landmark", True, "Birge Clark's Spanish Colonial post office."),
  ("Palo Alto Depot", "95 University Ave", 1941, None, "landmark", True, "Streamline Moderne train station (Southern Pacific, now Caltrain)."),
]

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "geocache.json")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def geocode(addr):
    if addr in cache: return cache[addr]
    q = urllib.parse.urlencode({"q": f"{addr}, Palo Alto, CA 94301", "format": "json", "limit": 1})
    req = urllib.request.Request("https://nominatim.openstreetmap.org/search?" + q,
                                 headers={"User-Agent": "ofcourseduh-downtownpaloalto/1.0"})
    res = json.load(urllib.request.urlopen(req, timeout=20)); time.sleep(1.1)
    cache[addr] = [float(res[0]["lat"]), float(res[0]["lon"])] if res else None
    json.dump(cache, open(CACHE, "w"), indent=1)
    return cache[addr]

out, missing = [], []
for name, addr, s, e, cat, approx, note in STORES:
    ll = geocode(addr)
    if not ll: missing.append(addr); continue
    rec = {"name": name, "address": addr, "start": s if s else CUR, "end": e, "category": cat,
           "approx": approx, "note": note, "lat": ll[0], "lng": ll[1]}
    if not s: rec["start_unknown"] = True
    out.append(rec)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stores.json"), "w"), indent=1)
print(f"{len(out)} entries written; not geocoded: {missing}")

# ---------------------------------------------------------------------------
# Accepted public suggestions (written by /root/dpa-review/review.py after verification).
SUG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "suggestions_applied.json")
sug = json.load(open(SUG)) if os.path.exists(SUG) else {"additions": [], "corrections": []}
for a in sug.get("additions", []):
    ll = geocode(a["address"])
    if not ll: missing.append(a["address"]); continue
    rec = {"name": a["name"], "address": a["address"], "start": a.get("start") or CUR, "end": a.get("end"),
           "category": a.get("category", "retail"), "approx": bool(a.get("approx")), "note": a.get("note", ""),
           "lat": ll[0], "lng": ll[1], "source": "suggestion"}
    if not a.get("start"): rec["start_unknown"] = True
    out.append(rec)

# ---------------------------------------------------------------------------
# Current businesses from OpenStreetMap (osm_current.json, fetched via Overpass).
# OSM has no opening years, so these get start=CUR and start_unknown=True.
# Refresh: re-run the Overpass query in osm_query.txt, save as osm_current.json.
import math, re
OSM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "osm_current.json")
FOOD = {"restaurant","cafe","bar","pub","fast_food","ice_cream","bakery","pastry","chocolate","confectionery","tea","food_court","biergarten","coffee","deli","wine","alcohol"}
ENT = {"cinema","theatre","nightclub"}
HOTEL = {"hotel","motel","guest_house"}
FIT = {"fitness_centre","sports_centre","dance","climbing","yoga","pilates","fitness","boxing"}
SERV = {"bank","hairdresser","beauty","hairdresser;beauty","dry_cleaning","optician","massage","copyshop","laundry","tailor","mobile_phone","pharmacy","chemist","glaziery","travel_agency"}
SKIP_NAMES = {"Stanford Theater": "Stanford Theatre", "Palo Alto Creamery": "Peninsula Creamery",
              "Graduate by Hilton Palo Alto": "Hotel President", "Apple Store": "Apple Store (current)"}
ABBR = [(" Avenue"," Ave"),(" Street"," St"),(" Road"," Rd")]

def norm(t): return re.sub(r"[^a-z0-9]", "", t.lower())
def short(a):
    for x, y in ABBR: a = a.replace(x, y)
    return a

def reverse(lat, lon):
    key = f"rev:{lat:.5f},{lon:.5f}"
    if key in cache: return cache[key]
    q = urllib.parse.urlencode({"lat": lat, "lon": lon, "format": "json", "zoom": 18})
    req = urllib.request.Request("https://nominatim.openstreetmap.org/reverse?" + q, headers={"User-Agent": "ofcourseduh-downtownpaloalto/1.0"})
    r = json.load(urllib.request.urlopen(req, timeout=20)); time.sleep(1.1)
    a = r.get("address", {}); val = short(f"{a.get('house_number','')} {a.get('road','')}".strip()) or "Downtown Palo Alto"
    if not a.get("house_number"): val = "near " + val
    cache[key] = val; json.dump(cache, open(CACHE, "w"), indent=1)
    return val

if os.path.exists(OSM):
    K = math.cos(math.radians(37.446)); A = (37.44330, -122.16419); W = (37.44952, -122.15802)
    def xy(la, ln): return ((ln - A[1]) * K * 111320, (la - A[0]) * 111320)
    wx, wy = xy(*W); L = math.hypot(wx, wy); ux, uy = wx / L, wy / L
    open_now = [s for s in out if s["end"] is None]
    added, merged, seen = 0, 0, []
    for e in json.load(open(OSM))["elements"]:
        t = e.get("tags", {}); name = t.get("name")
        la = e.get("lat") or e.get("center", {}).get("lat"); ln = e.get("lon") or e.get("center", {}).get("lon")
        if not name or la is None: continue
        x, y = xy(la, ln); along = x * ux + y * uy; perp = -x * uy + y * ux
        if not (-80 <= along <= L + 200 and -420 <= perp <= 270): continue   # downtown: Alma..Middlefield; Lytton side ~2 blocks, south through Homer (Whole Foods)
        if name in SKIP_NAMES: merged += 1; continue
        hn, st = t.get("addr:housenumber", "").split(";")[0], t.get("addr:street", "")
        addr = short(f"{hn} {st}".strip()) if hn and st else reverse(la, ln)
        # same place already in the hand-made list (open today, same address and a shared word)?
        words = {w for w in re.findall(r"[a-z]{4,}", name.lower())}
        if any(norm(s["address"]) == norm(addr) and words & set(re.findall(r"[a-z]{4,}", s["name"].lower())) for s in open_now):
            merged += 1; continue
        # exact same name as an open hand-made entry within ~150 m
        if any(norm(s["name"]) == norm(name) and math.hypot(*(a - b for a, b in zip(xy(s["lat"], s["lng"]), (x, y)))) < 150 for s in open_now):
            merged += 1; continue
        # same name within 40 m in OSM itself (duplicate mapping)
        if any(n == norm(name) and math.hypot(px - x, py - y) < 40 for n, px, py in seen): continue
        seen.append((norm(name), x, y))
        kind = t.get("amenity") or t.get("tourism") or t.get("leisure") or t.get("shop") or (t.get("sport","").split(";")[0] if t.get("sport") else "")
        cat = "fitness" if kind in FIT else "food" if kind in FOOD else "entertainment" if kind in ENT else "hotel" if kind in HOTEL else "services" if kind in SERV else "retail"
        label = kind.replace("_", " ").replace(";", ", ")
        out.append({"name": name, "address": addr, "start": CUR, "end": None, "category": cat, "approx": False,
                    "start_unknown": True, "source": "osm",
                    "note": f"Open today ({label}). Listed in OpenStreetMap; the year it opened isn't known yet.",
                    "lat": la, "lng": ln})
        added += 1
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stores.json"), "w"), indent=1)
    print(f"OpenStreetMap: {added} current places added, {merged} merged with existing entries; total {len(out)}")

# ---------------------------------------------------------------------------
# Historical sources (built by /root/dpa-history): city directories + phone books 1904-1963,
# and OpenStreetMap history 2013-2025. All approximate; curated entries win.
HS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history_sources.json")
if os.path.exists(HS):
    hs = json.load(open(HS))
    K2 = math.cos(math.radians(37.446)); A2 = (37.44330, -122.16419); W2 = (37.44952, -122.15802)
    def fxy(la, ln): return ((ln - A2[1]) * K2 * 111320, (la - A2[0]) * 111320)
    wx2, wy2 = fxy(*W2); L2 = math.hypot(wx2, wy2); ux2, uy2 = wx2 / L2, wy2 / L2
    def in_area(la, ln):
        x, y = fxy(la, ln); along = x * ux2 + y * uy2; perp = -x * uy2 + y * ux2
        return -80 <= along <= L2 + 200 and -420 <= perp <= 270
    def wset(n): return set(re.findall(r"[a-z]{4,}", n.lower()))
    curated = [x for x in out if x.get("source") not in ("osm",)]
    added_dir = skipped_dir = 0
    for e in hs.get("directory", []):
        ll = geocode(e["address"])
        if not ll or not in_area(*ll): skipped_dir += 1; continue
        if any(norm(c["address"]) == norm(e["address"]) and (wset(c["name"]) & wset(e["name"]) or norm(c["name"]) == norm(e["name"]))
               and c["start"] <= e["end"] + 3 and (c["end"] or CUR) >= e["start"] - 3 for c in curated):
            skipped_dir += 1; continue
        out.append(dict(e, lat=ll[0], lng=ll[1])); added_dir += 1
    # first year each current OpenStreetMap place was mapped (2013+)
    since = []
    for k, y in hs.get("osm_since", {}).items():
        nm, ll = k.rsplit("|", 1); la, ln = map(float, ll.split(","))
        since.append((norm(nm), la, ln, y))
    dated = 0
    for x in out:
        if x.get("source") == "osm" and x.get("start_unknown"):
            hits = [y for n, la, ln, y in since if n == norm(x["name"]) and abs(la - x["lat"]) < 0.0004 and abs(ln - x["lng"]) < 0.0004]
            if hits and min(hits) > 2013:   # first mapped after OSM coverage was good: a fair opening estimate
                x["start"] = min(hits); x["approx"] = True; x.pop("start_unknown", None); dated += 1
                x["note"] = x["note"].replace("the year it opened isn't known yet.", f"first mapped in {min(hits)}, which is roughly when it opened.")
            elif hits:                      # already mapped in the earliest snapshot: open since 2013 at the latest
                x["start"] = 2013; x["approx"] = True; x.pop("start_unknown", None); dated += 1
                x["note"] = x["note"].replace("the year it opened isn't known yet.", "on the map since at least 2013; it may be much older.")
    closed = 0
    for e in hs.get("osm_closed", []):
        if not in_area(e["lat"], e["lng"]): continue
        if any(norm(x["name"]) == norm(e["name"]) and abs(x["lat"] - e["lat"]) < 0.0004 and abs(x["lng"] - e["lng"]) < 0.0004 for x in out): continue
        k = e.pop("kind", ""); cat = "fitness" if k in FIT else "food" if k in FOOD else "entertainment" if k in ENT else "hotel" if k in HOTEL else "services" if k in SERV else "retail"
        out.append(dict(e, category=cat)); closed += 1
    print(f"History: {added_dir} directory entries added ({skipped_dir} outside the area or already curated), {dated} OSM places dated, {closed} closed OSM places added")

# ---------------------------------------------------------------------------
# Accepted corrections to existing entries (match by name, and address if given).
fixed = 0
for c in sug.get("corrections", []):
    hits = [x for x in out if x["name"].lower() == c["target"].lower() and (not c.get("target_address") or x["address"] == c["target_address"])]
    for x in hits:
        for k in ("name", "start", "end", "category", "note", "approx"):
            if k in c.get("fields", {}): x[k] = c["fields"][k]
        if "start" in c.get("fields", {}) and c["fields"]["start"]: x.pop("start_unknown", None)
        if c.get("fields", {}).get("address") and c["fields"]["address"] != x["address"]:
            ll = geocode(c["fields"]["address"])
            if ll: x["address"], x["lat"], x["lng"] = c["fields"]["address"], ll[0], ll[1]
        fixed += 1
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stores.json"), "w"), indent=1)
print(f"Suggestions: {len(sug.get('additions', []))} additions, {fixed} corrections applied; total {len(out)}")
