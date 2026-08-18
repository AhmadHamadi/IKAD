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
├── estimate/                   → /estimate/  (Instant HVAC Estimator, indexed)
│   ├── ac-replacement/         → ad landing page, noindex
│   ├── repair-or-replace/      → ad landing page, noindex
│   ├── financing/              → ad landing page, noindex
│   └── free-duct-cleaning/     → ad landing page, noindex
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

## Instant HVAC Estimator (`/estimate/`)

A guided estimator that qualifies the homeowner, gates the result behind contact
capture, then shows Good / Better / Best packages with installed pricing, monthly
payments, estimated rebates and an appointment request.

| File | Role |
| --- | --- |
| `assets/js/estimator.js` | Question flow, pricing engine, equipment catalogue, results UI |
| `assets/css/estimator.css` | Estimator-only styles (depends on `main.css` for tokens) |
| `api/estimate.js` | Serverless endpoint: spam scoring, lead scoring, both emails |
| `_build/generate_pages.py` → `ESTIMATOR_CAMPAIGNS` | One entry per landing page |

**Pricing.** Base ranges live in `CATALOG` in `assets/js/estimator.js`, quoted at the
2,000–2,500 sq. ft. baseline and scaled by a per-size `factor`. They deliberately match
the published cost guides in `/blog/` — **change both together or the site contradicts
itself.** Rebates follow Ontario's 2026 Home Renovation Savings rates
(~$1,250/ton for a full heat pump capped at $7,500, ~$500/ton hybrid, ~$100 thermostat).
Financing is illustrated at `FINANCE` (9.99% / 120 months) and always labelled OAC.

**Campaigns.** Add an object to `ESTIMATOR_CAMPAIGNS` and re-run the generator. `preset`
answers are applied *and their steps skipped*, so an "AC replacement" ad never re-asks
what the ad already said; a "not what you need?" control on step 1 lets a mis-clicked
visitor start over. Campaign pages are `noindex` so they never compete with `/estimate/`
in search. Point ads at e.g.
`/estimate/ac-replacement/?utm_source=meta&utm_campaign=ac-over-12`.

**Lead delivery.** The endpoint fires once per homeowner action, all sharing one
`lead_id`:

| stage | fires when | sends |
| --- | --- | --- |
| `estimate` | contact captured, result revealed | lead email **+** a copy to the homeowner |
| `selection` | they pick a Good/Better/Best tier | short update to sales |
| `booking` | they request an assessment slot | hot booking alert |
| `callback` | they ask an expert to contact them | callback alert |
| `resend` | they click "email my estimate again" | homeowner copy **only** — never a second lead |

Buying intent is scored server-side out of 120 from system age, timeline, stated reasons,
financing interest and tier selection, and rendered as a 🔥 rating in the subject line
alongside UTM / fbclid / gclid attribution.

Extra environment variables beyond the `/api/quote` set:

- `ESTIMATE_TO_EMAIL` — where leads go (falls back to `QUOTE_TO_EMAIL`).
- `ESTIMATE_SEND_COPY` — set to `0` to stop emailing homeowners their own estimate.

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
