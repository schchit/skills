---
name: Apple iCloud Suite
description: >
  Apple iCloud 全套服务操作：日历、照片、iCloud Drive、设备查找、提醒事项。
  Use when: (1) 用户要求查看/创建/修改/删除日历事件或日程,
  (2) 用户说"帮我看看今天有什么安排"/"加个日程"/"改一下会议时间",
  (3) 用户要求查找/下载/管理 iCloud 照片,
  (4) 用户提到"查找我的设备"/"手机在哪"/"定位设备",
  (5) 用户要求操作 iCloud Drive 文件（上传/下载/查看）,
  (6) 用户讨论 Apple 生态下的日程管理、照片整理、文件同步。
  即使用户没有明确说"iCloud"或"Apple"，只要涉及日历管理、
  照片操作、设备定位、云端文件管理等 Apple 生态服务，都应使用此技能。
  NOT for: Android 设备管理、Google Calendar/Photos、
  非 Apple 生态的云存储（OneDrive/Google Drive）、钉钉日历（用 mcporter）。
icon: 🍎
os: linux, macos
tools: pyicloud, caldav, icloudpd
install: |
  # Python iCloud API (照片、iCloud Drive、设备等)
  pip install pyicloud
  
  # CalDAV 工具 (日历)
  pip install caldav icalendar
  
  # iCloud 照片批量下载 (可选)
  pip install icloudpd
---

# Apple iCloud Suite

这个 Skill 提供对 Apple iCloud 主要服务的命令行访问能力。

## ✅ 实测验证结果 (2026-02-05)

| 服务 | 状态 | 工具 | 说明 |
|------|------|------|------|
| 📷 **照片** | ✅ 完全可用 | pyicloud / icloudpd | 浏览相册、下载照片 |
| 💾 **iCloud Drive** | ✅ 完全可用 | pyicloud | 浏览和下载文件 |
| 📱 **查找设备** | ✅ 完全可用 | pyicloud | 查看所有设备位置和状态 |
| 📅 **日历** | ✅ 完全可用 | CalDAV (caldav库) | 读取/创建事件 (需应用专用密码) |
| 📝 **备忘录** | ⚠️ 有限支持 | - | Apple Notes 无公开 API |

---

## 🔐 认证方式说明

### ⚠️ 重要发现

**pyicloud API** 需要使用 **主密码 + 双重认证码**，不支持应用专用密码！

**CalDAV (日历)** 可以使用 **应用专用密码**。

### 认证流程

```python
from pyicloud import PyiCloudService
import os

# 中国大陆用户设置环境变量
os.environ['icloud_china'] = '1'

# 使用主密码连接
api = PyiCloudService('your@email.com', '主密码', china_mainland=True)

# 处理双重认证
if api.requires_2fa:
    code = input("请输入 iPhone 上收到的验证码: ")
    api.validate_2fa_code(code)
    print("验证成功！")
```

---

## 服务索引（按需加载详细文档）

| 服务 | 详细文档 | 说明 |
|------|---------|------|
| 📷 照片 | `references/photos.md` | pyicloud + icloudpd，已验证 |
| 💾 iCloud Drive | `references/drive.md` | pyicloud，已验证 |
| 📱 查找设备 | `references/findmy.md` | pyicloud，已验证 |
| 📅 日历 | `references/calendar.md` | CalDAV + vdirsyncer + khal，已验证 |
| 🔧 完整脚本 | `references/scripts.md` | Python 辅助脚本 |

根据用户需要的具体服务，读取对应 reference 文件。

---

## 📋 快速参考

### pyicloud (需要主密码 + 2FA)

| 功能 | 代码 |
|------|------|
| 连接 | `api = PyiCloudService(email, pwd, china_mainland=True)` |
| 照片相册 | `api.photos.albums` |
| 照片列表 | `api.photos.albums['Library'].photos` |
| 下载照片 | `photo.download().raw.read()` |
| iCloud Drive | `api.drive.dir()` |
| 设备列表 | `api.devices` |

### CalDAV (使用应用专用密码)

| 功能 | 命令 |
|------|------|
| 同步 | `vdirsyncer sync` |
| 日历列表 | `khal list today 7d` |
| 创建事件 | `khal new DATE TIME "标题"` |

---

## ⚠️ 注意事项

1. **pyicloud 使用主密码**：不支持应用专用密码，需要双重认证
2. **CalDAV 使用应用专用密码**：在 appleid.apple.com 生成
3. **中国大陆用户**：
   - pyicloud: `china_mainland=True` 或 `os.environ['icloud_china'] = '1'`
   - icloudpd: `--domain cn`
4. **会话缓存**：首次认证后会话会保存在 `~/.pyicloud/`
5. **备忘录限制**：Apple Notes 没有公开 API，建议使用 iCloud.com 网页版

---

## 🔗 相关资源

- [pyicloud GitHub](https://github.com/picklepete/pyicloud)
- [icloudpd GitHub](https://github.com/icloud-photos-downloader/icloud_photos_downloader)
- [vdirsyncer 文档](https://vdirsyncer.pimutils.org/)
- [khal 文档](https://khal.readthedocs.io/)
- [todoman 文档](https://todoman.readthedocs.io/)
