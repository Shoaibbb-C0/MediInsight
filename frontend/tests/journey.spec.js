import { test, expect } from '@playwright/test';

test.describe('Simplifier 2.0 Phase 2 E2E Browser Flow', () => {
  test('Flow: Upload & Verify Extracted Results -> Correction Changes Downstream Summary', async ({ page }) => {
    // 1. Visit Home
    await page.goto('http://localhost:3000/');
    await expect(page.locator('text=Understand your lab reports without the confusion')).toBeVisible();

    // 2. Start sample report
    await page.click('text=Try an example health report');

    // 3. Verification screen: "Let's check a few details"
    await expect(page.locator('text=Let\'s check a few details')).toBeVisible();
    await expect(page.locator('text=Document Preview')).toBeVisible();

    // Check correction control
    const input = page.locator('#correct-reading-input');
    await expect(input).toBeVisible();

    // Change recognized value to custom number
    await input.fill('6.8');
    await page.click('button:has-text("Save Correction")');
    await expect(page.locator('text=Recorded! Value updated for your report analysis.')).toBeVisible();

    // 4. Continue to Step 2: Personalized Questions
    await page.click('button:has-text("Continue to Personalized Questions")');
    await expect(page.locator('text=A few questions about you')).toBeVisible();

    // Select an answer
    await page.click('button:has-text("Yes, I fasted for 10+ hours")');

    // 5. Continue to Step 3: Simplified Report
    await page.click('button:has-text("See my health explanation")');
    await expect(page.locator('text=Here\'s what we found')).toBeVisible();

    // Verify patient's correction is reflected in the downstream output
    await expect(page.locator('text=Verified by you: HbA1c (Glycated Hemoglobin) (6.8 %)')).toBeVisible();

    // 6. Return Home
    await page.click('button:has-text("Understand another report")');
    await expect(page.locator('text=Understand your lab reports without the confusion')).toBeVisible();
  });
});
