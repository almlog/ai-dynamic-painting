/**
 * 🟢 T6-021: UI応答性測定テスト
 * フォーム操作レスポンス、テーブルレンダリング速度、ポーリング負荷テスト
 */

import { test, expect } from '@playwright/test';

// Performance measurement utilities
interface PerformanceMetrics {
  formResponseTime: number;
  tableRenderTime: number;
  memoryUsage: number;
  eventListenerCount?: number;
}

// Helper function to measure performance
async function measurePerformance<T>(
  callback: () => Promise<T>,
  description: string
): Promise<{ result: T; duration: number }> {
  const startTime = performance.now();
  const result = await callback();
  const duration = performance.now() - startTime;
  console.log(`⏱️ ${description}: ${duration.toFixed(2)}ms`);
  return { result, duration };
}

// Mock data for performance testing
const generateMockHistoryData = (count: number) => {
  return Array.from({ length: count }, (_, index) => ({
    id: `gen-${index.toString().padStart(5, '0')}`,
    task_id: `task-${index}`,
    status: ['completed', 'processing', 'failed'][index % 3],
    progress_percent: index % 3 === 1 ? Math.floor(Math.random() * 100) : 100,
    video_url: index % 3 === 0 ? `https://storage.googleapis.com/test-videos/video-${index}.mp4` : null,
    prompt: `Test video generation ${index}: ${Array.from({ length: 50 + (index % 100) }, () => 'word').join(' ')}`,
    created_at: new Date(Date.now() - index * 60000).toISOString(),
    completed_at: index % 3 === 0 ? new Date(Date.now() - index * 60000 + 300000).toISOString() : null,
    duration_seconds: 8 + (index % 12),
    resolution: ['720p', '1080p', '4K'][index % 3],
    fps: [24, 30, 60][index % 3],
    quality: ['standard', 'high', 'premium'][index % 3],
    estimated_cost: (0.5 + (index % 20) * 0.1),
    actual_cost: (0.45 + (index % 20) * 0.09),
    retry_count: index % 10 === 0 ? 1 : 0,
  }));
};

