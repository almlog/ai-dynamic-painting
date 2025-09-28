import { test, expect } from '@playwright/test';

// Mock data adhering to the VideoGeneration type
const mockVideoTask = {
  task_id: 'task-12345',
  status: 'pending',
};

const mockProcessingResponse = {
  id: 'gen-abcde',
  task_id: 'task-12345',
  status: 'processing',
  progress_percent: 50,
  estimated_cost: 0.9,
  created_at: new Date().toISOString(),
  prompt: 'A cat chasing a laser pointer',
  duration_seconds: 8,
  resolution: '1080p',
  fps: 30,
  quality: 'standard',
  retry_count: 0,
};

const mockCompletedResponse = {
  ...mockProcessingResponse,
  status: 'completed',
  progress_percent: 100,
  video_url: 'https://storage.googleapis.com/test-videos/cat-laser.mp4',
  actual_cost: 0.85,
  completed_at: new Date().toISOString(),
};

const mockInitialHistory = [
  {
    id: 'gen-fghij',
    task_id: 'task-67890',
    status: 'completed',
    progress_percent: 100,
    video_url: 'https://storage.googleapis.com/test-videos/dog-park.mp4',
    prompt: 'Dogs playing in a sunny park',
    created_at: '2025-09-27T10:00:00Z',
    completed_at: '2025-09-27T10:05:00Z',
    duration_seconds: 10,
    resolution: '1080p',
    fps: 30,
    quality: 'standard',
    estimated_cost: 1.0,
    actual_cost: 0.95,
    retry_count: 0,
  },
];

test.describe('T6-017: Video Generation E2E Test', () => {
  test.beforeEach(async ({ page }) => {
    // Mock the initial history call
    await page.route('**/api/ai/generation/history', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockInitialHistory),
      });
    });

    // Mock the generation request
    await page.route('**/api/ai/generate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockVideoTask),
      });
    });

    // Mock the polling mechanism
    let pollCount = 0;
    await page.route(`**/api/ai/generation/${mockVideoTask.task_id}`, async (route) => {
      pollCount++;
      if (pollCount <= 2) {
        // Respond with processing status for the first two polls
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockProcessingResponse),
        });
      } else {
        // Respond with completed status afterwards
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockCompletedResponse),
        });
        // After completion, also update the history
        await page.route('**/api/ai/generation/history', async (historyRoute) => {
          await historyRoute.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([mockCompletedResponse, ...mockInitialHistory]),
          });
        });
      }
    });
  });

  test('should allow a user to generate a video and see it in the history', async ({ page }) => {
    // 1. Navigate to the dashboard
    await page.goto('/');
    await expect(page.getByText('Video Generation Dashboard')).toBeVisible();

    // 2. Open the generation form
    await page.getByRole('button', { name: 'Generate Video' }).first().click();

    // 3. Fill out the generation form
    await page.getByLabel('Prompt').fill('A cat chasing a laser pointer');
    await page.getByLabel('Duration (seconds)').fill('8');
    await page.getByLabel('Resolution').selectOption('1080p');

    // 4. Submit the form
    await page.getByRole('button', { name: 'Generate Video' }).nth(1).click();

    // 5. Verify progress polling
    // Check for the initial pending/processing state in the history table
    const newEntryRow = page.getByRole('row', { name: /A cat chasing a laser pointer/ });
    await expect(newEntryRow).toBeVisible();
    await expect(newEntryRow.getByText(/processing/i)).toBeVisible();

    // Check that the progress bar appears and updates
    await expect(newEntryRow.getByRole('progressbar')).toBeVisible();
    await expect(newEntryRow.getByText('50%')).toBeVisible();

    // 5. Verify completion
    // Wait for the polling to result in a completed state
    await expect(newEntryRow.getByText(/completed/i, { timeout: 15000 })).toBeVisible();
    await expect(newEntryRow.getByRole('progressbar')).not.toBeVisible(); // Progress bar should disappear

    // 6. Verify video URL and history display
    // Check if the video player/link is now present
    const videoLink = newEntryRow.getByRole('link', { name: /Play Video/i });
    await expect(videoLink).toBeVisible();
    await expect(videoLink).toHaveAttribute('href', mockCompletedResponse.video_url);

    // Verify the history has the new completed item at the top
    const historyRows = await page.getByRole('row').all();
    // The first row is the header, the second should be our new video
    const firstDataRowText = await historyRows[1].innerText();
    expect(firstDataRowText).toContain('A cat chasing a laser pointer');
    expect(firstDataRowText).toContain('completed');
  });
});