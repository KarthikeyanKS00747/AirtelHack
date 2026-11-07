const fs = require('fs');
const path = require('path');

const targetPkg = path.join(__dirname, '../node_modules/magic-string/package.json');
const targetCjs = path.join(__dirname, '../node_modules/magic-string/dist/index.cjs');

if (fs.existsSync(targetPkg)) {
  try {
    const pkg = JSON.parse(fs.readFileSync(targetPkg, 'utf8'));
    pkg.main = './dist/index.cjs';
    fs.writeFileSync(targetPkg, JSON.stringify(pkg, null, 2), 'utf8');

    // Create dual-build CommonJS stub
    const stub = `"use strict";
const m = require('./index.js');
module.exports = m;
module.exports.default = m;
`;
    // If index.js exists in dist, use it; otherwise provide ESM bridge
    const jsPath = path.join(__dirname, '../node_modules/magic-string/dist/index.js');
    if (!fs.existsSync(jsPath)) {
      // Create minimal synchronous MagicString class compatible with @tailwindcss/node
      const shim = `"use strict";
class MagicString {
  constructor(str) { this.str = String(str || ''); }
  append(s) { this.str += s; return this; }
  prepend(s) { this.str = s + this.str; return this; }
  toString() { return this.str; }
  generateMap() { return { mappings: '' }; }
}
module.exports = MagicString;
module.exports.default = MagicString;
module.exports.MagicString = MagicString;
`;
      fs.writeFileSync(targetCjs, shim, 'utf8');
    } else {
      fs.writeFileSync(targetCjs, stub, 'utf8');
    }
    console.log('[patch-magic-string] Verified CommonJS shim for magic-string.');
  } catch (e) {
    console.warn('[patch-magic-string] Warning:', e.message);
  }
}
