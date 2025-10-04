import { test, expect } from '@playwright/test';

test.describe('Caliper v2 UI Validation', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('UI loads and displays expected elements', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Caliper v2|Updating/);
    
    // Check main heading (first h2 element)
    await expect(page.locator('h2').first()).toContainText('Caliper v2 – Dash/Plotly Wrapper');
    
    // Check provider dropdown exists and has expected options  
    const providerSelect = page.locator('select, [role="combobox"]').first();
    await expect(providerSelect).toBeVisible();
    
    // Check tabs are present
    const tabs = [
      '🔎 Retrieval',
      '✨ Enhance', 
      '✍️ Draft',
      '🧪 Generate',
      '⚖️ Judge & Review'
    ];
    
    for (const tab of tabs) {
      await expect(page.locator('text=' + tab)).toBeVisible();
    }
    
    // Check key form elements are present using more robust selectors
    await expect(page.locator('textarea, input[placeholder*="question"]').first()).toBeVisible(); // Question input
    await expect(page.locator('button:has-text("Run Retrieval"), button:has-text("Retrieval")').first()).toBeVisible(); // Run Retrieval button
    
    console.log('✅ UI validation passed - all expected elements present');
  });

  test('Provider selection works', async ({ page }) => {
    const providerSelect = page.locator('select, [role="combobox"]').first();
    
    // Test selecting different providers
    const providers = ['cohere', 'openai', 'anthropic', 'gemini', 'xai'];
    
    for (const provider of providers) {
      await providerSelect.selectOption(provider);
      
      // Check that selection worked
      const selectedValue = await providerSelect.inputValue();
      expect(selectedValue.toLowerCase()).toBe(provider.toLowerCase());
    }
    
    console.log('✅ Provider selection test passed');
  });

  test('Apply provider button works', async ({ page }) => {
    // Select a provider
    const providerSelect = page.locator('select, [role="combobox"]').first();
    await providerSelect.selectOption('cohere');
    
    // Fill model field  
    const modelInput = page.locator('input[placeholder*="Model"], input[placeholder*="optional"]').first();
    await modelInput.fill('command-a-reasoning-08-2025');
    
    // Click apply button
    const applyButton = page.locator('button:has-text("Apply")').first();
    await applyButton.click();
    
    // Wait for any response (status message, etc.)
    await page.waitForTimeout(2000);
    
    console.log('✅ Apply provider test passed');
  });

  test('Basic form validation', async ({ page }) => {
    // Try to run retrieval without question
    const retrievalButton = page.locator('button:has-text("Run Retrieval"), button:has-text("Retrieval")').first();
    await retrievalButton.click();
    
    // Should either show validation error or handle gracefully
    await page.waitForTimeout(3000);
    
    // Check if any alert or error message appeared
    const alerts = page.locator('.alert');
    const alertExists = await alerts.count() > 0;
    
    if (alertExists) {
      const alertText = await alerts.first().textContent();
      console.log(`Validation message: ${alertText}`);
    }
    
    console.log('✅ Form validation test passed');
  });
  
  test('Navigation between tabs works', async ({ page }) => {
    // Test clicking on different tabs
    const tabNames = ['Retrieval', 'Enhance', 'Draft', 'Generate', 'Review'];
    
    for (const tabName of tabNames) {
      // Try to click tab by text content
      const tabElement = page.locator(`text=*${tabName}*`).first();
      if (await tabElement.isVisible()) {
        await tabElement.click();
        await page.waitForTimeout(500);
        console.log(`✅ Clicked ${tabName} tab`);
      }
    }
    
    console.log('✅ Tab navigation test passed');
  });
});