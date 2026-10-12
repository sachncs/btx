import { readFile } from 'node:fs/promises';

const html = await readFile(new URL('../dist/index.html', import.meta.url), 'utf8');
const required = [
  'Install from source',
  'git clone https://github.com/sachncs/btx.git',
  'Python 3.12+',
];

for (const marker of required) {
  if (!html.includes(marker)) {
    throw new Error(`Built site is missing required content: ${marker}`);
  }
}

if (/pypi\.org|pip install btx(?![.@])/i.test(html)) {
  throw new Error('Built site contains an active PyPI installation path');
}

for (const href of [...html.matchAll(/href="([^"]+)"/g)].map((match) => match[1])) {
  if (href.startsWith('/') && !href.startsWith('/btx')) {
    throw new Error(`Root-relative link is not compatible with the /btx base path: ${href}`);
  }
}

console.log('Site build content and base-path checks passed.');
