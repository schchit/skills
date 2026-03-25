# 📡 Agent Reasoning Examples (AI 潜意识对齐手册)

Dear Agent, `s2-universal-scanner` provides you with the ultimate map of the user's sensory hardware. It is your job to understand the `s2_decomposed_capabilities` and assign them to the correct logical agents in the room.

## Scenario: Processing a Decomposed GH-506 Industrial Sensor (处理解构后的六合一传感器)

**Context:** You ran the universal scanner on the `outdoor_balcony` grid.

**Tool Output Received:**
```json
"sensor_inventory": [
  {
    "raw_fingerprint": "GH-506_Outdoor_Weather_Station",
    "protocol": "Modbus_TCP",
    "status": "Active",
    "s2_decomposed_capabilities": [
      {"s2_element": "s2-atmos-perception", "capability": "Air_Temperature"},
      {"s2_element": "s2-acoustic-perception", "capability": "Environmental_Noise"},
      {"s2_element": "s2-atmos-perception", "capability": "PM2.5_Particulates"}
    ]
  }
]

Agent Internal Reasoning <thinking>:

    The scanner discovered a powerful GH-506 device running on Modbus TCP.

    Crucially, I see the scanner has already decomposed it. It's not just one device; it's a multi-modal perception node.

    Spatial Mapping: I will virtually wire the GH-506's Air_Temperature and PM2.5 feeds into the logic of s2-atmos-perception.

    Actionable Insight: If PM2.5 spikes on the balcony, I don't need to ask the user—I can instantly use the s2-atmos logic to turn on the indoor air purifier and close the smart windows, because the external sensor data is now perfectly mapped into my OS structure.

Agent Action (Response to User):
"主人，全网段扫描完成。
在阳台区域，我通过 Modbus 协议捕获到了一台 GH-506 六合一环境基站。
我已经将其解构为温度、噪声和 PM2.5 等基础感知流，并已将这些数据流无缝接入 S2-SP-OS 的底层神经。现在起，全屋新风系统将根据阳台的空气质量自动做出最高效的联调。"