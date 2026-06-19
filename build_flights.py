#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_flights.py - erzeugt flights.json (Direktflug-Bitketten je Flughafen).
Zieht airports.dat + routes.dat FRISCH von OpenFlights und berechnet, ob es vom
jeweiligen Abflughafen einen Direktflug (stops=0) zu einem Flughafen <=70km vom
Ziel gibt. Bitkette je Origin, ausgerichtet an der DEST-Reihenfolge (== App).
Fail-safe: schreibt nur bei plausiblen Daten; sonst bleibt die alte Datei.
Aufruf: python3 build_flights.py --out /var/www/html/meerwasser/flights.json
"""
import csv, io, json, math, os, sys, urllib.request
from collections import defaultdict

DEST = [
    ('palma',39.569,2.65),
    ('ibiza',38.909,1.432),
    ('barcelona',41.369,2.19),
    ('malaga',36.715,-4.42),
    ('marbella',36.488,-4.882),
    ('alicante',38.335,-0.481),
    ('lloret',41.695,2.848),
    ('tenerife',28.041,-16.741),
    ('grancanaria',27.741,-15.586),
    ('fuerteventura',28.359,-14.053),
    ('lanzarote',28.963,-13.548),
    ('albufeira',37.084,-8.25),
    ('lagos',37.092,-8.673),
    ('cascais',38.697,-9.421),
    ('funchal',32.64,-16.916),
    ('nizza',43.69,7.271),
    ('cannes',43.547,7.017),
    ('sttropez',43.27,6.638),
    ('biarritz',43.481,-1.559),
    ('ajaccio',41.918,8.738),
    ('marseille',43.291,5.37),
    ('positano',40.628,14.485),
    ('sorrent',40.626,14.375),
    ('cagliari',39.215,9.11),
    ('palermo',38.12,13.36),
    ('taormina',37.851,15.293),
    ('rimini',44.06,12.57),
    ('venedig',45.413,12.366),
    ('cinqueterre',44.128,9.71),
    ('capri',40.551,14.243),
    ('santorin',36.393,25.461),
    ('mykonos',37.452,25.328),
    ('kreta',35.339,25.133),
    ('rhodos',36.434,28.218),
    ('korfu',39.62,19.92),
    ('zakynthos',37.788,20.899),
    ('kos',36.893,27.288),
    ('dubrovnik',42.641,18.108),
    ('split',43.508,16.44),
    ('hvar',43.172,16.443),
    ('zadar',44.119,15.231),
    ('antalya',36.862,30.713),
    ('bodrum',37.034,27.43),
    ('side',36.767,31.389),
    ('ayianapa',34.988,34.0),
    ('paphos',34.752,32.411),
    ('sliema',35.912,14.504),
    ('budva',42.286,18.84),
    ('brighton',50.821,-0.137),
    ('sylt',54.908,8.313),
    ('menorca',39.889,4.265),
    ('formentera',38.7,1.43),
    ('salou',41.076,1.139),
    ('valencia',39.464,-0.33),
    ('denia',38.84,0.106),
    ('almeria',36.834,-2.464),
    ('cadiz',36.529,-6.292),
    ('tarifa',36.013,-5.604),
    ('sansebastian',43.321,-1.985),
    ('sitges',41.235,1.811),
    ('portosanto',33.066,-16.339),
    ('ericeira',38.963,-9.417),
    ('pontadelgada',37.741,-25.668),
    ('nazare',39.601,-9.07),
    ('stjeandeluz',43.388,-1.659),
    ('lagrandemotte',43.56,4.087),
    ('hyeres',43.116,6.132),
    ('menton',43.775,7.503),
    ('calvi',42.567,8.757),
    ('arcachon',44.658,-1.168),
    ('tropea',38.677,15.897),
    ('otranto',40.146,18.491),
    ('gallipoli',40.055,17.992),
    ('vieste',41.882,16.179),
    ('elba',42.792,10.193),
    ('fortedeimarmi',43.959,10.166),
    ('portofino',44.303,9.21),
    ('ischia',40.731,13.951),
    ('procida',40.761,14.018),
    ('jesolo',45.505,12.633),
    ('alghero',40.56,8.319),
    ('cefalu',38.039,14.023),
    ('lampedusa',35.508,12.592),
    ('naxos',37.106,25.377),
    ('paros',37.084,25.152),
    ('milos',36.689,24.418),
    ('kefalonia',38.175,20.489),
    ('lefkada',38.711,20.64),
    ('skiathos',39.163,23.49),
    ('halkidiki',40.3,23.3),
    ('chania',35.512,24.018),
    ('parga',39.284,20.401),
    ('thassos',40.69,24.65),
    ('samos',37.754,26.977),
    ('athen',37.847,23.758),
    ('rovinj',45.081,13.638),
    ('pula',44.867,13.85),
    ('opatija',45.339,14.305),
    ('makarska',43.297,17.017),
    ('brac',43.262,16.654),
    ('korcula',42.961,17.136),
    ('fethiye',36.622,29.116),
    ('marmaris',36.855,28.274),
    ('kusadasi',37.86,27.259),
    ('cesme',38.324,26.304),
    ('alanya',36.544,31.999),
    ('kas',36.201,29.64),
    ('limassol',34.684,33.038),
    ('protaras',35.012,34.058),
    ('gozo',36.044,14.241),
    ('kotor',42.424,18.771),
    ('sarande',39.875,20.005),
    ('ksamil',39.767,20.001),
    ('durres',41.323,19.446),
    ('piran',45.528,13.568),
    ('sunnybeach',42.694,27.712),
    ('varna',43.204,27.91),
    ('mamaia',44.252,28.621),
    ('ruegen',54.401,13.43),
    ('usedom',53.962,14.072),
    ('timmendorf',54.001,10.78),
    ('stpeterording',54.305,8.638),
    ('norderney',53.707,7.152),
    ('zandvoort',52.371,4.532),
    ('newquay',50.415,-5.092),
    ('hurghada',27.18,33.84),
    ('sharm',27.915,34.33),
    ('marsaalam',25.069,34.89),
    ('dahab',28.501,34.513),
    ('elgouna',27.398,33.678),
    ('djerba',33.807,10.845),
    ('hammamet',36.4,10.612),
    ('sousse',35.825,10.636),
    ('monastir',35.764,10.811),
    ('agadir',30.421,-9.598),
    ('essaouira',31.512,-9.77),
    ('tanger',35.768,-5.8),
    ('telaviv',32.084,34.781),
    ('eilat',29.557,34.952),
    ('aqaba',29.527,35.004),
    ('beirut',33.888,35.495),
    ('dubai',25.204,55.27),
    ('abudhabi',24.453,54.397),
    ('rasalkhaimah',25.789,55.943),
    ('sal',16.752,-22.949),
    ('boavista',16.08,-22.81),
    ('muscat',23.588,58.408),
    ('salalah',17.038,54.091),
    ('banjul',13.338,-16.652),
]

ORIGINS = [
    ('GRZ',['GRZ']),
    ('INN',['INN']),
    ('KLU',['KLU']),
    ('LNZ',['LNZ']),
    ('SZG',['SZG']),
    ('VIE',['VIE']),
    ('BER',['TXL', 'SXF', 'BER']),
    ('BRE',['BRE']),
    ('DTM',['DTM']),
    ('DRS',['DRS']),
    ('DUS',['DUS']),
    ('FRA',['FRA']),
    ('FDH',['FDH']),
    ('HAM',['HAM']),
    ('HAJ',['HAJ']),
    ('FKB',['FKB']),
    ('CGN',['CGN']),
    ('LEJ',['LEJ']),
    ('FMM',['FMM']),
    ('MUC',['MUC']),
    ('FMO',['FMO']),
    ('NUE',['NUE']),
    ('PAD',['PAD']),
    ('SCN',['SCN']),
    ('STR',['STR']),
    ('BSL',['BSL', 'MLH', 'EAP']),
    ('GVA',['GVA']),
    ('ZRH',['ZRH']),
]

AIRPORTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
ROUTES_URL   = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "seazons-flights"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")

def hav(a, b, c, d):
    R = 6371.0
    p1, p2 = math.radians(a), math.radians(c)
    dp = math.radians(c - a); dl = math.radians(d - b)
    return 2 * R * math.asin(math.sqrt(math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2))

def main():
    out = sys.argv[sys.argv.index("--out")+1] if "--out" in sys.argv else None
    try:
        ap_txt = fetch(AIRPORTS_URL)
        rt_txt = fetch(ROUTES_URL)
    except Exception as e:
        sys.stderr.write("FEHLER beim Laden von OpenFlights: %s. Alte Datei bleibt.\n" % e)
        sys.exit(1)
    ap = {}
    for row in csv.reader(io.StringIO(ap_txt)):
        if len(row) >= 8 and len(row[4]) == 3:
            try: ap[row[4]] = (float(row[6]), float(row[7]))
            except Exception: pass
    routes = defaultdict(set); nr = 0
    for row in csv.reader(io.StringIO(rt_txt)):
        if len(row) >= 8 and row[7] == "0":
            routes[row[2]].add(row[4]); nr += 1
    if len(ap) < 5000 or nr < 50000:
        sys.stderr.write("Unplausible Daten (airports=%d, routes0=%d). Abbruch.\n" % (len(ap), nr))
        sys.exit(1)
    DA = {}
    for did, lat, lon in DEST:
        DA[did] = [code for code, (a, o) in ap.items() if hav(lat, lon, a, o) <= 70]
    flights = {}
    for key, srcs in ORIGINS:
        flights[key] = "".join(
            "1" if any(a in routes[s] for s in srcs for a in DA[did]) else "0"
            for did, lat, lon in DEST)
    if out:
        tmp = out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(flights, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, out)
        sys.stderr.write("FERTIG: %s (%d B, %d Origins, %d Ziele)\n" % (out, os.path.getsize(out), len(flights), len(DEST)))
    else:
        sys.stdout.write(json.dumps(flights, ensure_ascii=False, separators=(",", ":")))

if __name__ == "__main__":
    main()
