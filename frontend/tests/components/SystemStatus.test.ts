/**
 * SystemStatus Component Test - T024
 * Phase 1 手動動画管理システム - システム状態表示コンポーネントテスト
 * Note: SystemStatus is integrated into Dashboard.tsx component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import Dashboard from '../../src/components/Dashboard';
import type { SystemStatus, Video } from '../../src/types';

describe('SystemStatus (Dashboard Component)', () => {
  const mockSystemStatus: SystemStatus = {
    api_status: 'healthy',
    m5stack_status: 'online',
    display_status: 'idle',
    uptime: 7200, // 2 hours
    cpu_usage: 45.5,
    memory_usage: 62.3,
    disk_usage: 78.9,
    active_sessions: 1,
    total_videos: 5
  };

  const mockCurrentVideo: Video = {
    id: 'current-video',
    title: 'Currently Playing',
    file_path: '/uploads/current.mp4',
    file_size: 1024 * 1024,
    duration: 120,
    format: 'mp4',
    upload_timestamp: new Date().toISOString(),
    status: 'active'
  };

  const mockUsageStats = {
    totalVideos: 5,
    totalSize: 50 * 1024 * 1024, // 50MB
    avgDuration: 150 // 2.5 minutes
  };

  const mockRecentVideos: Video[] = [
    {
      id: 'recent-1',
      title: 'Recent Video 1',
      file_path: '/uploads/recent1.mp4',
      file_size: 2 * 1024 * 1024,
      duration: 90,
      format: 'mp4',
      upload_timestamp: new Date().toISOString(),
      status: 'active'
    }
  ];

  const mockProps = {
    systemStatus: mockSystemStatus,
    currentVideo: mockCurrentVideo,
    usageStats: mockUsageStats,
    recentVideos: mockRecentVideos
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders system status correctly', () => {
    render(<Dashboard {...mockProps} />);
    
    // Check system status indicators
    expect(screen.getByText('🖥️ システム状態')).toBeInTheDocument();
    expect(screen.getByText('🟢')).toBeInTheDocument(); // Healthy status
    expect(screen.getByText('正常')).toBeInTheDocument();
  });

  it('displays system metrics correctly', () => {
    render(<Dashboard {...mockProps} />);
    
    // Check CPU usage
    expect(screen.getByText('45.5%')).toBeInTheDocument();
    
    // Check memory usage  
    expect(screen.getByText('62.3%')).toBeInTheDocument();
    
    // Check disk usage
    expect(screen.getByText('78.9%')).toBeInTheDocument();
  });

  it('formats uptime correctly', () => {
    render(<Dashboard {...mockProps} />);
    
    expect(screen.getByText('2時間')).toBeInTheDocument();
  });

  it('shows M5STACK status correctly', () => {
    render(<Dashboard {...mockProps} />);
    
    expect(screen.getByText('🤖 M5STACK')).toBeInTheDocument();
    expect(screen.getByText('オンライン')).toBeInTheDocument();
  });

  it('displays current video information', () => {
    render(<Dashboard {...mockProps} />);
    
    expect(screen.getByText('📺 現在の表示')).toBeInTheDocument();
    expect(screen.getByText('Currently Playing')).toBeInTheDocument();
  });

  it('shows usage statistics correctly', () => {
    render(<Dashboard {...mockProps} />);
    
    expect(screen.getByText('📊 利用統計')).toBeInTheDocument();
    expect(screen.getByText('総動画数: 5本')).toBeInTheDocument();
    expect(screen.getByText('50.0MB')).toBeInTheDocument(); // Total size
  });

  it('displays recent videos list', () => {
    render(<Dashboard {...mockProps} />);
    
    expect(screen.getByText('🕒 最近の動画')).toBeInTheDocument();
    expect(screen.getByText('Recent Video 1')).toBeInTheDocument();
  });

  it('shows warning status correctly', () => {
    const warningSystemStatus = {
      ...mockSystemStatus,
      api_status: 'degraded' as const,
      cpu_usage: 85.0
    };

    render(<Dashboard {...mockProps} systemStatus={warningSystemStatus} />);
    
    expect(screen.getByText('🟡')).toBeInTheDocument(); // Warning status
    expect(screen.getByText('85.0%')).toBeInTheDocument(); // High CPU
  });

  it('shows error status correctly', () => {
    const errorSystemStatus = {
      ...mockSystemStatus,
      api_status: 'unhealthy' as const,
      m5stack_status: 'offline' as const
    };

    render(<Dashboard {...mockProps} systemStatus={errorSystemStatus} />);
    
    expect(screen.getByText('🔴')).toBeInTheDocument(); // Error status
    expect(screen.getByText('オフライン')).toBeInTheDocument();
  });

  it('handles no current video correctly', () => {
    render(<Dashboard {...mockProps} currentVideo={null} />);
    
    expect(screen.getByText('動画が選択されていません')).toBeInTheDocument();
  });

  it('displays active sessions count', () => {
    render(<Dashboard {...mockProps} />);
    
    expect(screen.getByText('アクティブセッション: 1')).toBeInTheDocument();
  });

  it('shows performance metrics with appropriate colors', () => {
    const highUsageStatus = {
      ...mockSystemStatus,
      cpu_usage: 90.0,
      memory_usage: 85.0,
      disk_usage: 95.0
    };

    render(<Dashboard {...mockProps} systemStatus={highUsageStatus} />);
    
    // High usage should be displayed with warning colors
    const cpuElement = screen.getByText('90.0%');
    expect(cpuElement.closest('.metric')).toHaveClass('high');
  });

  it('formats large file sizes correctly', () => {
    const largeUsageStats = {
      ...mockUsageStats,
      totalSize: 1.5 * 1024 * 1024 * 1024 // 1.5GB
    };

    render(<Dashboard {...mockProps} usageStats={largeUsageStats} />);
    
    expect(screen.getByText('1.5GB')).toBeInTheDocument();
  });
});