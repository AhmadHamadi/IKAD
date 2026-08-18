// Vercel serverless function: POST /api/estimate
//
// Receives Instant HVAC Estimator submissions. Unlike /api/quote (a single
// contact form), this endpoint is called up to three times per homeowner:
//
//   stage: 'estimate'  - contact captured, estimate revealed  -> full lead email + homeowner copy
//   stage: 'selection' - they picked a Good/Better/Best tier  -> short update to sales
//   stage: 'booking'   - they requested an assessment         -> hot booking alert
//
// Every stage carries the same lead_id so the sales inbox threads together.
//
// Environment variables (SMTP_* are shared with /api/quote):
//   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS      - required
//   ESTIMATE_TO_EMAIL   - destination (falls back to QUOTE_TO_EMAIL)
//   QUOTE_FROM_EMAIL    - sender header
//   ESTIMATE_SEND_COPY  - "0" to stop emailing the homeowner their estimate
//   QUOTE_ALLOWED_HOSTS - comma-separated hosts the form may be submitted from

import nodemailer from 'nodemailer';
import { scoreSubmission, recordHit, FLAG_THRESHOLD } from './_spam.js';

const TO_EMAIL = process.env.ESTIMATE_TO_EMAIL || process.env.QUOTE_TO_EMAIL || 'Saifsabeeh.31@gmail.com';
const SPAM_TAG = process.env.QUOTE_SPAM_SUBJECT_TAG || '[SPAM?]';
const SEND_COPY = process.env.ESTIMATE_SEND_COPY !== '0';
const ALLOWED_HOSTS = (process.env.QUOTE_ALLOWED_HOSTS || 'ikad.ca,vercel.app,localhost')
  .split(',').map((h) => h.trim().toLowerCase()).filter(Boolean);

const PHONE = '(905) 491-6943';

const esc = (s) =>
  String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

const trim = (v, max = 200) => String(v ?? '').slice(0, max).trim();
const money = (n) => '$' + Math.round(n).toLocaleString('en-CA');

/* ---------------------------------------------------------------------------
   Answer labels — mirrors assets/js/estimator.js so the sales email reads in
   plain English instead of slugs.
   --------------------------------------------------------------------------- */

const LABELS = {
  project: {
    cooling: 'Cooling (AC)', heating: 'Heating (furnace)',
    both: 'Heating + Cooling', 'new-home': 'New home HVAC',
  },
  size: {
    'under-1500': 'Under 1,500 sq ft', '1500-2000': '1,500–2,000 sq ft',
    '2000-2500': '2,000–2,500 sq ft', '2500-3000': '2,500–3,000 sq ft',
    '3000-3500': '3,000–3,500 sq ft', '3500-4000': '3,500–4,000 sq ft',
    '4000-5000': '4,000–5,000 sq ft', '5000-plus': '5,000+ sq ft',
  },
  replacing: {
    ac: 'Air conditioner', furnace: 'Furnace', 'heat-pump': 'Heat pump',
    'ac-furnace': 'AC + furnace', complete: 'Complete system', 'not-sure': "Doesn't know",
  },
  age: {
    '0-5': '0–5 years', '6-10': '6–10 years', '11-15': '11–15 years',
    '16-plus': '16+ years', unknown: 'Not sure',
  },
  reasons: {
    'not-cooling': 'Not cooling properly', 'not-heating': 'Not heating properly',
    bills: 'High energy bills', repairs: 'Frequent repairs', old: 'System getting old',
    uneven: 'Uneven temperatures', noise: 'Wants quieter', efficiency: 'Wants efficiency',
    reno: 'Renovating', exploring: 'Just exploring',
  },
  priorities: {
    price: 'Lowest upfront price', operating: 'Lower energy costs', comfort: 'Maximum comfort',
    reliability: 'Reliability', efficiency: 'Best efficiency', premium: 'Premium features',
  },
  timeline: {
    emergency: 'RIGHT AWAY (no heat/cooling)', '30-days': 'Within 30 days',
    '1-3-months': '1–3 months', researching: 'Just researching',
  },
  financing: { yes: 'Interested in financing', no: 'Paying upfront' },
};

