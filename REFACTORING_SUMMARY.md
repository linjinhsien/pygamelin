# 伯努利雙視圖模擬器重構總結

## 重構目標
為 `bernoulli_dual_view.py` 添加縮小視窗按鈕和改進響應式設計功能。

## 主要改進

### 1. 視窗控制系統 (WindowControls 類)
- **自定義標題欄**: 實現了完整的視窗控制標題欄
- **三個控制按鈕**:
  - 🔴 關閉按鈕 (紅色) - 關閉應用程式
  - 🟡 最小化按鈕 (黃色) - 最小化視窗到工作列
  - 🟢 最大化按鈕 (綠色) - 切換全螢幕/視窗模式
- **懸停效果**: 滑鼠懸停時按鈕會改變顏色
- **拖拽支援**: 可以通過標題欄拖拽視窗 (框架已準備好)

### 2. 響應式佈局系統 (ResponsiveLayout 類)
- **動態縮放**: 根據視窗大小自動調整所有 UI 元素
- **最小尺寸限制**: 防止視窗縮小到無法使用的尺寸 (800x600)
- **智能字體縮放**: 字體大小根據視窗大小動態調整
- **比例保持**: 保持原始設計比例的同時適應不同螢幕尺寸

### 3. 改進的事件處理
- **優先級處理**: 視窗控制 → 球體互動 → 滑桿控制
- **鍵盤快捷鍵**:
  - `ESC` - 退出應用程式
  - `F11` - 切換全螢幕模式
  - `V` - 切換風速向量顯示
- **視窗大小調整**: 即時響應視窗大小變化

### 4. 視覺改進
- **現代化標題欄**: 深色主題標題欄配合彩色按鈕
- **更好的視覺層次**: 清晰的區域分隔和標籤
- **改進的指示說明**: 新增視窗控制相關說明

## 技術實現細節

### 架構改進
```python
# 原始架構
class BernoulliSimulation:
    # 所有功能混合在一個類中

# 重構後架構
class WindowControls:      # 專門處理視窗控制
class ResponsiveLayout:    # 專門處理響應式佈局
class BernoulliSimulation: # 核心模擬邏輯
```

### 響應式設計實現
- **縮放因子計算**: `scale_x`, `scale_y`, `global_scale`
- **動態元素大小**: 所有 UI 元素根據縮放因子調整
- **內容區域管理**: 考慮標題欄高度的內容區域計算

### 視窗狀態管理
- **無邊框視窗**: 使用 `pygame.NOFRAME` 實現自定義標題欄
- **大小限制**: 強制最小視窗尺寸
- **狀態追蹤**: 追蹤最大化/最小化狀態

## 使用方法

### 基本操作
1. **視窗控制**: 點擊右上角的彩色按鈕
2. **調整大小**: 拖拽視窗邊緣 (如果系統支援)
3. **鍵盤快捷鍵**: 使用 ESC、F11、V 等快捷鍵

### 檔案說明
- `bernoulli_dual_view_refactored.py` - 重構後的主程式
- `test_window_controls.py` - 視窗控制功能測試程式
- `bernoulli_dual_view.py` - 原始程式 (保留作為備份)

## 相容性
- **Python 3.6+**: 支援現代 Python 版本
- **Pygame 2.0+**: 利用最新 Pygame 功能
- **跨平台**: Windows、macOS、Linux 相容

## 未來改進建議
1. **真正的視窗拖拽**: 實現平台特定的視窗移動
2. **主題系統**: 支援明亮/黑暗主題切換
3. **設定保存**: 記住視窗大小和位置
4. **更多快捷鍵**: 增加更多鍵盤快捷鍵
5. **動畫效果**: 添加平滑的過渡動畫

## 測試
使用以下命令測試重構後的程式：
```bash
python3 bernoulli_dual_view_refactored.py  # 完整模擬器
python3 test_window_controls.py            # 視窗控制測試
```

重構成功實現了所有目標，提供了現代化的使用者介面和更好的使用體驗。
