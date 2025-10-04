import { test, expect } from '@playwright/test';
import { promises as fs } from 'fs';
import * as path from 'path';

// Test data for medium complexity engineering questions
const testQuestions = [
  {
    id: 'flow_calc',
    question: 'What are the typical design flow rates and peaking factors for a small municipal wastewater treatment plant serving 5,000 people in Washington State?',
    expectedContent: ['flow', 'peaking', 'municipal', 'design']
  },
  {
    id: 'permit_reqs',
    question: 'What are the key regulatory requirements for obtaining a new NPDES permit for industrial wastewater discharge in Washington State?',
    expectedContent: ['NPDES', 'permit', 'discharge', 'industrial']
  },
  {
    id: 'treatment_tech',
    question: 'Compare the effectiveness of different biological nutrient removal technologies for meeting phosphorus limits in wastewater treatment.',
    expectedContent: ['biological', 'nutrient', 'phosphorus', 'treatment']
  }
];

const providers = [
  { name: 'Cohere', value: 'cohere', model: 'command-a-reasoning-08-2025' },
  { name: 'OpenAI', value: 'openai', model: 'gpt-4o' },
  { name: 'Anthropic', value: 'anthropic', model: 'claude-3-opus-20240229' },
  { name: 'Google Gemini', value: 'gemini', model: 'models/gemini-1.5-pro' },
  { name: 'xAI Grok', value: 'xai', model: 'grok-2-1212' },
];

// Helper functions
async function selectProvider(page: any, provider: { name: string, value: string, model: string }) {
  // Select provider from dropdown
  await page.selectOption('#inp-provider', provider.value);
  
  // Clear and set model
  await page.fill('#inp-model', '');
  await page.fill('#inp-model', provider.model);
  
  // Apply provider settings
  await page.click('#btn-apply-provider');
  
  // Wait for provider to be applied
  await page.waitForTimeout(1000);
}

async function performRetrieval(page: any, question: string, outputPath: string) {
  // Navigate to retrieval tab
  await page.click('[data-value="tab-retrieval"]');
  
  // Enter question
  await page.fill('#ret-question', question);
  
  // Set output path
  await page.fill('#ret-out', outputPath);
  
  // Click retrieve button
  await page.click('#btn-retrieve');
  
  // Wait for retrieval to complete (increased timeout for API calls)
  await page.waitForSelector('.alert-success', { timeout: 60000 });
}

async function performGeneration(page: any, contextPath: string, outputPath: string, style: string = 'technical') {
  // Navigate to generate tab
  await page.click('[data-value="tab-generate"]');
  
  // Set context path
  await page.fill('#gen-ctx', contextPath);
  
  // Select style
  await page.selectOption('#gen-style', style);
  
  // Set output path
  await page.fill('#gen-out', outputPath);
  
  // Click generate button
  await page.click('#btn-generate');
  
  // Wait for generation to complete
  await page.waitForSelector('.alert-success', { timeout: 120000 });
}

async function validateOutputFile(filePath: string, expectedContent: string[]): Promise<boolean> {
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    
    // Check if file is not empty
    if (content.length < 100) {
      console.error(`File ${filePath} is too short: ${content.length} characters`);
      return false;
    }
    
    // Check for expected content keywords
    const lowerContent = content.toLowerCase();
    const missingKeywords = expectedContent.filter(keyword => 
      !lowerContent.includes(keyword.toLowerCase())
    );
    
    if (missingKeywords.length > 0) {
      console.warn(`Missing expected keywords in ${filePath}: ${missingKeywords.join(', ')}`);
    }
    
    return true;
  } catch (error) {
    console.error(`Error reading file ${filePath}:`, error);
    return false;
  }
}

