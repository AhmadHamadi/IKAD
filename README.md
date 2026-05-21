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

## Contact form

The contact form (`/contact/`) currently falls back to a `mailto:info@ikad.ca` submission via JavaScript. To convert it to a real backend, point the `<form>` action at your handler of choice (Formspree, Netlify Forms, HubSpot, custom endpoint) and remove the `data-form="quote"` JS hook in `assets/js/main.js`.

## Cleaning up

The `temp-extract/` folder contains the original zip contents from the photographer's footage drop (~4.9 GB of MOV/MP4 video). Everything needed by the live site is already copied into `assets/images/`. You can safely delete `temp-extract/` to reclaim space:

```bash
rm -rf temp-extract
```
