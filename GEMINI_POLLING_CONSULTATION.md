# Gemini様への緊急相談: ポーリングテストタイムアウト問題

## 🚨 現在の状況
vi.advanceTimersByTimeAsync()を使用しても、ポーリングテストが依然として5秒でタイムアウトしています。

### 修正済みコード
```typescript
it('should implement progress callbacks for real-time UI updates', async () => {
  vi.useFakeTimers();

  // Mock progressive responses
  mockFetch
    .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'processing', progress_percent: 30 }) })
    .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'processing', progress_percent: 60 }) })
    .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'completed', progress_percent: 100 }) });

  // GREEN PHASE: Progress callbacks implemented in polling
  const pollingPromise = apiClient.pollVideoStatus(taskId, {
    interval: 1000,
    onProgress: onProgress,
    onStatusChange: vi.fn()
  });

  // Use async timer advances to properly handle async operations
  await vi.advanceTimersByTimeAsync(1001);
  await vi.advanceTimersByTimeAsync(1001);
  await vi.advanceTimersByTimeAsync(1001);

  await pollingPromise;  // ← ここでタイムアウト
  
  vi.useRealTimers();
});
```

### pollVideoStatus実装
```typescript
async pollVideoStatus(taskId: string, options?: {...}): Promise<any> {
  const poll = async (): Promise<any> => {
    const response = await fetch(`${this.baseUrl}/api/videos/status/${taskId}`);
    const data = await response.json();
    
    // Call progress callback if provided
    if (onProgress) onProgress(data);
    
    // Check if polling should continue
    if (data.status === 'completed' || data.status === 'failed') {
      return data;
    }
    
    // Wait and poll again
    await new Promise(resolve => setTimeout(resolve, currentInterval));
    return poll();
  };
  
  return poll();
}
```

## 🤔 問題分析

### 仮説1: setTimeout内部の無限ループ
- setTimeoutが適切にfake timersで制御されていない？
- 再帰的なpoll()が終了条件に達していない？

### 仮説2: fetchモックとsetTimeoutの相互作用
- mockFetch.mockResolvedValueOnceが3回しか設定されていないのに、poll()が4回目を呼んでいる？

### 仮説3: Promiseの解決タイミング
- vi.advanceTimersByTimeAsync()がsetTimeoutを進めても、fetchのPromise解決が追いついていない？

## 🆘 Gemini様への質問

1. **vi.useFakeTimers()でsetTimeoutを使った再帰ポーリングのテスト方法**
   - vi.advanceTimersByTimeAsync()で適切に制御できますか？
   - 別のアプローチが必要ですか？

2. **mockFetchの設定方法**
   - `.mockResolvedValueOnce`を3回使用していますが、4回目以降の呼び出しでundefinedになっていませんか？
   - `.mockImplementation()`に変える必要がありますか？

3. **代替テストアプローチ**
   - ポーリング機能を直接テストする代わりに、モック化を深くすべきですか？
   - setTimeout部分を分離して単体でテストすべきですか？

## 🔧 試したいソリューション案

### 案A: mockFetchを完全制御
```typescript
let callCount = 0;
mockFetch.mockImplementation(() => {
  const responses = [
    { status: 'processing', progress_percent: 30 },
    { status: 'processing', progress_percent: 60 },
    { status: 'completed', progress_percent: 100 }
  ];
  const response = responses[callCount++] || responses[responses.length - 1];
  return Promise.resolve({
    ok: true,
    json: async () => response
  });
});
```

### 案B: ポーリングのモック化
```typescript
// pollVideoStatusの内部的なfetchを独立してテストし、ポーリングロジックは別でテスト
```

どのアプローチが最適でしょうか？Gemini様のご指導をお願いします！