# jf-open-camera-config

JF 杰峰摄像机配置技能。

## 功能

- 移动侦测配置（布防/撤防/灵敏度 1-6）
- 人形检测配置（开关/灵敏度 0-3/检测类型）
- 人形追踪配置（开关/灵敏度 0-2/回位时间）

## 安装

将 `jf-open-camera-config.skill` 文件放入 OpenClaw 的 skills 目录：

```bash
cp jf-open-camera-config.skill ~/.openclaw/workspace/skills/
```

## 使用

### Node.js 版本

```bash
# 获取移动侦测配置
node scripts/jf-open-camera-config.js motion-detect \
  --uuid <uuid> --appkey <appKey> --appsecret <appSecret> --sn <设备 SN> \
  --action get

# 开启移动侦测（布防），灵敏度 3
node scripts/jf-open-camera-config.js motion-detect \
  --uuid <uuid> --appkey <appKey> --appsecret <appSecret> --sn <设备 SN> \
  --action set --enable true --level 3
```

### Python 版本

```bash
# 获取人形检测配置
python3 scripts/jf_open_camera_config.py human-detection \
  --uuid <uuid> --appkey <appKey> --appsecret <appSecret> --sn <设备 SN> \
  --action get

# 开启人形检测，灵敏度 2
python3 scripts/jf_open_camera_config.py human-detection \
  --uuid <uuid> --appkey <appKey> --appsecret <appSecret> --sn <设备 SN> \
  --action set --enable true --sensitivity 2
```

## 必需参数

| 参数 | 说明 |
|------|------|
| `--uuid` | 开放平台用户 uuid |
| `--appkey` | 开放平台应用 Key |
| `--appsecret` | 应用密钥 |
| `--sn` | 设备序列号 |

## 示例

```bash
# 开启所有检测功能
node scripts/jf-open-camera-config.js motion-detect \
  --uuid xxx --appkey xxx --appsecret xxx --sn <SN> \
  --action set --enable true --level 3

node scripts/jf-open-camera-config.js human-detection \
  --uuid xxx --appkey xxx --appsecret xxx --sn <SN> \
  --action set --enable true --sensitivity 2

node scripts/jf-open-camera-config.js human-track \
  --uuid xxx --appkey xxx --appsecret xxx --sn <SN> \
  --action set --enable true --sensitivity 1 --return-time 10
```

## 完整文档

详见 `SKILL.md`

## 许可证

MIT
