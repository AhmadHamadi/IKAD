// Vercel serverless function: POST /api/quote
// Receives quote-request form submissions, spam-scores them, and emails them
// via SMTP (nodemailer).
//
// Required environment variables (set in Vercel project settings AND in local .env):
//   SMTP_HOST   - e.g. mail.clinimedia.ca
//   SMTP_PORT   - e.g. 465 (SSL) or 587 (STARTTLS)
//   SMTP_USER   - SMTP login user (the address that will appear in From if QUOTE_FROM_EMAIL is unset)
//   SMTP_PASS   - SMTP password
//
// Optional environment variables (with sensible defaults):
//   QUOTE_TO_EMAIL         - destination address
//   QUOTE_FROM_EMAIL       - sender header (default: "IKAD Mechanical <SMTP_USER>")
//   QUOTE_SUBJECT_PREFIX   - subject prefix for clean leads (default: [IKAD Quote])
//   QUOTE_SPAM_SUBJECT_TAG - subject prefix for flagged leads (default: [SPAM?])
//   QUOTE_SPAM_TO_EMAIL    - if set, blocked (obvious) spam is copied here instead of dropped
//   QUOTE_SPAM_FLAG_SCORE  - score at which a lead is tagged as suspected spam (default 5)
//   QUOTE_SPAM_BLOCK_SCORE - score at which a lead is never emailed (default 12)
//   QUOTE_ALLOWED_HOSTS    - comma-separated hosts the form may be submitted from

import nodemailer from 'nodemailer';
import { scoreSubmission, recordHit, FLAG_THRESHOLD, BLOCK_THRESHOLD } from './_spam.js';

const TO_EMAIL = process.env.QUOTE_TO_EMAIL || 'Saifsabeeh.31@gmail.com';
const SUBJECT_PREFIX = process.env.QUOTE_SUBJECT_PREFIX || '[IKAD Quote]';
const SPAM_TAG = process.env.QUOTE_SPAM_SUBJECT_TAG || '[SPAM?]';
const ALLOWED_HOSTS = (process.env.QUOTE_ALLOWED_HOSTS || 'ikad.ca,vercel.app,localhost')
  .split(',').map((h) => h.trim().toLowerCase()).filter(Boolean);

const escapeHtml = (s) =>
  String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

