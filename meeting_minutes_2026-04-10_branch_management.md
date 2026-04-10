# 運營議事錄：GitHub 分支選擇與專案管理討論

- **會議日期**：2026年04月10日
- **會議時間**：20:33
- **會議地點**：GitHub 分支選擇介面
- **參與對象**：開發團隊

## 一、6W2H 概況

- **When（何時）**：2026年04月10日 20:33
- **Where（在哪裡）**：GitHub 分支選擇介面
- **Who（誰做）**：開發團隊
- **What（做什麼）**：確認專案分支結構與功能修復進度
- **Why（為什麼）**：確保程式碼版本正確並解決特定的視窗控制問題
- **How（怎麼做）**：透過切換不同分支進行開發與測試
- **Whom（對誰）**：開發者及專案維護者
- **How much（花費多少）**：不適用

## 二、OGISM 架構

- **Objective（目的）**：完善專案開發流程與功能穩定性。
- **Goal（目標）**：
  - 維護主線（main）穩定性。
  - 完成特定功能與 Bug 修復。
- **Issue（課題）**：
  - Pygame 視窗控制功能異常。
  - 新功能分支 `2dplate` 的整合需求。
- **Strategy（策略）**：採用**功能分支開發模式**，隔離修復補丁與實驗性功能。
- **Action（行動）**：
  1. 維護 `main` 作為預設發布分支。
  2. 於 `fix-pygame-window-controls` 分支進行 Bug 修復。
  3. 於 `2dplate` 分支進行新功能開發。

## 三、TWOS 深度整理

- **Things Worth Overcoming（需克服的事項）**：
  - 修復 Pygame 視窗控制相關問題。
- **Things Worth Organizing（需整理的事項）**：
  - 確認各分支最新提交紀錄與合併狀態。
- **Things Worth Starting（需開始的事項）**：
  - 針對 `2dplate` 功能建立與執行單元測試。
- **Things Worth Sharing（需分享的事項）**：
  - 開發規範與分支命名慣例。

## 四、分支清單與狀態

1. **`main`（Default）**：目前穩定版本分支。
2. **`2dplate`**：開發中的新功能分支。
3. **`fix-pygame-window-controls`**：用於修復 Pygame 視窗控制問題之分支。

## 五、下一步行動計畫

- **負責人**：開發團隊
- **優先事項**：
  1. 優先完成 `fix-pygame-window-controls` 的程式碼審閱（Code Review）。
  2. 修復確認後將該分支併入 `main`。
  3. 持續追蹤 `2dplate` 的開發進度與測試結果。

## 六、URL 一覽

- 目前無外部連結。
