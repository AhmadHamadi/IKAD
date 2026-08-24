/**
 * Resend migration test harness — SENDS NOTHING.
 *
 * global.fetch is stubbed, so every call the mailer makes to the Resend API is
 * captured and inspected instead of delivered. Exercises every form and every
 * email path on the site, prints the subject line for each, and re-checks that
 * the spam filters and field validation still reject bad submissions.
 *
 *   node _build/test-resend.mjs
 */

process.env.RESEND_API_KEY = process.env.RESEND_API_KEY || 're_TEST_KEY_NOT_REAL';
process.env.RESEND_FROM = process.env.RESEND_FROM || 'IKAD Mechanical <info@tradeleadsmarketing.com>';
// Deliberately left unset so a stub failure can never silently fall back to SMTP.
delete process.env.SMTP_HOST; delete process.env.SMTP_PORT;
delete process.env.SMTP_USER; delete process.env.SMTP_PASS;

const sent = [];
let nextStatus = 200;

globalThis.fetch = async (url, opts) => {
  const payload = JSON.parse(opts.body);
  sent.push({ url, auth: opts.headers.Authorization, payload });
  return {
    ok: nextStatus < 400,
    status: nextStatus,
    json: async () => (nextStatus < 400
      ? { id: 'stub-' + sent.length }
      : { name: 'validation_error', message: 'stubbed failure' }),
  };
};

const quote = (await import('../api/quote.js')).default;
const estimate = (await import('../api/estimate.js')).default;

function mkRes() {
  const r = { statusCode: null, body: null };
  r.status = (c) => { r.statusCode = c; return r; };
  r.json = (b) => { r.body = b; return r; };
  r.setHeader = () => {};
  return r;
}
const mkReq = (body, headers = {}) => ({
  method: 'POST',
  body,
  headers: {
    origin: 'https://ikad.ca',
    referer: 'https://ikad.ca/contact/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
    'accept-language': 'en-CA,en;q=0.9',
    'x-forwarded-for': '198.51.100.' + Math.floor(Math.random() * 200),
    ...headers,
  },
  socket: { remoteAddress: '198.51.100.7' },
});

const goodQuote = (over = {}) => ({
  name: 'Jane Doe', phone: '905 555 0142', email: 'jane@example.com',
  city: 'Oakville', service: 'Duct work', message: 'Upstairs is always cold.',
  source_page: '/duct-work/', form_elapsed_ms: 45000, form_interacted: 1, ...over,
});

const goodEstimate = (over = {}) => ({
  contact: {
    first_name: 'Sam', last_name: 'Rivera', phone: '905 555 0188',
    email: 'sam@example.com', city: 'Burlington', address: '12 Maple St', postal: 'L7L 1A1',
  },
  answers: { home_size: '2000', reasons: ['comfort'] },
  sizing: { tons: 3 },
  system: { label: 'Heat pump + furnace' },
  packages: [
    { tier: 'good', name: 'Good', catLabel: 'Heat pump', low: 9000, high: 11000, monthly: 140 },
    { tier: 'better', name: 'Better', catLabel: 'Heat pump', low: 12000, high: 14000, monthly: 180 },
  ],
  form_elapsed_ms: 90000, form_interacted: 1, ...over,
});

const results = [];
async function run(label, handler, body, headers) {
  const before = sent.length;
  const res = mkRes();
  await handler(mkReq(body, headers), res);
  results.push({ label, status: res.statusCode, emails: sent.slice(before) });
}

console.log('Stubbing fetch — no email will be delivered.\n');

// ---- every form / every email path ----
await run('Quote form (all 20 pages post here) — clean lead', quote, goodQuote());
await run('Quote form — spam-flagged lead', quote, goodQuote({
  name: 'ALEKSANDR', email: 'seo@cheap-backlinks.ru',
  message: 'BUY CHEAP SEO BACKLINKS, casino, crypto loan http://spam1.ru http://spam2.ru',
  form_elapsed_ms: 400, form_interacted: 0,
}));
await run('Estimator — stage: estimate (sales + homeowner copy)', estimate, goodEstimate());
await run('Estimator — stage: selection', estimate, goodEstimate({ stage: 'selection', chosen_tier: 'better' }));
await run('Estimator — stage: booking', estimate, goodEstimate({ stage: 'booking', appointment: { when: 'Tue AM' } }));
await run('Estimator — stage: callback', estimate, goodEstimate({ stage: 'callback' }));
await run('Estimator — stage: resend (homeowner copy only)', estimate, goodEstimate({ stage: 'resend' }));