const trim = (v, max = 500) => String(v ?? '').slice(0, max).trim();

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  body = body || {};

  // Honeypots: real visitors never see these fields, so any value means bot.
  // Pretend success and drop so the bot doesn't learn to work around it.
  if (trim(body.website) || trim(body.url) || trim(body.company_website)) {
    console.warn('[quote] honeypot triggered — dropped', {
      ip: clientIp(req), name: trim(body.name, 60), email: trim(body.email, 80),
    });
    return res.status(200).json({ ok: true });
  }

  // Validate required fields
  const name = trim(body.name, 120);
  const phone = trim(body.phone, 40);
  const email = trim(body.email, 200);
  const city = trim(body.city, 80);
  const service = trim(body.service, 120);
  const message = trim(body.message, 2000);
  const sourcePage = trim(body.source_page, 200);

  if (!name || !phone || !email) {
    return res.status(400).json({ ok: false, error: 'Name, phone, and email are required.' });
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ ok: false, error: 'Invalid email address.' });
  }
  if (phone.replace(/\D/g, '').length < 10) {
    return res.status(400).json({ ok: false, error: 'Please enter a full 10-digit phone number.' });
  }

  /* ---------------- Spam scoring ---------------- */

  const ip = clientIp(req);
  const hits = recordHit(ip);
  const elapsedRaw = Number(body.form_elapsed_ms);
  const verdict = scoreSubmission({ name, phone, email, city, service, message }, {
    elapsedMs: Number.isFinite(elapsedRaw) && elapsedRaw >= 0 ? elapsedRaw : null,
    interacted: body.form_interacted == null ? null : Number(body.form_interacted),
    origin: req.headers.origin,
    referer: req.headers.referer || req.headers.referrer,
    userAgent: req.headers['user-agent'],
    acceptLanguage: req.headers['accept-language'],
    ip,
    hits,
    allowedHosts: ALLOWED_HOSTS,
  });

  const spamToEmail = trim(process.env.QUOTE_SPAM_TO_EMAIL, 200);

  if (verdict.isBlocked && !spamToEmail) {
    // Obvious spam. Log the whole thing (visible in Vercel → Logs) so nothing
    // is ever truly lost, then return success so the bot moves on.
    console.warn('[quote] BLOCKED as spam', {
      score: verdict.score, reasons: verdict.reasons,
      ip, name, phone, email, city, service, message: message.slice(0, 300),
    });
    return res.status(200).json({ ok: true });
  }

  /* ---------------- Send ---------------- */

  const { SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS } = process.env;
  if (!SMTP_HOST || !SMTP_PORT || !SMTP_USER || !SMTP_PASS) {
    console.error('SMTP env vars missing — set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS');
    return res.status(500).json({ ok: false, error: 'Email service unavailable. Please call (905) 491-6943.' });
  }

  const port = Number(SMTP_PORT);
  const transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port,
    secure: port === 465, // 465 = implicit TLS; 587 / others = STARTTLS
    auth: { user: SMTP_USER, pass: SMTP_PASS },
  });

  const fromHeader = process.env.QUOTE_FROM_EMAIL || `IKAD Mechanical <${SMTP_USER}>`;
  const flagged = verdict.isSpam;
  const prefix = flagged ? `${SPAM_TAG} ${SUBJECT_PREFIX}` : SUBJECT_PREFIX;
  const subject = `${prefix} ${service || 'New quote'} — ${name}${city ? ' (' + city + ')' : ''}`;

  const spamLines = flagged
    ? [
        `!! SUSPECTED SPAM — score ${verdict.score} (flag at ${FLAG_THRESHOLD}, auto-block at ${BLOCK_THRESHOLD})`,
        ...verdict.reasons.map((r) => `   - ${r}`),
        '',
      ]
    : [];

  const textBody = [
    ...spamLines,
    `New quote request from ikad.ca`,
    ``,
    `Name:    ${name}`,
    `Phone:   ${phone}`,
    `Email:   ${email}`,
    `City:    ${city || '(not given)'}`,
    `Service: ${service || '(not given)'}`,
    sourcePage ? `Page:    ${sourcePage}` : '',
    ``,
    `Message:`,
    message || '(none)',
    ``,
    `--`,
    `Spam score: ${verdict.score}${flagged ? ' — SUSPECTED SPAM' : ' — looks legitimate'}`,
    `IP: ${ip || 'unknown'}`,
  ].filter(Boolean).join('\n');

  const banner = flagged
    ? `<div style="background:#fef2f2;border:2px solid #dc2626;border-radius:6px;padding:12px 14px;margin-bottom:16px">
         <p style="margin:0 0 6px;font-size:16px;font-weight:bold;color:#b91c1c">
           ⚠ SUSPECTED SPAM — score ${verdict.score}
         </p>
         <p style="margin:0 0 6px;color:#7f1d1d">This submission tripped the following checks:</p>
         <ul style="margin:0;padding-left:20px;color:#7f1d1d">
           ${verdict.reasons.map((r) => `<li>${escapeHtml(r)}</li>`).join('')}
         </ul>
       </div>`
    : `<p style="margin:0 0 16px;padding:8px 12px;background:#f0fdf4;border-left:4px solid #16a34a;color:#166534;font-size:13px">
         ✓ Passed spam checks — score ${verdict.score} of ${FLAG_THRESHOLD} allowed.
       </p>`;

  const htmlBody = `
    <div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#111;line-height:1.5">
      ${banner}
      <p>New quote request from ikad.ca:</p>
      <p>
        <strong>Name:</strong> ${escapeHtml(name)}<br>
        <strong>Phone:</strong> ${escapeHtml(phone)}<br>
        <strong>Email:</strong> ${escapeHtml(email)}<br>
        <strong>City:</strong> ${escapeHtml(city) || '(not given)'}<br>
        <strong>Service:</strong> ${escapeHtml(service) || '(not given)'}${sourcePage ? `<br><strong>Page:</strong> ${escapeHtml(sourcePage)}` : ''}
      </p>
      ${message ? `<p><strong>Message:</strong><br>${escapeHtml(message).replace(/\n/g, '<br>')}</p>` : ''}
      <p style="color:#6b7280;font-size:12px;border-top:1px solid #e5e7eb;padding-top:8px;margin-top:16px">
        Spam score ${verdict.score} · IP ${escapeHtml(ip || 'unknown')}
      </p>
    </div>
  `;

  try {
    const info = await transporter.sendMail({
      from: fromHeader,
      to: verdict.isBlocked && spamToEmail ? spamToEmail : TO_EMAIL,
      replyTo: email,
      subject,
      text: textBody,
      html: htmlBody,
      headers: {
        'X-Spam-Flag': flagged ? 'YES' : 'NO',
        'X-Spam-Score': String(verdict.score),
        'X-IKAD-Spam-Reasons': verdict.reasons.join('; ').slice(0, 900) || 'none',
      },
    });

    if (flagged) {
      console.warn('[quote] flagged as possible spam', { score: verdict.score, reasons: verdict.reasons, email, ip });
    }
    return res.status(200).json({ ok: true, id: info.messageId });
  } catch (err) {
    console.error('SMTP send error:', err);
    return res.status(502).json({ ok: false, error: 'Email could not be sent. Please call (905) 491-6943.' });
  }
}

function clientIp(req) {
  const fwd = req.headers['x-forwarded-for'];
  if (typeof fwd === 'string' && fwd) return fwd.split(',')[0].trim();
  if (Array.isArray(fwd) && fwd.length) return String(fwd[0]).split(',')[0].trim();
  return req.headers['x-real-ip'] || req.socket?.remoteAddress || '';
}
