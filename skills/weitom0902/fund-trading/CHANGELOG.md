# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-03-30

### Changed
- 更新 API 地址为生产环境地址 `https://openapi.nicaifu.com/openApi`
- 优化错误处理和提示信息

### Fixed
- 修复 Token 过期后自动刷新的问题

## [1.0.0] - 2026-03-26

### Added
- 首次发布
- 支持账户管理（注册、切换、查看）
- 支持基金查询（列表、详情、推荐）
- 支持交易操作（申购、赎回、撤单）
- 支持资产查询（持仓、收益、交易记录）
- OAuth 2.0 Client Credentials 认证
- Token 自动缓存和刷新
- 同时发布 Python (PyPI) 和 TypeScript (npm) 版本
- 本地配置文件持久化

### Security
- 使用 OAuth 2.0 安全认证
- Token 本地加密存储
- 支持 Token 自动刷新