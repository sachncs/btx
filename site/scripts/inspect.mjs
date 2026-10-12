import puppeteer from 'puppeteer-core';

const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  headless: 'new',
});

const page = await browser.newPage();
const url = process.argv[2] || 'http://127.0.0.1:4321/btx/';
const width = Number.parseInt(process.argv[3] || '390', 10);
await page.setViewport({ width, height: 844, deviceScaleFactor: 1 });
await page.goto(url, { waitUntil: 'networkidle2' });
await new Promise(r => setTimeout(r, 1500));

const result = await page.evaluate((viewportWidth) => {
  const body = document.body;
  const html = document.documentElement;
  const widest = [];
  document.querySelectorAll('*').forEach(el => {
    const rect = el.getBoundingClientRect();
    const position = getComputedStyle(el).position;
    if (rect.right > viewportWidth && rect.width > 50 && !['absolute', 'fixed'].includes(position)) {
      widest.push({
        tag: el.tagName,
        cls: (el.className?.toString?.() || '').slice(0, 80),
        id: el.id,
        right: Math.round(rect.right),
        width: Math.round(rect.width),
      });
    }
  });
  return {
    scrollWidth: html.scrollWidth,
    clientWidth: html.clientWidth,
    bodyScroll: body.scrollWidth,
    offenders: widest.slice(0, 30),
  };
}, width);
console.log(JSON.stringify(result, null, 2));

await browser.close();
