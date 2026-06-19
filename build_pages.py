#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_pages.py - erzeugt SEO-/KI-optimierte Laenderseiten aus den vorhandenen
Datendateien (climate.json, flights.json) + seazons_meta.json.

Aufruf:
  python3 build_pages.py --meta /root/seazons_meta.json \
      --data /var/www/html/meerwasser --out /var/www/html/meerwasser --only vae

  --only <slug>   nur ein Land erzeugen (z.B. vae). Ohne --only: alle Laender.
Ausgabe: <out>/land/<slug>.html
"""
import json, os, sys, math, html, datetime

STAY22_AID = "seazonsde"
GYG_PARTNER = "WQAOT0I"
SHOW_ORIGINS = ["VIE", "MUC", "ZRH"]

MONTHS_DE = ["Januar","Februar","M\u00e4rz","April","Mai","Juni","Juli","August",
             "September","Oktober","November","Dezember"]
DIM = [31,28,31,30,31,30,31,31,30,31,30,31]

COUNTRY_EN = {
  "VAE":"United Arab Emirates","\u00c4gypten":"Egypt","Tunesien":"Tunisia",
  "Marokko":"Morocco","Israel":"Israel","Jordanien":"Jordan","Libanon":"Lebanon",
  "Kap Verde":"Cape Verde","Oman":"Oman","Gambia":"Gambia","Spanien":"Spain",
  "Portugal":"Portugal","Frankreich":"France","Italien":"Italy","Griechenland":"Greece",
  "Kroatien":"Croatia","T\u00fcrkei":"Turkey","Zypern":"Cyprus","Malta":"Malta",
  "Montenegro":"Montenegro","Albanien":"Albania","Slowenien":"Slovenia",
  "Bulgarien":"Bulgaria","Rum\u00e4nien":"Romania","Deutschland":"Germany",
  "Niederlande":"Netherlands","England":"United Kingdom",
}
# Schoene Formulierung fuer die H1/Lead ("Baden in ...")
COUNTRY_PHRASE = {
  "VAE":"den Vereinigten Arabischen Emiraten (VAE)",
  "\u00c4gypten":"\u00c4gypten", "Tunesien":"Tunesien", "Marokko":"Marokko",
}

CSS = """
:root{--deep:#04141d;--deep2:#06202c;--panel:#0a2733;--panel2:#0e3242;--line:rgba(178,224,224,.14);--foam:#e9f4f3;--mist:#8aa9b2;--mist-dim:#5d7e88;--focus:#6fe0d4;--tmin:#5aa6e0;--tmax:#ee8a3a;--maxw:820px}
*{box-sizing:border-box}html{background:var(--deep2)}html,body{margin:0}
body{background:linear-gradient(180deg,var(--deep),var(--deep2));color:var(--foam);font-family:"Space Grotesk",system-ui,-apple-system,Segoe UI,Roboto,sans-serif;min-height:100vh;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:var(--maxw);margin:0 auto;padding:24px 20px calc(64px + env(safe-area-inset-bottom,0px))}
a{color:var(--focus)}
.top{display:flex;align-items:center;gap:10px;padding:4px 0 18px}
.top .glyph{font-size:20px}.top b{font-size:17px}.top .back{margin-left:auto;font-size:13.5px}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:11.5px;letter-spacing:.28em;text-transform:uppercase;color:var(--mist-dim)}
h1{font-size:clamp(26px,5vw,38px);line-height:1.07;margin:8px 0 10px;letter-spacing:-.5px}
.lead{font-size:16.5px;color:#dcebed;background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--focus);border-radius:12px;padding:14px 16px;margin:8px 0 22px}
h2{font-size:21px;margin:34px 0 8px;letter-spacing:-.2px}
h3{font-size:16px;margin:20px 0 6px;color:var(--mist)}
p,li{color:#d6e4e6;font-size:15px}
.muted{color:var(--mist)}
table{border-collapse:collapse;width:100%;margin:10px 0 4px;font-size:14px}
th,td{text-align:center;padding:7px 6px;border-bottom:1px solid var(--line)}
th{color:var(--mist);font-weight:600;font-size:12px;letter-spacing:.04em;text-transform:uppercase}
td:first-child,th:first-child{text-align:left}
tbody tr:hover{background:rgba(255,255,255,.02)}
.sea{color:var(--foam);font-weight:600}
.flights{list-style:none;padding:0;margin:8px 0}
.flights li{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px 12px;margin:5px 0;font-family:"IBM Plex Mono",monospace;font-size:13.5px}
.embed{margin:12px 0 8px}
.ph{background:var(--panel);border:1px dashed var(--line);border-radius:12px;padding:22px 16px;text-align:center}
.ph p{margin:0 0 10px;color:var(--mist);font-size:13.5px}
.ph button{cursor:pointer;font-family:inherit;font-size:14px;font-weight:600;color:var(--deep);background:var(--focus);border:0;border-radius:999px;padding:10px 18px}
.faq dt{font-weight:600;margin:16px 0 3px;font-size:15.5px}
.faq dd{margin:0;color:#cfe0e2;font-size:14.5px}
.city{background:linear-gradient(180deg,rgba(14,50,66,.45),rgba(10,39,51,.45));border:1px solid var(--line);border-radius:16px;padding:14px 16px 8px;margin:14px 0}
.note{font-size:13px;color:var(--mist-dim);margin-top:6px}
hr{border:0;border-top:1px solid var(--line);margin:28px 0}
footer{border-top:1px solid var(--line);padding:22px 0 calc(40px + env(safe-area-inset-bottom,0px));color:var(--mist-dim);font-size:12.5px;line-height:1.6;margin-top:30px}
footer a{color:var(--mist)}
"""

def esc(s): return html.escape(str(s), quote=True)
def hav(la1, lo1, la2, lo2):
    R=6371.0; r=math.pi/180
    dla=(la2-la1)*r; dlo=(lo2-lo1)*r
    a=math.sin(dla/2)**2+math.cos(la1*r)*math.cos(la2*r)*math.sin(dlo/2)**2
    return 2*R*math.asin(math.sqrt(a))
def rnd(x): return None if x is None else int(round(x))
def fmt_hm(h):
    H=int(h); M=int(round((h-H)*60))
    if M==60: H+=1; M=0
    return f"{H}h{M:02d}" if M else f"{H}h"
def slugify(s):
    s=s.lower().replace("\u00e4","ae").replace("\u00f6","oe").replace("\u00fc","ue").replace("\u00df","ss")
    return "".join(c if c.isalnum() else "-" for c in s).strip("-")

def sea_avg(c, m):
    try: return c["sea"]["m"][m][1]
    except Exception: return None
def air_avg(c, m):
    try: return c["air"]["m"][m][1]
    except Exception: return None
def sun_h(c, m):
    try:
        v=c["sun"]["m"][m]; return v if isinstance(v,(int,float)) else None
    except Exception: return None
def rain_days(c, m):
    try: return c["rain"]["m"][m][1]*DIM[m]
    except Exception: return None

def month_table(c):
    head="<tr><th>Monat</th><th>Meer</th><th>Luft</th><th>Sonne</th><th>Regentage</th></tr>"
    rows=[]
    for m in range(12):
        sea=rnd(sea_avg(c,m))
        if sea is None:
            rows.append(f"<tr><td>{MONTHS_DE[m]}</td><td>\u2013</td><td>\u2013</td><td>\u2013</td><td>\u2013</td></tr>")
            continue
        air=rnd(air_avg(c,m)); sun=rnd(sun_h(c,m)); rd=rnd(rain_days(c,m))
        air_s=f"{air}\u00b0" if air is not None else "\u2013"
        sun_s=f"{sun} h" if sun is not None else "\u2013"
        rd_s=str(rd) if rd is not None else "\u2013"
        rows.append(f"<tr><td>{MONTHS_DE[m]}</td><td class=\"sea\">{sea}\u00b0</td>"
                    f"<td>{air_s}</td><td>{sun_s}</td><td>{rd_s}</td></tr>")
    return f"<table><thead>{head}</thead><tbody>{''.join(rows)}</tbody></table>"

def compare_table(cities, clim):
    head="<tr><th>Monat</th>"+"".join(f"<th>{esc(d['name'])}</th>" for d in cities)+"</tr>"
    rows=[]
    for m in range(12):
        tds=[]
        for d in cities:
            v=rnd(sea_avg(clim.get(d["id"],{}),m))
            tds.append(f"<td class=\"sea\">{v}\u00b0</td>" if v is not None else "<td>\u2013</td>")
        rows.append(f"<tr><td>{MONTHS_DE[m]}</td>{''.join(tds)}</tr>")
    return f"<table><thead>{head}</thead><tbody>{''.join(rows)}</tbody></table>"

def flight_items(d, flights, dest_index):
    idx=dest_index[d["id"]]; out=[]
    for ok in SHOW_ORIGINS:
        o=ORIGINS.get(ok)
        if not o: continue
        h=hav(o["lat"],o["lon"],d["lat"],d["lon"])/800+0.75
        bits=flights.get(ok,"")
        direct = idx < len(bits) and bits[idx]=="1"
        out.append(f"<li>\u2708 ab {esc(o['label'])} ~{fmt_hm(h)} \u00b7 {'direkt' if direct else 'mit Umstieg'}</li>")
    return "<ul class=\"flights\">"+"".join(out)+"</ul>"

def stay22(d):
    url=(f"https://www.stay22.com/embed/gm?aid={STAY22_AID}"
         f"&lat={d['lat']}&lng={d['lon']}&campaign={slugify(d['id'])}&maincolor=6fe0d4")
    return ('<div class="embed"><div class="ph" data-s22="'+esc(url)+'">'
            '<p>Unterk\u00fcnfte in '+esc(d["name"])+' \u2013 Preise mehrerer Anbieter auf einer Karte.</p>'
            '<button onclick="szLoadMap(this)">\U0001f3e8 Hotels auf der Karte anzeigen</button></div></div>')

def gyg(d):
    q=esc(d["name"]+", "+COUNTRY_EN.get(d["country"], d["country"]))
    return ('<div class="embed"><div class="ph" data-gygq="'+q+'">'
            '<p>Touren &amp; Aktivit\u00e4ten in '+esc(d["name"])+'.</p>'
            '<button onclick="szLoadGyg(this)">\U0001f39f\ufe0f Aktivit\u00e4ten anzeigen</button></div></div>')

LOADER = ("""
<script>
function szLoadMap(b){var d=b.parentNode,u=d.getAttribute('data-s22');
 d.innerHTML='<iframe src="'+u+'" width="100%" height="460" style="border:0;border-radius:12px" loading="lazy"></iframe>';}
var szGygLoaded=false;
function szLoadGyg(b){var d=b.parentNode,q=d.getAttribute('data-gygq');
 d.innerHTML='<div data-gyg-href="https://widget.getyourguide.com/default/activities.frame" data-gyg-locale-code="de-DE" data-gyg-widget="activities" data-gyg-number-of-items="4" data-gyg-partner-id="__GYG__" data-gyg-q="'+q+'"></div>';
 if(!szGygLoaded){var s=document.createElement('script');s.async=true;s.defer=true;
  s.src='https://widget.getyourguide.com/pw/latest/client-loader/widget.js';document.body.appendChild(s);szGygLoaded=true;}}
</script>
""").replace("__GYG__", GYG_PARTNER)

def swim_season(cs):
    months=[m for m in range(12) if cs[m] is not None and cs[m]>=24]
    if len(months)==12: return "ganzj\u00e4hrig"
    if not months: return None
    best=(0,0,-1)
    for start in range(12):
        if cs[start] is None or cs[start]<24: continue
        ln=0
        for k in range(12):
            mm=(start+k)%12
            if cs[mm] is not None and cs[mm]>=24: ln+=1
            else: break
        if ln>best[2]: best=(start,(start+ln-1)%12,ln)
    return f"von {MONTHS_DE[best[0]]} bis {MONTHS_DE[best[1]]}"

def join_names(names):
    if len(names)==1: return names[0]
    return ", ".join(names[:-1]) + " und " + names[-1]

def build_country(country, meta, clim, flights):
    dest_index={d["id"]: i for i, d in enumerate(meta["dest"])}
    cities=[d for d in meta["dest"] if d["country"]==country and d["id"] in clim]
    if not cities:
        return None, None
    slug=slugify(country)
    region=cities[0]["region"] or country
    citynames=join_names([d["name"] for d in cities])
    phrase=COUNTRY_PHRASE.get(country, country)

    # Laender-Mittel je Monat (ueber Staedte)
    cs=[]
    for m in range(12):
        vals=[sea_avg(clim[d["id"]],m) for d in cities if sea_avg(clim[d["id"]],m) is not None]
        cs.append(sum(vals)/len(vals) if vals else None)
    warm=max((m for m in range(12) if cs[m] is not None), key=lambda m: cs[m], default=6)
    season=swim_season(cs)
    season_txt = season if season else "in den w\u00e4rmeren Monaten"
    # Hitzehinweis
    maxair=max((air_avg(clim[d["id"]],m) or 0) for d in cities for m in range(12))
    hot = (" Im Hochsommer wird es an Land extrem hei\u00df (oft \u00fcber 40\u00a0\u00b0C) \u2013 "
           "am angenehmsten zum Baden sind Fr\u00fchjahr und Herbst.") if maxair>=39 else ""
    lead=(f"Am {esc(region)} \u2013 mit {esc(citynames)} \u2013 ist das Meer {season_txt} "
          f"warm genug zum Baden (\u00fcber 24\u00a0\u00b0C). Am w\u00e4rmsten ist es im "
          f"{MONTHS_DE[warm]} mit rund {rnd(cs[warm])}\u00a0\u00b0C Wassertemperatur.{hot}")

    today=datetime.date.today().isoformat()
    title=(f"Baden in {country}: Meerestemperatur Monat f\u00fcr Monat "
           f"({citynames}) \u2013 Seazons")
    desc=(f"Wie warm ist das Meer in {country}? Wassertemperatur, Wetter, Sonnenstunden und "
          f"Direktfl\u00fcge f\u00fcr {citynames} \u2013 Monat f\u00fcr Monat.")

    parts=[]
    parts.append(f'<div class="eyebrow">{esc(region)}</div>')
    parts.append(f"<h1>Baden in {esc(phrase)}: Wie warm ist das Meer?</h1>")
    parts.append(f'<p class="lead">{lead}</p>')

    parts.append("<h2>Meerestemperatur pro Monat im Vergleich</h2>")
    parts.append(f"<p>Durchschnittliche Wassertemperatur (\u00b0C) f\u00fcr {esc(citynames)}:</p>")
    parts.append(compare_table(cities, clim))

    # Pro Stadt
    faq=[]
    for d in cities:
        c=clim[d["id"]]
        parts.append(f'<div class="city"><h2>{d["flag"]} {esc(d["name"])}</h2>')
        parts.append("<h3>Klima &amp; Meerwasser Monat f\u00fcr Monat</h3>")
        parts.append(month_table(c))
        parts.append("<h3>Anreise &amp; Flugzeit ab DACH</h3>")
        parts.append(flight_items(d, flights, dest_index))
        parts.append("<h3>Unterk\u00fcnfte</h3>")
        parts.append(stay22(d))
        parts.append("<h3>Aktivit\u00e4ten</h3>")
        parts.append(gyg(d))
        parts.append("</div>")

    # FAQ: Primaerstadt, alle Monate + Anreise je Stadt
    primary=cities[0]; pc=clim[primary["id"]]
    for m in range(12):
        v=rnd(sea_avg(pc,m))
        if v is None: continue
        faq.append((f"Wie warm ist das Meer in {primary['name']} im {MONTHS_DE[m]}?",
                    f"Im {MONTHS_DE[m]} liegt die Wassertemperatur in {primary['name']} bei rund {v}\u00a0\u00b0C."))
    if season:
        faq.append((f"Wann ist die beste Reisezeit zum Baden in {country}?",
                    f"Das Meer ist {season} \u00fcber 24\u00a0\u00b0C; am w\u00e4rmsten im {MONTHS_DE[warm]} "
                    f"mit rund {rnd(cs[warm])}\u00a0\u00b0C."))
    for d in cities:
        idx=dest_index[d["id"]]
        vie=flights.get("VIE","")
        direct = idx < len(vie) and vie[idx]=="1"
        h=hav(ORIGINS['VIE']['lat'],ORIGINS['VIE']['lon'],d['lat'],d['lon'])/800+0.75
        faq.append((f"Gibt es Direktfl\u00fcge nach {d['name']}?",
                    f"Ab Wien ist {d['name']} in ca. {fmt_hm(h)} erreichbar \u2013 "
                    f"{'meist als Direktflug' if direct else 'in der Regel mit einem Umstieg'}."))

    parts.append("<h2>H\u00e4ufige Fragen</h2><dl class=\"faq\">")
    for q,a in faq:
        parts.append(f"<dt>{esc(q)}</dt><dd>{esc(a)}</dd>")
    parts.append("</dl>")

    parts.append('<hr><p class="muted">Mehr Ziele und der Monatsvergleich f\u00fcr ganz Europa &amp; '
                 'Mittelmeer-Anrainer auf der <a href="/">Seazons-Startseite</a>.</p>')

    body="\n".join(parts)

    # JSON-LD
    faq_ld={"@context":"https://schema.org","@type":"FAQPage",
            "mainEntity":[{"@type":"Question","name":q,
                           "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}
    bc_ld={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Seazons","item":"https://seazons.de/"},
            {"@type":"ListItem","position":2,"name":f"Baden in {country}",
             "item":f"https://seazons.de/land/{slug}.html"}]}

    page=PAGE.replace("__TITLE__", esc(title)).replace("__DESC__", esc(desc))
    page=page.replace("__CANON__", f"https://seazons.de/land/{slug}.html")
    page=page.replace("__BODY__", body).replace("__CSS__", CSS)
    page=page.replace("__JSONLD__", json.dumps([faq_ld, bc_ld], ensure_ascii=False))
    page=page.replace("__DATE__", today).replace("__LOADER__", LOADER)
    return slug, page

PAGE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>__TITLE__</title>
<meta name="description" content="__DESC__" />
<link rel="canonical" href="__CANON__" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
<script defer data-domain="seazons.de" src="https://plausible.io/js/script.js"></script>
<script type="application/ld+json">__JSONLD__</script>
<style>__CSS__</style>
</head>
<body>
  <div class="wrap">
    <div class="top"><span class="glyph">\U0001f30a</span><b>Seazons</b><a class="back" href="/">\u2190 zur Suche</a></div>
    __BODY__
    <footer>
      <p><a href="/impressum.html">Impressum</a> \u00b7 <a href="/datenschutz.html">Datenschutz</a> \u00b7
      <a href="#" onclick="if(window.SeazonsConsent){SeazonsConsent.open();}return false;">Cookie-Einstellungen</a></p>
      <p>Seazons enth\u00e4lt Werbe-/Affiliate-Links: Buchst du \u00fcber einen solchen Link, erhalten wir ggf. eine Provision \u2013 f\u00fcr dich ohne Aufpreis.</p>
      <p>Wir stellen alle Informationen nach bestem Wissen und Gewissen bereit, k\u00f6nnen aber keine Gew\u00e4hr f\u00fcr jederzeitige Vollst\u00e4ndigkeit, Aktualit\u00e4t und Richtigkeit \u00fcbernehmen. Klima sind typische Mehrjahreswerte; Flug- und Preisangaben k\u00f6nnen sich \u00e4ndern. Zuletzt aktualisiert: __DATE__.</p>
      <p class="muted">\u00a9 greenbody e.U. \u00b7 Seazons</p>
    </footer>
  </div>
  <script src="/consent.js?v=2" defer></script>
  __LOADER__
</body>
</html>
"""

def main():
    a=sys.argv
    meta_p=a[a.index("--meta")+1] if "--meta" in a else "seazons_meta.json"
    data=a[a.index("--data")+1] if "--data" in a else "."
    out=a[a.index("--out")+1] if "--out" in a else "."
    only=a[a.index("--only")+1].lower() if "--only" in a else None

    global ORIGINS
    meta=json.load(open(meta_p, encoding="utf-8"))
    ORIGINS=meta["origins"]
    clim=json.load(open(os.path.join(data,"climate.json"), encoding="utf-8"))
    try: flights=json.load(open(os.path.join(data,"flights.json"), encoding="utf-8"))
    except Exception: flights={}

    countries=sorted({d["country"] for d in meta["dest"]})
    os.makedirs(os.path.join(out,"land"), exist_ok=True)
    n=0
    for country in countries:
        slug=slugify(country)
        if only and only not in (slug, country.lower()): continue
        res=build_country(country, meta, clim, flights)
        if not res or not res[0]:
            sys.stderr.write(f"uebersprungen (keine Daten): {country}\n"); continue
        slug,page=res
        path=os.path.join(out,"land",slug+".html")
        with open(path,"w",encoding="utf-8") as f: f.write(page)
        sys.stderr.write(f"OK  {path}  ({len(page)//1024} KB, {sum(1 for d in meta['dest'] if d['country']==country)} Orte)\n")
        n+=1
    sys.stderr.write(f"FERTIG: {n} Seite(n).\n")

if __name__ == "__main__":
    main()
