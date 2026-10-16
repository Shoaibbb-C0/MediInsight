import { test, expect } from '@playwright/test';

// Real browser acceptance: requires the frontend and backend running locally.
const widths = [320, 360, 375, 390, 430, 768, 1024, 1280, 1440, 1920];
for (const width of widths) {
  test(`upload and navigation at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Add your report' })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.screenshot({ path: `test-results/upload-${width}.png`, fullPage: true });
    await page.getByRole('button', { name: 'Profile', exact: true }).click();
    await expect(page.getByLabel('Preferred Language')).toBeVisible();
    await page.screenshot({ path: `test-results/profile-${width}.png`, fullPage: true });
  });
}

test('explicit demo stays labelled and connects report, food preferences, and doctor states', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Example report · demo data' }).click();
  await expect(page.getByText('Step 1 of 2: A few questions about you')).toBeVisible();
  await page.getByRole('button', { name: 'Skip all questions' }).click();
  await expect(page.getByRole('heading', { name: /things need your attention/ })).toBeVisible();
  await expect(page.getByText('Example report · demo data')).toBeVisible();
  await page.getByRole('button', { name: 'Nutrition', exact: true }).filter({visible:true}).click();
  await expect(page.getByRole('heading', { name: 'Your 7-day food plan' }).first()).toBeVisible();
  await page.getByRole('button', { name: 'Doctors', exact: true }).filter({visible:true}).click();
  await expect(page.getByText(/Reservations are simulated/)).toBeVisible();
  await page.getByRole('button', { name: /Map View/ }).click();
  await expect(page.getByText(/embedded live map is not configured/)).toBeVisible();
});

test('unreadable real upload cannot become a successful synthetic report', async ({ page }) => {
  await page.goto('/');
  await page.route('**/api/v1/reports/upload', route => route.fulfill({status:503,body:'Unavailable'}));
  await page.getByRole('button', {name:'Upload a report',exact:true}).click();
  await page.locator('input[type=file]').setInputFiles({name:'synthetic-test.pdf',mimeType:'application/pdf',buffer:Buffer.from('%PDF-1.4 test')});
  await expect(page.getByRole('alert')).toContainText('No example measurements were substituted');
  await expect(page.getByRole('heading',{name:'Add your report'})).toBeVisible();
});
