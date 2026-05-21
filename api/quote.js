// Vercel serverless function: POST /api/quote
// Receives quote-request form submissions and emails them via SMTP (nodemailer).
//
// Required environment variables (set in Vercel project settings AND in local .env):
//   SMTP_HOST   - e.g. mail.clinimedia.ca
//   SMTP_PORT   - e.g. 465 (SSL) or 587 (STARTTLS)
//   SMTP_USER   - SMTP login user (the address that will appear in From if QUOTE_FROM_EMAIL is unset)
//   SMTP_PASS   - SMTP password
//
// Optional environment variables (with sensible defaults):
//   QUOTE_TO_EMAIL       - destination address (default: info@ikad.ca)
//   QUOTE_FROM_EMAIL     - sender header (default: "IKAD Mechanical <SMTP_USER>")
//   QUOTE_SUBJECT_PREFIX - subject prefix (default: [IKAD Quote])

import nodemailer from 'nodemailer';

const TO_EMAIL = process.env.QUOTE_TO_EMAIL || 'info@ikad.ca';
const SUBJECT_PREFIX = process.env.QUOTE_SUBJECT_PREFIX || '[IKAD Quote]';

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

  // Honeypot: any value in `website` means bot — pretend success and drop.
  if (trim(body.website)) {
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
  const subject = `${SUBJECT_PREFIX} ${service || 'New quote'} — ${name}${city ? ' (' + city + ')' : ''}`;

  const textBody = [
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
  ].filter(Boolean).join('\n');

  const htmlBody = `
    <div style="font-family:Arial,Helvetica,sans-serif;color:#111;max-width:560px">
      <h2 style="color:#e30613;margin:0 0 1rem">New quote request from ikad.ca</h2>
      <table style="border-collapse:collapse;width:100%;font-size:14px">
        <tr><td style="padding:6px 8px;background:#f6f7f9;width:120px"><strong>Name</strong></td><td style="padding:6px 8px">${escapeHtml(name)}</td></tr>
        <tr><td style="padding:6px 8px;background:#f6f7f9"><strong>Phone</strong></td><td style="padding:6px 8px"><a href="tel:${escapeHtml(phone)}">${escapeHtml(phone)}</a></td></tr>
        <tr><td style="padding:6px 8px;background:#f6f7f9"><strong>Email</strong></td><td style="padding:6px 8px"><a href="mailto:${escapeHtml(email)}">${escapeHtml(email)}</a></td></tr>
        <tr><td style="padding:6px 8px;background:#f6f7f9"><strong>City</strong></td><td style="padding:6px 8px">${escapeHtml(city) || '<em>not given</em>'}</td></tr>
        <tr><td style="padding:6px 8px;background:#f6f7f9"><strong>Service</strong></td><td style="padding:6px 8px">${escapeHtml(service) || '<em>not given</em>'}</td></tr>
        ${sourcePage ? `<tr><td style="padding:6px 8px;background:#f6f7f9"><strong>Page</strong></td><td style="padding:6px 8px">${escapeHtml(sourcePage)}</td></tr>` : ''}
      </table>
      ${message ? `<p style="margin-top:1rem"><strong>Message:</strong></p><p style="background:#f6f7f9;padding:1rem;border-left:3px solid #e30613;white-space:pre-wrap">${escapeHtml(message)}</p>` : ''}
      <p style="color:#64748b;font-size:12px;margin-top:2rem">Submitted via the IKAD Mechanical website quote form.</p>
    </div>
  `;

  try {
    const info = await transporter.sendMail({
      from: fromHeader,
      to: TO_EMAIL,
      replyTo: email,
      subject,
      text: textBody,
      html: htmlBody,
    });

    return res.status(200).json({ ok: true, id: info.messageId });
  } catch (err) {
    console.error('SMTP send error:', err);
    return res.status(502).json({ ok: false, error: 'Email could not be sent. Please call (905) 491-6943.' });
  }
}
