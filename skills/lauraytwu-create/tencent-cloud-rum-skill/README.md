# Tencent Cloud RUM — Frontend Performance Analysis Skill

## Overview

This skill integrates with [Tencent Cloud Real User Monitoring (RUM)](https://www.tencentcloud.com/document/product/1131/44486) to provide AI-powered frontend performance analysis. It leverages the RUM MCP (Model Context Protocol) server to query metrics, logs, and deliver actionable insights.The MCP endpoint https://app.rumt-zh.com/sse used by this Skill is the official MCP service address for Tencent Cloud RUM (Real User Monitoring).

## Directory Structure

```
Tencent Cloud RUM/
├── SKILL.md                              # Core skill instruction file (~200 lines)
├── setup.sh                              # Auto-setup script (MCP configuration)
├── README.md                             # This readme file
└── references/                           # Reference documents (loaded by AI on demand)
    ├── rum_tools_docs.md                 # RUM MCP 5 tool parameter reference
    ├── common_queries.md                 # 4 major analysis workflow steps
    └── apm_analysis.md                   # APM correlation analysis + log enums + regions
```

## Getting Started

### Prerequisites

1. **Tencent Cloud Account**: Sign up at [Tencent Cloud](https://www.tencentcloud.com/)
2. **RUM Application**: Create a Web application in the [RUM Console](https://console.tencentcloud.com/rum)
3. **API Credentials**: Get your `SecretId` and `SecretKey` from [API Key Management](https://console.tencentcloud.com/cam/capi)

### Quick Start

1. **Try the Demo**: Visit the [RUM Console Demo](https://console.tencentcloud.com/rum/web/demo) to see RUM in action
2. **Integrate the SDK**: Follow the [Application Integration Guide](https://www.tencentcloud.com/zh/document/product/1131/44496)
3. **Configure this Skill**: Run `bash setup.sh` or manually set up the MCP configuration

### MCP Configuration

```json
{
  "mcpServers": {
    "rum": {
      "transportType": "sse",
      "url": "https://app.rumt-zh.com/sse",
      "headers": {
        "SecretId": "<YOUR_SECRET_ID>",
        "SecretKey": "<YOUR_SECRET_KEY>"
      }
    }
  }
}
```

## Features

### Available Tools

| Tool | Purpose |
|------|---------|
| QueryRumWebProjects | Query RUM-WEB application list |
| QueryRumWebMetric | Query network/exception/PV/UV/performance/resource metrics |
| QueryRumWebLog | Full log search |
| QueryResourceByPage | Query resource metrics by page |
| QueryApmLinkId | Get linked APM application ID |

### Built-in Analysis Workflows

| Workflow | Description |
|----------|-------------|
| TOP Exception Analysis | JS/Promise errors, resource loading errors diagnosis |
| TOP Page Performance Analysis | LCP/FCP and WebVitals analysis, performance bottleneck diagnosis |
| TOP API Performance & Stability Analysis | API latency, status code errors, retcode error analysis |
| TOP Slow Resource Loading Analysis | Static resource loading bottleneck diagnosis |

### Advanced Capabilities

- **APM Correlation**: When logs contain trace information, correlate with APM for backend trace analysis
- **Multi-Dimensional Drill-Down**: Analyze by region, ISP, platform, version, page, and more
- **Smart Routing**: Automatically match the most suitable analysis workflow based on user needs

## Key Improvements (v2.0)

| Improvement | Change |
|-------------|--------|
| SKILL.md size | Reduced ~45% with better organization |
| Trigger conditions | Added when-not rules |
| Guardrails | 🔴🟡🟢 three-severity-level system |
| Workflow entry | Embedded decision tree in SKILL.md |
| Rule descriptions | Added "why" for each rule |
| Output standards | Added good/bad report benchmarks |
| APM section | Separated to `references/apm_analysis.md` |

## Useful Links

| Resource | URL |
|----------|-----|
| RUM Console | https://console.tencentcloud.com/rum |
| RUM Console Demo | https://console.tencentcloud.com/rum/web/demo |
| Application Integration Guide | https://www.tencentcloud.com/zh/document/product/1131/44496 |
| Web SDK Connection Guide | https://www.tencentcloud.com/document/product/1131/44517 |
| Getting Started | https://www.tencentcloud.com/document/product/1131/44493 |
| RUM Product Overview | https://www.tencentcloud.com/document/product/1131/44486 |
| RUM Pricing | https://www.tencentcloud.com/document/product/1131/44490 |
| API Key Management | https://console.tencentcloud.com/cam/capi |

## Notes

1. RUM MCP uses `SSE` protocol
2. Authentication is via `SecretId` and `SecretKey` in HTTP headers — keep them secure
3. Recommended timeout: 15-30 seconds