const label = (group, value) => LABELS[group]?.[value] || value || '(not given)';
const labelList = (group, values) =>
  Array.isArray(values) && values.length
    ? values.map((v) => label(group, v)).join(', ')
    : '(none selected)';

/* ---------------------------------------------------------------------------
   Lead scoring — buying intent, not spam. Computed here rather than in the
   browser so the sales team is reading one consistent scale.
   --------------------------------------------------------------------------- */

const AGE_POINTS = { '16-plus': 30, '11-15': 22, unknown: 12, '6-10': 10, '0-5': 2 };
const TIMELINE_POINTS = { emergency: 30, '30-days': 24, '1-3-months': 12, researching: 0 };
const REASON_POINTS = {
  'not-cooling': 18, 'not-heating': 18, repairs: 16, old: 10, bills: 8,
  reno: 6, uneven: 6, efficiency: 5, noise: 4, exploring: -18,
};

function scoreLead({ answers, contact, stage, chosenTier }) {
  let score = 0;
  const notes = [];

  const agePts = AGE_POINTS[answers.age] ?? 0;
  if (agePts) { score += agePts; if (agePts >= 22) notes.push('Aging system'); }

  const timePts = TIMELINE_POINTS[answers.timeline] ?? 0;
  score += timePts;
  if (timePts >= 24) notes.push('Urgent timeline');
  if (answers.timeline === 'researching') notes.push('Early-stage researcher');

  (answers.reasons || []).forEach((r) => {
    const pts = REASON_POINTS[r] ?? 0;
    score += pts;
    if (pts >= 16) notes.push(LABELS.reasons[r]);
  });

  if (answers.financing === 'yes') { score += 6; notes.push('Wants financing'); }
  if (trim(contact.address)) score += 8;
  if (chosenTier) { score += 12; notes.push(`Selected ${chosenTier} package`); }
  if (stage === 'booking') { score += 20; notes.push('REQUESTED APPOINTMENT'); }

  score = Math.max(0, Math.min(120, score));

  let flames = 1;
  if (score >= 80) flames = 5;
  else if (score >= 60) flames = 4;
  else if (score >= 40) flames = 3;
  else if (score >= 22) flames = 2;

  return { score, flames, notes: [...new Set(notes)] };
}

