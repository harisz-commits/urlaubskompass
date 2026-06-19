#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_climate.py  -  erzeugt/ergaenzt climate.json fuer "Meerwasser Europa".

Holt die Historie von Open-Meteo PRO ORT (gratis-schonend: wenige Jahre) und
ist FORTSETZBAR: speichert nach jedem Ort und ueberspringt beim naechsten Start
bereits fertige Ziele. Bei anhaltendem 429 (Limit) wird sauber gespeichert und
beendet -> einfach spaeter nochmal starten, dann macht es weiter.

Je Ziel, als MONATSwerte (12) und TAGESwerte (365, +-3 Tage):
  sea : [min, avg, max]                      (Tagesmittel Meerwasser)
  air : [min, avg, max, avgTief, avgHoch]    (Luft)
  sun : Stunden Sonne / Tag
  rain: [mm/Tag, Anteil Regentage 0..1]
  sr/ss (nur Tage): mittlerer Sonnenauf-/-untergang in Minuten lokal

Aufruf auf dem Server (mehrfach moeglich):
    python3 build_climate.py --out /var/www/html/meerwasser/climate.json
"""
import json, os, sys, time, urllib.request, urllib.error

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

AIR_START, AIR_END = '2022-01-01', '2024-12-31'   # Luft 3 Jahre
SEA_START, SEA_END = '2023-01-01', '2024-12-31'   # Meer 2 Jahre
DAY_WINDOW = 3

MONTH_LEN = [31,28,31,30,31,30,31,31,30,31,30,31]
MONTH_OFF = []
_s = 0
for _n in MONTH_LEN:
    MONTH_OFF.append(_s); _s += _n
NDAYS = 365

def slot_of(month, day):
    if month == 2 and day == 29: day = 28
    if day > MONTH_LEN[month-1]: day = MONTH_LEN[month-1]
    return MONTH_OFF[month-1] + (day-1)

def r1(x): return round(x + 0.0, 1)

class RateLimited(Exception): pass

def fetch_json(url, tries=4):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'meerwasser-climate/3.0'})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 429:
                wait = min(60, 8 * (2 ** k))
                sys.stderr.write(f" (429, warte {wait}s) "); sys.stderr.flush(); time.sleep(wait)
            else:
                raise
        except Exception as e:                       # noqa
            last = e
            sys.stderr.write(f" (Fehler: {e}, retry) "); sys.stderr.flush(); time.sleep(5)
    raise RateLimited(str(last))

def hhmm_to_min(s):
    try:
        return int(s[11:13]) * 60 + int(s[14:16])
    except Exception:
        return None

# ---------- Statistik ----------
def sea_stat(v):
    v = [x for x in v if x is not None]
    return [r1(min(v)), r1(sum(v)/len(v)), r1(max(v))] if v else None
def air_stat(mn, mx, me):
    mn=[x for x in mn if x is not None]; mx=[x for x in mx if x is not None]; me=[x for x in me if x is not None]
    if not me: return None
    return [r1(min(mn)), r1(sum(me)/len(me)), r1(max(mx)), r1(sum(mn)/len(mn)), r1(sum(mx)/len(mx))]
def sun_stat(v):
    v=[x for x in v if x is not None]; return r1(sum(v)/len(v)) if v else None
def rain_stat(v):
    v=[x for x in v if x is not None]
    if not v: return None
    return [r1(sum(v)/len(v)), round(sum(1 for x in v if x>=1.0)/len(v), 2)]
def avg_min(v):
    v=[x for x in v if x is not None]; return int(round(sum(v)/len(v))) if v else None

def new_buckets():
    return {k:[[] for _ in range(NDAYS)] for k in ('sea','amin','amax','amean','sun','rain','sr','ss')}

def add_air(b, daily):
    t=daily.get('time',[]); mn=daily.get('temperature_2m_min',[]); mx=daily.get('temperature_2m_max',[])
    me=daily.get('temperature_2m_mean',[]); sd=daily.get('sunshine_duration',[]); pr=daily.get('precipitation_sum',[])
    srise=daily.get('sunrise',[]); sset=daily.get('sunset',[])
    for i,ds in enumerate(t):
        s=slot_of(int(ds[5:7]), int(ds[8:10]))
        if i<len(mn) and mn[i] is not None: b['amin'][s].append(mn[i])
        if i<len(mx) and mx[i] is not None: b['amax'][s].append(mx[i])
        if i<len(me) and me[i] is not None: b['amean'][s].append(me[i])
        if i<len(sd) and sd[i] is not None: b['sun'][s].append(sd[i]/3600.0)
        if i<len(pr) and pr[i] is not None: b['rain'][s].append(pr[i])
        if i<len(srise) and srise[i]:
            m=hhmm_to_min(srise[i])
            if m is not None: b['sr'][s].append(m)
        if i<len(sset) and sset[i]:
            m=hhmm_to_min(sset[i])
            if m is not None: b['ss'][s].append(m)

def add_sea(b, hourly):
    t=hourly.get('time',[]); sst=hourly.get('sea_surface_temperature',[])
    acc={}
    for i,ts in enumerate(t):
        v=sst[i] if i<len(sst) else None
        if v is None: continue
        d=ts[:10]; a=acc.get(d)
        if a is None: acc[d]=[v,1]
        else: a[0]+=v; a[1]+=1
    for d,(tot,n) in acc.items():
        b['sea'][slot_of(int(d[5:7]), int(d[8:10]))].append(tot/n)

def finalize(b):
    def g(arr, idxs):
        out=[]
        for j in idxs: out+=arr[j]
        return out
    sea_d=[];air_d=[];sun_d=[];rain_d=[];sr_d=[];ss_d=[]
    for s in range(NDAYS):
        idx=[(s+k)%NDAYS for k in range(-DAY_WINDOW,DAY_WINDOW+1)]
        sea_d.append(sea_stat(g(b['sea'],idx)))
        air_d.append(air_stat(g(b['amin'],idx),g(b['amax'],idx),g(b['amean'],idx)))
        sun_d.append(sun_stat(g(b['sun'],idx)))
        rain_d.append(rain_stat(g(b['rain'],idx)))
        sr_d.append(avg_min(g(b['sr'],idx)))
        ss_d.append(avg_min(g(b['ss'],idx)))
    sea_m=[];air_m=[];sun_m=[];rain_m=[]
    for mo in range(12):
        idx=list(range(MONTH_OFF[mo], MONTH_OFF[mo]+MONTH_LEN[mo]))
        sea_m.append(sea_stat(g(b['sea'],idx)))
        air_m.append(air_stat(g(b['amin'],idx),g(b['amax'],idx),g(b['amean'],idx)))
        sun_m.append(sun_stat(g(b['sun'],idx)))
        rain_m.append(rain_stat(g(b['rain'],idx)))
    return {'sea':{'m':sea_m,'d':sea_d},'air':{'m':air_m,'d':air_d},
            'sun':{'m':sun_m,'d':sun_d},'rain':{'m':rain_m,'d':rain_d},'sr':sr_d,'ss':ss_d}

def build_one(lat, lon):
    b=new_buckets()
    air=("https://archive-api.open-meteo.com/v1/archive"
         f"?latitude={lat}&longitude={lon}&start_date={AIR_START}&end_date={AIR_END}"
         "&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,sunshine_duration,precipitation_sum,sunrise,sunset"
         "&timezone=auto")
    add_air(b, fetch_json(air).get('daily',{}))
    sea=("https://marine-api.open-meteo.com/v1/marine"
         f"?latitude={lat}&longitude={lon}&start_date={SEA_START}&end_date={SEA_END}"
         "&hourly=sea_surface_temperature&cell_selection=sea&timezone=auto")
    add_sea(b, fetch_json(sea).get('hourly',{}))
    return finalize(b)

def save(path, data):
    tmp=path+'.tmp'
    with open(tmp,'w',encoding='utf-8') as f:
        json.dump(data, f, separators=(',',':'), ensure_ascii=False)
    os.replace(tmp, path)

def main():
    argv=sys.argv
    out=argv[argv.index('--out')+1] if '--out' in argv else None
    refresh=None
    if '--refresh' in argv:
        try: refresh=int(argv[argv.index('--refresh')+1])
        except Exception: refresh=40
    result={}
    if out and os.path.exists(out):
        try: result=json.load(open(out,encoding='utf-8'))
        except Exception: result={}
    n=len(DEST)
    if refresh is not None:
        # Rollierender Refresh: neue/unfertige Ziele zuerst, dann die am laengsten
        # nicht aktualisierten (_ts aufsteigend). Pro Lauf maximal `refresh` Ziele,
        # damit das Tageslimit nicht gesprengt wird.
        def fertig(d): 
            v=result.get(d[0]); return isinstance(v,dict) and 'sun' in v
        missing=[d for d in DEST if not fertig(d)]
        present=[d for d in DEST if fertig(d)]
        present.sort(key=lambda d: result[d[0]].get('_ts',0))
        targets=(missing+present)[:max(refresh,len(missing))]
        sys.stderr.write(f"Refresh-Modus: {len(targets)} Ziele (neu/unfertig: {len(missing)}).\n")
    else:
        done={k for k,v in result.items() if isinstance(v,dict) and 'sun' in v}   # v2-fertig
        targets=[d for d in DEST if d[0] not in done]
        sys.stderr.write(f"Bereits fertig: {len(done)} / {n}.  Zu holen: {len(targets)}.\n")
    for i,(id_,lat,lon) in enumerate(targets,1):
        sys.stderr.write(f"[{i:2d}/{len(targets)}] {id_} ..."); sys.stderr.flush()
        try:
            data1=build_one(lat,lon)
        except RateLimited:
            sys.stderr.write("\n\nLIMIT erreicht. Fortschritt gespeichert.\n"
                             "Bitte SPAETER nochmal starten (macht dort weiter).\n")
            if out: save(out, result)
            sys.exit(0)
        data1['_ts']=int(time.time())
        result[id_]=data1
        if out: save(out, result)     # nach jedem Ort sichern
        sys.stderr.write(" ok\n")
        time.sleep(3)
    data=json.dumps(result, separators=(',',':'), ensure_ascii=False)
    if out:
        save(out, result)
        sys.stderr.write(f"\nFERTIG. Geschrieben: {out}  ({len(data)//1024} KB, {len(result)} Ziele)\n")
    else:
        sys.stdout.write(data)

if __name__ == '__main__':
    main()
