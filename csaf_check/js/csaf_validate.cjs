// csaf_validate.cjs - CSAF 2.0 validation bridge over @secvisogram/csaf-validator-lib (BSI).
//
// Usage: node csaf_validate.cjs <doc.json>
// Prints exactly one JSON line: {available, isValid, errors[], note}
//
// Why .cjs: this file ships inside a Python package, so at runtime there is usually no
// package.json next to it and Node's module type would be ambiguous. The .cjs extension pins it
// to CommonJS regardless of what any surrounding project declares. The validator itself is ESM,
// which is why it is loaded through dynamic import() - that works from CommonJS.
//
// The library ships subpath exports only - there is no main entry, so a bare
// import('@secvisogram/csaf-validator-lib') fails with "No exports main defined". Its tests are
// exported as individually-named functions rather than an array. Both have moved between releases,
// so each import and each shape is attempted in turn, and any failure degrades to
// {available:false} instead of throwing - a missing or renamed dependency should downgrade the
// caller's quality gate, not break it.
//
// Verified against @secvisogram/csaf-validator-lib 2.1.1.

const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

const PKG = '@secvisogram/csaf-validator-lib';

// Node resolves a bare specifier by walking up from THIS file. When the package is installed
// into site-packages by pip, that walk never reaches the directory where the user ran
// `npm install`, so the bare specifier alone is not enough. Try the working directory and
// NODE_PATH as explicit roots too.
function candidatesFor(subpath) {
  const out = [PKG + subpath];
  const roots = [process.cwd(), ...(process.env.NODE_PATH || '').split(path.delimiter)];
  for (const root of roots) {
    if (!root) continue;
    const base = path.basename(root) === 'node_modules' ? root : path.join(root, 'node_modules');
    const full = path.join(base, PKG, subpath.replace(/^\//, ''));
    try {
      if (fs.existsSync(full)) out.push(pathToFileURL(full).href);
    } catch {
      /* unreadable root, skip */
    }
  }
  return out;
}

async function importFirst(specifiers) {
  for (const specifier of specifiers) {
    try {
      return await import(specifier);
    } catch {
      /* try the next candidate */
    }
  }
  return null;
}

function resolveValidate(mod) {
  if (!mod) return null;
  const candidates = [mod.validate, mod.default, mod.default && mod.default.validate];
  for (const candidate of candidates) {
    if (typeof candidate === 'function') return candidate;
  }
  return null;
}

function resolveTests(mod) {
  if (!mod) return [];
  // Older releases exported a single array; 2.x exports one named function per test.
  for (const candidate of [mod.mandatoryTests, mod.mandatoryTest, mod.default]) {
    if (Array.isArray(candidate)) return candidate;
  }
  const fns = Object.values(mod).filter((x) => typeof x === 'function');
  if (fns.length) return fns;
  if (mod.default && typeof mod.default === 'object') {
    return Object.values(mod.default).filter((x) => typeof x === 'function');
  }
  return [];
}

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

    const validateMod = await importFirst([
      ...candidatesFor('/validate.js'),
      PKG + '/validate',
      PKG,
    ]);
    const testsMod = await importFirst([
      ...candidatesFor('/mandatoryTests.js'),
      PKG + '/mandatoryTests',
      PKG,
    ]);

    if (!validateMod || !testsMod) {
      out.note =
        'csaf-validator-lib not installed or not resolvable: run ' +
        '`npm install @secvisogram/csaf-validator-lib`';
      console.log(JSON.stringify(out));
      return;
    }

    const validate = resolveValidate(validateMod);
    const tests = resolveTests(testsMod);

    if (typeof validate !== 'function') {
      out.note = 'validate() not found in the library export; check the installed version';
      console.log(JSON.stringify(out));
      return;
    }
    if (!tests.length) {
      // Guard against the silent-pass trap: validating against an empty test list returns
      // isValid:true for any document, which would report broken advisories as clean.
      out.note = 'no mandatory tests resolved from the library; refusing to report a verdict';
      console.log(JSON.stringify(out));
      return;
    }

    out.available = true;
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
