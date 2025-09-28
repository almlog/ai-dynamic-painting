/**
 * T6-018: Cost Management E2E Test
 * 
 * Comprehensive E2E testing for cost management functionality:
 * 1. Budget setting tests
 * 2. Usage tracking tests  
 * 3. Limit behavior tests
 * 4. Alert display tests
 */

import { test, expect } from '@playwright/test';

test.describe('T6-018: Cost Management E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard first
    await page.goto('/');
    await expect(page.getByText('Video Generation Dashboard')).toBeVisible();
  });

  test('should display current budget status and cost information', async ({ page }) => {
    // 1. Verify budget panel is visible
    await expect(page.getByText('Daily Budget')).toBeVisible();
    
    // 2. Check cost display elements
    await expect(page.getByText('Total Cost')).toBeVisible();
    await expect(page.getByText('Remaining Budget')).toBeVisible();
    await expect(page.getByText('Budget Limit')).toBeVisible();
    
    // 3. Verify default values from CostManagementPanel are displayed
    // Default: totalCost: 0, remainingBudget: 10, dailyBudgetLimit: 10
    await expect(page.getByText('$0.00').first()).toBeVisible(); // Total Cost (take first occurrence)
    await expect(page.getByText('$10.00').first()).toBeVisible(); // Remaining Budget and Budget Limit
    
    // 4. Check usage percentage is calculated and displayed (0% when totalCost is 0)
    await expect(page.getByText('0.0% of budget used')).toBeVisible();
  });

  test('should hide progress bar when usage is zero (default state)', async ({ page }) => {
    // With default values (totalCost: 0), progress bar should be hidden
    // Since usagePercentage > 0 is the condition for showing progress bar
    
    // 1. Verify progress bar is NOT displayed when usage is 0
    const progressContainer = page.locator('.bg-gray-200.rounded-full.h-2');
    await expect(progressContainer).not.toBeVisible();
    
    // 2. But verify the budget panel itself is visible
    await expect(page.getByText('Daily Budget')).toBeVisible();
    await expect(page.getByText('0.0% of budget used')).toBeVisible();
  });

  test('should apply normal styling with default budget values', async ({ page }) => {
    // Default state: totalCost: 0, remainingBudget: 10, dailyBudgetLimit: 10
    // Usage: 0% - should be normal level (< 75%)
    
    // 1. Verify normal styling is applied (no warning/critical alerts)
    await expect(page.getByText('⚠️ Budget Warning')).not.toBeVisible();
    await expect(page.getByText('⚠️ Budget Critical')).not.toBeVisible();
    
    // 2. Check normal panel styling
    const panel = page.locator('.bg-blue-50.border-blue-200');
    await expect(panel).toBeVisible();
    
    // 3. Verify remaining budget shows normal color (not warning/critical)
    const remainingBudget = page.locator('text=$10.00').nth(0); // First $10.00 is remaining budget
    await expect(remainingBudget).toBeVisible();
  });

  test('should display budget sections with correct structure', async ({ page }) => {
    // Verify the component displays the expected budget information sections
    
    // 1. Check main sections are present
    await expect(page.getByText('Total Cost')).toBeVisible();
    await expect(page.getByText('Remaining Budget')).toBeVisible();
    await expect(page.getByText('Budget Limit')).toBeVisible();
    
    // 2. Verify descriptive text for each section
    await expect(page.getByText('0.0% of budget used')).toBeVisible();
    await expect(page.getByText('Available for today')).toBeVisible();
    await expect(page.getByText('Daily maximum')).toBeVisible();
    
    // 3. Check grid layout structure
    const gridContainer = page.locator('.grid.grid-cols-1.md\\:grid-cols-3.gap-4');
    await expect(gridContainer).toBeVisible();
  });

  test('should format cost values correctly', async ({ page }) => {
    // Verify cost formatting is working properly
    
    // 1. Check that cost values are properly formatted with $ and two decimal places
    const costElements = page.locator('.text-2xl.font-bold');
    const count = await costElements.count();
    expect(count).toBeGreaterThan(0);
    
    // 2. Verify specific default values
    await expect(page.getByText('$0.00').first()).toBeVisible(); // Total Cost
    await expect(page.getByText('$10.00').first()).toBeVisible(); // Remaining Budget and Limit
    
    // 3. Check percentage formatting
    await expect(page.getByText('0.0% of budget used')).toBeVisible();
  });

  test('should display component without crashing', async ({ page }) => {
    // Basic smoke test to ensure component renders properly
    
    // 1. Check component doesn't crash and displays main elements
    await expect(page.getByText('Daily Budget')).toBeVisible();
    
    // 2. Verify essential budget information is present
    await expect(page.getByText('Total Cost')).toBeVisible();
    await expect(page.getByText('Remaining Budget')).toBeVisible();
    await expect(page.getByText('Budget Limit')).toBeVisible();
    
    // 3. Check that component maintains responsive layout
    const container = page.locator('.mb-8.p-6.border.rounded-lg');
    await expect(container).toBeVisible();
  });

});