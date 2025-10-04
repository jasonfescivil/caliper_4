# Caliper v2 Comprehensive E2E Testing Strategy

## Overview

This document outlines the comprehensive end-to-end testing strategy for Caliper v2's multi-provider retrieve and generate functions using the Dash UI. The testing framework ensures robust operation across all 5 LLM providers with medium-complexity engineering questions.

## Testing Framework: Playwright

**Selected Framework**: Playwright
- **Rationale**: Best-in-class for modern web applications, excellent cross-browser support, built-in waiting and retry mechanisms
- **Configuration**: Headless mode optimized for CI/CD, with options for headed debugging
- **Browser Coverage**: Chromium, Firefox, Safari/WebKit

## Provider Coverage

All 5 providers are configured and tested:

1. **Cohere** (`command-a-reasoning-08-2025`)
2. **OpenAI** (`gpt-4o`) 
3. **Anthropic** (`claude-3-opus-20240229`)
4. **Google Gemini** (`models/gemini-1.5-pro`)
5. **xAI Grok** (`grok-2-1212`)

## Test Complexity Level

**Medium Complexity Engineering Questions** including:
- Wastewater treatment plant design calculations
- Regulatory compliance requirements (NPDES permits)
- Stormwater management for industrial facilities  
- Biosolids handling and disposal requirements
- Technical analysis requiring multi-source synthesis

## Test Suite Structure

### 1. Basic Functionality Tests (`multi-provider-retrieve-generate.spec.ts`)

**Core Workflow Testing:**
- Individual provider testing (retrieve → generate workflow)
- Cross-provider response comparison
- Error handling for edge cases
- Output validation and quality checks

**Key Scenarios:**
- ✅ Complete retrieve & generate workflow per provider
- ✅ Cross-provider response comparison 
- ✅ Error handling (empty questions, invalid paths)
- ✅ Output file validation (JSON structure, content quality)

### 2. Advanced Functions Tests (`advanced-functions.spec.ts`) 

**Advanced Feature Testing:**
- Context enhancement functionality
- Complete workflow (retrieve → enhance → generate → review)
- GraphRAG retrieval (when available)
- Judge function with different strictness levels
- Provider self-test and doctor functions

**Key Scenarios:**
- ✅ Enhancement function (context enrichment)
- ✅ Complete 4-step workflow validation
- ✅ GraphRAG integration testing
- ✅ Judge function with claims analysis
- ✅ System health check functions

### 3. Performance & Reliability Tests (`performance-reliability.spec.ts`)

**Robustness Testing:**
- Response time benchmarking across providers
- Error recovery and system resilience  
- Concurrent request handling
- Long-running operation stability
- Memory usage and resource stability

**Key Scenarios:**
- ✅ Performance benchmarking (< 2min retrieval, < 3min generation)
- ✅ Error recovery from various failure modes
- ✅ Concurrent request handling
- ✅ Long-running stability (complex 10min+ operations)
- ✅ Memory leak detection across iterations

### 4. UI Validation Tests (`ui-validation.spec.ts`)

**Interface Testing:**
- UI component loading and visibility
- Provider selection functionality
- Form validation and error handling
- Tab navigation and state management

## Test Execution

### Quick Start
```bash
# Run all tests
npm test

# Run specific test suites  
npm run test:basic
npm run test:advanced
npm run test:performance

# Run with visual feedback
npm run test:headed

# Generate reports
npm run test:report
```

### PowerShell Script
```powershell
# Comprehensive test runner with options
.\run-tests.ps1                    # All tests
.\run-tests.ps1 basic              # Basic tests only  
.\run-tests.ps1 -Headed            # Visual mode
.\run-tests.ps1 performance -Browser firefox  # Firefox performance tests
```

## Validation Criteria

### Functional Validation
- **Retrieval Quality**: Minimum 5 nodes retrieved, relevant to query
- **Generation Quality**: Minimum 200 characters, contains expected keywords  
- **File Outputs**: Valid JSON structure, proper markdown formatting
- **Error Handling**: Graceful degradation, appropriate user feedback

### Performance Validation  
- **Response Times**: < 2min average retrieval, < 3min average generation
- **Success Rates**: ≥ 80% success rate across providers
- **Stability**: No significant performance degradation over iterations
- **Concurrency**: System handles multiple requests gracefully

### Coverage Validation
- **Provider Coverage**: All 5 providers tested individually
- **Function Coverage**: Retrieve, enhance, generate, review, judge
- **Error Scenarios**: Empty inputs, invalid paths, provider failures
- **Browser Coverage**: Chromium, Firefox, WebKit

## Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions integration
- name: Install dependencies
  run: npm install && poetry install
  
- name: Install browsers  
  run: npx playwright install

- name: Start Dash UI
  run: poetry run python -m caliper_v2.ui_dash.app &
  
- name: Run E2E tests
  run: npx playwright test
  
- name: Upload test results
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## Test Data Management

### Engineering Questions Database
Medium-complexity scenarios covering:
- Municipal wastewater treatment design
- Industrial permit compliance
- Environmental regulatory analysis  
- Technical system recommendations

### Output Validation
- **Retrieval Outputs**: JSON validation, node count, relevance scores
- **Generation Outputs**: Length validation, keyword presence, technical accuracy
- **Review Outputs**: Claims extraction, evidence validation, citation quality

## Debugging and Troubleshooting

### Common Issues
1. **Provider API Limits**: Staggered testing, retry logic
2. **Timeout Issues**: Extended timeouts for complex operations
3. **UI Element Changes**: Robust selectors with fallbacks
4. **Network Issues**: Retry mechanisms and graceful degradation

### Debug Mode
```bash
# Step-through debugging
npm run test:debug

# Visual debugging with browser
.\run-tests.ps1 -Headed -Debug
```

## Reporting and Metrics

### Automated Reports
- **HTML Report**: Visual test results with screenshots/videos
- **Performance Report**: Response time metrics across providers  
- **Coverage Report**: Feature and provider coverage analysis
- **Error Analysis**: Failure categorization and trends

### Key Metrics Tracked
- ✅ Provider success rates
- ✅ Average response times  
- ✅ Output quality scores
- ✅ Error recovery effectiveness
- ✅ System stability over time

## Future Enhancements

### Planned Improvements
1. **Load Testing**: High-volume concurrent user simulation
2. **Integration Tests**: CLI command validation
3. **Visual Testing**: UI screenshot comparison
4. **API Testing**: Direct service layer validation
5. **Mobile Testing**: Responsive design validation

### Monitoring Integration
- Performance dashboards
- Alert thresholds for degradation
- Automated quality gates
- Provider health monitoring

---

## Quick Reference Commands

```bash
# Essential commands for testing
npm install -D @playwright/test     # Install Playwright
npx playwright install              # Install browsers  
npm test                           # Run all tests
npm run test:basic                 # Core functionality
npm run test:performance           # Performance tests
npx playwright show-report         # View results
.\run-tests.ps1 -Headed           # Visual debugging
```

This comprehensive testing strategy ensures Caliper v2 operates robustly across all providers with reliable retrieve and generate functionality, advanced features, and excellent user experience.