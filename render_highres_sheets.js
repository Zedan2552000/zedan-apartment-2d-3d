const path = require('path');
const puppeteer = require('C:\\Users\\Habib\\AppData\\Roaming\\npm\\node_modules\\puppeteer');

(async () => {
  const outDir = 'C:\\Users\\Habib\\Desktop\\شقتي';
  const htmlPath = 'file:///' + path.join(outDir, 'Zedan_Apartment_2D_3D_Studio.html').replace(/\\/g, '/');

  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--enable-webgl', '--ignore-gpu-blocklist']
  });

  const page = await browser.newPage();
  const pageErrors = [];
  page.on('pageerror', err => {
    console.error('PAGE_ERROR:', err.message);
    pageErrors.push(err.message);
  });
  await page.setViewport({ width: 1800, height: 1200, deviceScaleFactor: 2 });

  const jobs = [
    { mode: 'blueprint', query: '',                 file: 'FloorPlan_2D_Engineering_Blueprint.png' },
    { mode: 'colored',   query: '',                 file: 'FloorPlan_2D_Luxury_Colored.png' },
    { mode: '3d',        query: '&theme=daylight',  file: 'Apartment_3D_Isometric_Render.png' },
    { mode: 'walk',      query: '&t=0.05&theme=warm_real', file: 'Apartment_3D_Walkthrough_Interior.png' }
  ];

  for (const job of jobs) {
    const url = `${htmlPath}?mode=${job.mode}&capture=1${job.query}`;
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await new Promise(r => setTimeout(r, 750));
    const dest = path.join(outDir, job.file);
    await page.screenshot({ path: dest, fullPage: false });
    console.log('Rendered:', dest);
  }

  await browser.close();
  if (pageErrors.length > 0) {
    console.error('FAILED DUE TO PAGE ERRORS:', pageErrors);
    process.exit(1);
  }
  console.log('ALL HIGH-RES SHEETS RENDERED SUCCESSFULLY');
})();
