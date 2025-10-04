import { test, expect } from '@playwright/test';
import { 
  providers, 
  engineeringQuestions, 
  selectProvider, 
  performRetrieval, 
  performGeneration,
  validateRetrievalOutput,
  validateMarkdownFile,
  measureResponseTime,
  generateTimestampedPath,
  ensureOutputDirectory,
  waitForAlertAndGetText
} from './test-utils';

test.describe('Caliper v2 Performance & Reliability Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Caliper v2/);
    await page.waitForLoadState('networkidle');
    await ensureOutputDirectory();
  });

  test('Response Time Benchmarking - All Providers', async ({ page }) => {
    const results: Array<{
      provider: string;
      retrievalTime: number;
      generationTime: number;
      retrievalSuccess: boolean;
      generationSuccess: boolean;
    }> = [];

    const testQuestion = engineeringQuestions[0];

    for (const provider of providers) {
      console.log(`Benchmarking ${provider.name}...`);
      
      await selectProvider(page, provider);
      
      const retrievalPath = generateTimestampedPath(`perf_${provider.value}_retrieval`);
      const generationPath = generateTimestampedPath(`perf_${provider.value}_generation`, 'md');

      // Measure retrieval time
      const retrievalResult = await measureResponseTime(page, async () => {
        await performRetrieval(page, testQuestion.question, retrievalPath);
      });

      // Measure generation time
      const generationResult = await measureResponseTime(page, async () => {
        await performGeneration(page, retrievalPath, generationPath, { style: 'technical' });
      });

      results.push({
        provider: provider.name,
        retrievalTime: retrievalResult.duration,
        generationTime: generationResult.duration,
        retrievalSuccess: retrievalResult.success,
        generationSuccess: generationResult.success
      });

      // Log individual results
      console.log(`${provider.name}: Retrieval ${retrievalResult.duration}ms (${retrievalResult.success ? 'SUCCESS' : 'FAILED'}), Generation ${generationResult.duration}ms (${generationResult.success ? 'SUCCESS' : 'FAILED'})`);

      // Small delay between providers
      await page.waitForTimeout(2000);
    }

    // Analyze results
    const successfulProviders = results.filter(r => r.retrievalSuccess && r.generationSuccess);
    const avgRetrievalTime = successfulProviders.reduce((sum, r) => sum + r.retrievalTime, 0) / successfulProviders.length;
    const avgGenerationTime = successfulProviders.reduce((sum, r) => sum + r.generationTime, 0) / successfulProviders.length;

    console.log('\n=== Performance Summary ===');
    console.log(`Successful providers: ${successfulProviders.length}/${results.length}`);
    console.log(`Average retrieval time: ${avgRetrievalTime.toFixed(0)}ms`);
    console.log(`Average generation time: ${avgGenerationTime.toFixed(0)}ms`);

    // Expectations
    expect(successfulProviders.length).toBeGreaterThanOrEqual(3); // At least 3 providers should work
    expect(avgRetrievalTime).toBeLessThan(120000); // Average retrieval under 2 minutes
    expect(avgGenerationTime).toBeLessThan(180000); // Average generation under 3 minutes

    // Write results to file for analysis
    const reportPath = generateTimestampedPath('performance_report', 'json');
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        successfulProviders: successfulProviders.length,
        totalProviders: results.length,
        avgRetrievalTime,
        avgGenerationTime
      },
      results
    };
    
    await import('fs/promises').then(fs => 
      fs.writeFile(reportPath, JSON.stringify(report, null, 2), 'utf-8')
    );

    console.log(`Performance report saved to: ${reportPath}`);
  });

  test('Error Recovery and Resilience', async ({ page }) => {
    const provider = providers[0]; // Use first provider
    await selectProvider(page, provider);

    // Test 1: Recovery from invalid question
    console.log('Testing recovery from empty question...');
    await page.click('[data-value="tab-retrieval"]');
    await page.fill('#ret-question', '');
    await page.fill('#ret-out', generateTimestampedPath('error_test_empty_q'));
    await page.click('#btn-retrieve');

    let alert = await waitForAlertAndGetText(page, 10000);
    expect(alert.type).toBe('warning');
    expect(alert.text.toLowerCase()).toContain('question');

    // Test 2: Recovery from invalid output path
    console.log('Testing recovery from invalid output path...');
    await page.fill('#ret-question', 'test question');
    await page.fill('#ret-out', '<invalid>:|path');
    await page.click('#btn-retrieve');

    alert = await waitForAlertAndGetText(page, 10000);
    // Should either handle gracefully or show appropriate error
    expect(['warning', 'danger', 'success']).toContain(alert.type);

    // Test 3: Provider switching resilience
    console.log('Testing provider switching...');
    for (let i = 0; i < 3; i++) {
      const testProvider = providers[i % providers.length];
      await selectProvider(page, testProvider);
      
      // Verify provider can handle basic request
      const testPath = generateTimestampedPath(`switch_test_${testProvider.value}`);
      await page.fill('#ret-question', engineeringQuestions[0].question);
      await page.fill('#ret-out', testPath);
      await page.click('#btn-retrieve');

      alert = await waitForAlertAndGetText(page, 60000);
      
      if (alert.type === 'success') {
        console.log(`✅ ${testProvider.name} handled request successfully`);
      } else {
        console.log(`⚠️ ${testProvider.name} had issues: ${alert.text}`);
      }

      await page.waitForTimeout(1000);
    }

    console.log('✅ Error recovery tests completed');
  });

  test('Concurrent Request Handling', async ({ page }) => {
    const provider = providers[1]; // Use OpenAI
    await selectProvider(page, provider);

    const testQuestion = engineeringQuestions[1];
    
    // Test rapid sequential requests
    const promises = [];
    const paths = [];
    
    for (let i = 0; i < 3; i++) {
      const retrievalPath = generateTimestampedPath(`concurrent_${i}_retrieval`);
      paths.push(retrievalPath);
      
      // Don't await - start all requests concurrently
      promises.push((async () => {
        try {
          await performRetrieval(page, testQuestion.question, retrievalPath);
          return { success: true, path: retrievalPath };
        } catch (error) {
          return { success: false, path: retrievalPath, error };
        }
      })());
    }

    // Wait for all to complete
    const results = await Promise.allSettled(promises);
    
    // Analyze results
    let successCount = 0;
    for (const result of results) {
      if (result.status === 'fulfilled' && result.value.success) {
        successCount++;
      }
    }

    console.log(`Concurrent requests: ${successCount}/${results.length} succeeded`);
    
    // At least one should succeed (others might fail due to rate limiting)
    expect(successCount).toBeGreaterThanOrEqual(1);
    
    // Validate successful outputs
    for (const path of paths) {
      try {
        const validation = await validateRetrievalOutput(path);
        if (validation.valid) {
          console.log(`✅ Output ${path} valid with ${validation.nodeCount} nodes`);
        }
      } catch (error) {
        // Some may not exist if request failed
        console.log(`⚠️ Could not validate ${path}`);
      }
    }
  });

  test('Long-running Operation Stability', async ({ page }) => {
    const provider = providers[2]; // Use Anthropic
    await selectProvider(page, provider);

    // Use a complex question that should take longer to process
    const complexQuestion = `Provide a comprehensive analysis of the regulatory framework for wastewater treatment plant design in Washington State, including federal regulations (Clean Water Act, EPA guidelines), state regulations (Washington Administrative Code), local requirements, permitting processes, design standards for biological nutrient removal, monitoring and reporting requirements, and compliance deadlines. Include specific citations and explain how these regulations interact with each other.`;

    const retrievalPath = generateTimestampedPath('stability_retrieval');
    const generationPath = generateTimestampedPath('stability_generation', 'md');

    console.log('Starting long-running stability test...');

    // Perform retrieval with extended timeout
    const startTime = Date.now();
    await performRetrieval(page, complexQuestion, retrievalPath);
    const retrievalTime = Date.now() - startTime;

    // Validate retrieval
    const retrievalValidation = await validateRetrievalOutput(retrievalPath);
    expect(retrievalValidation.valid).toBeTruthy();
    console.log(`Retrieval completed in ${retrievalTime}ms with ${retrievalValidation.nodeCount} nodes`);

    // Perform generation
    const genStartTime = Date.now();
    await performGeneration(page, retrievalPath, generationPath, { style: 'comprehensive' });
    const generationTime = Date.now() - genStartTime;

    // Validate generation
    const generationValidation = await validateMarkdownFile(generationPath, ['regulation', 'treatment', 'permit'], 1000);
    expect(generationValidation.valid).toBeTruthy();
    console.log(`Generation completed in ${generationTime}ms`);

    // Log performance metrics
    const totalTime = retrievalTime + generationTime;
    console.log(`Total operation time: ${totalTime}ms (${(totalTime/1000/60).toFixed(1)} minutes)`);

    // Expectations for stability
    expect(totalTime).toBeLessThan(600000); // Should complete within 10 minutes
    expect(retrievalValidation.nodeCount).toBeGreaterThan(5); // Should retrieve meaningful content
    
    if (generationValidation.content) {
      expect(generationValidation.content.length).toBeGreaterThan(2000); // Should generate substantial content
    }
  });

  test('Memory and Resource Usage Stability', async ({ page }) => {
    const provider = providers[0]; // Use Cohere
    await selectProvider(page, provider);

    // Perform multiple operations to test memory stability
    const iterations = 5;
    const results = [];

    for (let i = 0; i < iterations; i++) {
      console.log(`Memory stability test iteration ${i + 1}/${iterations}`);
      
      const question = engineeringQuestions[i % engineeringQuestions.length];
      const retrievalPath = generateTimestampedPath(`memory_${i}_retrieval`);
      const generationPath = generateTimestampedPath(`memory_${i}_generation`, 'md');

      const startTime = Date.now();
      
      try {
        await performRetrieval(page, question.question, retrievalPath);
        await performGeneration(page, retrievalPath, generationPath);
        
        const duration = Date.now() - startTime;
        results.push({ iteration: i, duration, success: true });
        
        console.log(`Iteration ${i + 1} completed in ${duration}ms`);
        
        // Small delay between iterations
        await page.waitForTimeout(2000);
        
      } catch (error) {
        const duration = Date.now() - startTime;
        results.push({ iteration: i, duration, success: false, error });
        console.log(`Iteration ${i + 1} failed after ${duration}ms:`, error);
      }
    }

    // Analyze results for degradation
    const successfulResults = results.filter(r => r.success);
    const successRate = successfulResults.length / results.length;
    
    console.log(`Memory stability test: ${successfulResults.length}/${results.length} iterations successful`);
    
    if (successfulResults.length > 1) {
      const avgTime = successfulResults.reduce((sum, r) => sum + r.duration, 0) / successfulResults.length;
      const lastHalfAvg = successfulResults.slice(-Math.ceil(successfulResults.length / 2))
        .reduce((sum, r) => sum + r.duration, 0) / Math.ceil(successfulResults.length / 2);
      
      console.log(`Average time: ${avgTime.toFixed(0)}ms, Last half average: ${lastHalfAvg.toFixed(0)}ms`);
      
      // Check for significant performance degradation (more than 50% slower)
      if (lastHalfAvg > avgTime * 1.5) {
        console.warn('Performance degradation detected in later iterations');
      }
    }

    // Expectations
    expect(successRate).toBeGreaterThanOrEqual(0.8); // At least 80% success rate
  });
});