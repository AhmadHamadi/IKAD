"""GSC + Indexability + AI readiness automated test suite. Run from project root."""
import os, re, json

print("="*70)
print("AUTOMATED TEST SUITE: GSC + INDEXABILITY + AI READINESS")
print("="*70)

pages = []
for root,_,files in os.walk('.'):
    if any(x in root for x in ['_build','.git','temp-extract','node_modules']): continue
    for f in files:
        if f.endswith('.html'):
            pages.append(os.path.join(root,f).replace(os.sep,'/').lstrip('./'))
pages.sort()

# Which pages are actually noindex, read from the robots meta rather than
# guessed from the filename. Paid-traffic landing pages are noindex by design
# and must not be graded on canonical / sitemap / breadcrumb / LCP-preload.
def _robots(p):
    m = re.search(r'<meta name="robots" content="([^"]*)"', open(p,'r',encoding='utf-8').read())
    return m.group(1) if m else ''

NOINDEX = {p for p in pages if 'noindex' in _robots(p)}

results = {}
fail_examples = {}

def add_fail(category, item):
    fail_examples.setdefault(category, []).append(item)

# T1: doctype + html closing
t1 = sum(1 for p in pages if open(p,'r',encoding='utf-8').read().startswith(('<!doctype','<!DOCTYPE')) and '</html>' in open(p,'r',encoding='utf-8').read())
results['Valid HTML doctype + closing tag'] = (t1, len(pages))

# T2: every indexable page has JSON-LD (404 + thank-you are noindex, no schema needed)
indexable = [p for p in pages if p not in NOINDEX]
t2 = sum(1 for p in indexable if 'application/ld+json' in open(p,'r',encoding='utf-8').read())
results['Has JSON-LD schema (indexable pages)'] = (t2, len(indexable))

# T3: all JSON-LD parses
t3p = 0; t3t = 0
for p in pages:
    c = open(p,'r',encoding='utf-8').read()
    for s in re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', c, re.DOTALL):
        t3t += 1
        try: json.loads(s); t3p += 1
        except Exception as e: add_fail('Invalid JSON-LD', (p, str(e)[:60]))
results['JSON-LD blocks valid'] = (t3p, t3t)

# T4: unique titles
titles = {}
for p in pages:
    m = re.search(r'<title>([^<]+)</title>', open(p,'r',encoding='utf-8').read())
    if m: titles.setdefault(m.group(1), []).append(p)
dup_titles = sum(1 for t,ps in titles.items() if len(ps) > 1)
results['Unique titles'] = (len(titles) - dup_titles, len(titles))

# T5: canonical matches own URL
t5p = 0; t5t = 0
for p in pages:
    if p in NOINDEX: continue
    t5t += 1
    c = open(p,'r',encoding='utf-8').read()
    m = re.search(r'<link rel="canonical" href="([^"]+)"', c)
    if m:
        canon = m.group(1)
        ep = p.replace('index.html','').rstrip('/')
        expected = 'https://ikad.ca/' if ep == '' else f'https://ikad.ca/{ep}/'
        if canon == expected: t5p += 1
        else: add_fail('Canonical mismatch', (p, f'wanted {expected} got {canon}'))
results['Canonical matches own URL'] = (t5p, t5t)

# T6: vercel.json security headers
vc = open('vercel.json','r').read()
hdrs = ['Strict-Transport-Security','Content-Security-Policy','X-Frame-Options','X-Content-Type-Options','Referrer-Policy','Permissions-Policy']
t6 = sum(1 for h in hdrs if h in vc)
results['vercel.json security headers'] = (t6, len(hdrs))

# T7: sitemap covers indexable pages
sm = open('sitemap.xml').read()
sm_urls = set(re.findall(r'<loc>https://ikad\.ca/([^<]*)</loc>', sm))
indexable_urls = set()
for p in pages:
    if p in NOINDEX: continue
    u = p.replace('index.html','').rstrip('/')
    indexable_urls.add('' if u == '' else u + '/')
