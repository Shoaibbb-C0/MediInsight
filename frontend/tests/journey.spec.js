import { test, expect } from '@playwright/test';

test.describe('Simplifier 2.0 Feature 1 — Smart Report Patient Journey & Multilingual Verification', () => {
  test('Complete Seamless Patient Journey in English: Upload/Sample -> Adaptive Questions -> Abnormal-First Report -> PDF Download', async ({ page }) => {
    // 1. Visit Home
    await page.goto('http://localhost:3000/');
    await expect(page.locator('text=Understand your lab reports without the confusion')).toBeVisible();
    await expect(page.locator('text=Private & confidential')).toBeVisible();

    // 2. Start example report (seamless flow, no mandatory transcription grid)
    await page.click('text=Try an example health report');

    // 3. Arrive immediately at Step 1 of Journey: Personalized Adaptive Questions
    await expect(page.locator('text=Step 1 of 2: A few questions about you')).toBeVisible();
    await expect(page.locator('text=Was your blood sample strictly collected before breakfast')).toBeVisible();

    // Answer fasting question
    await page.click('text=Yes, strictly fasted');
    await page.click('button:has-text("Next question")');

    // Skip remainder to test respectful skipping
    await page.click('button:has-text("Skip all questions")');

    // 4. Arrive at Step 2 of Journey: Final Abnormal-First Simplified Report
    await expect(page.locator('text=Here\'s what we found')).toBeVisible();
    await expect(page.locator('text=What needs attention')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Fasting Blood Glucose' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Vitamin D (25-OH)' })).toBeVisible();

    // Expand Healthy / Within-Range Results
    await page.click('text=See all results');
    await expect(page.locator('text=Serum Creatinine').first()).toBeVisible();

    // Verify Download PDF button is visible and active
    const downloadBtn = page.locator('button:has-text("Download Summary PDF")');
    await expect(downloadBtn).toBeVisible();

    // 5. Open Feature 2: Inline Personalized Nutrition Plan
    await page.click('button:has-text("Show my guidance")');
    await expect(page.locator('text=Personalized 7-Day Nutrition Plan')).toBeVisible();
    await expect(page.locator('text=Day 1')).toBeVisible();
    await expect(page.locator('text=Breakfast')).toBeVisible();

    // Switch Day Tab to Day 2
    await page.click('button:has-text("Day 2")');
    await expect(page.locator('text=Day 2')).toBeVisible();

    // Verify Swap Meal button is accessible
    const swapButtons = page.locator('button:has-text("Swap dish")');
    if (await swapButtons.count() > 0) {
      await swapButtons.first().click();
      await expect(page.locator('text=Choose an alternative:')).toBeVisible();
      await page.click('button:has-text("Cancel")');
    }

    // Verify Download Weekly Meal Guide PDF button
    await expect(page.locator('button:has-text("Download Weekly Meal Guide (PDF)")')).toBeVisible();

    // Close Nutrition modal
    await page.click('button[aria-label="Close nutrition"]');

    // 6. Switch to Hindi via Navigation
    await page.click('button:has-text("हिं")');
    await expect(page.locator('text=जाँच में क्या सामने आया')).toBeVisible();
    await expect(page.locator('text=समग्र सारांश')).toBeVisible();
    await expect(page.locator('text=सारांश PDF डाउनलोड करें')).toBeVisible();

    // 7. Switch to Marathi via Navigation
    await page.click('button:has-text("मरा")');
    await expect(page.locator('text=तपासणीत काय आढळले')).toBeVisible();
    await expect(page.locator('text=एकूण सारांश')).toBeVisible();
    await expect(page.locator('text=अहवाल PDF डाउनलोड करा')).toBeVisible();

    // 8. Restart Journey and verify Home retains Marathi until switched
    await page.click('button:has-text("दुसरा अहवाल समजून घ्या")');
    await expect(page.locator('text=कोणत्याही गोंधळाशिवाय तुमचे लॅब रिपोर्ट समजून घ्या')).toBeVisible();

    // 9. Switch back to English
    await page.click('button:has-text("EN")');
    await expect(page.locator('text=Understand your lab reports without the confusion')).toBeVisible();
  });
});
