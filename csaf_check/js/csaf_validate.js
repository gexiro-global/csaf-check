// csaf_validate.js - CSAF 2.0 validation bridge over @secvisogram/csaf-validator-lib (BSI).
//
// Usage: node csaf_validate.js <doc.json>
// Prints exactly one JSON line: {available, isValid, errors[], note}
//
// The library's export names have moved between releases (mandatoryTest vs mandatoryTests,
// top-level vs default export). This script accepts either shape and degrades to
// {available:false} rather than throwing, so a missing or renamed dependency downgrades the
// caller's quality gate instead of breaking it.
const fs = require('fs');

(async () => {
  const out = { available: false, isValid: null, errors: [], note: '' };
  try {
    const docPath = process.argv[2];
    if (!docPath) {
      out.note = 'no document path given';
      console.log(JSON.stringify(out));
      return;
    }
    const doc = JSON.parse(fs.readFileSync(docPath, 'utf-8'));

    let lib;
    try {
      lib = await import('@secvisogram/csaf-validator-lib');
    } catch (e) {
      out.note = 'csaf-validator-lib not installed: ' + (e && e.message ? e.message : e);
      console.log(JSON.stringify(out));
      return;
    }
    out.available = true;

    const validate = lib.validate || (lib.default && lib.default.validate);
    const tests =
      lib.mandatoryTest ||
      lib.mandatoryTests ||
      (lib.default && (lib.default.mandatoryTest || lib.default.mandatoryTests)) ||
      [];

    if (typeof validate !== 'function') {
      out.note = 'validate() not found in the library export; check the installed version';
      console.log(JSON.stringify(out));
      return;
    }

    const res = await validate(tests, doc);
    out.isValid = !!res.isValid;
    for (const t of res.tests || []) {
      for (const er of t.errors || []) {
        out.errors.push((t.name || 'test') + ': ' + (er.message || JSON.stringify(er)));
      }
    }
    console.log(JSON.stringify(out));
  } catch (e) {
    out.note = 'validation error: ' + (e && e.message ? e.message : e);
    console.log(JSON.stringify(out));
  }
})();
