---
name: jf-open-pro-camera-config
description: 面向开发者控制杰峰设备相关配置，支持动检检测开关和灵敏度设置、人形检测开关和检测灵敏度、人形追踪开关和追踪灵敏度等。触发词：摄像机配置、动检设置、人形检测、人形追踪、灵敏度配置。

# 必需凭证声明 - 平台元数据
credentials:
  required:
    - name: JF_UUID
      type: string
      description: 杰峰开放平台用户唯一标识
      source: https://open.jftech.com/
    - name: JF_APPKEY
      type: string
      description: 杰峰开放平台应用 Key
      source: https://open.jftech.com/
    - name: JF_APPSECRET
      type: string
      description: 杰峰开放平台应用密钥
      source: https://open.jftech.com/
    - name: JF_MOVECARD
      type: integer
      description: 签名算法偏移量 (0-9)
      source: https://open.jftech.com/
  optional:
    - name: JF_SN
      type: string
      description: 设备序列号
    - name: JF_ENDPOINT
      type: string
      description: API 端点
      default: api.jftechws.com
    - name: JF_CHANNEL
      type: integer
      description: 通道号
      default: 0

# 网络端点声明
endpoints:
  - url: https://api.jftechws.com
    description: 杰峰官方 API (国际)
  - url: https://api-cn.jftech.com
    description: 杰峰官方 API (中国大陆)

# 安全声明
security:
  credentials_required: true
  env_vars_only: true  # 仅支持环境变量
  language: python  # 仅支持 Python
---

# JF Open Pro Camera Config

> **面向开发者杰峰设备配置工具 (Python)**
> 
> 支持动检检测开关和灵敏度设置、人形检测开关和检测灵敏度、人形追踪开关和追踪灵敏度等。

---

## 🔒 安全说明

**仅支持环境变量存储凭据**

| 方式 | 支持 | 说明 |
|------|------|------|
| **环境变量** | ✅ 支持 | 不会在进程列表中暴露，不会执行本地代码 |
| **命令行参数** | ❌ 不支持 | 避免凭据泄露风险 |
| **配置文件** | ❌ 不支持 | 避免代码执行风险 |

---

## 🚀 快速开始

### 设置环境变量

```bash
export JF_UUID="your-uuid"              # 开放平台用户唯一标识
export JF_APPKEY="your-appkey"          # 开放平台应用 Key
export JF_APPSECRET="your-appsecret"    # 开放平台应用密钥
export JF_MOVECARD=5                    # 签名算法偏移量 (0-9)
export JF_SN="your-device-sn"           # 设备序列号
export JF_CHANNEL=0                     # 通道号（可选，默认：0）
```

### 使用技能

```bash
# 移动侦测 - 获取配置
python scripts/jf_open_pro_camera_config.py motion-detect --action get

# 移动侦测 - 开启（布防），灵敏度 3
python scripts/jf_open_pro_camera_config.py motion-detect --action set --enable true --level 3

# 移动侦测 - 关闭（撤防）
python scripts/jf_open_pro_camera_config.py motion-detect --action set --enable false

# 人形检测 - 获取配置
python scripts/jf_open_pro_camera_config.py human-detection --action get

# 人形检测 - 开启，灵敏度 2
python scripts/jf_open_pro_camera_config.py human-detection --action set --enable true --sensitivity 2

# 人形检测 - 关闭
python scripts/jf_open_pro_camera_config.py human-detection --action set --enable false

# 人形追踪 - 获取配置
python scripts/jf_open_pro_camera_config.py human-track --action get

# 人形追踪 - 开启，灵敏度 1，10 秒回位
python scripts/jf_open_pro_camera_config.py human-track --action set --enable true --sensitivity 1 --return-time 10

# 人形追踪 - 关闭
python scripts/jf_open_pro_camera_config.py human-track --action set --enable false
```

---

## 📋 环境变量

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `JF_UUID` | 开放平台用户唯一标识 | 是 | - |
| `JF_APPKEY` | 开放平台应用 Key | 是 | - |
| `JF_APPSECRET` | 开放平台应用密钥 | 是 | - |
| `JF_MOVECARD` | 签名算法偏移量 (0-9) | 是 | - |
| `JF_SN` | 设备序列号 | 是 | - |
| `JF_ENDPOINT` | API 端点 | 否 | `api.jftechws.com` |
| `JF_CHANNEL` | 通道号 | 否 | `0` |

---

## 🛠️ 功能

### 1. 移动侦测配置 (Motion Detect)

用于检测画面中的物体移动，触发报警。

| 参数 | 取值范围 | 说明 |
|------|---------|------|
| Enable | true/false | 布防/撤防开关 |
| Level | 1-6 | 灵敏度，1 最低，6 最高 |

