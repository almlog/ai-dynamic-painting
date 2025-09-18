/**
 * DisplayController Component Test - T023
 * Phase 1 手動動画管理システム - 表示制御コンポーネントテスト
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DisplayController from '../../src/components/DisplayController';
import type { Video, DisplayStatus } from '../../src/types';

describe('DisplayController Component', () => {
  const mockVideo: Video = {
    id: 'test-video',
    title: 'Test Video',
    file_path: '/uploads/test.mp4',
    file_size: 5 * 1024 * 1024, // 5MB
    duration: 180, // 3 minutes
    format: 'mp4',
    upload_timestamp: new Date().toISOString(),
    status: 'active'
  };

  const mockProps = {
    currentVideo: mockVideo,
    displayStatus: 'stopped' as DisplayStatus,
    onPlay: vi.fn(),
    onPause: vi.fn(),
    onStop: vi.fn(),
    onVolumeChange: vi.fn(),
    onFullscreenToggle: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders controller correctly with video', () => {
    render(<DisplayController {...mockProps} />);
    
    expect(screen.getByText('🎬 現在の動画')).toBeInTheDocument();
    expect(screen.getByText('Test Video')).toBeInTheDocument();
    expect(screen.getByText('3:00')).toBeInTheDocument(); // Duration
    expect(screen.getByText('5MB')).toBeInTheDocument(); // File size
  });

  it('shows no video message when no video selected', () => {
    render(
      <DisplayController 
        {...mockProps} 
        currentVideo={null} 
      />
    );
    
    expect(screen.getByText('動画が選択されていません')).toBeInTheDocument();
  });

  it('displays correct status indicators', () => {
    const { rerender } = render(<DisplayController {...mockProps} />);
    
    expect(screen.getByText('⏹️')).toBeInTheDocument(); // Stopped
    expect(screen.getByText('停止中')).toBeInTheDocument();
    
    rerender(
      <DisplayController 
        {...mockProps} 
        displayStatus="playing" 
      />
    );
    
    expect(screen.getByText('▶️')).toBeInTheDocument(); // Playing
    expect(screen.getByText('再生中')).toBeInTheDocument();
  });

  it('calls onPlay when play button is clicked', async () => {
    const user = userEvent.setup();
    render(<DisplayController {...mockProps} />);
    
    const playButton = screen.getByRole('button', { name: /再生/i });
    await user.click(playButton);
    
    expect(mockProps.onPlay).toHaveBeenCalledWith('test-video');
  });

  it('calls onPause when pause button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <DisplayController 
        {...mockProps} 
        displayStatus="playing" 
      />
    );
    
    const pauseButton = screen.getByRole('button', { name: /一時停止/i });
    await user.click(pauseButton);
    
    expect(mockProps.onPause).toHaveBeenCalled();
  });

  it('calls onStop when stop button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <DisplayController 
        {...mockProps} 
        displayStatus="playing" 
      />
    );
    
    const stopButton = screen.getByRole('button', { name: /停止/i });
    await user.click(stopButton);
    
    expect(mockProps.onStop).toHaveBeenCalled();
  });

  it('handles volume control correctly', async () => {
    const user = userEvent.setup();
    render(<DisplayController {...mockProps} />);
    
    const volumeSlider = screen.getByRole('slider');
    fireEvent.change(volumeSlider, { target: { value: '50' } });
    
    expect(mockProps.onVolumeChange).toHaveBeenCalledWith(50);
    expect(screen.getByText('🔊 音量: 50%')).toBeInTheDocument();
  });

  it('handles volume preset buttons', async () => {
    const user = userEvent.setup();
    render(<DisplayController {...mockProps} />);
    
    const volumePresets = screen.getAllByRole('button').filter(
      button => ['🔇', '🔈', '🔉', '🔊', '📢'].includes(button.textContent || '')
    );
    
    await user.click(volumePresets[2]); // 50% volume button
    expect(mockProps.onVolumeChange).toHaveBeenCalledWith(50);
  });

  it('toggles fullscreen mode', async () => {
    const user = userEvent.setup();
    render(<DisplayController {...mockProps} />);
    
    const fullscreenButton = screen.getByRole('button', { name: /フルスクリーン/i });
    await user.click(fullscreenButton);
    
    expect(mockProps.onFullscreenToggle).toHaveBeenCalledWith(true);
  });

  it('handles emergency stop', async () => {
    const user = userEvent.setup();
    render(<DisplayController {...mockProps} />);
    
    const emergencyButton = screen.getByRole('button', { name: /緊急停止/i });
    await user.click(emergencyButton);
    
    expect(mockProps.onStop).toHaveBeenCalled();
  });

  it('disables controls appropriately', () => {
    const { rerender } = render(
      <DisplayController 
        {...mockProps} 
        displayStatus="playing" 
      />
    );
    
    const playButton = screen.getByRole('button', { name: /再生/i });
    expect(playButton).toBeDisabled();
    
    rerender(
      <DisplayController 
        {...mockProps} 
        displayStatus="stopped" 
      />
    );
    
    const pauseButton = screen.getByRole('button', { name: /一時停止/i });
    expect(pauseButton).toBeDisabled();
  });

  it('shows progress bar correctly', () => {
    render(<DisplayController {...mockProps} />);
    
    const progressBar = document.querySelector('.progress-bar');
    expect(progressBar).toBeInTheDocument();
    
    const progressFill = document.querySelector('.progress-fill');
    expect(progressFill).toBeInTheDocument();
  });

  it('formats time correctly', () => {
    render(<DisplayController {...mockProps} />);
    
    // Check duration formatting (180 seconds = 3:00)
    expect(screen.getByText('3:00')).toBeInTheDocument();
    
    // Check current time formatting (starts at 0:00)
    expect(screen.getByText('0:00')).toBeInTheDocument();
  });
});