import { Page } from '@playwright/test';
import { promises as fs } from 'fs';

export interface Provider {
  name: string;
  value: string;
  model: string;
}

export interface TestQuestion {
  id: string;
  question: string;
  expectedContent: string[];
}

// Common test data - Updated to match latest system prompt providers
export const providers: Provider[] = [
  { name: 'OpenAI', value: 'openai', model: 'gpt-5' },
  { name: 'Anthropic', value: 'anthropic', model: 'claude-opus-4.1' },
  { name: 'Google Gemini', value: 'gemini', model: 'gemini-2.5-pro-preview' },
  { name: 'Cohere', value: 'cohere', model: 'command-a-reasoning' },
  { name: 'xAI Grok', value: 'xai', model: 'grok-2-1212' },
];

export const engineeringQuestions: TestQuestion[] = [
  {
    id: 'wwtp_design',
    question: 'What are the key design considerations for a 2.5 MGD activated sludge wastewater treatment plant with biological nutrient removal in Washington State?',
    expectedContent: ['activated sludge', 'biological', 'nutrient', 'MGD', 'design']
  },
  {
    id: 'permit_compliance',
    question: 'What are the monitoring and reporting requirements for industrial facilities with NPDES permits in Washington State?',
    expectedContent: ['NPDES', 'monitoring', 'industrial', 'reporting', 'permit']
  },
  {
    id: 'stormwater_management',
    question: 'How should stormwater runoff be managed for a new industrial facility to comply with Washington State regulations?',
    expectedContent: ['stormwater', 'runoff', 'industrial', 'regulations', 'management']
  },
  {
    id: 'biosolids_handling',
    question: 'What are the requirements for biosolids management and disposal from municipal wastewater treatment plants in Washington?',
    expectedContent: ['biosolids', 'disposal', 'municipal', 'treatment', 'management']
  },
];

// Utility functions
export async function selectProvider(page: Page, provider: Provider): Promise<void> {
  // The provider selector is a combobox with options
  await page.selectOption('select', provider.value);
  
  // Fill model field (textbox with placeholder "Model (optional)")
  await page.locator('input[placeholder*="Model"]').first().fill('');
  await page.locator('input[placeholder*="Model"]').first().fill(provider.model);
  
  // Click Apply button
  await page.getByRole('button', { name: 'Apply' }).click();
  
  // Wait for provider application
  await page.waitForTimeout(1000);
}

export async function performRetrieval(page: Page, question: string, outputPath: string, options?: {
  textIndexes?: string;
  topK?: number;
  rerankTopN?: number;
}): Promise<void> {
  // Navigate to retrieval tab by clicking on the tab button
  await page.locator('div').filter({ hasText: /^🔎 Retrieval$/ }).click();
  
  // Fill basic fields
  await page.getByRole('textbox', { name: 'Question/Prompt' }).fill(question);
  await page.getByRole('textbox', { name: 'Output Path' }).first().fill(outputPath);
  
  // Fill optional fields if provided
  if (options?.textIndexes) {
    // Use more specific selector - the first Indexes field in the Cloud Text section
    await page.locator('input[id="ret-indexes"]').fill(options.textIndexes);
  }
  if (options?.topK) {
    // Find Top-K spinbutton by its accessible name
    await page.getByRole('spinbutton', { name: 'Top-K Results' }).fill(options.topK.toString());
  }
  if (options?.rerankTopN) {
    // Find Rerank spinbutton by its accessible name
    await page.getByRole('spinbutton', { name: 'Rerank Top-N' }).fill(options.rerankTopN.toString());
  }
  
  // Click retrieve
  await page.getByRole('button', { name: /Run Retrieval/ }).click();
  
  // Wait for completion
  await page.waitForSelector('.alert-success', { timeout: 90000 });
}

export async function performGeneration(page: Page, contextPath: string, outputPath: string, options?: {
  style?: string;
  maxTokens?: number;
}): Promise<void> {
  // Navigate to generate tab
  await page.locator('div').filter({ hasText: /^🧪 Generate$/ }).click();
  
  // Fill basic fields
  await page.getByRole('textbox', { name: 'Context Path' }).fill(contextPath);
  await page.getByRole('textbox', { name: 'Output Path' }).fill(outputPath);
  
  // Set options
  if (options?.style) {
    await page.getByRole('combobox', { name: 'Generation Style' }).selectOption(options.style);
  }
  
  // Click generate
  await page.getByRole('button', { name: /Generate/ }).click();
  
  // Wait for completion
  await page.waitForSelector('.alert-success', { timeout: 150000 });
}