/* ------------------------------------------------------------------------- */

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

  const contact = body.contact && typeof body.contact === 'object' ? body.contact : {};

  // Honeypots live inside the contact form, so they arrive on the contact object.
  if (trim(contact.website) || trim(contact.url) || trim(contact.company_website)) {
    console.warn('[estimate] honeypot triggered — dropped', { ip: clientIp(req), email: trim(contact.email, 80) });
    return res.status(200).json({ ok: true, lead_id: newLeadId() });
  }

  const stage = ['estimate', 'selection', 'booking', 'callback', 'resend'].includes(body.stage)
    ? body.stage
    : 'estimate';

  const firstName = trim(contact.first_name, 80);
  const lastName = trim(contact.last_name, 80);
  const name = [firstName, lastName].filter(Boolean).join(' ');
  const phone = trim(contact.phone, 40);
  const email = trim(contact.email, 200);
  const city = trim(contact.city, 80);
  const address = trim(contact.address, 200);
  const postal = trim(contact.postal, 20);

  if (!firstName || !phone || !email) {
    return res.status(400).json({ ok: false, error: 'First name, phone, and email are required.' });
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ ok: false, error: 'Invalid email address.' });
  }
  const phoneErr = phoneError(phone);
  if (phoneErr) {
    return res.status(400).json({ ok: false, error: phoneErr });
  }

  const answers = body.answers && typeof body.answers === 'object' ? body.answers : {};
  const sizing = body.sizing && typeof body.sizing === 'object' ? body.sizing : {};
  const system = body.system && typeof body.system === 'object' ? body.system : {};
  const tracking = body.tracking && typeof body.tracking === 'object' ? body.tracking : {};
  const appointment = body.appointment && typeof body.appointment === 'object' ? body.appointment : {};
  const chosenTier = trim(body.chosen_tier, 20) || null;
  const offer = trim(body.offer, 120);
  const leadId = trim(body.lead_id, 40) || newLeadId();

  // Packages are echoed back from the browser purely so the emails can restate
  // what the homeowner actually saw. Clamped so a tampered payload can't put
  // silly numbers in an inbox.
  const packages = Array.isArray(body.packages)
    ? body.packages.slice(0, 3).map((p) => ({
        tier: trim(p?.tier, 20),
        name: trim(p?.name, 60),
        catLabel: trim(p?.catLabel, 80),
        low: clampMoney(p?.low),
        high: clampMoney(p?.high),
        monthly: clampMoney(p?.monthly, 5000),
      }))
    : [];

  /* ---------------- Spam scoring ---------------- */

  const ip = clientIp(req);
  const hits = recordHit(ip);
  const elapsedRaw = Number(body.form_elapsed_ms);
  const verdict = scoreSubmission(
    { name, phone, email, city, service: system.label || 'HVAC estimate', message: address },
    {
      elapsedMs: Number.isFinite(elapsedRaw) && elapsedRaw >= 0 ? elapsedRaw : null,
      interacted: body.form_interacted == null ? null : Number(body.form_interacted),
      origin: req.headers.origin,
      referer: req.headers.referer || req.headers.referrer,
      userAgent: req.headers['user-agent'],
      acceptLanguage: req.headers['accept-language'],
      ip,
      hits,
      allowedHosts: ALLOWED_HOSTS,
    }
  );

  if (verdict.isBlocked) {
    console.warn('[estimate] BLOCKED as spam', {
      score: verdict.score, reasons: verdict.reasons, ip, name, phone, email, city,
    });
    return res.status(200).json({ ok: true, lead_id: leadId });
  }

  /* ---------------- Lead scoring ---------------- */

  const lead = scoreLead({ answers, contact: { address }, stage, chosenTier });

  /* ---------------- Send ---------------- */

  const { SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS } = process.env;
  if (!SMTP_HOST || !SMTP_PORT || !SMTP_USER || !SMTP_PASS) {
    console.error('[estimate] SMTP env vars missing — lead logged only', {
      leadId, name, phone, email, city, address, answers, stage,
    });
    return res.status(500).json({ ok: false, error: `Email service unavailable. Please call ${PHONE}.` });
  }

  const port = Number(SMTP_PORT);
  const transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port,
    secure: port === 465,
    auth: { user: SMTP_USER, pass: SMTP_PASS },
  });

  const fromHeader = process.env.QUOTE_FROM_EMAIL || `IKAD Mechanical <${SMTP_USER}>`;
  const flagged = verdict.isSpam;
  const flames = '🔥'.repeat(lead.flames);

  const stageSubject = {
    estimate: `${flames} NEW HVAC LEAD`,
    selection: `⭐ PACKAGE SELECTED`,
    booking: `📅 APPOINTMENT REQUESTED`,
    callback: `📞 CALLBACK REQUESTED`,
  }[stage];

  const subject =
    `${flagged ? SPAM_TAG + ' ' : ''}${stageSubject} — ${name}` +
    `${city ? ` (${city})` : ''} · ${system.label || 'HVAC'}`;

  const chosenPkg = chosenTier ? packages.find((p) => p.tier === chosenTier) : null;

  // Fixed-width labels so the sales team can scan a column, not read prose.
  // Only `null` entries are dropped — '' is a deliberate blank spacer line.
  const f = (k, v) => `${(k + ':').padEnd(10)} ${v}`;

  const lines = [
    flagged ? `!! SUSPECTED SPAM — score ${verdict.score} (flag at ${FLAG_THRESHOLD})` : null,
    flagged ? verdict.reasons.map((r) => `   - ${r}`).join('\n') : null,
    flagged ? '' : null,
    `${stageSubject}   ${flames}  (lead score ${lead.score}/120)`,
    lead.notes.length ? `Signals: ${lead.notes.join(' · ')}` : null,
    '',
    f('Name', name),
    f('Phone', phone),
    f('Email', email),
    f('Address', [address, city, postal].filter(Boolean).join(', ') || '(not given)'),
    '',
    f('Project', label('project', answers.project)),
    f('Home size', `${label('size', answers.size)}${sizing.tons ? ` (~${sizing.tons} ton / ${sizing.btu} BTU)` : ''}`),
    f('Replacing', label('replacing', answers.replacing)),
    f('Age', label('age', answers.age)),
    f('Why', labelList('reasons', answers.reasons)),
    f('Priority', labelList('priorities', answers.priorities)),
    f('Timeline', label('timeline', answers.timeline)),
    f('Financing', label('financing', answers.financing)),
    offer ? f('Offer', offer) : null,
    '',
    `System shown: ${system.label || '(n/a)'}`,
    ...packages.map((p) => `  ${p.tier === chosenTier ? '>>' : '  '} ${p.name}: ${money(p.low)}–${money(p.high)} (${money(p.monthly)}/mo)`),
    chosenPkg ? '' : null,
    chosenPkg ? `SELECTED: ${chosenPkg.name} — ${money(chosenPkg.low)}–${money(chosenPkg.high)}` : null,
    stage === 'booking' ? '' : null,
    stage === 'booking'
      ? `APPOINTMENT: ${appointment.preferred_day || 'n/a'} · ${appointment.preferred_window || 'n/a'}`
      : null,
    '',
    f('Lead ID', leadId),
    f('Source', `${tracking.utm_source || 'direct'}${tracking.utm_campaign ? ` / ${tracking.utm_campaign}` : ''}`),
    f('Campaign', tracking.campaign_slug || 'general'),
    f('Landing', tracking.landing_page || '(n/a)'),
    tracking.fbclid ? f('fbclid', tracking.fbclid) : null,
    tracking.gclid ? f('gclid', tracking.gclid) : null,
    f('Referrer', tracking.referrer || '(none)'),
    f('Spam score', verdict.score),
    f('IP', ip || 'unknown'),
  ].filter((l) => l != null).join('\n');

  const html = salesHtml({
    stageSubject, flames, lead, flagged, verdict, name, phone, email,
    address, city, postal, answers, sizing, system, packages, chosenTier,
    chosenPkg, appointment, stage, offer, tracking, leadId, ip,
  });

  // "Resend" is the homeowner asking for their own copy again. It must never
  // drop a second lead in the sales inbox, so it skips the sales email
  // entirely and falls through to the homeowner copy below.
  if (stage === 'resend') {
    if (!packages.length) {
      return res.status(400).json({ ok: false, error: 'Nothing to resend.' });
    }
    try {
      await transporter.sendMail({
        from: fromHeader,
        to: email,
        replyTo: process.env.QUOTE_TO_EMAIL || 'info@ikad.ca',
        subject: `Your IKAD system estimate — ${system.label || 'HVAC'}`,
        text: homeownerText({ firstName, system, sizing, packages, offer }),
        html: homeownerHtml({ firstName, system, sizing, packages, offer }),
      });
    } catch (err) {
      console.error('[estimate] resend failed:', err);
      return res.status(502).json({ ok: false, error: `Email could not be sent. Please call ${PHONE}.` });
    }
    return res.status(200).json({ ok: true, lead_id: leadId });
  }

  try {
    await transporter.sendMail({
      from: fromHeader,
      to: TO_EMAIL,
      replyTo: email,
      subject,
      text: lines,
      html,
      headers: {
        'X-IKAD-Lead-Id': leadId,
        'X-IKAD-Lead-Score': String(lead.score),
        'X-IKAD-Stage': stage,
        'X-Spam-Flag': flagged ? 'YES' : 'NO',
        'X-Spam-Score': String(verdict.score),
      },
    });
  } catch (err) {
    console.error('[estimate] SMTP send error:', err);
    return res.status(502).json({ ok: false, error: `Email could not be sent. Please call ${PHONE}.` });
  }

  // Homeowner copy — only on the first stage, and never to a flagged lead.
  if (stage === 'estimate' && SEND_COPY && !flagged && packages.length) {
    try {
      await transporter.sendMail({
        from: fromHeader,
        to: email,
        replyTo: process.env.QUOTE_TO_EMAIL || 'info@ikad.ca',
        subject: `Your IKAD system estimate — ${system.label || 'HVAC'}`,
        text: homeownerText({ firstName, system, sizing, packages, offer }),
        html: homeownerHtml({ firstName, system, sizing, packages, offer }),
      });
    } catch (err) {
      // The lead is already safely in the sales inbox. Don't fail the request.
      console.error('[estimate] homeowner copy failed (lead was still delivered):', err);
    }
  }

  if (flagged) {
    console.warn('[estimate] flagged as possible spam', { score: verdict.score, reasons: verdict.reasons, email, ip });
  }

  return res.status(200).json({ ok: true, lead_id: leadId, lead_score: lead.score });
}

