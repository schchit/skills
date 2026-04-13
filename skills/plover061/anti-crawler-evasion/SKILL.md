---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100d96eacc00aaef2df66fac2907daa80e9c97164cd110cbafd24cfa24f2ed6eb1002200b67842b9cb4dc33fea7842e5c36d382acdc8af97acfa296eca60c7c37781004
    ReservedCode2: 30440220229245186045ff828a3c36671b229334b3c4f720609f75455642ae84cec80b72022066fecc9741e8ff5517940746052c4ca9828b3940996c2477e5061744dc81fb2c
description: 防止被反爬虫机制识别和封禁。当用户需要进行网页爬取、数据采集、API访问，或询问如何绕过反爬、避免IP封禁、隐藏爬虫身份时使用。触发词包括：反爬、反爬虫、绕过反爬、避免封禁、爬虫伪装、隐身爬取。
name: anti-crawler-evasion
---

# Anti-Crawler Evasion Skill

## 核心策略概览

### 1. 请求伪装策略

#### User-Agent轮换
```python
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
]

def get_random_ua():
    return random.choice(USER_AGENTS)
```

#### 请求头完整性
```python
HEADERS = {
    "User-Agent": get_random_ua(),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}
```

### 2. IP轮换方案

#### 代理池策略
```python
import requests

PROXY_POOL = [
    {"http": "http://user:pass@proxy1.example.com:8080"},
    {"http": "http://user:pass@proxy2.example.com:8080"},
    {"http": "http://user:pass@proxy3.example.com:8080"}
]

def get_random_proxy():
    return random.choice(PROXY_POOL)

def fetch_with_proxy(url):
    proxy = get_random_proxy()
    response = requests.get(url, proxies=proxy, headers=HEADERS)
    return response
```

#### 代理类型选择
| 代理类型 | 匿名度 | 适用场景 | 成本 |
|---------|--------|----------|------|
| 住宅代理 | 高 | 高级反爬绕过 | 高 |
| 数据中心代理 | 中 | 常规爬取 | 中 |
| 旋转代理 | 高 | 大规模采集 | 高 |
| 免费代理 | 低 | 测试/演示 | 无 |

### 3. 访问频率控制

```python
import time
import random

class RateLimiter:
    def __init__(self, min_delay=3, max_delay=10):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request = 0

    def wait(self):
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)

    def adaptive_wait(self, response):
        """根据响应状态自适应调整延迟"""
        if response.status_code == 429:
            time.sleep(60)  # 遇到限流，等待更长时间
        elif response.status_code == 200:
            # 成功请求后稍微增加延迟，降低被封风险
            delay = random.uniform(self.min_delay, self.max_delay) * 1.5
            time.sleep(delay)
```

### 4. 浏览器指纹规避

#### 指纹随机化
```python
from selenium import webdriver
from selenium_stealth import stealth

def create_stealth_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(options=options)

    stealth(driver,
        languages=["en-US", "en", "zh-CN", "zh"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver
```

### 5. Cookie和会话管理

```python
import requests
from http.cookiejar import CookieJar

session = requests.Session()

# 保持Cookie持久化
session.cookies = CookieJar()

# 从真实浏览器导入Cookie
def import_browser_cookies(session, browser="chrome"):
    """从浏览器导入Cookie以通过初验"""
    # 实现细节根据目标浏览器而定
    pass
```

### 6. JavaScript挑战绕过

#### 使用Playwright/Selenium处理JS渲染
```python
from playwright.sync_api import sync_playwright

def scrape_dynamic_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=get_random_ua(),
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        # 模拟人类行为
        page.goto(url)
        page.mouse.wheel(0, 500)  # 模拟滚动
        page.wait_for_timeout(2000)  # 随机等待

        content = page.content()
        browser.close()
        return content
```

### 7. 验证码处理策略

#### 第三方验证码服务
```python
# 2Captcha API集成
import requests

def solve_captcha(site_key, page_url):
    """使用2Captcha解决验证码"""
    api_key = "YOUR_API_KEY"

    # 提交验证码
    submit_url = f"http://2captcha.com/in.php?key={api_key}&method=userrecaptcha&googlekey={site_key}&pageurl={page_url}"
    resp = requests.get(submit_url)
    captcha_id = resp.text.split('|')[1]

    # 等待结果
    for _ in range(30):
        time.sleep(5)
        result_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}"
        result = requests.get(result_url)
        if result.text.startswith('OK'):
            return result.text.split('|')[1]

    return None
```

## 高级规避技术

### 分布式爬取架构
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Master    │────▶│   Workers   │────▶│  Proxy Pool │
│   Server    │     │   (多个)     │     │  (轮换IP)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Task Queue │
                    │  (Redis)    │
                    └─────────────┘
```

### 行为模拟
```python
from mouse import move, click
from keyboard import write, press
import random
import time

def human_behavior_simulation(driver, element):
    """模拟人类行为操作元素"""
    rect = element.rect

    # 随机偏移模拟鼠标移动
    x = rect['x'] + random.randint(5, 20)
    y = rect['y'] + random.randint(5, 20)

    # 鼠标移动（不直线路径）
    move_in_human_pattern(x, y)

    # 随机延迟
    time.sleep(random.uniform(0.1, 0.3))

    # 点击
    click(x, y)

def move_in_human_pattern(target_x, target_y):
    """模拟人类鼠标移动路径"""
    # 添加随机中间点
    current_x, current_y = get_current_mouse_position()
    points = generate_human_path(current_x, current_y, target_x, target_y)

    for x, y in points:
        move(x, y)
        time.sleep(random.uniform(0.01, 0.03))
```

## 检测规避清单

| 检测类型 | 规避方法 | 优先级 |
|---------|---------|--------|
| IP频率检测 | 代理轮换 + 延迟 | 高 |
| User-Agent检测 | UA轮换池 | 高 |
| Cookie/Session检测 | 真实浏览器Cookie | 中 |
| 行为模式检测 | 人性化操作模拟 | 高 |
| 浏览器指纹检测 | Stealth模式 | 中 |
| JavaScript检测 | 使用真实浏览器 | 高 |
| 验证码 | 第三方识别服务 | 按需 |

## 最佳实践

1. **渐进式部署**：从低频率开始，逐步调整策略
2. **监控响应**：密切关注HTTP状态码和响应时间
3. **备用方案**：准备多个数据源，避免单点依赖
4. **遵守规则**：优先遵守robots.txt和网站条款
5. **日志记录**：详细记录请求和响应，便于问题排查

## 常见反爬绕过场景

### 场景1: IP封禁
- 症状: HTTP 403/429
- 解决: 接入代理池，降低请求频率

### 场景2: 验证码拦截
- 症状: 页面出现验证码
- 解决: 验证码识别服务或手动处理

### 场景3: JavaScript渲染
- 症状: 页面内容为空或加密
- 解决: 使用Playwright/Selenium

### 场景4: 行为分析拦截
- 症状: 无明显错误但数据异常
- 解决: 添加人性化行为模拟

## 工具推荐

| 工具 | 用途 | 场景 |
|------|------|------|
| Playwright | 浏览器自动化 | JS渲染页面 |
| Selenium + Stealth | 浏览器伪装 | 需要登录的页面 |
| ScraperAPI | 云端代理服务 | 快速集成 |
| Crawlera | 智能代理池 | 企业级应用 |
| 2Captcha | 验证码识别 | 验证码拦截 |
