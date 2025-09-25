/**
 * useVideoPolling Hook - T6-008 REFACTOR Phase
 * 
 * VEO動画生成のポーリング機構を提供するカスタムフック
 * 指定間隔でステータスを取得し、完了/失敗で自動停止
 * 
 * @version v2.6.1
 * @author Claude (博士)
 * @created 2025-09-24 (T6-008 GREEN Phase)
 * @updated 2025-09-24 (T6-008 REFACTOR Phase - パフォーマンス最適化)
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { apiClient } from '../services/api';
import type { VideoGeneration } from '../types/video';

/**
 * useVideoPollingのオプション設定
 */
export interface UseVideoPollingOptions {
  /** ポーリング間隔（ミリ秒） デフォルト: 5000 */
  interval?: number;
  /** 自動開始フラグ デフォルト: true */
  autoStart?: boolean;
  /** 完了時コールバック */
  onComplete?: (generation: VideoGeneration) => void;
  /** エラー時コールバック */
  onError?: (error: Error) => void;
}

/**
 * useVideoPollingの戻り値
 */
export interface UseVideoPollingReturn {
  /** 現在の動画生成情報 */
  generation: VideoGeneration | null;
  /** ポーリング中フラグ */
  isPolling: boolean;
  /** エラー情報 */
  error: Error | null;
  /** ポーリング開始 */
  startPolling: () => void;
  /** ポーリング停止 */
  stopPolling: () => void;
}

/**
 * 動画生成のステータスをポーリングするカスタムフック
 * 
 * メモリリーク防止とパフォーマンス最適化を実装済み。
 * コンポーネントのアンマウント時に自動的にクリーンアップされ、
 * taskId変更時も適切にポーリングが切り替わります。
 * 
 * @param taskId - ポーリング対象のタスクID (null/undefined/空文字の場合はポーリングしない)
 * @param options - ポーリングオプション設定
 * @returns ポーリング状態と制御関数
 * 
 * @example
 * ```typescript
 * // 基本的な使用方法
 * const { generation, isPolling, error } = useVideoPolling(taskId);
 * 
 * // カスタムオプション付き
 * const { generation, isPolling, error, stopPolling } = useVideoPolling(taskId, {
 *   interval: 3000, // 3秒間隔
 *   autoStart: false, // 手動開始
 *   onComplete: (gen) => console.log('完了！', gen),
 *   onError: (err) => console.error('エラー:', err)
 * });
 * 
 * // 手動制御
 * const { startPolling, stopPolling } = useVideoPolling(taskId, { autoStart: false });
 * startPolling(); // ポーリング開始
 * stopPolling();  // ポーリング停止
 * ```
 */
export function useVideoPolling(
  taskId?: string | null,
  options: UseVideoPollingOptions = {}
): UseVideoPollingReturn {
  const {
    interval = 5000,
    autoStart = true,
    onComplete,
    onError
  } = options;

  // State management
  const [generation, setGeneration] = useState<VideoGeneration | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Refs for cleanup
  const intervalIdRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  /**
   * ステータス取得処理
   */
  const fetchStatus = useCallback(async () => {
    if (!taskId || !taskId.trim()) {
      return;
    }

    try {
      const result = await apiClient.getVideoStatus(taskId);
      
      // コンポーネントがマウントされている場合のみ更新
      if (isMountedRef.current) {
        setGeneration(result);
        setError(null);

        // 完了状態チェック
        if (result.status === 'completed') {
          setIsPolling(false);
          if (intervalIdRef.current) {
            clearInterval(intervalIdRef.current);
            intervalIdRef.current = null;
          }
          onComplete?.(result);
        } else if (result.status === 'failed') {
          setIsPolling(false);
          if (intervalIdRef.current) {
            clearInterval(intervalIdRef.current);
            intervalIdRef.current = null;
          }
        }
      }
    } catch (err) {
      if (isMountedRef.current) {
        const errorObj = err instanceof Error ? err : new Error(String(err));
        setError(errorObj);
        onError?.(errorObj);
      }
    }
  }, [taskId, onComplete, onError]);

  /**
   * ポーリング開始
   */
  const startPolling = useCallback(() => {
    if (!taskId || !taskId.trim()) {
      return;
    }

    // 既存のintervalをクリア
    if (intervalIdRef.current) {
      clearInterval(intervalIdRef.current);
    }

    setIsPolling(true);
    setError(null);

    // 初回即実行
    fetchStatus();

    // 定期実行設定
    intervalIdRef.current = setInterval(fetchStatus, interval);
  }, [taskId, fetchStatus, interval]);

  /**
   * ポーリング停止
   */
  const stopPolling = useCallback(() => {
    setIsPolling(false);
    if (intervalIdRef.current) {
      clearInterval(intervalIdRef.current);
      intervalIdRef.current = null;
    }
  }, []);

  /**
   * taskId変更時の処理
   */
  useEffect(() => {
    isMountedRef.current = true;

    // taskIdがない場合は何もしない
    if (!taskId || !taskId.trim()) {
      setIsPolling(false);
      setGeneration(null);
      setError(null);
      return;
    }

    // autoStartがtrueの場合は自動開始
    if (autoStart) {
      startPolling();
    }

    // Cleanup
    return () => {
      isMountedRef.current = false;
      if (intervalIdRef.current) {
        clearInterval(intervalIdRef.current);
        intervalIdRef.current = null;
      }
    };
  }, [taskId, autoStart]); // startPollingは依存に含めない（無限ループ防止）

  /**
   * interval変更時の処理
   */
  useEffect(() => {
    if (isPolling && intervalIdRef.current) {
      // 既存のintervalをクリアして新しいintervalで再設定
      clearInterval(intervalIdRef.current);
      intervalIdRef.current = setInterval(fetchStatus, interval);
    }
  }, [interval, fetchStatus, isPolling]);

  return {
    generation,
    isPolling,
    error,
    startPolling,
    stopPolling
  };
}