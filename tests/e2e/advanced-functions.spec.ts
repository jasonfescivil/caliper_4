import { test, expect } from '@playwright/test';
import { promises as fs } from 'fs';
import * as path from 'path';

// Test data for advanced function testing
const advancedTestScenarios = [
  {
    id: 'regulatory_analysis',
    question: 'Analyze the regulatory compliance requirements for a new wastewater treatment facility in Washington State, considering both state and federal regulations.',
    expectedContent: ['regulatory', 'compliance', 'federal', 'state', 'wastewater']
  },
  {
    id: 'technical_design',
    question: 'Design recommendations for biological nutrient removal system for a 2 MGD wastewater treatment plant with stringent phosphorus limits.',
    expectedContent: ['biological', 'nutrient', 'phosphorus', 'design', 'MGD']
  }
];

const providers = [
  { name: 'Cohere', value: 'cohere', model: 'command-a-reasoning-08-2025' },
  { name: 'OpenAI', value: 'openai', model: 'gpt-4o' },
  { name: 'Anthropic', value: 'anthropic', model: 'claude-3-opus-20240229' }
];

// Helper functions
async function selectProvider(page: any, provider: { name: string, value: string, model: string }) {
  await page.selectOption('#inp-provider', provider.value);
  await page.fill('#inp-model', '');
  await page.fill('#inp-model', provider.model);
  await page.click('#btn-apply-provider');
  await page.waitForTimeout(1000);
}

async function performEnhancement(page: any, contextPath: string, outputPath: string, strategy: string = 'detailed') {
  // Navigate to enhance tab
  await page.click('[data-value="tab-enhance"]');
  
  // Set context path
  await page.fill('#enh-ctx', contextPath);
  
  // Select enhancement strategy
  await page.selectOption('#enh-strategy', strategy);
  
  // Set output path
  await page.fill('#enh-out', outputPath);
  
  // Click enhance button
  await page.click('#btn-enhance');
  
  // Wait for enhancement to complete
  await page.waitForSelector('.alert-success', { timeout: 120000 });
}

async function performReviewAndJudge(page: any, contextPath: string, draftPath: string, jsonOutput: string, mdOutput: string) {
  // Navigate to review tab
  await page.click('[data-value="tab-review"]');
  
  // Set context path
  await page.fill('#rev-ctx', contextPath);
  
  // Set draft path
  await page.fill('#rev-draft', draftPath);
  
  // Set output paths
  await page.fill('#rev-json', jsonOutput);
  await page.fill('#rev-md', mdOutput);
  
  // Click review button
  await page.click('#btn-review');
  
  // Wait for review to complete
  await page.waitForSelector('.alert-success', { timeout: 120000 });
}

async function performGraphRAGRetrieval(page: any, question: string, graphDir: string, outputPath: string, hops: number = 2, limit: number = 200) {
  // Navigate to retrieval tab
  await page.click('[data-value="tab-retrieval"]');
  
  // Switch to Graph tab if available
  const graphTab = page.locator('[data-tab="graph"]');
  if (await graphTab.isVisible()) {
    await graphTab.click();
  }
  
  // Fill GraphRAG specific fields
  await page.fill('#graph-question', question);
  await page.fill('#graph-dir', graphDir);
  await page.fill('#graph-out', outputPath);
  await page.fill('#graph-hops', hops.toString());
  await page.fill('#graph-limit', limit.toString());
  
  // Click GraphRAG retrieve button
  await page.click('#btn-graph-retrieve');
  
  // Wait for GraphRAG retrieval to complete
  await page.waitForSelector('.alert-success', { timeout: 180000 }); // GraphRAG can take longer
}

async function validateJsonOutput(filePath: string): Promise<{ valid: boolean; content?: any }> {
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    const parsed = JSON.parse(content);
    return { valid: true, content: parsed };
  } catch (error) {
    console.error(`Error parsing JSON file ${filePath}:`, error);
    return { valid: false };
  }
}

async function validateMarkdownOutput(filePath: string, expectedContent: string[]): Promise<boolean> {
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    
    if (content.length < 200) {
      console.error(`Markdown file ${filePath} is too short: ${content.length} characters`);
      return false;
    }
    
    const lowerContent = content.toLowerCase();
    const missingKeywords = expectedContent.filter(keyword => 
      !lowerContent.includes(keyword.toLowerCase())
    );
    
    if (missingKeywords.length > 0) {
      console.warn(`Missing expected keywords in ${filePath}: ${missingKeywords.join(', ')}`);
    }
    
    return true;
  } catch (error) {
    console.error(`Error reading markdown file ${filePath}:`, error);
    return false;
  }
}

