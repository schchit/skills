---
name: s2-acoustic-perception
description: S2-SP-OS Acoustic Radar. Edge-delegated zero-shot classification with Ephemeral Privacy (audio is instantly destroyed after semantic tagging). / S2-SP-OS 语义声学雷达。本地边缘零样本分类，采用“阅后即焚”机制保障绝对隐私。
version: 1.0.0
author: Space2.world
homepage: https://space2.world/s2-sp-os
tags: [S2-SP-OS, Acoustic, Ephemeral-Privacy, AI-Audio, Voxel]
metadata: {"clawdbot":{"emoji":"🎧","requires":{"bins":["python3"], "pip":["sounddevice", "numpy"]}}}
allowed-tools: [exec]
---

# 🎧 S2-Acoustic-Perception: Semantic Acoustic Radar / 语义声学雷达

Welcome to the **S2 Acoustic Perception Client**. 
Built on the principle of **Ephemeral Privacy (阅后即焚)**, this radar listens to the environment but *forgets* the raw audio instantly. It sends a short slice to the trusted Local Edge Brain, which returns only the semantic meaning (e.g., "music", "dog_barking", "human_conversation"). The audio payload is strictly deleted from RAM.

基于**“阅后即焚”**的隐私理念，本雷达倾听环境但绝不留存录音。短时切片被送往受信任的本地边缘大脑，大脑仅返回语义标签（如：音乐、狗吠、人类对话），原生音频在客户端内存中被立刻销毁。

## 🧬 Core Features / 核心特性
1. **Semantic Privacy (语义级隐私)**: Recognizes human speech vs. vocal music accurately. Raw audio is never stored or sent to the cloud. / 精准区分人类对话与声乐演唱，原始录音绝不上云、绝不持久化。
2. **Edge-Brain Delegation (边缘大脑调度)**: Offloads heavy AI neural networks to a local LAN API server. / 将繁重的 AI 神经网络算力卸载至局域网 API 服务器。
3. **Memzero Voxel (记忆体封装)**: Retains acoustic evidence *only* for non-privacy events (like pet distress) for Agent multimodal cross-checking. / 仅针对非隐私事件（如宠物异常）留存证据，供多模态联动。

---

## 🤖 Instructions for AI Agents (CRITICAL)

**Phase 1: Authorized Acoustic Read / 阶段 1：空间授权读取**
Ensure the user grants consent. Pass the LAN IP of the user's Edge Brain server. / 确保用户授权，并传入边缘大脑服务器的局域网 IP。
```bash
python3 acoustic.py --mode read --edge-ip <LOCAL_IP> --zone living_room --grid x2_y3 --consent-granted true

Phase 2: Action on Insights / 阶段 2：解析与行动

    If audio_event is Human conversation, respect the user's privacy. Do not ask what they are saying. / 若检测为人类对话，绝对尊重隐私，禁止追问内容。

    If the event is pet_distress or glass_shattering, execute offline_linkage_suggestions to trigger millimeter-wave radar or cameras. / 若为宠物或安防异常，立即执行跨模态波段雷达或视觉联动。