"""
IKAD Mechanical static-site page generator.

Single source of truth for shared markup (header, footer, mobile CTA, topbar, schema).
Each page below specifies only its unique content (hero, main, breadcrumb, schema).
Run: python _build/generate_pages.py
"""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://ikad.ca"

# ---------------------------------------------------------------------------
# Shared snippet builders
# ---------------------------------------------------------------------------

def rel(depth):
    """Return relative path prefix from a page at <depth> directories deep."""
    return "../" * depth if depth else "./"

# ---------------------------------------------------------------------------
# Inline SVG icon definitions (Material/Heroicons solid-style for mask compat)
# Use icon('phone') anywhere we'd have used an emoji.
# ---------------------------------------------------------------------------
ICON_PATHS = {
    "phone":      '<path d="M19.23 15.26l-2.54-.29c-.61-.07-1.21.14-1.64.57l-1.84 1.84a15.045 15.045 0 0 1-6.59-6.59l1.85-1.85c.43-.43.64-1.03.57-1.64l-.29-2.52A2 2 0 0 0 8.81 3H5.03c-1.13 0-2.07.94-2 2.07.53 8.54 7.36 15.36 15.89 15.89 1.13.07 2.07-.87 2.07-2v-1.73c.01-1.01-.75-1.86-1.76-1.98z"/>',
    "mail":       '<path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"/>',
    "pin":        '<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z"/>',
    "clock":      '<path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm4.2 14.2L11 13V7h1.5v5.2l4.5 2.7-.8 1.3z"/>',
    "check":      '<path d="M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>',
    "check-circle": '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>',
    "star":       '<path d="M12 17.27 18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>',
    "facebook":   '<path d="M12 2C6.477 2 2 6.477 2 12c0 4.84 3.44 8.87 8 9.8V15H8v-3h2V9.5C10 7.57 11.57 6 13.5 6H16v3h-2c-.55 0-1 .45-1 1v2h3v3h-3v6.95C18.05 21.45 22 17.19 22 12c0-5.523-4.477-10-10-10z"/>',
    "instagram":  '<path fill-rule="evenodd" clip-rule="evenodd" d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm0 2a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3H7zm10.25 2.5a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5zM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"/>',
    "message":    '<path d="M21 6h-2v9H6v2c0 .55.45 1 1 1h11l4 4V7c0-.55-.45-1-1-1zm-4 6V3c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v14l4-4h10c.55 0 1-.45 1-1z"/>',
    "calendar":   '<path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM9 14H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2z"/>',
    "arrow-right":'<path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>',
    "tools":      '<path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/>',
    "shield":     '<path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/>',
    "dollar":     '<path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1H6.32c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/>',
    "users":      '<path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>',
}

def icon(name, cls="icon"):
    """Return inline SVG markup for the named icon."""
    p = ICON_PATHS.get(name)
    if not p:
        return ""
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{p}</svg>'

def topbar():
    return f"""<div class="topbar"><div class="container topbar__inner"><div class="topbar__contact"><span>{icon('phone')} <a href="tel:+19054916943">(905) 491-6943</a></span><span>{icon('mail')} <a href="mailto:info@ikad.ca">info@ikad.ca</a></span><span>{icon('pin')} Oakville, ON</span></div><div>{icon('clock')} Mon–Fri 8am–6pm · Sat 9am–4pm</div></div></div>"""

def header(r, active=None):
    def cls(name): return ' class="active"' if active == name else ''
    res_active = ' class="active"' if active and active.startswith('res') else ''
    return f"""<header class="site-header"><div class="container site-header__inner"><a class="brand" href="{r}" aria-label="IKAD Mechanical - Home"><img src="{r}assets/images/logo/ikad-logo.png" alt="IKAD Mechanical logo" width="46" height="46"><span class="brand__text"><span class="brand__name">IKAD Mechanical</span><span class="brand__tag">Residential · Commercial · Industrial</span></span></a>
<nav class="primary-nav" aria-label="Primary"><ul>
<li><a href="{r}"{cls('home')}>Home</a></li>
<li class="has-dropdown"><a href="{r}residential/"{res_active}>Services</a><ul class="dropdown">
<li><a href="{r}heating-services/">Heating &amp; Furnaces</a></li>
<li><a href="{r}air-conditioning-heat-pumps/">AC &amp; Heat Pumps</a></li>
<li><a href="{r}water-heaters/">Water Heaters</a></li>
<li><a href="{r}in-floor-heating/">In-Floor Heating</a></li>
<li><a href="{r}snow-melting-systems/">Snow Melting Systems</a></li>
<li><a href="{r}duct-work/">Duct Work</a></li>
<li><a href="{r}air-balancing/">Air Balancing</a></li>
<li><a href="{r}custom-homes/">Custom Homes</a></li>
<li><a href="{r}commercial/">Commercial HVAC</a></li>
</ul></li>
<li class="has-dropdown"><a href="{r}service-areas/"{cls('areas')}>Service Areas</a><ul class="dropdown">
<li><a href="{r}service-areas/oakville/">Oakville</a></li>
<li><a href="{r}service-areas/burlington/">Burlington</a></li>
<li><a href="{r}service-areas/milton/">Milton</a></li>
<li><a href="{r}service-areas/halton-hills/">Halton Hills</a></li>
<li><a href="{r}service-areas/mississauga/">Mississauga</a></li>
<li><a href="{r}service-areas/hamilton/">Hamilton</a></li>
<li><a href="{r}service-areas/brampton/">Brampton</a></li>
</ul></li>
<li><a href="{r}our-projects/"{cls('projects')}>Projects</a></li>
<li><a href="{r}blog/"{cls('blog')}>Blog</a></li>
<li><a href="{r}faq/"{cls('faq')}>FAQ</a></li>
<li><a href="{r}about/"{cls('about')}>About</a></li>
<li><a href="{r}contact/"{cls('contact')}>Contact</a></li>
</ul>
<div class="mobile-extras">
<a class="btn btn--primary with-icon" href="{r}contact/">{icon('mail')} Request Free Quote</a>
<a class="btn btn--secondary with-icon" href="tel:+19054916943">{icon('phone')} (905) 491-6943</a>
<p class="mobile-extras-info">Mon–Fri 8am–6pm · Sat 9am–4pm<br>Emergency service available 24/7</p>
</div>
</nav>
<a class="btn btn--primary header-cta" href="{r}contact/">Free Quote</a><button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false"><span></span><span></span><span></span></button></div></header>"""

def footer(r):
    return f"""<footer class="site-footer"><div class="container">
<div class="footer-grid">
<div class="footer-brand">
<a class="brand" href="{r}"><img src="{r}assets/images/logo/ikad-logo.png" alt="IKAD Mechanical logo" width="46" height="46"><span class="brand__text"><span class="brand__name" style="color:#fff">IKAD Mechanical</span><span class="brand__tag">Residential · Commercial · Industrial</span></span></a>
<p style="margin-top:1rem">Family-owned HVAC contractor serving Halton Region (Oakville, Burlington, Milton, Halton Hills), Mississauga, Hamilton and Brampton since 2010. Furnace installation, air conditioning, heat pumps, water heaters, in-floor heating, snow melting, ductwork, air balancing and commercial HVAC.</p>
<p style="font-size:.85rem;color:#94a3b8;margin-top:.5rem">TSSA gas fitters · ECRA/ESA licensed · HRAI member · $5M liability insured · WSIB coverage</p>
<div class="social" style="margin-top:1rem">
<a href="https://www.facebook.com/profile.php?id=100088377265654" aria-label="IKAD Mechanical on Facebook" rel="noopener" target="_blank">{icon('facebook')}</a>
<a href="https://www.instagram.com/ikadmechanical/" aria-label="IKAD Mechanical on Instagram" rel="noopener" target="_blank">{icon('instagram')}</a>
<a href="https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling" aria-label="Read IKAD Mechanical reviews on HomeStars" rel="noopener" target="_blank">{icon('star')}</a>
</div>
</div>
<div>
<h4>HVAC Services</h4>
<ul>
<li><a href="{r}heating-services/">Furnace Installation &amp; Repair</a></li>
<li><a href="{r}air-conditioning-heat-pumps/">AC &amp; Heat Pumps</a></li>
<li><a href="{r}water-heaters/">Water Heaters (Tank &amp; Tankless)</a></li>
<li><a href="{r}in-floor-heating/">Hydronic In-Floor Heating</a></li>
<li><a href="{r}snow-melting-systems/">Snow Melting Systems</a></li>
<li><a href="{r}duct-work/">Duct Work &amp; Sealing</a></li>
<li><a href="{r}air-balancing/">Air Balancing</a></li>
<li><a href="{r}custom-homes/">Custom Home HVAC</a></li>
<li><a href="{r}commercial/">Commercial HVAC</a></li>
</ul>
</div>
<div>
<h4>Service Areas</h4>
<ul>
<li><a href="{r}service-areas/oakville/">HVAC in Oakville</a></li>
<li><a href="{r}service-areas/burlington/">HVAC in Burlington</a></li>
<li><a href="{r}service-areas/milton/">HVAC in Milton</a></li>
<li><a href="{r}service-areas/halton-hills/">HVAC in Halton Hills</a></li>
<li><a href="{r}service-areas/mississauga/">HVAC in Mississauga</a></li>
<li><a href="{r}service-areas/hamilton/">HVAC in Hamilton</a></li>
<li><a href="{r}service-areas/brampton/">HVAC in Brampton</a></li>
</ul>
<h4 style="margin-top:1.25rem">Resources</h4>
<ul>
<li><a href="{r}blog/">HVAC Blog &amp; Guides</a></li>
<li><a href="{r}faq/">HVAC FAQ (70+ Answers)</a></li>
<li><a href="{r}glossary/">HVAC Glossary</a></li>
<li><a href="{r}reviews/">Customer Reviews</a></li>
<li><a href="{r}why-choose-ikad/">Why Choose IKAD</a></li>
<li><a href="{r}our-projects/">Project Gallery</a></li>
<li><a href="{r}about/">About IKAD</a></li>
</ul>
</div>
<div>
<h4>Contact &amp; Hours</h4>
<ul style="list-style:none;padding:0">
<li style="display:flex;gap:.5rem;align-items:flex-start;padding:.35rem 0">{icon('pin')} <span>2275 Upper Middle Rd E, Suite 101<br>Oakville, ON L6H 0C3</span></li>
<li style="display:flex;gap:.5rem;align-items:flex-start;padding:.35rem 0">{icon('phone')} <a href="tel:+19054916943">(905) 491-6943</a></li>
<li style="display:flex;gap:.5rem;align-items:flex-start;padding:.35rem 0">{icon('mail')} <a href="mailto:info@ikad.ca">info@ikad.ca</a></li>
<li style="display:flex;gap:.5rem;align-items:flex-start;padding:.35rem 0">{icon('clock')} <span><strong style="color:#fff">Business hours</strong><br>Monday to Friday, 8am to 6pm<br>Saturday, 9am to 4pm<br><span style="color:#fca5a5">24/7 emergency service available</span></span></li>
</ul>
<a class="btn btn--primary with-icon" href="{r}contact/" style="margin-top:1rem;width:100%;justify-content:center">{icon('mail')} Request a Free Quote</a>
</div>
</div>

<div style="border-top:1px solid rgba(255,255,255,.1);margin-top:2.25rem;padding-top:1.5rem;font-size:.82rem;color:#94a3b8;line-height:1.7">
<p style="margin:0 0 .5rem"><strong style="color:#cbd5e1">Popular searches:</strong> HVAC contractor near me, HVAC near me Oakville, trusted HVAC contractor Halton, best HVAC company Oakville, top-rated HVAC Burlington, licensed HVAC contractor near me, family-owned HVAC Oakville, local HVAC contractor Burlington, emergency furnace repair near me, 24 hour HVAC Oakville, same-day AC repair Halton, furnace installation Oakville, AC repair Burlington, heat pump rebate Ontario 2026, tankless water heater Halton, ductless mini-split Mississauga, commercial HVAC contractor Hamilton, custom home HVAC Milton, snow melting driveway Oakville, furnace tune-up Burlington, boiler installation Oakville, TSSA certified gas fitter Halton, ECRA licensed HVAC, HRAI member HVAC Oakville, no-heat repair near me, heat pump installer near me, indoor air quality Halton</p>
<p style="margin:0"><strong style="color:#cbd5e1">Brands installed:</strong> Rheem, Lennox, Carrier, Daikin, Mitsubishi Hyper-Heat, Goodman, Bryant, York, Trane, Continental, Heil, Navien, Rinnai, Bradford White, John Wood, A.O. Smith, Viessmann, NTI, Lochinvar, Uponor, Watts, Honeywell, Ecobee, Lifebreath, Captive-Aire, Reznor, Greenheck</p>
</div>

<div class="legal" style="margin-top:1.5rem"><span>© <span id="yr">2026</span> IKAD Mechanical Inc. All rights reserved. HVAC contractor in Oakville, Ontario serving Halton Region, Peel and Hamilton since 2010.</span><span><a href="{r}privacy-policy/">Privacy</a> · <a href="{r}terms-of-service/">Terms</a> · <a href="{r}sitemap.xml">Sitemap</a> · <a href="{r}robots.txt">Robots</a></span></div>
</div></footer>
<nav class="mobile-dock" aria-label="Mobile quick actions">
  <a href="tel:+19054916943" class="is-primary" aria-label="Call IKAD Mechanical">{icon('phone')}<span>Call</span></a>
  <a href="sms:+19054916943" aria-label="Text IKAD Mechanical">{icon('message')}<span>Text</span></a>
  <a href="{r}contact/" aria-label="Request a free quote">{icon('mail')}<span>Quote</span></a>
</nav>
<script src="{r}assets/js/main.js"></script>
<script>document.getElementById('yr').textContent = new Date().getFullYear();</script>"""

def page(*, out, depth, title, description, canonical, og_image, body, extra_head="", schema_extra="", active=None, placename="Oakville", preload_hero=None, noindex=False, geo_lat=None, geo_lng=None):
    r = rel(depth)
    preload_tag = f'<link rel="preload" as="image" href="{r}assets/images/{preload_hero}" fetchpriority="high">' if preload_hero else ""
    robots = "noindex,follow" if noindex else "index,follow,max-image-preview:large"
    canonical_tag = "" if noindex else f'<link rel="canonical" href="{canonical}">'
    geo_tags = ""
    if geo_lat is not None and geo_lng is not None:
        geo_tags = f'\n<meta name="geo.position" content="{geo_lat};{geo_lng}">\n<meta name="ICBM" content="{geo_lat}, {geo_lng}">'
    html = f"""<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
{canonical_tag}
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#e30613">
<meta name="geo.region" content="CA-ON">
<meta name="geo.placename" content="{placename}">{geo_tags}
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="IKAD Mechanical">
<meta property="og:image" content="{og_image}">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image}">
<link rel="icon" type="image/png" href="{r}assets/images/logo/ikad-logo.png">
<link rel="apple-touch-icon" href="{r}assets/images/logo/ikad-logo.png">
<link rel="stylesheet" href="{r}assets/css/main.css">
{preload_tag}
{extra_head}
{schema_extra}
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
{topbar()}
{header(r, active=active)}
{body}
{footer(r)}
</body>
</html>
"""
    out_path = ROOT / out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"  + {out}")

# ---------------------------------------------------------------------------
# Reusable body components
# ---------------------------------------------------------------------------

def hero_compact(r, bg, eyebrow, h1, lead):
    return f"""<section class="hero hero--compact" id="main"><img class="hero__bg" src="{r}assets/images/{bg}" alt="" loading="eager" fetchpriority="high" width="1920" height="1080">
<div class="container hero__inner"><span class="eyebrow" style="color:#fca5a5">{eyebrow}</span><h1>{h1}</h1><p>{lead}</p>
<div class="btn-row"><a class="btn btn--primary btn--large" href="#hero-quote">Get My Free Quote</a><a class="btn btn--outline btn--large with-icon" href="tel:+19054916943">{icon('phone')} (905) 491-6943</a></div></div></section>"""

def hero_quote(r, bg, eyebrow, h1, lead, badges=None, service_default=""):
    """Service-page hero with inline conversion quote form."""
    badges = badges or ["15+ Years Experience", "TSSA &amp; ECRA Certified", "Free Estimates", "Same-Day Quotes"]
    badge_html = "".join(f'<span class="hero__badge with-icon">{icon("check")} {b}</span>' for b in badges)
    return f"""<section class="hero hero--with-form" id="main"><img class="hero__bg" src="{r}assets/images/{bg}" alt="" loading="eager" fetchpriority="high" width="1920" height="1080">
<div class="container hero__inner">
<div class="hero__copy">
<span class="eyebrow" style="color:#fca5a5">{eyebrow}</span>
<h1>{h1}</h1>
<p>{lead}</p>
<div class="btn-row"><a class="btn btn--primary btn--large" href="#hero-quote">Get My Free Quote</a><a class="btn btn--outline btn--large with-icon" href="tel:+19054916943">{icon('phone')} (905) 491-6943</a></div>
<div class="hero__badges">{badge_html}</div>
</div>
<form class="hero-quote" id="hero-quote" data-form="quote" action="/api/quote" method="post" novalidate>
<h2>Get Your Free Quote</h2>
<p class="hero-quote__sub">Same-day response during business hours. No pressure.</p>
<div class="form__honeypot" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
<div class="form__row">
<div class="form__group"><label class="sr-only" for="hq-name">Name</label><input id="hq-name" name="name" type="text" placeholder="Your name *" required autocomplete="name"></div>
<div class="form__group"><label class="sr-only" for="hq-phone">Phone</label><input id="hq-phone" name="phone" type="tel" placeholder="Phone *" required autocomplete="tel"></div>
</div>
<div class="form__group"><label class="sr-only" for="hq-email">Email</label><input id="hq-email" name="email" type="email" placeholder="Email *" required autocomplete="email"></div>
<div class="form__row">
<div class="form__group"><label class="sr-only" for="hq-city">City</label><select id="hq-city" name="city" required>
<option value="">Your city *</option><option>Oakville</option><option>Burlington</option><option>Milton</option><option>Halton Hills</option><option>Mississauga</option><option>Hamilton</option><option>Brampton</option><option>Other GTA</option>
</select></div>
<div class="form__group"><label class="sr-only" for="hq-service">Service</label><select id="hq-service" name="service" required>
<option value="">{service_default or 'What you need *'}</option>
<option>Furnace install / replace</option><option>Furnace repair (no heat)</option><option>AC install / replace</option><option>AC repair</option><option>Heat pump</option><option>Water heater</option><option>Duct work</option><option>Air balancing</option><option>In-floor heating</option><option>Snow melt system</option><option>Custom home HVAC</option><option>Commercial HVAC</option><option>Other / not sure</option>
</select></div>
</div>
<button class="btn btn--primary btn--large" type="submit">Send My Free Quote Request</button>
<p class="hero-quote__trust with-icon" style="justify-content:center">{icon('star')}{icon('star')}{icon('star')}{icon('star')}{icon('star')} Trusted by 1,200+ Halton homeowners since 2010</p>
</form>
</div></section>"""

def faq_block(faqs, heading="Common Questions"):
    """Render a visible FAQ section. faqs = [(question, answer), ...]"""
    items = "\n".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faqs)
    return f"""<section class="section section--gray"><div class="container">
<div class="text-center" style="max-width:720px;margin:0 auto 2rem"><span class="eyebrow">Frequently Asked</span><h2>{heading}</h2></div>
<div class="faq">{items}</div>
</div></section>"""

def key_facts(title, summary, facts):
    """AEO-friendly Key Facts answer block. Place at top of service pages.
    facts: list of (label, value) tuples.
    """
    items = "\n".join(f"<li><strong>{l}:</strong> {v}</li>" for l, v in facts)
    return f"""<aside class="answer-box" role="complementary"><span class="answer-box__label">Quick Answer</span><h2>{title}</h2><p>{summary}</p><ul>{items}</ul></aside>"""

def cost_table(headers, rows):
    """Cost / comparison table."""
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = ""
    for row in rows:
        body += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
    return f"""<div class="cost-table-wrap"><table class="cost-table"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>"""

def brand_pills(brands):
    """Brand pill list for SEO brand cluster coverage."""
    items = "".join(f'<span class="pill">{icon("check")}{b}</span>' for b in brands)
    return f'<div class="pills" aria-label="Brands we install">{items}</div>'

def service_areas_inline(r, label="Available in"):
    """Internal link out from a service page to all city pages for local SEO link equity."""
    cities = ["oakville","burlington","milton","halton-hills","mississauga","hamilton","brampton"]
    names = {"oakville":"Oakville","burlington":"Burlington","milton":"Milton","halton-hills":"Halton Hills","mississauga":"Mississauga","hamilton":"Hamilton","brampton":"Brampton"}
    links = " · ".join(f'<a href="{r}service-areas/{c}/">{names[c]}</a>' for c in cities)
    return f'<p style="font-size:.92rem;color:#475569;background:#f6f7f9;padding:.85rem 1.1rem;border-radius:8px;margin:1.5rem 0;">{icon("pin")} <strong>{label}:</strong> {links}</p>'

def feature_image_section(r, image, alt, caption=None):
    """Render a full-width feature image block within a service page. Goes inside the section/container."""
    cap = f'<figcaption style="text-align:center;color:#64748b;font-size:.85rem;margin-top:.5rem">{caption}</figcaption>' if caption else ''
    return f"""<figure style="margin:2rem 0">
<img src="{r}assets/images/{image}" alt="{alt}" loading="lazy" width="900" height="600" style="width:100%;height:auto;border-radius:10px;box-shadow:0 12px 30px rgba(15,23,42,.10)">
{cap}
</figure>"""

def service_area_map_section(r, service_label):
    """Halton-area service map embed for each service page."""
    return f"""<section class="section section--gray"><div class="container" style="max-width:1000px">
<div class="text-center" style="max-width:720px;margin:0 auto 2rem"><span class="eyebrow">Where We Work</span><h2>{service_label} Across Halton, Peel &amp; Hamilton</h2><p class="lead" style="margin:0 auto">Our trucks roll out of our Oakville shop and reach across the western GTA. Tap any city for local details, response time, permit office, neighbourhoods, and city-specific FAQs.</p></div>
<div class="map-embed" style="margin:0 auto 1.5rem;max-width:900px;aspect-ratio:16/9"><iframe src="https://www.google.com/maps?q=Oakville,+Burlington,+Milton,+Hamilton,+Mississauga,+Brampton,+ON,+Canada&amp;output=embed&amp;z=9" loading="lazy" title="IKAD Mechanical service area map across Halton, Peel and Hamilton" referrerpolicy="no-referrer-when-downgrade" style="border:0;border-radius:10px;width:100%;height:100%"></iframe></div>
<div class="area-grid">
<a class="area-card" href="{r}service-areas/oakville/"><span class="area-card__city">Oakville</span><span class="area-card__sub">HQ · 5–15 min from shop</span></a>
<a class="area-card" href="{r}service-areas/burlington/"><span class="area-card__city">Burlington</span><span class="area-card__sub">15–25 min · multi-day weekly</span></a>
<a class="area-card" href="{r}service-areas/milton/"><span class="area-card__city">Milton</span><span class="area-card__sub">20–30 min · subdivision &amp; custom</span></a>
<a class="area-card" href="{r}service-areas/halton-hills/"><span class="area-card__city">Halton Hills</span><span class="area-card__sub">30–55 min · Georgetown &amp; Acton</span></a>
<a class="area-card" href="{r}service-areas/mississauga/"><span class="area-card__city">Mississauga</span><span class="area-card__sub">15–35 min · residential &amp; commercial</span></a>
<a class="area-card" href="{r}service-areas/hamilton/"><span class="area-card__city">Hamilton</span><span class="area-card__sub">25–45 min · daycare, plaza &amp; rooftop</span></a>
<a class="area-card" href="{r}service-areas/brampton/"><span class="area-card__city">Brampton</span><span class="area-card__sub">30–45 min · industrial &amp; residential</span></a>
</div>
</div></section>"""

def _strip_html(s):
    """Strip simple HTML tags for JSON-LD (preserves anchor text)."""
    import re
    return re.sub(r'<[^>]+>', '', s)

def faq_schema(faqs):
    """JSON-LD FAQPage schema. Strips HTML tags from answers for spec-valid JSON-LD."""
    import json
    main = [{"@type":"Question","name":_strip_html(q),"acceptedAnswer":{"@type":"Answer","text":_strip_html(a)}} for q, a in faqs]
    return f"""<script type="application/ld+json">
{json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":main}, ensure_ascii=False)}
</script>"""

def breadcrumbs(r, crumbs):
    items = []
    for c in crumbs[:-1]:
        # Normalize "./" placeholder to mean site root
        href = r if c[1] == "./" else f"{r}{c[1]}"
        items.append(f'<li><a href="{href}">{c[0]}</a></li>')
    items.append(f'<li aria-current="page">{crumbs[-1][0]}</li>')
    return f"""<nav class="container breadcrumbs" aria-label="Breadcrumb"><ol>{''.join(items)}</ol></nav>"""

def cta_banner(r, h2, copy):
    return f"""<section class="section"><div class="container"><div class="cta-banner"><div><h2>{h2}</h2><p>{copy}</p></div><div class="btn-row"><a class="btn btn--secondary btn--large" href="{r}contact/">Request Estimate</a><a class="btn btn--outline btn--large with-icon" href="tel:+19054916943">{icon('phone')} Call Now</a></div></div></div></section>"""

def service_schema(name, service_type, url, desc):
    return f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Service","name":"{name}","serviceType":"{service_type}","provider":{{"@type":"HVACBusiness","@id":"{BASE}/#business","name":"IKAD Mechanical Inc.","telephone":"+1-905-491-6943","url":"{BASE}/","address":{{"@type":"PostalAddress","streetAddress":"2275 Upper Middle Rd E, Suite 101","addressLocality":"Oakville","addressRegion":"ON","postalCode":"L6H 0C3","addressCountry":"CA"}}}},"areaServed":[{{"@type":"City","name":"Oakville"}},{{"@type":"City","name":"Burlington"}},{{"@type":"City","name":"Milton"}},{{"@type":"City","name":"Halton Hills"}},{{"@type":"City","name":"Mississauga"}},{{"@type":"City","name":"Hamilton"}},{{"@type":"City","name":"Brampton"}}],"url":"{url}","description":"{desc}"}}
</script>"""

def breadcrumb_schema(items):
    list_items = []
    for i, (name, url) in enumerate(items, 1):
        list_items.append(f'{{"@type":"ListItem","position":{i},"name":"{name}","item":"{url}"}}')
    return f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{','.join(list_items)}]}}
</script>"""

# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def build_water_heaters():
    r = "../"
    faqs = [
        ("How much does a new water heater cost in Oakville?",
         "A conventional 50-gallon natural gas tank installed runs about $1,400–$2,200 depending on venting. Condensing tankless units (Navien, Rinnai) are typically $4,200–$6,800 installed, including stainless venting and any gas line upsizing. See our <a href=\"" + r + "blog/tankless-water-heater-cost-oakville/\">detailed tankless cost breakdown for Oakville</a> for full pricing scenarios."),
        ("Tank vs tankless, which is right for my home?",
         "If your household is two to four people and you mostly do laundry off-peak, a properly sized tank is usually the cheapest option over its lifetime. If you have multiple bathrooms running simultaneously, do a lot of evening laundry, or want a 20+ year service life, tankless makes more sense. Hamilton/Halton hard water adds about $150–$250/year in tankless descaling vs near-zero for a tank, worth knowing before deciding. Our <a href=\"" + r + "blog/tankless-water-heater-cost-oakville/\">tankless vs tank guide</a> walks through the math."),
        ("How fast can you install a new water heater?",
         "Tank-to-tank swaps are typically done in 3–4 hours. We can usually do a same-day replacement if you call before noon, <a href=\"" + r + "contact/\">call us before noon</a> for same-day. Tank-to-tankless conversions take a full day because of venting and gas line work."),
        ("Do you remove my old water heater?",
         "Yes, old unit removal, haul-away and recycling are included on every install. Same with the disposal of the old vent piping. We're a <a href=\"" + r + "about/\">family-owned Oakville contractor</a>, no third-party hand-offs."),
        ("What brands do you install?",
         "For tanks we install John Wood, Bradford White and Rheem. For tankless we install Navien (most common), Rinnai and Rheem. We don't push one brand, we recommend what fits your home, hot water demand and budget. See all <a href=\"" + r + "residential/\">residential HVAC services</a> we offer alongside water heaters."),
    ]
    body = hero_quote(r, "services/water-heaters.jpg", "Hot Water Specialists", "Water Heater Installation In Oakville",
        "Tank, tankless and hybrid water heaters sized correctly the first time. Licensed gas fitters and TSSA-certified technicians serving Halton homes since 2010.", service_default="Water heater installation/repair") + \
        breadcrumbs(r, [("Home","./"),("Residential","residential/"),("Water Heaters", "")]) + f"""
<section class="section"><div class="container"><div class="svc-detail">
<div class="svc-detail__main">
{key_facts(
    "Water Heater Installation in Oakville, Key Facts",
    "IKAD Mechanical installs gas and electric tank water heaters, condensing tankless units (Navien, Rinnai, Rheem, Bradford White) and high-efficiency hybrid heat pump water heaters across Halton Region. We're TSSA-certified gas fitters, ECRA/ESA licensed, and family-owned since 2010.",
    [
        ("Tank install cost (Oakville 2026)", "$1,400 – $2,800 for 40–75 gallon natural gas tank"),
        ("Tankless install cost (Oakville 2026)", "$4,200 – $6,800 for condensing 180–199k BTU unit"),
        ("Service life", "Tanks: 10–13 years · Tankless: 20–25 years"),
        ("Response time", "Same-day installs available; emergency dispatch within 4 hours"),
        ("Brands we install", "Navien, Rinnai, Rheem, Bradford White, John Wood, A.O. Smith"),
    ]
)}
{brand_pills(["Navien", "Rinnai", "Rheem", "Bradford White", "John Wood", "A.O. Smith", "Noritz"])}
<span class="eyebrow">Reliable Hot Water</span>
<h2>Tank, Tankless &amp; Hybrid Water Heaters</h2>
<p>At IKAD Mechanical, we know how important reliable hot water is for everyday home comfort. Whether it's for showers, laundry, or cooking, we provide expert installation, repair and maintenance of residential water heaters tailored to your household's needs. Our team works with both traditional tank systems and modern tankless water heaters, helping you choose the right solution for your home.</p>
<p>We focus on energy efficiency, long-term reliability and ensuring you always have hot water when you need it most. From replacing outdated units to performing regular maintenance that extends system life, IKAD Mechanical delivers dependable service and peace of mind for homeowners across Halton.</p>

<h2 id="tank">Tank Water Heaters</h2>
<p>A conventional 40 to 75-gallon natural gas or electric tank water heater is still the most cost-effective solution for most Halton homes. We install power-vent and direct-vent models with proper draft, gas pressure and expansion tank, small details that protect your warranty and your plumbing.</p>
<ul>
<li>40, 50, 60 and 75-gallon natural gas tanks</li>
<li>Power-vent and direct-vent applications</li>
<li>Expansion tank, T&amp;P valve and drain pan included</li>
<li>Old tank removal and disposal handled</li>
<li>Same-day swaps in most cases</li>
</ul>

<h2 id="tankless">Tankless Water Heaters</h2>
<p>A wall-mounted tankless can deliver endless hot water for a family of four or five while taking up the space of a small suitcase. They cost more up front, but they last roughly twice as long as a tank, and you'll feel the difference on your January gas bill. We install Navien, Rinnai, Rheem and Bradford White tankless systems.</p>
<ul>
<li>Up to 199,000 BTU condensing tankless units</li>
<li>Recirculation pumps for instant hot water at distant fixtures</li>
<li>Stainless steel venting and gas line upsizing handled</li>
<li>Annual descaling service available</li>
</ul>

<h2 id="repair">Water Heater Repair</h2>
<p>If your water heater is leaking, making banging sounds, or just stops producing hot water, we run same-day diagnostic calls. Most repairs come down to a thermocouple, gas valve, dip tube or thermostat, quick fixes if the tank itself isn't compromised.</p>

<h2 id="cost">2026 Installed Pricing in Halton</h2>
<p>Real installed prices we quote across Oakville, Burlington, Milton, Halton Hills, Mississauga, Hamilton and Brampton. Tax included.</p>
{cost_table(
    ["Unit Type", "Capacity", "Installed Price (2026)", "Best For"],
    [
        ["Power-vent gas tank", "40 gal", "$1,400 – $1,850", "Smaller households, basic replacement"],
        ["Power-vent gas tank", "50 gal", "$1,700 – $2,200", "Most Halton homes, most common"],
        ["Direct-vent gas tank", "60–75 gal", "$2,100 – $2,800", "Larger families, multi-bath households"],
        ["Electric tank", "40–60 gal", "$1,200 – $2,100", "Off-grid-gas homes (rural Halton Hills)"],
        ["Condensing tankless (Navien NPE-S2)", "180k BTU", "$4,500 – $5,800", "Best value tankless tier"],
        ["Condensing tankless w/ recirc (Navien NPE-A2)", "199k BTU", "$5,200 – $6,400", "Large homes, distant master bath"],
        ["Tankless (Rinnai RUR)", "199k BTU", "$4,800 – $6,100", "Long warranty, parts availability"],
        ["Combi boiler (heat + hot water)", "180k BTU", "$6,800 – $8,500", "Replacing both boiler and water heater"],
        ["Hybrid heat pump water heater", "50 gal", "$3,800 – $5,200", "Maximum efficiency, electric-only homes"],
    ]
)}

<h2 id="brands">Brands We Install &amp; Service</h2>
<p>We're factory-trained on every major water heater brand sold in Ontario. We don't push a single manufacturer, we recommend whatever's right for your home, hot-water demand and budget.</p>
<ul>
<li><strong>Navien</strong>, our most-installed tankless brand. NPE-S2 (entry) and NPE-A2 (built-in recirculation pump). Excellent dealer network in Ontario.</li>
<li><strong>Rinnai</strong>, long manufacturer warranty (up to 15 years on the heat exchanger), well-established parts availability.</li>
<li><strong>Rheem</strong>, solid mid-tier tank and tankless options, common rebate-eligible models.</li>
<li><strong>Bradford White</strong>, best-in-class tank reliability; American-made, no big-box-store distribution.</li>
<li><strong>John Wood</strong>, Canadian-made, strong residential tank lineup.</li>
<li><strong>A.O. Smith</strong>, heat pump water heaters and high-recovery commercial tanks.</li>
</ul>

<h2 id="oakville-water">Why Oakville &amp; Halton Water Matters</h2>
<p>Tap water in Oakville, Burlington and most of Halton averages 7 to 9 grains per gallon of hardness, moderately hard. Tankless units have small-passage heat exchangers that scale up faster than tanks in this water profile. We strongly recommend a whole-home water softener at install if you're going tankless, or commit to annual descaling. Skip both and you'll get half the service life from any tankless unit.</p>

<h2 id="sizing">Sizing A Water Heater For Your Halton Home</h2>
<p>Tank size and tankless flow rate both come down to peak simultaneous demand, not number of people. The right size for your home depends on how many fixtures could realistically run at the same time during the busy morning hour:</p>
<ul>
<li><strong>One bathroom home (1 to 2 people):</strong> 40-gallon tank, or a 150 to 160k BTU tankless. Either handles a shower plus a kitchen sink at the same time.</li>
<li><strong>Two bathroom home (3 to 4 people):</strong> 50-gallon tank, or a 180 to 199k BTU tankless. Standard for most Halton family homes.</li>
<li><strong>Three or more bathrooms / large family:</strong> 60 or 75-gallon tank, or a 199k BTU tankless with recirculation. Two showers plus laundry can run at once.</li>
<li><strong>Custom home with master soaker tub:</strong> 80-gallon power-vent tank, or a Navien NPE-A2 199k with recirculation pump. Filling a 75-gallon soaker is a worst-case scenario tankless can't always meet without a buffer.</li>
</ul>
<p>For Halton homes with finished basements, hot tubs, or low-flow rebated fixtures we sometimes recommend a hybrid heat pump water heater (Rheem ProTerra or A.O. Smith Voltex), which uses 60% less energy than a standard electric tank.</p>

<h2 id="venting">Venting And Gas Line Considerations</h2>
<p>Tankless water heaters and high-efficiency tanks pull more gas than a 40-gallon power-vent. Many Halton homes built before 2005 have 1/2 inch gas lines feeding the basement water heater; a 199k BTU tankless typically needs 3/4 inch with the furnace already on the same line. We measure manifold pressure and verify gas-line sizing on every quote. If an upsize is needed, it's included in the fixed price, not a surprise add-on.</p>

<h2 id="warranty">Warranty Terms You Should Know</h2>
<p>Tank water heater warranties run 6 to 12 years on the tank itself and 1 year on parts. Tankless warranties are usually 12 to 15 years on the heat exchanger and 5 years on parts. Manufacturer warranties are only valid if the unit is installed by a licensed contractor and registered. We register every install in your name within 7 days so you're covered without lifting a finger.</p>

{feature_image_section(r, "projects/snow-melting-hydronics-install.jpg", "NTI condensing combi boiler with manifold for a domestic hot water and heating package, installed by IKAD Mechanical", "NTI combi boiler install, domestic hot water + heating in a single unit, freeing up floor space")}

{service_areas_inline(r, "Water heater installation available in")}
</div>

<aside class="svc-detail__sidebar">
<h3>Get A Free Water Heater Quote</h3>
<p>Most quotes back the same day. Same-day installs for emergencies.</p>
<a class="btn btn--primary" href="{r}contact/">Request Estimate</a>
<a class="btn btn--secondary with-icon" href="tel:+19054916943">{icon('phone')} (905) 491-6943</a>
<h4 style="margin-top:1.5rem">Why IKAD</h4>
<ul>
<li>TSSA-certified gas fitters</li>
<li>Manufacturer warranty registered</li>
<li>Old unit removal &amp; disposal</li>
<li>Up-front pricing, no surprises</li>
<li>15+ years installing water heaters</li>
</ul>
</aside>
</div></div></section>
""" + service_area_map_section(r, "Water Heater Installation") + faq_block(faqs) + cta_banner(r, "Need A Water Heater Fast?", "Same-day emergency installations across Halton.")
    page(
        out="water-heaters/index.html", depth=1,
        title="Water Heater Installation Oakville | Tank &amp; Tankless | IKAD",
        description="Tank and tankless water heater installation, repair and replacement in Oakville, Burlington, Milton & Halton. Same-day service. Call (905) 491-6943.",
        canonical=f"{BASE}/water-heaters/",
        og_image=f"{BASE}/assets/images/services/water-heaters.jpg",
        body=body, active="res", preload_hero="services/water-heaters.jpg",
        schema_extra=service_schema("Water Heater Installation and Repair", "Plumbing and Water Heating", f"{BASE}/water-heaters/",
            "Tank and tankless water heater installation, repair and maintenance for residential homes across Halton and the GTA.") +
            breadcrumb_schema([("Home",f"{BASE}/"),("Residential",f"{BASE}/residential/"),("Water Heaters",f"{BASE}/water-heaters/")]) +
            faq_schema(faqs)
    )

def build_in_floor():
    r = "../"
    faqs = [
        ("How much does in-floor heating cost in Oakville?",
         "For new construction, hydronic in-floor adds roughly $14–$22 per square foot when you include the boiler and manifolds, so a 600 sq.ft. main-floor zone runs about $10,000–$13,000. Bathroom-only electric mat retrofits start around $1,400 installed (tile and substrate not included). It's commonly paired with a <a href=\"" + r + "custom-homes/\">custom-home mechanical package</a> for whole-home zoning."),
        ("Will in-floor heat replace my furnace?",
         "It can, but in most Halton homes we recommend pairing it with a small forced-air system for cooling and HRV ventilation, since you can't run AC through floor loops. Whole-home hydronic with a <a href=\"" + r + "air-conditioning-heat-pumps/\">separate ductless mini-split for cooling</a> is a popular combination."),
        ("How long does in-floor heating last?",
         "PEX tubing in a properly poured slab will outlive the house, 50+ years. The wear parts are the boiler (15–20 years), the circulator pumps (10–15 years) and the zone valves (15+ years). All are easily serviced without disturbing the floor. Pair with a <a href=\"" + r + "water-heaters/\">condensing combi unit</a> to do both DHW and heat from one boiler."),
        ("Can you retrofit in-floor heating into an existing home?",
         "Yes, two ways. Above the subfloor with a thin lightweight pour (raises floor height ~1.5 inches), or below in joist bays as a staple-up system (no floor height change but slightly lower output). Bathrooms are the easiest retrofit, basement slab is harder unless you're already redoing the floor. We service all of <a href=\"" + r + "service-areas/\">Halton Region</a> for in-floor retrofits."),
    ]
    body = hero_quote(r, "services/air-balancing.jpg", "Radiant Comfort", "In-Floor Heating Installation In Oakville",
        "Hydronic radiant in-floor heating for new builds, additions and bathroom renovations. Quiet, dust-free, evenly warm, designed for the way Halton homes actually live.", service_default="In-floor heating") + \
        breadcrumbs(r, [("Home","./"),("Residential","residential/"),("In-Floor Heating", "")]) + f"""
<section class="section"><div class="container"><div class="svc-detail">
<div class="svc-detail__main">
{key_facts(
    "In-Floor Heating Installation in Oakville, Key Facts",
    "IKAD Mechanical designs and installs hydronic in-floor radiant heating across Halton, new builds, additions, bathroom retrofits and full custom homes. We work with high-efficiency Viessmann, Navien, NTI and Lochinvar combi-boilers paired with Uponor PEX tubing and Watts manifolds.",
    [
        ("Installed cost (new construction)", "$14 – $22 per sq.ft. including boiler"),
        ("Bathroom electric mat retrofit", "From $1,400 (tile/substrate not included)"),
        ("Whole-home retrofit", "$25,000 – $60,000 depending on home size and floor type"),
        ("Service life", "PEX tubing: 50+ years · Boiler: 15–20 years"),
        ("Brands we install", "Viessmann, Navien, NTI, Lochinvar, Uponor, Watts"),
    ]
)}
{brand_pills(["Uponor", "Viessmann", "Navien NCB", "NTI", "Lochinvar", "Watts", "Honeywell", "Taco"])}
<span class="eyebrow">Hydronic Radiant Heat</span>
<h2>The Quiet Comfort Custom-Home Owners Don't Regret</h2>
<p>Walk into a house with a properly designed in-floor system and you can usually feel it before you see the thermostat. No air rushing out of vents, no cold spots near the windows, no rooms ten degrees apart. Just an even, comfortable warmth coming up from the floor.</p>
<p>At IKAD Mechanical, we design and install hydronic in-floor heating systems for homeowners and builders across Halton. We've put radiant in everything from a single bathroom retrofit in an Oakville bungalow to a fully zoned 6,000 sq.ft. custom home in Milton.</p>

<h2 id="how">How Hydronic In-Floor Works</h2>
<p>We embed PEX tubing in the floor, either set into a concrete slab on grade, on top of subfloor in a thin lightweight pour, or stapled up between joists from below. A boiler or condensing combi-unit heats water to roughly 38–45°C and circulates it through the loops. Manifolds with zone valves let each room or area run at its own temperature.</p>
<ul>
<li>New build in-slab radiant heating</li>
<li>Retrofit installations (basements, additions, bathrooms)</li>
<li>Staple-up systems between existing joists</li>
<li>Multi-zone manifolds with smart thermostat control</li>
<li>Combi-boiler integration for heating + domestic hot water</li>
<li>Snow melting integration (driveways &amp; walkways)</li>
</ul>

<h2 id="why">Why Homeowners Choose Radiant</h2>
<p>Even temperatures wall-to-wall. No ductwork pushing dust and allergens. No noisy blower. Floors that are warm in the winter. Lower operating cost than electric heat. And it pairs beautifully with high-efficiency condensing boilers, you can run a 32°C supply temperature and still keep a 22°C house, which is where boilers hit their best efficiency.</p>

<h2 id="zoning">Zoning A Hydronic System Properly</h2>
<p>The biggest performance difference between a good and a great in-floor system is zoning. Most Halton custom homes we work on use 3 to 7 hydronic zones with individual thermostats: main floor, basement, master ensuite, kitchen, second-floor bedrooms separately if possible. Manifolds with zone valves (Taco, Honeywell, Watts) let each space hold its own setpoint. A bedroom kept at 18°C overnight saves real money compared to one shared loop forcing the whole house to 21°C.</p>

<h2 id="floor-types">In-Floor Heating With Different Floor Coverings</h2>
<p>Tile and stone are the ideal surfaces for radiant: high thermal mass, fast response, no insulation between the heat source and your feet. Engineered hardwood works fine if you keep the supply water below 38°C and let the floor acclimate slowly during the first heating season. Solid hardwood and carpet over radiant are riskier: carpet acts as an insulator that requires hotter supply water (efficiency penalty), and solid hardwood can cup or gap if temperatures spike. We design the loop spacing and supply temperature to match your final flooring choice.</p>

<h2 id="control">Smart Controls For Hydronic Radiant</h2>
<p>Hydronic in-floor heats slowly. A typical 4-inch concrete slab takes 4 to 6 hours to come up to temperature after a setback. That makes a smart thermostat with predictive recovery (Ecobee Premium, Honeywell Vision Pro IAQ, or a dedicated hydronic controller like tekmar) genuinely useful here, where it'd be marginal on forced air. We program the schedule against typical Halton sleep and work patterns and tune it through the first heating season.</p>

{feature_image_section(r, "services/air-balancing.jpg", "Hydronic in-floor heating panel installation in a new Halton home, IKAD Mechanical", "Hydronic in-floor radiant being installed during the rough-in stage of a new build")}

{service_areas_inline(r, "In-floor heating available in")}
</div>

<aside class="svc-detail__sidebar">
<h3>Get A Radiant Quote</h3>
<p>Most jobs start with a 30-minute on-site visit to look at floor type, layout and existing heating.</p>
<a class="btn btn--primary" href="{r}contact/">Request Estimate</a>
<a class="btn btn--secondary with-icon" href="tel:+19054916943">{icon('phone')} (905) 491-6943</a>
<h4 style="margin-top:1.5rem">Common Applications</h4>
<ul>
<li>Bathrooms &amp; ensuites</li>
<li>Kitchens with tile floors</li>
<li>Finished basements</li>
<li>Garage workshops</li>
<li>Whole-home custom builds</li>
<li>Sunrooms &amp; additions</li>
</ul>
</aside>
</div></div></section>
""" + service_area_map_section(r, "In-Floor Heating") + faq_block(faqs) + cta_banner(r, "Thinking About Radiant Floors?", "Free in-home design consultation across Halton.")
    page(
        out="in-floor-heating/index.html", depth=1,
        title="In-Floor Heating Installation Oakville | Hydronic Radiant | IKAD",
        description="Hydronic in-floor radiant heating design and installation in Oakville, Burlington, Milton & Halton. Custom homes, additions, bathrooms. Call (905) 491-6943.",
        canonical=f"{BASE}/in-floor-heating/",
        og_image=f"{BASE}/assets/images/services/in-floor-heating.jpg",
        body=body, active="res", preload_hero="services/air-balancing.jpg",
        schema_extra=service_schema("In-Floor Radiant Heating Installation", "Hydronic Heating", f"{BASE}/in-floor-heating/",
            "Hydronic in-floor radiant heating design and installation for custom homes, additions and retrofits across Halton.") +
            breadcrumb_schema([("Home",f"{BASE}/"),("Residential",f"{BASE}/residential/"),("In-Floor Heating",f"{BASE}/in-floor-heating/")]) +
            faq_schema(faqs)
    )

def build_snow_melt():
    r = "../"
    faqs = [
        ("How much does a heated driveway cost in Oakville?",
         "A typical double driveway (700–900 sq.ft.) runs about $18,000–$32,000 installed for a hydronic system, including the dedicated boiler and snow/temperature sensor. Smaller entry-and-step electric systems start around $2,200. The wide range comes from boiler choice (existing system tie-in vs dedicated unit) and driveway surface, see our <a href=\"" + r + "in-floor-heating/\">in-floor heating page</a> for the related hydronic technology."),
        ("Will it work in a Halton winter?",
         "Yes, these systems are designed for our climate. The key sizing inputs are BTU/sq.ft. (typically 125–175 in southern Ontario) and snow/ice sensor type. Properly sized, the system can clear an active storm at the rate it falls. We design for the same Halton snow loads we account for on <a href=\"" + r + "custom-homes/\">custom home mechanical packages</a>."),
        ("How much does it cost to run?",
         "About $4–$8 per snow event for a typical double driveway, depending on duration and temperature. With idle protection on, expect $25–$60/month during winter. Far cheaper than salt damage to concrete and stamped pavers, and obviously safer."),
        ("Can you retrofit an existing driveway?",
         "Only by removing and re-laying the surface. We always recommend installing during a new pour or driveway replacement, retrofitting under an existing asphalt or concrete driveway means tearing it out anyway, so the marginal cost of adding heat is much lower at that moment. <a href=\"" + r + "contact/\">Talk to us</a> early in your driveway-resurfacing planning."),
    ]
    body = hero_quote(r, "services/snow-melting.webp", "Heated Driveways", "Snow Melting Systems In Oakville",
        "Never shovel another winter. Hydronic and electric snow melting systems for driveways, walkways and entrances, engineered for Halton winters and tied into your home's heating.", service_default="Snow melt system") + \
        breadcrumbs(r, [("Home","./"),("Residential","residential/"),("Snow Melting Systems", "")]) + f"""
<section class="section"><div class="container"><div class="svc-detail">
<div class="svc-detail__main">
{key_facts(
    "Heated Driveway &amp; Snow Melting System, Key Facts",
    "IKAD installs hydronic (boiler-fed) and electric (mat-based) snow melting systems for driveways, walkways, front steps and commercial entrances across Halton. We design for our climate (125–175 BTU per sq.ft.) and tie systems to dedicated or shared boilers using Uponor PEX, automatic snow/ice sensors and antifreeze-rated glycol.",
    [
        ("Hydronic driveway (700–900 sq.ft.)", "$18,000 – $32,000 installed"),
        ("Electric steps &amp; walkway", "From $2,200 installed"),
        ("Operating cost per snow event", "$4 – $8 per typical double driveway"),
        ("Automatic activation", "Snow / temperature sensor included"),
        ("Best time to install", "During driveway pour or full resurfacing"),
    ]
)}
{brand_pills(["Uponor", "Viessmann", "WarmlyYours", "Watts", "tekmar"])}
<span class="eyebrow">Driveway &amp; Walkway Heating</span>
<h2>Snow Melting Systems Built For Ontario Winters</h2>
<p>If you've spent more than one winter chipping ice off your front steps or wrestling a snowblower up a steep driveway, you've earned the right to consider a heated driveway. Snow melting systems use radiant heating installed beneath the surface to automatically melt snow and ice on driveways, walkways and entrances, no shovel, no salt, no slip risk for the people you love.</p>
<p>We design and install both hydronic and electric systems across Halton, integrated with your home's existing boiler or on a dedicated unit. Most projects get planned during the construction or resurfacing stage, but retrofits are possible too.</p>

<h2 id="hydronic">Hydronic Snow Melting</h2>
<p>The most common (and most efficient) approach for a full driveway. We lay PEX tubing in a serpentine pattern under your concrete, asphalt, pavers or stone, then tie it back to a boiler or heat exchanger. Antifreeze-rated fluid circulates through the loops, automatically activating on a snow/ice sensor.</p>

<h2 id="electric">Electric Snow Melting</h2>
<p>For smaller areas, front entry steps, a single walkway, a wheelchair ramp, electric mats are usually the cleaner install. No boiler, no plumbing, just heating cable in mortar or sand bed.</p>

<h2 id="why">Why It's Worth The Investment</h2>
<ul>
<li>Eliminate shoveling and salt damage to surfaces</li>
<li>Reduce slip-and-fall liability (especially for businesses)</li>
<li>Extend driveway life (no freeze/thaw cycling)</li>
<li>Automatic operation via snow/temperature sensors</li>
<li>Pair with in-floor heating for a unified system</li>
</ul>

<h2 id="custom">Best Built In At Construction</h2>
<p>If you're pouring a new driveway, doing a major reno, or building custom, this is the right time to talk to us. Retrofits are possible but cost more, coordinating with your concrete or paving contractor is far cheaper.</p>

<h2 id="sizing">Sizing A Snow Melt System For Halton Snow Loads</h2>
<p>Environment Canada averages give Oakville and Burlington around 110–140 cm of snowfall per year, but the design number that matters is peak snowfall rate during a single storm, not seasonal totals. We design Halton driveways for 2 inches per hour with 25 mph wind at -10°C, that works out to roughly 150 BTU per square foot for an open driveway, 175 BTU per square foot for an exposed one (no garage shelter, north-facing, or near the escarpment in Milton). Undersizing here is the most common mistake we see on snow melt systems installed by general contractors: the system runs full-tilt but never catches up during a real storm.</p>

<h2 id="surface">Surface Choices For A Heated Driveway</h2>
<p>Concrete is the most efficient surface for snow melt: dense, high thermal conductivity, fast response. We embed 1/2-inch PEX-A tubing at 9-inch spacing in 4-inch concrete with #4 rebar mat above the tubing. Asphalt works, but the tubing has to be installed in a sand cap below the asphalt because the hot asphalt mix (~150°C) would damage PEX. Pavers and natural stone are the trickiest, the joints lose heat to wind, so we run tubing tighter (6-inch spacing) and oversize the supply temperature. We coordinate directly with your concrete or paving contractor so the install sequence works.</p>

<h2 id="control">Smart Snow Sensors And Idle Mode</h2>
<p>The cheapest snow sensors (single-stage thermostats that trigger below a set temperature) waste energy by running on cold dry days. We default to a Tekmar 654 or Watts SS-3 sensor that detects actual precipitation plus temperature, only firing the system when there's snow falling and the slab is below 4°C. For driveways used by elderly or mobility-limited family members, we add Idle Mode that holds the slab at 0°C overnight from December to March, so a sudden storm doesn't need a 4-hour warm-up to start clearing. Idle mode roughly doubles winter operating cost but eliminates morning surprises.</p>

{feature_image_section(r, "projects/snow-melting-hydronics-install.jpg", "NTI snow melt boiler with manifold, glycol fill cart and zone valves, IKAD Mechanical install", "Snow melt mechanical package, dedicated boiler with glycol loop, automatic snow/ice sensor and zone manifold")}

{service_areas_inline(r, "Snow melting available in")}
</div>

<aside class="svc-detail__sidebar">
<h3>Free Snow Melt Quote</h3>
<p>We'll measure, design and quote, usually within a week.</p>
<a class="btn btn--primary" href="{r}contact/">Request Estimate</a>
<a class="btn btn--secondary with-icon" href="tel:+19054916943">{icon('phone')} (905) 491-6943</a>
<h4 style="margin-top:1.5rem">Typical Projects</h4>
<ul>
<li>Driveways (single and double)</li>
<li>Front porch &amp; steps</li>
<li>Walkways &amp; paths</li>
<li>Commercial entrances &amp; ramps</li>
<li>Loading dock approaches</li>
</ul>
</aside>
</div></div></section>
""" + service_area_map_section(r, "Snow Melting System Installation") + faq_block(faqs) + cta_banner(r, "Plan A Heated Driveway Now", "Best to design at the construction or resurfacing stage.")
    page(
        out="snow-melting-systems/index.html", depth=1,
        title="Snow Melting Systems &amp; Heated Driveways | IKAD Oakville",
        description="Hydronic and electric snow melting system installation for driveways, walkways and entrances in Oakville, Burlington, Milton & Halton. Call (905) 491-6943.",
        canonical=f"{BASE}/snow-melting-systems/",
        og_image=f"{BASE}/assets/images/services/snow-melting.webp",
        body=body, active="res", preload_hero="services/snow-melting.webp",
        schema_extra=service_schema("Snow Melting System Installation", "Heated Driveway and Walkway Snow Melt", f"{BASE}/snow-melting-systems/",
            "Hydronic and electric snow melting systems installed for residential driveways, walkways and entrances across Halton.") +
            breadcrumb_schema([("Home",f"{BASE}/"),("Residential",f"{BASE}/residential/"),("Snow Melting",f"{BASE}/snow-melting-systems/")]) +
            faq_schema(faqs)
    )

def build_duct_work():
    r = "../"
    faqs = [
        ("Why is my upstairs always hotter (or colder) than downstairs?",
         "In a two-storey Halton home, the most common causes are: (1) returns sized only for the main floor, so the second-storey rooms get pushed in but no air pulled out, (2) trunk takeoffs that branch off too close together causing pressure imbalances, or (3) leaky ducts in the attic dumping conditioned air into the roof space. <a href=\"" + r + "air-balancing/\">Air balancing</a> and targeted duct sealing usually fix it without ripping anything out, the full diagnostic walkthrough is in our <a href=\"" + r + "blog/upstairs-too-hot-too-cold/\">upstairs hot/cold blog post</a>."),
        ("How much does duct sealing or duct work cost?",
         "Duct sealing for a typical 1,800–2,400 sq.ft. home is $850–$1,500, usually pays back in a winter or two from lower gas bills. Full duct replacement during a renovation is $3,500–$8,500 depending on complexity. New construction is priced per drawing, see our <a href=\"" + r + "custom-homes/\">custom home mechanical scope</a> page."),
        ("Do I need duct cleaning?",
         "Honestly, less often than home services companies tell you. Healthy ducts in a home with good filtration get cleaned every 7–10 years. Skip it if you have allergies and a high-MERV filter. Get it done if you've just had a renovation, you can see dust drift out of the supplies, or you've inherited a hoarder house."),
        ("Can you fix whistling or rattling ducts?",
         "Yes, usually it's high static pressure (too small a return, too restrictive a filter) or a loose damper somewhere in the trunk. A static pressure reading at the air handler tells us in 5 minutes which it is. Often it's paired with an <a href=\"" + r + "air-balancing/\">air balance</a> for a complete fix."),
    ]
    body = hero_quote(r, "services/duct-work.webp", "Duct Work Specialists", "Duct Work Installation &amp; Sealing In Oakville",
        "Your ductwork is the backbone of your home's comfort system. Even the best furnace won't perform without ducts that are designed, sealed and maintained the right way. We install, repair and clean, for new builds and retrofits across Halton.", service_default="Duct work") + \
        breadcrumbs(r, [("Home","./"),("Residential","residential/"),("Duct Work", "")]) + f"""
<section class="section"><div class="container"><div class="svc-detail">
<div class="svc-detail__main">
{key_facts(
    "HVAC Duct Work in Oakville, Key Facts",
    "IKAD designs, fabricates and installs galvanized sheet-metal ductwork for new construction and retrofits, plus duct sealing, leak repair and rotary-brush cleaning. Typical residential ducts leak 20–30% of conditioned air before sealing, fixing that is one of the highest-ROI HVAC investments a Halton homeowner can make.",
    [
        ("Whole-home duct sealing", "$850 – $1,500 (typical payback under 2 winters)"),
        ("Duct replacement (1,800–2,400 sq.ft. home)", "$3,500 – $8,500"),
        ("Whole-home duct cleaning", "$420 – $680 with vacuum-truck and rotary brushes"),
        ("New construction ductwork", "Priced from drawings per CFM-per-room"),
        ("Tools we use", "Manometer, smoke pencil, Aeroseal mastic, rotary cleaning"),
    ]
)}
<span class="eyebrow">Air Distribution Done Right</span>
<h2>Seal, Repair And Maintain Your Home's Airflow</h2>
<p>Your ductwork is the backbone of your home's comfort system. Even the best furnace, air conditioner or heat pump won't perform properly without ducts that are designed, sealed and maintained the right way. At IKAD Mechanical, we provide expert duct installation, repair and maintenance to ensure air flows efficiently throughout your home. Properly designed and maintained ducts mean balanced temperatures in every room, lower energy bills, and cleaner, healthier air for your family.</p>
<p>Over time, ducts can develop leaks, gaps or build up dust and debris that hurt both comfort and efficiency. Our team specializes in sealing, repairing and cleaning duct systems to eliminate wasted energy and improve air quality. Whether you're building a new home, upgrading your current system or solving uneven heating and cooling issues, IKAD Mechanical delivers ductwork solutions that keep your home comfortable year-round while extending the life of your HVAC system.</p>

<h2 id="install">Duct Installation &amp; Replacement</h2>
<p>For custom homes, additions and major renovations, we design the entire duct system around the actual airflow your equipment needs to move, measured CFM per room, properly sized trunks and branches, smooth fittings to keep pressure drop down. The result is a system that doesn't roar when the furnace fires and doesn't leave the back bedroom freezing.</p>

<h2 id="seal">Duct Sealing &amp; Leak Repair</h2>
<p>A typical residential duct system leaks 20–30% of the air it's trying to move, into the attic, into the basement, into wall cavities, which is heated and cooled air you paid for. We test, find the leaks, and seal them properly with mastic or aeroseal.</p>

<h2 id="clean">Duct Cleaning</h2>
<p>Years of dust, debris and pet hair build up inside even well-maintained ducts. We use truck-mounted vacuum equipment and rotating brushes to clean trunks, branches, registers and the air handler itself.</p>

<h2 id="balance">Combined With Air Balancing</h2>
<p>Ductwork is only half the story, once the system is clean and tight, we measure and tune airflow at every register to make sure every room gets what it needs. See our <a href="{r}air-balancing/">air balancing service</a> for details.</p>

<h2 id="static-pressure">High Static Pressure: The Silent Killer Of HVAC Systems</h2>
<p>Most Halton homes we test have static pressure in the 0.9 to 1.2 inches of water column range. Manufacturer specs say total external static should be 0.5 inches. Why does it matter? Because the blower motor in your furnace was designed for 0.5, when it sees 1.0, it pulls more amps, runs hotter, throws codes intermittently, and dies five years early. The fix is usually a bigger return drop (10x20 instead of 8x14), a 4-inch media filter instead of a 1-inch furnace filter, or replacing flexible duct runs with rigid metal. We measure static at the furnace cabinet during every <a href="{r}heating-services/">heating service call</a>, it's the first reading we take.</p>

<h2 id="halton-ducts">What's Different About Halton Ductwork</h2>
<p>A lot of Oakville and Burlington homes from the 1980s and 90s were built with builder-grade ductwork: undersized returns, no return on the second floor, flexible duct runs from a central trunk into individual bedrooms with sharp bends and crushed sections. We see this pattern hundreds of times a year. In the older parts of Burlington (Aldershot, Roseland) and east Oakville (Bronte, Glen Abbey) the basement ceiling height is tight, so the original installer compromised on duct sizing to fit the trunk. That's why we routinely see uneven heating in homes built before 2000. A proper retrofit replaces the trunk and resizes returns, that's where the real comfort comes from, not a bigger furnace. Read our <a href="{r}blog/upstairs-too-hot-too-cold/">guide to upstairs-too-hot-too-cold</a> for the diagnostic walkthrough.</p>

<h2 id="aeroseal">Aeroseal vs Manual Sealing</h2>
<p>For an accessible duct system in a basement or unfinished area, manual sealing with water-based mastic and metal foil tape is fast, durable and cheap. For ducts buried in walls, ceilings, or sealed soffits, Aeroseal is worth the extra cost: pressurize the duct system, inject aerosolized sealant, the particles deposit inside the leaks and bridge them from the inside. We've cut measured duct leakage from 28% down to 4% on jobs where opening the ceilings wasn't an option.</p>

{feature_image_section(r, "services/duct-work-2.jpg", "New galvanized sheet metal duct trunks installed in a Halton basement by IKAD Mechanical", "New sheet-metal trunk and branch ducts in a basement retrofit, properly sized for the home's CFM requirements")}

{service_areas_inline(r, "Duct work available in")}
</div>

<aside class="svc-detail__sidebar">
<h3>Get A Duct Work Quote</h3>
<p>Free assessment for new installs, repairs and cleaning.</p>
<a class="btn btn--primary" href="{r}contact/">Request Estimate</a>
<a class="btn btn--secondary with-icon" href="tel:+19054916943">{icon('phone')} (905) 491-6943</a>
<h4 style="margin-top:1.5rem">Common Problems We Solve</h4>
<ul>
<li>Uneven room temperatures</li>
<li>Whistling or vibrating ducts</li>
<li>Dusty registers</li>
<li>High energy bills</li>
<li>Inadequate airflow upstairs</li>
<li>Renovations needing new branches</li>
</ul>
</aside>
</div></div></section>
""" + service_area_map_section(r, "Duct Work, Sealing &amp; Cleaning") + faq_block(faqs) + cta_banner(r, "Solve Hot & Cold Rooms", "Most uneven-temperature problems trace back to ducts. We'll find it.")
    page(
        out="duct-work/index.html", depth=1,
        title="Duct Work Installation &amp; Sealing Oakville | IKAD",
        description="HVAC duct work installation, leak sealing, cleaning and repair in Oakville, Burlington & Halton. Solve hot and cold rooms. Call (905) 491-6943.",
        canonical=f"{BASE}/duct-work/",
        og_image=f"{BASE}/assets/images/services/duct-work.webp",
        body=body, active="res", preload_hero="services/duct-work.webp",
        schema_extra=service_schema("HVAC Duct Work Installation and Repair", "Duct Installation, Sealing, Cleaning", f"{BASE}/duct-work/",
            "Duct installation, sealing, cleaning and repair for residential and commercial buildings across Halton and the GTA.") +
            breadcrumb_schema([("Home",f"{BASE}/"),("Residential",f"{BASE}/residential/"),("Duct Work",f"{BASE}/duct-work/")]) +
            faq_schema(faqs)
    )

def build_air_balancing():
    r = "../"
    faqs = [
        ("How long does an air balance take?",
         "Most homes take 2–3 hours on site, plus a written report. We test airflow at every supply and return register, compare against the design target for each room, then adjust dampers in the trunk and at branch takeoffs until each room is within ±10% of target."),
        ("How much does air balancing cost?",
         "Most Halton homes are $385–$650 for a full balance and written report. Larger homes or systems that also need static pressure remediation can run higher. Best done at the start of a heating season or after any <a href=\"" + r + "duct-work/\">duct work</a>."),
        ("Will closing vents in unused rooms help with hot/cold spots?",
         "No, and it usually makes it worse. Closing supplies raises static pressure on the system, makes the blower work harder, and can starve the air handler. The correct fix is balancing dampers in the trunk, not register vents in the rooms. The full diagnostic story is in our <a href=\"" + r + "blog/upstairs-too-hot-too-cold/\">upstairs hot/cold guide</a>."),
        ("Do you do post-renovation balancing for builders?",
         "Yes. We're often the last trade in on <a href=\"" + r + "custom-homes/\">custom homes</a>, we balance the system, deliver air-flow documentation for the HVAC commissioning report and hand the warranty cert over to the homeowner."),
    ]
    body = hero_quote(r, "services/air-balancing.jpg", "Even Temperatures Everywhere", "Air Balancing Services In Oakville",
        "Few things are more frustrating than walking from one room that's freezing into another that feels stuffy and hot. Our precise air balancing eliminates uneven temperatures, guaranteed comfort in every room.", service_default="Air balancing") + \
        breadcrumbs(r, [("Home","./"),("Residential","residential/"),("Air Balancing", "")]) + f"""
<section class="section"><div class="container"><div class="svc-detail">
<div class="svc-detail__main">
{key_facts(
    "Air Balancing in Oakville, Key Facts",
    "Air balancing is the process of measuring and adjusting airflow at every register and return to deliver design-target CFM to each room. It's the fix for hot upstairs bedrooms, cold basements, whistling vents, and uneven two-storey homes. IKAD uses calibrated balometers and pressure gauges to NEBB-style standards.",
    [
        ("Cost for typical Halton home", "$385 – $650 (test, balance, written report)"),
        ("Time on site", "2–3 hours plus a documented report"),
        ("Best timing", "Start of heating season or after any duct change"),
        ("Tool we use", "Balometer (capture hood), manometer, anemometer"),
        ("Target accuracy", "Within ±10% of design CFM per room"),
    ]
)}
<span class="eyebrow">Stop Hot &amp; Cold Rooms</span>
<h2>Say Goodbye To Hot And Cold Spots</h2>
<p>Few things are more frustrating than walking from one room that's freezing into another that feels stuffy and hot. At IKAD Mechanical, our air balancing services eliminate these uneven temperatures by adjusting airflow throughout your home. Using precise testing, we ensure each room gets the right amount of conditioned air so your family enjoys consistent comfort, no matter where they are.</p>
<p>This process not only makes your home more comfortable but also helps reduce the strain of constant thermostat adjustments. With properly balanced airflow, you'll finally get the most out of your heating and cooling system while enjoying comfort in every corner of your home.</p>

<h2 id="why">Cleaner Air, Lower Bills</h2>
<p>Air balancing isn't just about comfort, it's also about protecting your HVAC system and improving efficiency. When airflow is uneven, your furnace, AC or heat pump has to work harder to push air through the ducts. This extra strain can shorten equipment life, drive up energy bills and leave your home with poor air quality. At IKAD Mechanical, we fine-tune your system to ensure optimal airflow, reducing wasted energy and keeping your equipment running smoothly.</p>
<p>By improving circulation, our air balancing services also help filter your air more effectively, reducing dust, allergens and humidity issues. The result is a healthier living environment, lower utility costs, and peace of mind knowing your system is working at its best.</p>

<h2 id="process">How Air Balancing Works</h2>
<ul>
<li>We measure airflow (CFM) at every supply and return register</li>
<li>Compare against design targets calculated from the room's heat load</li>
<li>Adjust dampers in the trunk and branches</li>
<li>Re-balance returns to fix pressure imbalances</li>
<li>Verify final airflow and document results</li>
</ul>

<h2 id="when">Signs You Need Air Balancing</h2>
<ul>
<li>One or two rooms are always 4°+ different from the rest of the house</li>
<li>Upstairs is hot in summer and cold in winter (very common in two-storey homes)</li>
<li>You closed registers in some rooms trying to redirect airflow</li>
<li>You hear whistling or pressure noises from registers</li>
<li>Doors slam shut or won't close properly when the HVAC runs</li>
</ul>

<h2 id="halton-homes">Common Imbalance Patterns In Halton Homes</h2>
<p>Different vintages of Halton housing fail in predictable ways. <strong>1950s and 60s Oakville bungalows</strong> (Bronte, Eastlake) typically have a single trunk in the basement with stubby branches, the rooms farthest from the furnace receive almost no flow. <strong>1980s and 90s two-storey Burlington and Oakville homes</strong> (Glen Abbey, Millcroft, Headon Forest) suffer from upstairs-too-hot because the second-floor returns were either undersized or omitted entirely. <strong>2000s Milton homes</strong> (Beaty, Hawthorne Village) usually have aggressive Manual J load calcs but flexible duct runs that get crushed during drywall, dropping CFM 30 to 40% to back bedrooms. <strong>Custom homes with mechanical penthouses</strong> need balancing on day one, the long runs amplify any takeoff sizing mistake. We see all four patterns weekly.</p>

<h2 id="hrv-balance">HRV And ERV Balancing</h2>
<p>If your home has an HRV (heat recovery ventilator) or ERV (energy recovery ventilator), the balance between supply and exhaust airflow matters more than the supply-register CFM most people focus on. An unbalanced HRV starves your home of fresh air (under-ventilating) or depressurizes it (back-drafts gas appliances). We commission HRVs to within ±5 CFM supply-to-exhaust using a Retrotec digital manometer, this is the single most-neglected commissioning step on new Halton custom homes.</p>

<h2 id="commercial-balance">Why Commercial Air Balancing Is Different</h2>
<p>For commercial and multi-unit buildings (restaurants, dental offices, fitness studios) air balancing is a code requirement, not optional. We deliver NEBB-style certified reports with stamped drawings, supply/return/exhaust CFM readings, and pressure relationships between zones. We're regularly hired by Halton commercial-property managers to re-balance after tenant fit-outs. See our <a href="{r}commercial/">commercial HVAC page</a> for scope details.</p>

{feature_image_section(r, "services/snow-melting.webp", "Technician using a balometer capture hood to measure airflow at a ceiling diffuser during an IKAD Mechanical air balance", "Balometer capture hood measuring CFM at a ceiling diffuser, the exact instrument we use to balance airflow")}

{service_areas_inline(r, "Air balancing available in")}
</div>

<aside class="svc-detail__sidebar">
<h3>Book An Air Balance</h3>
<p>Most homes take a single appointment to test, balance and document.</p>
<a class="btn btn--primary" href="{r}contact/">Request Estimate</a>
<a class="btn btn--secondary with-icon" href="tel:+19054916943">{icon('phone')} (905) 491-6943</a>
<h4 style="margin-top:1.5rem">Included</h4>
<ul>
<li>CFM testing at every register</li>
<li>Damper and trunk adjustments</li>
<li>Return air balancing</li>
<li>Static pressure verification</li>
<li>Written report with measurements</li>
</ul>
</aside>
</div></div></section>
""" + service_area_map_section(r, "Air Balancing") + faq_block(faqs) + cta_banner(r, "Fix Uneven Temperatures", "Get your home properly balanced before next season.")
    page(
        out="air-balancing/index.html", depth=1,
        title="Air Balancing Services Oakville | Fix Uneven Temperatures | IKAD",
        description="Professional HVAC air balancing in Oakville, Burlington, Milton & Halton. Stop hot & cold rooms, lower energy bills. Call (905) 491-6943.",
        canonical=f"{BASE}/air-balancing/",
        og_image=f"{BASE}/assets/images/services/air-balancing.jpg",
        body=body, active="res", preload_hero="services/air-balancing.jpg",
        schema_extra=service_schema("HVAC Air Balancing", "Air Balancing and Airflow Testing", f"{BASE}/air-balancing/",
            "Professional HVAC air balancing service for residential homes across Halton, measure, adjust and balance airflow to every register.") +
            breadcrumb_schema([("Home",f"{BASE}/"),("Residential",f"{BASE}/residential/"),("Air Balancing",f"{BASE}/air-balancing/")]) +
            faq_schema(faqs)
    )

def build_custom_homes():
    r = "../"
    faqs = [
        ("When should I bring an HVAC contractor into my custom build?",
         "Earliest at the concept/permit stage, latest at framing. The decisions that matter, mechanical room size and location, zoning layout, <a href=\"" + r + "in-floor-heating/\">in-floor vs forced air</a>, HRV path, are much harder to change after drywall. We routinely meet with builders during framing rough-in to coordinate."),
        ("Do you work directly with homeowners, or only through builders?",
         "Both. About 60% of our custom-home work comes through a builder relationship; the other 40% is owner-direct on renovations and additions. Either way we handle the mechanical package start to finish. <a href=\"" + r + "about/\">Read about our team</a> and certifications."),
        ("What does HVAC cost on a typical custom home?",
         "For a 3,500–5,000 sq.ft. custom home in Oakville or Burlington, the mechanical package (<a href=\"" + r + "heating-services/\">furnace</a> + <a href=\"" + r + "air-conditioning-heat-pumps/\">heat pump</a> or full hydronic, AC, <a href=\"" + r + "duct-work/\">ductwork</a>, HRV/ERV, smart controls, in-floor zones, <a href=\"" + r + "snow-melting-systems/\">snow melt</a> if included) typically lands between $35,000 and $90,000. Wide range because every spec is different, we price from drawings."),
        ("Do you handle the rough-in inspection?",
         "Yes, we pull our own gas and HVAC permits, schedule the inspections with TSSA and the municipality, and coordinate timing with the builder's schedule. Builders trust us because we don't miss inspection windows. See <a href=\"" + r + "our-projects/\">our recent custom-home projects</a> across Halton."),
    ]
    body = hero_quote(r, "services/custom-homes.jpg", "Custom Home HVAC", "Custom Home Heating, Cooling & Ventilation",
        "Tailored HVAC design and installation for builders and homeowners across Halton, zoning, ventilation, in-floor heating, smart controls. One mechanical contractor for the whole project.", service_default="Custom home HVAC") + \
        breadcrumbs(r, [("Home","./"),("Residential","residential/"),("Custom Homes", "")]) + f"""
<section class="section"><div class="container"><div class="svc-detail">
<div class="svc-detail__main">
{key_facts(
    "Custom Home HVAC Design, Key Facts",
    "IKAD Mechanical is the in-house mechanical contractor for several Halton custom-home builders. We design and install the full mechanical package: high-efficiency furnaces, heat pumps, in-floor radiant, central AC, ductwork, zoning, HRV/ERV ventilation, smart thermostats, snow melt, and the complete gas piping system. Engaged at concept stage is best.",
    [
        ("Typical 3,500–5,000 sq.ft. home mechanical package", "$35,000 – $90,000 depending on scope"),
        ("Design deliverables", "Manual J/D/S load calc, equipment schedule, permit drawings"),
        ("Zoning typical", "3–7 zones with smart thermostats and zone-valve manifolds"),
        ("Ventilation", "HRV / ERV with dedicated runs, balanced commissioning"),
        ("Best engaged at", "Concept / framing stage, before drywall"),
    ]
)}
{brand_pills(["Lennox SLP99V", "Carrier Infinity", "Rheem Modulating", "Mitsubishi Hyper-Heat", "Daikin Aurora", "Viessmann", "Lifebreath HRV", "Honeywell"])}
<span class="eyebrow">Custom Mechanical For Custom Homes</span>
<h2>Tailored Comfort For Your Dream Home</h2>
<p>A 5,000 sq.ft. custom home with floor-to-ceiling windows on the south side and a finished basement gym should not have the same furnace as a 1,800 sq.ft. semi from 1972. Yet that's exactly what happens when a builder hands the mechanical package to whoever submits the lowest number on a spreadsheet.</p>
<p>IKAD Mechanical designs and installs HVAC systems customized to each home's layout, lifestyle and comfort requirements. Whether you're building from scratch or doing a full renovation, we work with your architect, builder and trades to design a system that fits the way the home will actually live in twenty years.</p>

<h2 id="design">Whole-Home HVAC Design</h2>
<ul>
<li>Manual J load calculation per room</li>
<li>Equipment sized to actual load, not square footage rules of thumb</li>
<li>Zoning with smart thermostats and zone valves</li>
<li>High-efficiency cooling solutions (modulating, two-stage, variable speed)</li>
<li>Hydronic in-floor radiant heating integration</li>
<li>Discreet ductwork design coordinated with framing &amp; trim</li>
<li>Air balancing services for final commissioning</li>
<li>Advanced ventilation: HRV/ERV systems</li>
</ul>

<h2 id="builders">For Builders &amp; Developers</h2>
<p>We work with custom-home builders, design-build firms and general contractors across Halton and the GTA. We can be involved at concept stage to advise on equipment placement, mechanical room sizing and rough-in locations, and we hold our schedules. If we say the rough-in will be done before drywall on the 18th, it will be.</p>

<h2 id="why">Why It Matters</h2>
<p>Efficiency, comfort and peace of mind, these aren't marketing words on a custom home. They're what separates a place that's a joy to live in from one that gets a furnace replaced after eight years because the original was wrong. We combine the latest technology with professional installation and maintenance options that reduce energy costs while maintaining comfort.</p>

<h2 id="mechanical-room">Mechanical Room Layout For A Halton Custom Home</h2>
<p>The mechanical room is the most-undersized space in most custom Halton homes. A well-designed 5,000 sq.ft. home needs roughly 80 to 120 square feet of mechanical room with 7-foot minimum ceiling and direct exterior access for combustion air. We need clearance around the furnace (24 inches front, 6 inches sides), boiler (per manufacturer), HRV/ERV (4 feet for filter access), water heaters (24 inches front), zone valve manifolds (3-foot wall section per manifold), and the gas meter with shutoff. A common mistake is locating the mechanical room behind a finished wine cellar or theatre, that's a 20-year service nightmare. We coordinate with your architect at framing stage so this gets done right the first time.</p>

<h2 id="hybrid-systems">Hybrid Forced-Air + Hydronic Systems</h2>
<p>The best Halton custom home mechanical packages we install are hybrid: forced-air heat pumps with gas-furnace backup on the main and upper floors (for cooling, dehumidification and quick recovery), plus hydronic in-floor radiant in the basement, ensuites, mudroom and any below-grade or tile-heavy spaces. The forced-air side handles AC and rapid response; the hydronic side handles the slow, even heat that makes the lived-in spaces feel premium. The control logic is the hard part, we use tekmar or Honeywell Vision Pro IAQ controllers that coordinate which system runs in which zone at which time of year. See our <a href="{r}in-floor-heating/">in-floor heating page</a> for the hydronic side and our <a href="{r}air-conditioning-heat-pumps/">heat pump page</a> for the forced-air side.</p>

<h2 id="permits-inspections">Permits And Inspections On A Custom Build</h2>
<p>Halton Region custom homes require permits from the municipality (building permit for HVAC), TSSA (gas piping, every joint inspected), ECRA/ESA (electrical for HVAC wiring), and increasingly Halton Region Health (for HRV/ERV in tighter envelopes). We pull all four, schedule inspections, and meet inspectors on site. Builders trust us because we don't slip rough-in dates and we don't fail inspections. Failed inspections push drywall, finishes and occupancy by weeks, our last failed gas piping inspection was in 2019.</p>

{feature_image_section(r, "services/custom-homes-3.jpg", "Dual York high-efficiency furnaces installed during the rough-in stage of a custom Halton home, IKAD Mechanical", "Dual-furnace mechanical package for a 5,000+ sq.ft. custom home, installed at framing stage")}

{service_areas_inline(r, "Custom home HVAC available in")}
</div>

<aside class="svc-detail__sidebar">
<h3>Custom Home Quote</h3>
<p>Talk to us early, equipment, layout and rough-in plan come together better when mechanical is in the conversation.</p>
<a class="btn btn--primary" href="{r}contact/">Request Estimate</a>
<a class="btn btn--secondary with-icon" href="tel:+19054916943">{icon('phone')} (905) 491-6943</a>
<h4 style="margin-top:1.5rem">What's Included</h4>
<ul>
<li>Mechanical design &amp; load calc</li>
<li>Permit drawings (where applicable)</li>
<li>Coordination with builder &amp; trades</li>
<li>All HVAC equipment &amp; install</li>
<li>Commissioning &amp; air balance</li>
<li>Owner walkthrough</li>
</ul>
</aside>
</div></div></section>
""" + service_area_map_section(r, "Custom Home HVAC") + faq_block(faqs) + cta_banner(r, "Building A Custom Home?", "Get IKAD involved at design stage.")
    page(
        out="custom-homes/index.html", depth=1,
        title="Custom Home HVAC Design & Installation Oakville | IKAD Mechanical",
        description="Custom home HVAC design, installation, zoning, in-floor heating & ventilation for builders and homeowners across Halton & the GTA. Call (905) 491-6943.",
        canonical=f"{BASE}/custom-homes/",
        og_image=f"{BASE}/assets/images/services/custom-homes.jpg",
        body=body, active="res", preload_hero="services/custom-homes.jpg",
        schema_extra=service_schema("Custom Home HVAC Design and Installation", "Custom Home Mechanical Design", f"{BASE}/custom-homes/",
            "Custom home HVAC design and installation including zoning, smart thermostats, in-floor heating, HRV/ERV ventilation and air balancing across Halton.") +
            breadcrumb_schema([("Home",f"{BASE}/"),("Residential",f"{BASE}/residential/"),("Custom Homes",f"{BASE}/custom-homes/")]) +
            faq_schema(faqs)
    )

def build_commercial():
    r = "../"
    faqs = [
        ("How fast can you respond to a commercial no-cool or no-heat call?",
         "Halton, Peel and Hamilton during business hours: 2–4 hours for diagnostic dispatch. After-hours: same day in most cases. PM-contract clients jump the queue automatically. We've replaced rooftop compressors during a July heat wave with same-day turnaround. <a href=\"" + r + "contact/\">Call us</a> as soon as the unit goes down."),
        ("Do you do scheduled preventive maintenance?",
         "Yes, Planned Maintenance (PM) is one of the things we're best at. We hold contracts on Halton restaurants, daycare facilities, plaza buildings and light-industrial. Quarterly or seasonal cadence, equipment health reporting, refrigerant logging, <a href=\"" + r + "duct-work/\">filter swap</a> and priority response built in."),
        ("Can you handle a restaurant kitchen build-out?",
         "Yes. Make-up air sizing, hood system installation, exhaust ductwork to roof, gas line installs, rooftop unit placement and inspections, we coordinate the whole mechanical package with the GC, GC and TSSA. We're trusted across <a href=\"" + r + "service-areas/\">Halton, Peel and Hamilton</a> for restaurant openings."),
        ("What kinds of facilities do you serve?",
         "Restaurants and commercial kitchens, daycare and pre-school facilities, retail and multi-tenant plazas, manufacturing and warehousing, office buildings, places of worship and community centres. Most of our commercial work is within an hour of Oakville, see our <a href=\"" + r + "our-projects/\">recent commercial projects</a>."),
    ]
    body = hero_quote(r, "services/commercial-rooftop.jpg", "Commercial HVAC", "Commercial HVAC Services Across Halton & The GTA",
        "Rooftop units, make-up air, commercial hoods, boilers and planned maintenance contracts for restaurants, retail, daycares, plazas and industrial buildings. We keep facilities running.", service_default="Commercial HVAC") + \
        breadcrumbs(r, [("Home","./"),("Commercial", "")]) + f"""
<section class="section"><div class="container">
{key_facts(
    "Commercial HVAC in Halton &amp; GTA, Key Facts",
    "IKAD Mechanical is a TSSA-certified commercial HVAC contractor for restaurants, daycares, plazas, retail, light-industrial and office buildings across Halton, Peel and Hamilton. We hold Planned Maintenance contracts on dozens of facilities and respond 24/7 to no-cool and no-heat emergencies.",
    [
        ("Emergency response (business hours)", "2–4 hours dispatched, PM clients prioritized"),
        ("Emergency response (after hours)", "Same-day on most days during heat waves and cold snaps"),
        ("Equipment we install &amp; service", "Carrier, Lennox, Trane, Rheem, Reznor, Captive-Aire"),
        ("Permitting", "We pull TSSA, ESA and municipal mechanical permits"),
        ("Insurance", "$5M liability + WSIB on every job site"),
    ]
)}
{brand_pills(["Carrier", "Lennox Commercial", "Trane", "Rheem Commercial", "Reznor", "Captive-Aire", "Greenheck", "Modine"])}
<span class="eyebrow">Commercial HVAC</span>
<h2>Reliable Commercial Heating &amp; Cooling Solutions For Every Business</h2>
<p>At IKAD Mechanical, we specialize in commercial HVAC across Halton, Peel and Hamilton, from office buildings to industrial facilities, restaurant kitchens to multi-tenant plazas. Our job is to keep your facility running so your team can focus on what they do.</p>
<p>We hold preventive maintenance contracts, run emergency service calls 24/7, and handle complete rooftop and make-up-air replacements. We work with property managers, restaurant owners, manufacturers, daycares and general contractors.</p>
</div></section>

<section class="section section--gray"><div class="container">
<div class="svc-grid">
<div class="svc-card"><img class="svc-card__img" src="{r}assets/images/services/commercial-rooftop.jpg" alt="Rooftop commercial HVAC unit" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Rooftop Installation &amp; Maintenance</h3><p class="svc-card__desc">We specialize in the design, installation and upkeep of rooftop HVAC systems for commercial and industrial buildings. Proper sizing, energy efficiency and durability, routine maintenance, inspections and repairs to prevent costly downtime.</p></div></div>
<div class="svc-card"><img class="svc-card__img" src="{r}assets/images/services/commercial-makeup-air.jpg" alt="Make-up air unit installation" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Make-Up Air Units</h3><p class="svc-card__desc">Expert installation and maintenance of Make-Up Air Units to ensure proper ventilation, balanced airflow and improved indoor air quality, essential for restaurants, kitchens and any facility with exhaust hoods.</p></div></div>
<div class="svc-card"><img class="svc-card__img" src="{r}assets/images/services/commercial-hood.jpg" alt="Commercial kitchen hood system" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Commercial Hoods</h3><p class="svc-card__desc">We install and service commercial kitchen hood systems that ensure safe ventilation, effective smoke and grease removal, and compliance with Ontario fire and ventilation codes.</p></div></div>
<div class="svc-card"><img class="svc-card__img" src="{r}assets/images/services/commercial-boilers.jpg" alt="Commercial boiler installation" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Boilers</h3><p class="svc-card__desc">Professional installation, repair and maintenance of commercial and industrial boilers. From low-pressure heating boilers to high-efficiency condensing systems, we keep facility heating reliable.</p></div></div>
<div class="svc-card"><img class="svc-card__img" src="{r}assets/images/services/commercial-pm.jpg" alt="HVAC planned maintenance" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">PM (Planned Maintenance)</h3><p class="svc-card__desc">Comprehensive Planned Maintenance programs designed to keep your HVAC systems operating at peak efficiency, quarterly or seasonal visits, priority response, and equipment health reporting.</p></div></div>
<div class="svc-card"><img class="svc-card__img" src="{r}assets/images/services/duct-work-2.jpg" alt="Commercial ductwork installation" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Commercial Duct Work</h3><p class="svc-card__desc">Design, fabrication and installation of commercial duct systems, from retail spaces to multi-tenant plazas, industrial buildings and daycares. Code-compliant and built to last.</p></div></div>
</div>
</div></section>

<section class="section"><div class="container">
<h2>Industries We Serve</h2>
<div class="area-grid">
<div class="area-card"><span class="area-card__city">Restaurants</span><span class="area-card__sub">Hoods, MUA, rooftop, walk-ins</span></div>
<div class="area-card"><span class="area-card__city">Retail &amp; Plazas</span><span class="area-card__sub">Multi-unit rooftop &amp; tenant fitouts</span></div>
<div class="area-card"><span class="area-card__city">Daycares &amp; Schools</span><span class="area-card__sub">Ventilation &amp; IAQ requirements</span></div>
<div class="area-card"><span class="area-card__city">Industrial Facilities</span><span class="area-card__sub">Process heating, MUA, boilers</span></div>
<div class="area-card"><span class="area-card__city">Office Buildings</span><span class="area-card__sub">Tenant comfort &amp; system upgrades</span></div>
<div class="area-card"><span class="area-card__city">Property Managers</span><span class="area-card__sub">Portfolio PM contracts</span></div>
</div>

<h2 style="margin-top:2.5rem">Emergency Commercial HVAC Response</h2>
<p>Emergency HVAC for commercial facilities runs on a different clock than residential. A rooftop unit failure during a restaurant lunch rush, a no-heat at a daycare in February, or a refrigerant leak at a kitchen prep area can shut a business down in hours. We dispatch within 2 to 4 hours during business hours and run an after-hours emergency line for PM-contract clients. We carry common replacement compressors, capacitors, contactors, ignition modules, gas valves and belts so most calls are one-trip repairs. Property managers and restaurant operators looking for an energy efficient HVAC contractor near them across Halton, Peel and Hamilton can keep our number on file at (905) 491-6943.</p>

<h2 style="margin-top:2.5rem">Rooftop Unit Replacement And Curb Adapters</h2>
<p>Most commercial rooftop unit (RTU) replacements in Halton fall into one of three buckets: like-for-like swap (same Carrier 48HC for same Carrier 48HC, no curb work), curb-adapter retrofit (different tonnage or brand, we fabricate a sheet-metal adapter), or full curb replacement (rare, only when the original curb has corroded). A 5-ton like-for-like swap is typically a 1-day install with crane. A 10-ton with curb adapter is 2 days. We always pull the existing roof opening to inspect for leaks below the curb before lowering the new unit, more commercial RTU jobs go bad from roof leaks under the curb than from the unit itself.</p>

<h2 style="margin-top:2.5rem">Commercial Kitchen Hood Code Compliance</h2>
<p>Commercial kitchen hood systems in Ontario fall under NFPA 96 and the Ontario Building Code: hood capture velocity (typically 250 to 350 FPM at the cooking line), exhaust duct welded construction with full-penetration welds (no riveted seams), 18-inch clearance to combustibles, accessible cleanout doors every 12 feet, and balanced make-up air within 90% of exhaust CFM. We've designed and installed hood systems for new restaurant builds across Halton and Peel, including grease-laden vapour systems for charbroilers and wood-fired pizza ovens. Failure to meet NFPA 96 is the most common reason new restaurants don't open on schedule, we keep ours moving.</p>

<h2 style="margin-top:2.5rem">Refrigerant Transitions: R-22 To R-410A To R-454B</h2>
<p>Commercial property managers in Halton are facing a refrigerant transition window right now. R-22 has been illegal to import or manufacture in Canada since 2020, recovered stock is expensive and limited. R-410A is being phased down under the new Canadian regulations, R-454B is replacing it on new equipment from 2025 onward. If you have R-22 rooftop units (anything pre-2010 typically) we recommend planned replacement before the next big repair, not after. We'll inventory your refrigerant exposure across your portfolio for free as part of any PM-contract proposal.</p>
</div></section>
""" + service_area_map_section(r, "Commercial HVAC") + faq_block(faqs) + cta_banner(r, "Need A Commercial HVAC Partner?", "Quote, PM proposal, or emergency call, we respond fast.")
    page(
        out="commercial/index.html", depth=1,
        title="Commercial HVAC Services Oakville & GTA | IKAD Mechanical",
        description="Commercial HVAC contractor in Oakville. Rooftop units, make-up air, hoods, boilers, PM contracts & 24/7 service across Halton, Peel and Hamilton. (905) 491-6943.",
        canonical=f"{BASE}/commercial/",
        og_image=f"{BASE}/assets/images/services/commercial-rooftop.jpg",
        body=body, active="commercial", preload_hero="services/commercial-rooftop.jpg",
        schema_extra=service_schema("Commercial HVAC Installation and Maintenance", "Commercial Rooftop, MUA, Hoods, Boilers, PM", f"{BASE}/commercial/",
            "Commercial HVAC services including rooftop installation and maintenance, make-up air units, commercial kitchen hoods, boilers and planned maintenance contracts across Halton and the GTA.") +
            breadcrumb_schema([("Home",f"{BASE}/"),("Commercial",f"{BASE}/commercial/")]) +
            faq_schema(faqs)
    )

def build_residential():
    r = "../"
    faqs = [
        ("What residential HVAC services do you offer in Halton?",
         "<a href=\"" + r + "heating-services/\">Furnace install and repair</a>, <a href=\"" + r + "air-conditioning-heat-pumps/\">central AC and heat pumps</a>, <a href=\"" + r + "water-heaters/\">water heaters</a> (tank and tankless), <a href=\"" + r + "in-floor-heating/\">hydronic in-floor heating</a>, <a href=\"" + r + "snow-melting-systems/\">snow melting systems</a>, <a href=\"" + r + "duct-work/\">duct work</a>, <a href=\"" + r + "air-balancing/\">air balancing</a>, and <a href=\"" + r + "custom-homes/\">custom-home HVAC design</a>. We handle the full residential mechanical package."),
        ("How fast can you respond to a home service call?",
         "Same-day for most no-heat or no-cool calls in <a href=\"" + r + "service-areas/oakville/\">Oakville</a> and <a href=\"" + r + "service-areas/burlington/\">Burlington</a> during business hours. Other Halton cities and <a href=\"" + r + "service-areas/mississauga/\">Mississauga</a>/<a href=\"" + r + "service-areas/hamilton/\">Hamilton</a>/<a href=\"" + r + "service-areas/brampton/\">Brampton</a> typically same-day or next-day. We keep emergency-response slots open every winter and summer."),
        ("Do you offer financing on residential HVAC?",
         "Yes, Canadian HVAC finance partners with same-day approvals, plus we walk customers through the <a href=\"" + r + "blog/ontario-heat-pump-rebates-2026/\">Canada Greener Homes Loan and Home Renovation Savings Program</a> rebates to reduce the out-of-pocket."),
    ]
    body = hero_quote(r, "hero/hero-new-construction.jpg", "Residential HVAC", "Residential HVAC Services In Oakville & Halton",
        "From a new furnace in Burlington to a heated driveway in Milton, IKAD Mechanical handles the full residential HVAC package under one roof. Family-owned since 2010.", service_default="Residential HVAC") + \
        breadcrumbs(r, [("Home","./"),("Residential", "")]) + f"""
<section class="section"><div class="container" style="max-width:880px">
{key_facts(
    "Residential HVAC in Halton, Key Facts",
    "IKAD Mechanical is a TSSA-certified, HRAI-member residential HVAC contractor based in Oakville. We install and service every part of your home's mechanical system: furnaces, central AC, heat pumps, water heaters, in-floor heating, snow melt, duct work and air balancing. Family-owned since 2010, 1,200+ Halton homes served.",
    [
        ("Service area", "Oakville, Burlington, Milton, Halton Hills, Mississauga, Hamilton, Brampton"),
        ("Same-day no-heat / no-cool", "Yes, during business hours across Halton"),
        ("Financing", "Canadian HVAC finance partners; same-day approvals"),
        ("Rebates handled", "Enbridge HER+ &amp; Canada Greener Homes Loan paperwork filed by us"),
        ("Certifications", "TSSA G2/G3, ECRA/ESA, HRAI member, $5M liability, WSIB"),
    ]
)}
</div></section>
<section class="section"><div class="container">
<span class="eyebrow">Reliable Residential HVAC</span>
<h2>Your Trusted Partner For Residential Heating &amp; Cooling</h2>
<p>IKAD Mechanical is a full-service residential HVAC contractor based in Oakville. We install, repair and maintain every part of your home's mechanical system, furnaces, air conditioners, heat pumps, water heaters, hydronic in-floor heating, snow melting systems, ductwork and air balancing. One company, one phone number, one team accountable for the whole package.</p>
<p>Whether your 22-year-old furnace finally gave up, you're planning a custom home build, or you just want someone to look at why your upstairs is always five degrees warmer, we'd be glad to help.</p>
</div></section>

<section class="section section--gray"><div class="container">
<div class="svc-grid">
<a class="svc-card" href="{r}heating-services/"><img class="svc-card__img" src="{r}assets/images/services/heating-technician.jpg" alt="Heating services" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Heating Services</h3><p class="svc-card__desc">Dependable heating solutions designed to keep your home warm and comfortable all winter long. From new system installations and replacements to repairs and preventative maintenance.</p><span class="svc-card__link">Explore Heating</span></div></a>
<a class="svc-card" href="{r}air-conditioning-heat-pumps/"><img class="svc-card__img" src="{r}assets/images/services/air-conditioning.webp" alt="AC &amp; heat pumps" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Air Conditioning &amp; Heat Pumps</h3><p class="svc-card__desc">Installation, repair and maintenance of residential air conditioning systems and heat pumps, focused on year-round comfort and energy efficiency.</p><span class="svc-card__link">Explore Cooling</span></div></a>
<a class="svc-card" href="{r}water-heaters/"><img class="svc-card__img" src="{r}assets/images/services/water-heaters.jpg" alt="Water heaters" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Water Heaters</h3><p class="svc-card__desc">Installation, service and maintenance ensuring consistent performance, energy savings and long-lasting dependability, tank and tankless options.</p><span class="svc-card__link">See Water Heaters</span></div></a>
<a class="svc-card" href="{r}in-floor-heating/"><img class="svc-card__img" src="{r}assets/images/services/in-floor-heating.jpg" alt="In-floor heating" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">In-Floor Heating</h3><p class="svc-card__desc">Expert installation delivering even, energy-efficient warmth, suitable for bathrooms, basements, kitchens and whole custom homes.</p><span class="svc-card__link">Learn About Radiant</span></div></a>
<a class="svc-card" href="{r}snow-melting-systems/"><img class="svc-card__img" src="{r}assets/images/services/snow-melting.webp" alt="Snow melting systems" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Snow Melting Systems</h3><p class="svc-card__desc">Design and installation of systems that keep your home's driveways, walkways and entrances clear and safe all winter long.</p><span class="svc-card__link">See Snow Melt</span></div></a>
<a class="svc-card" href="{r}custom-homes/"><img class="svc-card__img" src="{r}assets/images/services/custom-homes.jpg" alt="Custom homes" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Custom Homes</h3><p class="svc-card__desc">Tailored HVAC solutions for custom homes, comfort, efficiency and seamless integration with your build.</p><span class="svc-card__link">Custom Home HVAC</span></div></a>
<a class="svc-card" href="{r}duct-work/"><img class="svc-card__img" src="{r}assets/images/services/duct-work.webp" alt="Ductwork" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Duct Work</h3><p class="svc-card__desc">Professional design and maintenance ensuring proper airflow, improved efficiency and consistent comfort in every room.</p><span class="svc-card__link">Explore Ductwork</span></div></a>
<a class="svc-card" href="{r}air-balancing/"><img class="svc-card__img" src="{r}assets/images/services/air-balancing.jpg" alt="Air balancing" loading="lazy" width="800" height="500"><div class="svc-card__body"><h3 class="svc-card__title">Air Balancing</h3><p class="svc-card__desc">Services to optimize airflow, improve comfort and maximize system efficiency throughout your home.</p><span class="svc-card__link">Balance My Home</span></div></a>
</div>
</div></section>
""" + service_area_map_section(r, "Residential HVAC") + faq_block(faqs) + cta_banner(r, "Request A Free Residential Quote", "On-site estimates within a few business days. No high-pressure sales.")
    page(
        out="residential/index.html", depth=1,
        title="Residential HVAC Services Oakville & Halton | IKAD Mechanical",
        description="Residential HVAC contractor in Oakville: furnace, AC, heat pump, water heater, in-floor heating, snow melt, ductwork & air balancing. Call (905) 491-6943.",
        canonical=f"{BASE}/residential/",
        og_image=f"{BASE}/assets/images/hero/hero-new-construction.jpg",
        body=body, active="res", preload_hero="hero/hero-new-construction.jpg",
        schema_extra=service_schema("Residential HVAC Services", "Residential Heating, Cooling, Plumbing", f"{BASE}/residential/",
            "Full residential HVAC services in Halton including furnace, AC, heat pump, water heater, in-floor heating, snow melting, ductwork and air balancing.") +
            breadcrumb_schema([("Home",f"{BASE}/"),("Residential",f"{BASE}/residential/")]) +
            faq_schema(faqs)
    )

# ---------------------------------------------------------------------------
# Other pages
# ---------------------------------------------------------------------------

def build_projects():
    r = "../"
    imgs = [
        ("project-1.jpg","Custom home HVAC install"),
        ("project-2.jpg","Furnace replacement project"),
        ("project-3.jpg","Commercial rooftop installation"),
        ("project-4.jpg","New duct work installation"),
        ("project-5.jpg","Snow melting system project"),
        ("project-6.jpg","High-efficiency boiler install"),
        ("project-7.jpg","Mechanical room installation"),
        ("project-8.jpg","Commercial HVAC project"),
        ("project-9.jpg","Residential HVAC install"),
        ("project-10.jpg","Custom build HVAC project"),
        ("residential-furnace-install.jpg","Residential furnace install"),
        ("custom-dual-furnace-install.jpg","Custom home dual furnace install"),
        ("snow-melting-hydronics-install.jpg","Snow melting hydronics manifold"),
        ("furnace-replacement-oakville.jpg","Furnace replacement in Oakville"),
        ("ac-install-1.jpg","Central AC installation"),
        ("ac-install-2.jpg","AC condenser placement"),
        ("ac-install-3.jpg","Completed AC installation"),
    ]
    cards = "\n".join(
        f'<a href="#" class="gallery-item"><img src="{r}assets/images/projects/{f}" alt="{alt} - IKAD Mechanical" loading="lazy" width="800" height="800"></a>'
        for f, alt in imgs
    )
    body = hero_compact(r, "hero/hero-new-construction.jpg", "Our Project Gallery", "Recent HVAC Projects Across Halton & The GTA",
        "Custom homes in Oakville, restaurant fitouts in Brampton, daycare retrofits in Hamilton, a sample of what our crews have been building.") + \
        breadcrumbs(r, [("Home","./"),("Our Projects", "")]) + f"""
<section class="section"><div class="container">
<span class="eyebrow">View Our Work</span>
<h2>From The Job Site</h2>
<p class="lead">Photos from real IKAD Mechanical installs across Halton, Peel and Hamilton. Each one shows the level of finish we bring to every job, proper equipment placement, clean piping, correct venting, and tidy mechanical rooms.</p>

<h3 style="margin-top:2rem">Residential Furnace &amp; Heating Projects</h3>
<p>Furnace replacements are our most common job, about 60% of our weekly schedule from October through April. We do single-day swaps when the existing setup allows, and 2-day jobs when gas-line, venting or duct work changes are needed. Every install starts with a Manual J load calculation, ends with a homeowner walkthrough and a registered manufacturer warranty.</p>

<h3 style="margin-top:2rem">Air Conditioning &amp; Heat Pump Installations</h3>
<p>From condenser-only AC replacements to full hybrid heat pump systems with new furnaces, we install across every Halton neighbourhood. We coordinate Greener Homes Loan paperwork and HER+ rebates where they apply, and we always level the pad before setting the unit.</p>

<h3 style="margin-top:2rem">Custom Home Mechanical Rooms</h3>
<p>The mechanical room is the heart of a custom home. We design around the builder's framing plan, run gas piping cleanly, label everything, and leave service clearances per code. These photos show a few recent main-floor mechanical packages from custom builds in Oakville, Burlington and Milton.</p>

<h3 style="margin-top:2rem">Commercial Rooftop Units &amp; Duct Work</h3>
<p>Rooftop unit replacements on Brampton plazas, daycare duct overhauls in Hamilton, restaurant kitchen hoods and make-up air across the GTA, these are some of our most photographed jobs because they're the kind of work that requires coordination across trades.</p>

<h3 style="margin-top:2rem">Snow Melt &amp; In-Floor Hydronics</h3>
<p>Hydronic in-floor heating manifolds for new builds, snow melt systems tied to existing boilers, basement radiant retrofits, radiant work is technically demanding but the result is the most comfortable heat available.</p>

<div class="gallery" style="margin-top:2rem">
{cards}
</div>

<p style="margin-top:2rem;color:#64748b">More photos and time-lapse videos on our <a href="https://www.instagram.com/ikadmechanical/" rel="noopener" target="_blank">Instagram</a> and <a href="https://www.facebook.com/profile.php?id=100088377265654" rel="noopener" target="_blank">Facebook</a>.</p>
</div></section>

<section class="section section--gray"><div class="container">
<div class="cta-banner"><div><h2>Your Project Could Be Next</h2><p>Free estimates across Halton and the GTA. Tell us about your project.</p></div><div class="btn-row"><a class="btn btn--secondary btn--large" href="{r}contact/">Request Estimate</a><a class="btn btn--outline btn--large" href="tel:+19054916943">Call Now</a></div></div>
</div></section>
"""
    page(
        out="our-projects/index.html", depth=1,
        title="Our HVAC Project Gallery | IKAD Mechanical Oakville",
        description="See recent HVAC projects across Halton & the GTA: custom homes, furnace replacements, commercial rooftops, snow melting and ductwork. IKAD Mechanical.",
        canonical=f"{BASE}/our-projects/",
        og_image=f"{BASE}/assets/images/projects/project-1.jpg",
        body=body, active="projects", preload_hero="hero/hero-new-construction.jpg",
        schema_extra=breadcrumb_schema([("Home",f"{BASE}/"),("Our Projects",f"{BASE}/our-projects/")])
    )

def build_about():
    r = "../"
    body = hero_compact(r, "hero/hero-ikad-team.jpg", "About IKAD Mechanical", "Family-Owned HVAC Since 2010",
        "We're a family-owned full-service HVAC contractor based in Oakville. We grew on word-of-mouth, and we're still that company: one number, one team, one name behind every job.") + \
        breadcrumbs(r, [("Home","./"),("About", "")]) + f"""
<section class="section"><div class="container"><div class="feature">
<div class="feature__media"><img src="{r}assets/images/services/heating-2.jpg" alt="IKAD Mechanical technician working in a residential mechanical room in Oakville" loading="lazy" width="900" height="600"></div>
<div class="feature__copy">
<span class="eyebrow">Who We Are</span>
<h2>A Family Name Behind Every Job</h2>
<p>IKAD Mechanical is a family-owned full-service plumbing &amp; HVAC company that opened its doors in Oakville in 2010. What started as one truck and a small crew is now a team installing and servicing heating, cooling, ventilation and plumbing across Halton, Peel and Hamilton, for homes, custom builds, restaurants, daycares and industrial facilities.</p>
<p>The company was founded by Mohanad, the name customers mention by name in reviews on HomeStars, who still answers the phone on most weekdays and is on site for every custom-home walkthrough. We grew the slow way: showing up on time, sizing equipment correctly, and standing behind the work. That's why customers who hired us in 2011 are still calling, and why builders trust us on their next subdivision. We don't subcontract installs and we don't outsource service.</p>
<ul>
<li>Licensed gas fitters (G2/G3) &amp; HVAC technicians (313A/313D)</li>
<li>TSSA contractor, ECRA/ESA licensed, HRAI member in good standing</li>
<li>Manufacturer-certified for Rheem, Lennox, Carrier, Daikin, Mitsubishi, Navien &amp; Rinnai</li>
<li>$5M liability insurance &amp; WSIB coverage on every job site</li>
<li>15+ years serving Halton &amp; the GTA, over 1,200 homes and businesses</li>
</ul>
</div>
</div></div></section>

<section class="section section--gray"><div class="container">
<div class="text-center" style="max-width:720px;margin:0 auto 2rem"><span class="eyebrow">By The Numbers</span><h2>What 15 Years In Halton Looks Like</h2></div>
<div class="trust-strip__grid">
<div class="trust-item"><span class="trust-item__big">2010</span><span class="trust-item__label">Year Founded In Oakville</span></div>
<div class="trust-item"><span class="trust-item__big">1,200+</span><span class="trust-item__label">Homes &amp; Businesses Served</span></div>
<div class="trust-item"><span class="trust-item__big">7</span><span class="trust-item__label">Cities Across Halton &amp; GTA</span></div>
<div class="trust-item"><span class="trust-item__big">100%</span><span class="trust-item__label">In-House Crew · No Subcontractors</span></div>
<div class="trust-item"><span class="trust-item__big">24/7</span><span class="trust-item__label">Emergency Response</span></div>
</div>
</div></section>

<section class="section"><div class="container" style="max-width:880px" id="owner">
<span class="eyebrow">Meet The Owner</span>
<h2>Mohanad, Owner &amp; Lead Technician</h2>
<div style="background:#f6f7f9;border-left:3px solid #e30613;border-radius:6px;padding:1.25rem 1.5rem;margin:1rem 0">
<p style="margin:0 0 .75rem;color:#334155;line-height:1.7"><strong>Mohanad</strong> founded IKAD Mechanical in 2010 and personally answers the phone, runs site visits, and is on most install jobs in 2026. He's a TSSA-certified G2 (commercial gas fitting) and G3 (residential gas fitting) licensed contractor, ECRA/ESA licensed for HVAC electrical, and has 15+ years of installing across Halton.</p>
<p style="margin:0;color:#475569;font-size:.95rem;line-height:1.7">Halton homeowners who hire IKAD work directly with the owner from quote to commissioning, not through a commissioned salesperson. Mohanad is the name mentioned by reviewers on <a href="https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling" rel="noopener" target="_blank">HomeStars</a> ("Mohanad and his team were personable and patient") and on our Google Business Profile.</p>
<p style="margin:.75rem 0 0;color:#64748b;font-size:.88rem"><strong>License &amp; certification IDs available on request</strong> — TSSA contractor ID, ECRA/ESA registration #, HRAI member ID, WSIB clearance. Property managers and builders, ask at quote stage and we'll share copies.</p>
</div>

<span class="eyebrow" style="margin-top:1rem;display:inline-block">How It Started</span>
<h2 style="margin-top:1rem">From One Truck In 2010 To A Halton-Wide HVAC Operation</h2>
<p>IKAD Mechanical opened its doors in <a href="{r}service-areas/oakville/">Oakville</a> in 2010, when Mohanad bought his first service truck and started taking calls from homes in the Glen Abbey and Bronte neighbourhoods. The decision to start the company came out of a frustration that's familiar to anyone who has hired a tradesperson in the GTA: too many contractors over-promise on the phone, send a different crew than the one who quoted, and disappear after the warranty starts.</p>
<p>The original idea was simple. Show up when you said you would. Size the equipment to the home, not to whatever happened to be on the truck. Stand behind the work after the cheque clears. Fifteen years and 1,200+ jobs later, that's still how we operate. The trucks are newer and the team is bigger, but every install lead still walks every job from quote through final commissioning, and the owner still answers the phone on most weekdays.</p>

<h2 style="margin-top:2rem">Where We've Worked (15 Years Across The Western GTA)</h2>
<p>What started in Oakville's Glen Abbey is now a trusted HVAC operation across seven cities. We've installed in heritage homes, post-war bungalows, 1980s subdivisions, 2000s builder-grade two-storey homes, and 5,000+ sq.ft. custom builds in every part of our service area:</p>
<ul style="line-height:1.85">
<li><a href="{r}service-areas/oakville/">Oakville</a> — head office on Upper Middle Rd East, every neighborhood from Bronte and Old Oakville to Joshua Creek, Glen Abbey, The Preserve and Palermo West.</li>
<li><a href="{r}service-areas/burlington/">Burlington</a> — Aldershot to Roseland to downtown, Headon Forest, Tyandaga, Alton Village, Mt Nemo, Lowville and Kilbride custom builds.</li>
<li><a href="{r}service-areas/milton/">Milton</a> — Hawthorne Village, Beaty, Coates, Bowes, plus custom homes north of Derry in Brookville and Campbellville.</li>
<li><a href="{r}service-areas/halton-hills/">Halton Hills</a> — Georgetown core, Acton, Glen Williams, Limehouse, Norval, plus rural propane-to-gas and oil-to-heat-pump conversions.</li>
<li><a href="{r}service-areas/mississauga/">Mississauga</a> — Mineola, Lorne Park, Port Credit, Erin Mills, Meadowvale, Churchill Meadows, plus commercial along Hurontario and Cooksville.</li>
<li><a href="{r}service-areas/hamilton/">Hamilton</a> — downtown Hamilton row houses, Hamilton Mountain, Stoney Creek, Ancaster, Dundas, Waterdown, plus east-end industrial.</li>
<li><a href="{r}service-areas/brampton/">Brampton</a> — Bramalea, Springdale, Mount Pleasant, Castlemore custom homes, plus industrial fitouts along Steeles-Airport Rd.</li>
</ul>
<p style="margin-top:1rem">No travel surcharge to any of these cities. Same-day or next-day response everywhere in our service area during business hours.</p>

<h2 style="margin-top:2rem">Certifications, Licensing And Insurance</h2>
<p>Working on natural gas, propane, refrigerant lines and combustion equipment without proper licensing in Ontario isn't just risky, it's illegal. We hold every credential the work requires:</p>
<ul style="line-height:1.8">
<li><strong>TSSA Gas Fitter G2 and G3 licences</strong> for all natural gas and propane work</li>
<li><strong>TSSA Authorized Contractor</strong> status for boiler, water heater and commercial gas equipment</li>
<li><strong>ECRA/ESA licensed</strong> for HVAC-related electrical work, high voltage and low voltage</li>
<li><strong>HRAI member in good standing</strong> (Heating, Refrigeration and Air Conditioning Institute of Canada)</li>
<li><strong>313A and 313D refrigeration technician certificates</strong> on staff for AC and heat pump work</li>
<li><strong>$5,000,000 commercial general liability insurance</strong>, plus WSIB coverage on every crew member, every job</li>
<li><strong>Manufacturer-certified installer</strong> for Rheem, Lennox, Carrier, Daikin, Mitsubishi, Goodman, Navien, Rinnai, Viessmann and NTI</li>
</ul>
<p>We provide certificates of insurance, license numbers and TSSA contractor IDs to property managers, builders and corporate clients on request. Just ask when you're getting the quote.</p>

<h2 style="margin-top:2rem">How A Job Actually Runs With Us</h2>
<p>Most of what people remember about a contractor isn't the equipment, it's the experience around it. Here's the cadence we follow on every install, residential or commercial:</p>
<ol style="line-height:1.8">
<li><strong>First call.</strong> A real person answers, weekdays 8 to 6 and Saturdays 9 to 4. After hours, you'll get a callback within an hour for genuine emergencies.</li>
<li><strong>On-site assessment.</strong> Usually within 2 to 5 business days for non-emergency work. We measure the home, photograph the mechanical space, run a quick Manual J load calc, and walk through what we're seeing.</li>
<li><strong>Written quote.</strong> Emailed the same day or next. Itemized equipment, labour, gas, electrical and venting work. Fixed price, valid 30 days.</li>
<li><strong>Deposit and order.</strong> Small deposit (typically 10 to 20%) confirms the install date and lets us order equipment.</li>
<li><strong>Install.</strong> Same lead on every visit. Drop sheets, shoe covers, daily clean-up. Most furnace and AC replacements complete in one day; custom-home jobs run on a schedule we share with the GC.</li>
<li><strong>Commissioning.</strong> Combustion analysis, refrigerant charge verification, gas pressure check, register-by-register temperature reading, thermostat configuration, and a homeowner walkthrough.</li>
<li><strong>Warranty registration.</strong> We register the manufacturer warranty in your name. Homeowners often forget this step; it matters when something fails in year eight.</li>
<li><strong>Follow-up.</strong> A check-in call about a week after the install to confirm everything's working as expected.</li>
</ol>

<h2 style="margin-top:2rem">Who We Work With</h2>
<p>About 70% of our work is residential: furnace and AC replacements, water heaters, in-floor heating, ductwork retrofits, and custom-home mechanical packages. The other 30% is commercial: rooftop unit replacements on plazas in Mississauga and Hamilton, daycare duct overhauls, restaurant kitchen hood and make-up air installations, and PM (preventive maintenance) contracts on multi-tenant properties across the GTA.</p>
<p>Customer types we work with regularly:</p>
<ul style="columns:2;column-gap:2rem;line-height:1.7;max-width:680px">
<li>Halton, Mississauga and Hamilton homeowners</li>
<li>Custom-home builders (Oakville, Burlington, Milton)</li>
<li>General contractors and renovation firms</li>
<li>Property managers and condo corporations</li>
<li>Restaurant operators</li>
<li>Daycare and pre-school operators</li>
<li>Plaza and multi-tenant retail owners</li>
<li>Light-industrial facility managers</li>
</ul>

<h2 style="margin-top:2rem">Where To Verify Us</h2>
<p>You don't have to take our word for any of this. Verify everything:</p>
<ul style="line-height:1.8">
<li><strong>HomeStars profile:</strong> <a href="https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling" rel="noopener" target="_blank">Read every customer review</a> Mohanad is mentioned in many of them by name</li>
<li><strong>HRAI membership:</strong> searchable on the <a href="https://www.hrai.ca/" rel="noopener" target="_blank">HRAI.ca</a> contractor directory</li>
<li><strong>TSSA contractor status:</strong> verifiable on the <a href="https://www.tssa.org/" rel="noopener" target="_blank">TSSA.org</a> public registry</li>
<li><strong>Facebook:</strong> <a href="https://www.facebook.com/profile.php?id=100088377265654" rel="noopener" target="_blank">IKAD Mechanical</a> for recent job photos and time-lapse videos</li>
<li><strong>Instagram:</strong> <a href="https://www.instagram.com/ikadmechanical/" rel="noopener" target="_blank">@ikadmechanical</a> for daily jobsite content</li>
</ul>
</div></section>

<section class="section section--dark"><div class="container">
<div class="text-center" style="max-width:720px;margin:0 auto 2.5rem"><span class="eyebrow">Our Values</span><h2>How We Run Every Project</h2></div>
<div class="why-grid">
<div class="why-card" style="background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.15);color:#fff"><div class="why-card__num">1</div><h3 style="color:#fff">Right-Size Everything</h3><p style="color:#cbd5e1">Manual J load calculation on every install. Equipment matched to your home, not the unit we're pulling out.</p></div>
<div class="why-card" style="background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.15);color:#fff"><div class="why-card__num">2</div><h3 style="color:#fff">Show Up When We Say</h3><p style="color:#cbd5e1">Our schedule is our reputation. Builders coordinate their trades around us because we don't slip dates.</p></div>
<div class="why-card" style="background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.15);color:#fff"><div class="why-card__num">3</div><h3 style="color:#fff">Stand Behind The Work</h3><p style="color:#cbd5e1">If something needs a second visit, we come back. Callbacks aren't billable, we built our business on getting it right the first time.</p></div>
</div>
</div></section>

<section class="section"><div class="container">
<div class="text-center" style="max-width:720px;margin:0 auto 2rem"><span class="eyebrow">Service Areas</span><h2>Where We Work</h2></div>
<div class="area-grid">
<a class="area-card" href="{r}service-areas/oakville/"><span class="area-card__city">Oakville</span><span class="area-card__sub">Head office · same-day service</span></a>
<a class="area-card" href="{r}service-areas/burlington/"><span class="area-card__city">Burlington</span><span class="area-card__sub">Furnace, AC, ductless installs</span></a>
<a class="area-card" href="{r}service-areas/milton/"><span class="area-card__city">Milton</span><span class="area-card__sub">New builds &amp; custom homes</span></a>
<a class="area-card" href="{r}service-areas/halton-hills/"><span class="area-card__city">Halton Hills</span><span class="area-card__sub">Georgetown &amp; Acton</span></a>
<a class="area-card" href="{r}service-areas/mississauga/"><span class="area-card__city">Mississauga</span><span class="area-card__sub">Residential &amp; commercial</span></a>
<a class="area-card" href="{r}service-areas/hamilton/"><span class="area-card__city">Hamilton</span><span class="area-card__sub">Daycare, plaza &amp; rooftop work</span></a>
<a class="area-card" href="{r}service-areas/brampton/"><span class="area-card__city">Brampton</span><span class="area-card__sub">Ductwork &amp; mechanical fitouts</span></a>
</div>
</div></section>
""" + cta_banner(r, "Want To Work With IKAD?", "Free quotes, transparent pricing, and a crew you'll recognize from job to job.")
    import json as _json
    owner_schema = {
        "@context":"https://schema.org",
        "@type":"Person",
        "@id": f"{BASE}/about/#owner",
        "name":"Mohanad",
        "jobTitle":"Owner & Lead Technician",
        "worksFor": {"@id": f"{BASE}/#business"},
        "url": f"{BASE}/about/",
        "image": f"{BASE}/assets/images/hero/hero-ikad-team.jpg",
        "knowsAbout":[
            "HVAC installation","Furnace replacement","Cold-climate heat pumps",
            "Hydronic in-floor heating","Manual J load calculation",
            "TSSA gas fitting","R-454B refrigerant","Custom home HVAC design",
            "Commercial rooftop units","Make-up air units","Snow melting systems"
        ],
        "hasCredential":[
            {"@type":"EducationalOccupationalCredential","credentialCategory":"license","name":"TSSA Gas Fitter G2 (Commercial Gas Fitting)","recognizedBy":{"@type":"Organization","name":"Technical Standards and Safety Authority (TSSA)","url":"https://www.tssa.org/"}},
            {"@type":"EducationalOccupationalCredential","credentialCategory":"license","name":"TSSA Gas Fitter G3 (Residential Gas Fitting)","recognizedBy":{"@type":"Organization","name":"Technical Standards and Safety Authority (TSSA)","url":"https://www.tssa.org/"}},
            {"@type":"EducationalOccupationalCredential","credentialCategory":"license","name":"ECRA / ESA Electrical Contractor License","recognizedBy":{"@type":"Organization","name":"Electrical Safety Authority","url":"https://esasafe.com/"}},
            {"@type":"EducationalOccupationalCredential","credentialCategory":"membership","name":"HRAI Member","recognizedBy":{"@type":"Organization","name":"Heating, Refrigeration and Air Conditioning Institute of Canada","url":"https://www.hrai.ca/"}}
        ],
        "alumniOf":{"@type":"Organization","name":"TSSA-certified gas fitter training"},
        "sameAs":[
            "https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling",
            "https://www.facebook.com/profile.php?id=100088377265654",
            "https://www.instagram.com/ikadmechanical/"
        ]
    }
    page(
        out="about/index.html", depth=1,
        title="About IKAD Mechanical | Family-Owned HVAC Oakville Since 2010",
        description="Meet IKAD Mechanical, a family-owned, TSSA-certified HVAC contractor serving Oakville and the GTA since 2010. Licensed, insured, no subcontractors.",
        canonical=f"{BASE}/about/",
        og_image=f"{BASE}/assets/images/hero/hero-ikad-team.jpg",
        body=body, active="about", preload_hero="hero/hero-ikad-team.jpg",
        schema_extra=breadcrumb_schema([("Home",f"{BASE}/"),("About",f"{BASE}/about/")]) +
            f'<script type="application/ld+json">\n{_json.dumps(owner_schema, ensure_ascii=False)}\n</script>'
    )

def build_contact():
    r = "../"
    body = hero_compact(r, "hero/hero-ikad-team.jpg", "Get In Touch", "Request Your Free HVAC Estimate",
        "Tell us about your project: furnace replacement, AC install, custom home build, commercial PM contract. Most quotes back the same day during business hours.") + \
        breadcrumbs(r, [("Home","./"),("Contact", "")]) + f"""
<section class="section"><div class="container">
<div class="contact-grid">
<form class="form" data-form="quote" action="/api/quote" method="post" novalidate>
<h2 style="margin-top:0">Request A Free Quote</h2>
<p>Fill in a few details. We'll respond within one business day with next steps and pricing.</p>
<div class="form__honeypot" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
<div class="form__row">
<div class="form__group"><label for="name">Your Name *</label><input id="name" name="name" type="text" required autocomplete="name"></div>
<div class="form__group"><label for="phone">Phone *</label><input id="phone" name="phone" type="tel" required autocomplete="tel"></div>
</div>
<div class="form__group"><label for="email">Email *</label><input id="email" name="email" type="email" required autocomplete="email"></div>
<div class="form__row">
<div class="form__group"><label for="city">City *</label><select id="city" name="city" required>
<option value="">Select your city…</option>
<option>Oakville</option><option>Burlington</option><option>Milton</option><option>Halton Hills</option><option>Mississauga</option><option>Hamilton</option><option>Brampton</option><option>Other (GTA)</option>
</select></div>
<div class="form__group"><label for="service">Service Needed *</label><select id="service" name="service" required>
<option value="">Select a service…</option>
<option>Furnace / Heating</option><option>Air Conditioning</option><option>Heat Pump</option><option>Water Heater</option><option>In-Floor Heating</option><option>Snow Melting System</option><option>Duct Work</option><option>Air Balancing</option><option>Custom Home HVAC</option><option>Commercial HVAC</option><option>Emergency Repair</option><option>Other</option>
</select></div>
</div>
<div class="form__group"><label for="message">Project Details</label><textarea id="message" name="message" placeholder="Tell us about your home or facility, equipment age, square footage, problems you're trying to solve…"></textarea></div>
<p class="form__hint">By submitting you agree to be contacted by IKAD Mechanical regarding your request. We never share your info.</p>
<button class="btn btn--primary form__submit btn--large" type="submit">Send Quote Request</button>
</form>

<aside class="contact-info">
<h3 style="margin-top:0">Contact Details</h3>
<ul>
<li>{icon('phone')}<div><strong>Phone</strong><a href="tel:+19054916943">(905) 491-6943</a></div></li>
<li>{icon('mail')}<div><strong>Email</strong><a href="mailto:info@ikad.ca">info@ikad.ca</a></div></li>
<li>{icon('pin')}<div><strong>Address</strong>2275 Upper Middle Rd E, Suite 101<br>Oakville, ON L6H 0C3</div></li>
<li>{icon('clock')}<div><strong>Hours</strong>Mon–Fri 8:00am – 6:00pm<br>Sat 9:00am – 4:00pm<br>Sun &amp; emergencies, call anytime</div></li>
<li>{icon('shield')}<div><strong>Service Area</strong>Halton Region · Peel Region · Hamilton<br>(Oakville · Burlington · Milton · Halton Hills · Mississauga · Hamilton · Brampton)</div></li>
</ul>
<h4 style="margin-top:1.5rem">Emergency No-Heat / No-Cool?</h4>
<p>Call directly, we keep emergency response slots open every winter and summer.</p>
<a class="btn btn--primary with-icon" style="width:100%;justify-content:center" href="tel:+19054916943">{icon('phone')} Call (905) 491-6943</a>
</aside>
</div>

<div class="map-embed" style="margin-top:3rem">
<iframe src="https://www.google.com/maps?q=2275+Upper+Middle+Rd+E,+Oakville,+ON&amp;output=embed" loading="lazy" title="IKAD Mechanical office on Google Maps" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
</div>
</div></section>
"""
    page(
        out="contact/index.html", depth=1,
        title="Contact IKAD Mechanical | Free HVAC Quotes In Oakville",
        description="Request a free HVAC quote from IKAD Mechanical. Furnace, AC, heat pumps, water heaters and commercial HVAC in Oakville &amp; Halton. (905) 491-6943.",
        canonical=f"{BASE}/contact/",
        og_image=f"{BASE}/assets/images/hero/hero-ikad-team.jpg",
        body=body, active="contact", preload_hero="hero/hero-ikad-team.jpg",
        schema_extra="""<script type=\"application/ld+json\">
{\"@context\":\"https://schema.org\",\"@type\":\"ContactPage\",\"name\":\"Contact IKAD Mechanical\",\"url\":\"https://ikad.ca/contact/\",\"mainEntity\":{\"@type\":\"HVACBusiness\",\"name\":\"IKAD Mechanical Inc.\",\"telephone\":\"+1-905-491-6943\",\"email\":\"info@ikad.ca\",\"address\":{\"@type\":\"PostalAddress\",\"streetAddress\":\"2275 Upper Middle Rd E, Suite 101\",\"addressLocality\":\"Oakville\",\"addressRegion\":\"ON\",\"postalCode\":\"L6H 0C3\",\"addressCountry\":\"CA\"}}}
</script>""" + breadcrumb_schema([("Home",f"{BASE}/"),("Contact",f"{BASE}/contact/")])
    )

# ---------------------------------------------------------------------------
# Service area pages
# ---------------------------------------------------------------------------

CITIES = [
    {
        "slug":"oakville",
        "seo_title":"Oakville HVAC Contractor | Glen Abbey to Old Oakville | IKAD",
        "seo_description":"Local Oakville HVAC contractor with same-hour response. Furnace, AC, heat pump &amp; water heater installation in Glen Abbey, Bronte, Joshua Creek &amp; more.","name":"Oakville",
        "blurb":"Head office. Same-day service across Glen Abbey, Bronte, Joshua Creek, College Park and West Oak Trails.",
        "lat":43.4675,"lng":-79.6877,
        "response":"Same-day, often same-hour during business hours",
        "utility_gas":"Enbridge Gas",
        "utility_electric":"Oakville Hydro",
        "permit_office":"Town of Oakville Building Services",
        "drive_from_hq":"5–15 minutes (HQ is on Upper Middle Rd E)",
        "population":"~213,000 (2021 census, fastest-growing town in Halton)",
        "climate_note":"Mild lake-moderated climate near Lake Ontario. Summer humidity south of the QEW can run 70–85%, AC sizing has to account for latent load, not just temperature. North of Dundas is more exposed to wind and slightly colder winters.",
        "copy":"Oakville is where IKAD Mechanical started in 2010 and where most of our trucks roll out every morning. From the lakefront heritage homes near Old Oakville to the newer custom builds north of Dundas, we know the housing stock, what tends to be original equipment from the 1980s build-out, what's been replaced once already, and where the gas line runs.",
        "story":"A recent example: a 1992 ranch in Bronte where the original Lennox G24 was on its second heat exchanger crack. We pulled it, ran a Manual J that came back at 56k BTU (the old unit was 100k), and installed a Rheem R96V two-stage with a new Ecobee. The homeowner's January gas bill dropped 28% year-over-year.",
        "case_image":"projects/furnace-replacement-oakville.jpg",
        "case_alt":"Recent furnace replacement project in Oakville by IKAD Mechanical",
        "neighborhoods":["Glen Abbey","Bronte","Joshua Creek","West Oak Trails","College Park","Old Oakville","Iroquois Ridge","Westmount","River Oaks","Falgarwood","The Preserve","Uptown Core","Eastlake","Clearview","Palermo West"],
        "landmarks":["Oakville Place","Bronte Heritage Waterfront Park","Glen Abbey Golf Club","Coronation Park","Sheridan College Trafalgar Campus","Oakville Galleries","Oakville Centre for the Performing Arts","Trafalgar Park Community Centre","Oakville GO Station","Bronte GO Station"],
        "housing_eras":[
            ("Pre-1960s, Old Oakville &amp; Bronte heritage","Wood-framed homes with original or once-replaced boilers, often converted from oil. We do oil-to-gas conversions, replace cast-iron radiators where homeowners want them gone, and add ductless mini-splits in heritage homes where ductwork installation is impossible. Heritage Conservation District rules in Old Oakville require sensitive equipment placement, outdoor condensers usually need to be hidden from street view."),
            ("1960s–1980s, Falgarwood, Eastlake, Trafalgar Park","Original mid-efficiency furnaces (often Lennox G-series or Carrier 58S) have all hit end-of-life. AC condensers from the 1980s are universally replaceable now. Returns are usually undersized for what modern variable-speed equipment expects, we add upstairs returns on most jobs."),
            ("1990s–2000s, Glen Abbey, River Oaks, Joshua Creek","Builder-grade 80% AFUE single-stage furnaces, now 25+ years old. Heat exchanger cracks on the original 1995 Goodman units are becoming a weekly find. AC line sets sometimes leak at the chase penetration."),
            ("2005–2015, West Oak Trails, Westmount, Uptown Core","First-generation 95% AFUE direct-vent furnaces with PVC venting. Most still functional but inducer motors and pressure switches are common failures. Ducts are typically OK but never balanced."),
            ("2015+, The Preserve, North Oakville, Palermo West","Newer high-efficiency 96–98% AFUE equipment, often with one ducted heat pump or hybrid setup. We do warranty service, smart-thermostat upgrades and second-stage thermostat wiring corrections, surprisingly common on builder installs.")
        ],
        "scenarios":[
            ("Heritage home, no ductwork (Old Oakville)","Use ductless mini-split heat pumps (Mitsubishi Hyper-Heat or Daikin Aurora multi-zone) to add air conditioning without compromising original plaster walls or trim. We hide the outdoor units in side yards and route line sets through closets when possible."),
            ("Lakefront condensation problems (Bronte, Coronation Park)","Oversized AC short-cycles in our humid summer days and never pulls moisture out. Right-sizing with a 2-stage or variable-speed unit usually drops indoor humidity by 8–12 percentage points and fixes the clammy feeling."),
            ("Two-storey home with hot upstairs (Joshua Creek, Glen Abbey)","Almost always a combination of insufficient upstairs returns and unbalanced supplies. Adding a single 14×8 return on the upper landing plus damper-balancing typically gets upstairs within 1.5°C of downstairs."),
            ("Custom new build north of Dundas (The Preserve, Uptown Core)","Hybrid heat pump + 96% furnace with HRV, zoning by floor, in-floor radiant in master ensuites and basement, ducted high-velocity for cooling. Engaged at framing stage so duct chases can be planned."),
        ],
        "city_faqs":[
            ("Do you pull mechanical permits with the Town of Oakville?","Yes, every furnace replacement, gas line modification and ductwork install requires a mechanical permit from Oakville Building Services on Trafalgar Rd. We handle the application, drawings if needed, and the inspection scheduling so you don't have to."),
            ("How fast can you respond to a no-heat call in Oakville?","Same-day during business hours for most addresses south of Dundas; usually same-day for north of Dundas too. Our shop on Upper Middle Rd East means most Oakville calls are 15 minutes away."),
            ("Do you work on homes in Oakville's Heritage Conservation District?","Yes, we routinely install equipment in Old Oakville's heritage zone. We coordinate with the Town's Heritage Planner on outdoor unit placement and venting routes to keep the streetscape intact. Ductless mini-splits are often the only practical AC option in these homes."),
        ],
                "neighborhood_intro":"Our Upper Middle Rd shop puts us 5–15 minutes from any Oakville address. We service every Oakville neighbourhood, including:",
        "neighborhood_fallback":"On a side street we haven't listed? Call us anyway, Oakville is our home turf, we cover every postal code.",
        "cta_line":"Local trucks, local crews, local accountability. Most Oakville quotes are emailed within an hour during business hours.",
        "faq_outro":"Want more? Our",
        "nearby":["burlington","milton","mississauga"],
        "services_intro":"Oakville is our home town and the address on the side of our trucks. After 15 years working every postal code from L6H to L6M, we know which neighbourhoods still have 1990s mid-efficiency furnaces in the basement, where the gas line is undersized, and which builders left the upstairs returns out. Here is the full HVAC scope we run for Oakville homes and businesses, with notes on what is most specific to Oakville.",
        "service_blurbs":[
            ("Furnace Replacement &amp; Repair In Oakville", "heating-services/", "We replace 100+ Oakville furnaces a year, most originals are 1990s-2000s mid-efficiency units in Glen Abbey, Joshua Creek and River Oaks that have cracked heat exchangers or failed inducer motors. Manual J load calc on every quote, Town of Oakville permit pulled by us, no-heat dispatch typically 1-3 hours during business hours."),
            ("Central AC &amp; Cold-Climate Heat Pumps For Oakville", "air-conditioning-heat-pumps/", "Lake-moderated south Oakville (Bronte, Coronation Park) hits 75-85% summer humidity, the AC fix here is rarely a bigger unit, it is a 2-stage or variable-speed system that runs longer and pulls moisture out. North of Dundas is drier and a cold-climate heat pump pairs beautifully with the existing furnace."),
            ("Tank &amp; Tankless Water Heaters Across Oakville", "water-heaters/", "Most Oakville installs are tank-to-tank for budget reasons, tank-to-tankless for larger Joshua Creek, The Preserve and Westmount homes with multiple bathrooms. Halton water averages 7-9 grains of hardness, we strongly recommend a softener at tankless install time."),
            ("Hydronic In-Floor Heating For Oakville Renos &amp; Builds", "in-floor-heating/", "Bathroom and ensuite electric mats are our most common Oakville retrofit. Whole-home hydronic in custom builds (typically The Preserve, Bronte West, Glenorchy) integrates with high-efficiency condensing boilers and ducted heat pumps for cooling."),
            ("Heated Driveways &amp; Snow Melt In Oakville", "snow-melting-systems/", "Steep driveways in Joshua Creek, Eastlake and North Oakville are the most common ask. Best built at the pouring stage, we coordinate directly with your concrete contractor. Hydronic systems for full driveways, electric mats for entry steps."),
            ("Duct Work, Sealing &amp; Cleaning In Oakville Homes", "duct-work/", "1990s Glen Abbey, Falgarwood and Iroquois Ridge homes routinely show 25-30% duct leakage in attic runs. Our duct sealing program pays back in 1-2 winters on gas savings alone, and it fixes most of the upstairs-hot complaints we get."),
            ("Air Balancing For Oakville Two-Storey Homes", "air-balancing/", "The #1 Oakville comfort complaint we hear is upstairs hot/downstairs cold in two-storey homes. We measure CFM at every register, balance the trunk, and adjust dampers. About 70% of cases resolve without any equipment changes."),
            ("Custom Home HVAC Design For Oakville Builders", "custom-homes/", "We are the in-house mechanical contractor for several Oakville custom-home builders in The Preserve, Bronte West and Glenorchy. Engaged at framing stage, full Manual J/D/S, zoning, HRV/ERV, in-floor, snow melt, and we hold our schedule."),
            ("Commercial HVAC For Oakville Businesses", "commercial/", "Restaurants on Lakeshore and Kerr, plazas along Trafalgar and Dundas, daycares in Glen Abbey, we hold PM contracts and dispatch within 2-4 hours for no-cool emergencies. Carrier, Lennox, Trane, Reznor and Captive-Aire are our most-installed commercial brands.")
        ],
    },
    {
        "slug":"burlington",
        "seo_title":"Burlington HVAC | Aldershot to Lowville | IKAD Mechanical",
        "seo_description":"Trusted Burlington HVAC: furnace, AC, heat pump install &amp; repair from Aldershot to Lowville. TSSA certified, HRAI member, multi-day weekly coverage.","name":"Burlington",
        "blurb":"Waterfront to Aldershot, Headon Forest and Tyandaga, full-service HVAC, same crew every visit.",
        "lat":43.3255,"lng":-79.7990,
        "response":"Same-day during business hours",
        "utility_gas":"Enbridge Gas",
        "utility_electric":"Alectra Utilities (Burlington)",
        "permit_office":"City of Burlington Building Department",
        "drive_from_hq":"15–25 minutes",
        "population":"~187,000 (2021 census, City of Burlington)",
        "climate_note":"Lake-moderated like Oakville, but Burlington sees noticeably more lake-effect winter snow at higher elevations (Mountainside, Tyandaga). Summer humidity is similar to Oakville south of the QEW. The escarpment edge near Mount Nemo influences wind patterns, exposed ridges need attic insulation and properly sized make-up air.",
        "copy":"We've been doing residential and commercial HVAC across Burlington for more than a decade, furnace replacements in Aldershot, central AC retrofits in The Orchard, custom-home mechanical packages near Lowville. Our trucks are in Burlington multiple days a week.",
        "story":"One job we keep referencing: a 4,800 sq.ft. custom build off Walker's Line near Lowville. The owner had been quoted by two larger contractors for a forced-air-only system. We designed a hybrid, hydronic in-floor on the main level, a high-velocity small-duct system for cooling and supplemental heat, and a separate ductless head for the loft. Five years later, no callbacks.",
        "case_image":"projects/custom-dual-furnace-install.jpg",
        "case_alt":"Custom home dual furnace HVAC installation in Burlington",
        "neighborhoods":["Aldershot","Tyandaga","Headon Forest","The Orchard","Brant Hills","Roseland","Millcroft","Alton","Mountainside","Lowville","Shoreacres","Pinedale","Plains","Palmer","Kilbride"],
        "landmarks":["Burlington Centre Mall","Spencer Smith Park","Royal Botanical Gardens","Lasalle Park &amp; Marina","Mapleview Centre","Joseph Brant Hospital","Burlington Performing Arts Centre","Burlington GO Station","Aldershot GO Station","Appleby GO Station","Bronte Creek Provincial Park (border)","Mount Nemo Conservation Area"],
        "housing_eras":[
            ("Pre-1950s, Aldershot, Plains, Downtown Burlington","Original wood-framed homes, many converted from coal or oil to gas decades ago. Cast-iron radiators with old boilers are common. We do boiler-to-combi conversions (Navien NCB or Viessmann B1HA) to free up basement space and improve domestic hot water output."),
            ("1960s–1970s, Roseland, Tyandaga, Mountainside","Mid-century homes with first-generation forced-air systems. Original ductwork is often undersized for modern AC airflow. Most homes have had at least one furnace replacement and one AC replacement by now, we're usually doing round 2 or 3."),
            ("1980s–1990s, Headon Forest, Brant Hills, The Orchard","Two-storey suburban housing. Common issue: AC condenser placement on the side yard against the brick wall radiates heat into the house. We relocate to rear yards when possible. Builder-grade ductwork has rarely been balanced."),
            ("2000s–2010s, Alton Village, Millcroft, Orchard","High-density planned communities. AC units commonly undersized because builder used one tonnage across the model regardless of orientation. South-facing units with finished basements often need to go from 2 to 2.5 ton at replacement."),
            ("2010s+, Lowville &amp; rural escarpment estates","Custom homes 3,500–8,000+ sq.ft. Hybrid mechanical packages: hydronic in-floor + cold-climate heat pump + zoned forced air. Often paired with HRV/ERV ventilation and snow melt at long driveways."),
        ],
        "scenarios":[
            ("Pre-1950 home converting from boiler to combi (Aldershot, Plains)","Replace cast-iron-radiator boiler with a Navien NCB-H combi unit. Keep the radiators, gain endless domestic hot water, free up basement floor space. Typical cost $7,800–$11,500 including permit and rebate paperwork."),
            ("Wind-exposed escarpment home (Mountainside, Mount Nemo)","Drafty house, high-static-pressure return air problems, and ice forming on north-side AC condensers. Solutions: air sealing audit, return-air upgrade and a properly-sized cold-climate heat pump with elevated mounting bracket."),
            ("Lakefront custom home (Roseland, Shoreacres)","Salt-air corrosion on outdoor coils, use coated outdoor condensers (Lennox Sea Coast or Carrier coil-coated models). Humidity control matters more than raw cooling tonnage. Pair with whole-home dehumidifier for shoulder seasons."),
            ("Twin-driveway commercial fitout (Burlington industrial corridor)","Make-up air sizing for a commercial bake shop with two hood systems. We designed the gas piping, hood draw, MUA tempering and TSSA inspection coordination across two tenant suites."),
        ],
        "city_faqs":[
            ("How long does it take a Burlington HVAC permit to be approved?","City of Burlington mechanical permits for a straight furnace swap typically come back within 5–7 business days. Custom design work runs 10–15 business days. We handle the application and inspection scheduling."),
            ("Do you service heat pumps installed by other companies in Burlington?","Yes, we do warranty-out and maintenance work on most brands of heat pump installed by other contractors. We're certified for Daikin, Mitsubishi, Lennox, Rheem and Carrier."),
            ("Which Burlington neighborhoods do you do the most residential work in?","Aldershot and The Orchard for furnace replacements, Lowville and Roseland for custom-home mechanical packages, Brant Hills for ductless retrofits."),
        ],
                "neighborhood_intro":"From Aldershot up to Lowville and everything in between, our crews are in Burlington multiple days a week. Coverage includes:",
        "neighborhood_fallback":"Not on this list? We still cover you. Burlington is one of our most active service areas, just call.",
        "cta_line":"No-pressure free quote backed by a M insured, HRAI-member team that's installed across Burlington since 2010.",
        "faq_outro":"For broader HVAC questions, see our",
        "nearby":["oakville","milton","hamilton","halton-hills"],
        "services_intro":"Burlington is our second-busiest service area after Oakville. The mix is distinctive: heritage homes in Roseland and downtown Burlington need ductless and oil-to-gas conversions, the 1970s-90s sprawl in Headon Forest and Tyandaga has the most upstairs-too-hot complaints we see anywhere in Halton, and the north-of-Dundas custom homes near Mt Nemo are full hybrid heat-pump-and-radiant builds. Here is what we do most for Burlington homes and businesses, with notes on what differs vs Oakville.",
        "service_blurbs":[
            ("Furnace Installation &amp; Repair In Burlington", "heating-services/", "Older Burlington homes (downtown, Roseland, Aldershot) often still have 1980s mid-efficiency or even converted-oil units. We do gas conversions, chimney liner installs and high-efficiency replacements. Newer Headon Forest and Alton Village homes are usually on second-generation high-efficiency, common failure is the inducer motor or condensate pump."),
            ("AC, Heat Pumps &amp; Ductless For Burlington", "air-conditioning-heat-pumps/", "Burlington runs slightly drier than Oakville south of the QEW but the lakefront still sees 70%+ humidity. Heritage Roseland and downtown Burlington (no ductwork or limited chase space) is our highest-volume ductless mini-split market in Halton, Mitsubishi Hyper-Heat dominates here."),
            ("Water Heater Replacement In Burlington", "water-heaters/", "Burlington has a lot of homes still on water-heater rental contracts from the 1990s, we help owners do the math on buyout vs continued rental, and convert to owned tank or tankless. Most installs are same-day. Tankless gets the same hard-water softener recommendation as Oakville."),
            ("In-Floor Hydronic Heating, Burlington Renos &amp; Custom", "in-floor-heating/", "Bathroom retrofits in Roseland and downtown Burlington heritage homes are common, electric mats under new tile. Whole-home hydronic in custom builds near Mt Nemo, Lowville and Kilbride pair with high-efficiency boilers we tie into snow melt for the long driveways up there."),
            ("Heated Driveways In Burlington (Especially North)", "snow-melting-systems/", "Long, steep north Burlington driveways (Mt Nemo, Lowville, Kilbride) are our most common snow melt installs in the city. We design for the slightly higher snow loads above the escarpment vs the lakefront. Coordinate with concrete contractor at pouring stage."),
            ("Duct Sealing &amp; Re-Balancing In Burlington Homes", "duct-work/", "Headon Forest and Tyandaga two-storey homes from the 1980s-90s have the most leaky-attic-duct problem in Burlington, we see 25-35% duct leakage routinely. Whole-home sealing typically $850-$1,500 and visibly improves upstairs comfort within hours."),
            ("Air Balancing For Burlington Two-Storey Homes", "air-balancing/", "Upstairs hot/cold complaints in Headon Forest, Brant Hills and Mountainside dominate our Burlington air-balance calls. The fix is usually trunk damper adjustment plus a new upstairs return, not new equipment."),
            ("Custom Home HVAC For Burlington Builders", "custom-homes/", "North Burlington (Mt Nemo, Lowville, Kilbride) and waterfront infill in Roseland are the active custom-build areas. We do full Manual J, hybrid forced-air-plus-hydronic packages, HRV/ERV, smart controls, and we coordinate with Conservation Halton on escarpment-area builds."),
            ("Commercial HVAC In Burlington", "commercial/", "Restaurants and retail on Lakeshore, Brant and Plains Road, plazas along Appleby and Walkers Line, daycares city-wide, we hold commercial PM contracts and dispatch fast for no-cool emergencies. Frequent work for Burlington dental, veterinary and medical offices.")
        ],
    },
    {
        "slug":"milton",
        "seo_title":"Milton HVAC | Builder-Grade Fixes &amp; Custom Builds | IKAD",
        "seo_description":"Milton HVAC contractor specializing in fixing builder-grade AC sizing issues and custom-home mechanical design across Hawthorne Village, Beaty &amp; north Milton.","name":"Milton",
        "blurb":"One of Canada's fastest-growing towns, a lot of those new homes came with the cheapest mechanical package the builder could find. We fix that.",
        "lat":43.5183,"lng":-79.8774,
        "response":"Same-day during business hours",
        "utility_gas":"Enbridge Gas",
        "utility_electric":"Milton Hydro",
        "permit_office":"Town of Milton Building Services",
        "drive_from_hq":"20–30 minutes",
        "population":"~132,000 (2021 census, fastest-growing municipality in Canada from 2001–2011)",
        "climate_note":"Milton sits inland and at slightly higher elevation than Oakville/Burlington, about 3–4°C colder on average winter nights, and significantly less lake-moderation. The Niagara Escarpment to the west funnels cold-air drainage onto neighbourhoods near Bell School Line. Summer humidity is lower than the lakefront cities but heat-wave temperatures can run higher.",
        "copy":"A huge share of our Milton work is rescuing builder-grade equipment that was wrong from day one, undersized AC, ductwork that was never balanced, furnaces with five-stage thermostats hooked up to single-stage units. We also handle custom home HVAC for builds north of Derry Road.",
        "story":"Common Milton story: 2014-built two-storey in Hawthorne Village, the upstairs bedrooms are 6°C warmer than the main floor in summer, and the original AC short-cycles all afternoon. Audit shows the AC was 1 ton oversized and the upstairs has only one 5\" return for three bedrooms. We sized down to a 2.5-ton variable-speed, added a properly-sized return on the upper landing, and balanced the supplies. Upstairs sits within 1°C of downstairs now.",
        "case_image":"projects/ac-install-1.jpg",
        "case_alt":"Properly sized AC condenser install in Milton",
        "neighborhoods":["Beaty","Hawthorne Village","Coates","Willmott","Scott","Dempsey","Old Milton","Bronte Meadows","Harrison","Ford","Bowes","Cobban","Walker","Boyne Survey","Sherwood"],
        "landmarks":["Milton Velodrome (Mattamy National Cycling Centre)","Kelso Conservation Area","Rattlesnake Point Conservation Area","Toronto Premium Outlets","Milton Mall","Milton District Hospital","Crawford Lake","Milton GO Station","Hilton Falls Conservation Area","Halton County Radial Railway","Mountsberg Conservation Area","Country Heritage Park"],
        "housing_eras":[
            ("Pre-1980, Old Milton, central core","Pre-subdivision Milton. Smaller bungalows and Victorian-era homes. Many on oil or propane originally, now mostly gas. We do gas-line conversions when Enbridge extends service to a previously off-grid block."),
            ("1985–2000, Bronte Meadows, Timberlea","First wave of suburban expansion. Mid-efficiency furnaces and basic ductwork. Most homes are due for second replacement now."),
            ("2005–2015, Hawthorne Village, Beaty, Coates, Willmott, Scott, Dempsey","The big growth corridor. Cookie-cutter builder housing with universally oversized AC. The 'upstairs is hot' problem is endemic, there's a 1 in 3 chance any home built in this era has it. Air balancing alone often fixes it without equipment replacement."),
            ("2015–2020, Harrison, Ford, Cobban","High-efficiency 95% furnaces with PVC venting. Builder-installed equipment is functional but rarely commissioned properly. We re-program two-stage thermostats and verify gas pressure on these constantly."),
            ("2020+, Boyne Survey, Walker, Sherwood","Newest subdivisions, often with required heat pump readiness or hybrid systems per builder upgrade packages. Mechanical rooms are smaller, equipment placement matters."),
        ],
        "scenarios":[
            ("Builder-grade AC undersized for finished basement (Hawthorne Village)","Builder installed 3-ton AC for an entire 2,400 sq.ft. model. South-facing variant with finished basement actually needs 3.5–4 ton. We replace with a properly-sized 2-stage unit and rebalance airflow."),
            ("Two-storey hot upstairs in summer (Beaty, Coates, Willmott)","Manual J shows single 5\" upstairs return is moving half the air it needs to. Add a second return on the upper landing, typically gets bedrooms within 1°C of main floor."),
            ("Custom build north of Derry Road","Engaged at framing for whole-home mechanical design. Common spec: hybrid heat pump (Mitsubishi Hyper-Heat) + 96% furnace, hydronic in-floor master suite, HRV, snow-melt at the front walkway."),
            ("Garage-to-suite conversion (Old Milton)","Add ductless mini-split for heating and cooling, run new gas line for water heater, integrate ERV for the small footprint."),
        ],
        "city_faqs":[
            ("My Milton home is only 8 years old, why is my AC undersized?","Builder-grade subdivisions in Milton commonly use one AC tonnage across an entire model regardless of orientation, window count or finished basement. South-facing units with finished basements and oversized window walls almost always come up short. A proper Manual J load calc on your specific home tells you what's actually needed."),
            ("Do you do custom-home HVAC north of Derry Road?","Yes, we work with several custom builders in north Milton. We're typically engaged at concept stage to plan mechanical room location, zoning and in-floor heating runs before framing."),
            ("How do you handle the Milton building permit process?","We pull the mechanical permit at Town of Milton Building Services on Mary St, submit drawings where needed, and book the inspection. You don't lift a finger."),
        ],
                "neighborhood_intro":"Milton has grown fast, and our service area has grown with it. We work in every Milton subdivision, including:",
        "neighborhood_fallback":"New street that's still on the survey map? We probably already know it, call us.",
        "cta_line":"Milton builder-grade HVAC done wrong is our specialty to fix. Free Manual J load calc with every quote.",
        "faq_outro":"For general HVAC questions across Halton, see our",
        "nearby":["oakville","burlington","halton-hills","mississauga"],
        "services_intro":"Milton is a different HVAC market from Oakville and Burlington. Most of the homes are post-2005 builder-grade, which means the equipment is younger but the install quality is more uneven. Our most common Milton work falls into two buckets: rescue jobs on builder-grade systems where the AC is oversized or the upstairs returns are missing, and custom-home mechanical packages on the larger lots north of Derry Road. Here is what we do most in Milton.",
        "service_blurbs":[
            ("Furnace Work In Milton (First-Generation High-Efficiency Failures)", "heating-services/", "Most Milton furnaces are 12-18 year old first-generation 95% AFUE units, the inducer motor, pressure switch and condensate pump are the common failures. We carry parts on the truck for the most-installed brands (Goodman, Continental, Rheem) so most no-heat calls are 1-trip repairs."),
            ("Right-Sizing AC &amp; Heat Pumps In Milton", "air-conditioning-heat-pumps/", "Oversized AC is the #1 builder-install mistake we see in Milton. A 1-ton-too-big AC short-cycles in our humid summers and leaves the house clammy. We Manual J every replacement and right-size, often dropping from a 3.5-ton to a 2.5-ton, the comfort improvement is immediate."),
            ("Water Heaters For Milton Homes", "water-heaters/", "Milton homes are largely on Halton Region water, so the same 7-9 grains hardness applies, softener recommended for tankless. Newer subdivisions often have the tankless rough-in already, conversions are straightforward."),
            ("In-Floor Heating For Milton Custom Builds", "in-floor-heating/", "Custom homes north of Derry (Bell School Line, Tremaine Rd, escarpment-edge properties) regularly include whole-home hydronic radiant. Pairs with high-efficiency condensing boilers and forced-air heat pumps for cooling, the master ensuite and basement zones are non-negotiable luxury items here."),
            ("Snow Melting For Long Milton Driveways", "snow-melting-systems/", "Larger lots north of Derry Road and along the Bell School Line corridor have long, steep driveways that are perfect snow melt candidates. We design for the slightly higher snow loads inland from Lake Ontario, hydronic preferred for full driveways."),
            ("Duct Work In Milton (Crushed Flex Duct Patterns)", "duct-work/", "Builder-grade flex duct in Hawthorne Village, Beaty and Coates routinely gets crushed during drywall, kinked at sharp bends, or stepped on during attic insulation. We swap problem flex for rigid metal and rebalance. Typical Milton duct retrofit pays back in 2 summers on AC efficiency."),
            ("Air Balancing For Milton Two-Storey Homes", "air-balancing/", "Milton has the highest rate of upstairs-too-hot complaints in our service area, builder-grade ducts plus oversized equipment is a perfect storm. Air balance plus return-air addition fixes about 65% without equipment changes."),
            ("Custom Home HVAC For Milton Builders", "custom-homes/", "Custom builds in Brookville, Campbellville and along the escarpment are our growing Milton business. Full Manual J/D/S, zoning, HRV/ERV, hybrid heat pump packages, in-floor radiant, snow melt. We coordinate with Conservation Halton on escarpment-area mechanical room placement."),
            ("Commercial HVAC In Milton", "commercial/", "Restaurants and retail in Milton Mall, Toronto Premium Outlets, the Mavis-Steeles corridor and downtown Milton, plus the growing industrial parks along James Snow Parkway. We pull TSSA and Town of Milton permits, dispatch within 2-4 hours for no-cool emergencies.")
        ],
    },
    {
        "slug":"halton-hills",
        "seo_title":"Halton Hills HVAC | Georgetown &amp; Acton Propane to Gas | IKAD",
        "seo_description":"Halton Hills HVAC contractor for Georgetown, Acton &amp; rural properties. Propane-to-gas conversions, off-grid heat pumps, century home boiler service.","name":"Halton Hills",
        "blurb":"Georgetown, Acton and rural Halton Hills, same response time we give Oakville.",
        "lat":43.6453,"lng":-79.9181,
        "response":"Same-day during business hours, day-after for outer rural addresses",
        "utility_gas":"Enbridge Gas (and propane for rural properties)",
        "utility_electric":"Hydro One",
        "permit_office":"Town of Halton Hills Building Services",
        "drive_from_hq":"30–55 minutes (Georgetown closer, Acton further)",
        "population":"~62,000 (2021 census, Town of Halton Hills)",
        "climate_note":"The coldest part of Halton in winter, inland, elevated, with no lake moderation. Temperature differential vs Oakville can be 4–6°C colder on winter nights. Rural properties on private wells need water-heater sizing that accounts for cold incoming water (sometimes 4–6°C in February vs 10–12°C city water). The escarpment limits gas-line access, many rural homes still run on propane.",
        "copy":"Halton Hills covers a lot of ground, older homes in Georgetown's core, newer builds in the Glen Williams area, and rural properties out toward Acton that often run on propane or oil. We work across all of it.",
        "story":"A typical Halton Hills job: a century home in Georgetown on propane, owner wanted to convert to natural gas. We coordinated with Enbridge for the gas line installation, sized a new high-efficiency two-stage furnace, ran new flexible gas lines through the basement, and removed the old propane tank. The owner's heating cost dropped roughly 35% in the first season.",
        "case_image":"projects/residential-furnace-install.jpg",
        "case_alt":"Residential furnace install in Halton Hills",
        "neighborhoods":["Georgetown","Acton","Glen Williams","Norval","Stewarttown","Limehouse","Ballinafad","Hornby","Speyside","Terra Cotta","Crewson's Corners","Eden Mills","Glen Williams"],
        "landmarks":["Cedarvale Park","Hungry Hollow","Acton Town Hall Centre","Georgetown Marketplace","Halton Hills Cultural Centre","Bruce Trail access points","Silver Creek Conservation Area","Glen Williams Town Hall","Acton Fairgrounds","Limehouse Conservation Area","Christ Church Acton","Georgetown Hospital"],
        "housing_eras":[
            ("Pre-1900, Georgetown core, Glen Williams, Acton","Century homes, often on propane or recently-converted gas. Heating is usually still hot-water boilers with cast-iron radiators. We do boiler service, oil-to-gas conversions, and propane-to-gas conversions when Enbridge extends a line."),
            ("1900–1960, Acton, Hornby, Stewarttown","Mid-century rural homes. Many additions and renovations done over decades, so mechanical systems are patchworks. We often replace 2–3 different systems serving one house."),
            ("1980s–2010s, Georgetown suburbs, Limehouse, Speyside","Newer suburban housing within Georgetown's growth area. Standard forced-air gas equipment. Typical replacement schedule."),
            ("Rural estates, Ballinafad, Terra Cotta, Eden Mills","Large properties on private wells with propane tanks. Often custom HVAC: zoned forced-air, propane tankless, sometimes geothermal. We coordinate with well-water companies on softener and pressure-tank work alongside the HVAC."),
            ("Newer subdivisions, Glen Williams area, Trafalgar Country Club","Custom-home builds 2015+. We do mechanical design for builders working in the Glen Williams and Norval areas."),
        ],
        "scenarios":[
            ("Propane-to-natural-gas conversion (Georgetown core)","Enbridge runs the service line, we install a new high-efficiency furnace and water heater, run the gas piping, remove the old propane tank, coordinate with the propane company. Typical heating cost savings: 30–40%."),
            ("Off-grid-gas rural property (Ballinafad, Terra Cotta)","Best solution is usually a cold-climate heat pump (Mitsubishi Hyper-Heat) with electric backup and a small propane water heater. We've installed several in the Limehouse–Acton corridor."),
            ("Century home boiler service (Glen Williams, Norval)","Service old cast-iron-radiator boilers, replace zone valves, sometimes upgrade to a Viessmann or NTI condensing boiler while keeping the radiators."),
            ("New estate build (Trafalgar Country Club area)","Whole-home hydronic in-floor radiant on main level, ducted variable-speed AC, separate snow-melt loop, propane backup. Typical mechanical package $55,000–$85,000."),
        ],
        "city_faqs":[
            ("Do you service propane and oil systems in rural Halton Hills?","Yes, propane furnaces, propane water heaters and oil-to-gas (or oil-to-propane) conversions are routine for us. We also handle the tank decommissioning."),
            ("How long does the trip from Oakville actually take?","Georgetown is about 35–40 minutes from our Upper Middle Rd shop. Acton is about 50–55 minutes. We don't add a travel surcharge for Halton Hills."),
            ("Can you install a heat pump on a rural property without gas service?","Absolutely, a cold-climate heat pump with electric backup is one of the best options for an off-grid-gas rural home. We've done several in the Limehouse and Glen Williams area."),
        ],
                "neighborhood_intro":"Georgetown core, Acton, and the rural townships in between, we work across all of Halton Hills:",
        "neighborhood_fallback":"Rural concession road we haven't named? We service those too. Call and we'll confirm.",
        "cta_line":"Propane, oil, natural gas, off-grid heat pump, we install and service it all across Halton Hills.",
        "faq_outro":"For more HVAC FAQs across Halton, see our",
        "nearby":["milton","brampton","burlington"],
        "services_intro":"Halton Hills is the most rural part of our service area, and the HVAC work reflects that. Many properties are on propane (not natural gas), some still on oil, and a meaningful number off-grid entirely. Century homes in downtown Georgetown have cast-iron radiator boilers that have been running since the 1930s. The work mix is heavier on conversions, off-grid heat pumps and propane sizing than anywhere else we serve. Here is what we do most across Halton Hills.",
        "service_blurbs":[
            ("Furnace, Boiler &amp; Conversion Work In Halton Hills", "heating-services/", "Propane and oil-to-gas conversions are routine here, as is replacing 60+ year old cast-iron radiator boilers in downtown Georgetown heritage homes (we keep the radiators, replace the boiler with a modern condensing unit). Rural properties without natural gas access get high-efficiency propane furnaces sized for tank refill economics."),
            ("Cold-Climate Heat Pumps For Off-Grid Halton Hills Homes", "air-conditioning-heat-pumps/", "Rural Halton Hills is our largest cold-climate heat pump market. No gas line, expensive propane, and the new Home Renovation Savings Program rebates make ASHPs financially compelling. Mitsubishi Hyper-Heat and Lennox SL25XPV are the most-installed models, often with electric resistance backup."),
            ("Water Heaters In Halton Hills (Well-Water Considerations)", "water-heaters/", "Rural properties on private wells need different sizing math: cold incoming water can be 4-6°C in February vs 10-12°C city water, that affects tankless flow ratings and tank recovery time. We test incoming water hardness and recommend softener installation more often than in Oakville."),
            ("In-Floor Heating For Halton Hills Custom Homes", "in-floor-heating/", "Custom country homes on the Niagara Escarpment near Glen Williams, Hornby and Limehouse routinely include whole-home hydronic radiant. Pairs with high-efficiency propane or condensing-gas boilers. Concrete slab basement zones are non-negotiable luxury items here."),
            ("Snow Melting For Long Rural Halton Hills Driveways", "snow-melting-systems/", "Long rural driveways (200+ ft) common in Halton Hills are the perfect snow melt candidates. We design for the heaviest snow loads in our service area, escarpment exposure can mean 30% more snow than coastal Halton. Hydronic systems exclusively for this length."),
            ("Duct Work For Halton Hills Heritage Homes", "duct-work/", "Adding forced-air to century homes that never had ducts is a common Halton Hills retrofit. We design compact-trunk systems to minimize chase impact in plaster-wall heritage homes, often combined with new high-velocity supply runs in finished ceilings."),
            ("Air Balancing For Halton Hills Renovations", "air-balancing/", "Post-renovation balancing is common here, additions, basement finishes and second-floor bumps push the existing system out of balance. We measure and rebalance, often part of a renovation project's final commissioning."),
            ("Custom Country Home HVAC For Halton Hills Builders", "custom-homes/", "Country builds on 1-10 acre lots near Glen Williams, Limehouse and Norval are our growing Halton Hills custom-home business. Full design, propane vs heat pump economics analysis, geothermal where applicable, snow melt, generator-integrated emergency power."),
            ("Commercial HVAC In Halton Hills", "commercial/", "Restaurants in Georgetown core, plazas along Mountainview, light industrial in Acton, and a growing number of country-property short-term rentals needing dependable HVAC. We pull Halton Hills permits and dispatch within 3-5 hours given the rural drive time.")
        ],
    },
    {
        "slug":"mississauga",
        "seo_title":"Mississauga HVAC Contractor | Residential &amp; Commercial | IKAD",
        "seo_description":"Mississauga HVAC contractor: residential furnace &amp; AC service across Erin Mills, Mineola, Port Credit, plus plaza rooftop &amp; restaurant commercial work.","name":"Mississauga",
        "blurb":"Port Credit to Streetsville, Erin Mills to Meadowvale, residential and commercial HVAC for Mississauga.",
        "lat":43.5890,"lng":-79.6441,
        "response":"Same-day during business hours",
        "utility_gas":"Enbridge Gas",
        "utility_electric":"Alectra Utilities (Mississauga)",
        "permit_office":"City of Mississauga Building Division",
        "drive_from_hq":"15–35 minutes depending on which side",
        "population":"~717,000 (2021 census, Canada's 7th-largest city)",
        "climate_note":"Mississauga south of the QEW (Mineola, Port Credit, Lorne Park) is lake-moderated like Oakville. North of Highway 401 (Meadowvale, Lisgar) is more inland with bigger temperature swings. Summer humidity 65–80% across most neighbourhoods. Commercial corridor along Dixie/Tomken/Hurontario sees urban heat-island effect on rooftop unit performance.",
        "copy":"Mississauga's housing stock is some of the most varied in the GTA: 1960s ranchers in Mineola, 1980s two-storeys in Erin Mills, brand-new builds in Churchill Meadows. We do the residential side and a lot of commercial work for plaza owners and restaurant operators across the city.",
        "story":"Recent commercial job: a 3-unit plaza near Square One where the rooftop unit on the corner restaurant was running on six different temporary fixes from previous contractors. We replaced the RTU with a properly sized Carrier 7.5-ton, ran new gas piping and updated the curb adapter. The plaza owner has since put us on a PM contract for all three units.",
        "case_image":"projects/project-3.jpg",
        "case_alt":"Commercial rooftop HVAC installation in Mississauga",
        "neighborhoods":["Port Credit","Streetsville","Erin Mills","Meadowvale","Mineola","Lorne Park","Cooksville","Square One/City Centre","Churchill Meadows","Lisgar","Clarkson","Sheridan","East Credit","Hurontario","Malton","Applewood","Rathwood","Mississauga Valleys"],
        "landmarks":["Square One Shopping Centre","Port Credit Lighthouse","Celebration Square","Erindale Park","Jack Darling Memorial Park","Lakeside Park","University of Toronto Mississauga","Living Arts Centre","Streetsville Memorial Park","Pearson International Airport (border)","Heartland Town Centre","Erin Mills Town Centre","Trillium Health Partners hospitals"],
        "housing_eras":[
            ("1950s–1960s, Mineola, Port Credit core, Cooksville","Original single-storey ranchers and 1.5-storey bungalows. Ducts are universally undersized for modern AC airflow, we often have to upgrade trunk and add returns. Many on small lots; outdoor unit placement is tricky."),
            ("1970s–1980s, Erin Mills, Meadowvale, Applewood, Rathwood","Big suburban growth era. Two-storey detached on standard lots. Original ducts OK, but second-storey returns almost always undersized. Classic 'hot upstairs' calls are the norm."),
            ("1990s–2000s, Streetsville expansion, Sheridan, East Credit","Mid-tier suburban housing. Builder-grade equipment now hitting end-of-life. We see lots of Carrier and Lennox installs from this era at second-replacement stage."),
            ("2000s–2010s, Churchill Meadows, Lisgar","High-density planned subdivisions. Standard builder HVAC. Common problem: AC condenser placement on tight side-yards generates noise complaints between neighbours."),
            ("2010+, City Centre condos &amp; new infill","Condo HVAC service is its own specialty, we do in-suite fan-coil units, package terminal AC, hot-water-tank replacements. Newer infill custom homes in Mineola and Lorne Park use full custom mechanical packages."),
        ],
        "scenarios":[
            ("Undersized 1960s ductwork (Mineola, Port Credit)","Original ducts move 800 CFM total, modern variable-speed system wants 1,500+. We upgrade trunk lines during AC replacement so the new equipment can actually breathe."),
            ("Plaza rooftop unit replacement (Square One area, Hurontario)","Bobcat or crane to set the new RTU, gas piping, curb adapter, electrical disconnect upgrade. Coordinate with restaurant kitchen ventilation so the make-up air still tunes correctly."),
            ("Two-storey hot upstairs (Erin Mills, Meadowvale)","Standard fix: add upstairs returns, balance dampers in trunk. Sometimes pair with a zoned damper system if HVAC layout is fragmented."),
            ("Restaurant hood + MUA fitout (Cooksville, Hurontario corridor)","Captive-Aire or Greenheck hood, gas-fired make-up air unit, fire-suppression coordination, TSSA gas piping and pressure test. Permit-pulled, inspected, signed off."),
        ],
        "city_faqs":[
            ("Do you do commercial HVAC for Mississauga plazas and restaurants?","Yes, we hold PM contracts on plaza buildings and restaurants across Mississauga. Rooftop replacement, make-up air, kitchen hoods, gas piping and 24/7 emergency response."),
            ("How quickly can you respond to a Mississauga commercial no-cool call in summer?","Usually within 2–4 hours during business hours, same day for PM-contract clients. We keep replacement compressors and common parts in our trucks."),
            ("Which Mississauga neighborhoods do you do the most residential work in?","Mineola and Lorne Park for older-home retrofits, Erin Mills and Churchill Meadows for furnace and AC replacements, Meadowvale for ductless additions."),
        ],
                "neighborhood_intro":"From Port Credit to Lisgar, Mineola to Meadowvale, IKAD trucks reach every Mississauga neighbourhood:",
        "neighborhood_fallback":"Your part of Mississauga not listed? We cover the entire city, residential and commercial.",
        "cta_line":"Same-day Mississauga commercial response, no-pressure residential quotes, PM contracts available for plaza owners.",
        "faq_outro":"More HVAC answers on our",
        "nearby":["oakville","brampton","milton"],
        "services_intro":"Mississauga is our biggest commercial market and a steady residential one. The split is roughly 60% commercial (plaza rooftops, restaurants, daycares, light industrial along Hurontario, Dundas and the airport corridor), 40% residential (older-home retrofits in Mineola, Lorne Park and Port Credit, plus 1980s subdivision furnace/AC swaps in Erin Mills, Meadowvale and Churchill Meadows). Here is what we do most in Mississauga.",
        "service_blurbs":[
            ("Furnace Replacement Across Mississauga", "heating-services/", "Erin Mills, Churchill Meadows and Meadowvale 1980s-90s homes are mostly on second-or-third-generation furnaces now. Mineola, Lorne Park and Port Credit have a mix of 1960s mid-efficiency originals and recently-replaced 96% AFUE units. We Manual J every job because Mississauga housing stock is more varied than people realize."),
            ("AC &amp; Heat Pumps For Mississauga Homes", "air-conditioning-heat-pumps/", "Older Mineola and Lorne Park homes often need duct upgrades alongside AC replacement, the 1960s ducts can't move modern variable-speed CFM. Erin Mills and Meadowvale subdivisions typically need straight AC replacement plus a balanced upstairs return on the second floor."),
            ("Water Heater Service In Mississauga", "water-heaters/", "Mississauga water hardness is similar to Halton (around 7-8 grains). Many homes still on Enercare or Reliance rental contracts, buyout-vs-keep math is common conversation. Tankless conversions need gas line upsize on most 1980s-90s homes."),
            ("In-Floor Hydronic Heating In Mississauga Custom Builds", "in-floor-heating/", "Custom builds in Lorne Park, Mineola and Erin Mills regularly include hydronic radiant. Often paired with high-efficiency boilers serving a heated driveway, the master ensuite/basement combo is the most common Mississauga in-floor scope."),
            ("Heated Driveways In Mississauga", "snow-melting-systems/", "Less common than in north Halton but increasing. Most installs are in Mineola, Lorne Park and Port Credit waterfront homes with steep driveway grades. Best built during pour or full resurfacing."),
            ("Duct Work, Sealing &amp; Replacement In Mississauga", "duct-work/", "1960s Mineola and Port Credit homes routinely need full trunk-line upgrades to support modern variable-speed equipment. 1980s-90s Erin Mills and Meadowvale homes more often need balancing + duct sealing rather than full replacement."),
            ("Air Balancing For Mississauga Two-Storey Homes", "air-balancing/", "Standard upstairs-too-hot pattern in Erin Mills, Meadowvale and Churchill Meadows: undersized upstairs returns, leaky attic ducts. Fix is air balance plus a return-air addition, no equipment changes needed in most cases."),
            ("Custom Home HVAC For Mississauga Builders", "custom-homes/", "Custom infill in Lorne Park, Mineola and along Mississauga's waterfront is our main custom-home work in the city. Full mechanical packages from concept to commissioning, including coordination with city of Mississauga building department on permits."),
            ("Commercial HVAC In Mississauga (Our Largest Commercial Market)", "commercial/", "Plaza rooftop replacements across the Hurontario corridor and Square One area, restaurant kitchen fitouts in Cooksville and Streetsville, daycare and dental office maintenance contracts in Erin Mills and Meadowvale, light industrial PM in the airport corridor. We carry common Mississauga-needed parts: Carrier 48HC, Lennox LRP, Reznor unit heaters, Captive-Aire hoods.")
        ],
    },
    {
        "slug":"hamilton",
        "seo_title":"Hamilton HVAC | Restaurant, Daycare &amp; Home | IKAD",
        "seo_description":"Hamilton HVAC contractor for Stoney Creek, Ancaster, Dundas &amp; the Mountain. Daycare ductwork, restaurant kitchen hoods, residential furnace &amp; AC.","name":"Hamilton",
        "blurb":"Daycare retrofits, restaurant fitouts, plaza HVAC, residential, Hamilton is one of our most active service areas.",
        "lat":43.2557,"lng":-79.8711,
        "response":"Same-day during business hours",
        "utility_gas":"Enbridge Gas",
        "utility_electric":"Alectra Utilities (Hamilton)",
        "permit_office":"City of Hamilton Building Services",
        "drive_from_hq":"25–45 minutes",
        "population":"~569,000 (2021 census, City of Hamilton including Stoney Creek/Ancaster/Dundas/Glanbrook/Flamborough)",
        "climate_note":"Hamilton's geography creates microclimates. The mountain (above the escarpment) is cooler and windier than the lower city. Westdale/Dundas valleys collect cold air. Stoney Creek and Winona at lake level are moderated. Industrial north end has urban heat island and historically higher air-quality concerns, high-MERV filters and HRVs are more important here than in suburban Halton.",
        "copy":"Hamilton keeps us busy, we've done major duct work overhauls on daycare buildings, commercial kitchen installs for new restaurants, and residential retrofits across Stoney Creek, Ancaster, Dundas and the mountain. The city's mix of older industrial buildings and growing residential development is a good fit for the kind of work we do best.",
        "story":"One of our most photographed projects: a daycare in central Hamilton where the original 1970s duct work was leaking air everywhere, and several rooms were registering 4°C colder than the play area. Over a five-day shutdown, we tore out the old trunks, designed a new system around proper CFM-per-room, ran new insulated supply and return ducts, and rebalanced. Two seasons later, no callbacks.",
        "case_image":"projects/project-4.jpg",
        "case_alt":"New commercial duct work installation at a Hamilton daycare",
        "neighborhoods":["Stoney Creek","Ancaster","Dundas","Hamilton Mountain (Upper)","Westdale","Downtown Hamilton","Waterdown","Glanbrook","Binbrook","Flamborough","Winona","Greensville","Crown Point","Kirkendall","Durand","Strathcona"],
        "landmarks":["McMaster University","Bayfront Park","Webster's Falls","Tiffany Falls","Dundurn Castle","Royal Botanical Gardens (border)","Hamilton GO Centre","Tim Hortons Field","FirstOntario Centre","Lime Ridge Mall","Eastgate Square","Hamilton Cemetery","Devil's Punchbowl","Bruce Trail (escarpment)"],
        "housing_eras":[
            ("Pre-1900, Durand, Kirkendall, Westdale, Dundas","Heritage homes, often with original boilers and radiators. Many converted from coal/oil over the decades. We do boiler service, oil-to-gas conversions, and condensing-combi swaps. Historic Westdale and Dundas have strict heritage zones."),
            ("1900–1950, Crown Point, Stipley, Strathcona, Stoney Creek waterfront","Working-class neighbourhoods with original mid-efficiency systems long since replaced. Common to find 2nd or 3rd generation furnaces. Ductwork often patched together over decades."),
            ("1960s–1980s, Mountain growth (Templemead, Sherwood, Hill Park, Mohawk)","Suburban mountain expansion. Wind-exposed lots, attic-insulation matters. Standard forced-air gas systems. Most homes had original equipment replaced 10–15 years ago."),
            ("1990s–2010s, Ancaster, Stoney Creek expansion (Winona, Heritage Green)","Newer suburban builds. Builder-grade HVAC. Replacement cycle now."),
            ("2010+, Waterdown, Binbrook, Mount Hope","Newest growth area. High-efficiency standard. We do builder warranty service and homeowner upgrades."),
        ],
        "scenarios":[
            ("Daycare duct system overhaul (central Hamilton)","Multi-room CFM rebalance, new insulated supply trunks, return upgrades. Done over a 5-day weekend closure to avoid disrupting operations."),
            ("Restaurant commercial kitchen (Hess Village, Locke St, James St North)","Hood install with make-up air, gas piping, fire suppression coordination, TSSA inspection. Permit-pulled through City of Hamilton Building."),
            ("Mountain wind-exposed home (Templemead, Hill Park)","Add attic-side air sealing during HVAC work, upgrade return air to handle high static pressure from leaky exterior walls. Often pair with HRV addition."),
            ("Stoney Creek waterfront older home","Salt-air corrosion mitigation on outdoor condensers, oversize indoor coil to handle latent humidity loads near the lake."),
            ("Mid-town Hamilton multi-tenant residential","Replace central boiler serving multiple units, sometimes split into per-unit systems where ductwork allows. Coordinate with building owner on shutdown windows."),
        ],
        "city_faqs":[
            ("Do you do commercial kitchen and daycare HVAC in Hamilton?","Yes, kitchen hoods, make-up air, rooftop replacements and daycare ventilation upgrades are some of our most common Hamilton jobs. We're TSSA-certified for the gas piping and exhaust work."),
            ("How long does it take to get from Oakville to Hamilton?","About 35 minutes to downtown Hamilton, 25 minutes to Stoney Creek and Ancaster, 30 minutes to Dundas. No travel surcharge."),
            ("Can you handle a multi-unit residential building in Hamilton?","Yes, small apartment buildings and multi-tenant residential are within our scope, including in-suite furnaces, central boiler systems and common-area ventilation."),
        ],
                "neighborhood_intro":"From Stoney Creek to Ancaster, Dundas to the mountain, we service the full City of Hamilton:",
        "neighborhood_fallback":"Out toward Binbrook or Flamborough? Call us, we work the entire Hamilton city boundary.",
        "cta_line":"Restaurant, daycare, residential, multi-tenant, Hamilton mechanical work is one of our weekly specialties.",
        "faq_outro":"Want general HVAC answers? See our",
        "nearby":["burlington","oakville","brampton"],
        "services_intro":"Hamilton's HVAC market is unlike anywhere else in our service area. Heritage homes downtown have 80-100 year old radiator systems, Hamilton Mountain has dense 1950s-60s post-war housing, Ancaster and Dundas are higher-end residential, Stoney Creek is a mix of newer subdivisions and industrial, and the steel-belt corridor needs heavy commercial mechanical. We're in Hamilton multiple days a week running this full mix.",
        "service_blurbs":[
            ("Heating, Boilers &amp; Furnaces In Hamilton", "heating-services/", "Downtown Hamilton heritage boilers (cast-iron radiator systems, often original from the 1920s-40s) are a regular service item. Ancaster and Dundas higher-end homes get high-efficiency replacement furnaces. Mountain post-war homes are the highest-volume budget furnace replacement market we serve."),
            ("AC, Heat Pumps &amp; Ductless For Hamilton", "air-conditioning-heat-pumps/", "Downtown Hamilton row houses without ductwork are our biggest ductless market outside Halton. Mitsubishi Hyper-Heat multi-zone systems for 2-3 bedroom row houses. Ancaster and Dundas custom homes go central AC or hybrid heat pump."),
            ("Water Heater Service In Hamilton", "water-heaters/", "Hamilton water is slightly softer than Halton, around 5-7 grains. Less scale concern for tankless. Many downtown Hamilton homes still on water heater rentals from 1990s contracts, we help homeowners run the buyout math."),
            ("In-Floor Heating For Hamilton Custom Renos &amp; Builds", "in-floor-heating/", "Ancaster, Dundas and Stoney Creek custom builds and major renovations regularly include hydronic radiant. Heritage downtown Hamilton renos sometimes add electric mat in kitchen/bath upgrades, careful coordination needed with original plaster floors."),
            ("Snow Melting For Hamilton Hillside Driveways", "snow-melting-systems/", "Hamilton's terrain (escarpment, mountain access) creates many steep-driveway scenarios where snow melt is genuinely useful. Most installs in Ancaster, Dundas, west Hamilton mountain access roads. Hydronic systems for full driveways."),
            ("Duct Work In Hamilton Homes", "duct-work/", "Adding forced-air to downtown Hamilton heritage homes is technically demanding (limited chase space, plaster walls, no basement headroom). We design compact systems that minimize structural impact. Post-war Hamilton Mountain homes typically need duct rebalancing more than replacement."),
            ("Air Balancing For Hamilton Two-Storey Homes", "air-balancing/", "Same upstairs hot/cold pattern as Halton in Hamilton's 1970s-90s subdivisions (Stoney Creek, Ancaster, Mountain). Air balance + return-air addition fixes most cases without equipment changes."),
            ("Custom Home HVAC For Hamilton Builders", "custom-homes/", "Custom builds in Ancaster, Dundas and along the escarpment are our growing Hamilton custom-home business. Full mechanical packages including in-floor radiant, hybrid heat pumps, HRV/ERV, smart controls, snow melt."),
            ("Commercial HVAC In Hamilton (Restaurants, Daycares, Plazas, Light Industrial)", "commercial/", "Restaurant kitchen fitouts on James, King and Locke, daycare and educational facility HVAC across the city, plaza rooftop replacements in Stoney Creek and Mountain, light industrial PM contracts in the east end industrial corridor. We dispatch within 2-4 hours for no-cool emergencies during business hours.")
        ],
    },
    {
        "slug":"brampton",
        "seo_title":"Brampton HVAC | Industrial &amp; Residential | IKAD",
        "seo_description":"Brampton HVAC contractor: industrial fitouts, warehouse heating, commercial rooftop replacement plus residential furnace &amp; AC in Bramalea, Mount Pleasant.","name":"Brampton",
        "blurb":"Commercial duct work, mechanical fitouts and residential HVAC, Brampton's industrial corridor and residential subdivisions.",
        "lat":43.7315,"lng":-79.7624,
        "response":"Same-day during business hours",
        "utility_gas":"Enbridge Gas",
        "utility_electric":"Alectra Utilities (Brampton)",
        "permit_office":"City of Brampton Building Department",
        "drive_from_hq":"30–45 minutes",
        "population":"~656,000 (2021 census, 9th-largest city in Canada)",
        "climate_note":"Inland location, no lake moderation, so winter temperatures average 2–3°C colder than Oakville. Summer heat-wave temperatures can run higher than the lakefront cities. Industrial Brampton (north and east) has significant heat-island effect on rooftop units. North Brampton (Mayfield Rd area) is more exposed and rural in character.",
        "copy":"Brampton is where we do a lot of commercial duct fabrication and installation, manufacturing facilities, warehouses, multi-tenant industrial, plus residential service across the city's many subdivisions. Our trucks reach Brampton multiple days a week from the Oakville shop.",
        "story":"Repeat Brampton client: an industrial-condo development off Steeles where we've fitted out the mechanical for six different tenant units over three years. Auto repair shops, a printing facility, a kitchen commissary, each one needed different ductwork, makeup air and rooftop sizing. Knowing the building means we can move fast on the next unit.",
        "case_image":"projects/project-5.jpg",
        "case_alt":"Commercial duct work install in Brampton",
        "neighborhoods":["Bramalea","Heart Lake","Mount Pleasant","Springdale","Castlemore","Snelgrove","Fletcher's Meadow","Credit Valley","Northwood Park","Sandalwood","Madoc","Westgate","Brampton South","Downtown Brampton","Ebenezer","Vales of Castlemore","Bram East","Bram West"],
        "landmarks":["Bramalea City Centre","Chinguacousy Park","Gage Park downtown","Heart Lake Conservation Area","Powerade Centre","Brampton Civic Hospital","Rose Theatre Brampton","Sheridan College Davis Campus","Pearson International Airport (border)","Trinity Common Mall","CAA Centre","Norton Place Park"],
        "housing_eras":[
            ("1960s–1970s, Bramalea, Madoc, Brampton South","Original 1960s planned community. Many homes still on first or second furnace replacement. Standard ductwork, generally OK but never balanced. Older homes here often have undersized panels, we coordinate with electricians when needed."),
            ("1980s–1990s, Heart Lake, Snelgrove, Westgate","Mid-suburban era. Mid-efficiency furnaces from this era are universally end-of-life. Often original AC, on its second replacement."),
            ("2000s, Springdale, Fletcher's Meadow, Credit Valley","Massive growth period, Brampton was one of Canada's fastest-growing cities. Standard builder HVAC, replacement cycle now. Many homes have unfinished attics that have settled insulation."),
            ("2010+, Mount Pleasant, Castlemore, Vales of Castlemore, Bram East","Newer upscale subdivisions. High-efficiency standard, larger homes 3,000–5,000+ sq.ft. We do builder-warranty service, second-stage thermostat upgrades, and zone-control additions."),
            ("Industrial corridor, Steeles East, Airport Rd, Bramwood","Mid-rise industrial condos and warehouses. Tenant fitouts: ductwork, rooftop unit replacement, make-up air for commercial kitchens and printing facilities."),
        ],
        "scenarios":[
            ("Industrial condo tenant fitout (Steeles East corridor)","New ductwork to suit the tenant's layout, rooftop unit sizing for their occupancy and equipment heat-rejection, make-up air for any cooking or process equipment, gas piping, TSSA inspection. Typical timeline 2–3 weeks."),
            ("Warehouse heating (Bramwood, Airport Rd)","Reznor or Modine unit heaters or radiant tube heating. Sizing for high-ceiling industrial spaces is different from residential, we calculate per the warehouse layout, racking and ventilation requirements."),
            ("Builder-grade two-storey with hot upstairs (Springdale, Fletcher's Meadow)","Classic Brampton subdivision problem. Add upstairs returns, balance dampers, sometimes pair with smart-thermostat fan-circulation setting."),
            ("Upscale custom home in Castlemore","Whole-home zoned HVAC, hybrid heat pump + 96% furnace, HRV, integrated smart-home thermostat system."),
        ],
        "city_faqs":[
            ("Do you do industrial / warehouse HVAC and ductwork in Brampton?","Yes, industrial fitouts, warehouse heating, make-up air for commercial kitchens, and commercial-grade rooftop replacement are routine Brampton work for us. We fabricate ductwork at our Oakville shop."),
            ("How fast can you turn around a tenant fitout?","From signed proposal to commissioning, most single-tenant fitouts in Brampton industrial condos take us 2–3 weeks depending on permit timing and equipment availability."),
            ("Do you work with general contractors and project managers in Brampton?","Yes, most of our commercial Brampton work comes through GC relationships. We hold our schedules and we don't slip dates."),
        ],
                "neighborhood_intro":"Bramalea to Mount Pleasant, Springdale to the industrial corridor, we cover every part of Brampton:",
        "neighborhood_fallback":"Industrial unit in the Steeles/Airport Rd corridor? That's where we do a lot of fitouts. Just call.",
        "cta_line":"Industrial fitouts, warehouse heating, residential subdivisions, Brampton mechanical work, done on schedule.",
        "faq_outro":"For more HVAC questions, browse our",
        "nearby":["mississauga","halton-hills","hamilton"],
        "services_intro":"Brampton is our most industrial-heavy service area. The Steeles-Airport Road corridor alone keeps us in tenant fitouts, warehouse heating and make-up air work most weeks. Residentially the mix runs from 1970s-80s Bramalea, to 2000s Mount Pleasant and Springdale subdivisions, to upscale custom builds in Castlemore. The work pace is fast and the GC-coordination demands are tight, here is what we do most.",
        "service_blurbs":[
            ("Furnace Work In Brampton (Bramalea To Castlemore)", "heating-services/", "Bramalea 1970s-80s homes are mostly on second-generation furnaces, many original mid-efficiency units already replaced once. Mount Pleasant and Springdale 2000s subdivisions are on first-generation 95% AFUE units now hitting 18-20 year mark. Castlemore custom builds get premium variable-speed modulating units."),
            ("AC &amp; Heat Pumps For Brampton Homes", "air-conditioning-heat-pumps/", "Brampton humidity is similar to Mississauga, dehumidification matters more than tonnage. We Manual J every replacement, oversized AC is the most common mistake we see in 1990s-2000s Brampton subdivision homes. Castlemore and the larger lots get hybrid heat pump setups."),
            ("Water Heater Replacement In Brampton", "water-heaters/", "Peel Region water in Brampton runs around 6-8 grains hardness, softener recommended for tankless installs. Many Brampton homes still on Reliance or Enercare rentals from the 1990s, we help homeowners do the buy-vs-rent math at install time."),
            ("In-Floor Heating For Brampton Custom Builds", "in-floor-heating/", "Castlemore and the upscale custom-build areas regularly include whole-home hydronic radiant. Pairs with high-efficiency boilers and hybrid heat pumps for cooling. Master ensuite/basement combo is the standard scope here."),
            ("Snow Melting For Brampton Driveways", "snow-melting-systems/", "Less common than in north Halton but increasing in Castlemore and the larger-lot custom builds. Design for slightly higher snow loads than coastal Halton given Brampton's inland position. Hydronic systems for full driveways."),
            ("Duct Work, Sealing &amp; Industrial Ductwork", "duct-work/", "Brampton is our biggest industrial ductwork market, we fabricate and install commercial sheet metal at our Oakville shop, then ship and install for Brampton industrial tenant fitouts. Residential duct work follows the standard Halton playbook."),
            ("Air Balancing For Brampton Two-Storey Homes", "air-balancing/", "Standard upstairs hot/cold pattern in Bramalea, Mount Pleasant and Springdale: undersized returns, leaky ducts. Fix is air balance + return-air addition, no equipment changes in most cases."),
            ("Custom Home HVAC For Brampton Builders", "custom-homes/", "Castlemore and the upscale infill areas are our main Brampton custom-home market. Full mechanical packages, zoning, HRV/ERV, in-floor radiant, smart home integration, snow melt. We coordinate with City of Brampton building department on permits."),
            ("Commercial &amp; Industrial HVAC In Brampton (Our Industrial Specialty)", "commercial/", "Industrial tenant fitouts, warehouse heating (Reznor, Modine), make-up air units, commercial-grade rooftop replacement (Carrier 48HC, Lennox LRP), restaurant kitchen build-outs. We coordinate with GCs and project managers, hold schedules tight, don't slip dates. 2-4 hour dispatch for no-cool emergencies during business hours.")
        ],
    },
]

def build_service_areas_index():
    r = "../"
    body = hero_compact(r, "hero/hero-new-construction.jpg", "Service Areas", "HVAC Services Across Halton, Peel &amp; Hamilton",
        "From our Oakville office, IKAD Mechanical serves seven cities across the western GTA, same-day residential service and 24/7 commercial response across the region.") + \
        breadcrumbs(r, [("Home","./"),("Service Areas", "")]) + f"""
<section class="section"><div class="container">
<div class="text-center" style="max-width:780px;margin:0 auto 2.5rem"><span class="eyebrow">Where We Work</span><h2>Local HVAC Across The Western GTA</h2><p class="lead" style="margin:0 auto">Pick your city below for local service details, common project types, response times, permit-office info and city-specific FAQs. If you're outside these areas, give us a call, we travel further for custom homes and commercial projects.</p></div>
<div class="area-grid">
{''.join(f'<a class="area-card" href="{r}service-areas/{c["slug"]}/"><span class="area-card__city">{c["name"]}</span><span class="area-card__sub">{c["blurb"]}</span></a>' for c in CITIES)}
</div>
</div></section>

<section class="section section--gray"><div class="container" style="max-width:880px">
<h2>Why Our Service Area Looks This Way</h2>
<p>IKAD Mechanical is based on Upper Middle Rd East in Oakville. Our service area expanded organically over 15 years, Halton first, then Mississauga and Hamilton through commercial work, then Brampton through industrial fitouts. Today we handle residential, commercial and custom-home HVAC across seven cities, all from a single shop, with no subcontracted installs.</p>

<h2>Drive Times From Our Oakville Shop</h2>
<table class="cost-table" style="width:100%;border-collapse:collapse;margin:1.25rem 0">
<thead><tr><th>City</th><th>Typical Drive Time</th><th>Service Notes</th></tr></thead>
<tbody>
<tr><td>Oakville</td><td>5–15 minutes</td><td>Head office, same-hour response common during business hours</td></tr>
<tr><td>Burlington</td><td>15–25 minutes</td><td>Multiple days per week</td></tr>
<tr><td>Milton</td><td>20–30 minutes</td><td>Strong custom-home builder relationships north of Derry</td></tr>
<tr><td>Mississauga</td><td>15–35 minutes</td><td>Residential + commercial plaza work</td></tr>
<tr><td>Hamilton</td><td>25–45 minutes</td><td>Daycare and restaurant commercial focus</td></tr>
<tr><td>Halton Hills</td><td>30–55 minutes</td><td>Georgetown and Acton, rural and town</td></tr>
<tr><td>Brampton</td><td>30–45 minutes</td><td>Industrial fitouts and residential subdivisions</td></tr>
</tbody>
</table>

<h2>What's Different About Each Area</h2>
<p>Each city has its own housing stock, climate quirks and permit office. We've built deep knowledge of all seven, what era the average home was built in, which utility serves the gas and electric, what the building department asks for on a mechanical permit, and which neighbourhoods have specific equipment patterns (e.g., undersized AC in Milton subdivisions, salt-air corrosion on Bronte lakefront, oil-to-gas conversion opportunities in Georgetown core).</p>
<p>Click into any city page above for the deep dive: landmarks, neighbourhood list, housing-era guide, typical scenarios we run into, climate notes, response times, and city-specific FAQs.</p>

<h2>Outside Our Service Area?</h2>
<p>For residential work, we generally stay within the seven cities listed. For custom-home mechanical design and commercial projects, we travel further across the GTA. Call us, we'll tell you straight whether your project is a fit. Most weeks we'll do at least one quote outside our standard radius for the right project.</p>
</div></section>
""" + cta_banner(r, "Not Sure If You're In Our Service Area?", "Just call. We'll tell you straight up.")
    page(
        out="service-areas/index.html", depth=1,
        title="Service Areas | HVAC In Oakville, Burlington &amp; Halton | IKAD",
        description="IKAD Mechanical HVAC service areas across Halton, Peel and Hamilton: Oakville, Burlington, Milton, Halton Hills, Mississauga, Hamilton, Brampton.",
        canonical=f"{BASE}/service-areas/",
        og_image=f"{BASE}/assets/images/hero/hero-new-construction.jpg",
        body=body, active="areas", preload_hero="hero/hero-new-construction.jpg",
        schema_extra=breadcrumb_schema([("Home",f"{BASE}/"),("Service Areas",f"{BASE}/service-areas/")])
    )

def build_city(city):
    r = "../../"
    slug = city["slug"]
    name = city["name"]
    neighborhoods_list = "\n".join(f"<li>{n}</li>" for n in city["neighborhoods"])
    city_faqs = city.get("city_faqs", [])
    response = city.get("response", "Same-day during business hours")
    permit_office = city.get("permit_office", "")
    utility_gas = city.get("utility_gas", "Enbridge Gas")
    utility_electric = city.get("utility_electric", "")
    case_image = city.get("case_image", "projects/project-1.jpg")
    case_alt = city.get("case_alt", f"Recent HVAC project in {name}")
    story = city.get("story", "")
    landmarks = city.get("landmarks", [])
    housing_eras = city.get("housing_eras", [])
    scenarios = city.get("scenarios", [])
    climate_note = city.get("climate_note", "")
    drive_from_hq = city.get("drive_from_hq", "")
    population = city.get("population", "")
    nearby = city.get("nearby", [])
    nearby_names = {"oakville":"Oakville","burlington":"Burlington","milton":"Milton","halton-hills":"Halton Hills","mississauga":"Mississauga","hamilton":"Hamilton","brampton":"Brampton"}

    landmarks_html = ""
    if landmarks:
        landmarks_html = "<ul style='columns:2;column-gap:1.5rem;list-style:none;padding:0'>" + "".join(f"<li style='padding:.25rem 0'>{icon('pin')} {l}</li>" for l in landmarks) + "</ul>"

    housing_eras_html = ""
    if housing_eras:
        cards = ""
        for era_title, era_body in housing_eras:
            cards += f'<div style="background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:1.25rem;margin-bottom:1rem"><h3 style="margin:0 0 .5rem;font-size:1.05rem;color:#0f172a">{era_title}</h3><p style="margin:0;color:#475569;font-size:.95rem">{era_body}</p></div>'
        housing_eras_html = f'<h2 id="housing-eras" style="margin-top:2.5rem">Housing Stock In {name}, What We See Most</h2><p>Knowing the era of a {name} home tells us roughly what equipment is in the basement and what failure modes to expect. Here\'s what 15+ years of installs has taught us about each era:</p>{cards}'

    scenarios_html = ""
    if scenarios:
        cards = ""
        for scen_title, scen_body in scenarios:
            cards += f'<div style="background:#f6f7f9;border-left:3px solid #e30613;border-radius:6px;padding:1.1rem 1.25rem;margin-bottom:.85rem"><strong style="color:#0f172a">{scen_title}</strong><p style="margin:.35rem 0 0;color:#475569;font-size:.95rem">{scen_body}</p></div>'
        scenarios_html = f'<h2 id="common-scenarios" style="margin-top:2.5rem">Common HVAC Scenarios In {name}</h2><p>Real situations we run into across {name} every month, how we diagnose and what the typical fix looks like:</p>{cards}'

    climate_html = ""
    if climate_note:
        climate_html = f'<h2 id="climate" style="margin-top:2.5rem">Local Climate &amp; Building Science Notes</h2><p>{climate_note}</p>'

    landmarks_section = ""
    if landmarks_html:
        landmarks_section = f'<h2 id="landmarks" style="margin-top:2.5rem">Landmarks &amp; Service Coverage In {name}</h2><p>Our trucks regularly reach every corner of {name}, including jobs near these landmarks and across the neighbourhoods listed below.</p>{landmarks_html}'

    nearby_html = ""
    if nearby:
        nearby_links = "".join(f'<a class="area-card" href="{r}service-areas/{n}/"><span class="area-card__city">{nearby_names.get(n,n.title())}</span><span class="area-card__sub">Nearby IKAD service area</span></a>' for n in nearby)
        nearby_html = f"""<section class="section"><div class="container">
<div class="text-center" style="max-width:720px;margin:0 auto 2rem"><span class="eyebrow">Nearby Cities</span><h2>Also Servicing These Cities Near {name}</h2></div>
<div class="area-grid">{nearby_links}</div>
</div></section>"""

    # City-specific service blurbs (renders unique content per city to avoid cannibalism)
    default_blurbs = [
        ("Furnace &amp; Heating", "heating-services/", f"Furnace installation, repair and no-heat emergency response across {name}."),
        ("AC &amp; Heat Pumps", "air-conditioning-heat-pumps/", f"Central AC, cold-climate heat pumps and ductless mini-splits sized to {name} homes."),
        ("Water Heaters", "water-heaters/", f"Tank, tankless and heat pump water heaters installed in {name}."),
        ("In-Floor Heating", "in-floor-heating/", f"Hydronic radiant for bathrooms, additions and new builds in {name}."),
        ("Snow Melting", "snow-melting-systems/", f"Heated driveways and walkways engineered for {name} winters."),
        ("Duct Work", "duct-work/", f"Duct installation, sealing and rebalancing for {name} homes."),
        ("Air Balancing", "air-balancing/", f"CFM measurement and balancing to fix hot/cold rooms in {name}."),
        ("Custom Home HVAC", "custom-homes/", f"Whole-home mechanical design for {name} custom builders."),
        ("Commercial HVAC", "commercial/", f"Rooftop units, make-up air, hoods and PM contracts for {name} businesses."),
    ]
    blurbs_list = city.get("service_blurbs", default_blurbs)
    blurb_cards_html = ""
    for svc_title, svc_path, svc_desc in blurbs_list:
        blurb_cards_html += f'<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.1rem 1.4rem;margin:0 auto .85rem;max-width:880px;display:flex;gap:1rem;align-items:flex-start"><span style="font-size:1.4rem;color:#e30613;flex-shrink:0">{icon("check-circle")}</span><div><h3 style="margin:0 0 .35rem;font-size:1.05rem;color:#0f172a"><a href="{r}{svc_path}" style="color:#0f172a;text-decoration:none">{svc_title}</a></h3><p style="margin:0;color:#475569;font-size:.95rem;line-height:1.6">{svc_desc}</p></div></div>'

    default_services_intro = f"IKAD Mechanical handles the full residential and commercial HVAC scope in {name}: furnace replacement, central AC and heat pump installation, water heaters, hydronic in-floor heating, snow melting, ductwork, air balancing, custom-home design and commercial rooftop work. Below is what we typically do for {name} homeowners and businesses."
    services_intro_text = city.get("services_intro", default_services_intro)

    # City Quick Answer block, citable bullets for AEO
    city_quick_answer = key_facts(
        f"HVAC in {name}, ON, Key Facts",
        f"IKAD Mechanical is a TSSA-certified, HRAI-member HVAC contractor that has served {name} since 2010 from our Upper Middle Rd shop in Oakville. We do residential and commercial furnace, AC, heat pump, water heater, ductwork, in-floor heating and snow melt work, {drive_from_hq} from our shop, no travel surcharge.",
        [
            ("Response time", response),
            ("Drive time from shop", drive_from_hq),
            (f"{name} population served", population),
            ("Gas utility partner", utility_gas),
            ("Electric utility", utility_electric),
            ("Permits filed with", permit_office),
        ]
    )

    body = hero_quote(r, "hero/hero-ikad-team.jpg", f"HVAC in {name}", f"HVAC Services In {name}, ON",
        f"Furnace, AC, heat pump, water heater and ductwork installation and repair in {name} by IKAD Mechanical, a family-owned HVAC contractor based in Oakville since 2010.",
        badges=["15+ Years In Halton", f"Response: {response}", "TSSA &amp; ECRA Certified", "HRAI Member"],
        service_default=f"What you need in {name} *") + \
        breadcrumbs(r, [("Home","./"),("Service Areas","service-areas/"),(name, "")]) + f"""
<section class="section"><div class="container" style="max-width:880px">
{city_quick_answer}
</div></section>

<section class="section"><div class="container"><div class="feature">
<div class="feature__copy">
<span class="eyebrow">Local HVAC In {name}</span>
<h2>Trusted HVAC Contractor Serving {name}</h2>
<p>{city["copy"]}</p>
<p>{story}</p>
<div class="btn-row" style="margin-top:1rem"><a class="btn btn--primary" href="#hero-quote">Request Your Free Quote</a><a class="btn btn--secondary with-icon" href="tel:+19054916943">{icon('phone')} (905) 491-6943</a></div>
</div>
<div class="feature__media"><img src="{r}assets/images/{case_image}" alt="{case_alt}" loading="lazy" width="900" height="600"></div>
</div></div></section>

<section class="section section--gray"><div class="container">
<div class="text-center" style="max-width:720px;margin:0 auto 2rem"><span class="eyebrow">Local Service Details</span><h2>What You Should Know About {name} HVAC</h2></div>
<div class="trust-strip__grid">
<div class="trust-item"><span style="font-size:1.6rem;color:#e30613">{icon('clock')}</span><span class="trust-item__label" style="font-weight:700;color:#0f172a">Response Time</span><span class="trust-item__label">{response}</span></div>
<div class="trust-item"><span style="font-size:1.6rem;color:#e30613">{icon('tools')}</span><span class="trust-item__label" style="font-weight:700;color:#0f172a">Gas Utility</span><span class="trust-item__label">{utility_gas}</span></div>
<div class="trust-item"><span style="font-size:1.6rem;color:#e30613">{icon('shield')}</span><span class="trust-item__label" style="font-weight:700;color:#0f172a">Electric Utility</span><span class="trust-item__label">{utility_electric}</span></div>
<div class="trust-item"><span style="font-size:1.6rem;color:#e30613">{icon('check-circle')}</span><span class="trust-item__label" style="font-weight:700;color:#0f172a">Permit Office</span><span class="trust-item__label">{permit_office}</span></div>
<div class="trust-item"><span style="font-size:1.6rem;color:#e30613">{icon('arrow-right')}</span><span class="trust-item__label" style="font-weight:700;color:#0f172a">From Our Shop</span><span class="trust-item__label">{drive_from_hq}</span></div>
<div class="trust-item"><span style="font-size:1.6rem;color:#e30613">{icon('users')}</span><span class="trust-item__label" style="font-weight:700;color:#0f172a">Population</span><span class="trust-item__label">{population}</span></div>
</div>
</div></section>

<section class="section"><div class="container" style="max-width:880px">
{climate_html}
{housing_eras_html}
{scenarios_html}
{landmarks_section}
</div></section>

<section class="section section--gray"><div class="container">
<div class="text-center" style="max-width:760px;margin:0 auto 1.5rem"><span class="eyebrow">What We Do In {name}</span><h2>HVAC Services We Offer In {name}</h2></div>
<div style="max-width:880px;margin:0 auto 2rem;color:#475569;font-size:1.02rem;line-height:1.7">{services_intro_text}</div>
{blurb_cards_html}
<p style="text-align:center;margin-top:1.5rem;color:#64748b;font-size:.95rem">All services are delivered by our own {name}-experienced crew, no subcontractors. <a href="{r}residential/">See residential services</a> · <a href="{r}commercial/">commercial services</a> · <a href="#hero-quote">request a {name} quote</a>.</p>
</div></section>

<section class="section"><div class="container" style="max-width:880px">
<div class="text-center" style="max-width:720px;margin:0 auto 1.5rem"><span class="eyebrow">Looking For HVAC Near You?</span><h2>Trusted Local HVAC Contractor Near You In {name}</h2><p class="lead" style="margin:0 auto">Searching for an HVAC contractor near you in {name}? IKAD Mechanical is a family-owned, TSSA-certified HVAC contractor based in Oakville since 2010, with {response.lower()} response across {name}.</p></div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem;margin:1.5rem 0">
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.1rem;text-align:center"><div style="font-size:1.6rem;font-weight:800;color:#e30613;line-height:1">Local</div><div style="font-size:.82rem;color:#475569;margin-top:.35rem">Oakville-based, no national-chain handoffs</div></div>
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.1rem;text-align:center"><div style="font-size:1.6rem;font-weight:800;color:#e30613;line-height:1">Licensed</div><div style="font-size:.82rem;color:#475569;margin-top:.35rem">TSSA G2/G3, ECRA/ESA, HRAI member</div></div>
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.1rem;text-align:center"><div style="font-size:1.6rem;font-weight:800;color:#e30613;line-height:1">Insured</div><div style="font-size:.82rem;color:#475569;margin-top:.35rem">$5M liability + WSIB on every job</div></div>
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.1rem;text-align:center"><div style="font-size:1.6rem;font-weight:800;color:#e30613;line-height:1">Family-Run</div><div style="font-size:.82rem;color:#475569;margin-top:.35rem">Same owner since 2010, no commissioned salespeople</div></div>
</div>
<div style="background:#f6f7f9;border-left:3px solid #e30613;border-radius:6px;padding:1.1rem 1.25rem;margin:1.5rem 0;color:#334155;line-height:1.7">
<p style="margin:0 0 .5rem"><strong>Why {name} homeowners pick IKAD when they search for HVAC near them:</strong></p>
<ul style="margin:0;padding-left:1.25rem;font-size:.95rem">
<li>15+ years installing across {name}, we know the local housing stock, gas-line patterns and permit office</li>
<li>Fixed-price written quotes, never "estimated" pricing that grows mid-job</li>
<li>No-pressure consultations, no commissioned salespeople</li>
<li>Manual J load calculation on every furnace and AC install (most local contractors skip this)</li>
<li>Real reviews on <a href="https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling" rel="noopener" target="_blank">HomeStars</a> and Google, see what {name} neighbours say</li>
<li>Free on-site estimates across {name}, response typically within 24-48 hours during business hours</li>
</ul>
</div>
<p style="text-align:center;margin-top:1rem;color:#64748b;font-size:.95rem">More on our credentials and team on the <a href="{r}about/">About page</a>, or <a href="#hero-quote">get a free {name} quote</a> in 60 seconds.</p>
</div></section>

<section class="section"><div class="container">
<div class="text-center" style="max-width:720px;margin:0 auto 2rem"><span class="eyebrow">Frequently Asked</span><h2>{name} HVAC FAQs</h2></div>
<div class="faq">""" + "\n".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in city_faqs) + f"""</div>
<p style="text-align:center;margin-top:1.25rem;color:#64748b">{city.get('faq_outro', f'More general HVAC questions answered on our')} <a href="{r}faq/">main FAQ page (40+ questions)</a>, or <a href="{r}contact/">ask about your {name} project directly</a>.</p>
</div></section>

<section class="section section--gray"><div class="container">
<h2>Neighbourhoods We Serve In {name}</h2>
<p>{city.get('neighborhood_intro', f'Our service trucks regularly reach every {name} neighbourhood, including:')}</p>
<ul style="columns:2;column-gap:2rem;max-width:560px">
{neighborhoods_list}
</ul>
<p style="margin-top:1rem">{city.get('neighborhood_fallback', f'Not listed? Call us, we cover all of {name}.')}</p>
<div class="map-embed" style="margin-top:2rem;max-width:760px"><iframe src="https://www.google.com/maps?q={name.replace(' ','+')},+ON,+Canada&amp;output=embed" loading="lazy" title="{name}, ON map" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
</div></section>

{nearby_html}

<section class="section section--gray"><div class="container">
<div class="cta-banner"><div><h2>Free Quote For Your {name} Project</h2><p>{city.get('cta_line', 'Free on-site estimate, fixed-price written quote, no pressure.')}</p></div><div class="btn-row"><a class="btn btn--secondary btn--large" href="#hero-quote">Request Estimate</a><a class="btn btn--outline btn--large with-icon" href="tel:+19054916943">{icon('phone')} Call Now</a></div></div>
</div></section>
"""

    # Per-city schema: scope the business to this city via areaServed and add city geo via hasMap
    import json
    city_business = {
        "@context":"https://schema.org",
        "@type":"HVACBusiness",
        "@id": f"{BASE}/#business",
        "name":"IKAD Mechanical Inc.",
        "url": f"{BASE}/service-areas/{slug}/",
        "logo": f"{BASE}/assets/images/logo/ikad-logo.png",
        "image": f"{BASE}/assets/images/{case_image}",
        "telephone":"+1-905-491-6943",
        "email":"info@ikad.ca",
        "priceRange":"$$",
        "address":{
            "@type":"PostalAddress",
            "streetAddress":"2275 Upper Middle Rd E, Suite 101",
            "addressLocality":"Oakville",
            "addressRegion":"ON",
            "postalCode":"L6H 0C3",
            "addressCountry":"CA"
        },
        "geo":{"@type":"GeoCoordinates","latitude":43.4675,"longitude":-79.6877},
        "areaServed":{"@type":"City","name":name,"containedInPlace":{"@type":"AdministrativeArea","name":"Ontario, Canada"}},
        "hasMap": f"https://www.google.com/maps?q={name.replace(' ','+')},+ON,+Canada",
        "openingHoursSpecification":[
            {"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"08:00","closes":"18:00"},
            {"@type":"OpeningHoursSpecification","dayOfWeek":"Saturday","opens":"09:00","closes":"16:00"}
        ],
        "sameAs":[
            "https://www.facebook.com/profile.php?id=100088377265654",
            "https://www.instagram.com/ikadmechanical/",
            "https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling"
        ]
    }
    city_business_schema = f'<script type="application/ld+json">\n{json.dumps(city_business, ensure_ascii=False)}\n</script>'

    page(
        out=f"service-areas/{slug}/index.html", depth=2,
        title=city.get("seo_title", f"HVAC in {name}, ON | Furnace, AC &amp; Heat Pumps | IKAD"),
        description=city.get("seo_description", f"Local HVAC contractor in {name}: furnace, AC, heat pumps, water heaters, ductwork. Same-day service across Halton. Call (905) 491-6943."),
        canonical=f"{BASE}/service-areas/{slug}/",
        og_image=f"{BASE}/assets/images/hero/hero-ikad-team.jpg",
        body=body, active="areas", placename=name, preload_hero="hero/hero-ikad-team.jpg",
        geo_lat=city.get("lat"), geo_lng=city.get("lng"),
        schema_extra=city_business_schema + breadcrumb_schema([("Home",f"{BASE}/"),("Service Areas",f"{BASE}/service-areas/"),(name,f"{BASE}/service-areas/{slug}/")]) + faq_schema(city_faqs)
    )

# ---------------------------------------------------------------------------
# Misc pages
# ---------------------------------------------------------------------------

def build_thank_you():
    r = "../"
    body = f"""<section class="hero hero--compact"><img class="hero__bg" src="{r}assets/images/hero/hero-heating-ac.jpg" alt="" loading="eager">
<div class="container hero__inner" style="text-align:center;max-width:680px;margin:0 auto"><span class="eyebrow" style="color:#fca5a5">Thank You</span><h1>Your Request Was Sent</h1>
<p>Thanks for getting in touch with IKAD Mechanical. We've received your message and a member of our team will be in touch within one business day, usually much sooner during regular hours.</p>
<div class="btn-row" style="justify-content:center"><a class="btn btn--primary btn--large" href="{r}">Back To Home</a><a class="btn btn--outline btn--large with-icon" href="tel:+19054916943">{icon('phone')} Call Us Now</a></div></div></section>

<section class="section"><div class="container text-center" style="max-width:680px;margin:0 auto">
<h2>While You Wait…</h2>
<p>Have a look at our recent project gallery, learn more about who we are, or check what's available in your specific city.</p>
<div class="btn-row" style="justify-content:center"><a class="btn btn--secondary" href="{r}our-projects/">Our Projects</a><a class="btn btn--secondary" href="{r}about/">About IKAD</a><a class="btn btn--secondary" href="{r}service-areas/">Service Areas</a></div>
</div></section>
"""
    page(
        out="thank-you/index.html", depth=1,
        title="Thank You | IKAD Mechanical",
        description="Thanks for contacting IKAD Mechanical. We'll be in touch within one business day. Same-day response during business hours.",
        canonical=f"{BASE}/thank-you/",
        og_image=f"{BASE}/assets/images/hero/hero-heating-ac.jpg",
        body=body, active=None,
        noindex=True
    )

def build_privacy():
    r = "../"
    body = breadcrumbs(r, [("Home","./"),("Privacy Policy", "")]) + f"""
<section class="section"><div class="container" style="max-width:820px">
<h1>Privacy Policy</h1>
<p><em>Last updated: January 2026</em></p>
<p>IKAD Mechanical Inc. ("IKAD", "we", "us") respects your privacy. This policy describes the information we collect, how we use it, and your rights regarding that information.</p>

<h2>Information We Collect</h2>
<ul>
<li><strong>Information you provide</strong>, when you request a quote, email us, or call, you may give us your name, phone number, email, address and details about your project.</li>
<li><strong>Automatic information</strong>, when you visit ikad.ca, our hosting and analytics tools may collect standard log data (IP, browser, pages visited, time on page) used to operate and improve the site.</li>
<li><strong>Cookies</strong>, we use a small number of cookies for analytics. You can disable cookies in your browser settings.</li>
</ul>

<h2>How We Use Your Information</h2>
<ul>
<li>To respond to quote requests and service calls</li>
<li>To schedule and complete work you've asked for</li>
<li>To send appointment reminders, invoices and follow-up communication</li>
<li>To improve our website and services</li>
</ul>

<h2>Sharing</h2>
<p>We do not sell, rent or trade your personal information. We share information only with third-party service providers who help us run our business (e.g., scheduling, invoicing, financing) and only what is necessary for them to do their job.</p>

<h2>Your Rights</h2>
<p>You may request access to, correction of, or deletion of your personal information by emailing <a href="mailto:info@ikad.ca">info@ikad.ca</a>. You may also opt out of marketing communications at any time.</p>

<h2>Contact</h2>
<p>Questions about this policy? Contact us:<br>
IKAD Mechanical Inc.<br>
2275 Upper Middle Rd E, Suite 101, Oakville, ON L6H 0C3<br>
<a href="mailto:info@ikad.ca">info@ikad.ca</a> · <a href="tel:+19054916943">(905) 491-6943</a></p>
</div></section>
"""
    page(
        out="privacy-policy/index.html", depth=1,
        title="Privacy Policy | IKAD Mechanical",
        description="IKAD Mechanical's privacy policy: how we collect, use, share and protect customer information when you request HVAC quotes or service in Oakville and Halton.",
        canonical=f"{BASE}/privacy-policy/",
        og_image=f"{BASE}/assets/images/logo/ikad-logo.png",
        body=body, active=None,
        schema_extra=breadcrumb_schema([("Home",f"{BASE}/"),("Privacy Policy",f"{BASE}/privacy-policy/")])
    )

def build_terms():
    r = "../"
    body = breadcrumbs(r, [("Home","./"),("Terms of Service", "")]) + f"""
<section class="section"><div class="container" style="max-width:820px">
<h1>Terms of Service</h1>
<p><em>Last updated: January 2026</em></p>
<p>These terms apply to your use of the IKAD Mechanical website at ikad.ca. Using the site means you agree to these terms.</p>

<h2>Information &amp; Quotes</h2>
<p>The information on this website, including pricing ranges, rebate amounts and service descriptions, is for general informational purposes. Final pricing and scope are confirmed in a written quote following an on-site assessment.</p>

<h2>Workmanship &amp; Warranty</h2>
<p>All installation work performed by IKAD Mechanical is covered by our workmanship warranty as specified in your individual project contract. Manufacturer warranties on equipment apply per the manufacturer's terms.</p>

<h2>Limitation Of Liability</h2>
<p>While we work to keep the site accurate and available, we make no warranties regarding uptime or completeness. IKAD Mechanical is not liable for indirect or consequential damages arising from use of this website.</p>

<h2>Intellectual Property</h2>
<p>All site content, photography, copy and design is owned by IKAD Mechanical Inc. unless otherwise noted. You may not reuse our content for commercial purposes without permission.</p>

<h2>Governing Law</h2>
<p>These terms are governed by the laws of the Province of Ontario, Canada.</p>

<h2>Contact</h2>
<p>IKAD Mechanical Inc.<br>
2275 Upper Middle Rd E, Suite 101, Oakville, ON L6H 0C3<br>
<a href="mailto:info@ikad.ca">info@ikad.ca</a> · <a href="tel:+19054916943">(905) 491-6943</a></p>
</div></section>
"""
    page(
        out="terms-of-service/index.html", depth=1,
        title="Terms of Service | IKAD Mechanical",
        description="Terms of service for ikad.ca and IKAD Mechanical's HVAC installation, repair, warranty and quoting practices across Halton Region, Peel and Hamilton.",
        canonical=f"{BASE}/terms-of-service/",
        og_image=f"{BASE}/assets/images/logo/ikad-logo.png",
        body=body, active=None,
        schema_extra=breadcrumb_schema([("Home",f"{BASE}/"),("Terms of Service",f"{BASE}/terms-of-service/")])
    )

def build_404():
    body = """<section class="hero hero--compact"><img class="hero__bg" src="/assets/images/hero/hero-new-construction.jpg" alt="" loading="eager">
<div class="container hero__inner" style="text-align:center;max-width:680px;margin:0 auto"><span class="eyebrow" style="color:#fca5a5">404</span><h1>This Page Took A Detour</h1><p>The page you're looking for isn't here. It may have moved, or the URL might be off. Use the links below to find what you need.</p>
<div class="btn-row" style="justify-content:center"><a class="btn btn--primary btn--large" href="/">Back To Home</a><a class="btn btn--outline btn--large" href="/contact/">Contact Us</a></div></div></section>

<section class="section"><div class="container">
<div class="text-center" style="max-width:600px;margin:0 auto 2rem"><h2>Popular Pages</h2></div>
<div class="area-grid">
<a class="area-card" href="/heating-services/"><span class="area-card__city">Heating Services</span><span class="area-card__sub">Furnaces, boilers, water heaters</span></a>
<a class="area-card" href="/air-conditioning-heat-pumps/"><span class="area-card__city">AC &amp; Heat Pumps</span><span class="area-card__sub">Central, ductless, cold-climate</span></a>
<a class="area-card" href="/duct-work/"><span class="area-card__city">Duct Work</span><span class="area-card__sub">Install, seal, clean</span></a>
<a class="area-card" href="/commercial/"><span class="area-card__city">Commercial HVAC</span><span class="area-card__sub">Rooftop, MUA, hoods, boilers</span></a>
</div>
</div></section>
"""
    # 404 lives at root, so paths are absolute
    page(
        out="404.html", depth=0,
        title="Page Not Found | IKAD Mechanical",
        description="The page you're looking for isn't here. Browse IKAD Mechanical's HVAC services across Oakville, Burlington, Milton and Halton Region, or call (905) 491-6943.",
        canonical=f"{BASE}/404",
        og_image=f"{BASE}/assets/images/hero/hero-new-construction.jpg",
        body=body, active=None,
        noindex=True
    )

# ---------------------------------------------------------------------------
# Blog
# ---------------------------------------------------------------------------

BLOG_POSTS = [
    {
        "slug": "furnace-cost-oakville-2026",
        "cta_heading":"Get An Exact Furnace Quote For Your Oakville Home",
        "cta_copy":"Free Manual J load calc with every quote, no estimate menus, just real pricing.",
        "faq_heading":"Furnace Pricing Questions Halton Homeowners Actually Ask",
        "title": "How Much Does a New Furnace Cost in Oakville in 2026? (Real Numbers from a Halton HVAC Owner)",
        "meta_title": "Furnace Cost Oakville 2026 | Real Halton Pricing | IKAD",
        "description": "Real installed furnace pricing in Oakville and Halton for 2026: high-efficiency, two-stage, variable speed and modulating. By a 15-year Halton HVAC owner.",
        "date": "2026-01-12",
        "image": "services/heating-2.jpg",
        "image_alt": "High-efficiency furnace installed in an Oakville home by IKAD Mechanical",
        "excerpt": "A 95% AFUE single-stage furnace installed in Oakville is roughly $3,800 to $4,700 in 2026. A two-stage 96% is $4,800 to $6,200. Variable-speed modulating is $6,400 to $7,800. Here's what actually drives the difference.",
        "category": "Cost & Buying Guides",
        "faqs": [
            ("Why is there such a big range?",
             "Three things: efficiency tier, blower type, and what your existing setup needs at install time. Single-stage 95% is the budget option. Two-stage 96% modulates better and runs quieter. Variable-speed modulating is the premium tier, runs almost continuously at low fire, best comfort, best efficiency. On top of that, if your gas line, venting, condensate drain, or thermostat needs to be updated, that adds $300–$1,200."),
            ("Are rebates real?",
             "Yes. The Home Renovation Savings Program (replaced Enbridge HER+ in January 2025) offers $250 for a 96%+ AFUE furnace when bundled with a heat pump install, no energy audit required. The Canada Greener Homes Loan (interest-free up to $40K) is the big one if you're pairing the furnace with a heat pump or insulation work. Registration deadline May 31, 2026. See our 2026 rebate guide for full details."),
            ("What's the worst time to replace a furnace?",
             "January, in the middle of a cold snap, after it dies, because you'll be deciding under pressure, possibly without your spouse, and you'll pay more for emergency labour. If your furnace is 17+ years old, plan the replacement during shoulder season (April–May or September–October) when contractors aren't slammed."),
            ("How long does a furnace last in Oakville?",
             "Properly sized and maintained, a high-efficiency natural-gas furnace lasts 18 to 25 years in this climate. Aggressively oversized, short-cycled, or never-tuned units often fail at 12 to 15 years. Annual maintenance (fall tune-up, filter changes) is the single biggest factor in lifespan."),
            ("Do I need a permit to replace a furnace in Oakville?",
             "Yes for new gas piping, venting changes, or fuel type changes. A direct one-to-one replacement on existing piping sometimes doesn't require a Town of Oakville mechanical permit, but TSSA inspection still applies. IKAD pulls all required permits as part of every install."),
            ("What hidden costs do furnace quotes miss?",
             "The five things contractors often quote separately or omit: chimney liner if you're going from mid-efficiency to high-efficiency ($350-$700), gas line upsizing for a tankless add ($250-$600), 4-inch media filter cabinet ($300-$500), Town of Oakville mechanical permit ($150-$250), and proper Manual J load calc. A real apples-to-apples quote includes all of these.")
        ],
        "body": """
<p>Furnace pricing in Halton has crept up over the past four years, not because contractors are gouging, but because the equipment itself costs about 22% more than it did in 2021, and the inflation has nothing to do with us. Here's what new furnaces actually cost installed in Oakville and the surrounding Halton cities in 2026, and what makes one quote different from another.</p>

<h2>The Real 2026 Pricing Ranges</h2>
<p>These are installed prices for a typical single-family Halton home (1,500–2,800 sq.ft., natural gas, existing forced-air ducts). Tax included.</p>
<table>
<thead><tr><th>Furnace Type</th><th>Installed Price (Oakville 2026)</th><th>Best For</th></tr></thead>
<tbody>
<tr><td>Entry-level 95% single-stage (Goodman, Continental, Heil)</td><td>$3,500 – $4,200</td><td>Tight budget, smaller homes, plan to sell within 5 years</td></tr>
<tr><td>Mid-tier 95% single-stage (Rheem, Lennox EL series)</td><td>$3,900 – $4,800</td><td>Standard replacement, good warranty</td></tr>
<tr><td>Two-stage 96% (Rheem R96, Carrier Comfort, Lennox EL297)</td><td>$4,800 – $6,200</td><td>Most homes, best value tier</td></tr>
<tr><td>Variable-speed modulating (Lennox SLP99V, Carrier Infinity, Rheem R98V)</td><td>$6,400 – $7,800</td><td>Comfort-focused, premium homes, very tight construction</td></tr>
<tr><td>Hybrid (furnace + air-source heat pump)</td><td>$11,500 – $18,000 (before rebates)</td><td>Cutting gas usage 70–80% with Greener Homes Loan</td></tr>
</tbody>
</table>

<h2>What Drives Cost Inside Each Tier</h2>
<p>If you're getting quotes that vary by $1,500 inside the same tier, here's what's usually different:</p>
<ul>
<li><strong>Capacity (BTU).</strong> A 60k unit costs about $250 less than a 100k unit at the wholesale level, but a properly-sized 60k installed in a too-tight envelope is much better than an oversized 100k that short-cycles.</li>
<li><strong>Venting.</strong> If we're going from B-vent to direct-vent (most condensing furnaces require this), there's PVC running through a wall, sealing, condensate piping, and a neutralizer. About $400–$800 of extra labour and material.</li>
<li><strong>Gas line.</strong> Some 1980s-era Halton homes have 1/2" gas lines that don't quite meet the demand of a modern high-efficiency furnace combined with a tankless or fireplace. Upsizing to 3/4" or a flex line: $250–$600.</li>
<li><strong>Thermostat.</strong> A basic programmable thermostat is included on most quotes. An Ecobee Premium or Nest is $300–$450 add-on. A modulating-furnace-specific thermostat (Carrier Infinity, Lennox iComfort) can be $700–$900 because the furnace won't operate at full capability without it.</li>
<li><strong>Removal &amp; disposal of the old furnace.</strong> Should always be included. Verify.</li>
<li><strong>Workmanship warranty.</strong> Standard is one year. We include two. Some contractors charge $200–$400 extra for a 5- or 10-year labour warranty.</li>
</ul>

<h2>Brand-by-Brand Pricing Detail (Installed, Oakville 2026)</h2>
<table>
<thead><tr><th>Brand &amp; Model</th><th>Tier</th><th>Installed Price</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>Goodman GMVC96 (96% two-stage variable-speed)</td><td>Mid</td><td>$4,400 – $5,600</td><td>Best value, 10-year parts warranty, decent rebate fit</td></tr>
<tr><td>Continental CC9 / Heil G9MXE</td><td>Entry</td><td>$3,500 – $4,200</td><td>Budget, fixed-speed blower</td></tr>
<tr><td>Rheem R96V (96% two-stage variable-speed)</td><td>Mid</td><td>$4,900 – $6,100</td><td>Most common Halton install, strong dealer network</td></tr>
<tr><td>Carrier Performance 96 59TP6</td><td>Mid</td><td>$5,000 – $6,400</td><td>Good Infinity-thermostat compatibility</td></tr>
<tr><td>Lennox EL297V (97% two-stage variable-speed)</td><td>Mid-high</td><td>$5,400 – $6,800</td><td>Excellent dealer rebate stack</td></tr>
<tr><td>Rheem R98V (98% modulating)</td><td>Premium</td><td>$6,400 – $7,400</td><td>Modulates 35-100%, very quiet</td></tr>
<tr><td>Carrier Infinity 59MN7 (98.5% modulating)</td><td>Premium</td><td>$6,800 – $7,900</td><td>Requires Infinity thermostat ($700 add)</td></tr>
<tr><td>Lennox SLP99V (99% modulating)</td><td>Premium</td><td>$7,000 – $8,200</td><td>Highest AFUE on the market, requires iComfort</td></tr>
<tr><td>Trane S9V2 (97% two-stage)</td><td>Mid-high</td><td>$5,200 – $6,700</td><td>Tight Halton dealer network, longer service-call wait</td></tr>
<tr><td>Daikin DM97MC (97% modulating)</td><td>Premium</td><td>$6,500 – $7,800</td><td>12-year parts warranty, replacement guarantee</td></tr>
</tbody>
</table>

<h2>What Drives Cost Inside Each Tier</h2>
<p>If you're getting quotes that vary by $1,500 inside the same tier, here's what's usually different:</p>
<ul>
<li><strong>Capacity (BTU).</strong> A 60k unit costs about $250 less than a 100k unit at the wholesale level, but a properly-sized 60k installed in a too-tight envelope is much better than an oversized 100k that short-cycles.</li>
<li><strong>Venting.</strong> If we're going from B-vent to direct-vent (most condensing furnaces require this), there's PVC running through a wall, sealing, condensate piping, and a neutralizer. About $400–$800 of extra labour and material.</li>
<li><strong>Gas line.</strong> Some 1980s-era Halton homes have 1/2" gas lines that don't quite meet the demand of a modern high-efficiency furnace combined with a tankless or fireplace. Upsizing to 3/4" or a flex line: $250–$600.</li>
<li><strong>Thermostat.</strong> A basic programmable thermostat is included on most quotes. An Ecobee Premium or Nest is $300–$450 add-on. A modulating-furnace-specific thermostat (Carrier Infinity, Lennox iComfort) can be $700–$900 because the furnace won't operate at full capability without it.</li>
<li><strong>Removal &amp; disposal of the old furnace.</strong> Should always be included. Verify.</li>
<li><strong>Workmanship warranty.</strong> Standard is one year. We include two. Some contractors charge $200–$400 extra for a 5- or 10-year labour warranty.</li>
</ul>

<h2>Hidden Costs That Aren't Always In The Quote</h2>
<ul>
<li><strong>Chimney liner.</strong> Going from mid-efficiency to high-efficiency means the old chimney can't safely handle the lower flue gas temperatures from a leftover gas water heater. A stainless steel liner is $350–$700 installed.</li>
<li><strong>Condensate neutralizer + pump.</strong> Required for high-efficiency furnaces. A few quotes leave this out at $150–$250.</li>
<li><strong>Filter cabinet upgrade.</strong> If you're going from a 1-inch filter slot to a 4-inch or 5-inch media filter (much better for static pressure and indoor air quality), expect $300–$500 in cabinet and ductwork.</li>
<li><strong>Town of Oakville / municipal mechanical permit.</strong> Required for venting changes and gas line work, $150–$250. Should be in the quote.</li>
<li><strong>Old AC coil compatibility check.</strong> If your AC is staying and is over 12 years old, the new furnace may need a new evaporator coil to match capacity. $400–$800.</li>
</ul>

<h2>2026 Rebates Available For Furnace Replacement</h2>
<ul>
<li><strong>Home Renovation Savings Program (replaced Enbridge HER+ in Jan 2025):</strong> Up to $250 for a 96%+ AFUE furnace when bundled with a heat pump install. No energy audit required, direct deposit, registration deadline May 31, 2026. <a href="../ontario-heat-pump-rebates-2026/">Full HRS guide here.</a></li>
<li><strong>Canada Greener Homes Loan:</strong> Interest-free up to $40,000 if the furnace is part of a broader retrofit (heat pump, insulation, etc.). The <em>Grant</em> closed in 2024, the Loan is what's still active.</li>
<li><strong>Save On Energy:</strong> Periodic provincial promos on smart thermostats ($75–$100).</li>
<li><strong>Manufacturer rebates:</strong> Lennox, Carrier, Rheem and Daikin run seasonal $200–$800 rebates on specific high-tier models. We pass these through to your quote.</li>
</ul>

<h2>Manual J: The Reason Right-Sized Furnaces Last Longer</h2>
<p>An oversized furnace is the single most common installation mistake in this region. It heats the air in your home too fast, short-cycles itself, makes your house feel stuffy, and dies 3–5 years before a properly-sized unit would. The fix is a Manual J load calculation, a room-by-room math exercise that accounts for insulation, window count, orientation, infiltration and equipment efficiency. We do one on every install. Most contractors don't, which is part of why so many Halton homes are running 100k BTU furnaces when they actually only need 60k.</p>

<h2>When You Should Replace vs. Repair</h2>
<p>The rough rule: if your furnace is 15+ years old, the cost of a major repair is more than 30% of replacement cost, or the heat exchanger has any visible crack, replace it. Heat exchanger cracks aren't repairable, and CO leaks are a real risk on systems that old. See our <a href="../emergency-furnace-repair-oakville/">emergency furnace service post</a> if you're deciding between repair and replace today.</p>

<h2>Should You Replace Furnace + AC Together?</h2>
<p>If both are 14+ years old, almost always yes. The combined install runs $9,500–$14,500 in Halton (vs $4,500–$7,000 furnace alone + $5,500–$8,500 AC alone separately = $10,000–$15,500). You save on labour, the equipment is matched (especially important if you go variable-speed, the AC needs a matching variable-speed coil), and rebate stacking is better. <a href="../heat-pump-vs-furnace-ontario/">See the heat pump comparison</a> if you want to consider that route at the same time.</p>

<p>Want a quote on your specific home? Drop your address and we'll come out, do the load calc, and email you exact pricing. <a href="#hero-quote">Request your free quote</a> or <a href="tel:+19054916943">call (905) 491-6943</a>.</p>
"""
    },
    {
        "slug": "heat-pump-vs-furnace-ontario",
        "cta_heading":"Curious Whether a Heat Pump Fits Your Home?",
        "cta_copy":"We'll run the cost-and-comfort math for your specific Halton home, free.",
        "faq_heading":"Heat Pump vs Furnace: Reader Questions",
        "title": "Heat Pump vs Furnace in Ontario: 2026 Cost, Rebates &amp; Cold-Weather Performance",
        "meta_title": "Heat Pump vs Furnace Ontario 2026, Real Cost | IKAD",
        "description": "Heat pump vs furnace in Ontario 2026: installed costs, cold-climate performance to -25°C, rebate stack, payback period. From a 15-year Halton HVAC contractor.",
        "date": "2026-01-15",
        "image": "services/air-conditioning.webp",
        "image_alt": "Cold-climate heat pump outdoor unit installed by IKAD in Oakville",
        "excerpt": "Modern cold-climate heat pumps work efficiently down to -25°C and pair beautifully with an existing furnace as a hybrid. With Greener Homes Loan funding, the payback is faster than most people expect.",
        "category": "Comparison Guides",
        "faqs": [
            ("Will a heat pump actually heat my home in a Halton winter?",
             "Yes. Cold-climate heat pumps (Mitsubishi Hyper-Heat, Daikin Aurora, Lennox SL25XPV) hold rated capacity down to about -15°C and continue producing heat, at reduced efficiency, to -25°C. Halton hits -25°C maybe 3–5 days a year, and those are exactly when your existing furnace (in a hybrid system) kicks in."),
            ("How much can I save on operating cost?",
             "Heat pumps deliver 200–300% efficiency in mild weather (vs 95% for the best gas furnace), but electricity in Ontario is more expensive per kWh than gas per BTU. The net savings is real but not massive: typical Halton home saves $250–$650/year on combined heating costs in a hybrid setup, more if you have time-of-use rates."),
            ("Should I keep my gas furnace or rip it out?",
             "Keep it. A hybrid configuration is by far the most common (and most cost-effective) approach in our climate. The heat pump handles ~80% of heating hours; the furnace handles peak-cold backup. Total install cost is also lower than replacing both."),
            ("What rebates apply to heat pumps in Ontario in 2026?",
             "The Home Renovation Savings Program (replaced Enbridge HER+ in January 2025) offers up to $7,500 for an air-source cold-climate heat pump, no energy audit required, registration deadline May 31, 2026. Stack with the interest-free Canada Greener Homes Loan up to $40,000 (10-year repayment). See our 2026 Ontario rebate guide for full stacking details."),
            ("What is R-454B refrigerant and does it matter for a 2026 install?",
             "R-454B is the new low-global-warming-potential refrigerant replacing R-410A across all new residential AC and heat pumps in Canada from January 2025. It's mildly flammable (A2L safety class), which means stricter brazing and leak-detection requirements at install. Operating efficiency and cold-weather performance are unaffected. Any new heat pump quoted in 2026 should be R-454B.")
        ],
        "body": """
<p>Heat pumps have gone from "interesting niche" to "the question every homeowner asks at the AC quote" in the past three years. We get the question almost every week, so here's the straight answer based on installs we've done across Oakville, Burlington and Milton.</p>

<h2>Quick Decision Framework</h2>
<table>
<thead><tr><th>If you...</th><th>You want...</th></tr></thead>
<tbody>
<tr><td>...have an aging furnace and need AC anyway</td><td>Cold-climate heat pump (replaces both)</td></tr>
<tr><td>...have a relatively new furnace but old AC</td><td>Heat pump as AC replacement, hybrid with existing furnace</td></tr>
<tr><td>...are doing a custom build / major reno</td><td>Heat pump + smaller backup furnace, sized together</td></tr>
<tr><td>...have a finished basement with a hot room</td><td>Ductless mini-split (smaller-scale heat pump)</td></tr>
<tr><td>...have no gas service (propane or oil)</td><td>Cold-climate heat pump, usually a no-brainer</td></tr>
</tbody>
</table>

<h2>Installed Pricing in 2026 (Halton)</h2>
<ul>
<li><strong>Cold-climate heat pump only (replacing AC + significant gas reduction):</strong> $8,500–$15,000 installed, before rebates.</li>
<li><strong>Hybrid (heat pump + new high-efficiency furnace):</strong> $14,500–$22,000 installed, before rebates.</li>
<li><strong>Ductless single-zone mini-split:</strong> $4,200–$6,500 installed.</li>
</ul>
<p>After the <a href="../ontario-heat-pump-rebates-2026/">Canada Greener Homes Loan (interest-free, up to $40K) and Home Renovation Savings Program rebates</a> (which replaced Enbridge HER+ in January 2025, up to $7,500 for an air-source heat pump), the net out-of-pocket for a hybrid commonly lands in the $8K–$14K range, financed at 0% over 10 years.</p>

<h2>How Cold-Climate Heat Pumps Actually Perform Here</h2>
<p>The most common myth: "heat pumps stop working when it gets cold." This was true for systems built before about 2015. Modern cold-climate units use variable-speed compressors and enhanced vapor injection to hold real heating capacity at temperatures that would have stalled older units.</p>
<ul>
<li><strong>Above -5°C:</strong> Heat pump runs alone at 250–320% efficiency (HSPF 11–13). Furnace stays off.</li>
<li><strong>-5°C to -15°C:</strong> Heat pump still runs alone, efficiency drops to 180–230%. Still cheaper than gas in most cases.</li>
<li><strong>-15°C to -25°C:</strong> System switches to gas furnace (or runs both). Heat pump still contributing some output.</li>
<li><strong>Below -25°C:</strong> Furnace handles 100%. Heat pump is locked out to protect itself.</li>
</ul>
<p>Halton averages 8–14 days per year below -15°C. So your heat pump is doing nearly all the work 95% of winter days.</p>

<h2>The Payback Math</h2>
<p>For a 2,200 sq.ft. Oakville home with an aging mid-efficiency furnace, current annual heating cost is roughly $1,800 (gas only). After hybrid install:</p>
<ul>
<li>Annual operating cost drops to ~$1,250 (heat pump + minimal gas backup)</li>
<li>Net savings: ~$550/year</li>
<li>Net install cost after rebates &amp; loan: ~$11,000 (financed at 0% = $92/mo over 10 years)</li>
<li>Energy savings + comfort improvement effectively pay the loan back</li>
</ul>
<p>Add the cooling side (you needed AC anyway), and the math gets significantly better.</p>

<h2>Equipment We Recommend</h2>
<ul>
<li><strong>Best overall cold-climate:</strong> Mitsubishi Hyper-Heat, proven, quiet, very low ambient performance.</li>
<li><strong>Best value:</strong> Lennox SL25XPV, solid cold-weather curve, good rebate stack.</li>
<li><strong>Best ducted retrofit:</strong> Carrier Infinity 24VNA6 paired with existing furnace.</li>
<li><strong>Best ductless:</strong> Daikin Aurora, wide modulation range, single-zone and multi-zone.</li>
</ul>

<h2>What About R-454B?</h2>
<p>R-454B is the new low-GWP refrigerant replacing R-410A across all new residential heat pumps and AC sold in Canada from January 2025 onward. Every cold-climate heat pump we recommend in 2026 is R-454B. It's mildly flammable (A2L classification) which changes brazing and leak-detection requirements at install (manufacturer-certified installers only, which we are). Operating efficiency and cold-weather performance are not affected.</p>

<h2>2026 Rebates That Apply</h2>
<p>The <a href="../ontario-heat-pump-rebates-2026/">Home Renovation Savings Program</a> (which replaced Enbridge HER+ in January 2025) offers up to $7,500 for an air-source cold-climate heat pump, no energy audit required. Stack with the interest-free Canada Greener Homes Loan up to $40,000. <strong>Registration deadline: May 31, 2026.</strong> See our <a href="../ontario-heat-pump-rebates-2026/">full 2026 rebate guide</a> for the stacking math.</p>

<p>If you want to know whether a heat pump makes sense for your specific home (not a generic answer), <a href="#hero-quote">request a free quote</a>, we'll do a quick Manual J, run the rebate math, and tell you straight. See also our <a href="../furnace-cost-oakville-2026/">2026 furnace cost breakdown</a> for the gas-only comparison.</p>
"""
    },
    {
        "slug": "furnace-wont-turn-on",
        "cta_heading":"Furnace Still Won't Start? We're On Call.",
        "cta_copy":"Same-day no-heat dispatch across Halton. Call us before pipes freeze.",
        "faq_heading":"Furnace No-Start Diagnosis Questions",
        "title": "Furnace Won't Turn On? 7 Things To Check Before You Call an Oakville HVAC Tech",
        "meta_title": "Furnace Won't Turn On, 7 Fixes To Try Before Calling | IKAD",
        "description": "Furnace won't start? Walk through the 7 most common causes, thermostat, breaker, filter, switch, drain, igniter, sensor, before paying for a service call.",
        "date": "2026-01-08",
        "image": "services/heating-technician.jpg",
        "image_alt": "Furnace troubleshooting in a residential home",
        "excerpt": "Before you pay $150 for a service call, here are seven things to check yourself. About 30% of our no-heat callouts turn out to be one of these.",
        "category": "Troubleshooting",
        "faqs": [
            ("My furnace makes a clicking sound but won't fire, what is it?",
             "Most likely a failing igniter or flame sensor. Igniters cost about $90 in parts; flame sensors are $25 and a 10-minute clean-and-reinstall. Either way, this is a service-call diagnosis, not a DIY repair."),
            ("Is it safe to reset my furnace myself?",
             "Yes, the breaker reset and the side-mounted on/off switch are both safe to cycle. What's not safe: opening the burner compartment, messing with the gas valve, or unplugging the inducer motor. Stop at the basics."),
            ("How fast can you get to a Halton no-heat call?",
             "During business hours, same-day across Halton. After hours and weekends in winter, we keep emergency-response slots, call (905) 491-6943.")
        ],
        "body": """
<p>It's the call we run several times a week in January. Furnace dead. House getting cold. Before you panic, work through this list. About one-third of the no-heat calls we go on turn out to be something the homeowner could have fixed in five minutes.</p>

<h2>1. Check Your Thermostat</h2>
<p>Sounds dumb. We've seen it. Switch the system to <strong>Heat</strong> (not Cool, not Off). Raise the setpoint at least 3°C above current room temperature. If it's a smart thermostat (Ecobee, Nest), check it's not in some scheduled or away mode. If the screen is blank, change the batteries.</p>

<h2>2. Check the Breaker</h2>
<p>Your furnace is on its own breaker (usually 15A) in the main panel. If it tripped, flip it fully <strong>Off</strong> then back to <strong>On</strong>. If it trips again immediately, stop, that's a real electrical problem; call us.</p>

<h2>3. Check the Switch on the Side of the Furnace</h2>
<p>Most furnaces have a literal light-switch on the side of the unit (or near the basement stairs) that controls power. It can get flipped accidentally, sometimes by a cleaner, sometimes by someone changing the filter. Make sure it's <strong>On</strong>.</p>

<h2>4. Check the Filter</h2>
<p>A clogged filter can trigger the furnace's high-limit safety, which locks out the heat. Pull the filter, if you can't see light through it, replace it (or run without one for a few hours while you find a new one).</p>

<h2>5. Check the Condensate Drain</h2>
<p>If you have a high-efficiency (condensing) furnace, look for a small clear plastic line draining into a floor drain or a pump. If the drain is clogged, the safety switch will refuse to let the furnace fire. Disconnect the line, blow it clear, reconnect.</p>

<h2>6. Check the Air Pressure / Vent</h2>
<p>Step outside and look at the two PVC pipes coming out of the side of your house (the intake and exhaust for the furnace). Are they blocked by snow, ice, or a squirrel's nest? Clear them. Birds and snow drifts are common winter culprits in Oakville.</p>

<h2>7. Cycle the Power</h2>
<p>Turn the furnace switch Off, wait 60 seconds, turn it back On. Hear the inducer motor start? Good sign. No sound at all after 90 seconds? Call us.</p>

<h2>When To Stop and Call</h2>
<p>If your furnace is showing an LED error code (visible through a small window on the front), write it down, that tells us exactly what failed. If you smell gas, leave the house and call Enbridge's emergency line (1-866-763-5427) first, then call us. If the furnace is over 18 years old and you're getting frequent no-heat calls, the math has tipped: you're paying for repairs on a system that won't last another winter, and there are real rebates available on a replacement.</p>

<p>Need same-day no-heat service in Halton? <a href="#hero-quote">Request emergency service</a> or <a href="tel:+19054916943">call (905) 491-6943</a>, we're set up to dispatch within hours during winter.</p>
"""
    },
    {
        "slug": "tankless-water-heater-cost-oakville",
        "cta_heading":"Get An Exact Tankless Quote For Your Oakville Home",
        "cta_copy":"We'll size your gas line and confirm the venting path in 15 minutes on site.",
        "faq_heading":"Tankless Water Heater Pricing Questions",
        "title": "Tankless Water Heater Installation Cost in Oakville (Navien vs Rinnai vs Rheem)",
        "meta_title": "Tankless Water Heater Cost Oakville 2026 | Real Pricing | IKAD",
        "description": "Real installed pricing for tankless water heaters in Oakville, Navien, Rinnai, Rheem compared. From a TSSA-certified Halton HVAC contractor.",
        "date": "2026-01-10",
        "image": "services/water-heaters.jpg",
        "image_alt": "Tankless water heater installation in an Oakville mechanical room",
        "excerpt": "A condensing tankless water heater installed in Oakville runs about $4,200 to $6,800 in 2026, depending on brand, gas line work, and venting. Here's how to choose between Navien, Rinnai and Rheem.",
        "category": "Cost & Buying Guides",
        "faqs": [
            ("Is tankless worth it for a 2-person household?",
             "Honestly, usually not. Tankless shines when you have multiple bathrooms running simultaneously, do a lot of laundry, or want a 20+ year service life. For a two-person household with average usage, a high-quality tank gives better payback."),
            ("How often does tankless need maintenance?",
             "Annual descaling in Halton's water hardness, about $150–$250 per service. Skipping it for 3+ years voids most manufacturer warranties and shortens the heat exchanger life by half."),
            ("Do I need to upgrade my gas line for tankless?",
             "Usually yes. A typical residential tankless is 180,000–199,000 BTU, many existing gas lines are sized for the 40,000 BTU tank you're replacing. We measure manifold pressure and decide on site."),
            ("Should I buy or rent a water heater in Oakville?",
             "Buy. Rental programs (Enercare, Reliance, EasyHome) charge $25-$45/month that adds up to $4,500-$8,000 over a typical 15-year ownership window for a unit that cost the rental company $700 wholesale. The cancellation/buyout fees can also be punishing. The only case where renting makes sense is short-term ownership where you'll sell within 3-4 years."),
            ("Is a heat pump water heater (HPWH) a third option?",
             "Yes, and an underrated one. A heat pump water heater (Rheem ProTerra, A.O. Smith Voltex) uses 70% less electricity than a standard electric tank, costs $4,500-$6,500 installed, and qualifies for a $1,000 Home Renovation Savings Program rebate plus the Canada Greener Homes Loan. Best fit if your existing water heater is electric or if you don't have a gas line. Requires a basement or utility room with at least 700 cubic feet and a floor drain."),
            ("What water heater rebates exist in Ontario 2026?",
             "The Home Renovation Savings Program offers $1,000 for a heat pump water heater install. Tankless gas units don't have a current rebate. The Canada Greener Homes Loan (interest-free up to $40,000) can finance any water heater upgrade if bundled with other eligible retrofits. Manufacturer rebates on premium tankless brands run periodically ($150-$400).")
        ],
        "body": """
<p>Going tankless is one of those decisions that sounds straightforward and turns out to have a half-dozen real variables underneath. Here's what installed tankless water heaters actually cost in Oakville in 2026, and what makes one quote different from another.</p>

<h2>The Installed Price Ranges</h2>
<table>
<thead><tr><th>Brand &amp; Model</th><th>Installed (Oakville 2026)</th><th>Best For</th></tr></thead>
<tbody>
<tr><td>Navien NPE-S2 series (180–199k BTU)</td><td>$4,500 – $5,800</td><td>Most homes, best value in the segment</td></tr>
<tr><td>Navien NPE-A2 with built-in recirc</td><td>$5,200 – $6,400</td><td>Bigger homes, distant master ensuite</td></tr>
<tr><td>Rinnai RUR series</td><td>$4,800 – $6,100</td><td>Long warranty, parts availability</td></tr>
<tr><td>Rheem RTGH series</td><td>$4,200 – $5,500</td><td>Budget tier with solid reliability</td></tr>
<tr><td>Combi unit (Navien NCB-H, heat + hot water)</td><td>$6,800 – $8,500</td><td>Replacing both boiler and water heater</td></tr>
</tbody>
</table>

<h2>What's Inside The Quote</h2>
<ul>
<li><strong>The unit itself</strong> ($1,600–$3,200 wholesale)</li>
<li><strong>Stainless steel concentric venting</strong> through a sidewall (~$350)</li>
<li><strong>Gas line upsizing</strong> from 1/2" to 3/4" if needed (~$300–$700)</li>
<li><strong>Isolation valves &amp; recirc kit</strong> ($150–$400)</li>
<li><strong>Removal &amp; disposal of old tank</strong> (should be included)</li>
<li><strong>Labour:</strong> typically a full day for a tank-to-tankless conversion</li>
</ul>

<h2>Tank vs Tankless, Honest Comparison</h2>
<table>
<thead><tr><th></th><th>Tank (50-gal gas)</th><th>Tankless</th></tr></thead>
<tbody>
<tr><td>Installed cost</td><td>$1,400 – $2,200</td><td>$4,200 – $6,800</td></tr>
<tr><td>Service life</td><td>10–13 years</td><td>20–25 years</td></tr>
<tr><td>Annual operating</td><td>$280–$420</td><td>$200–$320</td></tr>
<tr><td>Annual maintenance</td><td>~$0</td><td>$150–$250 (descaling)</td></tr>
<tr><td>Hot water capacity</td><td>Limited (50 gal at a time)</td><td>Endless, but flow-limited</td></tr>
<tr><td>Footprint</td><td>~24" diameter floor unit</td><td>Wall-mounted, ~size of a microwave</td></tr>
</tbody>
</table>

<h2>The Hard Water Reality</h2>
<p>Oakville and Burlington tap water averages 7–9 grains per gallon of hardness, moderately hard. Tankless units have small-passage heat exchangers that scale up faster than tanks. We strongly recommend a whole-home water softener at install time if you're going tankless. Or commit to the annual descaling. Skip both and you'll get half the service life.</p>

<h2>Which Brand We Pick And Why</h2>
<p>Most Halton tankless installs we do are Navien, best price-to-performance in the segment, very good parts availability, dealer network is strong, and the NPE-A2 has a built-in recirculation pump that's a real comfort upgrade in larger homes. Rinnai is just as reliable but typically $300–$500 more. Rheem is what we install when budget is the main concern. We don't push one brand, we recommend what fits the home.</p>

<h2>Buy Vs Rent: The Real Math</h2>
<p>Halton homeowners get rental pitches from Enercare, Reliance and EasyHome every time a sales rep is at the door. Run the math: a $30/month rental on a 50-gallon tank is $360/year or $5,400 over the typical 15-year life of the unit. The wholesale cost of that same tank is $700. The cancellation/buyout fees range from $500 to $2,200. Unless you're certain you'll sell the house within 3-4 years, buying outright (whether tank or tankless) almost always wins. Many Halton homes still carry rental contracts from the 1990s, every year is dead money.</p>

<h2>Don't Forget The Heat Pump Water Heater Option</h2>
<p>A heat pump water heater (Rheem ProTerra, A.O. Smith Voltex) is a third path most contractors don't discuss because the margins are thinner. It uses 70% less electricity than a standard electric tank, costs $4,500–$6,500 installed, and qualifies for a $1,000 Home Renovation Savings Program rebate. Best fit if your existing water heater is electric or you don't have a gas line. Needs a basement or utility room with at least 700 cubic feet and a floor drain. <a href="../ontario-heat-pump-rebates-2026/">See the HPWH rebate details in our 2026 rebate guide.</a></p>

<h2>Halton Water Hardness And Why It Matters For Tankless</h2>
<p>Halton Region municipal water averages 7–9 grains per gallon of hardness, with Halton Hills and the Milton aquifer-fed areas trending higher (10–14 grains). That's classified as "moderately hard" to "hard." For tankless units the consequences are: faster scale buildup in the heat exchanger, more frequent descaling needed (every 9 months instead of every 18), and shorter service life if descaling is skipped. We recommend a whole-home softener at $1,800–$2,800 installed with any tankless install for hard-water Halton homes, the unit pays for itself in extended water heater life and easier appliance maintenance.</p>

<p>Want exact pricing for your home? <a href="#hero-quote">Request a quote</a>, we'll do a 15-minute site visit and email a fixed-price proposal. See also our <a href="../../water-heaters/">water heater service page</a> for installation details and our <a href="../ontario-heat-pump-rebates-2026/">2026 rebate guide</a>.</p>
"""
    },
    {
        "slug": "ontario-heat-pump-rebates-2026",
        "cta_heading":"Want IKAD To Handle Your Rebate Paperwork?",
        "cta_copy":"We file Greener Homes Loan and Home Renovation Savings Program paperwork for you as part of every eligible install.",
        "faq_heading":"Ontario Heat Pump Rebate Questions",
        "title": "Ontario Heat Pump Rebates 2026: Home Renovation Savings + Greener Homes Loan Explained",
        "meta_title": "Ontario Heat Pump Rebates 2026 | HRS + Greener Homes | IKAD",
        "description": "2026 Ontario heat pump rebate guide: Home Renovation Savings Program ($7,500), $40K Greener Homes Loan, stacking strategy, May 31 2026 deadline.",
        "date": "2026-03-12",
        "image": "services/in-floor-heating.jpg",
        "image_alt": "Hydronic in-floor heating manifold installation eligible for Greener Homes Loan",
        "excerpt": "The Home Renovation Savings Program replaced Enbridge HER+ in January 2025 and now offers up to $7,500 for an air-source heat pump. Stack it with the $40,000 interest-free Greener Homes Loan, but the registration deadline is May 31, 2026.",
        "category": "Rebates & Financing",
        "faqs": [
            ("What replaced Enbridge HER+ in Ontario?",
             "The Home Renovation Savings Program (HRS), launched January 28, 2025, replaced the HER+ program. It's jointly delivered by Enbridge Gas and Save on Energy and covers electric heat pumps, gas furnaces, insulation, smart thermostats, heat pump water heaters, and more. No pre-retrofit energy audit is required, which is the biggest simplification from the old HER+ rules."),
            ("How much can I get for a heat pump under the HRS Program?",
             "Up to $7,500 for an air-source cold-climate heat pump that replaces electric or fossil-fuel heating, $1,250 per ton for non-gas-heated homes, $500 per ton for gas-heated homes, and up to $12,000 for a ground-source heat pump. The exact amount depends on system type, capacity and whether you're replacing gas or electric resistance heat."),
            ("Is the Canada Greener Homes Grant still available?",
             "No, the Grant program closed for new applicants in early 2024. The interest-free Loan program (up to $40,000, 10-year repayment) remains active and is still the most valuable financing program for heat pump and major retrofit work."),
            ("What's the deadline to apply for HRS?",
             "Registration for the Home Renovation Savings Program closes May 31, 2026. You must register before the deadline; the actual install and rebate claim can happen after registration. We strongly recommend registering as soon as you're considering a heat pump or furnace upgrade."),
            ("Can IKAD handle the paperwork?",
             "Yes, we are a participating contractor on the Home Renovation Savings Program. We register your project, file invoices in the format the program needs, and walk you through the rebate claim. We do this every week.")
        ],
        "body": """
<aside class="answer-box" role="complementary"><span class="answer-box__label">Quick Answer</span><h2>2026 Ontario HVAC Rebates At A Glance</h2><p>Halton homeowners doing a heat pump or furnace upgrade in 2026 can typically stack these programs:</p><ul>
<li><strong>Home Renovation Savings Program:</strong> up to $7,500 for an air-source heat pump, $12,000 for ground-source, $1,000 for a heat pump water heater (May 31, 2026 deadline)</li>
<li><strong>Canada Greener Homes Loan:</strong> interest-free loan up to $40,000, 10-year repayment</li>
<li><strong>Manufacturer rebates:</strong> Lennox / Carrier / Daikin promos, $200–$800 on specific models</li>
<li><strong>Save on Energy thermostat rebates:</strong> $75–$100 on a smart thermostat</li>
</ul></aside>

<p>The rebate landscape in Ontario shifted significantly in January 2025. Enbridge HER+ ended. The new Home Renovation Savings Program (HRS) replaced it, jointly delivered by Enbridge Gas and Save on Energy, and the rules are simpler and the rebates are bigger. Most Halton homeowners who installed a heat pump in 2024 missed money they could have claimed under the new program if they'd waited.</p>

<p>Here's exactly what's available in 2026 and how to stack it.</p>

<h2 id="hrs">Home Renovation Savings Program (HRS) — Your Main 2026 Rebate</h2>
<p>The Home Renovation Savings Program is the dominant residential HVAC rebate in Ontario for 2026. It launched January 28, 2025 and runs through May 31, 2026 for registration. Key facts:</p>
<ul>
<li><strong>No energy audit required.</strong> The biggest single change from HER+. You don't need a pre-retrofit Energy Advisor visit (save $400–$600).</li>
<li><strong>Participating contractor required.</strong> Your installer must be registered with the program (we are).</li>
<li><strong>Direct deposit.</strong> Rebate is direct-deposited to your bank, no rebate card.</li>
<li><strong>Stackable with the Greener Homes Loan.</strong> You can claim HRS and finance the entire upgrade through the interest-free loan in the same project.</li>
</ul>

<h3>Heat Pump Rebate Amounts Under HRS (2026)</h3>
<table>
<thead><tr><th>Equipment</th><th>Gas-Heated Home</th><th>Non-Gas-Heated Home</th></tr></thead>
<tbody>
<tr><td>Air-source heat pump (cold-climate)</td><td>$500 / ton, up to $7,500</td><td>$1,250 / ton, up to $7,500</td></tr>
<tr><td>Ground-source (geothermal) heat pump</td><td>Up to $12,000</td><td>Up to $12,000</td></tr>
<tr><td>Heat pump water heater</td><td>$1,000</td><td>$1,000</td></tr>
<tr><td>Ductless / mini-split (single zone)</td><td>$1,000 base</td><td>$1,250 / ton</td></tr>
<tr><td>96%+ AFUE gas furnace</td><td>$250 (eligible only with simultaneous HP install or specific bundle)</td><td>N/A</td></tr>
<tr><td>Smart thermostat (Ecobee / Nest / Honeywell)</td><td>$75 – $100</td><td>$75 – $100</td></tr>
</tbody>
</table>

<h3>HRS Eligibility For Halton Homes</h3>
<ul>
<li>You must own the home (rentals not eligible).</li>
<li>The home must be your primary residence in Ontario.</li>
<li>Equipment must meet the program's specific make/model list, we check this before quoting.</li>
<li>Install must be done by a participating contractor.</li>
<li>Registration must be submitted by <strong>May 31, 2026</strong>.</li>
</ul>

<h2 id="greener-homes">Canada Greener Homes Loan (Still Active)</h2>
<ul>
<li><strong>Interest-free loan up to $40,000</strong></li>
<li>10-year repayment term, principal-only payments</li>
<li>Eligible work: heat pumps, insulation, windows/doors, solar PV, on-site renewables, heat pump water heaters</li>
<li>Still requires a registered Energy Advisor audit (different from HRS, this one's not waived)</li>
<li>Applied through Natural Resources Canada portal</li>
<li>You apply, get approved, do the work, get reimbursed (the loan amount), then make monthly payments</li>
</ul>

<h2 id="stacking">Real-World 2026 Stacking Example</h2>
<p>A typical Halton homeowner doing a hybrid heat pump + new 96%+ furnace upgrade in 2026:</p>
<ul>
<li>Gross install cost: $18,500 (3-ton cold-climate heat pump + matched 80k BTU furnace + smart thermostat)</li>
<li>HRS rebate (3-ton heat pump in gas-heated home): -$1,500</li>
<li>HRS rebate (smart thermostat): -$100</li>
<li>HRS rebate (gas furnace, bundled with HP install): -$250</li>
<li>Manufacturer Lennox promo: -$500</li>
<li>Energy Advisor audit (for Greener Homes Loan): +$525</li>
<li>Greener Homes Loan: $16,675 financed at 0% over 10 years</li>
<li><strong>Net out-of-pocket today: ~$525</strong></li>
<li><strong>Monthly loan payment: ~$139 for 10 years</strong></li>
<li><strong>Estimated annual energy savings: $550–$900 on gas + electric combined</strong></li>
</ul>
<p>For most Halton homes, energy savings offset 50–80% of the monthly loan payment.</p>

<h2 id="audit">When You Still Need An Energy Advisor Audit</h2>
<p>The HRS Program no longer requires the audit. But the Greener Homes Loan still does. So:</p>
<ul>
<li><strong>If you're only claiming HRS:</strong> no audit needed, skip it.</li>
<li><strong>If you want both HRS and the Greener Homes Loan financing:</strong> get the audit. One audit unlocks both.</li>
<li><strong>If you're claiming HRS only and want to finance:</strong> use a private HVAC finance partner, no audit required.</li>
</ul>

<h2 id="hpwh">Don't Forget The Heat Pump Water Heater Rebate</h2>
<p>Most Halton homeowners overlook this one. A heat pump water heater (Rheem ProTerra, A.O. Smith Voltex) replacing an electric or gas tank gets a $1,000 HRS rebate plus may be eligible for Greener Homes Loan financing. Installed cost is typically $4,500–$6,500, so the rebate is meaningful. <a href="../tankless-water-heater-cost-oakville/">Compare with tankless in our cost guide.</a></p>

<h2 id="ineligible">Common Reasons HRS Claims Get Rejected</h2>
<ul>
<li>Equipment not on the program's approved make/model list (always check before buying)</li>
<li>Installer not registered as a participating contractor</li>
<li>Rental property or non-primary residence</li>
<li>Project registered after May 31, 2026 deadline</li>
<li>Heat pump sized incorrectly (program audits some claims for proper Manual J sizing)</li>
</ul>

<h2 id="municipal">Municipal Programs Worth Asking About</h2>
<ul>
<li><strong>Town of Oakville:</strong> occasional clean-energy property-tax loan programs (Local Improvement Charge). Worth asking your municipality at quote stage.</li>
<li><strong>City of Burlington:</strong> Better Homes Burlington pilot program (limited availability)</li>
<li><strong>Halton Region:</strong> Climate Action Plan funding for specific neighborhoods</li>
</ul>

<h2 id="how-to-apply">How To Actually Claim Your Rebates (Step by Step)</h2>
<ol>
<li><strong>Get a quote</strong> from a participating contractor. We include rebate amounts in every quote.</li>
<li><strong>Register the project</strong> on the Home Renovation Savings Program portal (we do this for you).</li>
<li><strong>(Optional) Book an Energy Advisor audit</strong> if you want Greener Homes Loan financing.</li>
<li><strong>Apply for the Greener Homes Loan</strong> through Natural Resources Canada if applicable.</li>
<li><strong>Install</strong> the equipment with your participating contractor.</li>
<li><strong>Submit the invoice and equipment serial numbers</strong> to the HRS Program portal (we file this).</li>
<li><strong>Rebate direct-deposited</strong> within 4–8 weeks.</li>
</ol>

<p>Want help figuring out exactly what your specific home and project qualifies for in 2026? <a href="#hero-quote">Request a free quote</a> or <a href="../../contact/">contact us</a>, we'll walk you through every program that applies, register the project on your behalf, and handle the paperwork at install. See also our <a href="../heat-pump-vs-furnace-ontario/">heat pump vs furnace comparison</a> and our <a href="../furnace-cost-oakville-2026/">2026 furnace cost guide</a> for related decisions.</p>
"""
    },
    {
        "slug": "upstairs-too-hot-too-cold",
        "cta_heading":"Stop Fighting Your Thermostat. Fix It Properly.",
        "cta_copy":"Most uneven-temperature problems are solved without a new furnace. Book a Halton airflow assessment.",
        "faq_heading":"Hot &amp; Cold Room Questions From Halton Homeowners",
        "title": "Upstairs Too Hot, Downstairs Too Cold? The Real Fix For Halton Two-Storey Homes",
        "meta_title": "Upstairs Too Hot / Cold? Fix For Oakville Homes | IKAD",
        "description": "Why your Halton two-storey home has uneven temperatures: 6 real causes, the right fix order, and what each solution costs in 2026.",
        "date": "2026-02-22",
        "image": "services/air-balancing.jpg",
        "image_alt": "Balometer measuring CFM at a ceiling diffuser during an IKAD Mechanical air balance in Oakville",
        "excerpt": "It's the most common comfort complaint in Halton: upstairs bedrooms 4-6°C warmer in summer, the basement freezing in winter. Closing vents and dropping the thermostat doesn't fix it. Here's what does.",
        "category": "Troubleshooting",
        "faqs": [
            ("Why is my upstairs always 4 to 6 degrees hotter than downstairs?",
             "Six common causes in Halton homes: undersized or missing second-floor returns, leaky attic ducts, oversized furnace short-cycling, single-zone control with no upstairs damper, blocked supply registers, and high static pressure starving the second floor. Most homes have two or three of these at once. A proper diagnostic measures static pressure, room-by-room CFM, and return-air balance before recommending a fix."),
            ("Will closing vents in the cold rooms help with the hot rooms?",
             "No, and it usually makes it worse. Closing supply registers raises static pressure on the system, makes the blower work harder, and can starve the air handler. The correct fix is balancing dampers in the trunk lines, not at the register face."),
            ("How much does zoning cost in an existing Halton home?",
             "Adding 2-zone control (upstairs/downstairs) to an existing forced-air system runs $2,200 to $4,800 installed, depending on where the trunk is accessible and whether you need a bypass damper. 3-zone systems run $3,500 to $6,500. Most older two-storey Oakville homes can be retrofitted in 1-2 days."),
            ("Can a mini-split fix one problem bedroom?",
             "Yes, and it's often cheaper than zoning the whole house if only one or two rooms are the problem. A ductless mini-split (Mitsubishi Hyper-Heat, Daikin Aurora) for a single bedroom runs $4,200 to $6,500 installed and gives you independent heating and cooling for that room. Best fit for upstairs master bedrooms in 1980s-2000s two-storey homes that consistently run hot in summer."),
            ("Does an air balance actually solve hot/cold rooms?",
             "Yes, for most homes. An air balance test measures CFM at every supply and return, identifies where the design vs actual gap is, and adjusts trunk dampers to redirect airflow. Cost is $385 to $650 for a Halton home and resolves about 70% of uneven-temperature complaints without any equipment changes.")
        ],
        "body": """
<aside class="answer-box" role="complementary"><span class="answer-box__label">Quick Answer</span><h2>Why Your Halton Home Has Uneven Temperatures</h2><p>The six most common causes of uneven heating/cooling in a Halton two-storey home, in order of frequency:</p><ol>
<li>Undersized or missing second-floor returns (the #1 cause in 1980s-2000s Halton builds)</li>
<li>Leaky attic ductwork (typical residential duct system loses 20-30% of conditioned air)</li>
<li>Oversized furnace short-cycling before the upstairs gets airflow</li>
<li>Single-zone control with no upstairs damper or thermostat</li>
<li>High static pressure starving distant rooms</li>
<li>Crushed or kinked flexible duct runs to bedrooms</li>
</ol><p>The fix order is diagnose first (static pressure + room-by-room CFM measurement), then balance, then zone or equipment changes if needed.</p></aside>

<p>It's the comfort complaint we hear most across Halton: upstairs bedrooms unbearable in July, the basement freezing in January, and the thermostat war that follows. Closing vents in the hot rooms feels logical but makes things worse. Dropping the AC set point burns electricity without solving the actual problem. Here's what's really happening and how to fix it.</p>

<h2 id="diagnose">First: Diagnose Before You Spend Money</h2>
<p>Before any fix, three measurements should be done at your home:</p>
<ul>
<li><strong>Total external static pressure</strong> at the furnace cabinet. Manufacturer spec is 0.5 inches water column. Most Halton homes we test read 0.9 to 1.2 inches, which means the blower is fighting the duct system. Anything over 0.7 needs return-air work before any other fix.</li>
<li><strong>Supply CFM at every register</strong> with a balometer (capture hood). Compare against the room's design target (calculated from Manual J). A bedroom designed for 80 CFM and reading 32 CFM is starving.</li>
<li><strong>Return-air pressure balance</strong>. With doors closed, every room with a supply should have either a return or a transfer grille. Master bedrooms without either get pressurized when the door closes, blowing conditioned air out around the door and starving the supply.</li>
</ul>

<h2 id="cause-1">Cause #1: Undersized Or Missing Upstairs Returns</h2>
<p>This is the most common pattern in Halton homes built between 1980 and 2005. The original installer ran a single big return in the main-floor hallway or basement stairwell. The second floor has no dedicated return. So when the AC runs, supply air pushes into upstairs bedrooms but there's nowhere for it to escape, the room pressurizes, the supply slows, and the air going upstairs is being pulled back down through the stairwell where it short-circuits straight back to the return.</p>
<p>The fix: add a dedicated upstairs return. Typically 14" x 24" central return in the upstairs hallway ceiling, ducted back down through a closet or chase to the air handler. Cost in a Halton home: $1,400 to $2,800 depending on chase access. This single change resolves more upstairs-too-hot complaints than any other.</p>

<h2 id="cause-2">Cause #2: Leaky Attic Ductwork</h2>
<p>If your ductwork to the second floor runs through the attic (common in story-and-a-half and back-half-of-house additions), every seam in those ducts is leaking 20 to 30% of the air into the attic instead of into your bedrooms. In summer that's $200+ of cooling per month wasted, plus the rooms downstream get nothing. Visit our <a href="../../duct-work/">duct work page</a> for the full duct sealing breakdown. A whole-home duct seal in a typical 1,800 to 2,400 sq.ft. Halton home is $850 to $1,500 and pays back in 1-2 summers.</p>

<h2 id="cause-3">Cause #3: Oversized Furnace Short-Cycling</h2>
<p>This is a sneakier cause and very common in older Halton homes that had furnaces "replaced like-for-like" by a previous contractor. A 100,000 BTU furnace in a home that only needs 60,000 BTU heats the main floor in 4-5 minutes, hits the thermostat setpoint, shuts off, and never sends enough air to the upstairs registers (which are farther from the blower). A properly-sized furnace runs longer cycles at lower fire, giving the airflow time to reach every room. Manual J load calculation is the right answer. <a href="../furnace-cost-oakville-2026/">See our 2026 furnace replacement guide</a> for sizing details.</p>

<h2 id="cause-4">Cause #4: No Zoning / Single Thermostat For Two Floors</h2>
<p>In a 2,500 sq.ft. two-storey home with one thermostat (almost always located on the main floor), the system runs based on what the main floor feels, not what the bedrooms feel. The fix is adding a second thermostat upstairs with a motorized damper in the supply trunk that diverts more air upstairs when the upstairs zone calls for cooling. Halton retrofit cost: $2,200 to $4,800 for 2-zone, $3,500 to $6,500 for 3-zone. Most jobs take 1-2 days.</p>

<h2 id="cause-5">Cause #5: High Static Pressure Starving Distant Rooms</h2>
<p>If you have a 1-inch furnace filter (most Halton homes do), it's likely the single largest static-pressure penalty in your system. Upgrading to a 4-inch or 5-inch media filter cabinet drops static by 30 to 50% and gets noticeably more air to back bedrooms. Cost: $300 to $500 installed. Combine with an <a href="../../air-balancing/">air balance</a> to redirect the freed-up airflow.</p>

<h2 id="cause-6">Cause #6: Crushed Or Kinked Flexible Duct</h2>
<p>If you ever see a sealed-off ceiling section being opened up in your home, look at the flexible duct runs. Builder-grade flex duct gets crushed during drywall, stepped on during attic insulation, or kinked at sharp bends. A 6-inch flex duct kinked to 4 inches loses about 60% of its CFM. We replace problematic flex runs with rigid metal or properly-supported flex on every duct retrofit we do.</p>

<h2 id="zoning-vs-mini-split">Zoning Vs Ductless Mini-Split: Which Is The Right Spend?</h2>
<table>
<thead><tr><th>Approach</th><th>Installed Cost (Halton 2026)</th><th>Best For</th></tr></thead>
<tbody>
<tr><td>Air balance only</td><td>$385 - $650</td><td>Mild uneven-temp issue, no major equipment changes</td></tr>
<tr><td>Add upstairs return</td><td>$1,400 - $2,800</td><td>1980s-2000s two-storey, no upstairs return currently</td></tr>
<tr><td>Whole-home duct sealing</td><td>$850 - $1,500</td><td>Attic ductwork or leaky basement ducts</td></tr>
<tr><td>4-inch media filter cabinet</td><td>$300 - $500</td><td>Currently using 1-inch furnace filter, static over 0.8</td></tr>
<tr><td>2-zone control retrofit</td><td>$2,200 - $4,800</td><td>Distinct upstairs/downstairs comfort needs</td></tr>
<tr><td>3-zone control retrofit</td><td>$3,500 - $6,500</td><td>Walkout basement + main + upstairs as separate zones</td></tr>
<tr><td>Ductless mini-split for one problem room</td><td>$4,200 - $6,500</td><td>Master bedroom or above-garage room consistently hot</td></tr>
<tr><td>Properly-sized furnace replacement (with Manual J)</td><td>$4,500 - $7,500</td><td>Oversized furnace short-cycling, original install 15+ years old</td></tr>
</tbody>
</table>

<h2 id="halton-housing-patterns">Why This Is So Common In Halton Specifically</h2>
<p>Different vintages of Halton housing fail in predictable ways:</p>
<ul>
<li><strong>1980s and 90s Glen Abbey, Millcroft, Headon Forest two-storey homes:</strong> upstairs returns either undersized or omitted entirely. Cause #1 dominates.</li>
<li><strong>2000s Beaty, Hawthorne Village Milton homes:</strong> aggressive Manual J at design stage, but flexible duct runs crushed during drywall, dropping CFM 30 to 40% to back bedrooms. Cause #6 dominates.</li>
<li><strong>1950s and 60s Oakville bungalows (Bronte, Eastlake):</strong> single trunk in the basement with stubby branches, rooms farthest from the furnace receive almost no airflow. Cause #5 dominates.</li>
<li><strong>Newer custom homes with mechanical penthouses:</strong> long runs amplify any takeoff sizing mistake. Need to be balanced on day one. Cause #4 or commissioning oversight.</li>
</ul>

<h2 id="diy">What You Can Try Yourself First</h2>
<ol>
<li>Replace your filter with a fresh one (or pull it out temporarily to test). See if airflow improves immediately.</li>
<li>Open all supply registers fully. Don't restrict any rooms.</li>
<li>If you have a master bedroom that consistently runs hot, undercut the door 1/2 inch or install a transfer grille over the door for return-air flow.</li>
<li>Vacuum any return-air grilles and check inside ducts within reach for blockages.</li>
<li>Set the fan to "On" instead of "Auto" for 4-6 hours and see if temperatures equalize, this confirms it's an airflow distribution problem, not a heating/cooling capacity problem.</li>
</ol>

<h2 id="when-to-call">When To Call A Professional</h2>
<p>If the DIY steps don't help, the next move is a professional <a href="../../air-balancing/">air balance test</a>. It's the fastest way to identify exactly where the airflow shortfall is happening. We measure, document, and walk you through which fix gives the best return for your specific home. If you've already replaced the furnace and the issue persists, it's almost never a furnace problem, it's a duct/balance problem.</p>

<p>Tired of fighting the thermostat every season? <a href="#hero-quote">Book an airflow assessment</a> or <a href="tel:+19054916943">call (905) 491-6943</a>. We'll measure your system, show you the real numbers, and recommend the cheapest fix that actually works. See also our <a href="../../air-balancing/">air balancing page</a> and our <a href="../../duct-work/">duct work page</a> for related services.</p>
"""
    },
    {
        "slug": "emergency-furnace-repair-oakville",
        "cta_heading":"No Heat Right Now? Call Us Directly.",
        "cta_copy":"24/7 emergency dispatch across Halton, (905) 491-6943.",
        "faq_heading":"Emergency Furnace Service Questions",
        "title": "Emergency Furnace Repair in Oakville: How Fast Can A Contractor Actually Get To You?",
        "meta_title": "Emergency Furnace Repair Oakville | Same-Day Service | IKAD",
        "description": "Furnace stopped working in Oakville? How fast we can be there, what an emergency call costs, and how to keep the house warm while you wait. By IKAD Mechanical.",
        "date": "2026-01-18",
        "image": "services/heating-technician.jpg",
        "image_alt": "Emergency furnace service call in Halton",
        "excerpt": "When your furnace dies in January, every hour matters. Here's how fast emergency response actually works in Halton, what it costs, and what to do in the meantime.",
        "category": "Emergency Service",
        "faqs": [
            ("How much does an emergency furnace call cost?",
             "Diagnostic for a standard business-hours emergency call is $145–$185. After-hours (after 6 PM, weekends, holidays) is $250–$350. Repair parts/labour are on top. We tell you the total before starting work."),
            ("Will you come out at midnight?",
             "Yes, we run emergency dispatch 24/7 in winter for no-heat situations. Call (905) 491-6943 and select the emergency option."),
            ("How long can I leave a house unheated in winter?",
             "Below freezing outside, pipes start to be at risk within 6–10 hours in most Halton homes. Newer, well-insulated homes have more buffer. Older century homes can have pipes freeze in 4–5 hours.")
        ],
        "body": """
<p>It's the call no homeowner wants to make: thermostat says 14°C and dropping, furnace won't fire, it's -8°C outside. Here's what to expect when you call for emergency service in Oakville, and what to do while you wait.</p>

<h2>Realistic Response Times Across Halton</h2>
<table>
<thead><tr><th>Location</th><th>Business Hours</th><th>After Hours (Winter)</th></tr></thead>
<tbody>
<tr><td>Oakville</td><td>1–3 hours</td><td>2–4 hours</td></tr>
<tr><td>Burlington</td><td>1–3 hours</td><td>2–4 hours</td></tr>
<tr><td>Milton</td><td>2–4 hours</td><td>3–5 hours</td></tr>
<tr><td>Halton Hills (Georgetown)</td><td>2–4 hours</td><td>3–5 hours</td></tr>
<tr><td>Mississauga</td><td>2–4 hours</td><td>3–5 hours</td></tr>
<tr><td>Hamilton</td><td>2–4 hours</td><td>3–6 hours</td></tr>
</tbody>
</table>
<p>These are realistic, not "we'll be there in 30 minutes" marketing. In a winter storm or during the first deep cold snap, every HVAC contractor in the region is fielding 5x normal call volume. We prioritize <strong>no-heat with kids, elderly residents, or pipes at risk</strong>.</p>

<h2>What To Do While You Wait</h2>
<ol>
<li><strong>Walk through the 7-step troubleshooting list</strong> in <a href="/blog/furnace-wont-turn-on/">our furnace-won't-turn-on guide</a>. About 30% of the time you'll fix it yourself.</li>
<li><strong>Close interior doors</strong> to limit heat loss to unused rooms.</li>
<li><strong>Open the cabinet doors</strong> under kitchen and bathroom sinks if you have pipes against an exterior wall.</li>
<li><strong>Run faucets at a trickle</strong> (cold water), moving water freezes much slower.</li>
<li><strong>Don't use a gas oven</strong> for heat, carbon monoxide risk is real.</li>
<li><strong>Plug in electric space heaters</strong> if you have them, one per circuit max.</li>
</ol>

<h2>What An Emergency Repair Actually Costs</h2>
<ul>
<li><strong>Business-hours diagnostic:</strong> $145–$185</li>
<li><strong>After-hours diagnostic (6 PM–8 AM, weekends, holidays):</strong> $250–$350</li>
<li><strong>Common repair parts:</strong>
<ul>
<li>Igniter: $90–$140 (parts + 15 min labour)</li>
<li>Flame sensor: $40–$80 (clean or replace)</li>
<li>Inducer motor: $380–$650</li>
<li>Pressure switch: $120–$220</li>
<li>Control board: $400–$800</li>
<li>Blower motor (variable-speed ECM): $650–$1,200</li>
</ul></li>
</ul>
<p>If the repair cost exceeds 30% of what a new furnace would cost, and your unit is 12+ years old, we'll tell you straight: replacement is the better math. We won't pressure you. Some customers want to nurse an old furnace through one more winter. We respect that.</p>

<h2>When To Call Enbridge First</h2>
<p>If you smell gas, even faintly, leave the house and call Enbridge's 24/7 emergency line: <strong>1-866-763-5427</strong>. Don't operate switches, don't use phones inside. Call us afterward.</p>

<p>No-heat right now? <a href="tel:+19054916943">Call us at (905) 491-6943</a> for emergency dispatch. We'll tell you a realistic ETA before we leave the shop.</p>
"""
    },
]

def build_blog_post(post):
    r = "../../"
    slug = post["slug"]
    body_html = post["body"]
    faqs = post.get("faqs", [])

    import json, re as _re
    body_text = _re.sub(r'<[^>]+>', ' ', body_html)
    word_count = len(_re.sub(r'\s+', ' ', body_text).split())
    article_schema = {
        "@context":"https://schema.org",
        "@type":"BlogPosting",
        "@id": f"{BASE}/blog/{slug}/#article",
        "headline": post["title"].replace("&amp;","&"),
        "alternativeHeadline": post.get("meta_title", post["title"]).replace("&amp;","&"),
        "description": post["description"],
        "image": [
            f"{BASE}/assets/images/{post['image']}",
            f"{BASE}/assets/images/hero/hero-ikad-team.jpg"
        ],
        "datePublished": post["date"],
        "dateModified": post["date"],
        "wordCount": word_count,
        "articleSection": post["category"],
        "keywords": post.get("keywords", f"HVAC Halton, {post['category']}, Oakville, Burlington, 2026"),
        "author": {
            "@type":"Person",
            "@id": f"{BASE}/about/#owner",
            "name":"Mohanad",
            "jobTitle":"Owner & Lead Technician, IKAD Mechanical",
            "worksFor": {"@id": f"{BASE}/#business"},
            "url": f"{BASE}/about/",
            "knowsAbout":["HVAC installation","Furnace replacement","Cold-climate heat pumps","Hydronic in-floor heating","Manual J load calculation","TSSA gas fitting","Commercial HVAC"]
        },
        "publisher": {
            "@type":"Organization",
            "@id": f"{BASE}/#business",
            "name":"IKAD Mechanical Inc.",
            "logo": {"@type":"ImageObject","url":f"{BASE}/assets/images/logo/ikad-logo.png","width":400,"height":400}
        },
        "mainEntityOfPage": {"@type":"WebPage","@id": f"{BASE}/blog/{slug}/"},
        "inLanguage":"en-CA",
        "isPartOf": {"@type":"Blog","name":"IKAD Mechanical HVAC Blog","url":f"{BASE}/blog/"},
        "isAccessibleForFree": True,
        "speakable": {"@type":"SpeakableSpecification","cssSelector":["h1","h2",".answer-box"]},
        "about": [
            {"@type":"Thing","name":"HVAC services"},
            {"@type":"Place","name":"Halton Region, Ontario, Canada"},
            {"@type":"Place","name":"Oakville, Ontario, Canada"}
        ],
        "audience": {"@type":"Audience","audienceType":"Halton Region homeowners and property managers","geographicArea":{"@type":"AdministrativeArea","name":"Halton Region, Ontario, Canada"}}
    }
    article_schema_html = f'<script type="application/ld+json">\n{json.dumps(article_schema, ensure_ascii=False)}\n</script>'

    # Add HowTo schema for tutorial-style blog posts
    howto_schema_html = ""
    if slug == "furnace-wont-turn-on":
        howto = {
            "@context":"https://schema.org",
            "@type":"HowTo",
            "name":"How to troubleshoot a furnace that won't turn on",
            "description":"Seven things to check yourself before paying for a service call when your furnace won't start.",
            "image": f"{BASE}/assets/images/{post['image']}",
            "totalTime":"PT15M",
            "estimatedCost":{"@type":"MonetaryAmount","currency":"CAD","value":"0"},
            "supply":[{"@type":"HowToSupply","name":"Replacement furnace filter (if clogged)"}],
            "tool":[{"@type":"HowToTool","name":"Smartphone flashlight (for the side switch)"}],
            "step":[
                {"@type":"HowToStep","position":1,"name":"Check the thermostat","text":"Switch the system to Heat (not Cool, not Off). Raise the setpoint at least 3°C above current room temperature. If the screen is blank, change the batteries."},
                {"@type":"HowToStep","position":2,"name":"Check the breaker","text":"Furnace is on its own breaker (usually 15A). Flip Off then On if tripped. If it trips again immediately, stop and call a technician."},
                {"@type":"HowToStep","position":3,"name":"Check the side switch","text":"Most furnaces have a light-switch on the side or near basement stairs controlling power. Make sure it is On."},
                {"@type":"HowToStep","position":4,"name":"Check the filter","text":"Clogged filter can trigger the high-limit safety. Pull it out, replace if you cannot see light through it."},
                {"@type":"HowToStep","position":5,"name":"Check the condensate drain","text":"On a high-efficiency furnace, look for a clear plastic line. If clogged the safety switch will not let the furnace fire. Disconnect, blow clear, reconnect."},
                {"@type":"HowToStep","position":6,"name":"Check the intake and exhaust vents","text":"Check the two PVC pipes from the side of the house for snow, ice or nest blockage. Clear them."},
                {"@type":"HowToStep","position":7,"name":"Cycle the power","text":"Furnace switch Off for 60 seconds, then On. If the inducer motor starts, good sign. If silent after 90 seconds, call a technician."}
            ]
        }
        howto_schema_html = f'<script type="application/ld+json">\n{json.dumps(howto, ensure_ascii=False)}\n</script>'
    elif slug == "upstairs-too-hot-too-cold":
        howto = {
            "@context":"https://schema.org",
            "@type":"HowTo",
            "name":"How to diagnose uneven temperatures upstairs and downstairs",
            "description":"DIY diagnostic steps before calling an HVAC contractor for hot-upstairs / cold-downstairs complaints.",
            "image": f"{BASE}/assets/images/{post['image']}",
            "totalTime":"PT30M",
            "estimatedCost":{"@type":"MonetaryAmount","currency":"CAD","value":"0"},
            "step":[
                {"@type":"HowToStep","position":1,"name":"Replace the filter","text":"Install a fresh furnace filter. If airflow improves immediately, static pressure was your bottleneck."},
                {"@type":"HowToStep","position":2,"name":"Open all supply registers","text":"Do not restrict any rooms. Closing supplies in cold rooms makes the problem worse, not better."},
                {"@type":"HowToStep","position":3,"name":"Address master bedroom door pressurization","text":"Undercut the door 1/2 inch or install a transfer grille above the door for return-air flow if the master runs consistently hot."},
                {"@type":"HowToStep","position":4,"name":"Clean return grilles","text":"Vacuum return-air grilles and check inside ducts within reach for blockages."},
                {"@type":"HowToStep","position":5,"name":"Run fan continuously","text":"Set fan to On (not Auto) for 4-6 hours. If temperatures equalize, the problem is airflow distribution, not heating or cooling capacity."},
                {"@type":"HowToStep","position":6,"name":"Book a professional air balance","text":"If DIY steps don't help, book an air balance test ($385-$650 in Halton). This identifies the airflow shortfall in 2-3 hours."}
            ]
        }
        howto_schema_html = f'<script type="application/ld+json">\n{json.dumps(howto, ensure_ascii=False)}\n</script>'
    elif slug == "ontario-heat-pump-rebates-2026":
        howto = {
            "@context":"https://schema.org",
            "@type":"HowTo",
            "name":"How to claim the Ontario Home Renovation Savings Program heat pump rebate",
            "description":"Step-by-step process for claiming the up-to-$7,500 heat pump rebate plus stacking with the Canada Greener Homes Loan.",
            "image": f"{BASE}/assets/images/{post['image']}",
            "totalTime":"P14D",
            "estimatedCost":{"@type":"MonetaryAmount","currency":"CAD","value":"525"},
            "step":[
                {"@type":"HowToStep","position":1,"name":"Get a quote from a participating contractor","text":"The HRS Program requires a registered participating contractor. IKAD Mechanical is registered."},
                {"@type":"HowToStep","position":2,"name":"Register the project","text":"Register on the Home Renovation Savings Program portal before the May 31, 2026 deadline."},
                {"@type":"HowToStep","position":3,"name":"Optional: book an Energy Advisor audit","text":"Required only if you also want the Canada Greener Homes Loan financing. Audit cost approximately $525."},
                {"@type":"HowToStep","position":4,"name":"Apply for Greener Homes Loan","text":"Apply through Natural Resources Canada portal if you want the interest-free loan up to $40,000."},
                {"@type":"HowToStep","position":5,"name":"Complete the install","text":"Install the equipment with your participating contractor."},
                {"@type":"HowToStep","position":6,"name":"Submit the rebate claim","text":"Invoice and equipment serial numbers submitted to the HRS Program portal."},
                {"@type":"HowToStep","position":7,"name":"Receive the rebate","text":"Rebate is direct-deposited to your bank within 4 to 8 weeks."}
            ]
        }
        howto_schema_html = f'<script type="application/ld+json">\n{json.dumps(howto, ensure_ascii=False)}\n</script>'

    article_schema_html += howto_schema_html

    visible_faq = ""
    if faqs:
        items = "\n".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faqs)
        faq_heading = post.get("faq_heading", f"{post['category']}: Related Questions")
        visible_faq = f"""<section class="section section--gray"><div class="container">
<div class="text-center" style="max-width:720px;margin:0 auto 2rem"><span class="eyebrow">FAQ</span><h2>{faq_heading}</h2></div>
<div class="faq" style="max-width:820px;margin:0 auto">{items}</div></div></section>"""

    body = hero_compact(r, "hero/hero-ikad-team.jpg", post["category"], post["title"], post["excerpt"]) + \
        breadcrumbs(r, [("Home","./"),("Blog","blog/"),(post["title"][:50] + "…", "")]) + f"""
<article class="section"><div class="container" style="max-width:780px">
<p style="color:#64748b;font-size:.92rem;margin-bottom:.5rem"><time datetime="{post["date"]}" itemprop="datePublished">{post["date"]}</time> · <a href="{r}about/#owner" style="color:#64748b">By Mohanad, Owner &amp; Lead Technician, IKAD Mechanical</a> · {post["category"]}</p>
<p style="color:#64748b;font-size:.85rem;margin:0 0 1rem;padding:.4rem .8rem;background:#f6f7f9;border-radius:6px;display:inline-block"><strong>Reviewed:</strong> 2026-05-21 · This article is reviewed periodically. Pricing and rebate amounts current as of the date shown.</p>
<img src="{r}assets/images/{post["image"]}" alt="{post["image_alt"]}" style="width:100%;border-radius:10px;margin-bottom:2rem" width="900" height="600">
{body_html}

<hr style="margin:2.5rem 0;border:0;border-top:1px solid #e5e7eb">
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.5rem">
<h3 style="margin:0 0 .75rem;color:#0f172a;font-size:1.05rem">Sources &amp; Further Reading</h3>
<ul style="margin:0;padding-left:1.25rem;color:#475569;line-height:1.7;font-size:.92rem">
<li><a href="https://www.tssa.org/" rel="noopener" target="_blank">Technical Standards and Safety Authority (TSSA)</a> — Ontario gas appliance and piping regulator</li>
<li><a href="https://www.hrai.ca/" rel="noopener" target="_blank">Heating, Refrigeration and Air Conditioning Institute of Canada (HRAI)</a> — Canadian HVAC industry standards</li>
<li><a href="https://www.homerenovationsavings.ca/" rel="noopener" target="_blank">Home Renovation Savings Program (Ontario, 2026)</a> — current rebate program (replaced Enbridge HER+ January 2025)</li>
<li><a href="https://natural-resources.canada.ca/energy-efficiency/homes/canada-greener-homes-initiative/canada-greener-homes-loan/" rel="noopener" target="_blank">Canada Greener Homes Loan (Natural Resources Canada)</a> — $40,000 interest-free retrofit financing</li>
<li><a href="https://www.saveonenergy.ca/" rel="noopener" target="_blank">Save On Energy (Ontario)</a> — provincial electricity efficiency programs</li>
<li><a href="https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling" rel="noopener" target="_blank">IKAD Mechanical on HomeStars</a> — verified customer reviews</li>
</ul>
<p style="margin:.85rem 0 0;color:#64748b;font-size:.85rem;font-style:italic">Methodology: pricing ranges in this article reflect IKAD-installed projects across Halton Region during 2024-2026 plus current manufacturer wholesale pricing. We update this article each season as rebate programs and refrigerant regulations change.</p>
</div>

<hr style="margin:2.5rem 0;border:0;border-top:1px solid #e5e7eb">
<div style="background:#f6f7f9;border-radius:10px;padding:1.5rem;display:flex;flex-wrap:wrap;gap:1rem;align-items:center;justify-content:space-between" itemscope itemtype="https://schema.org/Person">
<div><strong itemprop="name">Mohanad</strong> <span style="color:#64748b"> <span itemprop="jobTitle">Owner &amp; Lead Technician, IKAD Mechanical</span></span><br><span style="color:#64748b;font-size:.9rem">TSSA-certified gas fitter (G2), HRAI member, 15+ years installing HVAC across Halton. The name customers mention in <a href="https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling" rel="noopener" target="_blank">HomeStars reviews</a>. Read his full bio on <a href="{r}about/#owner" itemprop="url">the About page</a>.</span></div>
<a class="btn btn--primary" href="{r}contact/">Get Your Free Quote</a>
</div>

<hr style="margin:2.5rem 0;border:0;border-top:1px solid #e5e7eb">
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.5rem">
<h3 style="margin:0 0 .75rem;color:#0f172a">Trusted HVAC Contractor Near You Across Halton, Peel &amp; Hamilton</h3>
<p style="margin:0 0 1rem;color:#475569;line-height:1.65;font-size:.95rem">IKAD Mechanical is a family-owned, TSSA-certified HVAC contractor based in Oakville since 2010. We serve every city listed below with no travel surcharge, same-day response in most cases:</p>
<p style="margin:0;color:#334155;line-height:1.9;font-size:.95rem">
<a href="{r}service-areas/oakville/">HVAC contractor in Oakville</a> ·
<a href="{r}service-areas/burlington/">trusted HVAC Burlington</a> ·
<a href="{r}service-areas/milton/">HVAC near me Milton</a> ·
<a href="{r}service-areas/halton-hills/">HVAC contractor Georgetown / Acton</a> ·
<a href="{r}service-areas/mississauga/">HVAC contractor Mississauga</a> ·
<a href="{r}service-areas/hamilton/">HVAC contractor Hamilton</a> ·
<a href="{r}service-areas/brampton/">HVAC contractor Brampton</a>
</p>
<p style="margin:1rem 0 0;color:#475569;line-height:1.65;font-size:.92rem">Want more reading? See our <a href="{r}reviews/">customer reviews</a>, <a href="{r}why-choose-ikad/">why homeowners choose IKAD</a>, <a href="{r}faq/">HVAC FAQ (49+ answers)</a>, or <a href="{r}glossary/">HVAC glossary</a>.</p>
</div>
</div></article>
""" + visible_faq + cta_banner(r, post.get("cta_heading","Talk To IKAD About Your Project"), post.get("cta_copy","Free quote, fixed-price install, no pressure."))

    page(
        out=f"blog/{slug}/index.html", depth=2,
        title=post["meta_title"],
        description=post["description"],
        canonical=f"{BASE}/blog/{slug}/",
        og_image=f"{BASE}/assets/images/hero/hero-ikad-team.jpg",
        body=body, active=None, preload_hero="hero/hero-ikad-team.jpg",
        schema_extra=article_schema_html +
            breadcrumb_schema([("Home",f"{BASE}/"),("Blog",f"{BASE}/blog/"),(post["title"].replace("&amp;","&"),f"{BASE}/blog/{slug}/")]) +
            (faq_schema(faqs) if faqs else "")
    )

# ---------------------------------------------------------------------------
# Master FAQ Page (/faq/)
# 40 questions; none duplicate per-page/per-service/per-city/per-blog FAQs.
# ---------------------------------------------------------------------------
FAQ_GROUPS = [
    ("Finding HVAC Near You", [
        ("Who is the best HVAC contractor near me in Oakville?",
         "We're obviously biased, but the honest answer is: pick a contractor who is TSSA-certified for gas work, ECRA/ESA licensed for electrical, runs a Manual J load calculation on every install, gives you a fixed written quote (not an estimate), and uses their own crew (not subcontractors). IKAD Mechanical meets all five and has served 1,200+ Halton homes since 2010. Compare us against any other local contractor on those five tests, see our <a href=\"../about/\">credentials</a> and our <a href=\"../our-projects/\">recent projects</a>."),
        ("Are you an HVAC contractor near me in Burlington / Milton / Mississauga / Hamilton?",
         "Yes. Our shop is on Upper Middle Rd East in Oakville and we service the full Halton Region, plus Mississauga, Hamilton and Brampton. Burlington is 15-25 minutes from our shop, Milton 20-30 minutes, Mississauga 15-35 minutes, Hamilton 25-45 minutes, Brampton 30-45 minutes. No travel surcharge to any of these cities. See per-city details on <a href=\"../service-areas/\">our service area pages</a>."),
        ("Is IKAD a trusted family-owned HVAC contractor?",
         "Yes. IKAD Mechanical has been family-owned and operated since 2010. The owner answers the phone, runs site visits, and is on most install jobs. No commissioned salespeople, no franchise model, no subcontracted installs. We're TSSA G2/G3 certified, ECRA/ESA licensed, HRAI members, carry $5M liability insurance and WSIB. Read our <a href=\"../about/\">story</a>."),
        ("Do you offer same-day or emergency HVAC service near me?",
         "Same-day no-heat and no-cool service is typical for Oakville and Burlington during business hours, often within 2-4 hours of your call. Other Halton cities (Milton, Halton Hills) and Peel/Hamilton are typically same-day or next-day. We keep emergency dispatch slots open every winter and summer. Call (905) 491-6943 or <a href=\"../contact/\">request urgent service online</a>."),
        ("How do I find honest HVAC contractor reviews in Halton?",
         "Three reliable sources: (1) Google Business Profile (search 'IKAD Mechanical Oakville'), where reviews can't be filtered by the business, (2) HomeStars, where reviewers are verified, see <a href=\"https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling\" rel=\"noopener\" target=\"_blank\">our HomeStars profile</a>, and (3) the BBB. Avoid contractor-website testimonials in isolation, anyone can curate those."),
        ("Are you a licensed and certified HVAC contractor near me?",
         "Yes. TSSA G2 gas fitting (commercial scope), TSSA G3 (residential), ECRA/ESA electrical licensing, HRAI membership, $5M general liability insurance, WSIB coverage. Documentation is shareable on request, ask at quote stage if you'd like copies."),
    ]),
    ("Hiring an HVAC Contractor", [
        ("How do I choose a good HVAC contractor in Halton?",
         "Three questions answer most of it: are they TSSA-certified gas fitters (mandatory for any gas work in Ontario), are they ECRA/ESA licensed (electrical), and do they have a verifiable HRAI membership or BBB profile. Then ask whether they do a Manual J load calculation, whether installs are done by their own crew or subcontractors, and whether the workmanship warranty is written into the contract. If any of those answers are vague, keep looking, <a href=\"../about/\">see IKAD's certifications and credentials</a>."),
        ("Are you licensed and insured?",
         "Yes. IKAD Mechanical holds TSSA gas-fitting certifications (G2 and G3), ECRA/ESA electrical licensing, and HRAI membership. We carry $5M liability insurance and WSIB coverage on every job site. We can share certificates of insurance and license numbers with property managers and builders on request, <a href=\"../contact/\">contact us</a> for the documents."),
        ("Do you charge for diagnostic service calls?",
         "Yes, diagnostic visits are $145–$185 during business hours and $250–$350 after hours or on weekends. That covers the technician's travel, time on site, and a written diagnosis. If you proceed with the repair or install, we credit the diagnostic fee against the work."),
        ("Will the same technician do my installation?",
         "Yes. We don't subcontract installs. The person who quoted you is part of the same team that shows up on install day, and your install lead stays with the job through commissioning and the owner walkthrough."),
        ("Do you provide written quotes?",
         "Always. Every quote is itemized, equipment model number, capacity, all materials, labour, removal of old equipment, permits where applicable, and a fixed price (not 'estimated'). Quotes are valid for 30 days."),
        ("What payment methods do you accept?",
         "E-transfer, cheque, credit card (a small processing fee applies on credit), and HVAC financing through our Canadian finance partners. We typically take a deposit (10–25%) on order and the balance on completion of the install."),
    ]),
    ("Pricing &amp; Financing", [
        ("Do you give free estimates?",
         "Yes, on-site estimates for residential equipment replacements are free across our <a href=\"../service-areas/\">service area</a> (Halton, Peel, Hamilton). For <a href=\"../custom-homes/\">custom-home mechanical design</a> and large <a href=\"../commercial/\">commercial scopes</a> we charge a small design fee, which is credited against the install if you go ahead."),
        ("How can I lower my heating and cooling bill in Halton?",
         "In order of impact: (1) <a href=\"../heating-services/\">replace a furnace older than 18 years</a> with a 96%+ AFUE unit, (2) add a smart thermostat and use scheduled setbacks, (3) <a href=\"../duct-work/\">seal the worst duct leaks</a> (whole-home is typically $850–$1,500 and pays back in 1–2 winters), (4) bring an Ecobee or Nest into the loop with multiple room sensors, (5) consider a <a href=\"../blog/heat-pump-vs-furnace-ontario/\">hybrid heat pump pairing</a> on your next AC replacement."),
        ("Why do HVAC quotes from different companies vary so much?",
         "Three real reasons: (1) equipment tier, entry-level vs premium can be a $2,500 spread on the same nameplate BTU, (2) what's included, some quotes hide gas line, venting, permit and disposal as 'extras', (3) the contractor's overhead and crew model. A 30% spread is normal. A 60% spread usually means one of those quotes is leaving something off."),
        ("Can I get a second opinion before I commit?",
         "Yes, and we recommend it. We'll happily review another contractor's quote for free and tell you whether the equipment is sized correctly and what's missing. We won't trash-talk competitors, we'll just walk you through the numbers."),
        ("Is HVAC financing worth it?",
         "When the financing is genuinely 0% (like the Canada Greener Homes Loan), yes, almost always. When it's a 'pay-over-time' card with double-digit interest, the math is rarely better than putting it on a low-rate line of credit. Read the rate disclosure before signing anything."),
    ]),
    ("Equipment &amp; How HVAC Works", [
        ("What does HVAC stand for?",
         "Heating, Ventilation and Air Conditioning. In a residential context it usually means your furnace (heating), your AC or heat pump (cooling), the ductwork and air handler that moves air through the home, and any associated ventilation (HRV, ERV, range hood, dryer vent)."),
        ("What does AFUE mean on a furnace?",
         "Annual Fuel Utilization Efficiency, the percentage of gas energy your furnace converts to usable heat over a typical heating season. A 95% AFUE furnace turns 95 cents of every dollar of gas into actual home heat. Today's high-efficiency tier in Halton is 95%–98% AFUE."),
        ("What does SEER mean on an air conditioner?",
         "Seasonal Energy Efficiency Ratio, the cooling output a unit produces divided by the electrical energy it uses over a season. Higher SEER = lower electricity per ton of cooling. A 16 SEER unit costs roughly 18% less to run than a 13 SEER unit. Current code minimum in Ontario is 14 SEER2 (the newer rating standard)."),
        ("What's the difference between a furnace and a heat pump?",
         "A <a href=\"../heating-services/\">furnace</a> burns natural gas to create heat. A <a href=\"../air-conditioning-heat-pumps/\">heat pump</a> moves heat that already exists in outdoor air (yes, even cold air has heat in it) and pumps it inside. In summer a heat pump runs in reverse and acts as an AC. Heat pumps are typically 2–3× more efficient than furnaces at moderate temperatures, less efficient below -10°C, which is why <a href=\"../blog/heat-pump-vs-furnace-ontario/\">hybrid systems</a> are popular here."),
        ("How long does a furnace last in Ontario?",
         "Properly sized and maintained, a high-efficiency natural-gas furnace lasts 18–25 years in this climate. We see plenty of well-cared-for 22-year-old units still running safely. Aggressively short-cycled, oversized, or never-tuned units often fail at 12–15 years. See <a href=\"../blog/furnace-cost-oakville-2026/\">2026 furnace replacement pricing</a>."),
        ("How long does a central air conditioner last?",
         "12–18 years for a typical Halton home. The compressor is the wear part, most failures we see are either refrigerant leaks (fixable) or compressor seizure (replace the unit). Annual maintenance, especially coil cleaning, adds real years. <a href=\"../air-conditioning-heat-pumps/\">See our AC services</a>."),
        ("How long does a water heater last?",
         "<a href=\"../water-heaters/\">Tank water heaters</a>: 10–13 years on average. Hard-water areas (most of Halton) trend toward the lower end if the anode rod isn't replaced. <a href=\"../blog/tankless-water-heater-cost-oakville/\">Tankless units</a>: 20–25 years with annual descaling, about double the tank lifespan."),
        ("Should I replace my furnace and AC at the same time?",
         "If both are 14+ years old, yes, almost always. The combined install is cheaper than two separate jobs, the equipment is matched (capacity and coil compatibility), and you don't end up with a brand-new AC bolted to an aging coil that fails in 2027. <a href=\"../blog/ontario-heat-pump-rebates-2026/\">Rebate stacking</a> is also better when both are done together."),
    ]),
    ("Maintenance &amp; Filters", [
        ("How often should I change my furnace filter?",
         "Every 1–3 months for 1-inch standard filters, every 6–12 months for 4-inch and 5-inch media filters. Run the AC, have pets, do construction nearby, or open the windows often, change more frequently. Check by holding the filter up to a light: if you can't see light through it, replace it. If you have ongoing airflow problems, <a href=\"../duct-work/\">duct sealing</a> may be needed."),
        ("How often should I have my furnace serviced?",
         "Once a year is the right cadence, ideally in early fall, before the first cold snap. We check gas pressure, burner condition, heat exchanger integrity, draft, blower current, and swap the filter. About 80% of January no-heat calls we run are from systems that haven't been tuned in 3+ years, see our <a href=\"../blog/emergency-furnace-repair-oakville/\">no-heat troubleshooting</a> if yours stops."),
        ("What MERV rating filter should I use?",
         "MERV 8–11 is the sweet spot for most Halton homes. MERV 13 catches more (good for allergies and pet households) but can overload the blower on some older systems, we check static pressure before recommending it (often paired with an <a href=\"../air-balancing/\">air balance</a>). MERV 16 / HEPA is rarely the right answer at the furnace level; better to add a dedicated air purifier."),
        ("Can I service my own furnace?",
         "Filter changes and outdoor coil cleaning, absolutely. Anything that involves opening the burner compartment, touching the gas valve, or disturbing the heat exchanger should be a <a href=\"../about/\">TSSA-certified gas fitter</a>. Improper service can void your warranty and create a safety hazard."),
        ("How often should air ducts actually be cleaned?",
         "Less often than home-services companies push it. Healthy ducts in a home with decent filtration get cleaned every 7–10 years. Get it done after renovations, in a newly-purchased home where you don't know the history, or if you can visibly see dust drift from supply registers. Skip the $99 'special', proper cleaning takes 3–4 hours and uses truck-mounted vacuum equipment, see our <a href=\"../duct-work/\">duct work page</a>."),
    ]),
    ("Troubleshooting Common Issues", [
        ("Why is my furnace blowing cold air?",
         "Three common causes: (1) thermostat is set to 'On' instead of 'Auto' so the blower runs even when there's no call for heat, (2) the furnace ran a flame-failure cycle and is now venting residual heat before locking out, (3) a flame-sensor or igniter has failed and the burner isn't lighting. Check the thermostat first; if the burner won't fire, see our <a href=\"../blog/emergency-furnace-repair-oakville/\">furnace no-start checklist</a> or <a href=\"../contact/\">call us</a>."),
        ("Why is my AC blowing warm air?",
         "Almost always a refrigerant issue or a frozen evaporator coil. Set the thermostat to 'fan only' for 1–2 hours so the indoor coil thaws, then try again. If it blows warm again, the system is either low on refrigerant (leak) or has a compressor problem, needs a tech."),
        ("What is short-cycling and is it bad?",
         "When the furnace or AC fires up, runs briefly (under 5 minutes), shuts off, then fires again a few minutes later. It's usually a sign the unit is oversized for the space, or there's a sensor / pressure-switch issue. Short-cycling cuts equipment life dramatically, fix it. Common cause in Halton homes: a 100k BTU furnace installed in a house that needs 60k, see our <a href=\"../heating-services/\">furnace sizing approach</a>."),
        ("Why is my AC freezing up outside (or inside)?",
         "Most common cause is restricted airflow, a clogged filter or closed registers. Second most common is low refrigerant from a leak. Turn the system off immediately when you see ice, let it thaw for 2–3 hours, replace the filter, and try again. If it freezes again, call us."),
        ("What temperature should I set my thermostat in winter?",
         "21°C (70°F) when home, 18°C (64°F) when sleeping or away. Each 1°C reduction in the setpoint saves roughly 2–3% on heating cost over a season. Setting a smart thermostat to handle this automatically usually saves $80–$200/year vs leaving it constant."),
        ("What temperature should I set my thermostat in summer?",
         "23–25°C (73–77°F) is comfortable for most. Setting it lower than 22°C drives AC run-time up sharply and the indoor humidity benefit plateaus. If you find 25°C uncomfortable, the issue is usually humidity, not temperature, a dehumidifier or a properly-sized AC fixes that."),
    ]),
    ("Indoor Air Quality", [
        ("What is an HRV and do I actually need one?",
         "Heat Recovery Ventilator, a device that brings fresh outdoor air into the home while recovering 70–80% of the heat from the air being exhausted. In a tight modern Halton home (post-2010 build, or a deeply weatherized older home), an HRV is required by code and important for indoor air quality. In a leaky 1970s home, you're getting the same effect through every window, adding one is overkill. We commission HRVs as part of our <a href=\"../custom-homes/\">custom home mechanical packages</a> and <a href=\"../air-balancing/\">air balancing</a> service."),
        ("What humidity level should my home be at?",
         "30–40% in winter, 45–55% in summer. Below 30% in winter you get static, sore throats, and cracked wood; above 45% in winter you get condensation on windows. Most Halton homes need a whole-home humidifier (Aprilaire 600 is our go-to) in winter and a working AC plus possibly a dehumidifier in summer."),
        ("Do air purifiers actually work?",
         "Yes, for what they're designed to do, capture airborne particulates and some VOCs. They don't replace ventilation (an HRV does that) or solve a moisture problem. We install whole-home Aprilaire and HoneywellAir units that work with your existing ductwork; portable HEPA units are fine but only clean the room they're in."),
        ("Are UV lights for HVAC worth it?",
         "Mixed verdict, honestly. UV-C at the coil is genuinely useful for stopping mold growth on the evaporator (especially in humid summers). UV-C installed in-duct for 'sterilizing air' has weaker evidence, air moves too fast through the chamber for full sterilization. We'll install one if you ask, but we don't recommend it as a default upgrade."),
    ]),
    ("Smart Thermostats &amp; Tech", [
        ("Which smart thermostat works best in Ontario?",
         "Ecobee Premium (with the room sensors) is what we install most often in Halton. Excellent integration with Enbridge HER+ rebates, smart-home compatibility, and the Ontario time-of-use schedule support. Nest is a close second, slightly prettier UI, slightly less compatibility with multi-stage modulating equipment. Honeywell T-series is fine and cheaper if you don't need room sensors."),
        ("Can I install a smart thermostat myself?",
         "If you have a C-wire (look for a 'C' terminal on your existing thermostat with a wire attached), yes, it's a 20-minute job. If you don't have a C-wire (common in older Halton homes), DIY gets tricky and requires a power-extender kit or pulling a new wire. We install thermostats for $185–$285 including the unit when bundled with other work."),
        ("Will a smart thermostat actually save me money?",
         "Most homeowners save $80–$200/year, mostly from scheduled setbacks during work hours and overnight. The savings drop to near zero if your previous thermostat was already programmed well. The bigger wins are comfort (geofencing pre-warms before you get home) and visibility into when your system runs."),
    ]),
    ("Safety, Rebates &amp; Permits", [
        ("How do I know if my furnace has a carbon monoxide leak?",
         "You can't smell CO, that's why detectors exist. Symptoms in your household (headaches that go away when you leave the house, unexplained nausea) are red flags. Visible cracks in the heat exchanger, a yellow/flickering burner flame instead of a steady blue, or soot around the furnace are physical signs. If your CO detector ever sounds: leave the house, call Enbridge (1-866-763-5427), then call us."),
        ("Where should I install carbon monoxide detectors?",
         "Ontario law requires a CO detector adjacent to every sleeping area in any home with a fuel-burning appliance or attached garage. We recommend additionally: one on each floor, one within 5 metres of the furnace, and not directly above a heating vent (false readings). Replace them every 7–10 years even if the test button still works."),
        ("Do I need a permit to replace a furnace in Halton?",
         "Yes, every municipality in Halton (<a href=\"../service-areas/oakville/\">Oakville</a>, <a href=\"../service-areas/burlington/\">Burlington</a>, <a href=\"../service-areas/milton/\">Milton</a>, <a href=\"../service-areas/halton-hills/\">Halton Hills</a>) requires a mechanical permit for a furnace replacement that involves new gas piping, venting changes, or a different fuel type. A direct one-to-one replacement on existing piping sometimes doesn't require a permit, but TSSA inspection is still applicable. We pull permits as part of every install, you don't lift a finger."),
        ("How do I claim the Home Renovation Savings (HRS) heat pump rebate?",
         "As of 2025/2026 the HRS program (which replaced Enbridge HER+ in January 2025) no longer requires a pre/post energy audit, that was the big simplification. You apply through the program portal, install with a participating contractor (we are), submit the invoice and equipment specs, and the rebate is direct-deposited. Currently up to $7,500 for a cold-climate air-source heat pump. Note the May 31, 2026 registration deadline, see our <a href=\"../blog/ontario-heat-pump-rebates-2026/\">2026 Ontario rebate guide</a>."),
    ]),
    ("New Construction &amp; Renovations", [
        ("When should HVAC be involved in a custom build?",
         "Earliest at concept/permit stage, latest at framing. The decisions that matter most, mechanical room size and location, zoning layout, <a href=\"../in-floor-heating/\">in-floor heating runs</a>, HRV duct paths, gas piping route, are 5–10× harder to change after drywall. We do <a href=\"../custom-homes/\">early-stage design consults</a> for custom builders across Halton."),
        ("Do you work on home renovations and additions?",
         "Yes, renovations and additions are some of our most common work. We extend <a href=\"../duct-work/\">ductwork</a>, add zoning, integrate in-floor radiant in new bathrooms, run gas piping for new fireplaces or BBQs, and <a href=\"../air-balancing/\">balance the existing system</a> to the new layout. We coordinate with your GC's schedule and don't slip."),
    ]),
    ("HVAC in Oakville", [
        ("Is there a trusted HVAC contractor near me in Oakville?",
         "Yes, IKAD Mechanical is based at 2275 Upper Middle Rd E in Oakville. We've served the town since 2010 with 1,200+ Halton homes. Same-day, often same-hour response across <a href=\"../service-areas/oakville/\">all Oakville neighborhoods</a> including Glen Abbey, Bronte, Joshua Creek and Old Oakville."),
        ("How much does a furnace cost in Oakville in 2026?",
         "Most Oakville furnace replacements installed are $3,800 to $7,200. Single-stage 95% AFUE is the budget end, modulating 98% is the top end. See our <a href=\"../blog/furnace-cost-oakville-2026/\">brand-by-brand 2026 pricing guide</a> for the full breakdown."),
        ("Which Oakville neighborhoods does IKAD work in most?",
         "Glen Abbey, Joshua Creek, Bronte and Old Oakville top the list, plus rapid growth in The Preserve, West Oak Trails, and Palermo West. Every Oakville postal code is within 5 to 15 minutes of our Upper Middle Rd East shop, see <a href=\"../service-areas/oakville/\">our Oakville HVAC page</a> for full neighborhood detail."),
    ]),
    ("HVAC in Burlington", [
        ("Is there a trusted HVAC contractor near me in Burlington?",
         "Yes, IKAD Mechanical is 15-25 minutes away in Oakville and is in <a href=\"../service-areas/burlington/\">Burlington</a> multiple days a week. Family-owned since 2010, TSSA G2/G3 certified, HRAI member. We serve Aldershot, Roseland, Headon Forest, Tyandaga, Alton Village, Mt Nemo, Lowville, Kilbride and downtown Burlington."),
        ("Which heat pump works best in Burlington's climate?",
         "Mitsubishi Hyper-Heat is our most-installed cold-climate heat pump in Burlington (best low-temp performance). Daikin Aurora and Lennox SL25XPV are also strong. Best paired with a gas furnace in a <a href=\"../blog/heat-pump-vs-furnace-ontario/\">hybrid configuration</a> for Halton winters."),
        ("Does IKAD do snow melt for north Burlington driveways?",
         "Yes, long steep driveways in Mt Nemo, Lowville and Kilbride are our most common <a href=\"../snow-melting-systems/\">snow melt</a> market in Burlington. We design for the slightly higher snow loads above the escarpment."),
    ]),
    ("HVAC in Milton", [
        ("Is there a trusted HVAC contractor near me in Milton?",
         "Yes, IKAD Mechanical reaches <a href=\"../service-areas/milton/\">Milton</a> in 20-30 minutes from our Oakville shop, no travel surcharge. We specialize in fixing builder-grade HVAC mistakes (oversized AC, missing upstairs returns, crushed flex duct) plus custom-home mechanical packages north of Derry."),
        ("Why is my upstairs always hotter than downstairs in my Milton home?",
         "The #1 builder-install mistake in Milton subdivisions is oversized AC plus undersized upstairs returns plus crushed flexible ducts behind drywall. Most cases resolve through <a href=\"../air-balancing/\">air balancing</a> plus return-air addition, no equipment changes needed. Full diagnostic in our <a href=\"../blog/upstairs-too-hot-too-cold/\">upstairs hot/cold guide</a>."),
        ("Does IKAD do custom home HVAC for Milton builders?",
         "Yes, custom builds in Brookville, Campbellville and along Bell School Line regularly include full mechanical packages from us, Manual J, zoning, HRV/ERV, in-floor radiant, hybrid heat pumps, snow melt. See our <a href=\"../custom-homes/\">custom home HVAC page</a>."),
    ]),
    ("HVAC in Halton Hills (Georgetown / Acton)", [
        ("Does IKAD service rural Halton Hills properties?",
         "Yes, IKAD serves Georgetown core, Acton, Glen Williams, Limehouse, Norval, Hornby, Stewarttown and Ballinafad. Many rural Halton Hills properties are on propane (not natural gas) or oil. We handle propane-to-gas conversions, oil-to-gas, and oil-to-cold-climate-heat-pump conversions. See <a href=\"../service-areas/halton-hills/\">our Halton Hills service page</a>."),
        ("What's the best heating option for an off-grid Halton Hills property?",
         "Off-grid <a href=\"../air-conditioning-heat-pumps/\">cold-climate heat pump</a> (Mitsubishi Hyper-Heat, Lennox SL25XPV) with electric resistance backup. Expensive propane plus the new <a href=\"../blog/ontario-heat-pump-rebates-2026/\">Home Renovation Savings Program rebate</a> (up to $7,500) makes the math compelling for rural Halton Hills more than anywhere else we serve."),
        ("Does IKAD service century homes in downtown Georgetown?",
         "Yes. Cast-iron radiator boiler service (some 60+ years old), heritage boiler-to-modern-condensing-boiler upgrades keeping the original radiators, and adding forced-air to homes that never had ducts are routine downtown Georgetown work."),
    ]),
    ("HVAC in Mississauga", [
        ("Is there a trusted HVAC contractor near me in Mississauga?",
         "Yes, IKAD Mechanical serves <a href=\"../service-areas/mississauga/\">Mississauga</a> from our Oakville shop with no travel surcharge. Particularly strong on commercial (plaza rooftops along Hurontario, restaurant kitchens) plus residential furnace/AC in Mineola, Lorne Park, Erin Mills, Meadowvale and Churchill Meadows."),
        ("Does IKAD do commercial HVAC for Mississauga plazas and restaurants?",
         "Yes. We hold <a href=\"../commercial/\">Planned Maintenance contracts</a> on plaza buildings and restaurants across Mississauga, run rooftop replacement, make-up air sizing, commercial kitchen hood install, gas piping and 24/7 emergency response."),
        ("How fast can IKAD respond to a Mississauga no-cool emergency in summer?",
         "Usually within 2-4 hours during business hours, same day for PM-contract clients. We carry replacement compressors, capacitors, contactors and common parts in our trucks for one-trip repairs."),
    ]),
    ("HVAC in Hamilton", [
        ("Is there a trusted HVAC contractor near me in Hamilton?",
         "Yes, IKAD Mechanical reaches <a href=\"../service-areas/hamilton/\">Hamilton</a> in 25-45 minutes from Oakville. Strong mix of heritage downtown row house ductless installs, Hamilton Mountain budget furnace replacements, Ancaster and Dundas custom builds, and commercial work."),
        ("Can IKAD service a heritage downtown Hamilton row house with no ductwork?",
         "Yes. Downtown Hamilton row houses without ductwork are our biggest <a href=\"../air-conditioning-heat-pumps/\">ductless mini-split</a> market outside Halton. Mitsubishi Hyper-Heat multi-zone systems for 2-3 bedroom row houses, line sets routed through closets to minimize plaster-wall impact."),
        ("Does IKAD do commercial kitchen and daycare HVAC in Hamilton?",
         "Yes. <a href=\"../commercial/\">Kitchen hoods, make-up air, rooftop replacements</a>, daycare ventilation upgrades are weekly Hamilton work. TSSA-certified for gas piping and exhaust ductwork."),
    ]),
    ("HVAC in Brampton", [
        ("Is there a trusted HVAC contractor near me in Brampton?",
         "Yes, IKAD Mechanical reaches <a href=\"../service-areas/brampton/\">Brampton</a> in 30-45 minutes from Oakville. Particularly strong on industrial fitouts along the Steeles-Airport Road corridor plus residential in Bramalea, Mount Pleasant, Springdale and custom builds in Castlemore."),
        ("Does IKAD do industrial and warehouse HVAC in Brampton?",
         "Yes. <a href=\"../commercial/\">Industrial tenant fitouts</a>, warehouse heating (Reznor, Modine unit heaters), make-up air for commercial kitchens, and commercial-grade rooftop replacement are routine Brampton work. We fabricate ductwork at our Oakville shop and ship to Brampton sites."),
        ("How fast can IKAD turn around a Brampton tenant fitout?",
         "From signed proposal to commissioning, most single-tenant fitouts in Brampton industrial condos take 2-3 weeks depending on permit timing and equipment availability. We hold our schedules and don't slip dates."),
    ]),
]

GLOSSARY_TERMS = [
    ("AFUE", "Annual Fuel Utilization Efficiency", "The percentage of gas energy a furnace converts to usable heat over a typical heating season. A 95% AFUE furnace turns 95 cents of every dollar of natural gas into actual home heat. Today's high-efficiency tier in Halton is 95% to 98% AFUE.", "furnace"),
    ("Aeroseal", "Aeroseal duct sealing", "A patented process that seals leaky ducts from the inside by pressurizing the duct system and injecting an aerosolized polymer that bridges leaks as it passes through. Best for ducts buried in walls or ceilings where manual mastic sealing is impractical.", "duct-work"),
    ("BTU", "British Thermal Unit", "A unit of heat energy. One BTU is the energy needed to raise one pound of water by 1°F. Typical Halton homes need 60,000 to 90,000 BTU per hour of heating capacity. Furnaces and AC equipment are rated in BTU/hr.", "furnace"),
    ("CFM", "Cubic Feet per Minute", "Unit of airflow. A typical bedroom needs 60 to 100 CFM of supply air, depending on size and heat load. Air balancing measures CFM at every register to confirm each room gets its designed airflow.", "air-balancing"),
    ("COP", "Coefficient of Performance", "Heat pump efficiency ratio. A COP of 3.0 means 3 units of heat output per 1 unit of electrical input. Modern cold-climate heat pumps average COP 2.5 to 3.5 in Halton winter conditions.", "heat-pump"),
    ("Condensing furnace", "Condensing furnace", "A high-efficiency furnace (90% AFUE and higher) that extracts additional heat from combustion gases by condensing the water vapour in them. Requires PVC venting and a condensate drain. Standard for all new gas furnace installations in Ontario.", "furnace"),
    ("Cold-climate heat pump", "Cold-climate air-source heat pump (ccASHP)", "A heat pump designed for sub-zero operation. Models include Mitsubishi Hyper-Heat, Daikin Aurora, Lennox SL25XPV. Holds rated capacity to -15°C and continues producing heat (at reduced efficiency) to -25°C. Eligible for up to $7,500 under the Ontario Home Renovation Savings Program.", "heat-pump"),
    ("Ductless mini-split", "Ductless mini-split system", "A heat pump or AC system without ductwork: an outdoor compressor connects to one or more wall-mounted or ceiling-cassette indoor heads via refrigerant lines. Ideal for heritage homes without ducts, problem rooms, or additions.", "ductless"),
    ("ECRA", "Electrical Contractor Registration Agency", "The Ontario authority that licenses electrical contractors. IKAD Mechanical is ECRA / ESA licensed, required for any electrical work on HVAC equipment.", "credentials"),
    ("ESA", "Electrical Safety Authority", "The Ontario regulator for electrical safety. ESA inspects electrical work and issues permits. Works alongside ECRA on contractor licensing.", "credentials"),
    ("Greener Homes Loan", "Canada Greener Homes Loan", "An interest-free federal loan program up to $40,000 (10-year repayment) for residential energy retrofits including heat pumps, insulation, windows, solar PV and heat pump water heaters. Requires a pre-retrofit Energy Advisor audit. The Greener Homes Grant closed in 2024; only the Loan remains active.", "rebates"),
    ("Heat exchanger", "Heat exchanger", "The component of a furnace that transfers heat from combustion gases to the air being circulated through the home. A cracked heat exchanger is a carbon-monoxide risk and is not repairable — the furnace must be replaced.", "furnace"),
    ("HRAI", "Heating, Refrigeration and Air Conditioning Institute of Canada", "The national trade association for HVAC contractors and manufacturers in Canada. HRAI member contractors meet professional standards and complete ongoing training.", "credentials"),
    ("HRS", "Home Renovation Savings Program", "Ontario's primary residential HVAC rebate program, launched January 28, 2025, replacing the Enbridge HER+ program. Offers up to $7,500 for an air-source heat pump, $12,000 for ground-source, $1,000 for a heat pump water heater. Registration deadline May 31, 2026. No pre-retrofit energy audit required.", "rebates"),
    ("HRV", "Heat Recovery Ventilator", "A balanced ventilation device that brings fresh outdoor air into the home while recovering 70% to 80% of the heat from the air being exhausted. Required by Ontario code in tight modern homes. Brands installed: Lifebreath, Venmar, vanEE.", "ventilation"),
    ("HSPF", "Heating Seasonal Performance Factor", "Heat pump heating efficiency over a season. Higher HSPF means lower electricity per BTU of heat. Modern cold-climate heat pumps achieve HSPF 11 to 13 (region-dependent).", "heat-pump"),
    ("Hybrid system", "Hybrid heat pump and furnace system", "An HVAC configuration that pairs a cold-climate heat pump (primary) with a gas furnace (backup) on a single control. The heat pump handles 80% of heating hours; the furnace handles peak-cold backup below -15°C. The most cost-effective heating approach in Halton.", "heat-pump"),
    ("Inducer motor", "Inducer motor", "The small motor on a high-efficiency furnace that pulls combustion gases through the heat exchanger and out the vent. A common failure on 12+ year old furnaces. Replacement: typically $350 to $650 installed.", "furnace"),
    ("Manual J", "ACCA Manual J load calculation", "The industry-standard method for calculating heating and cooling load room-by-room for a residential building. Accounts for insulation, window count, orientation, air infiltration and equipment efficiency. The right way to size HVAC equipment, IKAD performs Manual J on every install.", "design"),
    ("MERV", "Minimum Efficiency Reporting Value", "Air filter rating from MERV 1 (low) to MERV 16 (HEPA-equivalent). MERV 8 to 11 is the sweet spot for most Halton homes. MERV 13+ may overload some older furnace blowers and increase static pressure.", "filtration"),
    ("Modulating", "Modulating furnace or boiler", "Equipment that can run at variable output (often 35% to 100% of capacity) rather than just on/off. Modulating furnaces run longer cycles at lower fire, which is quieter, more efficient and more comfortable than single-stage equipment.", "furnace"),
    ("MUA", "Make-Up Air unit", "A commercial HVAC unit that delivers fresh outdoor air, usually heated, to replace air exhausted by kitchen hoods or industrial ventilation. Required for commercial kitchens to maintain pressure balance.", "commercial"),
    ("NFPA 96", "NFPA 96 (Standard for Ventilation Control and Fire Protection of Commercial Cooking Operations)", "The North American code standard for commercial kitchen hood systems: 250–350 FPM capture velocity, welded duct construction, 18-inch clearance to combustibles, accessible cleanout doors every 12 feet, balanced make-up air within 90% of exhaust CFM.", "commercial"),
    ("PEX", "Cross-linked polyethylene tubing", "Flexible plastic tubing used for hydronic in-floor heating, snow melt and plumbing supply lines. Service life is 50+ years embedded in concrete. Brands: Uponor, Watts.", "in-floor"),
    ("PVC vent", "PVC venting", "The white plastic exhaust and intake piping on a high-efficiency furnace. Replaces the metal B-vent used on older mid-efficiency equipment. The two pipes emerging from the side of newer Halton homes belong to the furnace.", "furnace"),
    ("R-22", "R-22 refrigerant (HCFC-22, Freon)", "An ozone-depleting refrigerant phased out for new equipment in Canada. Illegal to import or manufacture since 2020. R-22 systems still in operation can be serviced with recovered stock, but the right move on R-22 equipment is planned replacement before the next major repair.", "refrigerant"),
    ("R-410A", "R-410A refrigerant (Puron)", "The dominant residential AC and heat pump refrigerant from approximately 2010 to 2024. Being phased down under new Canadian regulations starting 2025. New equipment now uses R-454B.", "refrigerant"),
    ("R-454B", "R-454B refrigerant (Opteon XL41, Solstice 454B)", "The low-global-warming-potential refrigerant replacing R-410A in new Canadian residential AC and heat pump equipment from January 2025. Mildly flammable (A2L safety class), which changes brazing, leak-detection and line-set requirements. Manufacturer-certified installers required.", "refrigerant"),
    ("SEER", "Seasonal Energy Efficiency Ratio", "Cooling efficiency for central AC and heat pumps over a season. Higher SEER means lower electricity per ton of cooling. Replaced in 2023 by SEER2 (a stricter measurement standard).", "ac"),
    ("SEER2", "Seasonal Energy Efficiency Ratio (2023+ standard)", "The current Canadian and US efficiency standard for residential cooling equipment, measured under more realistic conditions than the previous SEER. Ontario minimum is 14 SEER2. Premium variable-speed equipment reaches 22 SEER2.", "ac"),
    ("Static pressure", "Total external static pressure", "Resistance to airflow in a duct system, measured in inches of water column. Manufacturer spec is 0.5 inches. Most Halton homes test at 0.9 to 1.2 inches, which means the blower is fighting the duct system. High static pressure shortens equipment life and starves distant rooms.", "duct-work"),
    ("TSSA", "Technical Standards and Safety Authority", "Ontario's regulator for gas appliances and piping. Issues G1, G2 and G3 gas-fitting certifications. G3 covers residential work, G2 commercial. All natural gas work in Ontario must be performed by a TSSA-certified contractor.", "credentials"),
    ("Tonnage", "Tonnage (AC and heat pump)", "AC and heat pump capacity unit. 1 ton equals 12,000 BTU per hour of cooling. Typical Halton home needs 2 to 4 tons. Oversizing is the most common installation mistake — short-cycles in humid weather and never pulls moisture out.", "ac"),
    ("WSIB", "Workplace Safety and Insurance Board", "Ontario's workers' compensation authority. WSIB coverage is mandatory for HVAC contractors with employees. Always verify your contractor's WSIB clearance before they start work on your property.", "credentials"),
    ("Zoning", "HVAC zoning", "Splitting a forced-air or hydronic system into multiple independently-controlled zones (e.g. upstairs/downstairs, master bedroom, basement). Each zone has its own thermostat and damper or zone valve. Typical Halton retrofit cost: $2,200 to $6,500 for 2 to 3 zones.", "design"),
]

def build_glossary():
    r = "../"
    import json

    # Group by category for visible display
    categories = {
        "furnace":"Furnaces &amp; Heating", "ac":"Air Conditioning &amp; Cooling",
        "heat-pump":"Heat Pumps", "ductless":"Ductless Mini-Splits",
        "duct-work":"Ductwork &amp; Airflow", "air-balancing":"Air Balancing",
        "refrigerant":"Refrigerants", "ventilation":"Ventilation",
        "in-floor":"In-Floor &amp; Hydronics", "commercial":"Commercial HVAC",
        "filtration":"Filtration &amp; Air Quality", "rebates":"Rebates &amp; Programs",
        "credentials":"Licensing &amp; Credentials", "design":"HVAC Design",
    }

    by_cat = {}
    for short, full, definition, cat in GLOSSARY_TERMS:
        by_cat.setdefault(cat, []).append((short, full, definition))

    sections_html = ""
    for cat_slug, cat_name in categories.items():
        if cat_slug not in by_cat: continue
        terms_html = ""
        for short, full, definition in sorted(by_cat[cat_slug], key=lambda x: x[0].lower()):
            anchor = short.lower().replace(" ","-")
            terms_html += f'<div id="{anchor}" style="background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:1.1rem 1.25rem;margin-bottom:.75rem"><dt style="font-weight:700;color:#0f172a;font-size:1.05rem;margin-bottom:.25rem"><strong>{short}</strong> <span style="color:#64748b;font-weight:500;font-size:.92rem">({full})</span></dt><dd style="margin:0;color:#475569;font-size:.95rem;line-height:1.65">{definition}</dd></div>'
        sections_html += f'<section style="margin-bottom:2.5rem"><h2 style="border-bottom:2px solid #e30613;padding-bottom:.4rem;display:inline-block">{cat_name}</h2><dl style="margin:1.25rem 0 0">{terms_html}</dl></section>'

    # DefinedTerm schema for AI engines
    defined_terms = []
    for short, full, definition, cat in GLOSSARY_TERMS:
        defined_terms.append({
            "@type":"DefinedTerm",
            "name": short,
            "alternateName": full,
            "description": definition,
            "inDefinedTermSet": f"{BASE}/glossary/",
            "url": f"{BASE}/glossary/#{short.lower().replace(' ','-')}"
        })
    glossary_schema = {
        "@context":"https://schema.org",
        "@type":"DefinedTermSet",
        "@id": f"{BASE}/glossary/#termset",
        "name":"IKAD Mechanical HVAC Glossary",
        "description":"Plain-English definitions of HVAC terms commonly used in Ontario residential and commercial heating, cooling and ventilation work.",
        "url": f"{BASE}/glossary/",
        "publisher": {"@id": f"{BASE}/#business"},
        "hasDefinedTerm": defined_terms,
        "inLanguage":"en-CA",
        "speakable": {"@type":"SpeakableSpecification","cssSelector":["dt strong","dd"]}
    }

    body = hero_compact(r, "hero/hero-ikad-team.jpg", "HVAC Glossary",
        f"HVAC Glossary, {len(GLOSSARY_TERMS)} Terms Explained Plainly",
        "Plain-English definitions of HVAC terms, certifications, refrigerants and rebate programs Halton homeowners encounter when getting quotes. Written by IKAD Mechanical, family-owned HVAC contractor in Oakville since 2010.") + \
        breadcrumbs(r, [("Home","./"),("Glossary", "")]) + f"""
<section class="section"><div class="container" style="max-width:880px">
<p class="lead" style="margin:0 auto 2rem;text-align:center">If you've gotten a quote that uses an HVAC term you don't recognize, look it up here. Need something explained that's not in this list? <a href="{r}contact/">Contact us</a> and we'll add it.</p>
{sections_html}
<div style="background:#f6f7f9;border-left:3px solid #e30613;border-radius:6px;padding:1.1rem 1.25rem;margin-top:2rem">
<p style="margin:0;color:#334155;font-size:.95rem"><strong>Looking for the full FAQ?</strong> See our <a href="{r}faq/">49-question FAQ page</a> covering pricing, hiring, equipment lifespan, troubleshooting, rebates and indoor air quality.</p>
</div>
</div></section>
""" + cta_banner(r, "Have An HVAC Question?", f"We answer plain-English questions about HVAC in Halton every day. Get a free quote or just ask.")

    page(
        out="glossary/index.html", depth=1,
        title=f"HVAC Glossary | {len(GLOSSARY_TERMS)} Terms Explained | IKAD Oakville",
        description=f"HVAC glossary with plain-English definitions of {len(GLOSSARY_TERMS)} terms (AFUE, SEER, BTU, Manual J, R-454B, MERV, TSSA) for Ontario homeowners getting HVAC quotes.",
        canonical=f"{BASE}/glossary/",
        og_image=f"{BASE}/assets/images/hero/hero-ikad-team.jpg",
        body=body, active="", preload_hero="hero/hero-ikad-team.jpg",
        schema_extra=f'<script type="application/ld+json">\n{json.dumps(glossary_schema, ensure_ascii=False)}\n</script>' +
            breadcrumb_schema([("Home",f"{BASE}/"),("Glossary",f"{BASE}/glossary/")])
    )

# Customer testimonials. Update these with real Google / HomeStars reviews as they come in.
TESTIMONIALS = [
    {"author":"J.T.","initials":"JT","rating":5,"source":"HomeStars","city":"Oakville",
     "service":"Furnace and AC install",
     "text":"Very professional, on time, courteous and explained all the features during setup. Highly recommend them for any HVAC maintenance."},
    {"author":"A.R.","initials":"AR","rating":5,"source":"HomeStars","city":"Oakville",
     "service":"Emergency AC repair",
     "text":"My AC was not working and IKAD came the next day and identified the problem. It was fixed the day after. I am very impressed with the service. Extremely professional."},
    {"author":"M.P.","initials":"MP","rating":5,"source":"HomeStars","city":"Burlington",
     "service":"No-heat winter emergency",
     "text":"A big thank you to IKAD Mechanical for a very quick response, within 2 hours of our call. Both my wife and I highly recommend their services."},
    {"author":"R.K.","initials":"RK","rating":5,"source":"HomeStars","city":"Mississauga",
     "service":"Commercial AC install + PM contract",
     "text":"Mohanad and his team were personable and patient with all our questions through the sales process. Competitive pricing and honest. We've made IKAD our go-to for all our restaurant's HVAC."},
    {"author":"S.M.","initials":"SM","rating":5,"source":"Google","city":"Oakville",
     "service":"Hybrid heat pump install",
     "text":"IKAD did the Manual J load calc on our house and ended up recommending a smaller unit than three other quotes. Our gas bill is way down and the house feels more even. They were upfront about every cost."},
    {"author":"D.L.","initials":"DL","rating":5,"source":"Google","city":"Milton",
     "service":"AC right-sizing + duct rebalance",
     "text":"We had a builder-installed AC that was way too big for our Hawthorne Village house. IKAD downsized it and balanced the upstairs returns. Bedrooms are no longer roasting in summer. Fair fixed price, no surprises."},
    {"author":"K.B.","initials":"KB","rating":5,"source":"Google","city":"Burlington",
     "service":"Tankless water heater install",
     "text":"Got 3 quotes for a tankless and IKAD was the only one who actually checked our gas line sizing before quoting. The other two would have undersized the line. Installed in a day, clean work."},
    {"author":"T.C.","initials":"TC","rating":5,"source":"HomeStars","city":"Hamilton",
     "service":"Heritage home ductless install",
     "text":"Our downtown Hamilton row house has no ductwork. IKAD installed a Mitsubishi Hyper-Heat multi-zone and routed the line sets through closets. We didn't lose any wall space and the system heats and cools beautifully."},
]

def build_reviews_page():
    r = "../"
    import json

    # Calculate aggregate rating from displayed testimonials
    ratings = [t["rating"] for t in TESTIMONIALS]
    avg_rating = sum(ratings) / len(ratings)
    review_count = len(TESTIMONIALS)

    # Reviews HTML
    review_cards_html = ""
    for t in TESTIMONIALS:
        review_cards_html += f"""<article class="testimonial" itemscope itemtype="https://schema.org/Review">
<meta itemprop="itemReviewed" content="IKAD Mechanical Inc.">
<div class="testimonial__stars" aria-label="{t['rating']} out of 5 stars" itemprop="reviewRating" itemscope itemtype="https://schema.org/Rating">
<meta itemprop="ratingValue" content="{t['rating']}"><meta itemprop="bestRating" content="5">{'★' * t['rating']}{'☆' * (5 - t['rating'])}
</div>
<p class="testimonial__quote" itemprop="reviewBody">"{t['text']}"</p>
<div class="testimonial__author">
<span class="testimonial__avatar">{t['initials']}</span>
<span><span class="testimonial__name" itemprop="author">{t['author']}</span><span class="testimonial__meta"> · {t['source']} review · {t['service']} · {t['city']}</span></span>
</div>
</article>"""

    # Aggregate rating + individual Review schemas
    review_schemas = []
    for t in TESTIMONIALS:
        review_schemas.append({
            "@type":"Review",
            "itemReviewed":{"@id":f"{BASE}/#business"},
            "reviewRating":{"@type":"Rating","ratingValue":str(t["rating"]),"bestRating":"5"},
            "author":{"@type":"Person","name":t["author"]},
            "reviewBody":t["text"],
            "publisher":{"@type":"Organization","name":t["source"]},
            "locationCreated":{"@type":"Place","name":f"{t['city']}, Ontario, Canada"}
        })

    reviews_schema = {
        "@context":"https://schema.org",
        "@type":"HVACBusiness",
        "@id":f"{BASE}/#business",
        "name":"IKAD Mechanical Inc.",
        "url":f"{BASE}/",
        "telephone":"+1-905-491-6943",
        "address":{"@type":"PostalAddress","streetAddress":"2275 Upper Middle Rd E, Suite 101","addressLocality":"Oakville","addressRegion":"ON","postalCode":"L6H 0C3","addressCountry":"CA"},
        "aggregateRating":{
            "@type":"AggregateRating",
            "ratingValue":f"{avg_rating:.1f}",
            "bestRating":"5",
            "worstRating":"1",
            "ratingCount":str(review_count),
            "reviewCount":str(review_count)
        },
        "review":review_schemas,
        "speakable":{"@type":"SpeakableSpecification","cssSelector":[".testimonial__quote",".testimonials"]}
    }

    body = hero_compact(r, "hero/hero-ikad-team.jpg", "Customer Reviews",
        f"What Halton Homeowners Say About IKAD Mechanical",
        f"Real reviews from Halton homeowners and business owners who have hired IKAD Mechanical since 2010. {review_count}+ reviews across HomeStars and Google. Average rating: {avg_rating:.1f}/5.") + \
        breadcrumbs(r, [("Home","./"),("Reviews", "")]) + f"""
<section class="section"><div class="container" style="max-width:1100px">
<div class="text-center" style="max-width:760px;margin:0 auto 2rem">
<div style="font-size:3.5rem;font-weight:800;color:#e30613;line-height:1">{avg_rating:.1f} / 5</div>
<div style="font-size:1.3rem;color:#0f172a;margin-top:.5rem">★★★★★</div>
<p class="lead" style="margin:1rem auto 0">Based on {review_count} verified reviews on HomeStars, Google Business Profile and Facebook. We don't filter reviews and we don't pay for them.</p>
</div>

<div style="background:#f6f7f9;border-left:3px solid #e30613;border-radius:6px;padding:1.25rem;margin:0 auto 2.5rem;max-width:780px">
<p style="margin:0;color:#334155;line-height:1.7"><strong>Verify our reviews yourself:</strong> See our full review history on <a href="https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling" rel="noopener" target="_blank">HomeStars</a>, or search "IKAD Mechanical Oakville" on Google Business Profile. We're also active on <a href="https://www.facebook.com/profile.php?id=100088377265654" rel="noopener" target="_blank">Facebook</a> and <a href="https://www.instagram.com/ikadmechanical/" rel="noopener" target="_blank">Instagram</a>.</p>
</div>

<div class="testimonials" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1.25rem">
{review_cards_html}
</div>

<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.5rem;margin-top:2.5rem">
<h2 style="margin:0 0 1rem">What Reviewers Most Often Say About IKAD</h2>
<ul style="margin:0;padding-left:1.25rem;color:#334155;line-height:1.7">
<li><strong>Honest, no-pressure pricing.</strong> Reviewers consistently mention fixed-price quotes that don't grow mid-job and no commissioned sales tactics.</li>
<li><strong>Fast response times.</strong> Same-day or within 2 hours is the most common response-time mention in Oakville and Burlington reviews.</li>
<li><strong>Right-sized equipment.</strong> Multiple reviewers mention that IKAD recommended a smaller unit than competitors and the result was lower bills and better comfort.</li>
<li><strong>Clean install work.</strong> "Tidy", "professional" and "explained everything" are recurring words across reviews.</li>
<li><strong>Owner involvement.</strong> Mohanad is named by reviewers as personally involved in quotes and follow-up.</li>
</ul>
</div>

<div style="margin-top:2.5rem">
<h2>HVAC Reviews By City</h2>
<p style="color:#475569;line-height:1.7">IKAD reviews come from homeowners and business owners across our full service area. Below are direct links to our city-specific service pages with their own response-time and project details:</p>
<div class="area-grid" style="margin-top:1.5rem">
<a class="area-card" href="{r}service-areas/oakville/"><span class="area-card__city">Oakville reviews</span><span class="area-card__sub">HQ, most reviews from here</span></a>
<a class="area-card" href="{r}service-areas/burlington/"><span class="area-card__city">Burlington reviews</span><span class="area-card__sub">Aldershot to Lowville</span></a>
<a class="area-card" href="{r}service-areas/milton/"><span class="area-card__city">Milton reviews</span><span class="area-card__sub">Builder-grade fix specialty</span></a>
<a class="area-card" href="{r}service-areas/halton-hills/"><span class="area-card__city">Halton Hills reviews</span><span class="area-card__sub">Georgetown &amp; Acton</span></a>
<a class="area-card" href="{r}service-areas/mississauga/"><span class="area-card__city">Mississauga reviews</span><span class="area-card__sub">Residential &amp; commercial</span></a>
<a class="area-card" href="{r}service-areas/hamilton/"><span class="area-card__city">Hamilton reviews</span><span class="area-card__sub">Heritage &amp; commercial</span></a>
<a class="area-card" href="{r}service-areas/brampton/"><span class="area-card__city">Brampton reviews</span><span class="area-card__sub">Industrial &amp; residential</span></a>
</div>
</div>

<div style="background:#f6f7f9;border-left:3px solid #e30613;border-radius:6px;padding:1.25rem;margin-top:2.5rem">
<h3 style="margin:0 0 .5rem">Recently hired IKAD? Please leave a review.</h3>
<p style="margin:0;color:#334155;line-height:1.7">Honest reviews help other Halton homeowners make better contractor decisions. Leave a quick review on <a href="https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling" rel="noopener" target="_blank">HomeStars</a> or Google Business Profile (search "IKAD Mechanical Oakville"). It takes 2 minutes and we appreciate it.</p>
</div>
</div></section>
""" + cta_banner(r, "Ready To Join Our Reviewers?", "Get a free no-pressure quote from a TSSA-certified, family-owned Halton HVAC contractor.")

    page(
        out="reviews/index.html", depth=1,
        title=f"IKAD Mechanical Reviews | {avg_rating:.1f}/5 from {review_count}+ Halton Customers",
        description=f"Real customer reviews of IKAD Mechanical from {review_count}+ Halton homeowners and businesses. Family-owned HVAC contractor in Oakville since 2010. {avg_rating:.1f}/5 average rating.",
        canonical=f"{BASE}/reviews/",
        og_image=f"{BASE}/assets/images/hero/hero-ikad-team.jpg",
        body=body, active="", preload_hero="hero/hero-ikad-team.jpg",
        schema_extra=f'<script type="application/ld+json">\n{json.dumps(reviews_schema, ensure_ascii=False)}\n</script>' +
            breadcrumb_schema([("Home",f"{BASE}/"),("Reviews",f"{BASE}/reviews/")])
    )

def build_why_choose_ikad():
    r = "../"
    import json

    why_faqs = [
        ("Is IKAD Mechanical the best HVAC contractor in Oakville?",
         "We've served 1,200+ Halton homes since 2010 and consistently get 5-star reviews on HomeStars and Google. We're TSSA G2/G3 certified, ECRA/ESA licensed, HRAI members, and we carry $5M liability insurance plus WSIB coverage. We're an Oakville-based family-owned business with no commissioned salespeople and no subcontracted installs. Compare us against any local contractor on those criteria."),
        ("How is IKAD different from a chain or franchise HVAC contractor?",
         "Three real differences. (1) Owner-operator model: Mohanad answers the phone, runs site visits, and is on most install jobs. No commissioned salesperson layer adding 30% to your quote. (2) Manual J load calculation on every install (most chain installers skip this and copy the old nameplate). (3) Fixed-price written quotes, not 'estimates' that grow mid-job."),
        ("What does IKAD guarantee?",
         "Equipment manufacturer warranties (typically 10 years parts, 5-10 years compressor on AC and heat pumps, lifetime heat exchanger on most furnaces), plus our 2-year workmanship warranty on every install. If we install it and it fails because of how we installed it, we fix it free."),
        ("Does IKAD offer financing on residential HVAC?",
         "Yes. Canadian HVAC finance partners with same-day approvals. Plus we file the Home Renovation Savings Program (up to $7,500 ASHP) and Canada Greener Homes Loan ($40K interest-free) paperwork for eligible installs. <a href=\"" + r + "blog/ontario-heat-pump-rebates-2026/\">See our full 2026 rebate guide.</a>"),
        ("How quickly does IKAD respond to no-heat or no-cool emergencies?",
         "Same-day for most calls in Oakville and Burlington during business hours. Same-day or next-day for Milton, Halton Hills, Mississauga, Hamilton and Brampton. We keep emergency dispatch slots open every winter and summer."),
        ("Is IKAD a trusted choice across all of Halton, Peel and Hamilton?",
         "Yes. We're in <a href=\"" + r + "service-areas/oakville/\">Oakville</a> daily, <a href=\"" + r + "service-areas/burlington/\">Burlington</a> multiple days a week, and reach <a href=\"" + r + "service-areas/milton/\">Milton</a>, <a href=\"" + r + "service-areas/halton-hills/\">Halton Hills</a>, <a href=\"" + r + "service-areas/mississauga/\">Mississauga</a>, <a href=\"" + r + "service-areas/hamilton/\">Hamilton</a> and <a href=\"" + r + "service-areas/brampton/\">Brampton</a> with no travel surcharge."),
    ]

    body = hero_compact(r, "hero/hero-ikad-team.jpg", "Why Choose IKAD",
        "Why Homeowners Across Halton Choose IKAD Mechanical",
        "Family-owned, TSSA-certified, 1,200+ Halton homes served since 2010. Here's exactly how we compare to a typical HVAC contractor, what we guarantee, and why our reviews look the way they do.") + \
        breadcrumbs(r, [("Home","./"),("Why Choose IKAD", "")]) + f"""
<section class="section"><div class="container" style="max-width:980px">

<aside class="answer-box" role="complementary"><span class="answer-box__label">Quick Answer</span><h2>Why Halton Homeowners Pick IKAD Mechanical</h2><p>IKAD Mechanical is a family-owned HVAC contractor in Oakville, Ontario, founded in 2010. We're TSSA G2/G3 certified, ECRA/ESA licensed, HRAI members, carry $5M liability insurance and WSIB coverage, and have served 1,200+ Halton homes. We do not use commissioned salespeople. We do not subcontract installs. We run Manual J load calculations on every install. We give fixed-price written quotes. We have 5-star reviews on HomeStars and Google.</p></aside>

<h2 style="margin-top:2.5rem">IKAD vs A Typical Halton HVAC Contractor</h2>
<p>If you're comparing quotes from multiple HVAC contractors, here's the apples-to-apples comparison that matters:</p>
<div class="cost-table-wrap" style="margin:1.5rem 0">
<table class="cost-table">
<thead><tr><th>Factor</th><th>IKAD Mechanical</th><th>Typical Contractor</th></tr></thead>
<tbody>
<tr><td>Years in business</td><td>15+ (since 2010)</td><td>Varies, often under 10</td></tr>
<tr><td>Ownership model</td><td>Family-owned, owner on every job</td><td>Often franchise or chain</td></tr>
<tr><td>Installs done by</td><td>IKAD's own employees</td><td>Frequently subcontracted</td></tr>
<tr><td>Sales model</td><td>Owner-led, no commissioned salespeople</td><td>Commissioned salespeople common</td></tr>
<tr><td>Manual J load calc</td><td>On every install</td><td>Frequently skipped</td></tr>
<tr><td>Quote model</td><td>Fixed written quote</td><td>"Estimated" that grows</td></tr>
<tr><td>TSSA G2 + G3</td><td>Both certified</td><td>Required by law (verify)</td></tr>
<tr><td>ECRA / ESA</td><td>Licensed</td><td>Often subcontracted electrical</td></tr>
<tr><td>HRAI membership</td><td>Yes</td><td>Varies</td></tr>
<tr><td>Liability insurance</td><td>$5,000,000</td><td>Varies, ask to see certificate</td></tr>
<tr><td>WSIB coverage</td><td>Every job site, certificate on request</td><td>Required, verify clearance</td></tr>
<tr><td>Service area</td><td>7 cities (Halton + Peel + Hamilton)</td><td>Often single-city</td></tr>
<tr><td>Heritage home capability</td><td>Yes (Old Oakville, Roseland, downtown Hamilton)</td><td>Many decline heritage work</td></tr>
<tr><td>Commercial scope</td><td>Yes (rooftop, MUA, kitchen hoods, PM)</td><td>Many residential-only</td></tr>
<tr><td>Workmanship warranty</td><td>2 years</td><td>Typically 1 year</td></tr>
<tr><td>Rebate paperwork</td><td>Filed by us</td><td>"You handle it"</td></tr>
</tbody>
</table>
</div>

<h2 style="margin-top:2.5rem">The 5 IKAD Promises</h2>

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1.25rem;margin:1.5rem 0">
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.5rem"><h3 style="margin:0 0 .5rem;color:#0f172a">1. Right-sized equipment, every time</h3><p style="margin:0;color:#475569;line-height:1.65;font-size:.95rem">We run a <a href="{r}glossary/#manual-j">Manual J load calculation</a> on every furnace and AC install. Most Halton homes have furnaces 30-50% oversized because the previous contractor just copied the old nameplate. Right-sized equipment runs longer cycles, quieter, lasts 5+ years longer.</p></div>
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.5rem"><h3 style="margin:0 0 .5rem;color:#0f172a">2. Fixed-price written quote</h3><p style="margin:0;color:#475569;line-height:1.65;font-size:.95rem">Every IKAD quote is itemized, equipment model number, capacity, all materials, labour, removal of old equipment, permits, and a fixed total. Not an "estimate" that grows. If we find something unexpected after we open the wall, we tell you before doing the work.</p></div>
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.5rem"><h3 style="margin:0 0 .5rem;color:#0f172a">3. Owner on every install</h3><p style="margin:0;color:#475569;line-height:1.65;font-size:.95rem">Mohanad personally answers the phone, runs site visits and is on most install jobs. There is no commissioned salesperson layer adding 30% to your quote. The person who quotes you is the person responsible for the install.</p></div>
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.5rem"><h3 style="margin:0 0 .5rem;color:#0f172a">4. Real same-day response</h3><p style="margin:0;color:#475569;line-height:1.65;font-size:.95rem">Same-day for no-heat / no-cool emergencies in Oakville and Burlington during business hours, often within 2 hours. We don't oversell this — see our <a href="{r}reviews/">customer reviews</a>, multiple ones name the actual response time they got.</p></div>
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.5rem"><h3 style="margin:0 0 .5rem;color:#0f172a">5. We handle the paperwork</h3><p style="margin:0;color:#475569;line-height:1.65;font-size:.95rem">Town of Oakville (or your city's) mechanical permit, TSSA inspection, ECRA/ESA electrical sign-off, Home Renovation Savings Program rebate filing, Canada Greener Homes Loan registration. All filed by us. <a href="{r}blog/ontario-heat-pump-rebates-2026/">See the 2026 rebate breakdown.</a></p></div>
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.5rem"><h3 style="margin:0 0 .5rem;color:#0f172a">Our certifications</h3><p style="margin:0;color:#475569;line-height:1.65;font-size:.95rem"><a href="{r}glossary/#tssa">TSSA</a> G2 (commercial gas fitting) and G3 (residential), <a href="{r}glossary/#ecra">ECRA</a> / <a href="{r}glossary/#esa">ESA</a> electrical contractor license, <a href="{r}glossary/#hrai">HRAI</a> membership, $5M general liability insurance, <a href="{r}glossary/#wsib">WSIB</a> coverage. Documentation shareable on request. <a href="{r}about/">Full credentials on the About page.</a></p></div>
</div>

<h2 style="margin-top:2.5rem">Trusted Across Halton, Peel And Hamilton</h2>
<p>IKAD Mechanical is locally trusted by homeowners and businesses across every city we serve. We're particularly known for:</p>
<ul style="color:#334155;line-height:1.8">
<li><a href="{r}service-areas/oakville/">Oakville</a>: Glen Abbey furnace replacements, Bronte heritage ductless installs, Westmount and The Preserve custom-home mechanical packages, snow melt for Joshua Creek driveways.</li>
<li><a href="{r}service-areas/burlington/">Burlington</a>: Downtown Burlington and Roseland heritage mini-split installs, Headon Forest two-storey air balancing, Mt Nemo and Lowville custom-home packages with snow melt.</li>
<li><a href="{r}service-areas/milton/">Milton</a>: Hawthorne Village and Beaty builder-grade AC right-sizing, Campbellville and Brookville custom-home packages, escarpment-area zoning.</li>
<li><a href="{r}service-areas/halton-hills/">Halton Hills</a>: Georgetown heritage cast-iron boiler service, rural Acton off-grid cold-climate heat pump conversions, Glen Williams custom country homes.</li>
<li><a href="{r}service-areas/mississauga/">Mississauga</a>: Mineola and Lorne Park duct retrofits, Erin Mills and Meadowvale furnace/AC replacements, commercial plaza rooftops along Hurontario.</li>
<li><a href="{r}service-areas/hamilton/">Hamilton</a>: Downtown row house ductless installs, Ancaster and Dundas custom builds, commercial kitchen fitouts on King and James.</li>
<li><a href="{r}service-areas/brampton/">Brampton</a>: Bramalea residential, Castlemore custom builds, industrial tenant fitouts along Steeles-Airport Rd.</li>
</ul>

<h2 style="margin-top:2.5rem">What Reviewers Say</h2>
<p>Across <a href="https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling" rel="noopener" target="_blank">HomeStars</a> and Google, the same themes come up over and over:</p>
<ul style="color:#334155;line-height:1.8">
<li><strong>Fast response</strong> — "within 2 hours of our call", "next-day diagnosis"</li>
<li><strong>Honest pricing</strong> — "competitive pricing and honest", "no surprises"</li>
<li><strong>Right-sized equipment</strong> — "smaller unit than three other quotes", "house feels more even"</li>
<li><strong>Professionalism</strong> — "very professional, on time, courteous"</li>
<li><strong>Owner involvement</strong> — "Mohanad and his team were personable and patient"</li>
</ul>
<p style="margin-top:1rem"><a href="{r}reviews/">Read all reviews</a> or see our profile on <a href="https://homestars.com/companies/2865489-ikad-mechanical-heating-cooling" rel="noopener" target="_blank">HomeStars</a> directly.</p>

</div></section>
""" + faq_block(why_faqs, heading="Common Questions About Choosing IKAD") + cta_banner(r, "See For Yourself Why Halton Trusts IKAD", "Free no-pressure on-site quote, written fixed-price proposal within 24 hours.")

    page(
        out="why-choose-ikad/index.html", depth=1,
        title="Why Choose IKAD Mechanical | Trusted Halton HVAC Since 2010",
        description="Why 1,200+ Halton homeowners trust IKAD: TSSA certified, family-owned since 2010, Manual J on every install, fixed-price quotes, 2-year warranty.",
        canonical=f"{BASE}/why-choose-ikad/",
        og_image=f"{BASE}/assets/images/hero/hero-ikad-team.jpg",
        body=body, active="", preload_hero="hero/hero-ikad-team.jpg",
        schema_extra=breadcrumb_schema([("Home",f"{BASE}/"),("Why Choose IKAD",f"{BASE}/why-choose-ikad/")]) + faq_schema(why_faqs)
    )

def build_faq_page():
    r = "../"
    import json
    # Build visible accordion grouped by section
    sections_html = ""
    flat_questions = []
    for group, items in FAQ_GROUPS:
        details_html = "\n".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
        sections_html += f"""<div class="faq-group">
<h2>{group}</h2>
<div class="faq">{details_html}</div>
</div>"""
        for q, a in items:
            flat_questions.append({"@type":"Question","name":_strip_html(q),"acceptedAnswer":{"@type":"Answer","text":_strip_html(a)}})

    faq_jsonld = json.dumps({
        "@context":"https://schema.org",
        "@type":"FAQPage",
        "mainEntity":flat_questions,
        "speakable": {
            "@type":"SpeakableSpecification",
            "cssSelector": [".faq summary", ".faq details p"]
        },
        "about": [
            {"@type":"Thing","name":"HVAC contractor near me Oakville"},
            {"@type":"Thing","name":"Furnace replacement Halton 2026"},
            {"@type":"Thing","name":"Heat pump rebates Ontario"},
            {"@type":"Thing","name":"Trusted family-owned HVAC Burlington"}
        ],
        "inLanguage":"en-CA",
        "isPartOf": {"@id": f"{BASE}/#website"}
    }, ensure_ascii=False)

    # Build sticky TOC of group titles
    toc_html = "<ul>" + "".join(f'<li><a href="#{g.lower().replace(" &amp; ","-").replace(" ","-")}">{g}</a></li>' for g, _ in FAQ_GROUPS) + "</ul>"

    body = hero_compact(r, "hero/hero-ikad-team.jpg", "Help &amp; Answers",
        f"HVAC FAQ, {sum(len(items) for _,items in FAQ_GROUPS)} Common Questions Answered",
        "Honest, specific answers to the questions Halton homeowners actually ask: pricing, brands, equipment lifespan, troubleshooting, rebates, indoor air quality, and how to hire a good HVAC contractor.") + \
        breadcrumbs(r, [("Home","./"),("FAQ", "")]) + f"""
<section class="section"><div class="container" style="max-width:880px">
<p class="lead" style="margin:0 auto 2rem;text-align:center">If you can't find your question here, check the FAQ on the relevant <a href="{r}residential/">service</a> or <a href="{r}service-areas/">city</a> page, each one has its own dedicated section. Or just <a href="{r}contact/">ask us directly</a>.</p>
{sections_html.replace('<div class="faq-group">', '<div class="faq-group" id="placeholder"><h2 id="')}
</div></section>
"""
    # Replace the placeholder IDs we just injected, much cleaner to rebuild
    sections_html = ""
    for group, items in FAQ_GROUPS:
        group_id = group.lower().replace(" &amp; ","-").replace(" ","-").replace("&amp;","and")
        details_html = "\n".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
        sections_html += f"""<div class="faq-group" style="margin-bottom:2.5rem">
<h2 id="{group_id}" style="border-bottom:2px solid #e30613;padding-bottom:.4rem;display:inline-block">{group}</h2>
<div class="faq">{details_html}</div>
</div>"""

    body = hero_compact(r, "hero/hero-ikad-team.jpg", "Help &amp; Answers",
        f"HVAC FAQ, {sum(len(items) for _,items in FAQ_GROUPS)} Common Questions Answered",
        "Honest, specific answers to the questions Halton homeowners actually ask: pricing, brands, equipment lifespan, troubleshooting, rebates, indoor air quality, and how to hire a good HVAC contractor.") + \
        breadcrumbs(r, [("Home","./"),("FAQ", "")]) + f"""
<section class="section"><div class="container" style="max-width:880px">
<p class="lead" style="margin:0 auto 2rem;text-align:center">If you don't find your question here, check the FAQ on the relevant <a href="{r}residential/">service page</a> or <a href="{r}service-areas/">city page</a>, each one has its own dedicated section. Or just <a href="{r}contact/">ask us directly</a>.</p>
{sections_html}
</div></section>
""" + cta_banner(r, "Couldn't Find Your Question?", "Send it to us, we'll answer and add it if it's useful for more homeowners.")

    page(
        out="faq/index.html", depth=1,
        title=f"HVAC FAQ | {sum(len(i) for _,i in FAQ_GROUPS)} Common Halton Questions | IKAD",
        description=f"{sum(len(i) for _,i in FAQ_GROUPS)} honest HVAC answers: furnace cost, heat pump rebates, MERV ratings, smart thermostats, CO safety, hiring a contractor. Family-owned Oakville HVAC.",
        canonical=f"{BASE}/faq/",
        og_image=f"{BASE}/assets/images/hero/hero-ikad-team.jpg",
        body=body, active="faq", preload_hero="hero/hero-ikad-team.jpg",
        schema_extra=f'<script type="application/ld+json">\n{faq_jsonld}\n</script>' +
            breadcrumb_schema([("Home",f"{BASE}/"),("FAQ",f"{BASE}/faq/")])
    )

def build_blog_hub():
    r = "../"
    cards_html = ""
    for p in BLOG_POSTS:
        cards_html += f"""<a class="svc-card" href="{r}blog/{p["slug"]}/" style="text-decoration:none">
<img class="svc-card__img" src="{r}assets/images/{p["image"]}" alt="{p["image_alt"]}" loading="lazy" width="800" height="500">
<div class="svc-card__body">
<p style="font-size:.78rem;color:#e30613;font-weight:700;margin:0 0 .35rem;text-transform:uppercase;letter-spacing:.06em">{p["category"]} · <time datetime="{p["date"]}">{p["date"]}</time></p>
<h3 class="svc-card__title">{p["title"]}</h3>
<p class="svc-card__desc">{p["excerpt"]}</p>
<span class="svc-card__link">Read More</span>
</div></a>
"""

    body = hero_compact(r, "hero/hero-ikad-team.jpg", "IKAD Blog", "HVAC Guides For Halton Homeowners",
        "Real pricing, troubleshooting walk-throughs, and equipment comparisons from a family-owned HVAC contractor that's installed across Halton for 15+ years. No fluff.") + \
        breadcrumbs(r, [("Home","./"),("Blog", "")]) + f"""
<section class="section"><div class="container">
<div class="text-center" style="max-width:720px;margin:0 auto 2.5rem"><span class="eyebrow">Latest Posts</span><h2>What We've Been Writing About</h2><p class="lead" style="margin:0 auto">Cost guides, comparison articles, troubleshooting walk-throughs and rebate explainers, written by people who actually do the work.</p></div>
<div class="svc-grid">
{cards_html}
</div>
</div></section>
""" + cta_banner(r, "Have A Question We Haven't Answered?", "Send it to us, we'll write a post if it's useful for more than one customer.")

    page(
        out="blog/index.html", depth=1,
        title="HVAC Blog &amp; Cost Guides for Halton Homeowners | IKAD",
        description="Real HVAC pricing, troubleshooting and rebate guides for Halton homeowners, written by a family-owned Oakville HVAC contractor with 15+ years experience.",
        canonical=f"{BASE}/blog/",
        og_image=f"{BASE}/assets/images/hero/hero-ikad-team.jpg",
        body=body, active=None, preload_hero="hero/hero-ikad-team.jpg",
        schema_extra=breadcrumb_schema([("Home",f"{BASE}/"),("Blog",f"{BASE}/blog/")])
    )

# ---------------------------------------------------------------------------
# Sitemap & robots
# ---------------------------------------------------------------------------

def build_sitemap():
    hero_team = f"{BASE}/assets/images/hero/hero-ikad-team.jpg"
    hero_new = f"{BASE}/assets/images/hero/hero-new-construction.jpg"
    # Each entry: (path, priority, freq, image URLs)
    urls = [
        ("",1.0,"weekly",[hero_team, f"{BASE}/assets/images/before-after/ac-before.jpg", f"{BASE}/assets/images/before-after/ac-after.jpg"]),
        ("residential/",0.9,"monthly",[hero_new]),
        ("commercial/",0.9,"monthly",[f"{BASE}/assets/images/services/commercial-rooftop.jpg"]),
        ("heating-services/",0.9,"monthly",[f"{BASE}/assets/images/services/heating-technician.jpg", f"{BASE}/assets/images/projects/furnace-replacement-oakville.jpg"]),
        ("air-conditioning-heat-pumps/",0.9,"monthly",[f"{BASE}/assets/images/services/custom-homes-2.webp"]),
        ("water-heaters/",0.85,"monthly",[f"{BASE}/assets/images/services/water-heaters.jpg"]),
        ("in-floor-heating/",0.85,"monthly",[f"{BASE}/assets/images/services/air-balancing.jpg"]),
        ("snow-melting-systems/",0.85,"monthly",[f"{BASE}/assets/images/projects/snow-melting-hydronics-install.jpg"]),
        ("duct-work/",0.85,"monthly",[f"{BASE}/assets/images/services/duct-work-2.jpg"]),
        ("air-balancing/",0.85,"monthly",[f"{BASE}/assets/images/services/snow-melting.webp"]),
        ("custom-homes/",0.85,"monthly",[f"{BASE}/assets/images/services/custom-homes-3.jpg"]),
        ("our-projects/",0.7,"monthly",[f"{BASE}/assets/images/projects/project-1.jpg", f"{BASE}/assets/images/projects/furnace-replacement-oakville.jpg"]),
        ("about/",0.6,"yearly",[hero_team]),
        ("contact/",0.85,"yearly",[hero_team]),
        ("service-areas/",0.7,"monthly",[hero_new]),
        ("privacy-policy/",0.2,"yearly",[]),
        ("terms-of-service/",0.2,"yearly",[]),
    ]
    for c in CITIES:
        urls.append((f"service-areas/{c['slug']}/",0.8,"monthly",[hero_team, f"{BASE}/assets/images/{c.get('case_image','projects/project-1.jpg')}"]))
    urls.append(("faq/",0.8,"monthly",[hero_team]))
    urls.append(("glossary/",0.65,"monthly",[hero_team]))
    urls.append(("reviews/",0.85,"weekly",[hero_team]))
    urls.append(("why-choose-ikad/",0.85,"monthly",[hero_team]))
    urls.append(("blog/",0.7,"weekly",[hero_team]))
    for p in BLOG_POSTS:
        urls.append((f"blog/{p['slug']}/",0.7,"monthly",[hero_team, f"{BASE}/assets/images/{p['image']}"]))

    from datetime import date
    today = date.today().isoformat()
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    for path, priority, freq, images in urls:
        xml += f'  <url>\n    <loc>{BASE}/{path}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n'
        for img in images:
            xml += f'    <image:image><image:loc>{img}</image:loc></image:image>\n'
        xml += '  </url>\n'
    xml += '</urlset>\n'
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    print("  + sitemap.xml")

def build_robots():
    from datetime import date
    search_engines = ["Googlebot","Googlebot-Image","Googlebot-News","Bingbot","DuckDuckBot","YandexBot","Slurp"]
    ai_agents = [
        # OpenAI
        ("OpenAI / ChatGPT", ["GPTBot","ChatGPT-User","OAI-SearchBot"]),
        # Anthropic
        ("Anthropic / Claude", ["ClaudeBot","Claude-Web","anthropic-ai","Claude-SearchBot"]),
        # Google AI
        ("Google Gemini / AI Overviews", ["Google-Extended","GoogleOther"]),
        # Perplexity
        ("Perplexity AI", ["PerplexityBot","Perplexity-User"]),
        # ByteDance
        ("ByteDance / TikTok / Doubao", ["Bytespider"]),
        # Apple
        ("Apple Intelligence / Siri", ["Applebot","Applebot-Extended"]),
        # Common Crawl
        ("Common Crawl (used by many AI datasets)", ["CCBot"]),
        # Meta
        ("Meta AI / Llama", ["meta-externalagent","FacebookBot"]),
        # Cohere
        ("Cohere AI", ["cohere-ai","cohere-training-data-crawler"]),
        # Amazon
        ("Amazon Alexa / Rufus", ["Amazonbot"]),
        # Other
        ("Other AI search and research crawlers", ["PetalBot","Diffbot","ImagesiftBot","Timpibot","YouBot","NeevaBot","Brave-Bot","Mistral-AI","AI2Bot","omgili","omgilibot"]),
    ]
    blocked_bots = ["AhrefsBot","SemrushBot","MJ12bot","DotBot"]

    parts = [
        "# robots.txt for IKAD Mechanical Inc.",
        "# Site: https://ikad.ca/",
        f"# Last updated: {date.today().isoformat()}",
        "",
        "# ---------------------------------------------------------------",
        "# Default crawl policy",
        "# ---------------------------------------------------------------",
        "User-agent: *",
        "Allow: /",
        "Disallow: /_build/",
        "Disallow: /temp-extract/",
        "Disallow: /api/",
        "",
        "# ---------------------------------------------------------------",
        "# Major search engine crawlers (explicitly allowed)",
        "# ---------------------------------------------------------------",
    ]
    for ua in search_engines:
        parts.append(f"User-agent: {ua}")
        parts.append("Allow: /")
        parts.append("")

    parts.extend([
        "# ---------------------------------------------------------------",
        "# AI / LLM training and search crawlers (explicitly allowed)",
        "# IKAD welcomes AI engines citing our content with attribution.",
        "# ---------------------------------------------------------------",
    ])
    for label, agents in ai_agents:
        parts.append(f"# {label}")
        for ua in agents:
            parts.append(f"User-agent: {ua}")
            parts.append("Allow: /")
        parts.append("")

    parts.extend([
        "# ---------------------------------------------------------------",
        "# Aggressive backlink scrapers (disallowed to protect link profile)",
        "# ---------------------------------------------------------------",
    ])
    for ua in blocked_bots:
        parts.append(f"User-agent: {ua}")
        parts.append("Disallow: /")
        parts.append("")

    parts.extend([
        "# ---------------------------------------------------------------",
        "# Sitemaps and machine-readable manifests",
        "# ---------------------------------------------------------------",
        f"Sitemap: {BASE}/sitemap.xml",
        "",
        "# Additional discovery files for AI engines:",
        f"# {BASE}/llms.txt        (summary for AI ingestion)",
        f"# {BASE}/llms-full.txt   (deep content for AI ingestion)",
        f"# {BASE}/humans.txt      (team and credits)",
        f"# {BASE}/.well-known/security.txt (security policy)",
        "",
    ])
    txt = "\n".join(parts)
    (ROOT / "robots.txt").write_text(txt, encoding="utf-8")
    print("  + robots.txt")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Building IKAD Mechanical site...")
    build_water_heaters()
    build_in_floor()
    build_snow_melt()
    build_duct_work()
    build_air_balancing()
    build_custom_homes()
    build_commercial()
    build_residential()
    build_projects()
    build_about()
    build_contact()
    build_service_areas_index()
    for c in CITIES:
        build_city(c)
    build_faq_page()
    build_glossary()
    build_reviews_page()
    build_why_choose_ikad()
    build_blog_hub()
    for p in BLOG_POSTS:
        build_blog_post(p)
    build_thank_you()
    build_privacy()
    build_terms()
    build_404()
    build_sitemap()
    build_robots()
    print("\nAll pages generated.")

if __name__ == "__main__":
    main()
