// Shared outbound mail transport for /api/quote and /api/estimate.
//
// Resend is used when RESEND_API_KEY is set; SMTP (nodemailer) stays as the
// fallback so a Resend outage, a bad key or a revoked domain cannot take the
// lead forms down.
//
// The From address is deliberately derived per-transport rather than passed in
// by the caller. Resend will only accept a sender on a verified domain, so if
// it inherited the SMTP From (SMTP_USER, a different domain) every send would
// be rejected. Keeping the two apart means the fallback path also gets the
// right sender automatically.
//
// Environment variables:
//   RESEND_API_KEY - Resend API key. Its presence is what enables Resend.
//   RESEND_FROM    - verified sender (default: IKAD Mechanical <info@tradeleadsmarketing.com>)
//   SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASS - fallback transport
//   QUOTE_FROM_EMAIL - From header for the SMTP path only (unchanged behaviour)

import nodemailer from 'nodemailer';

const RESEND_ENDPOINT = 'https://api.resend.com/emails';
const RESEND_FROM_DEFAULT = 'IKAD Mechanical <info@tradeleadsmarketing.com>';

export function resendConfigured() {
  return Boolean(process.env.RESEND_API_KEY);
}

export function smtpConfigured() {
  const { SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS } = process.env;
  return Boolean(SMTP_HOST && SMTP_PORT && SMTP_USER && SMTP_PASS);
}

/** 'resend' | 'smtp' | 'none' — which transport a send would use right now. */
export function mailerMode() {
  if (resendConfigured()) return 'resend';
  if (smtpConfigured()) return 'smtp';
  return 'none';
}

/** The From header for a given transport. Never share one across both. */
export function fromAddress(mode) {
  if (mode === 'resend') return process.env.RESEND_FROM || RESEND_FROM_DEFAULT;
  return process.env.QUOTE_FROM_EMAIL || `IKAD Mechanical <${process.env.SMTP_USER}>`;
}

const asList = (v) => (Array.isArray(v) ? v.filter(Boolean) : [v].filter(Boolean));

async function sendViaResend({ to, replyTo, subject, text, html, headers }) {
  const payload = {
    from: fromAddress('resend'),
    to: asList(to),          // real recipients, never bcc
    subject,
    html,
    text,
  };
  if (replyTo) payload.reply_to = replyTo;
  if (headers && Object.keys(headers).length) payload.headers = headers;

  const res = await fetch(RESEND_ENDPOINT, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  let body = {};
  try { body = await res.json(); } catch { /* non-JSON error page */ }

  if (!res.ok) {
    const detail = body && (body.message || body.name)
      ? `${body.name || 'error'}: ${body.message || ''}`
      : `HTTP ${res.status}`;
    throw new Error(`Resend rejected the send (${detail})`);
  }
  return { messageId: body.id, transport: 'resend' };
}

async function sendViaSmtp({ to, replyTo, subject, text, html, headers }) {
  const port = Number(process.env.SMTP_PORT);
  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port,
    secure: port === 465, // 465 = implicit TLS; 587 / others = STARTTLS
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
  });

  const info = await transporter.sendMail({
    from: fromAddress('smtp'),
    to,
    replyTo,
    subject,
    text,
    html,
    headers,
  });
  return { messageId: info.messageId, transport: 'smtp' };
}

/**
 * Send one email. Subject, html, text, to and replyTo are passed straight
 * through untouched — this module only decides how it is delivered.
 */
export async function sendMail({ to, replyTo, subject, text, html, headers }) {
  const mode = mailerMode();
  if (mode === 'none') throw new Error('No mail transport configured');

  if (mode === 'resend') {
    try {
      return await sendViaResend({ to, replyTo, subject, text, html, headers });
    } catch (err) {
      if (!smtpConfigured()) throw err;
      console.error('[mailer] Resend send failed, falling back to SMTP:', err.message);
      return await sendViaSmtp({ to, replyTo, subject, text, html, headers });
    }
  }

  return sendViaSmtp({ to, replyTo, subject, text, html, headers });
}
