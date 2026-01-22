import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });

await page.goto('https://ibanista-tools.vercel.app');
await page.waitForTimeout(2000);

// Screenshot before
await page.screenshot({ path: '/tmp/calc-before.png' });
console.log('Before click screenshot saved');

// Click the Calculate button
await page.click('button:has-text("Calculate My Budget")');
await page.waitForTimeout(1500);

// Screenshot after - should show results
await page.screenshot({ path: '/tmp/calc-after.png' });
console.log('After click screenshot saved');

await browser.close();