**灵敏度说明：**
| 值 | 说明 |
|----|------|
| 1 | 最低灵敏度 |
| 2 | 较低灵敏度 |
| 3 | 中等灵敏度 |
| 4 | 较高灵敏度 |
| 5 | 很高灵敏度 |
| 6 | 最高灵敏度 |

---

### 2. 人形检测配置 (Human Detection)

使用 AI 算法检测画面中的人形目标，比移动侦测更准确。

| 参数 | 取值范围 | 说明 |
|------|---------|------|
| Enable | true/false | 开关 |
| Sensitivity | 0-3 | 灵敏度，0 低，1 中，2 高 |
| ObjectType | 0-1 | 0 检测人，1 检测物体 |

**灵敏度说明：**
| 值 | 说明 |
|----|------|
| 0 | 低灵敏度 |
| 1 | 中灵敏度 |
| 2 | 高灵敏度 |
| 3 | 灵敏度数量（只读） |

**检测类型：**
| 值 | 说明 |
|----|------|
| 0 | 检测人 |
| 1 | 检测物体 |

---

### 3. 人形追踪配置 (Human Track)

云台自动跟随人形目标移动。

| 参数 | 取值范围 | 说明 |
|------|---------|------|
| Enable | 0/1 | 开关（整数而非布尔值） |
| Sensitivity | 0-2 | 灵敏度，0 低，1 中，2 高 |
| ReturnTime | 0-600 | 无人后回位时间（秒），0 不返回 |

**灵敏度说明：**
| 值 | 说明 |
|----|------|
| 0 | 低灵敏度 |
| 1 | 中灵敏度 |
| 2 | 高灵敏度 |

**回位时间：**
| 值 | 说明 |
|----|------|
| 0 | 不返回 |
| 1-600 | 秒后返回默认位置（守望位） |

---

## 📖 使用场景示例

### 场景 1: 开启所有检测功能

```bash
# 开启移动侦测（灵敏度 3）
python scripts/jf_open_pro_camera_config.py motion-detect --action set --enable true --level 3

# 开启人形检测（灵敏度 2）
python scripts/jf_open_pro_camera_config.py human-detection --action set --enable true --sensitivity 2

# 开启人形追踪（灵敏度 1，10 秒回位）
python scripts/jf_open_pro_camera_config.py human-track --action set --enable true --sensitivity 1 --return-time 10
```

### 场景 2: 夜间模式（只保留移动侦测）

```bash
# 关闭人形检测
python scripts/jf_open_pro_camera_config.py human-detection --action set --enable false

# 关闭人形追踪
python scripts/jf_open_pro_camera_config.py human-track --action set --enable false

# 提高移动侦测灵敏度
python scripts/jf_open_pro_camera_config.py motion-detect --action set --enable true --level 5
```

### 场景 3: 查看当前配置

```bash
# 查看移动侦测配置
python scripts/jf_open_pro_camera_config.py motion-detect --action get

# 查看人形检测配置
python scripts/jf_open_pro_camera_config.py human-detection --action get

# 查看人形追踪配置
python scripts/jf_open_pro_camera_config.py human-track --action get
```

---

## ⚠️ 错误处理

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `2000` | 成功 | - |
| `4118` | 连接超时 | 设备离线/休眠，稍后重试 |
| `10001` | Token 无效 | 重新获取 Token |
| `10002` | 设备未登录 | 脚本会自动处理登录 |

---

## ⚠️ 注意事项

1. **设备需在线** - 操作前确保设备在线
2. **设备需登录** - 脚本会自动处理设备登录
3. **人形追踪限制** - 需要画面正放且能识别出人形才生效
4. **灵敏度调整** - 过高可能导致误报，过低可能漏报
5. **通道号** - 默认通道 0，NVR 设备可通过 `JF_CHANNEL` 环境变量指定

---

## 📚 官方参考资料

- **杰峰开放平台**: https://open.jftech.com/
- **API 文档**: https://docs.jftech.com/
- **API 端点**: `api.jftechws.com` (国际) / `api-cn.jftech.com` (中国大陆)

---

## 📁 脚本工具

```bash
# 获取帮助
python scripts/jf_open_pro_camera_config.py --help

# 移动侦测
python scripts/jf_open_pro_camera_config.py motion-detect --action <get|set>

# 人形检测
python scripts/jf_open_pro_camera_config.py human-detection --action <get|set>

# 人形追踪
python scripts/jf_open_pro_camera_config.py human-track --action <get|set>
```

脚本路径：`scripts/jf_open_pro_camera_config.py`

---

**技能版本：** v1.0.0  
**语言：** Python  
**最后更新：** 2026-04-07