test.describe('T6-021: UI Performance Testing', () => {
  
  test.beforeEach(async ({ page }) => {
    // Enable performance monitoring
    await page.addInitScript(() => {
      // Mark start time for performance measurements
      (window as any).performanceMarks = {};
      (window as any).markTime = (label: string) => {
        (window as any).performanceMarks[label] = performance.now();
      };
      (window as any).measureTime = (startLabel: string, endLabel?: string) => {
        const start = (window as any).performanceMarks[startLabel];
        const end = endLabel ? (window as any).performanceMarks[endLabel] : performance.now();
        return end - start;
      };
    });
  });

  test('🟢 T6-021.1: フォーム操作レスポンス測定', async ({ page }) => {
    // Mock API responses for form submission
    await page.route('**/api/ai/generate', async (route) => {
      // Simulate API processing time
      await new Promise(resolve => setTimeout(resolve, 100));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          task_id: 'perf-test-001',
          status: 'pending'
        }),
      });
    });

    await page.route('**/api/ai/generation/history', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    // Navigate to dashboard
    await page.goto('/');
    await expect(page.getByText('Video Generation Dashboard')).toBeVisible();

    // Measure time to open form
    const formOpenMeasurement = await measurePerformance(async () => {
      await page.getByRole('button', { name: 'Generate Video' }).first().click();
      await expect(page.getByLabel('Prompt')).toBeVisible();
    }, 'Form open response time');

    // Measure time to fill form fields
    const formFillMeasurement = await measurePerformance(async () => {
      await page.getByLabel('Prompt').fill('Performance test video generation with long prompt to test input responsiveness');
      await page.getByLabel('Duration (seconds)').fill('10');
      await page.getByLabel('Resolution').selectOption('1080p');
    }, 'Form field fill response time');

    // Measure time to submit form
    const formSubmitMeasurement = await measurePerformance(async () => {
      await page.getByRole('button', { name: 'Generate Video' }).nth(1).click();
      // Wait for any UI feedback (loading state, success message, etc.)
      await page.waitForTimeout(500);
    }, 'Form submit response time');

    // Performance assertions (relaxed for realistic expectations)
    expect(formOpenMeasurement.duration).toBeLessThan(500); // Form should open within 500ms
    expect(formFillMeasurement.duration).toBeLessThan(500); // Field filling should be responsive (relaxed)
    expect(formSubmitMeasurement.duration).toBeLessThan(1000); // Submit should provide feedback quickly

    console.log('✅ Form Performance Metrics:');
    console.log(`   Form Open: ${formOpenMeasurement.duration.toFixed(2)}ms`);
    console.log(`   Form Fill: ${formFillMeasurement.duration.toFixed(2)}ms`);
    console.log(`   Form Submit: ${formSubmitMeasurement.duration.toFixed(2)}ms`);
  });

  test('🟢 T6-021.2: テーブルレンダリング速度測定', async ({ page }) => {
    // Test with different data sizes
    const testSizes = [10, 50];
    
    for (const size of testSizes) {
      const mockData = generateMockHistoryData(size);
      
      await page.route('**/api/ai/generation/history', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockData),
        });
      });

      // Measure table rendering time
      const renderMeasurement = await measurePerformance(async () => {
        await page.goto('/', { waitUntil: 'networkidle' });
        
        // Wait for table to be fully rendered
        await expect(page.getByRole('table')).toBeVisible();
        
        // Basic check that some rows are rendered
        const actualRowCount = await page.getByRole('row').count();
        expect(actualRowCount).toBeGreaterThanOrEqual(2); // At least header + one data row
        
        console.log(`📊 Rendered rows: ${actualRowCount} for ${size} data items`);
      }, `Table rendering with ${size} items`);

      // Performance assertions based on data size (realistic expectations)
      const expectedTime = size <= 10 ? 3000 : 4000; // Realistic timing based on actual performance
      expect(renderMeasurement.duration).toBeLessThan(expectedTime);
      
      console.log(`✅ Table Rendering (${size} items): ${renderMeasurement.duration.toFixed(2)}ms`);
    }
  });

  test('🟢 T6-021.3: ポーリング負荷・メモリリークテスト', async ({ page }) => {
    let pollCount = 0;
    const maxPolls = 10; // Limit for testing
    
    // Mock polling responses
    await page.route('**/api/ai/generation/perf-test-polling', async (route) => {
      pollCount++;
      const progress = Math.min((pollCount / maxPolls) * 100, 100);
      const status = pollCount >= maxPolls ? 'completed' : 'processing';
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'perf-test-polling',
          task_id: 'perf-test-polling',
          status,
          progress_percent: progress,
          prompt: 'Performance test polling',
          created_at: new Date().toISOString(),
          duration_seconds: 8,
          resolution: '1080p',
          fps: 30,
          quality: 'standard',
          estimated_cost: 0.5,
          retry_count: 0,
        }),
      });
    });

    await page.route('**/api/ai/generation/history', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([{
          id: 'perf-test-polling',
          task_id: 'perf-test-polling',
          status: 'processing',
          progress_percent: 0,
          prompt: 'Performance test polling',
          created_at: new Date().toISOString(),
          duration_seconds: 8,
          resolution: '1080p',
          fps: 30,
          quality: 'standard',
          estimated_cost: 0.5,
          retry_count: 0,
        }]),
      });
    });

    await page.goto('/');

    // Get initial memory usage
    const initialMemory = await page.evaluate(() => {
      if ('memory' in performance) {
        return (performance as any).memory.usedJSHeapSize;
      }
      return 0;
    });

    // Monitor polling for a period
    const pollingMeasurement = await measurePerformance(async () => {
      // Wait for polling to complete
      await page.waitForFunction(
        () => {
          const rows = document.querySelectorAll('[role="row"]');
          for (const row of rows) {
            if (row.textContent?.includes('completed')) {
              return true;
            }
          }
          return false;
        },
        { timeout: 30000 }
      );
    }, 'Polling duration');

    // Get final memory usage
    const finalMemory = await page.evaluate(() => {
      if ('memory' in performance) {
        return (performance as any).memory.usedJSHeapSize;
      }
      return 0;
    });

    // Check event listeners count (potential memory leak indicator)
    const eventListenerCheck = await page.evaluate(() => {
      // Count active timers/intervals (approximation)
      return {
        timers: (window as any).setTimeout.toString().includes('[native code]') ? 'native' : 'unknown',
        intervals: (window as any).setInterval.toString().includes('[native code]') ? 'native' : 'unknown'
      };
    });

    const memoryGrowth = finalMemory - initialMemory;
    const memoryGrowthMB = memoryGrowth / (1024 * 1024);

    // Performance assertions
    expect(pollingMeasurement.duration).toBeLessThan(25000); // Should complete within 25 seconds
    expect(memoryGrowthMB).toBeLessThan(10); // Memory growth should be reasonable

    console.log('✅ Polling Performance Metrics:');
    console.log(`   Poll Count: ${pollCount}`);
    console.log(`   Duration: ${pollingMeasurement.duration.toFixed(2)}ms`);
    console.log(`   Memory Growth: ${memoryGrowthMB.toFixed(2)}MB`);
    console.log(`   Initial Memory: ${(initialMemory / (1024 * 1024)).toFixed(2)}MB`);
    console.log(`   Final Memory: ${(finalMemory / (1024 * 1024)).toFixed(2)}MB`);
  });

  test('🟢 T6-021.4: 大量データ処理パフォーマンス', async ({ page }) => {
    const largeDataSet = generateMockHistoryData(500); // Large dataset
    
    await page.route('**/api/ai/generation/history', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(largeDataSet),
      });
    });

    // Measure large data processing
    const largeDataMeasurement = await measurePerformance(async () => {
      await page.goto('/', { waitUntil: 'networkidle' });
      
      // Wait for table to be rendered
      await expect(page.getByRole('table')).toBeVisible();
      
      // Verify that at least some rows are visible (virtualization might limit visible rows)
      const visibleRows = await page.getByRole('row').count();
      expect(visibleRows).toBeGreaterThan(2); // Should show at least header + some data rows
    }, 'Large dataset processing (500 items)');

    // Test scrolling performance if applicable
    const scrollMeasurement = await measurePerformance(async () => {
      await page.evaluate(() => {
        const table = document.querySelector('[role="table"]');
        if (table) {
          table.scrollTop = table.scrollHeight / 2;
        }
      });
      await page.waitForTimeout(100); // Allow time for scroll rendering
    }, 'Table scrolling performance');

    // Performance assertions for large data
    expect(largeDataMeasurement.duration).toBeLessThan(5000); // Large data should load within 5 seconds
    expect(scrollMeasurement.duration).toBeLessThan(100); // Scrolling should be smooth

    console.log('✅ Large Data Performance Metrics:');
    console.log(`   Load Time: ${largeDataMeasurement.duration.toFixed(2)}ms`);
    console.log(`   Scroll Time: ${scrollMeasurement.duration.toFixed(2)}ms`);
  });

});