/* ---------------------------------------------------------------------------
   Email bodies
   --------------------------------------------------------------------------- */

function salesHtml(d) {
  const row = (k, v) =>
    `<tr><td style="padding:4px 12px 4px 0;color:#64748b;font-size:12px;white-space:nowrap">${esc(k)}</td>
         <td style="padding:4px 0;color:#0f172a;font-size:13px;font-weight:600">${esc(v)}</td></tr>`;

  const banner = d.flagged
    ? `<div style="background:#fef2f2;border:2px solid #dc2626;border-radius:6px;padding:12px;margin-bottom:16px">
         <p style="margin:0 0 6px;font-weight:bold;color:#b91c1c">⚠ SUSPECTED SPAM — score ${d.verdict.score}</p>
         <ul style="margin:0;padding-left:18px;color:#7f1d1d;font-size:12px">
           ${d.verdict.reasons.map((r) => `<li>${esc(r)}</li>`).join('')}
         </ul>
       </div>`
    : '';

  const pkgRows = d.packages
    .map((p) => {
      const picked = p.tier === d.chosenTier;
      return `<tr style="background:${picked ? '#f0fdf4' : '#fff'}">
        <td style="padding:8px 10px;border-bottom:1px solid #e5e7eb;font-weight:${picked ? 700 : 500}">
          ${picked ? '✅ ' : ''}${esc(p.name)}</td>
        <td style="padding:8px 10px;border-bottom:1px solid #e5e7eb;text-align:right">${money(p.low)} – ${money(p.high)}</td>
        <td style="padding:8px 10px;border-bottom:1px solid #e5e7eb;text-align:right;color:#64748b">${money(p.monthly)}/mo</td>
      </tr>`;
    })
    .join('');

  return `
  <div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#111;line-height:1.5;max-width:640px">
    ${banner}
    <div style="background:#0f172a;color:#fff;padding:16px 18px;border-radius:8px 8px 0 0">
      <p style="margin:0;font-size:18px;font-weight:bold">${esc(d.stageSubject)} ${d.flames}</p>
      <p style="margin:6px 0 0;color:#cbd5e1;font-size:13px">
        Lead score <strong style="color:#fff">${d.lead.score}/120</strong>
        ${d.lead.notes.length ? ' · ' + esc(d.lead.notes.join(' · ')) : ''}
      </p>
    </div>

    <div style="border:1px solid #e5e7eb;border-top:0;padding:16px 18px">
      <p style="margin:0 0 4px;font-size:20px;font-weight:bold;color:#0f172a">${esc(d.name)}</p>
      <p style="margin:0 0 14px;font-size:15px">
        <a href="tel:${esc(d.phone.replace(/[^\d+]/g, ''))}" style="color:#e30613;font-weight:bold;text-decoration:none">${esc(d.phone)}</a>
        &nbsp;·&nbsp; <a href="mailto:${esc(d.email)}" style="color:#0f172a">${esc(d.email)}</a>
      </p>
      <p style="margin:0 0 16px;color:#475569;font-size:13px">
        📍 ${esc([d.address, d.city, d.postal].filter(Boolean).join(', ') || 'Address not given')}
      </p>

      ${d.stage === 'booking' ? `
      <div style="background:#fef4f4;border-left:4px solid #e30613;padding:10px 12px;margin-bottom:16px">
        <strong style="color:#b91c1c">Appointment requested:</strong>
        ${esc(d.appointment.preferred_day || 'n/a')} · ${esc(d.appointment.preferred_window || 'n/a')}
      </div>` : ''}

      <table style="border-collapse:collapse;width:100%;margin-bottom:16px">
        ${row('Project', label('project', d.answers.project))}
        ${row('Home size', label('size', d.answers.size) + (d.sizing.tons ? ` (~${d.sizing.tons} ton / ${d.sizing.btu} BTU)` : ''))}
        ${row('Replacing', label('replacing', d.answers.replacing))}
        ${row('System age', label('age', d.answers.age))}
        ${row('Why replacing', labelList('reasons', d.answers.reasons))}
        ${row('Priorities', labelList('priorities', d.answers.priorities))}
        ${row('Timeline', label('timeline', d.answers.timeline))}
        ${row('Financing', label('financing', d.answers.financing))}
        ${d.offer ? row('Offer applied', d.offer) : ''}
      </table>

      <p style="margin:0 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8;font-weight:bold">
        Packages shown — ${esc(d.system.label || 'HVAC')}
      </p>
      <table style="border-collapse:collapse;width:100%;font-size:13px;margin-bottom:16px">${pkgRows}</table>

      <table style="border-collapse:collapse;width:100%;border-top:1px solid #e5e7eb;padding-top:8px">
        ${row('Lead ID', d.leadId)}
        ${row('Source', (d.tracking.utm_source || 'direct') + (d.tracking.utm_campaign ? ` / ${d.tracking.utm_campaign}` : ''))}
        ${row('Campaign', d.tracking.campaign_slug || 'general')}
        ${row('Landing page', d.tracking.landing_page || 'n/a')}
        ${d.tracking.fbclid ? row('fbclid', d.tracking.fbclid) : ''}
        ${d.tracking.gclid ? row('gclid', d.tracking.gclid) : ''}
        ${row('Referrer', d.tracking.referrer || 'none')}
        ${row('Spam score', String(d.verdict.score))}
        ${row('IP', d.ip || 'unknown')}
      </table>
    </div>
  </div>`;
}

