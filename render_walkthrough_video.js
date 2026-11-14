const puppeteer = require('C:\\Users\\Habib\\AppData\\Roaming\\npm\\node_modules\\puppeteer');
const fs = require('fs');
const path = require('path');
const os = require('os');

(async () => {
  const framesDir = path.join(os.tmpdir(), 'walk_frames');
  fs.mkdirSync(framesDir, { recursive: true });
  for (const f of fs.readdirSync(framesDir)) {
    fs.unlinkSync(path.join(framesDir, f));
  }

  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-gpu-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: 1 });

  const url = 'file:///' + path.resolve('C:\\Users\\Habib\\Desktop\\شقتي\\Zedan_Apartment_2D_3D_Studio.html').replace(/\\/g, '/') + '?mode=walk&capture=1&t=0';
  await page.goto(url, { waitUntil: 'networkidle0' });
  await page.addStyleTag({ content: 'aside { display: none !important; }' });
  await page.evaluate(() => { window.dispatchEvent(new Event('resize')); });
  await new Promise(r => setTimeout(r, 250));

  const totalFrames = 240;
  for (let i = 0; i < totalFrames; i++) {
    const t = i / (totalFrames - 1);
    await page.evaluate(val => new Promise(resolve => {
      window.setTourProgress(val);
      requestAnimationFrame(() => resolve());
    }), t);
    const framePath = path.join(framesDir, `frame_${String(i).padStart(4, '0')}.jpg`);
    await page.screenshot({ path: framePath, type: 'jpeg', quality: 90 });
  }

  await browser.close();
  console.log(`CAPTURED ${totalFrames} WALKTHROUGH FRAMES AT: ${framesDir}`);
})();