export async function performEnhancement(page: Page, contextPath: string, outputPath: string, strategy: string = 'detailed'): Promise<void> {
  await page.locator('div').filter({ hasText: /^✨ Enhance$/ }).click();
  await page.getByRole('textbox', { name: 'Context Input Path' }).fill(contextPath);
  await page.getByRole('textbox', { name: 'Enhanced Output Path' }).fill(outputPath);
  await page.getByRole('button', { name: /Enhance Context/ }).click();
  await page.waitForSelector('.alert-success', { timeout: 120000 });
}

export async function performReview(page: Page, contextPath: string, draftPath: string, jsonOutput: string, mdOutput: string, options?: {
  strict?: boolean;
  maxEvidence?: number;
}): Promise<void> {
  await page.locator('div').filter({ hasText: /^⚖️ Judge & Review$/ }).click();
  await page.getByRole('textbox', { name: 'Context Path' }).fill(contextPath);
  await page.getByRole('textbox', { name: 'Draft Path' }).fill(draftPath);
  await page.getByRole('textbox', { name: 'JSON Output' }).fill(jsonOutput);
  await page.getByRole('textbox', { name: 'Markdown Output' }).fill(mdOutput);
  
  if (options?.strict) {
    await page.getByRole('checkbox', { name: 'Strict Mode' }).check();
  }
  if (options?.maxEvidence) {
    await page.getByRole('spinbutton', { name: 'Max Evidence per Claim' }).fill(options.maxEvidence.toString());
  }
  
  await page.getByRole('button', { name: /Run Full Review/ }).click();
  await page.waitForSelector('.alert-success', { timeout: 120000 });
}

// Validation functions
export async function validateJsonFile(filePath: string): Promise<{ valid: boolean; content?: any; error?: string }> {
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    if (content.length < 50) {
      return { valid: false, error: `File too short: ${content.length} characters` };
    }
    
    const parsed = JSON.parse(content);
    return { valid: true, content: parsed };
  } catch (error) {
    return { valid: false, error: `Parse error: ${error}` };
  }
}

export async function validateMarkdownFile(filePath: string, expectedContent: string[], minLength: number = 200): Promise<{ valid: boolean; content?: string; error?: string; missingKeywords?: string[] }> {
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    
    if (content.length < minLength) {
      return { valid: false, error: `File too short: ${content.length} characters (minimum: ${minLength})` };
    }
    
    const lowerContent = content.toLowerCase();
    const missingKeywords = expectedContent.filter(keyword => 
      !lowerContent.includes(keyword.toLowerCase())
    );
    
    return {
      valid: missingKeywords.length === 0,
      content,
      missingKeywords: missingKeywords.length > 0 ? missingKeywords : undefined
    };
  } catch (error) {
    return { valid: false, error: `Read error: ${error}` };
  }
}

export async function validateRetrievalOutput(filePath: string): Promise<{ valid: boolean; nodeCount?: number; error?: string }> {
  const { valid, content, error } = await validateJsonFile(filePath);
  
  if (!valid) {
    return { valid: false, error };
  }
  
  // Check for expected retrieval structure
  const nodes = content?.retrieval?.nodes || content?.nodes || [];
  if (!Array.isArray(nodes) || nodes.length === 0) {
    return { valid: false, error: 'No retrieval nodes found in output' };
  }
  
  return { valid: true, nodeCount: nodes.length };
}

// Error handling utilities
export async function waitForAlertAndGetText(page: Page, timeout: number = 10000): Promise<{ type: 'success' | 'warning' | 'danger' | 'info' | null; text: string }> {
  try {
    // Wait for any alert to appear
    await page.waitForSelector('.alert', { timeout });
    
    // Determine alert type
    const alertElement = page.locator('.alert').first();
    const classes = await alertElement.getAttribute('class') || '';
    
    let type: 'success' | 'warning' | 'danger' | 'info' | null = null;
    if (classes.includes('alert-success')) type = 'success';
    else if (classes.includes('alert-warning')) type = 'warning';
    else if (classes.includes('alert-danger')) type = 'danger';
    else if (classes.includes('alert-info')) type = 'info';
    
    const text = await alertElement.textContent() || '';
    
    return { type, text };
  } catch (error) {
    return { type: null, text: `No alert found within ${timeout}ms` };
  }
}

export function generateTimestampedPath(baseName: string, extension: string = 'json'): string {
  const timestamp = Date.now();
  return `outputs/test_${baseName}_${timestamp}.${extension}`;
}

export async function ensureOutputDirectory(): Promise<void> {
  try {
    await fs.mkdir('outputs', { recursive: true });
  } catch (error) {
    // Directory might already exist
  }
}

// Performance measurement utilities
export async function measureResponseTime(page: Page, action: () => Promise<void>): Promise<{ duration: number; success: boolean }> {
  const startTime = Date.now();
  let success = false;
  
  try {
    await action();
    success = true;
  } catch (error) {
    console.error('Action failed:', error);
  }
  
  const duration = Date.now() - startTime;
  return { duration, success };
}