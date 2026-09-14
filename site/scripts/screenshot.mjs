import puppeteer from 'puppeteer-core';

const url = process.argv[2] || 'http://127.0.0.1:4325/btx/';
const out = process.argv[3] || '/tmp/btx-shots/puppeteer.png';
const width = parseInt(process.argv[4] || '1440', 10);
const height = parseInt(process.argv[5] || '900', 10);

const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
  headless: 'new',
});

const page = await browser.newPage();
await page.setViewport({ width, height, deviceScaleFactor: 1 });
await page.goto(url, { waitUntil: 'networkidle2' });
// Allow reveal animations to trigger by scrolling through the page
await page.evaluate(() => {
  document.querySelectorAll('.reveal').forEach(el => el.classList.add('is-visible'));
});
await new Promise(r => setTimeout(r, 500));

await page.screenshot({ path: out, fullPage: height > 2000 });
console.log(`Saved ${out} (${width}x${height})`);

await browser.close();