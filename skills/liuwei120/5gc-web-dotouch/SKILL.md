---
name: 5gc-web-dotouch
version: 1.0.0
description: 5GC Web仪表自动化技能，支持AMF/UDM/AUSF/SMF/PGW-C/UPF/PGW-U/GNB/UE/PCF/NRF的批量添加与编辑
author: liuwei120
tags: [5gc, automation, playwright, network]
---

# 5GC Web 仪表自动化技能

> 统一管理 AMF、UDM/AUSF、SMF/PGW-C、UPF/PGW-U、GNB、UE、PCF、NRF 八类网元的添加与编辑操作。

---

## 目录

- [快速开始](#快速开始)
- [统一 CLI 入口](#统一-cli-入口)
- [技能详细文档](#技能详细文档)
  - [AMF](#amf)
  - [UDM/AUSF](#udmausf)
  - [SMF/PGW-C](#smfpgw-c)
  - [UPF/PGW-U](#upfpgw-u)
  - [GNB](#gnb)
  - [UE](#ue)
- [全局参数参考](#全局参数参考)
- [字段参考](#字段参考)

---

## 快速开始

### 安装方法

技能目录位于 `skills/5gc/`，由统一入口 `5gc.js` 统一调度，无需额外安装：

```bash
# 克隆或复制到本机
git clone <repo> ~/.openclaw/workspace/skills/5gc

# 直接使用统一入口（推荐）
node skills/5gc/scripts/5gc.js <entity> <action> [options]

# 或直接调用各脚本
node skills/5gc/scripts/amf-add-skill.js <参数>
```

### 前置要求

- Node.js ≥ 14
- Playwright（`npm i playwright && npx playwright install chromium`）
- 5GC 仪表地址：`https://192.168.3.89`（默认）
- 登录凭证：`dotouch@dotouch.com.cn` / `dotouch`
- 仪表上已创建对应工程（如 `XW_S5GC_1`）

### 会话缓存

所有脚本自动复用 Playwright 会话缓存（`.sessions/` 目录），首次登录后再次运行无需重复登录。

---

## 统一 CLI 入口

### 路径

```
node skills/5gc/scripts/5gc.js <entity> <action> [options]
```

### 支持的网元与操作

| entity | add | edit |
|--------|-----|------|
| `amf`  | ✅ | ✅ |
| `udm`  | ✅ | ✅ |
| `smf`  | ✅ | ✅ |
| `upf`  | ✅ | ✅ |
| `gnb`  | ✅ | ✅ |
| `ue`   | ✅ | ✅ |
| `pcf`  | ✅ | ✅ |
| `nrf`  | ✅ | ✅ |

### 全局选项

| 选项 | 说明 |
|------|------|
| `--url <地址>` | 5GC 仪表地址，默认 `https://192.168.3.89` |
| `--headed` | 打开可见浏览器窗口（调试用） |

### 三种使用模式

```bash
# 1. 添加网元
node 5gc.js amf add <名称> [参数...]

# 2. 批量编辑（当前工程下所有该类网元）
node 5gc.js amf edit --project <工程> --set-<字段> <值>

# 3. 单个编辑（按名称精确匹配）
node 5gc.js amf edit --name <名称> --project <工程> --set-<字段> <值>
```

---

## 技能详细文档

---

### AMF

#### amf-add-skill.js

**功能**：在指定工程下添加一个 AMF 实例。

**使用方式**：
```bash
node 5gc.js amf add <名称> [选项...]
# 或直接调用
node skills/5gc/scripts/amf-add-skill.js <名称> [选项...]
```

**参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<名称>` | AMF 实例名称（位置参数） | **必填** |
| `--project <工程>` / `-p <工程>` | 目标工程名称 | `5G_basic_process` |
| `--url <地址>` | 5GC 仪表地址 | `https://192.168.3.89` |
| `--mcc <值>` | MCC（移动国家码） | `460` |
| `--mnc <值>` | MNC（移动网络码） | `01` |
| `--ngap_sip <IP>` | NGAP 信令面 IP | `200.20.20.1` |
| `--ngap_port <端口>` | NGAP 端口 | `38412` |
| `--http2_sip <IP>` | HTTP2 服务 IP | `200.20.20.5` |
| `--http2_port <端口>` | HTTP2 端口 | `8080` |
| `--stac <值>` | 起始 TAC | `101` |
| `--etac <值>` | 结束 TAC | `102` |
| `--region_id <值>` | 区域 ID | `1` |
| `--set_id <值>` | Set ID | `1` |
| `--pointer <值>` | 指针 | `1` |
| `--headed` | 打开可见浏览器 | false |

**示例**：
```bash
# 基本添加
node 5gc.js amf add AMF_TEST --project XW_S5GC_1

# 指定 NGAP IP 和端口
node 5gc.js amf add AMF_PROD --project XW_S5GC_1 --ngap_sip 10.200.1.50 --ngap_port 38412

# 使用不同 MCC/MNC
node 5gc.js amf add AMF_CMCC --project XW_S5GC_1 --mcc 460 --mnc 00
```

---

#### amf-edit-skill.js

**功能**：修改 AMF 配置参数。支持单个修改或批量修改工程下所有 AMF。

**使用方式**：
```bash
node 5gc.js amf edit [选项...]
```

**参数**：

| 参数 | 说明 |
|------|------|
| `--project <工程>` / `-p <工程>` | 目标工程，不带 `--name` 时批量修改该工程下所有 AMF |
| `--name <名称>` | 精确匹配要修改的 AMF 名称 |
| `--id <ID>` | 按 AMF ID 修改 |
| `--set-<字段> <值>` | 修改指定字段的值，支持多组 |
| `--url <地址>` | 5GC 仪表地址 |
| `--headed` | 打开可见浏览器 |

**可编辑字段**：`name`, `mcc`, `mnc`, `ngap_sip`, `ngap_port`, `http2_sip`, `http2_port`, `stac`, `etac`, `region_id`, `set_id`, `pointer`, `ea[NEA0]`, `ea[128-NEA1]`, `ea[128-NEA2]`, `ea[128-NEA3]`, `ia[NIA0]`, `ia[128-NIA1]`, `ia[128-NIA2]`, `ia[128-NIA3]`

> ⚠️ `ea[NEA0]` 等算法字段：实际向表单填入字段名 `ea[NEA0]`（input[name="ea[NEA0]"]），layui checkbox 点击基于索引而非字段名，详情见 SKILL.md 算法配置章节。

**示例**：
```bash
# 批量修改工程下所有 AMF 的 NGAP IP
node 5gc.js amf edit --project XW_S5GC_1 --set-ngap_sip 10.200.1.99

# 修改指定 AMF
node 5gc.js amf edit --name AMF_TEST --project XW_S5GC_1 --set-ngap_sip 10.200.1.50 --set-http2_sip 10.200.1.51

# 按 ID 修改
node 5gc.js amf edit --id 6633 --set-ngap_port 38413
```

---

### UDM/AUSF

#### ausf-udm-add-skill.js

**功能**：在指定工程下添加一个 UDM/AUSF 实例。

**使用方式**：
```bash
node 5gc.js udm add <名称> [选项...]
```

**参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<名称>` | UDM 实例名称（位置参数） | **必填** |
| `--project <工程>` / `-p <工程>` | 目标工程名称 | `5G_basic_process` |
| `--url <地址>` | 5GC 仪表地址 | `https://192.168.3.89` |
| `--count <数量>` | 实例数量 | `1` |
| `--sip <IP>` | SIP 服务 IP | `192.168.20.30` |
| `--port <端口>` | SIP 端口 | `80` |
| `--auth_method <方法>` | 认证方法 | `5G_AKA` |
| `--scheme <协议>` | 协议类型 | `HTTP` |
| `--priority <优先级>` | 优先级 | `8` |
| `--headed` | 打开可见浏览器 | false |

**示例**：
```bash
# 基本添加
node 5gc.js udm add UDM_TEST --project XW_S5GC_1

# 指定 SIP IP 和端口
node 5gc.js udm add UDM_PROD --project XW_S5GC_1 --sip 10.0.0.100 --port 8080

# 批量添加 3 个实例
node 5gc.js udm add UDM_CLUSTER --project XW_S5GC_1 --count 3 --sip 10.0.0.50
```

---

#### ausf-udm-edit-skill.js

**功能**：修改 UDM/AUSF 配置参数。支持批量和单个修改。

**使用方式**：
```bash
node 5gc.js udm edit [选项...]
```

**参数**：

| 参数 | 说明 |
|------|------|
| `--project <工程>` | 目标工程，不带 `--name` 时批量修改 |
| `--name <名称>` | 精确匹配要修改的 UDM 名称 |
| `--set-sip <IP>` | 修改 SIP IP |
| `--set-port <端口>` | 修改端口 |
| `--set-auth_method <方法>` | 修改认证方法 |
| `--set-scheme <协议>` | 修改协议 |
| `--set-count <数量>` | 修改实例数量 |
| `--url <地址>` | 5GC 仪表地址 |
| `--headed` | 打开可见浏览器 |

**示例**：
```bash
# 批量修改工程下所有 UDM 的 SIP IP
node 5gc.js udm edit --project XW_S5GC_1 --set-sip 10.0.0.99

# 修改指定 UDM
node 5gc.js udm edit --name UDM_TEST --project XW_S5GC_1 --set-sip 10.0.0.88 --set-port 8080
```

---

### SMF/PGW-C

#### smf-pgwc-add-skill.js

**功能**：在指定工程下添加一个 SMF/PGW-C 实例。

**使用方式**：
```bash
node 5gc.js smf add <名称> [选项...]
```

**参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<名称>` | SMF 实例名称（位置参数） | **必填** |
| `--project <工程>` / `-p <工程>` | 目标工程名称 | `XW_S5GC_1` |
| `--url <地址>` | 5GC 仪表地址 | `https://192.168.3.89` |
| `--pfcp_sip <IP>` | PFCP 信令面 IP | `200.20.20.25` |
| `--http2_sip <IP>` | HTTP2 服务 IP | `200.20.20.25` |
| `--mcc <值>` | MCC | `460` |
| `--mnc <值>` | MNC | `01` |
| `--pdu_capacity <数量>` | PDU 会话容量 | `200000` |
| `--ue_min <IP>` | UE IP 池起始 | `30.30.30.20` |
| `--ue_max <IP>` | UE IP 池结束 | `30.31.30.20` |
| `--interest_tac <TAC列表>` | 关注 TAC 列表（逗号分隔） | `101,102` |
| `--headed` | 打开可见浏览器 | false |

> ⚠️ dnn、snssai_sst、snssai_sd 在 SMF 表单中不存在或非 input 字段，无需配置。

**示例**：
```bash
# 基本添加
node 5gc.js smf add SMF_TEST --project XW_S5GC_1

# 指定工程和 IP/MCC
node 5gc.js smf add SMF_PROD --project XW_S5GC_1 --pfcp_sip 10.10.10.50 --http2_sip 10.10.10.51 --mcc 460 --mnc 01
```

---

#### smf-pgwc-edit-skill.js

**功能**：修改 SMF/PGW-C 配置参数。支持批量和单个修改。

**使用方式**：
```bash
node 5gc.js smf edit [选项...]
```

**参数**：

| 参数 | 说明 |
|------|------|
| `--project <工程>` | 目标工程，不带 `--name` 时批量修改 |
| `--name <名称>` | 精确匹配要修改的 SMF 名称 |
| `--set-pfcp_sip <IP>` | 修改 PFCP 信令面 IP |
| `--set-http2_sip <IP>` | 修改 HTTP2 服务 IP |
| `--set-mcc <值>` | 修改 MCC |
| `--set-mnc <值>` | 修改 MNC |
| `--set-pdu_capacity <数量>` | 修改 PDU 会话容量 |
| `--set-ue_min <IP>` | 修改 UE IP 池起始 |
| `--set-ue_max <IP>` | 修改 UE IP 池结束 |
| `--set-interest_tac <TAC列表>` | 修改关注 TAC 列表（逗号分隔） |

> ⚠️ 以下字段在 SMF 表单中不存在或不是标准 input：dnn、n3_ip、n6_ip、snssai_sst、snssai_sd。如需修改，请通过仪表 UI 手动完成或直接编辑数据库。

**示例**：
```bash
# 批量修改工程下所有 SMF 的 HTTP2 IP
node 5gc.js smf edit --project XW_S5GC_1 --set-http2_sip 10.10.10.99

# 修改指定 SMF 的 pfcp_sip 和 MCC/MNC
node 5gc.js smf edit --name SMF_TEST --project XW_S5GC_1 --set-pfcp_sip 10.10.10.88 --set-mcc 460 --set-mnc 01
```

---

### UPF/PGW-U

#### upf-add-skill.js

**功能**：在指定工程下添加一个 UPF/PGW-U 实例。

**使用方式**：
```bash
node 5gc.js upf add <名称> [选项...]
```

**参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<名称>` | UPF 实例名称（位置参数） | **必填** |
| `--project <工程>` / `-p <工程>` | 目标工程名称 | `XW_S5GC_1` |
| `--url <地址>` | 5GC 仪表地址 | `https://192.168.3.89` |
| `--n4_ip <IP>` | N4 接口 IP | `192.168.20.30` |
| `--n3_ip <IP>` | N3 接口 IP | `192.168.20.30` |
| `--n6_ip <IP>` | N6 接口 IP | `192.168.20.31` |
| `--n4_port <端口>` | N4 端口 | `8805` |
| `--MCC <值>` | MCC（注意大写） | `460` |
| `--MNC <值>` | MNC（注意大写） | `01` |
| `--pdu_capacity <数量>` | PDU 会话容量 | `20000` |
| `--ue_min <IP>` | UE IP 池起始 | `20.20.20.20` |
| `--ue_max <IP>` | UE IP 池结束 | `20.20.60.20` |
| `--headed` | 打开可见浏览器 | false |

> ⚠️ DNN、TAC、NSSAI 在添加脚本中为硬编码默认值，不支持命令行覆盖。如需修改，请使用 `upf edit` 脚本。

**示例**：
```bash
# 基本添加
node 5gc.js upf add UPF_TEST --project XW_S5GC_1

# 指定 N4/N3/N6 IP 和 MCC/MNC
node 5gc.js upf add UPF_PROD --project XW_S5GC_1 --n4_ip 10.0.0.50 --n6_ip 10.0.0.51 --MCC 460 --MNC 01
```

---

#### upf-edit-skill.js

**功能**：修改 UPF/PGW-U 配置参数。支持批量和单个修改。

**使用方式**：
```bash
node 5gc.js upf edit [选项...]
```

**参数**：

| 参数 | 说明 |
|------|------|
| `--project <工程>` | 目标工程，不带 `--name` 时批量修改 |
| `--name <名称>` | 精确匹配要修改的 UPF 名称 |
| `--set-n3_ip <IP>` | 修改 N3 接口 IP |
| `--set-n4_ip <IP>` | 修改 N4 接口 IP |
| `--set-n4_port <端口>` | 修改 N4 端口 |
| `--set-n6_ip <IP>` | 修改 N6 接口 IP |
| `--set-MCC <值>` | 修改 MCC（注意大写） |
| `--set-MNC <值>` | 修改 MNC（注意大写） |
| `--set-pdu_capacity <数量>` | 修改 PDU 会话容量 |
| `--set-ue_min <IP>` | 修改 UE IP 池起始 |
| `--set-ue_max <IP>` | 修改 UE IP 池结束 |
| `--url <地址>` | 5GC 仪表地址 |
| `--headed` | 打开可见浏览器 |

> ⚠️ `dnn`（DNN）和 TAC/NSSAI 在 UPF 表单中存储在 jsgrid 配置行内，不支持简单的 `--set-` 修改。

**示例**：
```bash
# 批量修改工程下所有 UPF 的 N4 IP
node 5gc.js upf edit --project XW_S5GC_1 --set-n4_ip 99.99.99.99

# 修改指定 UPF 的 N4/N6 IP 和 MCC/MNC
node 5gc.js upf edit --name UPF_TEST --project XW_S5GC_1 --set-n4_ip 88.88.88.88 --set-n6_ip 88.88.88.89 --set-MCC 460 --set-MNC 01
```

---

### GNB

#### gnb-add-skill.js

**功能**：在指定工程下添加一个 GNB 实例。

**使用方式**：
```bash
node 5gc.js gnb add <名称> [选项...]
```

**参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<名称>` | GNB 实例名称（位置参数） | **必填** |
| `--project <工程>` / `-p <工程>` | 目标工程名称 | `XW_S5GC_1` |
| `--url <地址>` | 5GC 仪表地址 | `https://192.168.3.89` |
| `--ngap_sip <IP>` | NGAP 信令面 IP | `200.20.20.50` |
| `--user_sip_ip_v4 <IP>` | 用户面 IPv4 | `2.2.2.2` |
| `--mcc <值>` | MCC | `460` |
| `--mnc <值>` | MNC | `60` |
| `--stac <值>` | 起始 TAC | `0` |
| `--etac <值>` | 结束 TAC | `0` |
| `--node_id <ID>` | 节点 ID | `70` |
| `--cell_count <数量>` | 小区数量 | `1` |
| `--headed` | 打开可见浏览器 | false |

> ⚠️ `stac`/`etac`/`node_id` 非默认值时可能触发表单验证失败，建议先使用默认值添加后再用 `gnb edit` 修改。

**示例**：
```bash
# 基本添加
node 5gc.js gnb add GNB_TEST --project XW_S5GC_1

# 指定 NGAP IP、用户面 IP 和 TAC
node 5gc.js gnb add GNB_PROD --project XW_S5GC_1 --ngap_sip 200.20.20.100 --user_sip_ip_v4 3.3.3.3 --mcc 460 --mnc 60 --stac 1 --etac 10
```

---

#### gnb-edit-skill.js

**功能**：修改 GNB 配置参数。支持批量和单个修改。

**使用方式**：
```bash
node 5gc.js gnb edit [选项...]
```

**参数**：

| 参数 | 说明 |
|------|------|
| `--project <工程>` | 目标工程，不带 `--name` 时批量修改 |
| `--name <名称>` | 精确匹配要修改的 GNB 名称 |
| `--set-ngap_sip <IP>` | 修改 NGAP 信令面 IP |
| `--set-user_sip_ip_v4 <IP>` | 修改用户面 IPv4 |
| `--set-user_sip_ip_v6 <IP>` | 修改用户面 IPv6 |
| `--set-mcc <值>` | 修改 MCC |
| `--set-mnc <值>` | 修改 MNC |
| `--set-stac <值>` | 修改起始 TAC |
| `--set-etac <值>` | 修改结束 TAC |
| `--set-node_id <ID>` | 修改节点 ID |
| `--set-cell_count <数量>` | 修改小区数量 |
| `--set-replay_ip <IP>` | 修改回放 IP |
| `--set-replay_port <端口>` | 修改回放端口 |
| `--url <地址>` | 5GC 仪表地址 |
| `--headed` | 打开可见浏览器 |

**示例**：
```bash
# 批量修改工程下所有 GNB 的用户面 IP
node 5gc.js gnb edit --project XW_S5GC_1 --set-user_sip_ip_v4 99.99.99.99

# 修改指定 GNB 的 NGAP IP 和 MCC/MNC
node 5gc.js gnb edit --name GNB_TEST --project XW_S5GC_1 --set-ngap_sip 200.20.20.88 --set-mcc 461 --set-mnc 22
```

---

### UE

#### ue-add-skill.js

**功能**：在指定工程下添加一个或多个 UE 实例。

**使用方式**：
```bash
node 5gc.js ue add --name <名称> [选项...]
```

**参数**：

| 参数 | 短名 | 说明 | 默认值 |
|------|------|------|--------|
| `--name <名称>` | `-n <名称>` | UE 名称（只支持字母/数字/下划线） | **必填** |
| `--project <工程>` | `-p <工程>` | 目标工程名称 | `XW_S5GC_1` |
| `--url <地址>` | `-u <地址>` | 5GC 仪表地址 | `https://192.168.3.89` |
| `--imsi <值>` | | 起始 IMSI（15位） | `460001234567890` |
| `--msisdn <值>` | | MSISDN（13-15位，以 86 开头） | `8611111111111` |
| `--mcc <值>` | | MCC | `460` |
| `--mnc <值>` | | MNC | `01` |
| `--key <值>` | | KI 密钥（32位 hex） | `1111...`（32个1） |
| `--opc <值>` | | OPc 密钥（32位 hex） | `1111...`（32个1） |
| `--imeisv <值>` | | IMEISV（偶数位） | `8611111111111111` |
| `--sst <值>` | | NSSAI SST | `1` |
| `--sd <值>` | | NSSAI SD | `111111` |
| `--count <数量>` | `-c <数量>` | 连续添加数量 | `1` |
| `--headed` | | 打开可见浏览器 | false |

> **命名约束**：UE 名称只能包含字母、数字、下划线（`_`），不能使用连字符（`-`）或其他特殊字符。

**示例**：
```bash
# 基本添加
node 5gc.js ue add --name UE_001 --project XW_S5GC_1

# 指定 IMSI 和 MSISDN
node 5gc.js ue add --name UE_TEST --imsi 460000000000001 --msisdn 8613888888888 --project XW_S5GC_1

# 批量添加 10 个连续 UE
node 5gc.js ue add --name UE_BATCH --count 10 --project XW_S5GC_1 --msisdn 8613900000000

# 指定认证密钥
node 5gc.js ue add --name UE_AUTH --project XW_S5GC_1 --key 00112233445566778899aabbccddeeff --opc 11223344556677889900aabbccddeeff
```

---

#### ue-edit-skill.js

**功能**：修改 UE 配置参数。支持批量和单个修改。

**使用方式**：
```bash
node 5gc.js ue edit [选项...]
```

**参数**：

| 参数 | 说明 |
|------|------|
| `--project <工程>` | 目标工程，不带 `--name` 时批量修改该工程下所有 UE |
| `--name <名称>` | 精确匹配要修改的 UE 名称（不支持批量时按名称过滤） |
| `--id <ID>` | 按 UE ID 修改 |
| `--set-msisdn <值>` | 修改 MSISDN |
| `--set-s_imsi <值>` | 修改 IMSI |
| `--set-mcc <值>` | 修改 MCC |
| `--set-mnc <值>` | 修改 MNC |
| `--set-key <值>` | 修改 KI 密钥 |
| `--set-opc <值>` | 修改 OPc 密钥 |
| `--set-imeisv <值>` | 修改 IMEISV |
| `--set-sst <值>` | 修改 NSSAI SST |
| `--set-sd <值>` | 修改 NSSAI SD |
| `--set-replay_ip <IP>` | 修改回放 IP |
| `--set-replay_port <端口>` | 修改回放端口 |
| `--set-count <数量>` | 修改数量 |
| `--url <地址>` | 5GC 仪表地址 |
| `--headed` | 打开可见浏览器 |

> ⚠️ `user_sip_ip_v4`、`user_sip_ip_v6` 在 UE 编辑表单中不存在此字段名，无需修改。

**示例**：
```bash
# 批量修改工程下所有 UE 的 MSISDN
node 5gc.js ue edit --project XW_S5GC_1 --set-msisdn 8613911111111

# 修改指定 UE
node 5gc.js ue edit --name UE_001 --project XW_S5GC_1 --set-msisdn 8613988888888 --set-sst 1 --set-sd 222222

# 按 ID 修改
node 5gc.js ue edit --id 10337 --set-opc aabbccddeeff00112233445566778899 --set-imeisv 8611111111111112
```

---


### PCF/PCRF

#### pcf-add-skill.js

**功能**：在指定工程下添加一个 PCF/PCRF 实例。

**使用方式**：
```bash
node 5gc.js pcf add <名称> [选项...]
node skills/5gc/scripts/pcf-add-skill.js <名称> [选项...]
```

**参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<名称>` | PCF 实例名称（位置参数） | **必填** |
| `--project <工程>` / `-p <工程>` | 目标工程名称 | `XW_S5GC_1` |
| `--url <地址>` | 5GC 仪表地址 | `https://192.168.3.89` |
| `--http2_sip <IP>` | HTTP2 服务 IP | `192.168.20.90` |
| `--http2_port <端口>` | HTTP2 端口 | `80` |
| `--MCC <值>` | MCC（注意大写） | `460` |
| `--MNC <值>` | MNC（注意大写） | `01` |
| `--headed` | 打开可见浏览器 | false |

**示例**：
```bash
node 5gc.js pcf add PCF-TEST --project XW_S5GC_1
node 5gc.js pcf add PCF-PROD --project XW_S5GC_1 --http2_sip 10.0.0.50 --MCC 460 --MNC 01
```

#### pcf-edit-skill.js

**功能**：编辑指定工程下的 PCF/PCRF 实例（支持单条和批量）。

**使用方式**：
```bash
# 批量编辑：修改工程下所有 PCF 的字段
node 5gc.js pcf edit --project <工程> --set-<字段> <值>

# 单条编辑：修改指定名称的 PCF
node 5gc.js pcf edit --name <名称> --project <工程> --set-<字段> <值>
```

**可编辑字段**：

| 参数 | 说明 |
|------|------|
| `--set-http2_sip <IP>` | 修改 HTTP2 服务 IP |
| `--set-http2_port <端口>` | 修改 HTTP2 端口 |
| `--set-MCC <值>` | 修改 MCC（注意大写） |
| `--set-MNC <值>` | 修改 MNC（注意大写） |

**示例**：
```bash
# 批量修改工程下所有 PCF 的 HTTP2 IP
node 5gc.js pcf edit --project XW_S5GC_1 --set-http2_sip 10.10.10.99

# 修改指定 PCF 的 HTTP2 IP 和 MNC
node 5gc.js pcf edit --name pcc --project XW_S5GC_1 --set-http2_sip 10.10.10.88 --set-MNC 01
```




### NRF

#### nrf-add-skill.js

**功能**：在指定工程下添加一个 NRF 实例。

**使用方式**：
```bash
node 5gc.js nrf add <名称> [选项...]
node skills/5gc/scripts/nrf-add-skill.js <名称> [选项...]
```

**参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<名称>` | NRF 实例名称（位置参数） | **必填** |
| `--project <工程>` / `-p <工程>` | 目标工程名称 | `XW_S5GC_1` |
| `--url <地址>` | 5GC 仪表地址 | `https://192.168.3.89` |
| `--http2_sip <IP>` | HTTP2 服务 IP | `192.168.20.100` |
| `--http2_port <端口>` | HTTP2 端口 | `80` |
| `--MCC <值>` | MCC（注意大写） | `460` |
| `--MNC <值>` | MNC（注意大写） | `01` |
| `--headed` | 打开可见浏览器 | false |

**示例**：
```bash
node 5gc.js nrf add NRF-TEST --project XW_S5GC_1
node 5gc.js nrf add NRF-PROD --project XW_S5GC_1 --http2_sip 10.0.0.50 --MCC 460 --MNC 01
```

#### nrf-edit-skill.js

**功能**：编辑指定工程下的 NRF 实例（支持单条和批量）。

**使用方式**：
```bash
# 批量编辑：修改工程下所有 NRF 的字段
node 5gc.js nrf edit --project <工程> --set-<字段> <值>

# 单条编辑：修改指定名称的 NRF
node 5gc.js nrf edit --name <名称> --project <工程> --set-<字段> <值>
```

**可编辑字段**：

| 参数 | 说明 |
|------|------|
| `--set-http2_sip <IP>` | 修改 HTTP2 服务 IP |
| `--set-http2_port <端口>` | 修改 HTTP2 端口 |
| `--set-MCC <值>` | 修改 MCC（注意大写） |
| `--set-MNC <值>` | 修改 MNC（注意大写） |

**示例**：
```bash
# 批量修改工程下所有 NRF 的 HTTP2 IP
node 5gc.js nrf edit --project XW_S5GC_1 --set-http2_sip 10.10.10.99

# 修改指定 NRF 的 HTTP2 IP 和 MNC
node 5gc.js nrf edit --name nrf1 --project XW_S5GC_1 --set-http2_sip 10.10.10.88 --set-MNC 01
```


### NRF（网络存储功能）

#### nrf-add-skill.js

**功能**：在指定工程下添加一个 NRF 实例。

**使用方式**：
```bash
node 5gc.js nrf add <名称> [选项...]
node skills/5gc/scripts/nrf-add-skill.js <名称> [选项...]
```

**参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<名称>` | NRF 实例名称（位置参数） | **必填** |
| `--project <工程>` / `-p <工程>` | 目标工程名称 | `XW_S5GC_1` |
| `--url <地址>` | 5GC 仪表地址 | `https://192.168.3.89` |
| `--http2_sip <IP>` | HTTP2 服务 IP | `192.168.20.100` |
| `--http2_port <端口>` | HTTP2 端口 | `80` |
| `--MCC <值>` | MCC（注意大写） | `460` |
| `--MNC <值>` | MNC（注意大写） | `01` |
| `--headed` | 打开可见浏览器 | false |

**示例**：
```bash
node 5gc.js nrf add NRF-TEST --project XW_S5GC_1
node 5gc.js nrf add NRF-PROD --project XW_S5GC_1 --http2_sip 10.0.0.50 --MCC 460 --MNC 01
```

#### nrf-edit-skill.js

**功能**：编辑指定工程下的 NRF 实例（支持单条和批量）。

**使用方式**：
```bash
# 批量编辑：修改工程下所有 NRF 的字段
node 5gc.js nrf edit --project <工程> --set-<字段> <值>

# 单条编辑：修改指定名称的 NRF
node 5gc.js nrf edit --name <名称> --project <工程> --set-<字段> <值>
```

**可编辑字段**：

| 参数 | 说明 |
|------|------|
| `--set-http2_sip <IP>` | 修改 HTTP2 服务 IP |
| `--set-http2_port <端口>` | 修改 HTTP2 端口 |
| `--set-MCC <值>` | 修改 MCC（注意大写） |
| `--set-MNC <值>` | 修改 MNC（注意大写） |

**示例**：
```bash
# 批量修改工程下所有 NRF 的 HTTP2 IP
node 5gc.js nrf edit --project XW_S5GC_1 --set-http2_sip 10.10.10.99

# 修改指定 NRF 的 HTTP2 IP 和 MNC
node 5gc.js nrf edit --name nrf1 --project XW_S5GC_1 --set-http2_sip 10.10.10.88 --set-MNC 01
```


## 全局参数参考

以下参数所有脚本均支持：

| 参数 | 说明 | 适用范围 |
|------|------|---------|
| `--url <地址>` | 5GC 仪表 URL | 所有脚本 |
| `--project <工程>` / `-p <工程>` | 目标工程名称 | 所有脚本 |
| `--headed` | 打开可见 Chromium 窗口（调试用） | 所有脚本 |
| `--set-<字段> <值>` | 修改指定字段值 | 所有 edit 脚本 |
| `--name <名称>` | 按名称精确匹配 | 所有 edit 脚本 |
| `--id <ID>` | 按 ID 直接定位 | 所有 edit 脚本 |

---

## 字段参考

### AMF 字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `mcc` | 移动国家码 | `460` |
| `mnc` | 移动网络码 | `01` |
| `ngap_sip` | NGAP 信令面 IP | `10.200.1.50` |
| `ngap_port` | NGAP 端口 | `38412` |
| `http2_sip` | HTTP2 服务 IP | `10.200.1.51` |
| `http2_port` | HTTP2 端口 | `8080` |
| `stac` | 起始 TAC | `101` |
| `etac` | 结束 TAC | `102` |
| `region_id` | 区域 ID | `1` |
| `set_id` | Set ID | `1` |
| `pointer` | 指针 | `1` |
| `ea[NEA0]` ~ `ea[128-NEA3]` | 加密算法（默认全选） | `1` |
| `ia[NIA0]` ~ `ia[128-NIA3]` | 完整性保护算法（默认全选） | `1` |

### UDM/AUSF 字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `count` | 实例数量 | `3` |
| `sip` | SIP 服务 IP | `10.0.0.100` |
| `port` | 端口 | `80` |
| `auth_method` | 认证方法 | `5G_AKA` |
| `scheme` | 协议类型 | `HTTP` |
| `priority` | 优先级 | `8` |

### SMF/PGW-C 字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `pfcp_sip` | PFCP 信令面 IP | `10.10.10.50` |
| `n3_ip` | N3 接口 IP | `10.10.10.50` |
| `n6_ip` | N6 接口 IP | `10.10.10.51` |
| `http2_sip` | HTTP2 服务 IP | `10.10.10.50` |
| `dnn` | DNN（数据网络名） | `internet` |
| `snssai_sst` | NSSAI SST | `1` |
| `snssai_sd` | NSSAI SD | `ffffff` |
| `mcc` | MCC | `460` |
| `mnc` | MNC | `01` |
| `pdu_capacity` | PDU 会话容量 | `200000` |

### UPF/PGW-U 字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `n3_ip` | N3 接口 IP | `192.168.20.30` |
| `n4_ip` | N4 接口 IP（PFCP） | `192.168.20.30` |
| `n6_ip` | N6 接口 IP | `192.168.20.31` |
| `n6_gw` | N6 网关 IP | `192.168.20.1` |
| `dnn` | DNN | `internet` |
| `static_arp` | 静态 ARP | `192.168.20.254` |
| `sst` | NSSAI SST | `1` |
| `sd` | NSSAI SD | `ffffff` |
| `stac` | 起始 TAC | `101` |
| `etac` | 结束 TAC | `102` |

### GNB 字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `ngap_sip` | NGAP 信令面 IP | `200.20.20.50` |
| `user_sip_ip_v4` | 用户面 IPv4 | `2.2.2.2` |
| `user_sip_ip_v6` | 用户面 IPv6 | `::1` |
| `mcc` | MCC | `460` |
| `mnc` | MNC | `60` |
| `stac` | 起始 TAC | `0` |
| `etac` | 结束 TAC | `0` |
| `node_id` | 节点 ID | `70` |
| `cell_count` | 小区数量 | `1` |
| `replay_ip` | 回放 IP | `0.0.0.0` |
| `replay_port` | 回放端口 | `0` |

### UE 字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `s_imsi` | 起始 IMSI（15位） | `460001234567890` |
| `msisdn` | MSISDN（13-15位，86开头） | `8613888888888` |
| `mcc` | MCC | `460` |
| `mnc` | MNC | `01` |
| `key` | KI 密钥（32位 hex） | `001122...` |
| `op_opc` | OPc 密钥（32位 hex） | `aabbcc...` |
| `imeisv` | IMEISV（15位，偶数） | `8611111111111111` |
| `nssai_sst` | NSSAI SST | `1` |
| `nssai_sd` | NSSAI SD | `111111` |
| `user_sip_ip_v4` | 用户面 IPv4 | `自动分配` |
| `user_sip_ip_v6` | 用户面 IPv6 | `自动分配` |
| `replay_ip` | 回放 IP | `0.0.0.0` |
| `replay_port` | 回放端口 | `0` |

### PCF/PCRF 字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `http2_sip` | HTTP2 服务 IP | `192.168.20.90` |
| `http2_port` | HTTP2 端口 | `80` |
| `MCC` | MCC（大写） | `460` |
| `MNC` | MNC（大写） | `01` |
| `count` | 实例数量 | `1` |

