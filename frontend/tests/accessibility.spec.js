import {test,expect} from '@playwright/test';
import {TRANSLATIONS} from '../src/fixtures/translations.js';
for(const language of ['en','hi','mr']){
 test(`keyboard, reduced motion and 200 percent layout ${language}`,async({page},testInfo)=>{
   await page.setViewportSize({width:375,height:900});
   await page.emulateMedia({reducedMotion:'reduce'});
   const pageErrors=[];page.on('pageerror',error=>pageErrors.push(error.message));
   await page.goto('/');
   if(language!=='en')await page.getByRole('button',{name:language==='hi'?'हिं':'मरा',exact:true}).click();
   await expect(page.locator('html')).toHaveAttribute('lang',language);
   await page.keyboard.press('Tab');
   await expect(page.locator(':focus')).not.toHaveCount(0);
   const t=TRANSLATIONS[language];
   await page.getByRole('button',{name:t.uploadButton,exact:true}).focus();
   await page.keyboard.press('Enter');
   await expect(page.getByRole('dialog'),pageErrors.join(' | ')).toBeVisible();
   await page.keyboard.press('Shift+Tab');
   expect(await page.locator(':focus').evaluate(element=>!!element.closest('[role=dialog]'))).toBe(true);
   await page.keyboard.press('Escape');
   await expect(page.getByRole('dialog')).toHaveCount(0);
   await expect(page.getByRole('button',{name:t.uploadButton,exact:true})).toBeFocused();
   const unnamed=await page.locator('button:visible').evaluateAll(buttons=>buttons.filter(button=>!(button.getAttribute('aria-label')||button.innerText).trim()).length);
   expect(unnamed).toBe(0);
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   const overflow=await page.locator('body *').evaluateAll(elements=>elements.filter(element=>element.getBoundingClientRect().right>innerWidth+1 && getComputedStyle(element).position!=='absolute').slice(0,12).map(element=>({tag:element.tagName,css:element.className,right:element.getBoundingClientRect().right})));
   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),JSON.stringify(overflow)).toBe(true);
   await page.screenshot({path:testInfo.outputPath('zoom-200.png'),fullPage:true});
 });
}
