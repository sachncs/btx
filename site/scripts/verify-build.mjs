import { readFile, readdir } from 'node:fs/promises';

const dist = new URL('../dist/', import.meta.url);
const htmlFiles = [];

async function collectHtml(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = new URL(entry.name, directory);
    if (entry.isDirectory()) await collectHtml(new URL(`${entry.name}/`, directory));
    else if (entry.name.endsWith('.html')) htmlFiles.push(path);
  }
}

await collectHtml(dist);
const documents = await Promise.all(htmlFiles.map(async (path) => ({ path, html: await readFile(path, 'utf8') })));
const html = documents.find(({ path }) => path.pathname.endsWith('/dist/index.html'))?.html;
if (!html) throw new Error('Built site is missing dist/index.html');
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

const requiredRoutes = ['docs/index.html', 'docs/getting-started/index.html', 'docs/api/index.html', 'docs/architecture/index.html', 'docs/testing/index.html', 'docs/changelog/index.html', 'docs/security/index.html', 'docs/contributing/index.html'];
for (const route of requiredRoutes) {
  if (!documents.some(({ path }) => path.pathname.endsWith(`/dist/${route}`))) {
    throw new Error(`Built site is missing standalone documentation route: ${route}`);
  }
}

for (const { path, html: page } of documents) {
  if (/href="[^"]*\.md(?:[#"]|$)/i.test(page) || /github\.com\/[^" ]+\/blob\/[^" ]+\/docs\//i.test(page)) {
    throw new Error(`Built page links to repository Markdown documentation: ${path.pathname}`);
  }
  for (const href of [...page.matchAll(/href="([^"]+)"/g)].map((match) => match[1])) {
    if (href.startsWith('/') && !href.startsWith('/btx')) {
      throw new Error(`Root-relative link is not compatible with the /btx base path: ${href}`);
    }
  }
}

console.log(`Site build content, standalone docs, and base-path checks passed (${documents.length} HTML files).`);