function homeownerText({ firstName, system, sizing, packages, offer }) {
  return [
    `Hi ${firstName},`,
    '',
    `Thanks for using the IKAD Instant Estimator. Here are the ${system.label || 'system'} options we matched to your home${sizing.tons ? ` (approximately ${sizing.tons} ton)` : ''}:`,
    '',
    ...packages.map((p) => `  ${p.name}: ${money(p.low)} – ${money(p.high)} installed  (from ${money(p.monthly)}/month OAC)`),
    '',
    offer ? `Your offer: ${offer}` : '',
    '',
    'Every price above is a complete installation: equipment, licensed installation, removal and disposal of your old system, electrical and drain work, startup, commissioning, testing, thermostat and warranty registration. Prices are before rebates and HST.',
    '',
    'This is an estimate based on what you told us. Final equipment selection and installation pricing are confirmed after a free assessment of your home — we check ductwork, electrical, venting and load before anything is ordered.',
    '',
    `Questions, or ready to book? Call us at ${PHONE} or reply to this email.`,
    '',
    'IKAD Mechanical Inc.',
    '2275 Upper Middle Rd E, Suite 101, Oakville, ON L6H 0C3',
    'TSSA gas fitters · ECRA/ESA licensed · HRAI member',
  ].filter((l) => l !== '').join('\n');
}

