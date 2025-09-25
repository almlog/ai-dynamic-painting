/**
 * T4C-001 Red Phase: E2E Test for Full Generation Flow
 * 
 * This test covers the complete user journey from UI interaction to backend processing:
 * 1. Navigate to dashboard
 * 2. Open generation form  
 * 3. Input parameters
 * 4. Submit generation request
 * 5. Verify loading state
 * 6. Verify success/failure handling
 * 7. Verify result display in history
 */

import { test, expect } from '@playwright/test';

// Mock API responses for controlled testing
const mockSuccessResponse = {
  generation_id: 'test-gen-123',
  status: 'pending'
};

const mockFailureResponse = {
  error: 'API quota exceeded'
};

const mockHistoryResponse = [
  {
    id: 'test-gen-123',
    request: {
      variables: { prompt: 'Test prompt for E2E' },
      quality: 'hd',
      aspect_ratio: '16:9'
    },
    status: 'completed',
    created_at: '2025-09-22T22:30:00Z',
    image_path: '/test-images/test-gen-123.jpg'
  }
];

test.describe('T4C-001 Red Phase: Full Generation Flow E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API endpoints for controlled testing - corrected endpoints
    await page.route('**/api/admin/generate/history**', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockHistoryResponse)
        });
      }
    });
    
    await page.route('**/api/admin/generate', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSuccessResponse)
        });
      }
    });
  });

  test('RED PHASE: should fail - complete generation flow is not working', async ({ page }) => {
    let generationRequestData: any = null;
    
    // Mock slow API response for loading state visibility
    await page.route('**/api/admin/generate', async route => {
      if (route.request().method() === 'POST') {
        // Capture generation request data
        generationRequestData = await route.request().postDataJSON();
        
        // Add delay to ensure loading state is visible
        await new Promise(resolve => setTimeout(resolve, 1000));
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSuccessResponse)
        });
      }
    });

    // Mock dynamic history response that includes the new generation
    await page.route('**/api/admin/generate/history**', async route => {
      if (route.request().method() === 'GET') {
        // If a generation was submitted, include it in history
        let dynamicHistory = [...mockHistoryResponse];
        if (generationRequestData) {
          dynamicHistory.unshift({
            id: 'test-gen-new',
            request: {
              variables: { prompt: generationRequestData.variables.prompt },
              quality: generationRequestData.quality,
              aspect_ratio: generationRequestData.aspect_ratio
            },
            status: 'completed',
            created_at: new Date().toISOString(),
            image_path: '/test-images/test-gen-new.jpg'
          });
        }
        
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(dynamicHistory)
        });
      }
    });

    // Navigate to dashboard
    await page.goto('/');
    
    // RED PHASE: This should FAIL because complete flow is not implemented
    // Wait for dashboard to load
    await expect(page.getByText('AI Generation Dashboard')).toBeVisible();
    
    // Open generation form
    await page.click('text=Create New Generation');
    
    // Fill form with test parameters
    await page.fill('textarea[id="prompt"]', 'Test prompt for E2E generation');
    await page.selectOption('select[id="quality"]', 'hd');
    await page.selectOption('select[id="aspect_ratio"]', '16:9');
    
    // Submit generation request
    await page.click('text=Start Generation');
    
    // RED PHASE: This should FAIL - loading state is not properly displayed
    await expect(page.getByText('Generating...')).toBeVisible();
    
    // RED PHASE: This should FAIL - form doesn't close after submission
    await expect(page.getByText('Create AI Generation')).not.toBeVisible();
    
    // Wait for history refresh after generation
    await page.waitForTimeout(2000);
    
    // RED PHASE: This should FAIL - history is not updated with new generation
    await expect(page.getByText('Test prompt for E2E generation')).toBeVisible();
    
    // RED PHASE: This should FAIL - generation status is not displayed correctly
    await expect(page.getByRole('row', { name: /Test prompt for E2E generation.*completed/ })).toBeVisible();
  });

  test('RED PHASE: should fail - loading state display during generation', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/admin/generate', async route => {
      if (route.request().method() === 'POST') {
        // Delay response to test loading state
        await new Promise(resolve => setTimeout(resolve, 2000));
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSuccessResponse)
        });
      }
    });

    await page.goto('/');
    
    // Open form and submit
    await page.click('text=Create New Generation');
    await page.fill('textarea[id="prompt"]', 'Test loading state');
    await page.click('text=Start Generation');
    
    // RED PHASE: This should FAIL - loading state not implemented
    await expect(page.getByText('Generating...')).toBeVisible();
    
    // Verify button is disabled during generation
    await expect(page.getByRole('button', { name: 'Generating...' })).toBeDisabled();
  });

  test('RED PHASE: should fail - error handling and display', async ({ page }) => {
    // Mock API error response
    await page.route('**/api/admin/generate', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify(mockFailureResponse)
        });
      }
    });

    await page.goto('/');
    
    // Submit generation that will fail
    await page.click('text=Create New Generation');
    await page.fill('textarea[id="prompt"]', 'Test error handling');
    await page.click('text=Start Generation');
    
    // RED PHASE: This should FAIL - error messages not displayed
    // Match actual error format: "Error: API Error: 400 Bad Request"
    await expect(page.getByText('Error: API Error: 400 Bad Request')).toBeVisible();
    
    // RED PHASE: This should FAIL - form doesn't stay open on error
    await expect(page.getByText('Create AI Generation')).toBeVisible();
    
    // RED PHASE: This should FAIL - error doesn't clear on retry
    await page.fill('textarea[id="prompt"]', 'Retry test');
    await expect(page.getByText('Error: API quota exceeded')).not.toBeVisible();
  });

  test('RED PHASE: should fail - generation history refresh after creation', async ({ page }) => {
    let callCount = 0;
    
    // Mock API to track calls
    await page.route('**/api/admin/generate/history**', async route => {
      if (route.request().method() === 'GET') {
        callCount++;
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockHistoryResponse)
        });
      }
    });
    
    await page.route('**/api/admin/generate', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSuccessResponse)
        });
      }
    });

    await page.goto('/');
    
    // Initial load should call API once
    await expect(page.getByText('AI Generation Dashboard')).toBeVisible();
    
    // Submit new generation
    await page.click('text=Create New Generation');
    await page.fill('textarea[id="prompt"]', 'Test history refresh');
    await page.click('text=Start Generation');
    
    // RED PHASE: This should FAIL - history is not refreshed after creation
    // Should call API again to refresh history
    await page.waitForTimeout(1000); // Allow time for API call
    
    // Verify API was called multiple times (initial load + refresh after creation)
    expect(callCount).toBeGreaterThan(1);
  });

  test('RED PHASE: should fail - form validation prevents empty submission', async ({ page }) => {
    await page.goto('/');
    
    // Open form without filling required fields
    await page.click('text=Create New Generation');
    
    // Try to submit with empty prompt
    const submitButton = page.getByText('Start Generation');
    
    // RED PHASE: This should FAIL - empty prompt submission is not prevented
    await expect(submitButton).toBeDisabled();
    
    // Fill prompt and verify button becomes enabled
    await page.fill('textarea[id="prompt"]', 'Valid prompt');
    await expect(submitButton).toBeEnabled();
    
    // Clear prompt and verify button becomes disabled again
    await page.fill('textarea[id="prompt"]', '');
    await expect(submitButton).toBeDisabled();
  });

  test('RED PHASE: should fail - form reset after successful submission', async ({ page }) => {
    await page.goto('/');
    
    // Fill and submit form
    await page.click('text=Create New Generation');
    await page.fill('textarea[id="prompt"]', 'Test form reset');
    await page.selectOption('select[id="quality"]', 'hd');
    await page.selectOption('select[id="aspect_ratio"]', '9:16');
    await page.click('text=Start Generation');
    
    // Wait for form to close and reopen
    await page.waitForTimeout(1000);
    await page.click('text=Create New Generation');
    
    // RED PHASE: This should FAIL - form fields are not reset
    await expect(page.locator('textarea[id="prompt"]')).toHaveValue('');
    await expect(page.locator('select[id="quality"]')).toHaveValue('standard');
    await expect(page.locator('select[id="aspect_ratio"]')).toHaveValue('1:1');
  });

  test('RED PHASE: should fail - API request contains correct parameters', async ({ page }) => {
    let capturedRequest: any = null;
    
    // Capture API request for verification
    await page.route('**/api/admin/generate', async route => {
      if (route.request().method() === 'POST') {
        capturedRequest = await route.request().postDataJSON();
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSuccessResponse)
        });
      }
    });

    await page.goto('/');
    
    // Submit form with specific parameters
    await page.click('text=Create New Generation');
    await page.fill('textarea[id="prompt"]', 'Specific test prompt');
    await page.selectOption('select[id="quality"]', 'hd');
    await page.selectOption('select[id="aspect_ratio"]', '16:9');
    await page.click('text=Start Generation');
    
    // Wait for API call
    await page.waitForTimeout(1000);
    
    // RED PHASE: This should FAIL - API request doesn't contain correct parameters
    expect(capturedRequest).toBeTruthy();
    expect(capturedRequest.variables.prompt).toBe('Specific test prompt');
    expect(capturedRequest.quality).toBe('hd');
    expect(capturedRequest.aspect_ratio).toBe('16:9');
    expect(capturedRequest.model).toBe('gemini-1.5-flash');
  });
});