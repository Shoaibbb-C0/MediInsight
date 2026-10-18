import { test, expect } from '@playwright/test';

for (const width of [375,1440]) {
 test(`real bundled Mumbai snapshot, PIN, GPS and map ${width}px with live discovery disabled`,async({page,context},info)=>{
  await page.setViewportSize({width,height:900});
  await context.grantPermissions(['geolocation']);
  await context.setGeolocation({latitude:19.18,longitude:72.96});
  await page.route('https://tiles.openfreemap.org/**',route=>route.fulfill({json:{version:8,sources:{},layers:[{id:'background',type:'background',paint:{'background-color':'#f7f4ec'}}]}}));
  await page.goto('/');
  await page.getByRole('button',{name:'Example report · demo data'}).click();
  await page.getByRole('button',{name:'Skip all questions'}).click();
  await page.getByRole('button',{name:'Doctors',exact:true}).filter({visible:true}).click();
  const input=page.getByPlaceholder('Enter city or PIN code (e.g., Mumbai, 411004)');
  await input.fill('Mumbai');
  const searched=page.waitForResponse(r=>r.url().includes('/doctors?')&&r.url().includes('city=Mumbai'));
  await page.getByRole('button',{name:'Update Location'}).click();
  const data=await (await searched).json();expect(data.data_source).toBe('osm_snapshot');
  await expect(page.getByText(/OSM snapshot — retrieved/)).toBeVisible();
  const general=page.waitForResponse(r=>r.url().includes('/doctors?')&&r.url().includes('specialty_id=general_physician'));
  await page.getByRole('button',{name:'Browse general healthcare facilities'}).click();
  const generalData=await (await general).json();
  const firstName=generalData.providers[0].name;
  await expect(page.getByRole('article',{name:firstName,exact:true}).first()).toBeVisible();
  await page.getByRole('button',{name:'Map',exact:true}).click();
  const marker=page.getByRole('button',{name:`Select facility: ${firstName}`,exact:true}).first();
  await expect(marker).toBeVisible();await marker.focus();await page.keyboard.press('Enter');
  await expect(page.getByRole('dialog')).toContainText(firstName);
  await page.keyboard.press('Escape');
  await expect(marker).toHaveAttribute('aria-pressed','true');
  await input.fill('400001');
  const pin=page.waitForResponse(r=>r.url().includes('/doctors?')&&r.url().includes('city=400001'));
  await page.getByRole('button',{name:'Update Location'}).click();
  expect((await (await pin).json()).resolved_location.pincode).toBe('400001');
  const gps=page.waitForResponse(r=>r.url().includes('/doctors?')&&r.url().includes('lat='));
  await page.getByRole('button',{name:'Use my location'}).click();
  const result=await (await gps).json();expect(result.data_source).toBe('osm_snapshot');
  expect(result.resolved_location.is_approximate).toBe(false);
  await expect(page.getByText(/OSM snapshot — retrieved/)).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.getByRole('region',{name:'Nearby healthcare facilities map',exact:true}).first().scrollIntoViewIfNeeded();
  await page.screenshot({path:info.outputPath('real-osm-snapshot.png')});
 });
}
