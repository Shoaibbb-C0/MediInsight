import { test, expect } from '@playwright/test';

test.describe('Simplifier 2.0 Patient Journey E2E', () => {
  test('Complete journey: Home -> Upload -> Verification -> Questionnaire -> Simplified Report', async ({ page }) => {
    // 1. Visit Home
    await page.goto('http://localhost:3000/');
    await expect(page.locator('text=Understand your lab reports without the confusion')).toBeVisible();
    await expect(page.locator('text=Private & confidential')).toBeVisible();

    // 2. Click Upload Modal
    await page.click('button:has-text("Upload a report")');
    await expect(page.locator('text=Upload your lab report')).toBeVisible();

    // 3. Close modal & Start Example / Captured Flow
    await page.click('button[aria-label="Close dialog"]');
    await page.click('text=Try an example health report');

    // 4. Source Verification Screen
    await expect(page.locator('text=Check these results')).toBeVisible();
    await expect(page.locator('text=Source Document Region')).toBeVisible();
    await expect(page.locator('text=Fasting Blood Glucose')).toBeVisible();
    
    // Check editable value
    const input = page.locator('#correct-value-input');
    await expect(input).toBeVisible();
    await input.fill('6.5');
    await page.click('button:has-text("Save Value")');
    await expect(page.locator('text=Correction recorded successfully!')).toBeVisible();

    // 5. Proceed to Step 2: Personalized Questionnaire
    await page.click('button:has-text("Confirm & Answer a few questions")');

    // Verify Questionnaire is displayed BEFORE report
    await expect(page.locator('text=A few questions about you')).toBeVisible();
    await expect(page.locator('text=Step 2 of 3: Personalized context')).toBeVisible();

    // Select an answer
    await page.click('button:has-text("Yes, I fasted for 10+ hours")');

    // 6. Proceed to Step 3: Simplified Report
    await page.click('button:has-text("See my health explanation")');

    // Verify Simplified Report Screen
    await expect(page.locator('text=Here\'s what we found')).toBeVisible();
    await expect(page.locator('text=Overall Summary')).toBeVisible();
    await expect(page.locator('text=Detailed Findings')).toBeVisible();
    await expect(page.locator('text=Important Medical Notice')).toBeVisible();
    await expect(page.locator('text=Phase 1 Synthetic Fixture')).toBeVisible();

    // 7. Test Navigation tabs (no dead-ends)
    await page.click('button:has-text("My Reports")');
    await expect(page.locator('h1:has-text("My Reports")')).toBeVisible();

    await page.click('button:has-text("Profile")');
    await expect(page.locator('h1:has-text("Profile & Preferences")')).toBeVisible();

    await page.click('button:has-text("Home")');
    await expect(page.locator('text=Here\'s what we found')).toBeVisible();

    // 8. Restart Journey returns cleanly to Home entry
    await page.click('button:has-text("Understand another report")');
    await expect(page.locator('text=Understand your lab reports without the confusion')).toBeVisible();
  });
});