function homeownerHtml({ firstName, system, sizing, packages, offer }) {
  const cards = packages
    .map(
      (p) => `
    <tr>
      <td style="padding:14px 16px;border:1px solid #e5e7eb;border-radius:8px;background:#fff">
        <div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#94a3b8;font-weight:bold">${esc(p.tier)}</div>
        <div style="font-size:17px;font-weight:bold;color:#0f172a;margin:2px 0 6px">${esc(p.name)}</div>
        <div style="font-size:20px;font-weight:bold;color:#e30613">${money(p.low)} – ${money(p.high)}</div>
        <div style="font-size:12px;color:#64748b">installed · before rebates · HST extra · from ${money(p.monthly)}/month OAC</div>
      </td>
    </tr>
    <tr><td style="height:10px"></td></tr>`
    )
    .join('');

  return `
  <div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#1f2937;line-height:1.6;max-width:600px;margin:0 auto">
    <div style="background:#0f172a;color:#fff;padding:22px 20px;border-radius:8px 8px 0 0">
      <p style="margin:0;font-size:20px;font-weight:bold;color:#fff">Your IKAD system estimate</p>
      <p style="margin:6px 0 0;color:#cbd5e1;font-size:14px">
        ${esc(system.label || 'HVAC system')}${sizing.tons ? ` · approx. ${esc(String(sizing.tons))} ton` : ''}
      </p>
    </div>

    <div style="border:1px solid #e5e7eb;border-top:0;padding:20px;background:#f8fafc">
      <p style="margin:0 0 16px">Hi ${esc(firstName)}, thanks for using our Instant Estimator. Here is what we matched to your home:</p>

      ${offer ? `<p style="margin:0 0 14px;background:#e30613;color:#fff;padding:10px 14px;border-radius:6px;font-weight:bold;text-align:center">🎁 ${esc(offer)}</p>` : ''}

      <table style="width:100%;border-collapse:separate;border-spacing:0">${cards}</table>

      <p style="margin:16px 0 8px;font-weight:bold;color:#0f172a">Every price above is a complete installation</p>
      <p style="margin:0 0 16px;font-size:14px;color:#475569">
        Equipment · licensed TSSA-certified installation · removal and disposal of your old system ·
        refrigerant and line connections · electrical · drain work · startup and commissioning ·
        full system testing · thermostat · manufacturer warranty registration · IKAD workmanship warranty.
      </p>

      <p style="margin:0 0 18px;font-size:13px;color:#64748b;background:#fff;border-left:4px solid #cbd5e1;padding:10px 14px">
        This estimate is based on the information you provided. Final equipment selection and installation
        pricing are confirmed following a free assessment of your home — we check ductwork, electrical,
        venting and heat loss before anything is ordered.
      </p>

      <p style="text-align:center;margin:0 0 8px">
        <a href="tel:+19054916943" style="display:inline-block;background:#e30613;color:#fff;text-decoration:none;font-weight:bold;padding:13px 26px;border-radius:6px">
          Call ${PHONE}
        </a>
      </p>
      <p style="text-align:center;margin:0;font-size:13px;color:#64748b">or simply reply to this email</p>
    </div>

    <div style="padding:16px 20px;font-size:12px;color:#94a3b8;text-align:center">
      IKAD Mechanical Inc. · 2275 Upper Middle Rd E, Suite 101, Oakville, ON L6H 0C3<br>
      TSSA gas fitters · ECRA/ESA licensed · HRAI member · Serving Halton, Peel &amp; Hamilton since 2010
    </div>
  </div>`;
}

