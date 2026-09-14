import puppeteer from 'puppeteer-core';

const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  headless: 'new',
});

const page = await browser.newPage();
await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
await page.goto('http://127.0.0.1:4323/btx/', { waitUntil: 'networkidle2' });
await new Promise(r => setTimeout(r, 1500));

const result = await page.evaluate(() => {
  const body = document.body;
  const html = document.documentElement;
  const widest = [];
  document.querySelectorAll('*').forEach(el => {
    const rect = el.getBoundingClientRect();
    if (rect.right > 390 && rect.width > 50) {
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
});
console.log(JSON.stringify(result, null, 2));

await browser.close();