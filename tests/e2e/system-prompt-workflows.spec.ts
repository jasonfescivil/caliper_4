import { test, expect } from '@playwright/test';
import { promises as fs } from 'fs';
import * as path from 'path';
import { 
  providers, 
  engineeringQuestions,
  selectProvider,
  performRetrieval,
  performGeneration,
  performEnhancement,
  performReview,
  validateJsonFile,
  validateMarkdownFile,
  validateRetrievalOutput,
  waitForAlertAndGetText,
  generateTimestampedPath,
  ensureOutputDirectory
} from './test-utils';

/**
 * E2E Tests for Caliper v2 System Prompt Workflows
 * 
 * This test suite validates all the workflows described in the CALIPER_AI_SYSTEM_PROMPT.md
 * including basic retrieval/generation, complete enhanced workflows, and GraphRAG workflows.
 */

test.describe('Caliper v2 System Prompt Workflows', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Caliper v2/);
    await page.waitForLoadState('networkidle');
    await ensureOutputDirectory();
  });

  /**
   * Test: Basic Retrieval & Generation Workflow
   * Based on system prompt example:
   * ```bash
   * poetry run caliper_v2 retrieve "What are G1 requirements?" --indexes federal,state --cloud
   * poetry run caliper_v2 generate data_v2/context/file.json --style strict-citation
   * ```
   */
  test('Basic Retrieval & Generation Workflow', async ({ page }) => {
    console.log('Testing basic retrieval and generation workflow...');
    
    // Test with first available provider
    const provider = providers[0];
    await selectProvider(page, provider);
    
    // Step 1: Retrieve with cloud indexes (simulating --indexes federal,state --cloud)
    const retrievalPath = generateTimestampedPath('basic_retrieval');
    const question = 'What are G1 requirements for wastewater treatment facilities?';
    
    await performRetrieval(page, question, retrievalPath, {
      textIndexes: 'federal,state',
      topK: 20
    });
    
    // Validate retrieval output
    const retrievalResult = await validateRetrievalOutput(path.resolve(retrievalPath));
    expect(retrievalResult.valid).toBeTruthy();
    expect(retrievalResult.nodeCount).toBeGreaterThan(5);
    
    // Step 2: Generate with strict-citation style
    const generationPath = generateTimestampedPath('basic_generation', 'md');
    
    await performGeneration(page, retrievalPath, generationPath, {
      style: 'strict-citation'
    });
    
    // Validate generation output
    const generationResult = await validateMarkdownFile(
      path.resolve(generationPath), 
      ['G1', 'requirements', 'treatment'], 
      500
    );
    expect(generationResult.valid).toBeTruthy();
    
    console.log('✅ Basic retrieval & generation workflow completed successfully');
  });

  /**
   * Test: Complete Enhanced Workflow (5-step process)
   * Based on system prompt example:
   * 1. Retrieve with cloud indexes
   * 2. Enhance context (outline, gaps)
   * 3. Generate draft
   * 4. Judge generated content
   * 5. Review (combines judge + lints)
   */
  test('Complete Enhanced Workflow (5-step)', async ({ page }) => {
    console.log('Testing complete enhanced 5-step workflow...');
    
    const provider = providers[1]; // Use second provider for variation
    await selectProvider(page, provider);
    
    const baseTimestamp = Date.now();
    
    // Step 1: Retrieve with cloud indexes
    const retrievalPath = generateTimestampedPath('enhanced_retrieval');
    const question = 'What are NPDES permit requirements for industrial facilities in Washington State?';
    
    await performRetrieval(page, question, retrievalPath, {
      textIndexes: 'federal,state',
      topK: 30
    });
    
    const retrievalResult = await validateRetrievalOutput(path.resolve(retrievalPath));
    expect(retrievalResult.valid).toBeTruthy();
    
    // Step 2: Enhance context (outline, gaps)
    const enhancedPath = generateTimestampedPath('enhanced_context');
    
    await performEnhancement(page, retrievalPath, enhancedPath, 'detailed');
    
    const enhancedResult = await validateJsonFile(path.resolve(enhancedPath));
    expect(enhancedResult.valid).toBeTruthy();
    
    // Step 3: Generate draft
    const draftPath = generateTimestampedPath('enhanced_draft', 'md');
    
    await performGeneration(page, enhancedPath, draftPath, {
      style: 'technical'
    });
    
    const draftResult = await validateMarkdownFile(
      path.resolve(draftPath), 
      ['NPDES', 'permit', 'industrial', 'requirements'], 
      800
    );
    expect(draftResult.valid).toBeTruthy();
    
    // Step 4: Review/Judge quality
    const reviewJsonPath = generateTimestampedPath('enhanced_review_json');
    const reviewMdPath = generateTimestampedPath('enhanced_review_md', 'md');
    
    await performReview(page, enhancedPath, draftPath, reviewJsonPath, reviewMdPath, {
      strict: true,
      maxEvidence: 10
    });
    
    const reviewJsonResult = await validateJsonFile(path.resolve(reviewJsonPath));
    const reviewMdResult = await validateMarkdownFile(
      path.resolve(reviewMdPath), 
      ['review', 'analysis'], 
      300
    );
    
    expect(reviewJsonResult.valid).toBeTruthy();
    expect(reviewMdResult.valid).toBeTruthy();
    
    console.log('✅ Complete enhanced 5-step workflow completed successfully');
  });

  /**
   * Test: GraphRAG Workflow Simulation
   * Since the UI may not have full GraphRAG functionality exposed,
   * we test the closest equivalent workflow with mixed retrieval modes
   */
  test('GraphRAG-Style Mixed Retrieval Workflow', async ({ page }) => {
    console.log('Testing GraphRAG-style mixed retrieval workflow...');
    
    const provider = providers[2]; // Use third provider
    await selectProvider(page, provider);
    
    // Test with biosolids requirements as mentioned in system prompt
    const question = 'What are biosolids management and disposal requirements for municipal treatment plants?';
    const retrievalPath = generateTimestampedPath('graph_style_retrieval');
    
    // Perform retrieval with design standards (closest to graph + text mix)
    await performRetrieval(page, question, retrievalPath, {
      textIndexes: 'design,federal',
      topK: 25,
      rerankTopN: 10
    });
    
    const retrievalResult = await validateRetrievalOutput(path.resolve(retrievalPath));
    expect(retrievalResult.valid).toBeTruthy();
    expect(retrievalResult.nodeCount).toBeGreaterThan(8);
    
    // Generate from the mixed context
    const generationPath = generateTimestampedPath('graph_style_generation', 'md');
    
    await performGeneration(page, retrievalPath, generationPath, {
      style: 'technical'
    });
    
    const generationResult = await validateMarkdownFile(
      path.resolve(generationPath), 
      ['biosolids', 'management', 'disposal', 'municipal'], 
      600
    );
    expect(generationResult.valid).toBeTruthy();
    
    console.log('✅ GraphRAG-style mixed retrieval workflow completed successfully');
  });

  /**
   * Test: Multi-Provider Consistency Check
   * Validates that different providers can handle the same workflow
   * and produce reasonable outputs
   */
  test('Multi-Provider Workflow Consistency', async ({ page }) => {
    console.log('Testing multi-provider workflow consistency...');
    
    const question = 'What are key design considerations for activated sludge treatment systems?';
    const results: { provider: string; retrievalValid: boolean; generationValid: boolean }[] = [];
    
    // Test with first 3 providers to balance thoroughness and execution time
    for (const provider of providers.slice(0, 3)) {
      console.log(`Testing consistency with ${provider.name}...`);
      
      await selectProvider(page, provider);
      
      const timestamp = Date.now();
      const retrievalPath = `outputs/consistency_${provider.value}_retrieval_${timestamp}.json`;
      const generationPath = `outputs/consistency_${provider.value}_generation_${timestamp}.md`;
      
      // Perform standard workflow
      await performRetrieval(page, question, retrievalPath, {
        textIndexes: 'federal,design',
        topK: 20
      });
      
      await performGeneration(page, retrievalPath, generationPath, {
        style: 'technical'
      });
      
      // Validate outputs
      const retrievalResult = await validateRetrievalOutput(path.resolve(retrievalPath));
      const generationResult = await validateMarkdownFile(
        path.resolve(generationPath), 
        ['activated', 'sludge', 'treatment', 'design'], 
        400
      );
      
      results.push({
        provider: provider.name,
        retrievalValid: retrievalResult.valid,
        generationValid: generationResult.valid
      });
      
      expect(retrievalResult.valid).toBeTruthy();
      expect(generationResult.valid).toBeTruthy();
      
      // Brief pause between providers
      await page.waitForTimeout(2000);
    }
    
    // Verify all providers succeeded
    const successfulProviders = results.filter(r => r.retrievalValid && r.generationValid);
    expect(successfulProviders.length).toBe(3);
    
    console.log('✅ Multi-provider workflow consistency validated');
    console.log('Successful providers:', successfulProviders.map(r => r.provider).join(', '));
  });

  /**
   * Test: Error Handling and Edge Cases
   * Tests the robustness of workflows with various edge cases
   */
  test('Workflow Error Handling and Edge Cases', async ({ page }) => {
    console.log('Testing workflow error handling and edge cases...');
    
    const provider = providers[0];
    await selectProvider(page, provider);
    
    // Test 1: Empty question handling
    await page.click('[data-value="tab-retrieval"]');
    await page.fill('#ret-question', '');
    await page.fill('#ret-out', generateTimestampedPath('empty_test'));
    await page.click('#btn-retrieve');
    
    const emptyAlert = await waitForAlertAndGetText(page, 10000);
    expect(emptyAlert.type).toBe('warning');
    expect(emptyAlert.text.toLowerCase()).toContain('question');
    
    // Test 2: Very short question
    await page.fill('#ret-question', 'G1?');
    await page.fill('#ret-out', generateTimestampedPath('short_test'));
    await page.click('#btn-retrieve');
    
    // Should either succeed or provide appropriate feedback
    const shortAlert = await waitForAlertAndGetText(page, 90000);
    expect(['success', 'warning', 'info']).toContain(shortAlert.type);
    
    // Test 3: Generation without proper context
    await page.click('[data-value="tab-generate"]');
    await page.fill('#gen-ctx', 'nonexistent_file.json');
    await page.fill('#gen-out', generateTimestampedPath('invalid_ctx_test', 'md'));
    await page.click('#btn-generate');
    
    const invalidCtxAlert = await waitForAlertAndGetText(page, 30000);
    expect(['danger', 'warning']).toContain(invalidCtxAlert.type);
    
    console.log('✅ Workflow error handling validated successfully');
  });

  /**
   * Test: Performance and Timeout Handling
   * Ensures workflows complete within reasonable timeframes
   */
  test('Workflow Performance and Timeout Handling', async ({ page }) => {
    console.log('Testing workflow performance and timeout handling...');
    
    const provider = providers[0];
    await selectProvider(page, provider);
    
    // Test with a complex question that should take moderate time
    const complexQuestion = 'Provide a comprehensive analysis of advanced biological nutrient removal technologies for municipal wastewater treatment plants, including process design considerations, operational requirements, and regulatory compliance aspects for phosphorus and nitrogen removal in Washington State.';
    
    const startTime = Date.now();
    
    // Perform retrieval with higher node count
    const retrievalPath = generateTimestampedPath('performance_retrieval');
    
    await performRetrieval(page, complexQuestion, retrievalPath, {
      textIndexes: 'federal,state,design',
      topK: 35,
      rerankTopN: 15
    });
    
    const retrievalTime = Date.now() - startTime;
    console.log(`Retrieval completed in ${retrievalTime}ms`);
    
    // Validate retrieval succeeded and took reasonable time (< 2 minutes as per strategy)
    expect(retrievalTime).toBeLessThan(120000); // 2 minutes max
    
    const retrievalResult = await validateRetrievalOutput(path.resolve(retrievalPath));
    expect(retrievalResult.valid).toBeTruthy();
    expect(retrievalResult.nodeCount).toBeGreaterThan(10);
    
    // Perform generation
    const genStartTime = Date.now();
    const generationPath = generateTimestampedPath('performance_generation', 'md');
    
    await performGeneration(page, retrievalPath, generationPath, {
      style: 'comprehensive'
    });
    
    const generationTime = Date.now() - genStartTime;
    console.log(`Generation completed in ${generationTime}ms`);
    
    // Validate generation succeeded and took reasonable time (< 3 minutes as per strategy)
    expect(generationTime).toBeLessThan(180000); // 3 minutes max
    
    const generationResult = await validateMarkdownFile(
      path.resolve(generationPath), 
      ['biological', 'nutrient', 'removal', 'phosphorus', 'nitrogen'], 
      1000
    );
    expect(generationResult.valid).toBeTruthy();
    
    const totalTime = Date.now() - startTime;
    console.log(`Total workflow completed in ${totalTime}ms`);
    
    console.log('✅ Performance and timeout handling validated successfully');
  });

  /**
   * Test: File Output Quality and Structure
   * Validates that all generated files meet expected quality standards
   */
  test('File Output Quality and Structure Validation', async ({ page }) => {
    console.log('Testing file output quality and structure...');
    
    const provider = providers[1];
    await selectProvider(page, provider);
    
    const question = 'What are the monitoring and reporting requirements for municipal wastewater treatment plants under Washington State regulations?';
    
    // Step 1: Generate retrieval with comprehensive validation
    const retrievalPath = generateTimestampedPath('quality_retrieval');
    
    await performRetrieval(page, question, retrievalPath, {
      textIndexes: 'state,federal',
      topK: 25
    });
    
    // Comprehensive retrieval validation
    const retrievalResult = await validateRetrievalOutput(path.resolve(retrievalPath));
    expect(retrievalResult.valid).toBeTruthy();
    
    // Read and validate JSON structure
    const retrievalContent = JSON.parse(await fs.readFile(path.resolve(retrievalPath), 'utf-8'));
    expect(retrievalContent).toHaveProperty('retrieval');
    expect(retrievalContent.retrieval).toHaveProperty('nodes');
    expect(Array.isArray(retrievalContent.retrieval.nodes)).toBeTruthy();
    expect(retrievalContent.retrieval.nodes.length).toBeGreaterThan(5);
    
    // Validate nodes have required properties
    const firstNode = retrievalContent.retrieval.nodes[0];
    expect(firstNode).toHaveProperty('node');
    expect(firstNode.node).toHaveProperty('text');
    expect(firstNode.node.text.length).toBeGreaterThan(50);
    
    // Step 2: Generate with comprehensive validation
    const generationPath = generateTimestampedPath('quality_generation', 'md');
    
    await performGeneration(page, retrievalPath, generationPath, {
      style: 'comprehensive'
    });
    
    // Comprehensive generation validation
    const generationResult = await validateMarkdownFile(
      path.resolve(generationPath), 
      ['monitoring', 'reporting', 'municipal', 'regulations'], 
      800
    );
    expect(generationResult.valid).toBeTruthy();
    
    // Read and validate markdown structure
    const generationContent = await fs.readFile(path.resolve(generationPath), 'utf-8');
    expect(generationContent.length).toBeGreaterThan(800);
    expect(generationContent).toMatch(/#{1,3}\s/); // Should have headers
    expect(generationContent.toLowerCase()).toContain('washington');
    
    console.log('✅ File output quality and structure validation completed successfully');
  });
});