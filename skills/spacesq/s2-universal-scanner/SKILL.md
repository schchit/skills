---
name: s2-universal-scanner
description: S2-SP-OS Universal Spatial Sensor Sniffer. Scans LAN for wired/wireless sensors (Modbus, MQTT, Matter, KNX) via active port knocking and cross-verifies sleeping nodes (Zigbee/BLE) via Gateway APIs. Decomposes multi-sensors (e.g. GH-506). / S2 万能空间传感器探测器。主动嗅探有线/无线物联网传感协议，通过网关 API 对账休眠节点，并解构多合一传感器。
version: 1.0.0
author: Space2.world
homepage: https://space2.world/s2-sp-os
tags: [S2-SP-OS, Nmap, IoT-Scanner, Modbus, MQTT, Home-Assistant]
metadata: {"clawdbot":{"emoji":"📡","requires":{"bins":["python3"], "pip":["requests"], "env":["S2_PRIVACY_CONSENT", "S2_HA_TOKEN"]}}}
allowed-tools: [exec]
---

# 📡 S2-Universal-Scanner: Spatial IoT Discovery / 空间万能探测器

Welcome to the **S2 Universal Scanner**. 
This is the ultimate Nmap for Spatial Intelligence. It performs active network sniffing for environmental sensors and passive cross-verification with existing Smart Home Gateways to find sleeping nodes.

这是空间智能的终极雷达。它通过主动网络嗅探发现环境传感器，并与现有的智能家居网关（如 Home Assistant）进行被动对账，找出处于休眠状态的电池节点。

## 🧬 Core Capabilities / 核心能力
1. **Active Sniffing (主动火力侦察)**: Sweeps LAN for MQTT (1883), Modbus (502), Matter (5540), and BACnet (47808) signatures. / 扫段识别主流物联网感知端口。
2. **Sleeping Node Bypass (休眠节点对账)**: If `S2_HA_TOKEN` is provided, it secretly pulls the Gateway's registry to find offline BLE/Zigbee sensors. / 通过网关 API 拉取配置清单，防止漏掉休眠的低功耗传感器。
3. **Multi-Sensor Decomposition (多合一解构)**: Automatically breaks down industrial sensors (like the GH-506 6-in-1) into discrete S2 atomic elements (`s2-atmos`, `s2-acoustic`). / 将复杂的六合一工业传感器解构为 S2 原子级感知要素。

## 🤖 Instructions for AI Agents (CRITICAL)

**Prerequisite:** `export S2_PRIVACY_CONSENT=1`. Optionally, set `export S2_HA_TOKEN=xxx` for sleeping node discovery.

**Action: Run the Universal Scan / 动作：执行全网格扫描**
```bash
python3 universal_scanner.py --target-subnet 192.168.1.0/24 --zone outdoor_balcony --grid x1_y1

Cognitive Post-Processing (大脑后处理):
When the tool returns the final_sensor_inventory, you (the Agent) MUST mentally register these devices. If a GH-506 is found, you now know this grid has temperature, noise, and air quality capabilities, and you must link them to the respective S2 OS perception modules.