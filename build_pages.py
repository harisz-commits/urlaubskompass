#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_pages.py - erzeugt SEO-/KI-optimierte Laender- und Zielseiten aus
climate.json / flights.json + seazons_meta.json. Lockerer, menschlicher Text,
nur normale Bindestriche, gekuerzte FAQ, manuelle Direktflug-Korrektur.

  python3 build_pages.py --meta /root/seazons_meta.json \
      --data /var/www/html/meerwasser --out /var/www/html/meerwasser --only vae
"""
import json, os, sys, math, html, datetime

STAY22_AID = "seazonsde"
GYG_PARTNER = "WQAOT0I"
SHOW_ORIGINS = ["VIE", "MUC", "ZRH"]

MONTHS_DE = ["Januar","Februar","März","April","Mai","Juni","Juli","August",
             "September","Oktober","November","Dezember"]
DIM = [31,28,31,30,31,30,31,31,30,31,30,31]

COUNTRY_EN = {
  "VAE":"United Arab Emirates","Ägypten":"Egypt","Tunesien":"Tunisia",
  "Marokko":"Morocco","Israel":"Israel","Jordanien":"Jordan","Libanon":"Lebanon",
  "Kap Verde":"Cape Verde","Oman":"Oman","Gambia":"Gambia","Spanien":"Spain",
  "Portugal":"Portugal","Frankreich":"France","Italien":"Italy","Griechenland":"Greece",
  "Kroatien":"Croatia","Türkei":"Turkey","Zypern":"Cyprus","Malta":"Malta",
  "Montenegro":"Montenegro","Albanien":"Albania","Slowenien":"Slovenia",
  "Bulgarien":"Bulgaria","Rumänien":"Romania","Deutschland":"Germany",
  "Niederlande":"Netherlands","England":"United Kingdom",
  "Malediven":"Maldives",
  "Mauritius":"Mauritius",
  "Seychellen":"Seychelles",
  "Tansania":"Tanzania",
  "Kenia":"Kenya",
  "Madagaskar":"Madagascar",
  "Sri Lanka":"Sri Lanka",
  "Indien":"India",
  "Thailand":"Thailand",
  "Vietnam":"Vietnam",
  "Indonesien":"Indonesia",
  "Malaysia":"Malaysia",
  "Philippinen":"Philippines",
  "China":"China",
  "Japan":"Japan",
  "Dominikanische Republik":"Dominican Republic",
  "Kuba":"Cuba",
  "Jamaika":"Jamaica",
  "Mexiko":"Mexico",
  "Barbados":"Barbados",
  "Curaçao":"Curacao",
  "Aruba":"Aruba",
  "Bahamas":"Bahamas",
  "Antigua und Barbuda":"Antigua and Barbuda",
  "St. Lucia":"Saint Lucia",
  "Martinique":"Martinique",
  "Guadeloupe":"Guadeloupe",
  "Puerto Rico":"Puerto Rico",
  "Turks- und Caicosinseln":"Turks and Caicos",
  "Costa Rica":"Costa Rica",
  "Panama":"Panama",
  "Belize":"Belize",
  "Kolumbien":"Colombia",
  "USA":"United States",
  "Brasilien":"Brazil",
  "Südafrika":"South Africa",
  "Senegal":"Senegal",
  "Mosambik":"Mozambique",
  "Katar":"Qatar",
  "Bahrain":"Bahrain",
  "Australien":"Australia",
  "Fidschi":"Fiji",
  "Französisch-Polynesien":"French Polynesia",
  "Georgien":"Georgia",
}
COUNTRY_PHRASE = {
  "VAE":"den Vereinigten Arabischen Emiraten",
  "Ägypten":"Ägypten", "Tunesien":"Tunesien", "Marokko":"Marokko",
}

# Bekannte Direktverbindungen ab DACH (OpenFlights ist veraltet -> manuell korrigiert)
OVERRIDE_DIRECT = {}
for _o in ("VIE","MUC","ZRH","FRA","DUS"):
    for _d in ("dubai","abudhabi"):
        OVERRIDE_DIRECT[(_o,_d)] = True

# Locker geschriebene, menschliche Intros (eigene Texte). Liste = Absaetze.
CUSTOM_INTRO = {
 "vae":[
  "Warmes, sicheres Badewasser fast das ganze Jahr - dafür stehen die Emirate. Dubai, Abu Dhabi und Ras Al Khaimah liegen alle am Persischen Golf, und der bleibt selbst im Winter angenehm warm. Wirklich kalt wird das Meer hier nie.",
  "Der Haken ist der Sommer. Zwischen Juni und September klettert die Lufttemperatur locker über 40 Grad, dazu kommt an der Küste eine ordentliche Portion Schwüle. Das Wasser fühlt sich dann eher wie eine warme Badewanne an als wie Erfrischung, und tagsüber ist Schatten Pflicht. Wer es entspannt mag, reist deshalb am besten in der kühleren Jahreshälfte, also grob von Oktober bis April.",
  "Praktisch: Alle drei Ziele erreichst du ab Wien, München und Zürich nonstop, meist in gut sechs Stunden. Du sitzt also morgens im Flieger und liegst nachmittags am Strand.",
 ],
 "dubai":[
  "Dubai ist die sichere Bank, wenn du einfach nur warmes Wasser und Sonne willst. Der Persische Golf kühlt selbst im Januar kaum unter 22 Grad ab, und ab dem Frühling wird das Meer richtig warm. Regen fällt praktisch das ganze Jahr kaum.",
  "Spannend wird nur der Hochsommer. Im Juli und August zeigt das Thermometer oft über 40 Grad, dazu kommt an der Küste hohe Luftfeuchtigkeit. Baden geht dann zwar immer noch, aber Abkühlung ist was anderes, und Sightseeing macht in der Mittagshitze keinen Spaß. Strand am Morgen oder späten Nachmittag, mittags lieber Pool oder Mall mit Klimaanlage.",
  "Am angenehmsten ist Dubai zwischen Oktober und April: warmes Meer, blauer Himmel und Lufttemperaturen, bei denen man auch tagsüber gut draußen sein kann. Ab Wien, München und Zürich geht es nonstop hin, in rund sechs Stunden bist du da. Kleiner Hinweis: Viele der schönsten Strandabschnitte gehören zu Hotels, das lohnt sich beim Buchen mitzudenken.",
 ],
 "abudhabi":[
  "Abu Dhabi ist der etwas ruhigere große Nachbar von Dubai. Gleiche warme Golfküste, gleiche Sonne, nur insgesamt eine Spur gelassener und weniger trubelig. Das Meer ist fast das ganze Jahr badewarm.",
  "Im Sommer gilt das Gleiche wie überall am Golf: Juli und August sind mit über 40 Grad und viel Schwüle echt heftig. Die schöne Badezeit ist die kühlere Hälfte des Jahres, ungefähr Oktober bis April, mit warmem Wasser und erträglicher Luft.",
  "Hinkommen ist einfach: Etihad fliegt ab Wien, München und Zürich direkt nach Abu Dhabi, du bist in gut sechs Stunden da.",
 ],
 "rasalkhaimah":[
  "Ras Al Khaimah ist das entspannte Emirat im Norden - mehr Berge, Strand und Natur, weniger Wolkenkratzer und Trubel. Wer Golf-Wärme ohne Großstadt sucht, ist hier richtig.",
  "Das Wasser ist genauso warm wie in Dubai, und auch hier gilt: Sommer brutal heiß, Winter und Frühjahr ideal zum Baden. Dazu gibt es das ganze Jahr kaum Regen.",
  "Bei der Anreise ist Ras Al Khaimah etwas zickiger als Dubai: Direktverbindungen ab dem deutschsprachigen Raum sind dünn gesät und oft saisonal. Häufig fliegst du nach Dubai und fährst die letzte knappe Stunde mit dem Auto oder Transfer weiter.",
 ],
}

CSS = """
:root{--deep:#04141d;--deep2:#06202c;--panel:#0a2733;--panel2:#0e3242;--line:rgba(178,224,224,.14);--foam:#e9f4f3;--mist:#8aa9b2;--mist-dim:#5d7e88;--focus:#6fe0d4;--maxw:820px}
*{box-sizing:border-box}html{background:var(--deep2)}html,body{margin:0}
body{background:linear-gradient(180deg,var(--deep),var(--deep2));color:var(--foam);font-family:"Space Grotesk",system-ui,-apple-system,Segoe UI,Roboto,sans-serif;min-height:100vh;line-height:1.62;-webkit-font-smoothing:antialiased}
.wrap{max-width:var(--maxw);margin:0 auto;padding:24px 20px calc(64px + env(safe-area-inset-bottom,0px))}
a{color:var(--focus)}
.top{display:flex;align-items:center;gap:10px;padding:4px 0 16px}
.top .glyph{font-size:20px}.top b{font-size:17px}.top .back{margin-left:auto;font-size:13.5px}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:11.5px;letter-spacing:.28em;text-transform:uppercase;color:var(--mist-dim)}
h1{font-size:clamp(25px,5vw,36px);line-height:1.1;margin:8px 0 14px;letter-spacing:-.4px}
.prose p{font-size:15.5px;color:#dde9ea;margin:0 0 13px}
.box{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--focus);border-radius:12px;padding:13px 16px;margin:6px 0 22px}
.box b{color:var(--foam)}
h2{font-size:21px;margin:32px 0 8px;letter-spacing:-.2px}
h3{font-size:14px;margin:18px 0 5px;color:var(--mist);text-transform:uppercase;letter-spacing:.05em}
p,li{color:#d6e4e6;font-size:15px}
.muted{color:var(--mist)}
table{border-collapse:collapse;width:100%;margin:8px 0 4px;font-size:14px}
th,td{text-align:center;padding:7px 6px;border-bottom:1px solid var(--line)}
th{color:var(--mist);font-weight:600;font-size:12px;letter-spacing:.04em;text-transform:uppercase}
td:first-child,th:first-child{text-align:left}
tbody tr:hover{background:rgba(255,255,255,.02)}
.sea{color:var(--foam);font-weight:600}
.flights{list-style:none;padding:0;margin:6px 0}
.flights li{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px 12px;margin:5px 0;font-family:"IBM Plex Mono",monospace;font-size:13.5px}
.embed{margin:10px 0 6px}
.ph{background:var(--panel);border:1px dashed var(--line);border-radius:12px;padding:20px 16px;text-align:center}
.ph p{margin:0 0 10px;color:var(--mist);font-size:13.5px}
.ph button{cursor:pointer;font-family:inherit;font-size:14px;font-weight:600;color:var(--deep);background:var(--focus);border:0;border-radius:999px;padding:10px 18px}
.faq dt{font-weight:600;margin:15px 0 3px;font-size:15.5px}
.faq dd{margin:0;color:#cfe0e2;font-size:14.5px}
.city{background:linear-gradient(180deg,rgba(14,50,66,.45),rgba(10,39,51,.45));border:1px solid var(--line);border-radius:16px;padding:14px 16px 8px;margin:16px 0}
.links{font-size:14.5px}.links a{display:inline-block;margin:3px 10px 3px 0}
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
    s=s.lower().replace("ä","ae").replace("ö","oe").replace("ü","ue").replace("ß","ss")
    return "".join(c if c.isalnum() else "-" for c in s).strip("-")

def sea_avg(c, m):
    try: return c["sea"]["m"][m][1]
    except Exception: return None
def air_hi(c, m):
    try: return c["air"]["m"][m][4]
    except Exception:
        try: return c["air"]["m"][m][1]
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

def warm_cold(cs):
    valid=[m for m in range(12) if cs[m] is not None]
    if not valid: return 6,0
    return max(valid,key=lambda m:cs[m]), min(valid,key=lambda m:cs[m])

def swim_season(cs):
    months=[m for m in range(12) if cs[m] is not None and cs[m]>=24]
    if len(months)==12: return "das ganze Jahr über"
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

def month_table(c):
    head="<tr><th>Monat</th><th>Meer</th><th>Luft</th><th>Sonne</th><th>Regentage</th></tr>"
    rows=[]
    for m in range(12):
        sea=rnd(sea_avg(c,m))
        if sea is None:
            rows.append(f"<tr><td>{MONTHS_DE[m]}</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>")
            continue
        air=rnd(air_avg(c,m)); sun=rnd(sun_h(c,m)); rd=rnd(rain_days(c,m))
        air_s=f"{air}°" if air is not None else "-"
        sun_s=f"{sun} h" if sun is not None else "-"
        rd_s=str(rd) if rd is not None else "-"
        rows.append(f"<tr><td>{MONTHS_DE[m]}</td><td class=\"sea\">{sea}°</td>"
                    f"<td>{air_s}</td><td>{sun_s}</td><td>{rd_s}</td></tr>")
    return f"<table><thead>{head}</thead><tbody>{''.join(rows)}</tbody></table>"

def compare_table(cities, clim):
    head="<tr><th>Monat</th>"+"".join(f"<th>{esc(d['name'])}</th>" for d in cities)+"</tr>"
    rows=[]
    for m in range(12):
        tds=[]
        for d in cities:
            v=rnd(sea_avg(clim.get(d["id"],{}),m))
            tds.append(f"<td class=\"sea\">{v}°</td>" if v is not None else "<td>-</td>")
        rows.append(f"<tr><td>{MONTHS_DE[m]}</td>{''.join(tds)}</tr>")
    return f"<table><thead>{head}</thead><tbody>{''.join(rows)}</tbody></table>"

def is_direct(ok, d, flights, dest_index):
    if (ok, d["id"]) in OVERRIDE_DIRECT:
        return OVERRIDE_DIRECT[(ok, d["id"])]
    idx=dest_index[d["id"]]; bits=flights.get(ok,"")
    return idx < len(bits) and bits[idx]=="1"

LONGHAUL_H = 7.5   # ab hier keine harte Direktflug-Aussage (Saisonfluege wechseln staendig)

def flight_hours(ok, d):
    o=ORIGINS[ok]
    return hav(o["lat"],o["lon"],d["lat"],d["lon"])/800+0.75

def flight_items(d, flights, dest_index):
    out=[]
    for ok in SHOW_ORIGINS:
        o=ORIGINS.get(ok)
        if not o: continue
        h=flight_hours(ok, d)
        if h > LONGHAUL_H:
            note="Direktflug je nach Saison, sonst ein Umstieg"
        else:
            note="direkt" if is_direct(ok, d, flights, dest_index) else "mit Umstieg"
        out.append(f"<li>ab {esc(o['label'])} ~{fmt_hm(h)} · {note}</li>")
    return "<ul class=\"flights\">"+"".join(out)+"</ul>"

def stay22(d):
    url=(f"https://www.stay22.com/embed/gm?aid={STAY22_AID}"
         f"&lat={d['lat']}&lng={d['lon']}&campaign={slugify(d['id'])}&maincolor=6fe0d4")
    return ('<div class="embed"><div class="ph" data-s22="'+esc(url)+'">'
            '<p>Unterkünfte in '+esc(d["name"])+', Preise von mehreren Anbietern auf einer Karte.</p>'
            '<button onclick="szLoadMap(this)">Hotels auf der Karte anzeigen</button></div></div>')

def gyg(d):
    q=esc(d["name"]+", "+COUNTRY_EN.get(d["country"], d["country"]))
    return ('<div class="embed"><div class="ph" data-gygq="'+q+'">'
            '<p>Touren und Aktivitäten in '+esc(d["name"])+'.</p>'
            '<button onclick="szLoadGyg(this)">Aktivitäten anzeigen</button></div></div>')

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

def intro_prose(key, name, region, cs):
    if key in CUSTOM_INTRO:
        return "".join(f"<p>{esc(p)}</p>" for p in CUSTOM_INTRO[key])
    warm, cold = warm_cold(cs)
    sw = swim_season(cs)
    if sw:
        season = f"Angenehm baden kannst du ungefähr {sw}."
    else:
        season = "Richtig warm wird das Wasser hier eher selten, es bleibt das Jahr über frisch."
    p1=(f"{name} liegt am {region}, und wie warm das Wasser ist, hängt stark vom Monat ab. "
        f"Am wärmsten wird das Meer im {MONTHS_DE[warm]} mit rund {rnd(cs[warm])} Grad, "
        f"am kühlsten im {MONTHS_DE[cold]} mit etwa {rnd(cs[cold])} Grad. {season}")
    p2=("Die Tabelle unten zeigt dir Wasser- und Lufttemperatur, Sonnenstunden und Regentage "
        "Monat für Monat - so findest du schnell den Zeitraum, der zu dir passt.")
    return f"<p>{esc(p1)}</p><p>{esc(p2)}</p>"

def quick_box(name, cs, d, flights, dest_index):
    warm,_=warm_cold(cs); sw=swim_season(cs)
    when = sw if sw else "nur in den wärmsten Monaten"
    flighttxt=""
    if d:
        h=flight_hours("VIE", d)
        if h > LONGHAUL_H:
            flighttxt=f" Ab Wien sind es rund {fmt_hm(h)} Flug."
        else:
            direct_any=any(is_direct(ok, d, flights, dest_index) for ok in SHOW_ORIGINS)
            flighttxt=(f" Ab Wien bist du in rund {fmt_hm(h)} da"
                       f"{', meist direkt' if direct_any else ', meist mit einem Umstieg'}.")
    return (f'<div class="box"><b>Kurz gesagt:</b> Baden lohnt sich {esc(when)}, '
            f'am wärmsten ist das Meer im {MONTHS_DE[warm]} mit rund {rnd(cs[warm])} Grad.'
            f'{esc(flighttxt)}</div>')

def faq_dest(d, c, flights, dest_index):
    cs=[sea_avg(c,m) for m in range(12)]
    warm,cold=warm_cold(cs); sw=swim_season(cs)
    faq=[]
    if sw:
        faq.append((f"Wann ist die beste Reisezeit zum Baden in {d['name']}?",
                    f"Das Meer ist {sw} warm genug zum Baden. Am wärmsten ist es im {MONTHS_DE[warm]} "
                    f"mit rund {rnd(cs[warm])} Grad."))
    faq.append((f"Wie warm ist das Meer in {d['name']} im {MONTHS_DE[warm]}?",
                f"Im {MONTHS_DE[warm]} hat das Wasser in {d['name']} im Schnitt rund {rnd(cs[warm])} Grad."))
    ah=air_hi(c,warm)
    if ah is not None and ah>=35:
        faq.append((f"Wie heiß wird es im Sommer in {d['name']}?",
                    f"Im Hochsommer klettert die Lufttemperatur tagsüber auf über {rnd(ah)} Grad. "
                    f"Zum Sightseeing ist das viel, fürs Wasser dafür ideal."))
    h=flight_hours("VIE", d)
    if h > LONGHAUL_H:
        faq.append((f"Wie lange fliegt man nach {d['name']}?",
                    f"Ab Wien dauert der Flug ungefähr {fmt_hm(h)}. Direktverbindungen gibt es "
                    f"je nach Saison, sonst fliegst du mit einem Umstieg."))
    else:
        direct=is_direct("VIE", d, flights, dest_index)
        faq.append((f"Gibt es Direktflüge nach {d['name']}?",
                    f"Ab Wien ist {d['name']} in ungefähr {fmt_hm(h)} erreichbar, "
                    f"{'in der Regel als Direktflug' if direct else 'meist mit einem Umstieg'}."))
    return faq

def faq_country(country, cities, clim, flights, dest_index):
    cs=[]
    for m in range(12):
        vals=[sea_avg(clim[d["id"]],m) for d in cities if sea_avg(clim[d["id"]],m) is not None]
        cs.append(sum(vals)/len(vals) if vals else None)
    warm,_=warm_cold(cs); sw=swim_season(cs)
    primary=cities[0]
    faq=[]
    if sw:
        faq.append((f"Wann ist die beste Reisezeit zum Baden in {country}?",
                    f"Das Meer ist {sw} warm genug zum Baden, am wärmsten im {MONTHS_DE[warm]} "
                    f"mit rund {rnd(cs[warm])} Grad."))
    faq.append((f"Wie warm ist das Meer in {primary['name']} im {MONTHS_DE[warm]}?",
                f"Im {MONTHS_DE[warm]} liegt die Wassertemperatur in {primary['name']} bei rund "
                f"{rnd(sea_avg(clim[primary['id']],warm))} Grad."))
    h=flight_hours("VIE", primary)
    if h > LONGHAUL_H:
        faq.append((f"Wie lange fliegt man nach {primary['name']}?",
                    f"Ab Wien dauert der Flug ungefähr {fmt_hm(h)}. Direktverbindungen gibt es "
                    f"je nach Saison, sonst mit einem Umstieg."))
    else:
        direct=is_direct("VIE", primary, flights, dest_index)
        faq.append((f"Gibt es Direktflüge nach {primary['name']}?",
                    f"Ab Wien ist {primary['name']} in ungefähr {fmt_hm(h)} erreichbar, "
                    f"{'in der Regel als Direktflug' if direct else 'meist mit einem Umstieg'}."))
    return faq

def faq_html(faq):
    out=["<h2>Häufige Fragen</h2><dl class=\"faq\">"]
    for q,a in faq: out.append(f"<dt>{esc(q)}</dt><dd>{esc(a)}</dd>")
    out.append("</dl>")
    return "".join(out)

def faq_jsonld(faq):
    return {"@context":"https://schema.org","@type":"FAQPage",
            "mainEntity":[{"@type":"Question","name":q,
                           "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}
def breadcrumb(items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":u} for i,(n,u) in enumerate(items)]}

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
    <div class="top"><span class="glyph">🌊</span><b>Seazons</b><a class="back" href="/">zur Suche</a></div>
    __BODY__
    <footer>
      <p><a href="/impressum.html">Impressum</a> · <a href="/datenschutz.html">Datenschutz</a> ·
      <a href="#" onclick="if(window.SeazonsConsent){SeazonsConsent.open();}return false;">Cookie-Einstellungen</a></p>
      <p>Seazons enthält Werbe- und Affiliate-Links. Buchst du über so einen Link, bekommen wir vielleicht eine kleine Provision, für dich ohne Aufpreis.</p>
      <p>Wir geben alle Infos nach bestem Wissen und Gewissen weiter, können aber nicht garantieren, dass immer alles aktuell und richtig ist. Klimawerte sind typische Mehrjahres-Durchschnitte, Flug- und Preisangaben können sich ändern. Stand: __DATE__.</p>
      <p class="muted">greenbody e.U. · Seazons</p>
    </footer>
  </div>
  <script src="/consent.js?v=2" defer></script>
  __LOADER__
</body>
</html>
"""

def render(title, desc, canon, body, jsonld):
    p=PAGE.replace("__TITLE__", esc(title)).replace("__DESC__", esc(desc))
    p=p.replace("__CANON__", canon).replace("__CSS__", CSS)
    p=p.replace("__JSONLD__", json.dumps(jsonld, ensure_ascii=False))
    p=p.replace("__DATE__", datetime.date.today().isoformat())
    p=p.replace("__BODY__", body).replace("__LOADER__", LOADER)
    return p

def build_country(country, meta, clim, flights):
    dest_index={d["id"]: i for i, d in enumerate(meta["dest"])}
    cities=[d for d in meta["dest"] if d["country"]==country and d["id"] in clim]
    if not cities: return None, None
    slug=slugify(country); region=cities[0]["region"] or country
    phrase=COUNTRY_PHRASE.get(country, country)
    cs=[]
    for m in range(12):
        vals=[sea_avg(clim[d["id"]],m) for d in cities if sea_avg(clim[d["id"]],m) is not None]
        cs.append(sum(vals)/len(vals) if vals else None)

    P=[]
    P.append(f'<div class="eyebrow">{esc(region)}</div>')
    P.append(f"<h1>Baden in {esc(phrase)}: wie warm ist das Meer?</h1>")
    P.append(f'<div class="prose">{intro_prose(slug, country, region, cs)}</div>')
    P.append(quick_box(country, cs, cities[0], flights, dest_index))
    P.append("<h2>Wassertemperatur Monat für Monat</h2>")
    P.append(f"<p>Durchschnittliche Meerestemperatur in {esc(', '.join(d['name'] for d in cities))}:</p>")
    P.append(compare_table(cities, clim))
    for d in cities:
        c=clim[d["id"]]
        P.append(f'<div class="city"><h2>{d["flag"]} {esc(d["name"])}</h2>')
        ci=CUSTOM_INTRO.get(d["id"])
        if ci: P.append(f'<div class="prose"><p>{esc(ci[0])}</p></div>')
        P.append("<h3>Klima Monat für Monat</h3>")
        P.append(month_table(c))
        P.append("<h3>Anreise ab DACH</h3>")
        P.append(flight_items(d, flights, dest_index))
        P.append("<h3>Hotels</h3>")
        P.append(stay22(d))
        P.append("<h3>Aktivitäten</h3>")
        P.append(gyg(d))
        P.append(f'<p class="links" style="margin-top:6px"><a href="/ziel/{d["id"]}.html">Mehr Details zu {esc(d["name"])}</a></p>')
        P.append("</div>")
    faq=faq_country(country, cities, clim, flights, dest_index)
    P.append(faq_html(faq))
    P.append('<hr><p class="links"><a href="/">Alle Badeziele und Monatsvergleich</a></p>')
    body="\n".join(P)

    title=f"Baden in {country}: Meerestemperatur Monat für Monat - Seazons"
    desc=(f"Wie warm ist das Meer in {country}? Wassertemperatur, Wetter und Direktflüge für "
          f"{', '.join(d['name'] for d in cities)}, Monat für Monat.")
    canon=f"https://seazons.de/land/{slug}.html"
    jsonld=[faq_jsonld(faq), breadcrumb([("Seazons","https://seazons.de/"),
            (f"Baden in {country}", canon)])]
    return slug, render(title, desc, canon, body, jsonld)

def build_dest(d, meta, clim, flights):
    dest_index={x["id"]: i for i, x in enumerate(meta["dest"])}
    c=clim.get(d["id"])
    if not c: return None, None
    region=d["region"] or d["country"]
    cs=[sea_avg(c,m) for m in range(12)]
    cslug=slugify(d["country"])
    siblings=[x for x in meta["dest"] if x["country"]==d["country"] and x["id"]!=d["id"] and x["id"] in clim]

    P=[]
    P.append(f'<div class="eyebrow">{esc(d["country"])} · {esc(region)}</div>')
    P.append(f"<h1>{d['flag']} {esc(d['name'])}: wie warm ist das Meer?</h1>")
    P.append(f'<div class="prose">{intro_prose(d["id"], d["name"], region, cs)}</div>')
    P.append(quick_box(d["name"], cs, d, flights, dest_index))
    P.append("<h2>Wetter und Wassertemperatur Monat für Monat</h2>")
    P.append(month_table(c))
    P.append("<h2>Anreise</h2>")
    P.append("<p>Ungefähre Flugzeiten ab dem deutschsprachigen Raum:</p>")
    P.append(flight_items(d, flights, dest_index))
    P.append("<h2>Übernachten</h2>")
    P.append(stay22(d))
    P.append("<h2>Aktivitäten vor Ort</h2>")
    P.append(gyg(d))
    faq=faq_dest(d, c, flights, dest_index)
    P.append(faq_html(faq))
    links=[f'<a href="/land/{cslug}.html">Überblick {esc(d["country"])}</a>']
    for s in siblings[:6]:
        links.append(f'<a href="/ziel/{s["id"]}.html">{esc(s["name"])}</a>')
    links.append('<a href="/">Alle Badeziele</a>')
    P.append('<hr><p class="links">'+" ".join(links)+"</p>")
    body="\n".join(P)

    title=f"{d['name']}: Meerestemperatur und beste Reisezeit Monat für Monat - Seazons"
    desc=(f"Wie warm ist das Meer in {d['name']}? Wassertemperatur, Wetter, Sonnenstunden und "
          f"Flugzeit ab DACH, Monat für Monat.")
    canon=f"https://seazons.de/ziel/{d['id']}.html"
    jsonld=[faq_jsonld(faq), breadcrumb([("Seazons","https://seazons.de/"),
            (f"Baden in {d['country']}", f"https://seazons.de/land/{cslug}.html"),
            (d["name"], canon)])]
    return d["id"], render(title, desc, canon, body, jsonld)

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

    os.makedirs(os.path.join(out,"land"), exist_ok=True)
    os.makedirs(os.path.join(out,"ziel"), exist_ok=True)
    countries=sorted({d["country"] for d in meta["dest"]})
    nc=nd=0
    for country in countries:
        slug=slugify(country)
        if only and only not in (slug, country.lower()): continue
        s,page=build_country(country, meta, clim, flights)
        if s:
            open(os.path.join(out,"land",s+".html"),"w",encoding="utf-8").write(page); nc+=1
            sys.stderr.write(f"LAND  /land/{s}.html\n")
        for d in [x for x in meta["dest"] if x["country"]==country and x["id"] in clim]:
            did,dpage=build_dest(d, meta, clim, flights)
            if did:
                open(os.path.join(out,"ziel",did+".html"),"w",encoding="utf-8").write(dpage); nd+=1
                sys.stderr.write(f"ZIEL  /ziel/{did}.html\n")
    sys.stderr.write(f"FERTIG: {nc} Laenderseite(n), {nd} Zielseite(n).\n")

if __name__ == "__main__":
    main()
