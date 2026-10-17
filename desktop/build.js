// node build.js        -> copies ../game in and builds Windows + macOS apps into ../dist
// node build.js copy   -> only copies ../game in (used by `npm start`)
const fs = require('fs');
const path = require('path');

const src = path.join(__dirname, '..', 'game');
const dst = path.join(__dirname, 'game');
fs.rmSync(dst, { recursive: true, force: true });
fs.cpSync(src, dst, { recursive: true });
if (process.argv[2] === 'copy') process.exit(0);

const { packager } = require('@electron/packager');
const targets = [
  { platform: 'win32', arch: 'x64' },
  { platform: 'darwin', arch: 'x64' },
  { platform: 'darwin', arch: 'arm64' },
];
(async () => {
  for (const t of targets) {
    const out = await packager({
      dir: __dirname, name: 'SHADE', ...t, out: path.join(__dirname, '..', 'dist'), overwrite: true,
      ignore: [/^\/dist/, /^\/build\.js$/, /^\/node_modules\/(?!$)/], prune: true, appBundleId: 'com.teamshade.shade',
    });
    console.log('built', out.join(', '));
  }
})();