console.log('='.repeat(78));
console.log('EVERY EMAIL THE SITE CAN SEND');
console.log('='.repeat(78));
let n = 0;
for (const r of results) {
  console.log(`\n${r.label}   [HTTP ${r.status}]`);
  if (!r.emails.length) { console.log('   (no email — expected for blocked/dropped submissions)'); continue; }
  for (const e of r.emails) {
    n++;
    const p = e.payload;
    console.log(`   ${n}. SUBJECT: ${p.subject}`);
    console.log(`      from ....... ${p.from}`);
    console.log(`      to ......... ${JSON.stringify(p.to)}`);
    console.log(`      reply_to ... ${p.reply_to || '(none)'}`);
    console.log(`      html ${p.html ? p.html.length + ' chars' : 'MISSING'} · text ${p.text ? p.text.length + ' chars' : 'MISSING'}`);
  }
}

// ---- contract checks ----
console.log('\n' + '='.repeat(78));
console.log('CONTRACT CHECKS');
console.log('='.repeat(78));
const checks = [];
const ok = (name, cond, detail = '') => checks.push({ name, cond, detail });

ok('Every send hit the Resend API', sent.every((s) => s.url === 'https://api.resend.com/emails'));
ok('Bearer token used', sent.every((s) => /^Bearer re_/.test(s.auth)));
ok('Every email has BOTH html and text', sent.every((s) => s.payload.html && s.payload.text));
ok('Uses reply_to, never replyTo', sent.every((s) => !('replyTo' in s.payload)));
ok('Real recipients in "to"', sent.every((s) => Array.isArray(s.payload.to) && s.payload.to.length > 0));
ok('Never uses bcc', sent.every((s) => !('bcc' in s.payload)));
ok('From is the verified Resend domain', sent.every((s) => s.payload.from.includes('@tradeleadsmarketing.com')),
   [...new Set(sent.map((s) => s.payload.from))].join(', '));
ok('Sales emails still reply to the customer',
   sent.filter((s) => s.payload.to.includes('Saifsabeeh.31@gmail.com')).every((s) => s.payload.reply_to));
ok('Recipients unchanged from before the migration',
   [...new Set(sent.flatMap((s) => s.payload.to))].every((t) =>
     ['Saifsabeeh.31@gmail.com', 'sam@example.com', 'jane@example.com'].includes(t)),
   [...new Set(sent.flatMap((s) => s.payload.to))].join(', '));

// ---- spam + validation still enforced ----
const guard = async (label, handler, body, expectStatus, expectEmails) => {
  const before = sent.length;
  const res = mkRes();
  await handler(mkReq(body), res);
  const emails = sent.length - before;
  ok(label, res.statusCode === expectStatus && emails === expectEmails,
     `HTTP ${res.statusCode}, ${emails} email(s)`);
};
await guard('Honeypot still dropped silently', quote, goodQuote({ website: 'http://bot.ru' }), 200, 0);
await guard('Missing required fields still 400', quote, goodQuote({ phone: '', email: '' }), 400, 0);
await guard('Malformed email still 400', quote, goodQuote({ email: 'not-an-email' }), 400, 0);
await guard('Short phone still 400', quote, goodQuote({ phone: '12345' }), 400, 0);
await guard('Estimator honeypot still dropped', estimate,
  goodEstimate({ contact: { ...goodEstimate().contact, website: 'http://bot.ru' } }), 200, 0);
await guard('Estimator missing fields still 400', estimate,
  goodEstimate({ contact: { first_name: '', phone: '', email: '' } }), 400, 0);

// ---- transport failure must surface, not vanish ----
nextStatus = 422;
const failRes = mkRes();
await quote(mkReq(goodQuote()), failRes);
ok('Resend API error surfaces as 502 (no SMTP configured)', failRes.statusCode === 502,
   `HTTP ${failRes.statusCode}`);
nextStatus = 200;

let pass = 0, fail = 0;
for (const c of checks) {
  console.log(`  [${c.cond ? 'PASS' : 'FAIL'}] ${c.name}${c.detail ? '  —  ' + c.detail : ''}`);
  c.cond ? pass++ : fail++;
}
console.log(`\n${pass} passed, ${fail} failed · ${n} emails captured, 0 delivered`);
process.exit(fail ? 1 : 0);
