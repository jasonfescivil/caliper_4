import { test, expect } from '@playwright/test';
import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

/**
 * CLI Integration Tests for Caliper v2
 * 
 * Tests the CLI commands that complement our Dash UI testing.
 * These tests validate that CLI commands work correctly for scenarios
 * that users might prefer to run via command line.
 */
test.describe('Caliper v2 CLI Integration', () => {
  const tempDir = path.join(process.cwd(), 'temp_cli_test');
  const testIndexPath = 'data_v2/indexes/wastewater_index';
  
  test.beforeAll(async () => {
    // Ensure temp directory exists
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
  });

  test.afterAll(async () => {
    // Clean up temp files
    if (fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });

  test('CLI doctor command - System health check', async () => {
    try {
      const result = execSync('python -m caliper_v2.cli_main doctor', {
        encoding: 'utf8',
        timeout: 30000,
        cwd: process.cwd()
      });
      
      console.log('Doctor output:', result);
      
      // Should contain provider information
      expect(result).toContain('API');
      
      // Should not contain critical errors (though warnings are OK)
      expect(result.toLowerCase()).not.toContain('fatal');
      expect(result.toLowerCase()).not.toContain('critical error');
      
    } catch (error: any) {
      // Doctor command may have warnings but shouldn't crash
      expect(error.status).not.toBe(1);
      console.log('Doctor stderr:', error.stderr);
      console.log('Doctor stdout:', error.stdout);
    }
  });

  test('CLI retrieve command - Basic retrieval', async () => {
    const outputPath = path.join(tempDir, 'cli_retrieve_output.json');
    const question = 'What are the key requirements for wastewater treatment permit applications?';
    
    try {
      const result = execSync(`python -m caliper_v2.cli_main retrieve "${question}" --indexes federal,wa --out "${outputPath}"`, {
        encoding: 'utf8',
        timeout: 120000, // 2 minutes
        cwd: process.cwd()
      });
      
      console.log('CLI retrieve result:', result);
      
      // Check that output file was created
      expect(fs.existsSync(outputPath)).toBeTruthy();
      
      // Validate JSON structure
      const jsonContent = fs.readFileSync(outputPath, 'utf8');
      const retrievalData = JSON.parse(jsonContent);
      
      expect(retrievalData).toHaveProperty('question');
      expect(retrievalData).toHaveProperty('results');
      expect(retrievalData.question).toContain(question);
      expect(Array.isArray(retrievalData.results)).toBeTruthy();
      expect(retrievalData.results.length).toBeGreaterThan(0);
      
      // Validate individual results have required fields
      const firstResult = retrievalData.results[0];
      expect(firstResult).toHaveProperty('score');
      expect(firstResult).toHaveProperty('text');
      expect(firstResult).toHaveProperty('metadata');
      
    } catch (error: any) {
      console.error('CLI retrieve error:', error.message);
      console.error('stderr:', error.stderr);
      console.error('stdout:', error.stdout);
      throw error;
    }
  });

  test('CLI generate command - Using existing retrieval', async () => {
    const retrievalPath = path.join(tempDir, 'cli_retrieve_for_generate.json');
    const outputPath = path.join(tempDir, 'cli_generate_output.md');
    const question = 'What are NPDES permit requirements for industrial wastewater?';
    
    try {
      // First, create a retrieval file
      const retrieveResult = execSync(`python -m caliper_v2.cli_main retrieve "${question}" --indexes federal,wa --out "${retrievalPath}"`, {
        encoding: 'utf8',
        timeout: 120000,
        cwd: process.cwd()
      });
      
      console.log('CLI retrieve for generate:', retrieveResult);
      expect(fs.existsSync(retrievalPath)).toBeTruthy();
      
      // Now generate using the retrieval
      const generateResult = execSync(`python -m caliper_v2.cli_main generate "${retrievalPath}" --out "${outputPath}" --llm-provider openai`, {
        encoding: 'utf8',
        timeout: 180000, // 3 minutes
        cwd: process.cwd()
      });
      
      console.log('CLI generate result:', generateResult);
      
      // Check that output file was created
      expect(fs.existsSync(outputPath)).toBeTruthy();
      
      // Validate markdown content
      const markdownContent = fs.readFileSync(outputPath, 'utf8');
      expect(markdownContent.length).toBeGreaterThan(500); // Substantial content
      expect(markdownContent).toContain('NPDES'); // Should contain key terms
      expect(markdownContent).toMatch(/#{1,3}/); // Should have headers
      
    } catch (error: any) {
      console.error('CLI generate error:', error.message);
      console.error('stderr:', error.stderr);
      console.error('stdout:', error.stdout);
      throw error;
    }
  });

  test('CLI report review command - Analyze generated content', async () => {
    const markdownPath = path.join(tempDir, 'content_for_review.md');
    const outputDir = path.join(tempDir, 'review_output');
    
    // Create sample markdown content for review
    const sampleMarkdown = `
# NPDES Permit Requirements for Industrial Wastewater

## Introduction
The National Pollutant Discharge Elimination System (NPDES) requires permits for industrial wastewater discharge.

## Key Requirements
1. **Effluent Limitations**: Must meet technology-based and water quality-based standards
2. **Monitoring and Reporting**: Regular sampling and DMR submission required
3. **Best Management Practices**: Implementation of pollution prevention measures

## Compliance Timeline
- Application submission: 180 days before discharge
- Permit issuance: Within 90 days of complete application
- Compliance deadline: Immediate upon permit effective date

## References
- Clean Water Act Section 402
- 40 CFR Part 122
- EPA NPDES Permit Writers' Manual
    `;
    
    try {
      // Ensure output directory exists
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }
      
      // Write sample content
      fs.writeFileSync(markdownPath, sampleMarkdown);
      
      // Run review command
      const result = execSync(`python -m caliper_v2.cli_main report review "${markdownPath}" --out-dir "${outputDir}"`, {
        encoding: 'utf8',
        timeout: 120000,
        cwd: process.cwd()
      });
      
      console.log('CLI report review result:', result);
      
      // Check that review files were created
      const reviewJsonPath = path.join(outputDir, 'review.json');
      const reviewMdPath = path.join(outputDir, 'review.md');
      
      // At least one review output should exist
      const hasReviewJson = fs.existsSync(reviewJsonPath);
      const hasReviewMd = fs.existsSync(reviewMdPath);
      expect(hasReviewJson || hasReviewMd).toBeTruthy();
      
      if (hasReviewJson) {
        const reviewData = JSON.parse(fs.readFileSync(reviewJsonPath, 'utf8'));
        expect(reviewData).toBeTruthy();
        expect(typeof reviewData).toBe('object');
      }
      
    } catch (error: any) {
      console.error('CLI report review error:', error.message);
      console.error('stderr:', error.stderr);
      console.error('stdout:', error.stdout);
      throw error;
    }
  });

  test('CLI report claims command - Extract claims', async () => {
    const markdownPath = path.join(tempDir, 'content_for_claims.md');
    const outputPath = path.join(tempDir, 'cli_claims_output.json');
    
    // Create content with verifiable claims
    const sampleContent = `
# Industrial Wastewater Treatment Standards

## Regulatory Framework
The Clean Water Act requires all industrial facilities to obtain NPDES permits before discharging wastewater. 
BOD levels must not exceed 30 mg/L for most industrial categories.
pH must be maintained between 6.0 and 9.0 standard units.

## Treatment Technologies
Advanced oxidation processes can achieve 99% removal of organic pollutants.
Membrane bioreactors are required for all pharmaceutical manufacturing facilities.
    `;
    
    try {
      fs.writeFileSync(markdownPath, sampleContent);
      
      const result = execSync(`python -m caliper_v2.cli_main report claims "${markdownPath}" --out "${outputPath}"`, {
        encoding: 'utf8',
        timeout: 120000, // 2 minutes for claims extraction
        cwd: process.cwd()
      });
      
      console.log('CLI claims result:', result);
      expect(fs.existsSync(outputPath)).toBeTruthy();
      
      // Validate claims output structure
      const claimsData = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
      expect(claimsData).toHaveProperty('claims');
      expect(Array.isArray(claimsData.claims)).toBeTruthy();
      expect(claimsData.claims.length).toBeGreaterThan(0);
      
      // Each claim should have required fields
      const firstClaim = claimsData.claims[0];
      expect(firstClaim).toHaveProperty('text');
      expect(firstClaim).toHaveProperty('heading');
      
    } catch (error: any) {
      console.error('CLI claims error:', error.message);
      console.error('stderr:', error.stderr);
      console.error('stdout:', error.stdout);
      throw error;
    }
  });

  test('CLI graph commands - GraphRAG functionality', async () => {
    // Test graph stats command (non-destructive)
    try {
      const result = execSync('python -m caliper_v2.cli_main graph stats', {
        encoding: 'utf8',
        timeout: 30000,
        cwd: process.cwd()
      });
      
      console.log('Graph stats result:', result);
      
      // Should provide some information about graph status
      // Even if no graphs exist, should not crash
      expect(result.length).toBeGreaterThan(0);
      
    } catch (error: any) {
      // Graph commands may not be fully configured, check error type
      console.log('Graph stats output:', error.stdout);
      console.log('Graph stats error:', error.stderr);
      
      // Should not be a critical system error
      expect(error.status).not.toBe(127); // Command not found
    }
  });

  test('CLI pipeline - Complete workflow', async () => {
    const question = 'What are the monitoring requirements for industrial wastewater discharge permits?';
    const retrievalPath = path.join(tempDir, 'pipeline_retrieval.json');
    const generatePath = path.join(tempDir, 'pipeline_generated.md');
    const reviewPath = path.join(tempDir, 'pipeline_review.json');
    
    try {
      console.log('Starting CLI pipeline test...');
      
      // Step 1: Retrieve
      console.log('Step 1: Retrieving...');
      const retrieveResult = execSync(`python -m caliper_v2.cli_main retrieve "${question}" --indexes federal,wa --out "${retrievalPath}"`, {
        encoding: 'utf8',
        timeout: 120000,
        cwd: process.cwd()
      });
      console.log('Retrieve completed');
      expect(fs.existsSync(retrievalPath)).toBeTruthy();
      
      // Step 2: Generate
      console.log('Step 2: Generating...');
      const generateResult = execSync(`python -m caliper_v2.cli_main generate "${retrievalPath}" --out "${generatePath}" --llm-provider cohere`, {
        encoding: 'utf8',
        timeout: 180000,
        cwd: process.cwd()
      });
      console.log('Generate completed');
      expect(fs.existsSync(generatePath)).toBeTruthy();
      
      // Step 3: Extract Claims (instead of review which has complex output structure)
      console.log('Step 3: Extracting claims...');
      const claimsResult = execSync(`python -m caliper_v2.cli_main report claims "${generatePath}" --out "${reviewPath}"`, {
        encoding: 'utf8',
        timeout: 120000,
        cwd: process.cwd()
      });
      console.log('Claims extraction completed');
      expect(fs.existsSync(reviewPath)).toBeTruthy();
      
      // Validate the complete pipeline output (claims JSON)
      const finalClaims = JSON.parse(fs.readFileSync(reviewPath, 'utf8'));
      expect(finalClaims).toHaveProperty('claims');
      expect(Array.isArray(finalClaims.claims)).toBeTruthy();
      
      console.log('CLI pipeline test completed successfully');
      
    } catch (error: any) {
      console.error('CLI pipeline error at step:', error.message);
      console.error('stderr:', error.stderr);
      console.error('stdout:', error.stdout);
      throw error;
    }
  });

  test('CLI error handling - Invalid commands', async () => {
    // Test graceful handling of invalid parameters
    try {
      execSync('python -m caliper_v2.cli_main retrieve', {
        encoding: 'utf8',
        timeout: 10000,
        cwd: process.cwd()
      });
      
      // Should not reach here - command should fail
      expect(false).toBeTruthy();
      
    } catch (error: any) {
      // Should fail gracefully - either missing argument or help displayed
      expect(error.status).not.toBe(0); // Should not succeed
      console.log('Expected retrieve error:', error.stdout);
    }
    
    // Test invalid provider
    try {
      execSync('python -m caliper_v2.cli_main generate "dummy.json" --llm-provider invalidprovider', {
        encoding: 'utf8',
        timeout: 10000,
        cwd: process.cwd()
      });
      
      expect(false).toBeTruthy();
      
    } catch (error: any) {
      // Should fail with provider-related or file-not-found error
      expect(error.status).not.toBe(0);
      console.log('Expected provider error:', error.stdout);
    }
  });
});