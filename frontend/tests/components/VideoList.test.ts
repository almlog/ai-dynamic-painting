/**
 * VideoList Component Test - T022
 * Phase 1 手動動画管理システム - 動画リストコンポーネントテスト
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import VideoList from '../../src/components/VideoList';
import type { Video } from '../../src/types';

describe('VideoList Component', () => {
  const mockVideos: Video[] = [
    {
      id: '1',
      title: 'Test Video 1',
      file_path: '/uploads/video1.mp4',
      file_size: 1024 * 1024, // 1MB
      duration: 120,
      format: 'mp4',
      upload_timestamp: new Date().toISOString(),
      status: 'active'
    },
    {
      id: '2', 
      title: 'Test Video 2',
      file_path: '/uploads/video2.mp4',
      file_size: 2 * 1024 * 1024, // 2MB
      duration: 180,
      format: 'mp4',
      upload_timestamp: new Date().toISOString(),
      status: 'active'
    }
  ];

  const mockProps = {
    videos: mockVideos,
    currentVideo: null,
    onVideoSelect: vi.fn(),
    onVideoPlay: vi.fn(),
    onVideoDelete: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders video list correctly', () => {
    render(<VideoList {...mockProps} />);
    
    expect(screen.getByText('📹 動画リスト')).toBeInTheDocument();
    expect(screen.getByText('Test Video 1')).toBeInTheDocument();
    expect(screen.getByText('Test Video 2')).toBeInTheDocument();
    expect(screen.getByText('2分')).toBeInTheDocument();
    expect(screen.getByText('3分')).toBeInTheDocument();
  });

  it('displays empty state when no videos', () => {
    render(<VideoList {...mockProps} videos={[]} />);
    
    expect(screen.getByText(/動画がアップロードされていません/i)).toBeInTheDocument();
  });

  it('highlights currently playing video', () => {
    render(
      <VideoList 
        {...mockProps} 
        currentVideo={mockVideos[0]}
      />
    );
    
    const videoItem = screen.getByText('Test Video 1').closest('.video-item');
    expect(videoItem).toHaveClass('current');
  });

  it('calls onVideoSelect when video is clicked', async () => {
    const user = userEvent.setup();
    render(<VideoList {...mockProps} />);
    
    await user.click(screen.getByText('Test Video 1'));
    expect(mockProps.onVideoSelect).toHaveBeenCalledWith(mockVideos[0]);
  });

  it('calls onVideoPlay when play button is clicked', async () => {
    const user = userEvent.setup();
    render(<VideoList {...mockProps} />);
    
    const playButton = screen.getAllByText('▶️')[0];
    await user.click(playButton);
    
    expect(mockProps.onVideoPlay).toHaveBeenCalledWith('1');
  });

  it('calls onVideoDelete when delete button is clicked', async () => {
    const user = userEvent.setup();
    render(<VideoList {...mockProps} />);
    
    const deleteButton = screen.getAllByText('🗑️')[0];
    await user.click(deleteButton);
    
    expect(mockProps.onVideoDelete).toHaveBeenCalledWith('1');
  });

  it('displays file size correctly', () => {
    render(<VideoList {...mockProps} />);
    
    expect(screen.getByText('1.0MB')).toBeInTheDocument();
    expect(screen.getByText('2.0MB')).toBeInTheDocument();
  });

  it('shows video format correctly', () => {
    render(<VideoList {...mockProps} />);
    
    expect(screen.getAllByText('MP4')).toHaveLength(2);
  });

  it('filters videos by search term', async () => {
    const user = userEvent.setup();
    render(<VideoList {...mockProps} />);
    
    const searchInput = screen.getByPlaceholderText(/動画を検索/i);
    await user.type(searchInput, 'Video 1');
    
    expect(screen.getByText('Test Video 1')).toBeInTheDocument();
    expect(screen.queryByText('Test Video 2')).not.toBeInTheDocument();
  });

  it('sorts videos by different criteria', async () => {
    const user = userEvent.setup();
    render(<VideoList {...mockProps} />);
    
    const sortSelect = screen.getByDisplayValue(/新しい順/i);
    await user.selectOptions(sortSelect, 'title');
    
    // Check that videos are re-ordered (implementation specific)
    expect(screen.getAllByText(/Test Video/)[0]).toHaveTextContent('Test Video 1');
  });

  it('displays loading state correctly', () => {
    render(<VideoList {...mockProps} videos={[]} loading={true} />);
    
    expect(screen.getByText(/読み込み中/i)).toBeInTheDocument();
  });
});