// Legge la pagina eventi di beartgallery.eu e tutte le pagine evento collegate,
// e ne stampa il testo. Il sito si costruisce con JavaScript: una semplice
// richiesta della pagina restituisce solo il titolo, serve un browser.
//
//   node comunicati-stampa/leggi-sito.js
//
// Lo usa Claude nelle sessioni cloud, dove Playwright è già installato.

const { chromium } = require('playwright');

const BASE = 'https://www.beartgallery.eu';
const PARTENZA = BASE + '/eventi';
const ESCLUSE = new Set([BASE + '/eventi', BASE + '/eventi/archivio']);

async function testo(page, url) {
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1500);
  const main = await page.$('main');
  return (main ? main.innerText() : page.innerText('body'));
}

async function linkEventi(page) {
  const href = await page.$$eval('a', as => as.map(a => a.href));
  return [...new Set(href)].filter(h => h.startsWith(BASE + '/eventi/') && !ESCLUSE.has(h));
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const visti = new Set();
  const coda = [PARTENZA];
  while (coda.length) {
    const url = coda.shift();
    if (visti.has(url)) continue;
    visti.add(url);
    const t = await testo(page, url);
    console.log('\n==================== ' + url + '\n');
    console.log(t.trim());
    for (const l of await linkEventi(page)) if (!visti.has(l)) coda.push(l);
  }
  await browser.close();
})().catch(e => { console.error(e.message); process.exit(1); });
