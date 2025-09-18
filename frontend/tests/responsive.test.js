/**
 * TDD RED: Responsive Design Tests
 * これらのテストは最初は FAIL するはずなのだ〜！
 */

/**
 * @jest-environment jsdom
 */

describe('Responsive Design Tests (TDD RED)', () => {
  beforeEach(() => {
    // Setup DOM environment
    document.body.innerHTML = `
      <div class="app">
        <nav class="app-nav">
          <div class="nav-brand">
            <h1>AI Dynamic Painting</h1>
          </div>
          <div class="nav-links">
            <button class="nav-btn">Dashboard</button>
            <button class="nav-btn">Videos</button>
          </div>
        </nav>
        <main class="app-main">
          <div class="status-cards">
            <div class="status-card">Card 1</div>
            <div class="status-card">Card 2</div>
            <div class="status-card">Card 3</div>
            <div class="status-card">Card 4</div>
          </div>
          <div class="video-grid grid">
            <div class="video-card">Video 1</div>
            <div class="video-card">Video 2</div>
            <div class="video-card">Video 3</div>
          </div>
        </main>
      </div>
    `;

    // Load CSS styles
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/src/App.css';
    document.head.appendChild(link);
  });

  test('RED: App main should utilize full browser width (currently FAILS)', () => {
    const appMain = document.querySelector('.app-main');
    const computedStyle = window.getComputedStyle(appMain);
    
    // This should FAIL because max-width: 1400px restricts width
    expect(computedStyle.maxWidth).toBe('none');
    expect(computedStyle.width).toBe('100%');
  });

  test('RED: Status cards should be responsive on different screen sizes (currently FAILS)', () => {
    const statusCards = document.querySelector('.status-cards');
    
    // Simulate different viewport widths
    Object.defineProperty(window, 'innerWidth', { value: 1500, configurable: true });
    window.dispatchEvent(new Event('resize'));
    
    const computedStyle = window.getComputedStyle(statusCards);
    
    // Should have appropriate grid columns for large screens
    // This will FAIL with current fixed minmax(280px, 1fr)
    expect(computedStyle.gridTemplateColumns).toContain('300px');
  });

  test('RED: Video grid should adapt to different screen widths (currently FAILS)', () => {
    const videoGrid = document.querySelector('.video-grid.grid');
    
    // Test different viewport sizes
    const testSizes = [
      { width: 1600, expectedMinSize: '350px' },
      { width: 1200, expectedMinSize: '320px' },
      { width: 800, expectedMinSize: '280px' },
      { width: 400, expectedMinSize: 'none' } // Should be 1fr for mobile
    ];

    testSizes.forEach(({ width, expectedMinSize }) => {
      Object.defineProperty(window, 'innerWidth', { value: width, configurable: true });
      window.dispatchEvent(new Event('resize'));
      
      const computedStyle = window.getComputedStyle(videoGrid);
      
      // This will FAIL because responsive breakpoints don't exist yet
      if (expectedMinSize === 'none') {
        expect(computedStyle.gridTemplateColumns).toBe('1fr');
      } else {
        expect(computedStyle.gridTemplateColumns).toContain(expectedMinSize);
      }
    });
  });

  test('RED: Navigation should stack vertically on mobile (currently FAILS)', () => {
    const appNav = document.querySelector('.app-nav');
    
    // Simulate mobile viewport
    Object.defineProperty(window, 'innerWidth', { value: 600, configurable: true });
    window.dispatchEvent(new Event('resize'));
    
    const computedStyle = window.getComputedStyle(appNav);
    
    // Should be column direction on mobile
    // This will FAIL without proper media queries
    expect(computedStyle.flexDirection).toBe('column');
  });

  test('RED: Modal should be responsive and not overflow on small screens (currently FAILS)', () => {
    document.body.innerHTML += `
      <div class="modal-overlay">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Test Modal</h2>
          </div>
        </div>
      </div>
    `;

    const modalContent = document.querySelector('.modal-content');
    
    // Simulate small screen
    Object.defineProperty(window, 'innerWidth', { value: 400, configurable: true });
    window.dispatchEvent(new Event('resize'));
    
    const computedStyle = window.getComputedStyle(modalContent);
    
    // Should be 95% width on very small screens
    // This will FAIL without proper responsive modal styles
    expect(computedStyle.width).toBe('95%');
  });

  test('RED: Filter controls should stack vertically on mobile (currently FAILS)', () => {
    document.body.innerHTML += `
      <div class="list-controls">
        <div class="filter-group">
          <label>Filter 1</label>
          <select><option>Option 1</option></select>
        </div>
        <div class="filter-group">
          <label>Filter 2</label>
          <input type="text" />
        </div>
      </div>
    `;

    const listControls = document.querySelector('.list-controls');
    
    // Simulate mobile viewport
    Object.defineProperty(window, 'innerWidth', { value: 500, configurable: true });
    window.dispatchEvent(new Event('resize'));
    
    const computedStyle = window.getComputedStyle(listControls);
    
    // Should stack vertically on mobile
    // This will FAIL without proper mobile styles
    expect(computedStyle.flexDirection).toBe('column');
  });

  afterEach(() => {
    document.head.innerHTML = '';
    document.body.innerHTML = '';
    // Reset viewport width
    Object.defineProperty(window, 'innerWidth', { value: 1024, configurable: true });
  });
});

describe('Responsive Design Integration Tests (TDD RED)', () => {
  test('RED: Full page layout should not have horizontal scrollbar on any screen size (currently FAILS)', () => {
    // This is an integration test that would be run with actual DOM
    // Should check that document.body.scrollWidth <= window.innerWidth
    const testWidths = [320, 480, 768, 1024, 1440, 1920];
    
    testWidths.forEach(width => {
      Object.defineProperty(window, 'innerWidth', { value: width, configurable: true });
      window.dispatchEvent(new Event('resize'));
      
      // This should FAIL if there are fixed widths causing overflow
      expect(document.body.scrollWidth).toBeLessThanOrEqual(width + 20); // 20px tolerance
    });
  });

  test('RED: Touch targets should be at least 44px on mobile (currently FAILS)', () => {
    document.body.innerHTML = `
      <div class="nav-links">
        <button class="nav-btn">Dashboard</button>
        <button class="nav-btn">Videos</button>
      </div>
    `;

    // Simulate mobile
    Object.defineProperty(window, 'innerWidth', { value: 400, configurable: true });
    window.dispatchEvent(new Event('resize'));

    const buttons = document.querySelectorAll('.nav-btn');
    buttons.forEach(button => {
      const computedStyle = window.getComputedStyle(button);
      const height = parseInt(computedStyle.height) + 
                     parseInt(computedStyle.paddingTop) + 
                     parseInt(computedStyle.paddingBottom);
      
      // Should be at least 44px for accessibility
      // This will FAIL with current button sizes
      expect(height).toBeGreaterThanOrEqual(44);
    });
  });
});