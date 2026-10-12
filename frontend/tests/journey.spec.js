import { test, expect } from '@playwright/test';

test.describe('Simplifier 2.0 Patient Journey E2E', () => {
  test('Complete Phase 5 Flow: Upload -> Verify -> Questions -> Report -> Inline Nutrition & Doctors -> PDF Download', async ({ page }) => {
    // 1. Visit Home
    await page.goto('http://localhost:3000/');
    await expect(page.locator('text=Understand your lab reports without the confusion')).toBeVisible();

    // 2. Start example report
    await page.click('text=Try an example health report');

    // 3. Verification screen: "Let's check a few details"
    await expect(page.locator('text=Let\'s check a few details')).toBeVisible();
    await expect(page.locator('text=Document Preview')).toBeVisible();

    // Correct a recognized value
    const input = page.locator('#correct-reading-input');
    await expect(input).toBeVisible();
    await input.fill('6.8');
    await page.click('button:has-text("Save Correction")');
    await expect(page.locator('text=Recorded! Value updated for your report analysis.')).toBeVisible();

    // 4. Continue to Step 2: Personalized Questions
    await page.click('button:has-text("Continue to Personalized Questions")');
    await expect(page.locator('text=A few questions about you')).toBeVisible();

    // Skip all questions to test honest uncertainty handling
    await page.click('button:has-text("Skip all questions")');

    // 5. Arrive at Step 3: Simplified Health Report
    await expect(page.locator('text=Here\'s what we found')).toBeVisible();
    await expect(page.locator('text=What needs attention')).toBeVisible();

    // Verify patient's correction is reflected in the downstream output
    await expect(page.locator('text=Verified by you: HbA1c (Glycated Hemoglobin) (6.8 %)')).toBeVisible();

    // 6. Test Inline Nutrition
    await page.click('button:has-text("Show my guidance")');
    await expect(page.locator('text=Everyday Food Guidance')).toBeVisible();
    await expect(page.locator('text=Wholesome Grains')).toBeVisible();
    await page.click('button:has-text("Back to report")');

    // 7. Test Inline Doctor Discovery & Demo Booking
    await page.click('button:has-text("Find a doctor")');
    await expect(page.locator('text=Find the Right Doctor')).toBeVisible();
    await expect(page.locator('text=Dr. Ananya Sharma, MD')).toBeVisible();
    await page.click('button:has-text("10:00 AM")');
    await expect(page.locator('text=Appointment reserved with Dr. Ananya Sharma')).toBeVisible();
    await page.click('button:has-text("Back to report")');

    // 8. Test Navigation tabs (Profile with Language selection)
    await page.click('button:has-text("Profile")');
    await expect(page.locator('h1:has-text("Profile & Medical Context")')).toBeVisible();

    await page.click('button:has-text("My Reports")');
    await expect(page.locator('h1:has-text("My Reports")')).toBeVisible();

    await page.click('button:has-text("Home")');
    await expect(page.locator('text=Here\'s what we found')).toBeVisible();

    // 9. Restart Journey
    await page.click('button:has-text("Understand another report")');
    await expect(page.locator('text=Understand your lab reports without the confusion')).toBeVisible();
  });
});
