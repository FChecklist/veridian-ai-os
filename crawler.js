const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const https = require('https');

const SNAPSHOT_DIR = '/opt/veridian/shared/spec-snapshot-20260817';
const BASE_URL = 'https://x1mw26zqhcr1-d.space-z.ai';

// Ensure snapshot directory exists
if (!fs.existsSync(SNAPSHOT_DIR)) {
  fs.mkdirSync(SNAPSHOT_DIR, { recursive: true });
}

async function downloadFile(url, filename) {
  return new Promise((resolve, reject) => {
    const filepath = path.join(SNAPSHOT_DIR, filename);
    const file = fs.createWriteStream(filepath);

    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (response) => {
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        console.log(`Downloaded: ${filename}`);
        resolve(filepath);
      });
    }).on('error', reject);
  });
}

async function crawlApp() {
  console.log('Starting crawler...');
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Intercept and log all network requests
  const networkLog = [];
  page.on('response', async (response) => {
    try {
      const url = response.url();
      const status = response.status();
      const headers = response.headers();

      networkLog.push({
        url,
        status,
        method: 'GET',
        contentType: headers['content-type'] || 'unknown'
      });

      // Try to capture JSON responses
      if (headers['content-type']?.includes('application/json')) {
        try {
          const body = await response.json();
          const filename = url.replace(/[^a-z0-9]/gi, '_').substring(0, 100) + '.json';
          fs.writeFileSync(
            path.join(SNAPSHOT_DIR, filename),
            JSON.stringify(body, null, 2)
          );
          console.log(`Captured JSON: ${filename}`);
        } catch (e) {
          // Not valid JSON
        }
      }
    } catch (e) {
      // Ignore errors
    }
  });

  try {
    console.log('Loading main page...');
    await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

    // Get page content
    const content = await page.content();
    fs.writeFileSync(path.join(SNAPSHOT_DIR, 'index.html'), content);
    console.log('Saved main page HTML');

    // Extract all download links
    const links = await page.evaluate(() => {
      const anchors = document.querySelectorAll('a[href*="/api/download/"]');
      return Array.from(anchors).map(a => ({
        href: a.href,
        text: a.textContent.trim()
      }));
    });

    console.log(`Found ${links.length} download links`);

    // Download all phase files
    for (const link of links) {
      const filename = link.href.split('/').pop();
      try {
        await downloadFile(link.href, filename);
      } catch (e) {
        console.error(`Failed to download ${filename}:`, e.message);
      }
    }

    // Save network log
    fs.writeFileSync(
      path.join(SNAPSHOT_DIR, 'network-log.json'),
      JSON.stringify(networkLog, null, 2)
    );
    console.log('Saved network log');

  } catch (error) {
    console.error('Error during crawl:', error);
  } finally {
    await browser.close();
  }
}

crawlApp().then(() => {
  // Get snapshot size
  const files = fs.readdirSync(SNAPSHOT_DIR);
  let totalSize = 0;
  files.forEach(file => {
    const filepath = path.join(SNAPSHOT_DIR, file);
    const stats = fs.statSync(filepath);
    totalSize += stats.size;
  });

  console.log(`\nSnapshot complete!`);
  console.log(`Files: ${files.length}`);
  console.log(`Total size: ${(totalSize / 1024 / 1024).toFixed(2)} MB`);
  process.exit(0);
}).catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
