/* Seazons – Cookie-Consent (Opt-in fuer Marketing).
   Plausible laeuft cookielos und zustimmungsfrei (im <head> eingebunden).
   Marketing-Dienste (Google Ads, Meta-Pixel) werden NUR nach Einwilligung geladen.
   IDs unten eintragen, sobald die Konten existieren – solange sie leer sind,
   wird nichts geladen (kein Tracking ohne Einwilligung, nichts bricht). */
(function () {
  "use strict";

  // === Hier spaeter die echten IDs eintragen ===
  var GOOGLE_ADS_ID = "";   // z.B. "AW-1234567890"
  var META_PIXEL_ID = "";   // z.B. "1234567890123456"
  // ============================================

  var KEY = "seazons_consent_v1";

  function read() {
    try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; }
  }
  function write(c) {
    try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {}
  }

  var marketingLoaded = false;
  function loadMarketing() {
    if (marketingLoaded) return;
    marketingLoaded = true;

    if (GOOGLE_ADS_ID) {
      var g = document.createElement("script");
      g.async = true;
      g.src = "https://www.googletagmanager.com/gtag/js?id=" + GOOGLE_ADS_ID;
      document.head.appendChild(g);
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag("js", new Date());
      window.gtag("config", GOOGLE_ADS_ID);
    }

    if (META_PIXEL_ID) {
      !function (f, b, e, v, n, t, s) {
        if (f.fbq) return; n = f.fbq = function () {
          n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
        };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0";
        n.queue = []; t = b.createElement(e); t.async = !0; t.src = v;
        s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
      }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
      window.fbq("init", META_PIXEL_ID);
      window.fbq("track", "PageView");
    }
  }

  function apply(c) {
    if (c && c.marketing) loadMarketing();
  }

  // ---- UI ----
  function injectStyle() {
    if (document.getElementById("seazons-consent-style")) return;
    var css = ""
      + ".sz-cc{position:fixed;left:0;right:0;bottom:0;z-index:9999;display:flex;justify-content:center;padding:14px}"
      + ".sz-cc-box{max-width:760px;width:100%;background:#0a2733;color:#e9f4f3;border:1px solid rgba(178,224,224,.25);"
      + "border-radius:14px;box-shadow:0 16px 44px -20px rgba(0,0,0,.9);padding:18px 18px 16px;"
      + "font-family:'Space Grotesk',system-ui,-apple-system,Segoe UI,Roboto,sans-serif;font-size:14px;line-height:1.55}"
      + ".sz-cc-box h3{margin:0 0 8px;font-size:16px;font-weight:700}"
      + ".sz-cc-box p{margin:0 0 12px;color:#b9cdd2}"
      + ".sz-cc-box a{color:#6fe0d4}"
      + ".sz-cc-row{display:flex;flex-wrap:wrap;gap:8px}"
      + ".sz-cc-btn{cursor:pointer;font-family:inherit;font-size:13.5px;border-radius:999px;padding:9px 16px;border:1px solid rgba(178,224,224,.25);background:transparent;color:#e9f4f3}"
      + ".sz-cc-btn.primary{background:#6fe0d4;color:#041820;border-color:#6fe0d4;font-weight:600}"
      + ".sz-cc-btn:hover{border-color:rgba(178,224,224,.5)}"
      + ".sz-cc-set{margin:4px 0 12px;display:none}"
      + ".sz-cc-set.on{display:block}"
      + ".sz-cc-toggle{display:flex;align-items:center;gap:10px;padding:10px 0;border-top:1px solid rgba(178,224,224,.12)}"
      + ".sz-cc-toggle:last-child{border-bottom:1px solid rgba(178,224,224,.12)}"
      + ".sz-cc-toggle .t-txt{flex:1}.sz-cc-toggle .t-txt small{color:#8aa9b2;display:block;font-size:12px}"
      + ".sz-cc-toggle input{width:18px;height:18px;accent-color:#6fe0d4}";
    var s = document.createElement("style");
    s.id = "seazons-consent-style";
    s.textContent = css;
    document.head.appendChild(s);
  }

  var bannerEl = null;
  function buildBanner() {
    injectStyle();
    var wrap = document.createElement("div");
    wrap.className = "sz-cc";
    wrap.setAttribute("role", "dialog");
    wrap.setAttribute("aria-label", "Cookie-Einstellungen");
    wrap.innerHTML =
      '<div class="sz-cc-box">'
      + '<h3>Datenschutz &amp; Cookies</h3>'
      + '<p>Wir nutzen technisch notwendige Mittel sowie – nur mit deiner Einwilligung – '
      + 'Marketing-Dienste (Google Ads, Meta) für Werbung und Conversion-Messung. '
      + 'Die anonyme Reichweitenmessung (Plausible) läuft cookielos und ohne deine Daten. '
      + 'Details in der <a href="/datenschutz.html">Datenschutzerklärung</a>.</p>'
      + '<div class="sz-cc-set" id="sz-cc-set">'
      + '  <div class="sz-cc-toggle"><span class="t-txt">Notwendig<small>Für den Betrieb der Seite erforderlich.</small></span><input type="checkbox" checked disabled></div>'
      + '  <div class="sz-cc-toggle"><span class="t-txt">Marketing<small>Google Ads &amp; Meta-Pixel (Werbung, Conversion-Tracking).</small></span><input type="checkbox" id="sz-cc-mkt"></div>'
      + '</div>'
      + '<div class="sz-cc-row">'
      + '  <button class="sz-cc-btn primary" id="sz-cc-all">Alle akzeptieren</button>'
      + '  <button class="sz-cc-btn" id="sz-cc-necessary">Nur notwendige</button>'
      + '  <button class="sz-cc-btn" id="sz-cc-settings">Einstellungen</button>'
      + '  <button class="sz-cc-btn" id="sz-cc-save" style="display:none">Auswahl speichern</button>'
      + '</div>'
      + '</div>';
    document.body.appendChild(wrap);
    bannerEl = wrap;

    document.getElementById("sz-cc-all").onclick = function () {
      var c = { marketing: true, ts: Date.now() };
      write(c); apply(c); close();
    };
    document.getElementById("sz-cc-necessary").onclick = function () {
      var c = { marketing: false, ts: Date.now() };
      write(c); close();
    };
    document.getElementById("sz-cc-settings").onclick = function () {
      var set = document.getElementById("sz-cc-set");
      set.classList.add("on");
      document.getElementById("sz-cc-save").style.display = "";
      var existing = read();
      document.getElementById("sz-cc-mkt").checked = !!(existing && existing.marketing);
    };
    document.getElementById("sz-cc-save").onclick = function () {
      var c = { marketing: document.getElementById("sz-cc-mkt").checked, ts: Date.now() };
      write(c); apply(c); close();
    };
  }

  function close() {
    if (bannerEl && bannerEl.parentNode) bannerEl.parentNode.removeChild(bannerEl);
    bannerEl = null;
  }

  function open() {
    if (bannerEl) return;
    if (document.body) buildBanner();
  }

  window.SeazonsConsent = { open: open, get: read };

  function init() {
    var c = read();
    if (c) { apply(c); }   // frühere Wahl anwenden, kein Banner
    else { open(); }       // erste Visite: Banner zeigen
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
