// Spam scoring for the IKAD quote form.
//
// Every submission gets a score. Rules that fire are recorded by name so the
// notification email can show exactly WHY something was flagged.
//
//   score >= FLAG_THRESHOLD  (default 5)  -> delivered, but subject is prefixed
//                                            with [SPAM?] and headers are tagged
//   score >= BLOCK_THRESHOLD (default 12) -> never emailed, logged only
//
// Tune with env vars QUOTE_SPAM_FLAG_SCORE / QUOTE_SPAM_BLOCK_SCORE.

export const FLAG_THRESHOLD = Number(process.env.QUOTE_SPAM_FLAG_SCORE) || 5;
export const BLOCK_THRESHOLD = Number(process.env.QUOTE_SPAM_BLOCK_SCORE) || 12;

/* ------------------------------------------------------------------ *
 * Keyword lists
 * ------------------------------------------------------------------ */

// Phrases that essentially never appear in a real HVAC enquiry.
const STRONG_TERMS = [
  'seo', 'search engine optimization', 'search engine optimisation',
  'backlink', 'back link', 'link building', 'link exchange',
  'guest post', 'guest posting', 'domain authority', 'dofollow', 'do-follow',
  'off page', 'off-page', 'on page seo', 'on-page seo', 'serp',
  'first page of google', 'top of google', 'top on google', 'rank higher',
  'rank your website', 'ranking on google', 'google ranking', 'higher rankings',
  'increase your traffic', 'website traffic', 'organic traffic', 'more visitors',
  'web design', 'website design', 'website redesign', 'web development',
  'website development', 'wordpress development', 'shopify development',
  'digital marketing', 'internet marketing', 'social media marketing',
  'lead generation', 'ppc', 'adwords', 'google ads campaign',
  'app development', 'mobile app', 'logo design', 'graphic design',
  'white label', 'outsourc', 'offshore team', 'dedicated developers',
  'b2b leads', 'email list', 'data entry', 'virtual assistant', 'cold email',
  'website audit', 'free audit', 'free seo', 'seo audit', 'site audit',
  'crypto', 'bitcoin', 'forex', 'investment opportunity', 'loan offer',
  'casino', 'viagra', 'cialis', 'porn', 'escort', 'xxx', 'webcam',
  'work from home', 'make money online', 'earn money', 'binary option',
];

// Cold-outreach boilerplate. Softer — a real person could stumble into one.
const SOFT_TERMS = [
  'came across your website', 'visited your website', 'i was browsing',
  'i noticed your website', 'noticed that your website', 'your website is not',
  'checked your website', 'reviewing your website', 'went through your website',
  'dear sir', 'dear madam', 'dear owner', 'to whom it may concern',
  'hope this email finds you', 'hope this message finds you',
  'hope you are doing well', 'hope you\'re doing well', 'greetings of the day',
  'we specialize in', 'we specialise in', 'our team of experts',
  'business proposal', 'partnership opportunity', 'mutually beneficial',
  'if you are interested', 'if you\'re interested', 'let me know if you would',
  'no obligation', 'unsubscribe', 'opt out of', 'best regards,',
  'affordable price', 'competitive price', 'reasonable price',
  'increase your sales', 'grow your business', 'boost your',
  'i can send you', 'send you a proposal', 'schedule a call',
];

const DISPOSABLE_DOMAINS = [
  'mailinator.com', 'guerrillamail.com', 'yopmail.com', 'temp-mail.org',
  'tempmail.com', '10minutemail.com', 'trashmail.com', 'sharklasers.com',
  'getnada.com', 'dispostable.com', 'maildrop.cc', 'throwawaymail.com',
  'fakeinbox.com', 'mailnesia.com', 'spam4.me', 'grr.la', 'moakt.com',
];

const BOT_AGENTS = [
  'curl/', 'wget', 'python-requests', 'python-urllib', 'go-http-client',
  'okhttp', 'java/', 'libwww-perl', 'axios/', 'node-fetch', 'postmanruntime',
  'insomnia', 'httpie', 'scrapy', 'phantomjs', 'headlesschrome', 'zgrab',
];

// Note: bare `.ca` domains are deliberately NOT matched — local customers often
// mention their own business site. Explicit http(s):// links are caught regardless.
const URL_RE = /(https?:\/\/|www\.[a-z0-9-]+\.[a-z]{2,}|\b[a-z0-9-]+\.(?:com|net|org|io|ru|cn|info|biz|xyz|top|online|site|shop|club|live|store)\b)/i;
const HTML_RE = /<\s*(a|script|img|iframe|div|p|br)\b|\[url[=\]]|\[link[=\]]/i;
// Cyrillic, Arabic, Devanagari, CJK, Kana, Hangul.
const NON_LATIN_RE = /[Ѐ-ӿ؀-ۿऀ-ॿ一-鿿぀-ヿ가-힯]/;

const wordRe = (term) => {
  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`(^|[^a-z0-9])${escaped}`, 'i');
};

const digitsOnly = (s) => String(s || '').replace(/\D/g, '');

/* ------------------------------------------------------------------ *
 * Best-effort per-IP rate limiting.
 * Serverless instances are recycled, so this only catches bursts that land
 * on the same warm instance — which is exactly what form-blasting bots do.
 * ------------------------------------------------------------------ */

const HITS = new Map();
const WINDOW_MS = 10 * 60 * 1000;
const SOFT_LIMIT = 3;   // more than this in the window -> suspicious
const HARD_LIMIT = 6;   // more than this -> treat as an attack

