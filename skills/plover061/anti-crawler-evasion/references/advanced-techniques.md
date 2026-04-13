---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100dff91a5ee52581a469fa72d3300685228697e144e9ab763a9893b467e44ce5d402210080bf2a79a18fc53a72835d650a565a640ebed32ca8e4c6e1f0fe042bca44783c
    ReservedCode2: 304502203e6a1ab77645d578f8af23471b85f763bef19e7e824d779cedb38648a8139827022100ed803e77ac65c2e95d194fced77fffc5215853ddfcec979569a123e83cbafb73
---

# 高级反爬技术参考

## 常见反爬机制分类

### 1. 网络层检测
- IP频率限制
- 地理位置检测
- 网络指纹识别

### 2. 应用层检测
- User-Agent验证
- Cookie/Session分析
- 请求头完整性检查

### 3. 行为层检测
- 鼠标轨迹分析
- 点击模式识别
- 滚动行为分析

### 4. 浏览器层检测
- WebDriver/Selenium检测
- 浏览器指纹比对
- Canvas/WebGL指纹

## 代理服务提供商

| 提供商 | 类型 | 特点 | 价格 |
|--------|------|------|------|
| Luminati (Bright Data) | 住宅代理 | 高匿名，全球覆盖 | 高 |
| Oxylabs | 混合代理 | 稳定高速 | 高 |
| SmartProxy | 住宅代理 | 易用性好 | 中 |
| ScraperAPI | API服务 | 简化集成 | 按调用 |
| Crawlera | 智能代理 | 自动轮换 | 按流量 |

## 验证码类型及处理

### 1. reCAPTCHA v2/v3
- 图像选择验证码
- 分数评估验证码

### 2. hCaptcha
- 隐私导向的验证码

### 3. Cloudflare Turnstile
- 无感知验证码

### 4. 滑块验证码
- 图片缺口识别
- 轨迹模拟

## 浏览器指纹参数

### 需要随机化的参数
- User-Agent
- Accept-Language
- Accept-Encoding
- Screen Resolution
- Timezone
- WebGL Renderer
- Canvas Hash
- Audio Context

### Stealth插件参数示例
```javascript
navigator.webdriver = false
navigator.languages = ['en-US', 'en', 'zh-CN']
navigator.plugins = [真实浏览器插件列表]
window.chrome = { runtime: {} }
```
