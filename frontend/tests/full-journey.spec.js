import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { existsSync, statSync } from "node:fs";
import { TRANSLATIONS } from "../src/fixtures/translations.js";
const candidate = fileURLToPath(
  new URL(
    "../../backend/.venv/" +
      (process.platform === "win32" ? "Scripts/python.exe" : "bin/python"),
    import.meta.url,
  ),
);
const python =
  process.env.PYTHON || (existsSync(candidate) ? candidate : "python");
const source = execFileSync(python, [
  fileURLToPath(
    new URL("../../backend/scripts/create_test_report.py", import.meta.url),
  ),
]);
const locale = {
  en: [
    "Check uncertain readings",
    "Save reading",
    "Saved",
    "Continue to questions",
    "Nutrition",
    "Doctors",
    "View profile",
    "Consult Doctor",
    "Download consultation-ready PDF",
  ],
  hi: [
    "अस्पष्ट माप जाँचें",
    "माप सहेजें",
    "सहेजा गया",
    "प्रश्नों पर जाएँ",
    "आहार",
    "डॉक्टर",
    "प्रोफ़ाइल देखें",
    "डॉक्टर से परामर्श",
    "परामर्श के लिए PDF डाउनलोड करें",
  ],
  mr: [
    "अस्पष्ट मोजमाप तपासा",
    "मोजमाप जतन करा",
    "जतन झाले",
    "प्रश्नांकडे जा",
    "आहार",
    "डॉक्टर",
    "प्रोफाइल पाहा",
    "डॉक्टरांचा सल्ला घ्या",
    "सल्ल्यासाठी PDF डाउनलोड करा",
  ],
};
for (const [language, width] of [
  ["en", 375],
  ["en", 1440],
  ["hi", 390],
  ["mr", 430],
]) {
  test(`real local report-food-history journey ${language} ${width}px with mocked provider only`, async ({
    page,
  }, testInfo) => {
    const t = TRANSLATIONS[language],
      c = locale[language];
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/");
    if (language !== "en")
      await page
        .getByRole("button", {
          name: language === "hi" ? "हिं" : "मरा",
          exact: true,
        })
        .click();
    await page
      .getByRole("button", { name: t.uploadButton, exact: true })
      .click();
    const upload = page.waitForResponse((response) =>
      response.url().endsWith("/reports/upload"),
    );
    await page
      .locator("input[type=file]")
      .setInputFiles({
        name: "synthetic-test-report.pdf",
        mimeType: "application/pdf",
        buffer: source,
      });
    const id = (await (await upload).json()).report_id;
    await expect(page.getByRole("heading", { name: c[0] })).toBeVisible();
    await page.getByRole("button", { name: c[1], exact: true }).click();
    await expect(page.getByRole("status")).toHaveText(c[2]);
    await page.getByRole("button", { name: c[3], exact: true }).click();
    await page
      .getByRole("button", { name: t.skipAllQuestions, exact: true })
      .click();
    await expect(
      page.getByRole("meter", { name: /124\.5 mg\/dL/ }).first(),
    ).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page.screenshot({
      path: testInfo.outputPath("report.png"),
      fullPage: true,
    });
    await page
      .getByRole("button", { name: c[4], exact: true })
      .filter({ visible: true })
      .click();
    await page
      .getByRole("button", { name: t.recalculatePlanBtn, exact: true })
      .click();
    const questions = (
      await (
        await page.request.get(
          `/api/v1/reports/${id}/nutrition/questions?lang=${language}`,
        )
      ).json()
    ).questions;
    const choices = {
      nq_age_group: "adult",
      nq_dietary_pref: "vegetarian",
      nq_allergies: "none",
      nq_health_conditions: "none",
      nq_special_restrictions: "none",
    };
    for (let index = 0; index < questions.length; index++) {
      const q = questions[index],
        option =
          q.options.find((item) => item.id === choices[q.id]) || q.options[0];
      await page
        .getByRole("button", { name: option.text, exact: true })
        .click();
      await page
        .getByRole("button", {
          name:
            index === questions.length - 1
              ? t.generatePlanBtn + " →"
              : t.nextQuestion + " →",
          exact: true,
        })
        .click();
    }
    await expect(
      page.getByRole("button", { name: t.swapMeal, exact: true }).first(),
    ).toBeVisible();
    await page
      .getByRole("button", { name: t.swapMeal, exact: true })
      .first()
      .click();
    await page
      .getByRole("dialog")
      .getByRole("button", { name: t.selectAlternative, exact: true })
      .first()
      .click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await page.screenshot({path:testInfo.outputPath("nutrition.png"),fullPage:true});
    const plan = await page.request.get(
      `/api/v1/reports/${id}/nutrition/plan?lang=${language}`,
    );
    expect((await plan.json()).days).toHaveLength(7);
    const foodPDF = await page.request.get(
      `/api/v1/reports/${id}/nutrition/pdf?lang=${language}`,
    );
    expect(foodPDF.status()).toBe(200);
    expect((await foodPDF.body()).subarray(0, 4).toString()).toBe("%PDF");
    await page.route("**/api/v1/reports/*/doctors?*", (route) => {
      if (!new URL(route.request().url()).searchParams.has("city"))
        return route.continue();
      return route.fulfill({
        json: {
          providers: [
            {
              id: "test-place",
              name: "MOCK TEST CLINIC",
              specialty: "Test specialty listing",
              address: "Synthetic test address",
              source: "external_discovery",
              rating: 4.8,
              user_rating_count: 120,
              consultation_options: [
                {
                  type: "call",
                  url: "tel:+911234567890",
                  evidence: "Test fixture only",
                },
              ],
            },
          ],
          live_provider_api_configured: false,
        },
      });
    });
    await page
      .getByRole("button", { name: c[5], exact: true })
      .filter({ visible: true })
      .click();
    await page.getByPlaceholder(t.locationPlaceholder).fill("Panvel");
    await page
      .getByRole("button", { name: t.searchLocationBtn, exact: true })
      .click();
    await page.getByRole("button", { name: c[6], exact: true }).click();
    await page
      .getByRole("dialog")
      .getByRole("button", { name: c[7], exact: true })
      .click();
    const dialog = page.getByRole("dialog"),
      download = dialog.getByRole("button", { name: c[8], exact: true });
    await expect(download).toBeDisabled();
    await dialog.getByRole("checkbox").check();
    await expect(download).toBeEnabled();
    await page.screenshot({path:testInfo.outputPath("consultation.png"),fullPage:true});
    const exported = page.waitForEvent("download");
    await download.click();
    const file = await exported,
      path = testInfo.outputPath("consultation.pdf");
    await file.saveAs(path);
    expect(statSync(path).size).toBeGreaterThan(1000);
    await page.keyboard.press("Escape");
    await page
      .getByRole("button", { name: t.reports, exact: true })
      .filter({ visible: true })
      .click();
    await expect(
      page.getByRole("heading", {
        name: "synthetic-test-report.pdf",
        exact: true,
      }),
    ).toBeVisible();
    await page.reload();
    await page
      .getByRole("button", { name: t.reports, exact: true })
      .filter({ visible: true })
      .click();
    await expect(
      page.getByRole("heading", {
        name: "synthetic-test-report.pdf",
        exact: true,
      }),
    ).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  });
}


