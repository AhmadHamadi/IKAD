/* ==========================================================================
   IKAD Instant HVAC Estimator
   --------------------------------------------------------------------------
   A guided multi-step estimator that qualifies the homeowner, gates the
   result behind contact capture, then presents Good / Better / Best packages
   with financing, rebates and an appointment request.

   The page supplies campaign config via window.IKAD_ESTIMATOR before this
   file loads (headline copy, preset answers, active offer, lead source).

   Pricing is a *range*, deliberately. It anchors the conversation; the real
   number comes from the in-home assessment. Base ranges below match the
   published cost guides in /blog/ so the site never contradicts itself.
   ========================================================================== */
(function () {
  'use strict';

  var root = document.getElementById('estimator');
  if (!root) return;

  var CFG = window.IKAD_ESTIMATOR || {};
  // Namespaced per campaign: each landing page has its own presets, so sharing
  // one bucket would let a previous campaign's answers leak into this one.
  var STORE_KEY = 'ikad_est_v1_' + (CFG.campaign || 'general');

  /* ======================================================================
     Reference data
     ====================================================================== */

  /* Home size drives equipment sizing and a price factor. Ranges beat a
     free-text sq-ft box: less friction, and it stops the tool pretending
     it did a Manual J load calculation. */
  var SIZES = [
    { v: 'under-1500', label: 'Under 1,500 sq. ft.', factor: 0.90, tons: 2.0, btu: '60,000' },
    { v: '1500-2000', label: '1,500 – 2,000 sq. ft.', factor: 0.95, tons: 2.0, btu: '60,000' },
    { v: '2000-2500', label: '2,000 – 2,500 sq. ft.', factor: 1.00, tons: 2.5, btu: '80,000' },
    { v: '2500-3000', label: '2,500 – 3,000 sq. ft.', factor: 1.08, tons: 3.0, btu: '80,000' },
    { v: '3000-3500', label: '3,000 – 3,500 sq. ft.', factor: 1.16, tons: 3.5, btu: '100,000' },
    { v: '3500-4000', label: '3,500 – 4,000 sq. ft.', factor: 1.24, tons: 4.0, btu: '100,000' },
    { v: '4000-5000', label: '4,000 – 5,000 sq. ft.', factor: 1.35, tons: 4.0, btu: '120,000' },
    { v: '5000-plus', label: '5,000+ sq. ft.', factor: 1.55, tons: 5.0, btu: '120,000+' }
  ];

  var THERMOSTATS = {
    good: 'Honeywell programmable thermostat',
    better: 'ecobee3 lite smart thermostat',
    best: 'ecobee Smart Thermostat Premium'
  };

  var INSTALL_BASE = [
    'Removal and disposal of your existing equipment',
    'New equipment set, levelled and secured',
    'Electrical connections and disconnect',
    'Startup, commissioning and airflow check',
    'Full system test before we leave',
    'Manufacturer warranty registration filed for you'
  ];

  /* Equipment catalogue. Prices are installed, in CAD, at the 2,000–2,500
     sq. ft. baseline; the size factor scales them. Model families are York /
     Luxaire / Coleman lines IKAD actually installs — exact model is confirmed
     at the assessment, hence "or equivalent". */
  var CATALOG = {
    ac: {
      label: 'Air conditioner replacement',
      short: 'AC replacement',
      tiers: {
        good: {
          name: 'Essential Comfort', low: 3900, high: 4800,
          tagline: 'Dependable cooling at the lowest upfront investment.',
          bestFor: 'Homeowners on a tight budget, smaller homes, or planning to sell within a few years.',
          equipment: [{ t: 'Air Conditioner', m: 'York LX Series (YCG) or equivalent', s: '14.3 SEER2 · single-stage · {TONS} ton' }],
          warranty: ['10-year parts (registered)', '1-year IKAD labour', '10-year compressor'],
          ratings: { eff: 2, comf: 2, noise: 'Standard', stat: 'Programmable', hum: '—', filt: '1" standard', warr: '★★☆' }
        },
        better: {
          name: 'Enhanced Comfort', low: 5400, high: 6400,
          tagline: 'Two-stage cooling that runs longer and quieter, and pulls more humidity out.',
          bestFor: 'Most Halton homes. The best balance of comfort, efficiency and price.',
          equipment: [{ t: 'Air Conditioner', m: 'York Affinity (YXT) or equivalent', s: '17 SEER2 · two-stage · {TONS} ton' }],
          warranty: ['10-year parts (registered)', '2-year IKAD labour', '10-year compressor'],
          ratings: { eff: 3, comf: 3, noise: 'Low (as quiet as 68 dB)', stat: 'Smart / Wi-Fi', hum: 'Improved', filt: '4" media cabinet', warr: '★★★' }
        },
        best: {
          name: 'Ultimate Comfort', low: 6200, high: 8200,
          tagline: 'Variable-speed inverter cooling — the quietest, most efficient system we install.',
          bestFor: 'Tight or newer homes, comfort-focused owners, anyone staying put 10+ years.',
          equipment: [{ t: 'Air Conditioner', m: 'York Affinity (YXV) variable-speed or equivalent', s: 'Up to 20 SEER2 · inverter-driven · {TONS} ton' }],
          warranty: ['10-year parts (registered)', '3-year IKAD labour', '10-year compressor'],
          ratings: { eff: 5, comf: 5, noise: 'Ultra low (as quiet as 56 dB)', stat: 'Premium smart', hum: 'Precise', filt: '5" media cabinet', warr: '★★★★' }
        }
      }
    },

    furnace: {
      label: 'Furnace replacement',
      short: 'Furnace replacement',
      tiers: {
        good: {
          name: 'Essential Comfort', low: 3500, high: 4200,
          tagline: 'A reliable 95% single-stage furnace, professionally installed.',
          bestFor: 'Tight budgets, smaller homes, rental properties, or a short hold.',
          equipment: [{ t: 'Furnace', m: 'Coleman TG9S / TM9E or equivalent', s: '95–96% AFUE · single-stage · {BTU} BTU' }],
          warranty: ['10-year parts (registered)', '1-year IKAD labour', '20-year heat exchanger'],
          ratings: { eff: 2, comf: 2, noise: 'Standard', stat: 'Programmable', hum: '—', filt: '1" standard', warr: '★★☆' }
        },
        better: {
          name: 'Enhanced Comfort', low: 4800, high: 6200,
          tagline: 'Two-stage heat with a variable-speed ECM blower — even temperatures, lower hydro.',
          bestFor: 'Most homes. Fixes the "upstairs is freezing" complaint better than anything else at this price.',
          equipment: [{ t: 'Furnace', m: 'York LX TM9V / Affinity YC97C or equivalent', s: '96–97% AFUE · two-stage · variable-speed ECM · {BTU} BTU' }],
          warranty: ['10-year parts (registered)', '2-year IKAD labour', 'Lifetime heat exchanger'],
          ratings: { eff: 3, comf: 3, noise: 'Low', stat: 'Smart / Wi-Fi', hum: 'Optional bypass', filt: '4" media cabinet', warr: '★★★' }
        },
        best: {
          name: 'Ultimate Comfort', low: 6400, high: 7900,
          tagline: 'Fully modulating 98% AFUE — the furnace throttles from 35–100% instead of blasting on and off.',
          bestFor: 'Premium and very tight homes where quiet, steady heat matters most.',
          equipment: [{ t: 'Furnace', m: 'York Affinity YP9C modulating or equivalent', s: '98% AFUE · modulating · variable-speed ECM · {BTU} BTU' }],
          warranty: ['10-year parts (registered)', '3-year IKAD labour', 'Lifetime heat exchanger'],
          ratings: { eff: 5, comf: 5, noise: 'Ultra low', stat: 'Premium smart', hum: 'Steam/bypass included', filt: '5" media cabinet', warr: '★★★★' }
        }
      }
    },

    'ac-furnace': {
      label: 'Complete heating & cooling system',
      short: 'Furnace + AC',
      tiers: {
        good: {
          name: 'Essential Comfort', low: 6900, high: 8300,
          tagline: 'A matched furnace and AC pair at the lowest complete-system price.',
          bestFor: 'Replacing both at once on a budget — and never paying twice for labour.',
          equipment: [
            { t: 'Furnace', m: 'Coleman TM9E or equivalent', s: '96% AFUE · single-stage · {BTU} BTU' },
            { t: 'Air Conditioner', m: 'York LX Series (YCG) or equivalent', s: '14.3 SEER2 · single-stage · {TONS} ton' }
          ],
          warranty: ['10-year parts (registered)', '1-year IKAD labour', '20-year heat exchanger'],
          ratings: { eff: 2, comf: 2, noise: 'Standard', stat: 'Programmable', hum: '—', filt: '1" standard', warr: '★★☆' }
        },
        better: {
          name: 'Enhanced Comfort', low: 9400, high: 11800,
          tagline: 'Two-stage heat, two-stage cool, variable-speed blower — a properly matched system.',
          bestFor: 'Our most-installed package across Oakville, Burlington and Milton.',
          equipment: [
            { t: 'Furnace', m: 'York LX TM9V / Affinity YC97C or equivalent', s: '96–97% AFUE · two-stage · variable-speed ECM · {BTU} BTU' },
            { t: 'Air Conditioner', m: 'York Affinity (YXT) or equivalent', s: '17 SEER2 · two-stage · {TONS} ton' }
          ],
          warranty: ['10-year parts (registered)', '2-year IKAD labour', 'Lifetime heat exchanger'],
          ratings: { eff: 3, comf: 4, noise: 'Low', stat: 'Smart / Wi-Fi', hum: 'Bypass humidifier', filt: '4" media cabinet', warr: '★★★' }
        },
        best: {
          name: 'Ultimate Comfort', low: 12200, high: 15200,
          tagline: 'Modulating furnace paired with a variable-speed inverter AC. Nothing else comes close.',
          bestFor: 'Owners who want the quietest, most even, lowest-operating-cost system available.',
          equipment: [
            { t: 'Furnace', m: 'York Affinity YP9C modulating or equivalent', s: '98% AFUE · modulating · variable-speed ECM · {BTU} BTU' },
            { t: 'Air Conditioner', m: 'York Affinity (YXV) variable-speed or equivalent', s: 'Up to 20 SEER2 · inverter-driven · {TONS} ton' }
          ],
          warranty: ['10-year parts (registered)', '3-year IKAD labour', 'Lifetime heat exchanger'],
          ratings: { eff: 5, comf: 5, noise: 'Ultra low', stat: 'Premium smart', hum: 'Steam humidifier', filt: '5" media cabinet', warr: '★★★★' }
        }
      }
    },

    'heat-pump': {
      label: 'Cold-climate heat pump',
      short: 'Heat pump',
      rebateRate: 1250,
      tiers: {
        good: {
          name: 'Essential Electrify', low: 7500, high: 9500,
          tagline: 'An entry cold-climate heat pump that heats and cools from one system.',
          bestFor: 'Cutting gas use with the smallest upfront spend — and the largest rebate per dollar.',
          equipment: [{ t: 'Heat Pump', m: 'York LX (YHE) cold-climate or equivalent', s: '15 SEER2 · single-stage · {TONS} ton' }],
          warranty: ['10-year parts (registered)', '1-year IKAD labour', '10-year compressor'],
          ratings: { eff: 3, comf: 3, noise: 'Standard', stat: 'Smart / Wi-Fi', hum: '—', filt: '1" standard', warr: '★★☆' }
        },
        better: {
          name: 'Enhanced Electrify', low: 9500, high: 12000,
          tagline: 'Two-stage cold-climate heat pump holding capacity well below freezing.',
          bestFor: 'Standard forced-air Halton homes going electric with confidence.',
          equipment: [{ t: 'Heat Pump', m: 'York Affinity (YZT) cold-climate or equivalent', s: '17 SEER2 · two-stage · rated to -25°C · {TONS} ton' }],
          warranty: ['10-year parts (registered)', '2-year IKAD labour', '10-year compressor'],
          ratings: { eff: 4, comf: 4, noise: 'Low', stat: 'Smart / Wi-Fi', hum: 'Improved', filt: '4" media cabinet', warr: '★★★' }
        },
        best: {
          name: 'Ultimate Electrify', low: 11500, high: 14500,
          tagline: 'Variable-capacity inverter heat pump — maximum efficiency, maximum rebate.',
          bestFor: 'Full electrification with the highest HRS rebate and lowest running cost.',
          equipment: [{ t: 'Heat Pump', m: 'York Affinity (YZV) variable-capacity or Mitsubishi Hyper-Heat', s: 'Up to 20 SEER2 · inverter · rated to -30°C · {TONS} ton' }],
          warranty: ['10-year parts (registered)', '3-year IKAD labour', '10-year compressor'],
          ratings: { eff: 5, comf: 5, noise: 'Ultra low', stat: 'Premium smart', hum: 'Precise', filt: '5" media cabinet', warr: '★★★★' }
        }
      }
    },

    hybrid: {
      label: 'Hybrid system (heat pump + gas furnace)',
      short: 'Hybrid heat pump system',
      rebateRate: 500,
      tiers: {
        good: {
          name: 'Essential Hybrid', low: 11500, high: 13500,
          tagline: 'Heat pump does the shoulder seasons, the furnace covers the coldest nights.',
          bestFor: 'Cutting gas use 60–70% without giving up a gas backup.',
          equipment: [
            { t: 'Heat Pump', m: 'York LX (YHE) cold-climate or equivalent', s: '15 SEER2 · {TONS} ton' },
            { t: 'Backup Furnace', m: 'Coleman TM9E or equivalent', s: '96% AFUE · single-stage · {BTU} BTU' }
          ],
          warranty: ['10-year parts (registered)', '1-year IKAD labour', '20-year heat exchanger'],
          ratings: { eff: 3, comf: 3, noise: 'Standard', stat: 'Dual-fuel smart', hum: '—', filt: '1" standard', warr: '★★☆' }
        },
        better: {
          name: 'Enhanced Hybrid', low: 14000, high: 17000,
          tagline: 'Two-stage heat pump with a variable-speed furnace on true dual-fuel controls.',
          bestFor: 'The package most Halton homeowners land on once they see the rebate math.',
          equipment: [
            { t: 'Heat Pump', m: 'York Affinity (YZT) cold-climate or equivalent', s: '17 SEER2 · two-stage · {TONS} ton' },
            { t: 'Backup Furnace', m: 'York LX TM9V or equivalent', s: '96% AFUE · two-stage · variable-speed ECM · {BTU} BTU' }
          ],
          warranty: ['10-year parts (registered)', '2-year IKAD labour', 'Lifetime heat exchanger'],
          ratings: { eff: 4, comf: 4, noise: 'Low', stat: 'Dual-fuel smart', hum: 'Bypass humidifier', filt: '4" media cabinet', warr: '★★★' }
        },
        best: {
          name: 'Ultimate Hybrid', low: 16500, high: 20000,
          tagline: 'Inverter heat pump and modulating furnace, switching automatically on cost or temperature.',
          bestFor: 'Lowest possible operating cost with gas backup that never leaves you cold.',
          equipment: [
            { t: 'Heat Pump', m: 'York Affinity (YZV) variable-capacity or equivalent', s: 'Up to 20 SEER2 · inverter · {TONS} ton' },
            { t: 'Backup Furnace', m: 'York Affinity YP9C modulating or equivalent', s: '98% AFUE · modulating · {BTU} BTU' }
          ],
          warranty: ['10-year parts (registered)', '3-year IKAD labour', 'Lifetime heat exchanger'],
          ratings: { eff: 5, comf: 5, noise: 'Ultra low', stat: 'Premium dual-fuel', hum: 'Steam humidifier', filt: '5" media cabinet', warr: '★★★★' }
        }
      }
    },

    'new-home': {
      label: 'New home / custom build HVAC',
      short: 'New construction HVAC',
      custom: true,
      tiers: {
        good: {
          name: 'Builder Standard', low: 9500, high: 12500,
          tagline: 'Code-compliant forced-air package: furnace, AC, HRV and full duct design.',
          bestFor: 'Spec builds and secondary suites where budget leads.',
          equipment: [
            { t: 'Furnace', m: 'Coleman TM9E or equivalent', s: '96% AFUE · single-stage · {BTU} BTU' },
            { t: 'Air Conditioner', m: 'York LX Series (YCG) or equivalent', s: '14.3 SEER2 · {TONS} ton' },
            { t: 'Ventilation', m: 'Lifebreath HRV', s: 'Code-required ventilation' }
          ],
          warranty: ['10-year parts (registered)', '1-year IKAD labour', '20-year heat exchanger'],
          ratings: { eff: 2, comf: 2, noise: 'Standard', stat: 'Programmable', hum: '—', filt: '1" standard', warr: '★★☆' }
        },
        better: {
          name: 'Custom Comfort', low: 14000, high: 19000,
          tagline: 'Zoned two-stage system with engineered duct design and balanced airflow.',
          bestFor: 'Custom homes where every room should actually hit setpoint.',
          equipment: [
            { t: 'Furnace', m: 'York Affinity YC97C or equivalent', s: '97% AFUE · two-stage · variable-speed ECM · {BTU} BTU' },
            { t: 'Air Conditioner', m: 'York Affinity (YXT) or equivalent', s: '17 SEER2 · two-stage · {TONS} ton' },
            { t: 'Ventilation', m: 'Lifebreath HRV + zoning', s: 'Zoned dampers, engineered duct design' }
          ],
          warranty: ['10-year parts (registered)', '2-year IKAD labour', 'Lifetime heat exchanger'],
          ratings: { eff: 3, comf: 4, noise: 'Low', stat: 'Smart / Wi-Fi', hum: 'Bypass humidifier', filt: '4" media cabinet', warr: '★★★' }
        },
        best: {
          name: 'Signature Build', low: 22000, high: 38000,
          tagline: 'Modulating equipment, multi-zone control, in-floor hydronics and full air balancing.',
          bestFor: 'Estate builds and anything with a mechanical room worth showing off.',
          equipment: [
            { t: 'Heating', m: 'York Affinity YP9C modulating and/or hydronic in-floor', s: '98% AFUE · modulating · multi-zone' },
            { t: 'Cooling', m: 'York Affinity (YZV) variable-capacity', s: 'Up to 20 SEER2 · inverter · {TONS} ton' },
            { t: 'Air Quality', m: 'HRV, steam humidifier, 5" filtration', s: 'Certified air balancing report included' }
          ],
          warranty: ['10-year parts (registered)', '3-year IKAD labour', 'Lifetime heat exchanger'],
          ratings: { eff: 5, comf: 5, noise: 'Ultra low', stat: 'Multi-zone premium', hum: 'Steam humidifier', filt: '5" media cabinet', warr: '★★★★' }
        }
      }
    }
  };

  /* Tier-level perks layered on top of every package. A humidifier is only
     offered where we're actually touching heating equipment — on an AC-only
     swap the furnace stays put, so promising one would be a lie. */
  var HEATING_SYSTEMS = { furnace: 1, 'ac-furnace': 1, hybrid: 1, 'heat-pump': 1, 'new-home': 1 };

  function tierPerks(tierKey, catKey) {
    var perks = [];
    if (tierKey === 'good') return perks;
    perks.push('FREE duct cleaning with installation');
    if (tierKey === 'best') {
      if (HEATING_SYSTEMS[catKey]) perks.push('Whole-home humidifier included');
      perks.push('5" high-capacity filter cabinet');
    }
    return perks;
  }

  /* Financing: representative amortized terms. Real rate/term comes from the
     lender at approval — always labelled OAC. */
  var FINANCE = { apr: 0.0999, months: 120, promo: '6 months at 0% — no payments, no interest' };

  /* ======================================================================
     Question flow
     ====================================================================== */

  var STEPS = [
    {
      id: 'project', title: 'What are you looking for?',
      hint: 'Pick the closest match — you can tell us more in a moment.',
      options: [
        { v: 'cooling', e: '❄️', label: 'Cooling', sub: 'Air conditioning' },
        { v: 'heating', e: '🔥', label: 'Heating', sub: 'Furnace or boiler' },
        { v: 'both', e: '🌡️', label: 'Heating + Cooling', sub: 'Complete system' },
        { v: 'new-home', e: '🏠', label: 'New Home HVAC', sub: 'New build or full custom' }
      ]
    },
    {
      id: 'size', title: 'How large is your home?',
      hint: 'Above-grade living space. A close estimate is fine.',
      grid: 'tight',
      options: SIZES.map(function (s) { return { v: s.v, label: s.label }; })
    },
    {
      id: 'replacing', title: 'What are you replacing?',
      hint: 'Not sure what you have? That is completely normal — pick the last option.',
      skipIf: function (a) { return a.project === 'new-home'; },
      options: [
        { v: 'ac', e: '❄️', label: 'Air Conditioner' },
        { v: 'furnace', e: '🔥', label: 'Furnace' },
        { v: 'heat-pump', e: '♻️', label: 'Heat Pump' },
        { v: 'ac-furnace', e: '🌡️', label: 'AC + Furnace' },
        { v: 'complete', e: '🏡', label: 'Complete Heating & Cooling System' },
        { v: 'not-sure', e: '🤔', label: "I'm not sure" }
      ]
    },
    {
      id: 'age', title: 'How old is your current system?',
      hint: 'Most systems in Halton start failing between year 12 and year 18.',
      grid: 'tight',
      skipIf: function (a) { return a.project === 'new-home'; },
      options: [
        { v: '0-5', label: '0 – 5 years' },
        { v: '6-10', label: '6 – 10 years' },
        { v: '11-15', label: '11 – 15 years' },
        { v: '16-plus', label: '16+ years' },
        { v: 'unknown', label: 'Not sure' }
      ]
    },
    {
      id: 'reasons', title: "What's making you consider a new system?",
      hint: 'Select all that apply.', multi: true,
      options: [
        { v: 'not-cooling', e: '❄️', label: 'Not cooling properly' },
        { v: 'not-heating', e: '🔥', label: 'Not heating properly' },
        { v: 'bills', e: '💰', label: 'High energy bills' },
        { v: 'repairs', e: '🔧', label: 'Frequent repairs' },
        { v: 'old', e: '🕐', label: 'System is getting old' },
        { v: 'uneven', e: '🌡️', label: 'Uneven temperatures' },
        { v: 'noise', e: '🤫', label: 'Want something quieter' },
        { v: 'efficiency', e: '⚡', label: 'Want better efficiency' },
        { v: 'reno', e: '🏠', label: 'Renovating or adding on' },
        { v: 'exploring', e: '🔄', label: 'Just exploring my options' }
      ]
    },
    {
      id: 'priorities', title: 'What matters most to you?',
      hint: 'Choose up to two. We will lead with the package that fits.',
      multi: true, max: 2,
      options: [
        { v: 'price', label: 'Lowest upfront price' },
        { v: 'operating', label: 'Lower monthly energy costs' },
        { v: 'comfort', label: 'Maximum comfort' },
        { v: 'reliability', label: 'Reliability' },
        { v: 'efficiency', label: 'Best efficiency' },
        { v: 'premium', label: 'Premium system & features' }
      ]
    },
    {
      id: 'timeline', title: 'When would you like this done?',
      hint: 'This only decides how quickly we get back to you.',
      options: [
        { v: 'emergency', e: '🚨', label: 'Right away', sub: 'No heat / no cooling' },
        { v: '30-days', e: '📅', label: 'Within 30 days' },
        { v: '1-3-months', e: '🗓️', label: '1 – 3 months' },
        { v: 'researching', e: '🔍', label: 'Just researching' }
      ]
    },
    {
      id: 'financing', title: 'Would you like to see financing options?',
      hint: 'No credit check here — this only decides what we show you next.',
      options: [
        { v: 'yes', e: '💳', label: 'Yes, show me monthly payments' },
        { v: 'no', e: '💵', label: "No, I'll pay upfront" }
      ]
    },
    { id: 'contact', type: 'form', title: 'Almost there!' }
  ];

  /* ======================================================================
     State
     ====================================================================== */

  var state = {
    idx: 0,
    answers: {},
    contact: {},
    chosen: null,
    leadId: null,
    completed: false,
    startedAt: Date.now(),
    interacted: 0
  };

  /* Campaign presets answer questions the ad already answered, and those steps
     are skipped entirely — someone who clicked "replace your AC" should not be
     asked whether they want an AC. `startOver` below is the escape hatch for
     anyone who clicked the wrong ad. */
  state.skipped = [];
  if (CFG.preset) {
    for (var pk in CFG.preset) {
      if (!Object.prototype.hasOwnProperty.call(CFG.preset, pk)) continue;
      state.answers[pk] = CFG.preset[pk];
      if (STEPS.some(function (s) { return s.id === pk; })) state.skipped.push(pk);
    }
  }

  restore();

  /* ======================================================================
     Attribution — captured once, carried through to the lead email
     ====================================================================== */

  var tracking = (function () {
    var qs = new URLSearchParams(window.location.search);
    var t = {
      campaign_slug: CFG.campaign || 'general',
      landing_page: window.location.pathname,
      referrer: document.referrer || ''
    };
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'gclid', 'fbclid', 'ttclid', 'msclkid'].forEach(function (k) {
      var v = qs.get(k);
      if (v) t[k] = v.slice(0, 200);
    });
    if (!t.utm_source && CFG.defaultSource) t.utm_source = CFG.defaultSource;
    try {
      var saved = JSON.parse(sessionStorage.getItem(STORE_KEY + '_tracking') || 'null');
      if (saved) { for (var sk in saved) { if (!t[sk]) t[sk] = saved[sk]; } }
      sessionStorage.setItem(STORE_KEY + '_tracking', JSON.stringify(t));
    } catch (e) { /* private mode — attribution is best-effort */ }
    return t;
  })();

  /* ======================================================================
     Helpers
     ====================================================================== */

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function money(n) { return '$' + Math.round(n).toLocaleString('en-CA'); }

  /* Read a typed number back the way they'd expect to see it, so the
     confirmation doubles as a last chance to spot a wrong digit. */
  function prettyPhone(p) {
    var d = String(p == null ? '' : p).replace(/\D/g, '');
    if (d.length === 11 && d.charAt(0) === '1') d = d.slice(1);
    if (d.length === 10) return '(' + d.slice(0, 3) + ') ' + d.slice(3, 6) + '-' + d.slice(6);
    return p || 'you';
  }
  function roundTo(n, step) { return Math.round(n / step) * step; }

  function sizeInfo() {
    var found = null;
    SIZES.forEach(function (s) { if (s.v === state.answers.size) found = s; });
    return found || SIZES[2];
  }

  function activeSteps() {
    return STEPS.filter(function (s) {
      if (state.skipped.indexOf(s.id) > -1) return false;
      return !(s.skipIf && s.skipIf(state.answers));
    });
  }

  /* Drop the campaign presets and run the full question set from the top. */
  function startOver() {
    state.skipped = [];
    state.answers = {};
    state.chosen = null;
    state.idx = 0;
    save();
    render();
  }

  function save() {
    try {
      sessionStorage.setItem(STORE_KEY, JSON.stringify({
        idx: state.idx, answers: state.answers, contact: state.contact,
        chosen: state.chosen, leadId: state.leadId, skipped: state.skipped,
        completed: state.completed
      }));
    } catch (e) { /* non-fatal */ }
  }

  function restore() {
    try {
      var raw = sessionStorage.getItem(STORE_KEY);
      if (!raw) return;
      var d = JSON.parse(raw);
      if (!d || typeof d !== 'object') return;
      state.answers = Object.assign(state.answers, d.answers || {});
      if (Array.isArray(d.skipped)) state.skipped = d.skipped;
      state.contact = d.contact || {};
      state.chosen = d.chosen || null;
      state.leadId = d.leadId || null;
      state.completed = !!d.completed;
      state.idx = typeof d.idx === 'number' ? d.idx : 0;
    } catch (e) { /* start fresh */ }
  }

  function track(event, data) {
    try {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push(Object.assign({ event: event }, data || {}));
      if (typeof window.fbq === 'function') {
        var fbMap = { estimator_lead: 'Lead', estimator_booking: 'Schedule', estimator_start: 'InitiateCheckout' };
        if (fbMap[event]) window.fbq('track', fbMap[event], data || {});
      }
    } catch (e) { /* analytics must never break the funnel */ }
  }

  /* ======================================================================
     Pricing engine
     ====================================================================== */

  /* Map the homeowner's answers onto a catalogue key. Project type leads;
     an existing heat pump (or a heat-pump-shaped goal) upgrades the path. */
  function systemKey() {
    var a = state.answers;
    if (a.project === 'new-home') return 'new-home';

    var r = a.replacing;
    if (r === 'heat-pump') return a.project === 'cooling' ? 'heat-pump' : 'hybrid';
    if (r === 'ac-furnace' || r === 'complete') return 'ac-furnace';
    if (a.project === 'both') return 'ac-furnace';
    if (a.project === 'heating') return 'furnace';
    if (a.project === 'cooling') return 'ac';
    return 'ac-furnace';
  }

  /* The "Best" tier for a full-system replacement is a hybrid heat pump.
     It is genuinely the premium option here and it is the only one that
     unlocks the Home Renovation Savings rebate — so it earns the slot. */
  function upgradeBest(key) {
    if (key !== 'ac-furnace') return null;
    var a = state.answers;
    var wantsEff = (a.priorities || []).indexOf('efficiency') > -1 ||
      (a.priorities || []).indexOf('operating') > -1 ||
      (a.reasons || []).indexOf('bills') > -1 ||
      (a.reasons || []).indexOf('efficiency') > -1;
    return wantsEff ? 'hybrid' : null;
  }

  /* Which package gets the "Most Popular" flag. Defaults to Better, but a
     price-first homeowner sees Essential highlighted and a premium/comfort
     buyer sees Ultimate. Selling to their stated priority, not ours. */
  function featuredTier() {
    var p = state.answers.priorities || [];
    if (p.indexOf('premium') > -1) return 'best';
    if (p.indexOf('price') > -1 && p.indexOf('comfort') === -1) return 'good';
    if (p.indexOf('comfort') > -1 && p.indexOf('price') === -1) return 'best';
    return 'better';
  }

  function monthlyFrom(amount) {
    var r = FINANCE.apr / 12;
    var n = FINANCE.months;
    var pay = amount * r / (1 - Math.pow(1 + r, -n));
    return Math.ceil(pay);
  }

  /* HRS rebates scale with capacity for heat pump paths. Gas-only swaps get
     the thermostat rebate at best. Always presented as "estimated". */
  function rebateFor(tierKey, catKey) {
    var cat = CATALOG[catKey];
    var tons = sizeInfo().tons;
    var items = [];
    var total = 0;

    if (cat.rebateRate) {
      var equip = Math.min(Math.round(cat.rebateRate * tons), 7500);
      items.push({ label: 'Home Renovation Savings — heat pump (' + tons + ' ton)', value: equip });
      total += equip;
    }
    if (tierKey !== 'good') {
      items.push({ label: 'Smart thermostat rebate', value: 100 });
      total += 100;
    }
    if (catKey === 'ac-furnace' || catKey === 'furnace') {
      items.push({ label: 'Ask us about switching to a heat pump — up to $7,500', value: null });
    }
    return { items: items, total: total };
  }

  function buildPackages() {
    var key = systemKey();
    var bestKey = upgradeBest(key);
    var factor = sizeInfo().factor;
    var si = sizeInfo();
    var featured = featuredTier();
    var offer = CFG.offer || null;

    return ['good', 'better', 'best'].map(function (tierKey) {
      var catKey = (tierKey === 'best' && bestKey) ? bestKey : key;
      var cat = CATALOG[catKey];
      var t = cat.tiers[tierKey];

      var low = roundTo(t.low * factor, 50);
      var high = roundTo(t.high * factor, 50);

      var equipment = t.equipment.map(function (e) {
        return {
          t: e.t, m: e.m,
          s: e.s.replace('{TONS}', si.tons).replace('{BTU}', si.btu)
        };
      });

      var perks = tierPerks(tierKey, catKey);
      if (offer && (!offer.tiers || offer.tiers.indexOf(tierKey) > -1)) {
        // A campaign offer supersedes the equivalent standard perk — listing
        // free duct cleaning twice in one card reads as a mistake, not a deal.
        if (/duct clean/i.test(offer.label)) {
          perks = perks.filter(function (k) { return !/duct clean/i.test(k); });
        }
        if (perks.indexOf(offer.label) === -1) perks.unshift(offer.label);
      }

      return {
        tier: tierKey,
        tierLabel: tierKey === 'good' ? 'Good' : tierKey === 'better' ? 'Better' : 'Best',
        catKey: catKey,
        catLabel: cat.label,
        name: t.name,
        tagline: t.tagline,
        bestFor: t.bestFor,
        low: low, high: high,
        monthly: monthlyFrom(low),
        equipment: equipment,
        warranty: t.warranty,
        ratings: t.ratings,
        thermostat: THERMOSTATS[tierKey],
        perks: perks,
        rebate: rebateFor(tierKey, catKey),
        featured: tierKey === featured
      };
    });
  }

  /* ======================================================================
     Rendering — steps
     ====================================================================== */

  function render() {
    var steps = activeSteps();
    if (state.idx >= steps.length) { showLoading(); return; }
    var step = steps[state.idx];
    root.innerHTML = progressHtml(state.idx, steps.length) +
      (step.type === 'form' ? contactStepHtml(step) : optionStepHtml(step));
    wireStep(step);
    focusStep();
  }

  function progressHtml(i, total) {
    var pct = Math.round((i / total) * 100);
    return '<div class="est-progress">' +
      '<div class="est-progress__meta"><span>Step <strong>' + (i + 1) + '</strong> of ' + total + '</span>' +
      '<span>' + (i === 0 ? 'Takes about 60 seconds' : pct + '% complete') + '</span></div>' +
      '<div class="est-progress__track"><div class="est-progress__bar" style="width:' + Math.max(pct, 4) + '%"></div></div>' +
      '</div>';
  }

  function optionStepHtml(step) {
    var selected = state.answers[step.id];
    var isMulti = !!step.multi;
    var sel = isMulti ? (selected || []) : selected;

    var opts = step.options.map(function (o) {
      var on = isMulti ? sel.indexOf(o.v) > -1 : sel === o.v;
      var full = isMulti && step.max && sel.length >= step.max && !on;
      return '<button type="button" class="est-opt' + (on ? ' is-selected' : '') + (full ? ' is-disabled' : '') + '"' +
        ' data-value="' + esc(o.v) + '"' + (full ? ' aria-disabled="true"' : '') +
        ' aria-pressed="' + (on ? 'true' : 'false') + '">' +
        (o.e ? '<span class="est-opt__emoji" aria-hidden="true">' + o.e + '</span>' : '') +
        '<span class="est-opt__text"><span class="est-opt__label">' + esc(o.label) + '</span>' +
        (o.sub ? '<span class="est-opt__sub">' + esc(o.sub) + '</span>' : '') +
        '</span></button>';
    }).join('');

    var continueBtn = isMulti
      ? '<button type="button" class="btn btn--primary" data-act="next"' + (sel.length ? '' : ' disabled') + '>Continue</button>'
      : '<p class="est-nav__note">Tap an option to continue</p>';

    return '<div class="est-step">' +
      '<span class="est-step__eyebrow">' + esc(CFG.eyebrow || 'Instant Estimate') + '</span>' +
      '<h2>' + esc(step.title) + '</h2>' +
      '<p class="est-step__hint">' + esc(step.hint || '') + '</p>' +
      '<div class="est-options' + (step.grid === 'tight' ? ' est-options--tight' : '') + '" role="group" aria-label="' + esc(step.title) + '">' + opts + '</div>' +
      '<div class="est-nav">' + backControl() + continueBtn + '</div></div>';
  }

  /* At step 0 there is nothing to go back to — but on a campaign page there is
     something to correct, so the slot holds the "wrong ad" escape hatch. */
  function backControl() {
    if (state.idx > 0) return '<button type="button" class="est-back" data-act="back">&larr; Back</button>';
    if (state.skipped.length) {
      return '<button type="button" class="est-back" data-act="start-over">' +
        'Estimating for <strong>' + esc(CATALOG[systemKey()].short) + '</strong> — not what you need?</button>';
    }
    return '<span></span>';
  }

  function summaryHtml() {
    var a = state.answers;
    var si = sizeInfo();
    var cat = CATALOG[systemKey()];
    var rows = [
      ['Project', cat.short],
      ['Home size', si.label],
      ['System age', labelOf('age', a.age)],
      ['Timeline', labelOf('timeline', a.timeline)]
    ].filter(function (r) { return r[1]; });
    return '<div class="est-summary"><h3>Your answers so far</h3><dl>' +
      rows.map(function (r) { return '<dt>' + esc(r[0]) + '</dt><dd>' + esc(r[1]) + '</dd>'; }).join('') +
      '</dl></div>';
  }

  function labelOf(stepId, value) {
    if (!value) return '';
    var out = '';
    STEPS.forEach(function (s) {
      if (s.id !== stepId || !s.options) return;
      s.options.forEach(function (o) { if (o.v === value) out = o.label; });
    });
    return out;
  }

  function contactStepHtml(step) {
    var c = state.contact || {};
    return '<div class="est-step">' +
      '<span class="est-step__eyebrow">Last step</span>' +
      '<h2>' + esc(step.title) + '</h2>' +
      '<p class="est-step__hint">We\'ve matched three system options to your home. Tell us where to send them.</p>' +
      summaryHtml() +
      '<form class="est-form" id="est-contact" novalidate>' +
      '<div class="form__honeypot" aria-hidden="true">' +
      '<label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label>' +
      '<label>Company URL<input type="text" name="url" tabindex="-1" autocomplete="off"></label>' +
      '<label>Confirm email<input type="text" name="company_website" tabindex="-1" autocomplete="off"></label>' +
      '</div>' +
      '<div class="est-form__row">' +
      field('first_name', 'First name', 'text', 'given-name', c.first_name, true) +
      field('last_name', 'Last name', 'text', 'family-name', c.last_name, true) +
      '</div>' +
      '<div>' +
      '<label for="est-phone">Phone number *</label>' +
      '<input id="est-phone" name="phone" type="tel" inputmode="tel" autocomplete="off" placeholder="(905) 555-0123" value="' + esc(c.phone || '') + '" required>' +
      '<p class="est-field__err" data-err="phone" hidden></p>' +
      '</div>' +
      '<p class="est-phone-note"><span aria-hidden="true">📱</span><span>Please type your number rather than using autofill, and double-check it — this is how we send your estimate and confirm your appointment.</span></p>' +
      field('email', 'Email', 'email', 'email', c.email, true) +
      field('address', 'Property address', 'text', 'street-address', c.address, false, 'Street address (helps us confirm rebates)') +
      '<div class="est-form__row">' +
      cityField(c.city) +
      field('postal', 'Postal code', 'text', 'postal-code', c.postal, false, 'L6H 0C3') +
      '</div>' +
      '<button type="submit" class="btn btn--primary btn--large" style="width:100%;justify-content:center">See My Personalized Estimate &rarr;</button>' +
      '<p class="est-consent">By continuing you agree that IKAD Mechanical may contact you by phone, text or email about your estimate. No spam, and you can opt out any time. See our <a href="' + esc(CFG.rel || '../') + 'privacy-policy/">Privacy Policy</a>.</p>' +
      '</form>' +
      '<div class="est-nav"><button type="button" class="est-back" data-act="back">&larr; Back</button></div>' +
      '</div>';
  }

  function field(name, label, type, ac, value, required, placeholder) {
    return '<div>' +
      '<label for="est-' + name + '">' + esc(label) + (required ? ' *' : '') + '</label>' +
      '<input id="est-' + name + '" name="' + name + '" type="' + type + '" autocomplete="' + ac + '"' +
      (placeholder ? ' placeholder="' + esc(placeholder) + '"' : '') +
      ' value="' + esc(value || '') + '"' + (required ? ' required' : '') + '>' +
      '<p class="est-field__err" data-err="' + name + '" hidden></p>' +
      '</div>';
  }

  function cityField(value) {
    var cities = ['Oakville', 'Burlington', 'Milton', 'Halton Hills', 'Mississauga', 'Hamilton', 'Brampton', 'Other GTA'];
    return '<div><label for="est-city">City *</label><select id="est-city" name="city" required>' +
      '<option value="">Select your city</option>' +
      cities.map(function (c) { return '<option' + (value === c ? ' selected' : '') + '>' + c + '</option>'; }).join('') +
      '</select><p class="est-field__err" data-err="city" hidden></p></div>';
  }

  function focusStep() {
    var h = root.querySelector('.est-step h2');
    if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); }
    if (state.idx > 0) {
      var card = root.closest('.est-card') || root;
      var top = card.getBoundingClientRect().top + window.pageYOffset - 80;
      window.scrollTo({ top: top, behavior: 'smooth' });
    }
  }

  /* ======================================================================
     Step interaction
     ====================================================================== */

  function wireStep(step) {
    state.interacted = 1;

    root.querySelectorAll('[data-act="back"]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (state.idx > 0) { state.idx--; save(); render(); }
      });
    });

    root.querySelectorAll('[data-act="start-over"]').forEach(function (b) {
      b.addEventListener('click', startOver);
    });

    if (step.type === 'form') { wireContact(); return; }

    var nextBtn = root.querySelector('[data-act="next"]');

    root.querySelectorAll('.est-opt').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var v = btn.getAttribute('data-value');

        if (step.multi) {
          var cur = state.answers[step.id] || [];
          var at = cur.indexOf(v);
          if (at > -1) cur.splice(at, 1);
          else {
            if (step.max && cur.length >= step.max) return;
            cur.push(v);
          }
          state.answers[step.id] = cur;
          save();
          render();
          return;
        }

        state.answers[step.id] = v;
        if (state.idx === 0) track('estimator_start', { project: v });
        save();
        state.idx++;
        render();
      });
    });

    if (nextBtn) {
      nextBtn.addEventListener('click', function () {
        var cur = state.answers[step.id] || [];
        if (!cur.length) return;
        state.idx++;
        save();
        render();
      });
    }
  }

  function wireContact() {
    var form = root.querySelector('#est-contact');
    if (!form) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = String(v).trim(); });

      var errors = validate(data);
      form.querySelectorAll('.est-field__err').forEach(function (p) { p.hidden = true; p.textContent = ''; });
      form.querySelectorAll('[aria-invalid]').forEach(function (i) { i.removeAttribute('aria-invalid'); });

      var firstBad = null;
      Object.keys(errors).forEach(function (k) {
        var p = form.querySelector('[data-err="' + k + '"]');
        var input = form.querySelector('[name="' + k + '"]');
        if (p) { p.textContent = errors[k]; p.hidden = false; }
        if (input) { input.setAttribute('aria-invalid', 'true'); if (!firstBad) firstBad = input; }
      });
      if (firstBad) { firstBad.focus(); return; }

      state.contact = data;
      save();
      submitLead();
    });
  }

  function validate(d) {
    var e = {};
    if (!d.first_name) e.first_name = 'Please enter your first name.';
    if (!d.last_name) e.last_name = 'Please enter your last name.';
    if (!d.email) e.email = 'Please enter your email.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) e.email = 'That email address does not look right.';
    if (!d.city) e.city = 'Please choose your city.';

    var phoneErr = phoneError(d.phone);
    if (phoneErr) e.phone = phoneErr;
    return e;
  }

  /* Strict enough to catch a mistyped number, forgiving enough to accept the
     ways people actually write one: "+1 (905) 555-0123", "905-555-0123 x22",
     "1 905 555 0123". Rejecting an extension used to lose the lead outright. */
  function phoneError(raw) {
    var s = String(raw == null ? '' : raw).trim();
    if (!s) return 'Please enter your phone number.';

    // Split off a trailing extension before counting digits.
    var ext = s.match(/(?:e?xt?|extension|#)\.?\s*\d{1,6}\s*$/i);
    var main = ext ? s.slice(0, ext.index) : s;

    var digits = main.replace(/\D/g, '');
    if (digits.length === 11 && digits.charAt(0) === '1') digits = digits.slice(1);

    if (digits.length < 10) return 'Please enter a full 10-digit phone number.';
    if (digits.length > 10) return 'That phone number has too many digits — please check it.';
    if (/^(\d)\1{9}$/.test(digits)) return 'Please enter a real phone number.';
    // North American numbering: area code and exchange never start with 0 or 1.
    if (/^[01]/.test(digits) || /^[01]/.test(digits.slice(3))) {
      return 'Please check your phone number — that area code is not valid.';
    }
    return null;
  }

  /* ======================================================================
     Submission
     ====================================================================== */

  function showLoading() {
    root.innerHTML = '<div class="est-loading" role="status" aria-live="polite">' +
      '<div class="est-spinner" aria-hidden="true"></div>' +
      '<p>Matching systems to your home…</p></div>';
  }

  function payload(extra) {
    var packages = buildPackages();
    return Object.assign({
      stage: 'estimate',
      answers: state.answers,
      contact: state.contact,
      sizing: { label: sizeInfo().label, tons: sizeInfo().tons, btu: sizeInfo().btu },
      system: { key: systemKey(), label: CATALOG[systemKey()].label },
      packages: packages.map(function (p) {
        return { tier: p.tier, name: p.name, low: p.low, high: p.high, monthly: p.monthly, catLabel: p.catLabel };
      }),
      offer: CFG.offer ? CFG.offer.label : null,
      tracking: tracking,
      lead_id: state.leadId,
      form_elapsed_ms: Date.now() - state.startedAt,
      form_interacted: state.interacted
    }, extra || {});
  }

  function post(body) {
    return fetch('/api/estimate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    }).then(function (r) {
      return r.json().then(function (j) { return { ok: r.ok, body: j }; });
    });
  }

  function submitLead() {
    showLoading();
    var started = Date.now();

    post(payload()).then(function (res) {
      if (res.ok && res.body && res.body.ok) {
        state.leadId = res.body.lead_id || state.leadId;
        state.completed = true;
        save();
        track('estimator_lead', {
          value: buildPackages()[1].low,
          currency: 'CAD',
          campaign: tracking.campaign_slug
        });
      } else {
        // The lead email failed, but the homeowner still earned their estimate.
        // Show it anyway and surface a call-us fallback on the results page.
        state.sendError = (res.body && res.body.error) || null;
      }
    }).catch(function () {
      state.sendError = 'network';
    }).then(function () {
      // Hold the spinner briefly so the reveal reads as a calculation, not a flash.
      var wait = Math.max(0, 900 - (Date.now() - started));
      window.setTimeout(renderResults, wait);
    });
  }

  /* ======================================================================
     Rendering — results
     ====================================================================== */

  function renderResults() {
    var pkgs = buildPackages();
    var si = sizeInfo();
    var a = state.answers;
    var showFinancing = a.financing !== 'no';

    var html = '';

    html += '<div class="est-results">';

    /* Header */
    html += '<div class="est-results__head">' +
      '<h2>' + esc(state.contact.first_name || 'Your') + ', here are your ' + pkgs.length + ' system options</h2>' +
      '<p>Based on a ' + esc(si.label.toLowerCase()) + ' home in ' + esc(state.contact.city || 'your area') +
      '. Installed pricing — not equipment-only.</p>' +
      '<div class="est-results__spec">' +
      chip(CATALOG[systemKey()].label) +
      chip('Approx. ' + si.tons + ' ton') +
      (systemKey() !== 'ac' && systemKey() !== 'heat-pump' ? chip(si.btu + ' BTU') : '') +
      (a.age && a.age !== 'unknown' ? chip('Current system ' + labelOf('age', a.age).toLowerCase()) : '') +
      '</div></div>';

    if (CFG.offer) {
      html += '<div class="est-offer-banner">🎁 ' + esc(CFG.offer.bannerLabel || CFG.offer.label) + ' — applied to your estimate below</div>';
    }

    /* New construction can't be estimated from a size range the way a
       like-for-like swap can — there are no plans, no zone count and no
       hydronics decision yet. Say so plainly rather than implying precision. */
    if (CATALOG[systemKey()].custom) {
      html += '<div class="est-block" style="border-top:0;padding-bottom:0">' +
        '<p class="est-status est-status--error" style="background:#fffbeb;border-color:#fde68a;color:#78350f">' +
        '<strong>New construction works differently.</strong> The ranges below are what comparable builds in Halton ' +
        'typically land at. A real new-home number comes from your drawings — zone count, duct design, hydronics, ' +
        'HRV and ventilation requirements move it more than square footage does. Use this to set a budget, then send ' +
        'us your plans.</p></div>';
    }

    /* Packages */
    html += '<div class="est-packages">' + pkgs.map(function (p) { return packageHtml(p, showFinancing); }).join('') + '</div>';

    /* Compare */
    html += '<div class="est-block est-block--gray">' +
      '<h3>Compare your options</h3>' +
      '<p class="est-block__sub">The price difference is real, but so is what you get for it. Here it is side by side.</p>' +
      '<button type="button" class="est-toggle" data-act="toggle-compare" aria-expanded="false" aria-controls="est-compare">Compare Systems </button>' +
      '<div id="est-compare" hidden>' + compareHtml(pkgs) + '</div>' +
      '</div>';

    /* Full details */
    html += '<div class="est-block">' +
      '<h3>Full system details</h3>' +
      '<p class="est-block__sub">Exact equipment, installation scope and warranty for each package.</p>' +
      '<div class="est-details">' + pkgs.map(detailsHtml).join('') + '</div>' +
      '</div>';

    /* Financing */
    if (showFinancing) {
      var mid = pkgs[1];
      html += '<div class="est-block est-block--gray">' +
        '<h3>Make your new system affordable</h3>' +
        '<p class="est-block__sub">' + esc(FINANCE.promo) + ', then equal monthly payments. On approved credit.</p>' +
        '<div class="est-panel">' +
        '<div>' +
        '<ul class="est-rebate-list">' +
        // Names come from the packages themselves — hardcoding them meant the
        // heat pump and hybrid paths listed tiers the homeowner never saw.
        pkgs.map(function (p) {
          return '<li><span>' + esc(p.name) + '</span><b>from ' + money(p.monthly) + '/mo</b></li>';
        }).join('') +
        '</ul>' +
        '<p style="font-size:.82rem;color:#64748b;margin:0 0 1rem">Illustrated at ' + (FINANCE.apr * 100).toFixed(2) + '% over ' +
        (FINANCE.months / 12) + ' years on the low end of each range. Your actual rate, term and payment are set by the lender at approval.</p>' +
        '<button type="button" class="est-toggle" data-act="see-financing">See Financing Options</button>' +
        '</div>' +
        '<div class="est-figure"><span class="est-figure__label">Most popular package</span>' +
        '<span class="est-figure__value">' + money(mid.monthly) + '<small>/mo</small></span>' +
        '<p class="est-figure__note">' + esc(mid.name) + ' · OAC</p></div>' +
        '</div></div>';
    }

    /* Rebates */
    var reb = pkgs[featuredIndex(pkgs)].rebate;
    var maxReb = Math.max.apply(null, pkgs.map(function (p) { return p.rebate.total; }));
    html += '<div class="est-block">' +
      '<h3>You may qualify for rebates</h3>' +
      '<p class="est-block__sub">Estimated from your location, equipment type and efficiency. Final eligibility is set by the program, not by us — we file the paperwork either way.</p>' +
      '<div class="est-panel">' +
      '<div><ul class="est-rebate-list">' +
      (reb.items.length
        ? reb.items.map(function (i) {
            return '<li><span>' + esc(i.label) + '</span><b>' + (i.value == null ? 'Ask us' : money(i.value)) + '</b></li>';
          }).join('')
        : '<li><span>No equipment rebate applies to this system type in 2026</span><b>—</b></li>') +
      (maxReb > reb.total ? '<li><span>Upgrading to a heat pump package on this estimate</span><b>up to ' + money(maxReb) + '</b></li>' : '') +
      '</ul>' +
      '<p style="font-size:.82rem;color:#64748b;margin:0">Ontario\'s Home Renovation Savings Program and the Canada Greener Homes Loan are the two big ones in 2026. ' +
      '<a href="' + esc(CFG.rel || '../') + 'blog/ontario-heat-pump-rebates-2026/">Read our full 2026 rebate guide &rarr;</a></p></div>' +
      '<div class="est-figure est-figure--green"><span class="est-figure__label">Estimated available rebates</span>' +
      '<span class="est-figure__value">' + (maxReb > 0 ? '<small>up to</small> ' + money(maxReb) : money(0)) + '</span>' +
      '<p class="est-figure__note">Subject to program requirements &amp; confirmation</p></div>' +
      '</div></div>';

    /* What's included */
    html += '<div class="est-block est-block--gray">' +
      '<h3>Every price above is a complete installation</h3>' +
      '<p class="est-block__sub">You are not comparing a box. This is what IKAD hands over on the day we finish.</p>' +
      '<ul class="est-included">' +
      ['Equipment supplied by IKAD',
       'Licensed, insured, TSSA-certified installation',
       'Removal and disposal of your old equipment',
       'Refrigerant, line set connections and evacuation',
       'Electrical connections and disconnect',
       'Condensate drain work',
       'Gas piping and venting (where applicable)',
       'Startup, commissioning and airflow verification',
       'Full system testing before we leave',
       'Thermostat supplied and configured',
       'Manufacturer warranty registration filed for you',
       'IKAD workmanship warranty',
       'Permits pulled where required',
       'Rebate paperwork handled on your behalf'
      ].map(function (i) { return '<li>' + esc(i) + '</li>'; }).join('') +
      '</ul></div>';

    /* Social proof, then the final CTA + booking */
    html += socialProofHtml();
    html += finalCtaHtml();

    html += '</div>'; // .est-results

    root.innerHTML = html;
    wireResults();

    var card = root.closest('.est-card') || root;
    card.classList.add('est-card--wide');
    window.scrollTo({ top: card.getBoundingClientRect().top + window.pageYOffset - 70, behavior: 'smooth' });
    track('estimator_results', { campaign: tracking.campaign_slug });
  }

  function chip(text) { return '<span class="est-chip">' + esc(text) + '</span>'; }

  function featuredIndex(pkgs) {
    for (var i = 0; i < pkgs.length; i++) { if (pkgs[i].featured) return i; }
    return 1;
  }

  function packageHtml(p, showFinancing) {
    var chosen = state.chosen === p.tier;
    var lines = [];
    lines.push('Professional installation by licensed IKAD technicians');
    lines.push('Removal &amp; disposal of existing equipment');
    lines.push('Startup, commissioning &amp; system testing');
    lines.push(p.thermostat);
    lines.push(p.warranty[0] + ' · ' + p.warranty[1]);

    return '<article class="est-pkg' + (p.featured ? ' est-pkg--featured' : '') + (chosen ? ' is-chosen' : '') + '">' +
      // "Most Popular" is only true of the middle tier. When we promote a
      // different tier because of their stated priorities, say that instead.
      (chosen ? '<span class="est-pkg__flag">✓ Your pick</span>'
        : p.featured
          ? '<span class="est-pkg__flag">' + (p.tier === 'better' ? '★ Most Popular' : '★ Best Match For You') + '</span>'
          : '') +
      '<span class="est-pkg__tier">' + esc(p.tierLabel) + '</span>' +
      '<h4 class="est-pkg__name">' + esc(p.name) + '</h4>' +
      '<div class="est-pkg__price">' + money(p.low) + ' – ' + money(p.high) +
      '<small>installed · before rebates · HST extra</small></div>' +
      (showFinancing ? '<span class="est-pkg__mo">or from <em>' + money(p.monthly) + '/month</em> OAC</span>' : '') +
      '<div class="est-pkg__equip">' +
      p.equipment.map(function (e) {
        return '<div><strong>' + esc(e.t) + '</strong><span>' + esc(e.m) + '<br>' + esc(e.s) + '</span></div>';
      }).join('') +
      '</div>' +
      '<ul class="est-pkg__list">' +
      p.perks.map(function (k) { return '<li class="is-perk">' + esc(k) + '</li>'; }).join('') +
      lines.map(function (l) { return '<li>' + l + '</li>'; }).join('') +
      '</ul>' +
      '<p class="est-pkg__for"><strong>Best for:</strong> ' + esc(p.bestFor) + '</p>' +
      '<button type="button" class="btn ' + (p.featured ? 'btn--primary' : 'btn--secondary') + '" data-act="choose" data-tier="' + p.tier + '">' +
      (chosen ? 'Selected ✓' : 'Choose ' + esc(p.name.split(' ')[0])) + '</button>' +
      '</article>';
  }

  function dots(n) {
    var out = '';
    for (var i = 1; i <= 5; i++) out += i <= n ? '●' : '<span>●</span>';
    return '<span class="est-dots">' + out + '</span>';
  }

  function compareHtml(pkgs) {
    var rows = [
      ['Efficiency', function (p) { return dots(p.ratings.eff); }],
      ['Comfort & evenness', function (p) { return dots(p.ratings.comf); }],
      ['Noise level', function (p) { return esc(p.ratings.noise); }],
      ['Thermostat', function (p) { return esc(p.thermostat); }],
      ['Humidity control', function (p) { return esc(p.ratings.hum); }],
      ['Filter cabinet', function (p) { return esc(p.ratings.filt); }],
      ['Duct cleaning', function (p) {
        return p.perks.some(function (k) { return /duct clean/i.test(k); }) ? 'FREE' : '—';
      }],
      ['Warranty', function (p) { return esc(p.ratings.warr); }],
      ['Estimated rebates', function (p) { return p.rebate.total ? money(p.rebate.total) : '—'; }],
      ['Installed price', function (p) { return '<b>' + money(p.low) + ' – ' + money(p.high) + '</b>'; }],
      ['Monthly (OAC)', function (p) { return money(p.monthly) + '/mo'; }]
    ];

    return '<div class="est-compare-wrap"><table class="est-compare">' +
      '<thead><tr><th scope="col">&nbsp;</th>' +
      pkgs.map(function (p) { return '<th scope="col">' + esc(p.name) + '</th>'; }).join('') +
      '</tr></thead><tbody>' +
      rows.map(function (r) {
        return '<tr><th scope="row">' + esc(r[0]) + '</th>' +
          pkgs.map(function (p) { return '<td' + (p.featured ? ' class="is-featured"' : '') + '>' + r[1](p) + '</td>'; }).join('') +
          '</tr>';
      }).join('') +
      '</tbody></table></div>';
  }

  function detailsHtml(p) {
    return '<details><summary><span>' + esc(p.name) + ' — ' + money(p.low) + ' – ' + money(p.high) + '</span></summary>' +
      '<div class="est-details__body">' +
      '<h4>Equipment</h4><ul>' +
      p.equipment.map(function (e) { return '<li><strong>' + esc(e.t) + ':</strong> ' + esc(e.m) + ' — ' + esc(e.s) + '</li>'; }).join('') +
      '<li><strong>Thermostat:</strong> ' + esc(p.thermostat) + '</li>' +
      '</ul>' +
      '<h4>Installation</h4><ul>' + INSTALL_BASE.map(function (i) { return '<li>' + esc(i) + '</li>'; }).join('') + '</ul>' +
      '<h4>Warranty</h4><ul>' + p.warranty.map(function (w) { return '<li>' + esc(w) + '</li>'; }).join('') + '</ul>' +
      (p.perks.length ? '<h4>Included with this package</h4><ul>' + p.perks.map(function (k) { return '<li>' + esc(k) + '</li>'; }).join('') + '</ul>' : '') +
      '<h4>Why this tier</h4><ul><li>' + esc(p.tagline) + '</li><li>' + esc(p.bestFor) + '</li></ul>' +
      '</div></details>';
  }

  /* Trust signals stay factual and match what the rest of the site claims —
     certifications and brands installed, not a dealer status we can't back. */
  function socialProofHtml() {
    var badges = [
      'TSSA certified gas fitters',
      'ECRA / ESA licensed',
      'HRAI member',
      '$5M liability insured',
      'WSIB covered',
      'Financing available',
      'York · Luxaire · Coleman certified'
    ];
    return '<div class="est-block est-block--gray est-proof">' +
      '<h3 style="justify-content:center">Trusted by homeowners across the GTA</h3>' +
      '<div class="est-proof__rating">' +
      '<span class="est-proof__stars" aria-hidden="true">★★★★★</span>' +
      '<span><strong>5.0</strong> average on HomeStars &amp; Google</span>' +
      '</div>' +
      '<div class="est-proof__stats">' +
      '<div><span class="est-trust__num">1,200+</span><span class="est-trust__label">Homes &amp; businesses served</span></div>' +
      '<div><span class="est-trust__num">15+</span><span class="est-trust__label">Years serving Ontario homeowners</span></div>' +
      '<div><span class="est-trust__num">7</span><span class="est-trust__label">Cities across Halton, Peel &amp; Hamilton</span></div>' +
      '</div>' +
      '<div class="est-badges">' +
      badges.map(function (b) { return '<span class="est-badge">' + esc(b) + '</span>'; }).join('') +
      '</div></div>';
  }

  function finalCtaHtml() {
    var err = state.sendError
      ? '<p class="est-status est-status--error">We could not email your estimate automatically. Nothing is lost — call us at (905) 491-6943 and we will pull it up.</p>'
      : '';

    return '<div class="est-final">' +
      '<h3>Ready to see which system is right for your home?</h3>' +
      '<p>Your estimate is on its way to ' + esc(state.contact.email || 'your inbox') +
      '. The next step is a complimentary in-home assessment — we measure, check your ducts and electrical, and confirm the exact price.</p>' +
      '<div class="btn-row">' +
      '<button type="button" class="btn btn--primary btn--large" data-act="book">Book My Free Assessment</button>' +
      '<button type="button" class="btn btn--secondary btn--large" data-act="callback">Have an IKAD Expert Contact Me</button>' +
      '<a class="btn btn--outline btn--large" href="tel:+19054916943">Call (905) 491-6943</a>' +
      '</div>' +
      '<div data-callback-status></div>' +
      '<p class="est-final__resend">Want another copy? ' +
      '<button type="button" class="est-linkbtn" data-act="resend">Email my estimate again</button></p>' +
      '<div data-resend-status></div>' +
      err +
      '<div class="est-booking" id="est-booking" hidden>' +
      '<h4>When works best for you?</h4>' +
      '<div class="est-options est-options--tight" data-group="when">' +
      [['asap', 'As soon as possible'], ['this-week', 'This week'], ['next-week', 'Next week'], ['flexible', "I'm flexible"]]
        .map(function (o) {
          return '<button type="button" class="est-opt" data-when="' + o[0] + '" aria-pressed="false">' +
            '<span class="est-opt__text"><span class="est-opt__label">' + o[1] + '</span></span></button>';
        }).join('') +
      '</div>' +
      '<div style="margin-top:.85rem"><label for="est-window">Preferred time of day</label>' +
      '<select id="est-window" class="est-form" style="width:100%;padding:.8rem .9rem;border-radius:8px;border:1px solid #d1d5db;font:inherit">' +
      '<option>Morning (8am – 12pm)</option><option>Afternoon (12pm – 4pm)</option>' +
      '<option>Late afternoon (4pm – 6pm)</option><option>Saturday</option></select></div>' +
      '<button type="button" class="btn btn--primary" style="width:100%;justify-content:center;margin-top:1rem" data-act="confirm-booking">Request My Appointment</button>' +
      '<div data-booking-status></div>' +
      '</div>' +
      '<p style="font-size:.8rem;color:#94a3b8;margin:1.25rem 0 0">No obligation. No high-pressure sales. If replacing is not the right call, we will tell you.</p>' +
      '</div>';
  }

  /* ======================================================================
     Results interaction
     ====================================================================== */

  /* Only the package cards get re-rendered when a tier is chosen, so their
     listeners are wired separately. Re-running the full wiring would stack a
     second listener on every element that did NOT re-render — which meant a
     second "Request My Appointment" click sent the booking email twice. */
  function wirePackages() {
    root.querySelectorAll('[data-act="choose"]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var tier = btn.getAttribute('data-tier');
        state.chosen = state.chosen === tier ? null : tier;
        save();

        var wrap = root.querySelector('.est-packages');
        if (wrap) {
          wrap.innerHTML = buildPackages().map(function (p) {
            return packageHtml(p, state.answers.financing !== 'no');
          }).join('');
          wirePackages();
        }

        if (state.chosen) {
          track('estimator_select', { tier: tier });
          notifySelection(tier);
          var booking = root.querySelector('#est-booking');
          if (booking) {
            booking.hidden = false;
            booking.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }
      });
    });
  }

  function wireResults() {
    wirePackages();

    var toggle = root.querySelector('[data-act="toggle-compare"]');
    if (toggle) {
      toggle.addEventListener('click', function () {
        var panel = root.querySelector('#est-compare');
        var open = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', open ? 'false' : 'true');
        panel.hidden = open;
        if (!open) track('estimator_compare', {});
      });
    }

    /* "Have an IKAD expert contact me" — the lower-commitment sibling of
       booking, for someone who wants a human but not a calendar slot yet. */
    var callbackBtn = root.querySelector('[data-act="callback"]');
    if (callbackBtn) {
      callbackBtn.addEventListener('click', function () {
        var status = root.querySelector('[data-callback-status]');
        callbackBtn.disabled = true;
        callbackBtn.textContent = 'Sending…';
        post(payload({ stage: 'callback', chosen_tier: state.chosen })).then(function (res) {
          if (res.ok && res.body && res.body.ok) {
            track('estimator_callback', { tier: state.chosen });
            status.innerHTML = '<p class="est-status est-status--success">Done — an IKAD advisor will reach out to ' +
              esc(prettyPhone(state.contact.phone)) + ', usually within one business day. No appointment locked in yet.</p>';
            callbackBtn.textContent = 'Request sent ✓';
          } else {
            status.innerHTML = '<p class="est-status est-status--error">That did not go through. Please call (905) 491-6943.</p>';
            callbackBtn.disabled = false;
            callbackBtn.textContent = 'Have an IKAD Expert Contact Me';
          }
        }).catch(function () {
          status.innerHTML = '<p class="est-status est-status--error">Connection problem. Please call (905) 491-6943.</p>';
          callbackBtn.disabled = false;
          callbackBtn.textContent = 'Have an IKAD Expert Contact Me';
        });
      });
    }

    /* Resend only re-sends the homeowner's own copy — it must never put a
       second lead in the sales inbox. */
    var resendBtn = root.querySelector('[data-act="resend"]');
    if (resendBtn) {
      resendBtn.addEventListener('click', function () {
        var status = root.querySelector('[data-resend-status]');
        resendBtn.disabled = true;
        resendBtn.textContent = 'Sending…';
        post(payload({ stage: 'resend' })).then(function (res) {
          var okay = res.ok && res.body && res.body.ok;
          status.innerHTML = okay
            ? '<p class="est-status est-status--success">Sent again to ' + esc(state.contact.email) +
              '. If it is not there in a minute, check your junk folder.</p>'
            : '<p class="est-status est-status--error">Could not resend. Call (905) 491-6943 and we will read it to you.</p>';
          resendBtn.textContent = okay ? 'Sent ✓' : 'Email my estimate again';
          resendBtn.disabled = okay;
        }).catch(function () {
          status.innerHTML = '<p class="est-status est-status--error">Connection problem. Please call (905) 491-6943.</p>';
          resendBtn.disabled = false;
          resendBtn.textContent = 'Email my estimate again';
        });
      });
    }

    /* No lender pre-qualification URL is wired up yet, so this sends them to
       the human who can actually start an application. Swap for a direct link
       if the finance provider gives us a pre-qual page. */
    var financeBtn = root.querySelector('[data-act="see-financing"]');
    if (financeBtn) {
      financeBtn.addEventListener('click', function () {
        track('estimator_financing_cta', {});
        var target = root.querySelector('.est-final');
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        var cb = root.querySelector('[data-act="callback"]');
        if (cb) cb.focus({ preventScroll: true });
      });
    }

    var bookBtn = root.querySelector('[data-act="book"]');
    if (bookBtn) {
      bookBtn.addEventListener('click', function () {
        var booking = root.querySelector('#est-booking');
        if (!booking) return;
        booking.hidden = false;
        booking.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
    }

    root.querySelectorAll('[data-when]').forEach(function (b) {
      b.addEventListener('click', function () {
        root.querySelectorAll('[data-when]').forEach(function (o) {
          o.classList.remove('is-selected');
          o.setAttribute('aria-pressed', 'false');
        });
        b.classList.add('is-selected');
        b.setAttribute('aria-pressed', 'true');
      });
    });

    var confirm = root.querySelector('[data-act="confirm-booking"]');
    if (confirm) {
      confirm.addEventListener('click', function () {
        var picked = root.querySelector('[data-when].is-selected');
        var when = picked ? picked.querySelector('.est-opt__label').textContent : 'Not specified';
        var windowSel = root.querySelector('#est-window');
        var status = root.querySelector('[data-booking-status]');

        confirm.disabled = true;
        confirm.textContent = 'Sending…';

        post(payload({
          stage: 'booking',
          chosen_tier: state.chosen,
          appointment: { preferred_day: when, preferred_window: windowSel ? windowSel.value : '' }
        })).then(function (res) {
          if (res.ok && res.body && res.body.ok) {
            track('estimator_booking', { tier: state.chosen });
            status.innerHTML = '<p class="est-status est-status--success">Got it — your assessment request is in. ' +
              'An IKAD advisor will call ' + esc(prettyPhone(state.contact.phone)) + ' to lock in the exact time, usually within one business day.</p>';
            confirm.textContent = 'Request sent ✓';
          } else {
            status.innerHTML = '<p class="est-status est-status--error">That did not go through. Please call us at (905) 491-6943 and we will book you in.</p>';
            confirm.disabled = false;
            confirm.textContent = 'Request My Appointment';
          }
        }).catch(function () {
          status.innerHTML = '<p class="est-status est-status--error">Connection problem. Please call (905) 491-6943 — we have your estimate on file.</p>';
          confirm.disabled = false;
          confirm.textContent = 'Request My Appointment';
        });
      });
    }
  }

  /* Fire-and-forget: tell sales which package the homeowner leaned toward.
     A failure here is invisible on purpose — the lead is already captured. */
  function notifySelection(tier) {
    post(payload({ stage: 'selection', chosen_tier: tier })).catch(function () {});
  }

  /* ======================================================================
     Boot

     A reload after completion goes straight back to the results. Re-running
     submitLead() would post the same lead a second time and land a duplicate
     in the sales inbox.
     ====================================================================== */

  if (state.completed && state.contact && state.contact.email) renderResults();
  else render();
})();
