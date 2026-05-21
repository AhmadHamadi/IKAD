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
    <div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#111;line-height:1.5">
      <p>New quote request from ikad.ca:</p>
      <p>
        <strong>Name:</strong> ${escapeHtml(name)}<br>
        <strong>Phone:</strong> ${escapeHtml(phone)}<br>
        <strong>Email:</strong> ${escapeHtml(email)}<br>
        <strong>City:</strong> ${escapeHtml(city) || '(not given)'}<br>
        <strong>Service:</strong> ${escapeHtml(service) || '(not given)'}${sourcePage ? `<br><strong>Page:</strong> ${escapeHtml(sourcePage)}` : ''}
      </p>
      ${message ? `<p><strong>Message:</strong><br>${escapeHtml(message).replace(/\n/g, '<br>')}</p>` : ''}
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
