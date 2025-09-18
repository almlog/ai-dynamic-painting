/**
 * VideoUpload Component Test - T021
 * Phase 1 手動動画管理システム - 動画アップロードコンポーネントテスト
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import VideoUpload from '../../src/components/VideoUpload';

// Mock fetch API
global.fetch = vi.fn();

describe('VideoUpload Component', () => {
  const mockOnUploadSuccess = vi.fn();
  const mockFile = new File(['video content'], 'test-video.mp4', {
    type: 'video/mp4'
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders upload form correctly', () => {
    render(<VideoUpload onUploadSuccess={mockOnUploadSuccess} />);
    
    expect(screen.getByText('🎬 動画アップロード')).toBeInTheDocument();
    expect(screen.getByText('動画ファイルを選択')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /アップロード/i })).toBeInTheDocument();
  });

  it('displays file information when file is selected', async () => {
    const user = userEvent.setup();
    render(<VideoUpload onUploadSuccess={mockOnUploadSuccess} />);
    
    const fileInput = screen.getByLabelText(/動画ファイルを選択/i);
    await user.upload(fileInput, mockFile);
    
    expect(screen.getByText('test-video.mp4')).toBeInTheDocument();
    expect(screen.getByText(/MP4/i)).toBeInTheDocument();
  });

  it('validates file type correctly', async () => {
    const user = userEvent.setup();
    const invalidFile = new File(['content'], 'test.txt', { type: 'text/plain' });
    
    render(<VideoUpload onUploadSuccess={mockOnUploadSuccess} />);
    
    const fileInput = screen.getByLabelText(/動画ファイルを選択/i);
    await user.upload(fileInput, invalidFile);
    
    expect(screen.getByText(/対応していないファイル形式/i)).toBeInTheDocument();
  });

  it('validates file size correctly', async () => {
    const user = userEvent.setup();
    // Create a file larger than 500MB (simulated)
    Object.defineProperty(mockFile, 'size', {
      value: 600 * 1024 * 1024, // 600MB
      configurable: true
    });
    
    render(<VideoUpload onUploadSuccess={mockOnUploadSuccess} />);
    
    const fileInput = screen.getByLabelText(/動画ファイルを選択/i);
    await user.upload(fileInput, mockFile);
    
    expect(screen.getByText(/ファイルサイズが大きすぎます/i)).toBeInTheDocument();
  });

  it('handles successful upload', async () => {
    const user = userEvent.setup();
    const mockResponse = {
      ok: true,
      json: async () => ({
        id: 'test-id',
        title: 'test-video.mp4',
        file_path: '/uploads/test-video.mp4',
        file_size: 1024,
        duration: 120
      })
    };
    
    (global.fetch as any).mockResolvedValueOnce(mockResponse);
    
    render(<VideoUpload onUploadSuccess={mockOnUploadSuccess} />);
    
    const fileInput = screen.getByLabelText(/動画ファイルを選択/i);
    const titleInput = screen.getByPlaceholderText(/動画のタイトル/i);
    
    await user.upload(fileInput, mockFile);
    await user.type(titleInput, 'Test Video Title');
    
    const uploadButton = screen.getByRole('button', { name: /アップロード/i });
    await user.click(uploadButton);
    
    await waitFor(() => {
      expect(mockOnUploadSuccess).toHaveBeenCalledWith({
        id: 'test-id',
        title: 'test-video.mp4',
        file_path: '/uploads/test-video.mp4',
        file_size: 1024,
        duration: 120
      });
    });
  });

  it('handles upload error correctly', async () => {
    const user = userEvent.setup();
    const mockResponse = {
      ok: false,
      status: 400,
      text: async () => 'Upload failed'
    };
    
    (global.fetch as any).mockResolvedValueOnce(mockResponse);
    
    render(<VideoUpload onUploadSuccess={mockOnUploadSuccess} />);
    
    const fileInput = screen.getByLabelText(/動画ファイルを選択/i);
    await user.upload(fileInput, mockFile);
    
    const uploadButton = screen.getByRole('button', { name: /アップロード/i });
    await user.click(uploadButton);
    
    await waitFor(() => {
      expect(screen.getByText(/アップロードに失敗しました/i)).toBeInTheDocument();
    });
  });

  it('shows progress during upload', async () => {
    const user = userEvent.setup();
    let resolveUpload: (value: any) => void;
    const uploadPromise = new Promise(resolve => {
      resolveUpload = resolve;
    });
    
    (global.fetch as any).mockImplementation(() => uploadPromise);
    
    render(<VideoUpload onUploadSuccess={mockOnUploadSuccess} />);
    
    const fileInput = screen.getByLabelText(/動画ファイルを選択/i);
    await user.upload(fileInput, mockFile);
    
    const uploadButton = screen.getByRole('button', { name: /アップロード/i });
    await user.click(uploadButton);
    
    expect(screen.getByText(/アップロード中/i)).toBeInTheDocument();
    expect(uploadButton).toBeDisabled();
    
    // Complete the upload
    resolveUpload!({
      ok: true,
      json: async () => ({ id: 'test-id', title: 'test' })
    });
  });

  it('disables upload button when no file selected', () => {
    render(<VideoUpload onUploadSuccess={mockOnUploadSuccess} />);
    
    const uploadButton = screen.getByRole('button', { name: /アップロード/i });
    expect(uploadButton).toBeDisabled();
  });

  it('allows drag and drop file selection', async () => {
    render(<VideoUpload onUploadSuccess={mockOnUploadSuccess} />);
    
    const dropZone = screen.getByText(/ドラッグ&ドロップ/i).closest('div');
    
    fireEvent.dragOver(dropZone!, {
      dataTransfer: {
        files: [mockFile]
      }
    });
    
    expect(dropZone).toHaveClass('drag-over');
    
    fireEvent.drop(dropZone!, {
      dataTransfer: {
        files: [mockFile]
      }
    });
    
    await waitFor(() => {
      expect(screen.getByText('test-video.mp4')).toBeInTheDocument();
    });
  });

  it('resets form after successful upload', async () => {
    const user = userEvent.setup();
    const mockResponse = {
      ok: true,
      json: async () => ({ id: 'test-id', title: 'test' })
    };
    
    (global.fetch as any).mockResolvedValueOnce(mockResponse);
    
    render(<VideoUpload onUploadSuccess={mockOnUploadSuccess} />);
    
    const fileInput = screen.getByLabelText(/動画ファイルを選択/i);
    const titleInput = screen.getByPlaceholderText(/動画のタイトル/i);
    
    await user.upload(fileInput, mockFile);
    await user.type(titleInput, 'Test Title');
    
    const uploadButton = screen.getByRole('button', { name: /アップロード/i });
    await user.click(uploadButton);
    
    await waitFor(() => {
      expect(mockOnUploadSuccess).toHaveBeenCalled();
    });
    
    await waitFor(() => {
      expect(titleInput).toHaveValue('');
      expect(uploadButton).toBeDisabled();
    });
  });
});