test('camera fallback submits both selected pages through real capture processing',async({page})=>{
 await page.addInitScript(()=>{
   Object.defineProperty(navigator,'mediaDevices',{value:{getUserMedia:async()=>{throw new DOMException('Test fixture permission denial','NotAllowedError');}},configurable:true});
 });
 const image=execFileSync(python,[fileURLToPath(new URL('../../backend/scripts/create_test_report.py',import.meta.url)),'--png']);
 await page.goto('/');
 await page.getByRole('button',{name:'Take a photo',exact:true}).click();
 await page.getByRole('button',{name:'Choose photo from device',exact:true}).waitFor();
 await page.locator('input[type=file]').setInputFiles({name:'test-page-one.png',mimeType:'image/png',buffer:image});
 await expect(page.getByText('Selected pages: 1')).toBeVisible();
 await page.getByRole('button',{name:'Add another page',exact:true}).click();
 await page.getByRole('button',{name:'Choose photo from device',exact:true}).waitFor();
 await page.locator('input[type=file]').setInputFiles({name:'test-page-two.png',mimeType:'image/png',buffer:image});
 await expect(page.getByText('Selected pages: 2')).toBeVisible();
 const response=page.waitForResponse(item=>item.url().endsWith('/reports/capture'));
 await page.getByRole('button',{name:/Process This Report/}).click();
 const captured=await response;expect(captured.status()).toBe(200);expect((await captured.json()).page_count).toBe(2);
 await expect(page.getByRole('heading',{name:'Check uncertain readings'})).toBeVisible();
});