// Main test suite
test.describe('Caliper v2 Multi-Provider Retrieve & Generate', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Caliper v2/);
    
    // Wait for the app to load completely
    await page.waitForLoadState('networkidle');
  });

  // Test each provider individually
  providers.forEach(provider => {
    test(`${provider.name} - Complete Retrieve & Generate Workflow`, async ({ page }) => {
      console.log(`Testing provider: ${provider.name}`);
      
      // Select and configure provider
      await selectProvider(page, provider);
      
      // Verify provider status shows success
      await expect(page.locator('#provider-status')).toContainText('applied');
      
      const question = testQuestions[0]; // Use first question for individual provider tests
      const timestamp = Date.now();
      const retrievalPath = `outputs/test_${provider.value}_${question.id}_retrieval_${timestamp}.json`;
      const generationPath = `outputs/test_${provider.value}_${question.id}_generation_${timestamp}.md`;
      
      // Step 1: Perform retrieval
      await performRetrieval(page, question.question, retrievalPath);
      
      // Verify retrieval output
      const retrievalSuccess = await page.locator('.alert-success').isVisible();
      expect(retrievalSuccess).toBeTruthy();
      
      // Step 2: Perform generation using retrieval context
      await performGeneration(page, retrievalPath, generationPath);
      
      // Verify generation output
      const generationSuccess = await page.locator('.alert-success').isVisible();
      expect(generationSuccess).toBeTruthy();
      
      // Step 3: Validate output files exist and have content
      const retrievalValid = await validateOutputFile(path.resolve(retrievalPath), ['nodes', 'query']);
      const generationValid = await validateOutputFile(path.resolve(generationPath), question.expectedContent);
      
      expect(retrievalValid).toBeTruthy();
      expect(generationValid).toBeTruthy();
      
      console.log(`✅ ${provider.name} test completed successfully`);
    });
  });
  
  // Cross-provider comparison test
  test('Cross-Provider Response Comparison', async ({ page }) => {
    const question = testQuestions[1]; // Use second question for comparison
    const results: { provider: string; retrievalPath: string; generationPath: string }[] = [];
    
    for (const provider of providers.slice(0, 3)) { // Test first 3 providers for comparison
      console.log(`Processing ${provider.name} for comparison...`);
      
      // Configure provider
      await selectProvider(page, provider);
      
      const timestamp = Date.now();
      const retrievalPath = `outputs/comparison_${provider.value}_retrieval_${timestamp}.json`;
      const generationPath = `outputs/comparison_${provider.value}_generation_${timestamp}.md`;
      
      // Perform retrieval and generation
      await performRetrieval(page, question.question, retrievalPath);
      await performGeneration(page, retrievalPath, generationPath);
      
      results.push({
        provider: provider.name,
        retrievalPath,
        generationPath
      });
      
      // Small delay between providers
      await page.waitForTimeout(2000);
    }
    
    // Validate all results
    for (const result of results) {
      const retrievalValid = await validateOutputFile(path.resolve(result.retrievalPath), ['nodes']);
      const generationValid = await validateOutputFile(path.resolve(result.generationPath), question.expectedContent);
      
      expect(retrievalValid).toBeTruthy();
      expect(generationValid).toBeTruthy();
    }
    
    console.log('✅ Cross-provider comparison completed successfully');
  });
  
  // Error handling and edge cases
  test('Error Handling - Empty Question', async ({ page }) => {
    // Select first provider
    await selectProvider(page, providers[0]);
    
    // Try to retrieve with empty question
    await page.click('[data-value="tab-retrieval"]');
    await page.click('#btn-retrieve');
    
    // Should show warning about empty question
    await expect(page.locator('.alert-warning')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.alert-warning')).toContainText('question');
  });
  
  test('Error Handling - Invalid Output Path', async ({ page }) => {
    // Select first provider
    await selectProvider(page, providers[0]);
    
    // Try to retrieve with invalid path
    await page.click('[data-value="tab-retrieval"]');
    await page.fill('#ret-question', testQuestions[0].question);
    await page.fill('#ret-out', '<>:|"invalid/path/name"');
    await page.click('#btn-retrieve');
    
    // Should handle the error gracefully
    await page.waitForTimeout(5000);
    // Check that either it handles gracefully or shows appropriate error
    const hasError = await page.locator('.alert-danger, .alert-warning').isVisible();
    const hasSuccess = await page.locator('.alert-success').isVisible();
    
    // Either should work (graceful handling) or show error - but shouldn't crash
    expect(hasError || hasSuccess).toBeTruthy();
  });
});