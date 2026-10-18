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
    await expect(page.getByRole('combobox',{name:'Preferred Language'})).toBeVisible();
    await page.screenshot({ path: `test-results/profile-${width}.png`, fullPage: true });
  });
}

test('explicit demo stays labelled and connects report, food preferences, and doctor states', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Example report · demo data' }).click();
  await expect(page.getByText(/Step 1 of \d+: A few questions about you/)).toBeVisible();
  await page.getByRole('button', { name: 'Skip all questions' }).click();
  await expect(page.getByRole('heading', { name: /things need your attention/ })).toBeVisible();
  await expect(page.getByText('Example report · demo data')).toBeVisible();
  await page.getByRole('button', { name: 'Nutrition', exact: true }).filter({visible:true}).click();
  await expect(page.getByRole('heading', { name: 'Your 7-day food plan' }).first()).toBeVisible();
  await page.getByRole('button', { name: 'Doctors', exact: true }).filter({visible:true}).click();
  await expect(page.getByText(/Demo provider — no real consultation availability/)).toBeVisible();
  await page.route('https://tiles.openfreemap.org/**', route => route.abort());
  await page.getByRole('button', { name: 'Map', exact: true }).click();
  await expect(page.getByText(/Map unavailable/)).toBeVisible();
});

test('unreadable real upload cannot become a successful synthetic report', async ({ page }) => {
  await page.goto('/');
  await page.route('**/api/v1/reports/upload', route => route.fulfill({status:503,body:'Unavailable'}));
  await page.getByRole('button', {name:'Upload a report',exact:true}).click();
  await page.locator('input[type=file]').setInputFiles({name:'synthetic-test.pdf',mimeType:'application/pdf',buffer:Buffer.from('%PDF-1.4 test')});
  await expect(page.getByRole('alert')).toContainText('No example measurements were substituted');
  await expect(page.getByRole('heading',{name:'Add your report'})).toBeVisible();
});


// Mocked provider UI acceptance only. This cannot verify any real clinic or booking.
for (const width of [320, 375, 390, 430, 768, 1024, 1440, 1920]) {
  test(`mocked consultation consent at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.route('**/api/v1/reports/*/doctors?*', route => route.fulfill({json:{
      providers:[{id:'test-place',name:'Test clinic (mock)',address:'Test address',source:'external_discovery',consultation_options:[{type:'call',url:'tel:+911234567890',evidence:'Test fixture'}]}],
      live_provider_api_configured:false
    }}));
    await page.route('**/api/v1/consultation/preparation/*', route => route.fulfill({json:{findings:[],questions:['What should I ask?'],sharing_status:'not_shared',booking_status:'not_booked'}}));
    await page.goto('/');
    await page.getByRole('button', {name:'Example report · demo data'}).click();
    await page.getByRole('button', {name:'Skip all questions'}).click();
    await page.getByRole('button', {name:'Doctors',exact:true}).filter({visible:true}).click();
    await page.getByRole('button', {name:'View profile',exact:true}).click();
    const dialog=page.getByRole('dialog');
    await dialog.getByRole('button',{name:'Consult Doctor',exact:true}).click();
    await expect(dialog.getByText(/No appointment has been booked/)).toBeVisible();
    await expect(dialog.getByRole('link',{name:'Call Doctor/Clinic'})).toHaveAttribute('href','tel:+911234567890');
    await expect(dialog.getByRole('button',{name:'Download consultation-ready PDF'})).toBeDisabled();
    await dialog.getByRole('checkbox').check();
    await expect(dialog.getByRole('button',{name:'Download consultation-ready PDF'})).toBeEnabled();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.screenshot({path:`test-results/consultation-mocked-${width}.png`,fullPage:true});
  });
}


test('auth configuration is healthy through the configured Vite proxy',async({request})=>{
 const proxied=await request.get('/api/v1/auth/configuration');
 expect(proxied.status()).toBe(200);
 expect(await proxied.json()).toEqual({configured:false,sign_in_required:false,development_mode:true});
 const direct=await request.get(`http://127.0.0.1:${process.env.E2E_BACKEND_PORT||8101}/api/v1/auth/configuration`);
 expect(direct.status()).toBe(200);
 expect(await direct.json()).toEqual(await proxied.json());
});
