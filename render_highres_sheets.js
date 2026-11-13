const path = require('path');
const puppeteer = require('C:\\Users\\Habib\\AppData\\Roaming\\npm\\node_modules\\puppeteer');

(async () => {
  const outDir = 'C:\\Users\\Habib\\Desktop\\شقتي';
  const htmlPath = 'file:///' + path.join(outDir, 'Zedan_Apartment_2D_3D_Studio.html').replace(/\\/g, '/');

  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1800, height: 1200, deviceScaleFactor: 2 });

  const jobs = [
    { mode: 'blueprint', file: 'FloorPlan_2D_Engineering_Blueprint.png' },
    { mode: 'colored',   file: 'FloorPlan_2D_Luxury_Colored.png' },
    { mode: '3d',        file: 'Apartment_3D_Isometric_Render.png' }
  ];

  for (const job of jobs) {
    const url = `${htmlPath}?mode=${job.mode}&capture=1`;
    await page.goto(url, { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 400));
    const dest = path.join(outDir, job.file);
    await page.screenshot({ path: dest, fullPage: false });
    console.log('Rendered:', dest);
  }

  await browser.close();
  console.log('ALL HIGH-RES SHEETS RENDERED SUCCESSFULLY');
})();