export function recordHit(ip) {
  if (!ip) return 0;
  const now = Date.now();
  const recent = (HITS.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  recent.push(now);
  HITS.set(ip, recent);
  // Keep the map from growing unbounded on a long-lived instance.
  if (HITS.size > 500) {
    for (const [key, times] of HITS) {
      if (!times.length || now - times[times.length - 1] > WINDOW_MS) HITS.delete(key);
    }
  }
  return recent.length;
}

/* ------------------------------------------------------------------ *
 * Scoring
 * ------------------------------------------------------------------ */

/**
 * @param {object} fields  { name, phone, email, city, service, message }
 * @param {object} ctx     { elapsedMs, origin, referer, userAgent, acceptLanguage, ip, hits, allowedHosts }
 * @returns {{score:number, reasons:string[], isSpam:boolean, isBlocked:boolean}}
 */
export function scoreSubmission(fields, ctx = {}) {
  const reasons = [];
  let score = 0;
  const add = (points, why) => { score += points; reasons.push(`${why} (+${points})`); };

  const name = String(fields.name || '');
  const phone = String(fields.phone || '');
  const email = String(fields.email || '');
  const city = String(fields.city || '');
  const service = String(fields.service || '');
  const message = String(fields.message || '');

  const haystack = `${name} ${email} ${city} ${service} ${message}`.toLowerCase();

  /* --- Content signals --- */

  const strongHits = STRONG_TERMS.filter((t) => wordRe(t).test(haystack));
  if (strongHits.length) {
    add(Math.min(6 + (strongHits.length - 1) * 2, 12),
      `Marketing/SEO keywords: ${strongHits.slice(0, 5).join(', ')}`);
  }

  const softHits = SOFT_TERMS.filter((t) => haystack.includes(t));
  if (softHits.length) {
    add(Math.min(softHits.length * 2, 6),
      `Cold-outreach phrasing: ${softHits.slice(0, 4).join(', ')}`);
  }

  if (URL_RE.test(message)) {
    const count = (message.match(/https?:\/\//gi) || []).length;
    add(count >= 2 ? 8 : 5, 'Link(s) in the message body');
  }
  if (URL_RE.test(name)) add(8, 'Link in the name field');
  if (HTML_RE.test(`${name} ${message}`)) add(8, 'HTML or BBCode markup in the submission');
  if (NON_LATIN_RE.test(`${name} ${message}`)) add(6, 'Non-Latin script (Cyrillic/CJK/Arabic)');
  if (name.includes('@') || name.includes('://')) add(3, 'Name field contains an email or URL');
  if (message.length > 40) {
    const letters = message.replace(/[^a-z]/gi, '');
    const upper = message.replace(/[^A-Z]/g, '');
    if (letters.length && upper.length / letters.length > 0.7) add(2, 'Message is nearly all caps');
  }

  /* --- Phone signals --- */

  const digits = digitsOnly(phone);
  if (/^(\d)\1+$/.test(digits) || /^1?(?:0123456789|1234567890|9876543210)$/.test(digits)) {
    add(6, 'Filler phone number');
  } else if (digits.length === 10 || (digits.length === 11 && digits.startsWith('1'))) {
    const area = digits.length === 11 ? digits.slice(1, 4) : digits.slice(0, 3);
    if (/^[01]/.test(area)) add(3, 'Impossible North American area code');
  } else if (digits.length > 11) {
    add(2, 'International phone number');
  }

  /* --- Email signals --- */

  const domain = (email.split('@')[1] || '').toLowerCase();
  if (DISPOSABLE_DOMAINS.includes(domain)) add(5, `Disposable email domain (${domain})`);
  if (/\.(ru|cn|tk|ml|ga|cf|gq|top|xyz|buzz)$/.test(domain)) add(4, `High-risk email TLD (${domain})`);

  /* --- Behavioural / transport signals --- */

  const { elapsedMs, interacted, origin, referer, userAgent, acceptLanguage, hits, allowedHosts = [] } = ctx;

  if (elapsedMs == null) {
    add(2, 'No timing data (form posted without running our JavaScript)');
  } else if (elapsedMs < 1200) {
    add(7, `Form submitted in ${elapsedMs}ms — faster than a human can type`);
  } else if (elapsedMs < 3000) {
    add(4, `Form submitted in ${(elapsedMs / 1000).toFixed(1)}s — unusually fast`);
  }

  if (interacted === 0) add(6, 'Submitted without a single click, keystroke or field focus');

  const hostOf = (u) => { try { return new URL(u).host.toLowerCase(); } catch { return ''; } };
  const originHost = hostOf(origin) || hostOf(referer);
  if (!origin && !referer) {
    add(4, 'No Origin/Referer header — posted directly to the API, not from the site');
  } else if (allowedHosts.length && originHost && !allowedHosts.some((h) => originHost === h || originHost.endsWith(`.${h}`))) {
    add(6, `Submitted from an outside origin (${originHost})`);
  }

  const ua = String(userAgent || '').toLowerCase();
  if (!ua) add(3, 'No browser User-Agent');
  else if (BOT_AGENTS.some((a) => ua.includes(a))) add(6, `Automated client User-Agent (${ua.slice(0, 40)})`);
  if (!acceptLanguage) add(2, 'No Accept-Language header');

  if (!city && !service) add(3, 'City and service both missing (fields the real form requires)');

  if (hits > HARD_LIMIT) add(8, `${hits} submissions from this IP in 10 minutes`);
  else if (hits > SOFT_LIMIT) add(4, `${hits} submissions from this IP in 10 minutes`);

  return {
    score,
    reasons,
    isSpam: score >= FLAG_THRESHOLD,
    isBlocked: score >= BLOCK_THRESHOLD,
  };
}
