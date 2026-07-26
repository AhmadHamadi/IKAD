# IKAD Mechanical, ikad.ca

Static HTML rebuild of [ikad.ca](https://ikad.ca/) (HVAC contractor, Oakville ON).

## Folder structure

```
IKAD/
├── index.html                  → /
├── residential/                → /residential/
├── commercial/                 → /commercial/
├── heating-services/           → /heating-services/
├── air-conditioning-heat-pumps/
├── water-heaters/
├── in-floor-heating/
├── snow-melting-systems/
├── duct-work/
├── air-balancing/
├── custom-homes/
├── our-projects/
├── about/
├── contact/
├── service-areas/              → /service-areas/
│   ├── oakville/
│   ├── burlington/
│   ├── milton/
│   ├── halton-hills/
│   ├── mississauga/
│   ├── hamilton/
│   └── brampton/
├── thank-you/                  (noindex)
├── privacy-policy/
├── terms-of-service/
├── 404.html
├── sitemap.xml
├── robots.txt
└── assets/
    ├── css/main.css
    ├── js/main.js
    └── images/
        ├── hero/
        ├── services/
        ├── projects/
        ├── before-after/
        └── logo/

_build/generate_pages.py        ← page generator (single source of truth)
temp-extract/                   ← raw extracted footage + downloaded images (safe to delete, 4.9GB)
```

URLs match the originally indexed paths on ikad.ca, so Google Search Console history is preserved when this replaces the old site.

## Local preview

```bash
python -m http.server 8765
# then open http://localhost:8765/
```

## Rebuilding pages

All service and city pages are generated from `_build/generate_pages.py`. Edit the content there (not the individual `index.html` files) and rerun:

```bash
python _build/generate_pages.py
```

`index.html` (homepage), `heating-services/index.html` and `air-conditioning-heat-pumps/index.html` are hand-written, edit them directly.

## SEO essentials in place

- Canonical URL on every page (`<link rel="canonical">`)
- Unique `<title>` and `<meta name="description">` per page
- Open Graph + Twitter Card tags
- `application/ld+json` schema:
  - `HVACBusiness` LocalBusiness schema with NAP, geo, hours, areaServed, sameAs (homepage)
  - `Service` schema per service page
  - `BreadcrumbList` schema per page
  - `FAQPage` schema on homepage
  - `ContactPage` schema on contact page
  - Per-city `HVACBusiness` snippet on each service-area page
- `sitemap.xml` referenced from `robots.txt`
- `robots.txt` disallows `/_build/`, `/temp-extract/`, `/thank-you/`
- Geo meta tags (`geo.region`, `geo.placename`, `ICBM`)
- Semantic HTML (header, nav, main sections, footer, breadcrumbs)
- Mobile-first responsive CSS
- Sticky mobile call button (always-visible CTA on phones)
- Preloaded hero image with `fetchpriority="high"`
- All images have descriptive `alt` text
- `loading="lazy"` on below-the-fold images

## Local SEO details (Google Maps / local pack)

- Seven city landing pages (Oakville, Burlington, Milton, Halton Hills, Mississauga, Hamilton, Brampton) each with:
  - Local-intent H1 + content
  - Neighbourhoods served list
  - City-specific schema
  - Local NAP and breadcrumbs
- Consistent NAP across header, footer, contact page, schema, and all service pages
- Google Maps embed on `/contact/`

## Quote forms

Every quote form on the site (`data-form="quote"`) posts JSON to `POST /api/quote`
(`api/quote.js`), a Vercel serverless function that emails the lead over SMTP.
Configure it with the environment variables listed in `.env.example` — locally in
`.env`, in production under **Vercel → Project Settings → Environment Variables**.

If the fetch fails outright, `assets/js/main.js` falls back to a `mailto:` link so a
lead is never lost.

## Spam filtering

SEO / web-design cold-outreach bots are the main source of junk on trade sites.
Three layers handle them, none of which add friction for a real customer (no CAPTCHA):

1. **Honeypots** — three off-screen fields (`website`, `url`, `company_website`) that
   only a bot fills in. Any value = silently dropped.
2. **Behavioural checks** — the client stamps each submission with how long the page
   was open and whether any field was ever clicked or typed into. Instant submissions,
   submissions with no interaction at all, requests with no `Origin`/`Referer`, and
   scripted user-agents (`python-requests`, `curl`, …) all score against the sender.
   There's also a best-effort per-IP burst limit.
3. **Content scoring** (`api/_spam.js`) — weighted rules for SEO/marketing keywords,
   cold-outreach boilerplate ("I came across your website…"), links or HTML in the
   message, non-Latin script, filler phone numbers, disposable email domains and
   high-risk TLDs.

### How you see it in the inbox

Every rule that fires adds points, and the total decides what happens:

| Score | What happens |
| --- | --- |
| `0–4` | Delivered normally. Email carries a green **"✓ Passed spam checks"** line. |
| `5–11` | Delivered, but the subject is prefixed **`[SPAM?]`** and the email opens with a red banner listing exactly which checks it tripped. |
| `12+` | Never emailed. Logged in full under **Vercel → your project → Logs** (search `BLOCKED as spam`) so nothing is truly lost. |

Every email also carries `X-Spam-Flag`, `X-Spam-Score` and `X-IKAD-Spam-Reasons`
headers.

**Gmail filter (recommended):** Settings → Filters → *Create a new filter* → Subject
contains `[SPAM?]` → *Apply the label* `Possible Spam` and *Skip the Inbox*. Real
quote requests then land in the inbox untouched, and anything questionable is one
click away for review rather than lost.

### Tuning

All thresholds are environment variables, no code change needed:

- `QUOTE_SPAM_FLAG_SCORE` (default `5`) — lower it to tag more aggressively.
- `QUOTE_SPAM_BLOCK_SCORE` (default `12`) — **raise it** if a real lead ever gets
  blocked; check the Vercel logs to see the score and reasons first.
- `QUOTE_SPAM_TO_EMAIL` — set it and blocked spam is delivered to that address
  instead of being dropped, so you can audit for a couple of weeks.
- `QUOTE_ALLOWED_HOSTS` (default `ikad.ca,vercel.app,localhost`) — hosts the form
  may be submitted from.

Keyword lists live at the top of `api/_spam.js`; add new spam phrases there as they
show up.

## Cleaning up

The `temp-extract/` folder contains the original zip contents from the photographer's footage drop (~4.9 GB of MOV/MP4 video). Everything needed by the live site is already copied into `assets/images/`. You can safely delete `temp-extract/` to reclaim space:

```bash
rm -rf temp-extract
```