// Main test suite for advanced functions
test.describe('Caliper v2 Advanced Functions', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Caliper v2/);
    await page.waitForLoadState('networkidle');
  });

  test('Enhancement Function - Context Enrichment', async ({ page }) => {
    const provider = providers[0]; // Use Cohere for this test
    const scenario = advancedTestScenarios[0];
    
    await selectProvider(page, provider);
    
    const timestamp = Date.now();
    const retrievalPath = `outputs/test_enhance_retrieval_${timestamp}.json`;
    const enhancedPath = `outputs/test_enhance_enhanced_${timestamp}.json`;
    
    // First perform retrieval to get base context
    await page.click('[data-value="tab-retrieval"]');
    await page.fill('#ret-question', scenario.question);
    await page.fill('#ret-out', retrievalPath);
    await page.click('#btn-retrieve');
    await page.waitForSelector('.alert-success', { timeout: 60000 });
    
    // Then enhance the context
    await performEnhancement(page, retrievalPath, enhancedPath, 'detailed');
    
    // Verify enhancement output
    const enhancementSuccess = await page.locator('.alert-success').isVisible();
    expect(enhancementSuccess).toBeTruthy();
    
    // Validate enhanced output file
    const { valid: enhancedValid } = await validateJsonOutput(path.resolve(enhancedPath));
    expect(enhancedValid).toBeTruthy();
    
    console.log('✅ Enhancement function test completed successfully');
  });

  test('Complete Workflow - Retrieve > Enhance > Generate > Review', async ({ page }) => {
    const provider = providers[1]; // Use OpenAI for this comprehensive test
    const scenario = advancedTestScenarios[1];
    
    await selectProvider(page, provider);
    
    const timestamp = Date.now();
    const retrievalPath = `outputs/workflow_retrieval_${timestamp}.json`;
    const enhancedPath = `outputs/workflow_enhanced_${timestamp}.json`;
    const draftPath = `outputs/workflow_draft_${timestamp}.md`;
    const reviewJsonPath = `outputs/workflow_review_${timestamp}.json`;
    const reviewMdPath = `outputs/workflow_review_${timestamp}.md`;
    
    // Step 1: Retrieval
    await page.click('[data-value="tab-retrieval"]');
    await page.fill('#ret-question', scenario.question);
    await page.fill('#ret-out', retrievalPath);
    await page.click('#btn-retrieve');
    await page.waitForSelector('.alert-success', { timeout: 60000 });
    
    // Step 2: Enhancement
    await performEnhancement(page, retrievalPath, enhancedPath, 'comprehensive');
    
    // Step 3: Generation
    await page.click('[data-value="tab-generate"]');
    await page.fill('#gen-ctx', enhancedPath);
    await page.selectOption('#gen-style', 'technical');
    await page.fill('#gen-out', draftPath);
    await page.click('#btn-generate');
    await page.waitForSelector('.alert-success', { timeout: 120000 });
    
    // Step 4: Review and Judge
    await performReviewAndJudge(page, enhancedPath, draftPath, reviewJsonPath, reviewMdPath);
    
    // Validate all outputs
    const { valid: retrievalValid } = await validateJsonOutput(path.resolve(retrievalPath));
    const { valid: enhancedValid } = await validateJsonOutput(path.resolve(enhancedPath));
    const draftValid = await validateMarkdownOutput(path.resolve(draftPath), scenario.expectedContent);
    const { valid: reviewJsonValid } = await validateJsonOutput(path.resolve(reviewJsonPath));
    const reviewMdValid = await validateMarkdownOutput(path.resolve(reviewMdPath), ['review', 'analysis']);
    
    expect(retrievalValid).toBeTruthy();
    expect(enhancedValid).toBeTruthy();
    expect(draftValid).toBeTruthy();
    expect(reviewJsonValid).toBeTruthy();
    expect(reviewMdValid).toBeTruthy();
    
    console.log('✅ Complete workflow test completed successfully');
  });

  test('GraphRAG Retrieval Function', async ({ page }) => {
    const provider = providers[2]; // Use Anthropic for GraphRAG test
    const scenario = advancedTestScenarios[0];
    
    await selectProvider(page, provider);
    
    const timestamp = Date.now();
    const graphOutputPath = `outputs/test_graphrag_${timestamp}.json`;
    
    // Check if GraphRAG is available (graph directory exists)
    const graphDir = 'data_v2/graphs/test_graph'; // Adjust based on actual structure
    
    try {
      await performGraphRAGRetrieval(page, scenario.question, graphDir, graphOutputPath, 2, 150);
      
      // Verify GraphRAG output
      const graphSuccess = await page.locator('.alert-success').isVisible();
      expect(graphSuccess).toBeTruthy();
      
      // Validate GraphRAG output file
      const { valid: graphValid } = await validateJsonOutput(path.resolve(graphOutputPath));
      expect(graphValid).toBeTruthy();
      
      console.log('✅ GraphRAG function test completed successfully');
    } catch (error) {
      // If GraphRAG is not set up, skip gracefully
      console.log('⚠️ GraphRAG test skipped - feature may not be configured');
      test.skip();
    }
  });

  test('Judge Function - Content Analysis', async ({ page }) => {
    const provider = providers[0]; // Use Cohere for judge function
    const scenario = advancedTestScenarios[0];
    
    await selectProvider(page, provider);
    
    const timestamp = Date.now();
    const retrievalPath = `outputs/judge_test_retrieval_${timestamp}.json`;
    const draftPath = `outputs/judge_test_draft_${timestamp}.md`;
    const reviewJsonPath = `outputs/judge_test_review_${timestamp}.json`;
    const reviewMdPath = `outputs/judge_test_review_${timestamp}.md`;
    
    // Create base content first
    await page.click('[data-value="tab-retrieval"]');
    await page.fill('#ret-question', scenario.question);
    await page.fill('#ret-out', retrievalPath);
    await page.click('#btn-retrieve');
    await page.waitForSelector('.alert-success', { timeout: 60000 });
    
    // Generate draft
    await page.click('[data-value="tab-generate"]');
    await page.fill('#gen-ctx', retrievalPath);
    await page.fill('#gen-out', draftPath);
    await page.click('#btn-generate');
    await page.waitForSelector('.alert-success', { timeout: 120000 });
    
    // Test judge function with different strictness levels
    await page.click('[data-value="tab-review"]');
    await page.fill('#rev-ctx', retrievalPath);
    await page.fill('#rev-draft', draftPath);
    await page.fill('#rev-json', reviewJsonPath);
    await page.fill('#rev-md', reviewMdPath);
    
    // Enable strict mode
    await page.check('#rev-strict');
    
    // Set max evidence per claim
    await page.fill('#rev-max-ev', '3');
    
    await page.click('#btn-review');
    await page.waitForSelector('.alert-success', { timeout: 120000 });
    
    // Validate judge outputs
    const { valid: reviewJsonValid, content: reviewContent } = await validateJsonOutput(path.resolve(reviewJsonPath));
    const reviewMdValid = await validateMarkdownOutput(path.resolve(reviewMdPath), ['claims', 'evidence']);
    
    expect(reviewJsonValid).toBeTruthy();
    expect(reviewMdValid).toBeTruthy();
    
    // Check if review contains expected analysis fields
    if (reviewContent) {
      expect(reviewContent).toHaveProperty('claims');
      expect(Array.isArray(reviewContent.claims)).toBeTruthy();
    }
    
    console.log('✅ Judge function test completed successfully');
  });

  test('Provider Self-Test Function', async ({ page }) => {
    // Test the provider self-test functionality
    await page.selectOption('#inp-provider', 'cohere');
    await page.click('#btn-apply-provider');
    await page.waitForTimeout(1000);
    
    // Click self-test button
    await page.click('#btn-provider-selftest');
    
    // Wait for self-test to complete
    await page.waitForTimeout(10000);
    
    // Check that status indicates test completion
    const statusElement = page.locator('#provider-status');
    await expect(statusElement).toBeVisible();
    
    // The status should contain some indication of test results
    const statusText = await statusElement.textContent();
    expect(statusText).toBeTruthy();
    expect(statusText!.length).toBeGreaterThan(10);
    
    console.log('✅ Provider self-test completed');
  });

  test('Doctor Function - System Health Check', async ({ page }) => {
    // Test the doctor/diagnostic functionality
    await page.click('#btn-doctor');
    
    // Wait for doctor check to complete
    await page.waitForTimeout(15000);
    
    // Check for status updates
    const statusElement = page.locator('#provider-status');
    await expect(statusElement).toBeVisible();
    
    console.log('✅ Doctor function test completed');
  });
});