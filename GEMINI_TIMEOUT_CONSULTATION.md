# Gemini相談: T6-010 タイムアウトテスト問題

## 🚨 問題状況
**タイムアウトテストが依然として失敗している**

### 現在の失敗状況
```bash
× tests/services/api.test.ts > Advanced Timeout Handling > should implement configurable request timeout 5020ms
→ Test timed out in 5000ms.
```

### 実装したGemini提案の修正
```typescript
it('should implement configurable request timeout', async () => {
  vi.useFakeTimers();
  
  // Mock a slow fetch request that takes longer than timeout
  mockFetch.mockReturnValueOnce(
    new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          ok: true,
          headers: new Headers(),
          json: async () => createMockVideoResponse()
        });
      }, 1000); // Takes 1000ms but timeout is 500ms
    })
  );

  // GREEN PHASE: apiClient has configurable timeout (500ms timeout for test)
  const timeoutPromise = apiClient.generateVideo(request, { timeout: 500 });
  
  // Advance time to trigger timeout
  await vi.advanceTimersByTimeAsync(500);

  await expect(timeoutPromise)
    .rejects
    .toThrow('Request timeout after 500ms');

  vi.useRealTimers();
});
```

### API Client実装状況
```typescript
// RequestOptions interface exists
export interface RequestOptions {
  timeout?: number;
  maxRetries?: number;
  backoffMultiplier?: number;
  signal?: AbortSignal;
  priority?: 'low' | 'normal' | 'high';
}

// requestWithAdvancedOptions method exists with timeout handling
private async requestWithAdvancedOptions<T>(
  url: string,
  options: RequestInit & { timeout?: number } = {}
): Promise<T> {
  const { timeout = 30000, ...fetchOptions } = options;
  
  const controller = new AbortController();
  const signal = fetchOptions.signal || controller.signal;
  
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, timeout);
  
  try {
    const response = await fetch(url, { ...fetchOptions, signal });
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw await this.parseErrorResponse(response);
    }
    
    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    
    throw error;
  }
}
```

## 🤔 Gemini様への質問

1. **vi.useFakeTimers()とsetTimeoutの相互作用**: 
   - mockFetch内のsetTimeoutはfake timersで制御されますか？
   - vi.advanceTimersByTimeAsync(500)でmockFetch内のsetTimeoutも進みますか？

2. **AbortControllerとの相互作用**:
   - API Client内のsetTimeout（タイムアウト）とmockFetch内のsetTimeout（遅延）の競合は？
   - fake timersでAbortControllerのタイムアウトは正常に動作しますか？

3. **テスト実行順序**:
   ```typescript
   const timeoutPromise = apiClient.generateVideo(request, { timeout: 500 });
   await vi.advanceTimersByTimeAsync(500);
   await expect(timeoutPromise).rejects.toThrow('Request timeout after 500ms');
   ```
   この順序で正しいでしょうか？

4. **代替アプローチ**:
   - fetchをモックする代わりに、AbortController.abort()を直接テストすべき？
   - Promise.race()でのタイムアウト実装をテストすべき？

## 📊 テスト結果詳細
- **Client-side Parameter Validation**: 4/4 tests ✅ PASS
- **Enhanced Error Response Handling**: 3/3 tests ✅ PASS  
- **Advanced Timeout Handling**: 2/3 tests ✅ PASS (retry, AbortController)
- **Advanced Timeout Handling**: 1/3 tests ❌ FAIL (configurable timeout)

## 🚨 UPDATE: Gemini様のact()解決策を実装済み

### ✅ 実装済みの修正
```typescript
import { act } from '@testing-library/react'; // actをインポート

it('should implement configurable request timeout', async () => {
  vi.useFakeTimers();

  // Mock a slow fetch request that takes longer than timeout
  mockFetch.mockReturnValueOnce(
    new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          ok: true,
          headers: new Headers(),
          json: async () => createMockVideoResponse()
        });
      }, 10000); // Takes 10000ms but timeout is 500ms
    })
  );

  const timeoutPromise = apiClient.generateVideo(request, { timeout: 500 });
  
  // actでタイマーの進行と、それに伴う状態更新をラップする
  await act(async () => {
    await vi.advanceTimersByTimeAsync(501);
  });

  await expect(timeoutPromise)
    .rejects
    .toThrow('Request timeout after 500ms');

  vi.useRealTimers();
});
```

### ❌ 依然として失敗
```
× should implement configurable request timeout 5027ms
→ Test timed out in 5000ms.
```

## 🤔 Gemini様への追加質問

1. **act()でも解決しない理由**:
   - act()内でvi.advanceTimersByTimeAsync()を実行しても、テスト自体が5秒でタイムアウトする
   - AbortControllerのabort()イベントが適切に発火していない？

2. **API Client内部のタイムアウト実装確認**:
   ```typescript
   const timeoutId = setTimeout(() => {
     controller.abort();  // これが呼ばれているか？
   }, timeout);
   ```

3. **デバッグのための提案**:
   - console.logでタイムアウト発生タイミングを確認すべき？
   - AbortControllerのabortイベントリスナーが正常に動作しているか確認すべき？

4. **根本的な問題**:
   - fetchのモック自体に問題がある？
   - 非同期処理のチェーンがact()でも解決できない複雑さ？

## 📊 現在のテスト実行結果
```bash
× should implement configurable request timeout 5027ms
→ Test timed out in 5000ms.
```

**Gemini様への緊急相談**: act()解決策でも解決しない理由と、さらなる修正案をお教えください。このテストを通すために他の手法は必要でしょうか？