t7 = sum(1 for u in indexable_urls if u in sm_urls)
results['Indexable pages in sitemap'] = (t7, len(indexable_urls))

# T8: required crawlers in robots.txt
rt = open('robots.txt').read()
crawlers = ['Googlebot','Bingbot','GPTBot','ClaudeBot','PerplexityBot','Google-Extended','Applebot-Extended','CCBot']
t8 = sum(1 for c in crawlers if f'User-agent: {c}' in rt)
results['Required crawlers allowed in robots.txt'] = (t8, len(crawlers))

# T9: viewport
t9 = sum(1 for p in pages if 'width=device-width' in open(p,'r',encoding='utf-8').read())
results['Mobile viewport on all pages'] = (t9, len(pages))

# T10: html lang
t10 = sum(1 for p in pages if re.search(r'<html[^>]+lang=["\']en', open(p,'r',encoding='utf-8').read()[:500]))
results['HTML lang attribute'] = (t10, len(pages))

# T11: blog posts have BlogPosting
blog_posts = [p for p in pages if p.startswith('blog/') and p.endswith('/index.html') and p != 'blog/index.html']
t11 = 0
for p in blog_posts:
    c = open(p,'r',encoding='utf-8').read()
    if '"BlogPosting"' in c: t11 += 1
results['Blog posts have BlogPosting schema'] = (t11, len(blog_posts))

# T12: FAQPage schemas valid
t12p = 0; t12t = 0
for p in pages:
    c = open(p,'r',encoding='utf-8').read()
    for s in re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', c, re.DOTALL):
        try:
            d = json.loads(s)
            if d.get('@type') == 'FAQPage':
                t12t += 1
                qs = d.get('mainEntity',[])
                if len(qs) >= 2 and not any('<' in q.get('acceptedAnswer',{}).get('text','') for q in qs):
                    t12p += 1
        except: pass
results['FAQPage valid (>=2 Qs, no HTML)'] = (t12p, t12t)

# T13: non-home has breadcrumb
t13p = 0; t13t = 0
for p in pages:
    if p == 'index.html' or p in NOINDEX: continue
    t13t += 1
    if 'BreadcrumbList' in open(p,'r',encoding='utf-8').read(): t13p += 1
results['Non-home pages have breadcrumb'] = (t13p, t13t)

# T14: images alt + dims (excluding noindex pages)
t14p = 0; t14t = 0
for p in pages:
    if p in NOINDEX: continue  # noindex pages excluded
    c = open(p,'r',encoding='utf-8').read()
    for img in re.findall(r'<img[^>]+>', c):
        if 'class="icon"' in img or 'ikad-logo' in img: continue
        t14t += 1
        if 'alt=' in img and 'width=' in img and 'height=' in img: t14p += 1
results['Images: alt + width + height (indexable)'] = (t14p, t14t)

# T15: AI files exist
ai_files = ['llms.txt','llms-full.txt','humans.txt','.well-known/security.txt']
t15 = sum(1 for f in ai_files if os.path.exists(f) and os.path.getsize(f) > 200)
results['AI discovery files exist'] = (t15, len(ai_files))

# T16: internal links don't 404
valid_paths = set()
for root,_,files in os.walk('.'):
    if any(x in root for x in ['_build','.git','temp-extract','node_modules']): continue
    for f in files:
        if f.endswith('.html'):
            rel = os.path.relpath(os.path.join(root,f),'.').replace(os.sep,'/')
            valid_paths.add(rel)
            if rel.endswith('/index.html'):
                valid_paths.add(rel[:-10])
                valid_paths.add(rel[:-11])
broken = 0; total_links = 0
for p in pages:
    c = open(p,'r',encoding='utf-8').read()
    for m in re.finditer(r'href="([^"]+)"', c):
        href = m.group(1)
        if href.startswith(('http','tel:','sms:','mailto:','#','/','data:')): continue
        if href.endswith(('.pdf','.png','.jpg','.webp','.xml','.txt','.js','.css','.ico')): continue
        total_links += 1
        pd = os.path.dirname(p)
        tgt = os.path.normpath(os.path.join(pd, href.split('#')[0])).replace(os.sep,'/')
        if not tgt: continue
        candidates = [tgt, tgt+'/index.html', tgt+'index.html', tgt+'/']
        if any(t in valid_paths or os.path.exists(t) for t in candidates):
            pass
        else:
            broken += 1
            add_fail('Broken link', (p, href))