/* ------------------------------------------------------------------------- */

/* Mirrors phoneError() in assets/js/estimator.js — keep the two in step, or a
   number the browser accepted will be rejected here and the lead is lost. */
function phoneError(raw) {
  const s = String(raw ?? '').trim();
  if (!s) return 'Please enter your phone number.';

  const ext = s.match(/(?:e?xt?|extension|#)\.?\s*\d{1,6}\s*$/i);
  const main = ext ? s.slice(0, ext.index) : s;

  let digits = main.replace(/\D/g, '');
  if (digits.length === 11 && digits.startsWith('1')) digits = digits.slice(1);

  if (digits.length < 10) return 'Please enter a full 10-digit phone number.';
  if (digits.length > 10) return 'That phone number has too many digits — please check it.';
  if (/^(\d)\1{9}$/.test(digits)) return 'Please enter a real phone number.';
  if (/^[01]/.test(digits) || /^[01]/.test(digits.slice(3))) {
    return 'Please check your phone number — that area code is not valid.';
  }
  return null;
}

function clampMoney(v, max = 200000) {
  const n = Number(v);
  if (!Number.isFinite(n) || n < 0) return 0;
  return Math.min(Math.round(n), max);
}

function newLeadId() {
  return 'IKAD-' + Math.random().toString(36).slice(2, 8).toUpperCase();
}

function clientIp(req) {
  const fwd = req.headers['x-forwarded-for'];
  if (typeof fwd === 'string' && fwd) return fwd.split(',')[0].trim();
  if (Array.isArray(fwd) && fwd.length) return String(fwd[0]).split(',')[0].trim();
  return req.headers['x-real-ip'] || req.socket?.remoteAddress || '';
}
