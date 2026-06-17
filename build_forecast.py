#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_forecast.py - 16-Tage-Vorhersage fuer "Urlaubskompass".
Holt GEBUENDELT (alle Orte in 2 Anfragen -> minimal Rate-Limit):
  Luft: Tageshoch + Wettercode + max Wind   (api.open-meteo.com/forecast)
  Meer: Tagesmittel Wassertemperatur        (marine-api hourly -> Tagesmittel)
Schreibt forecast.json:  { id: { air:[{d,t,c,w}...], sea:[{d,t}...] } }

Cron (taeglich 12:00 Wien):
  0 12 * * *  TZ=Europe/Vienna python3 /root/build_forecast.py --out /var/www/html/meerwasser/forecast.json
"""
import json, sys, time, urllib.request, urllib.error

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
DAYS = 16

def fetch_json(url, tries=5):
    last=None
    for k in range(tries):
        try:
            req=urllib.request.Request(url, headers={'User-Agent':'urlaubskompass-forecast/1.0'})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            last=e
            if e.code==429: time.sleep(min(60,8*(2**k)))
            else: raise
        except Exception as e:
            last=e; time.sleep(5)
    raise last

def as_list(r): return r if isinstance(r,list) else [r]

def main():
    out=sys.argv[sys.argv.index('--out')+1] if '--out' in sys.argv else None
    lat=",".join(str(d[1]) for d in DEST); lon=",".join(str(d[2]) for d in DEST)
    res={d[0]:{'air':[], 'sea':[]} for d in DEST}

    air_url=("https://api.open-meteo.com/v1/forecast"
             f"?latitude={lat}&longitude={lon}"
             "&daily=temperature_2m_max,weathercode,windspeed_10m_max,precipitation_probability_max"
             f"&forecast_days={DAYS}&timezone=auto")
    sys.stderr.write("Luft-Vorhersage ..."); sys.stderr.flush()
    for d,r in zip(DEST, as_list(fetch_json(air_url))):
        dl=r.get('daily',{})
        t=dl.get('time',[]); tmax=dl.get('temperature_2m_max',[]); wc=dl.get('weathercode',[])
        wnd=dl.get('windspeed_10m_max',[]); pop=dl.get('precipitation_probability_max',[])
        out_air=[]
        for i,ds in enumerate(t):
            out_air.append({'d':ds,
                't': round(tmax[i]) if i<len(tmax) and tmax[i] is not None else None,
                'c': wc[i] if i<len(wc) else None,
                'w': round(wnd[i]) if i<len(wnd) and wnd[i] is not None else None,
                'p': pop[i] if i<len(pop) and pop[i] is not None else None})
        res[d[0]]['air']=out_air
    sys.stderr.write(" ok\n")
    time.sleep(2)

    sea_url=("https://marine-api.open-meteo.com/v1/marine"
             f"?latitude={lat}&longitude={lon}"
             "&hourly=sea_surface_temperature&cell_selection=sea"
             f"&forecast_days={DAYS}&timezone=auto")
    sys.stderr.write("Meer-Vorhersage ..."); sys.stderr.flush()
    for d,r in zip(DEST, as_list(fetch_json(sea_url))):
        h=r.get('hourly',{}); t=h.get('time',[]); sst=h.get('sea_surface_temperature',[])
        acc={}
        for i,ts in enumerate(t):
            v=sst[i] if i<len(sst) else None
            if v is None: continue
            day=ts[:10]; a=acc.get(day)
            if a is None: acc[day]=[v,1]
            else: a[0]+=v; a[1]+=1
        out_sea=[{'d':day,'t':round(tot/n,1)} for day,(tot,n) in sorted(acc.items())]
        res[d[0]]['sea']=out_sea
    sys.stderr.write(" ok\n")

    data=json.dumps(res, separators=(',',':'), ensure_ascii=False)
    if out:
        with open(out+'.tmp','w',encoding='utf-8') as f: f.write(data)
        import os; os.replace(out+'.tmp', out)
        sys.stderr.write(f"Geschrieben: {out} ({len(data)//1024} KB)\n")
    else:
        sys.stdout.write(data)

if __name__=='__main__':
    main()