results['Internal links resolve'] = (total_links - broken, total_links)

# T17: hero image preload on indexable pages
t17p = 0; t17t = 0
for p in pages:
    if p in NOINDEX or 'privacy' in p or 'terms' in p: continue
    c = open(p,'r',encoding='utf-8').read()
    # Only pages whose LCP is actually an image can preload one. Text-hero
    # pages (e.g. the estimator) have nothing to preload and aren't graded.
    if 'class="hero__bg"' not in c: continue
    t17t += 1
    if 'rel="preload"' in c and 'as="image"' in c: t17p += 1
results['Hero preload (LCP signal)'] = (t17p, t17t)

# T18: every page has OG and Twitter card
t18p = 0
for p in pages:
    c = open(p,'r',encoding='utf-8').read()
    if all(t in c for t in ['og:title','og:description','og:image','og:url','twitter:card']):
        t18p += 1
results['Full OG + Twitter tags'] = (t18p, len(pages))

# T19: every page has robots meta
t19p = sum(1 for p in pages if 'name="robots"' in open(p,'r',encoding='utf-8').read())
results['Meta robots present'] = (t19p, len(pages))

# T20: no spammy patterns
spam_patterns = [
    (r'(SEO|click here|buy now){3,}', 'keyword stuffing'),
    (r'<a [^>]+style="display:\s*none', 'hidden link'),
    (r'<div [^>]+style="[^"]*font-size:\s*0', 'font-size 0 hidden text'),
    (r'<div [^>]+style="[^"]*position:\s*absolute[^"]*left:\s*-\d+', 'off-screen hidden text'),
]
t20p = 0
for p in pages:
    c = open(p,'r',encoding='utf-8').read()
    ok = True
    for pat, desc in spam_patterns:
        if re.search(pat, c):
            ok = False
            add_fail(f'Spam pattern: {desc}', (p, ''))
            break
    if ok: t20p += 1
results['No spam patterns (hidden text, keyword stuffing)'] = (t20p, len(pages))

# T21: anchor text diversity (no over-optimized anchor text)
all_anchors = []
for p in pages:
    c = open(p,'r',encoding='utf-8').read()
    for m in re.finditer(r'<a [^>]+href="[^"]*service-areas/([^/]+)/[^"]*"[^>]*>([^<]+)</a>', c):
        all_anchors.append((m.group(1), m.group(2).strip()))
# For each city, check anchor text diversity
city_anchor_diversity = {}
for city, anchor in all_anchors:
    city_anchor_diversity.setdefault(city, set()).add(anchor.lower())
diverse_cities = sum(1 for city, anchors in city_anchor_diversity.items() if len(anchors) >= 3)
results['City anchor text diversity (>=3 variants/city)'] = (diverse_cities, len(city_anchor_diversity))

# Print results
print()
critical_fails = []
total_pct = 0
total_tests = 0
for name, (passed, total) in results.items():
    if total == 0: continue
    pct = 100 * passed / total
    total_pct += pct
    total_tests += 1
    status = "PASS" if passed == total else f"{passed}/{total} ({pct:.0f}%)"
    print(f"  {name:55s}: {status}")
    if passed < total: critical_fails.append(name)

print(f"\nOverall: {total_pct/total_tests:.1f}% average across {total_tests} test categories")
if critical_fails:
    print(f"{len(critical_fails)} tests below 100%:")
    for k,vs in fail_examples.items():
        print(f"\n  {k}:")
        for v in vs[:3]: print(f"    - {v}")
else:
    print(f"All {total_tests} tests at 100% pass rate. Site is GSC + AI ready.")
