import { test, expect } from '@playwright/test';

for (const width of [375, 1440]) {
 test(`OSM map markers, cards and contact links at ${width}px (mocked upstream)`, async({page},info)=>{
  await page.setViewportSize({width,height:900});
  await page.route('https://tiles.openfreemap.org/**',route=>route.fulfill({json:{version:8,sources:{},layers:[{id:'background',type:'background',paint:{'background-color':'#f7f4ec'}}]}}));
  await page.route('**/api/v1/reports/*/doctors?*',route=>route.fulfill({json:{providers:[{id:'osm:node/1',name:'OSM FIXTURE CLINIC',specialty:'clinic',address:'Fixture address',coordinates:{lat:18.99,lng:73.12},distance_km:0.6,phone:'+911234567890',website:'https://example.org/fixture',directions_url:'https://www.openstreetmap.org/directions?to=18.99%2C73.12',source:'external_discovery',available_slots:[],consultation_options:[],attributions:[{provider:'© OpenStreetMap contributors',providerUri:'https://www.openstreetmap.org/copyright'}]}],resolved_location:{display_name:'Panvel fixture location',coordinates:{lat:18.989,lng:73.122}},live_provider_api_configured:true,searched_radius_m:5000,is_demo_mode:false}}));
  await page.goto('/');
  await page.getByRole('button',{name:'Example report · demo data'}).click();
  await page.getByRole('button',{name:'Skip all questions'}).click();
  await page.getByRole('button',{name:'Doctors',exact:true}).filter({visible:true}).click();
  await page.getByRole('button',{name:'Map',exact:true}).click();
  const marker=page.getByRole('button',{name:'Select facility: OSM FIXTURE CLINIC'});
  await expect(marker).toBeVisible();await marker.click();
  const dialog=page.getByRole('dialog');await expect(dialog).toContainText('OSM FIXTURE CLINIC');
  await dialog.getByRole('button',{name:'Close',exact:true}).click();
  await expect(marker).toHaveAttribute('aria-pressed','true');
  const card=page.getByRole('article',{name:'OSM FIXTURE CLINIC'});
  await expect(card.getByRole('link',{name:'Call Doctor/Clinic'})).toHaveAttribute('href','tel:+911234567890');
  await expect(card.getByRole('link',{name:'Visit Website'})).toHaveAttribute('href','https://example.org/fixture');
  await expect(card.getByRole('link',{name:'Get Directions'})).toHaveAttribute('href',/openstreetmap.org/);
  await card.getByRole('button',{name:'View profile'}).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.keyboard.press('Escape');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:info.outputPath('osm-map.png'),fullPage:true});
 });
}
