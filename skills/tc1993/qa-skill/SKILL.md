---
name: qa-skill
description: 根据生成的代码自动创建测试用例和测试步骤。当接收到dev-skill的输出时自动触发，确保代码质量和功能完整性。
---

# QA Skill - 自动化测试生成器

## 🎯 功能概述

本skill根据生成的SwiftUI iOS代码自动创建测试用例和测试步骤。作为"一人公司自动开发流水线"的第三环节，负责质量保证和功能验证。

## 🔄 触发条件

自动触发条件：
1. dev-skill生成代码后自动触发
2. 接收到包含代码仓库路径的消息
3. 检测到新生成的iOS工程目录

## 📋 输入输出规范

### 输入
- SwiftUI iOS工程代码
- PRD文档（用于验证需求覆盖）
- 项目元数据

### 输出
完整的测试套件，包含：
1. 单元测试用例
2. UI测试用例
3. 集成测试用例
4. 测试步骤文档
5. 测试报告模板

## 🚀 处理流程

### 步骤1：代码分析
1. 扫描工程结构
2. 分析SwiftUI视图组件
3. 识别数据模型和业务逻辑
4. 提取功能点和交互流程

### 步骤2：测试策略制定
1. 根据PRD确定测试范围
2. 设计测试金字塔（单元/集成/UI）
3. 确定测试优先级
4. 规划测试数据

### 步骤3：测试用例生成
1. 生成单元测试（XCTest）
2. 生成UI测试（XCUITest）
3. 创建测试辅助类
4. 生成测试数据工厂

### 步骤4：测试步骤文档
1. 创建手动测试步骤
2. 生成测试检查清单
3. 编写测试场景描述
4. 创建缺陷报告模板

### 步骤5：测试执行准备
1. 配置测试环境
2. 设置测试目标
3. 创建测试计划
4. 生成测试报告模板

## 📁 测试结构

生成的测试工程结构：
```
Tests/
├── UnitTests/
│   ├── {项目名称}Tests.swift
│   ├── ModelsTests/
│   │   ├── {模型1}Tests.swift
│   │   └── {模型2}Tests.swift
│   ├── ViewModelsTests/
│   │   ├── {视图模型1}Tests.swift
│   │   └── {视图模型2}Tests.swift
│   └── ServicesTests/
│       ├── {服务1}Tests.swift
│       └── {服务2}Tests.swift
├── UITests/
│   ├── {项目名称}UITests.swift
│   ├── {功能1}UITests.swift
│   └── {功能2}UITests.swift
└── TestResources/
    ├── TestData/
    ├── TestHelpers/
    └── TestConfigurations/
```

## 🔧 测试技术栈

### 测试框架
- **单元测试**: XCTest
- **UI测试**: XCUITest
- **模拟框架**: 使用协议和依赖注入
- **测试数据**: 工厂模式生成

### 测试策略
- **测试金字塔**: 70%单元测试，20%集成测试，10%UI测试
- **测试驱动**: 关键路径优先测试
- **边界测试**: 异常情况和边界条件
- **回归测试**: 核心功能持续验证

## 🔗 与其他Skill的集成

### 上游依赖
- 从dev-skill接收代码工程
- 从prd-skill获取需求文档
- 验证需求与实现的一致性

### 测试反馈
- 生成测试报告
- 标识潜在问题
- 提供改进建议

### 流水线完成
- 标记流水线完成状态
- 生成最终交付物
- 提供部署建议

## ⚙️ 配置参数

### 测试生成选项
```yaml
test_coverage: 80
include_unit_tests: true
include_ui_tests: true
include_integration_tests: true
test_priority: critical_first
```

### 测试环境
- `test_device`: 测试设备（iPhone 14 Pro）
- `ios_version`: iOS测试版本（16.0+）
- `test_timeout`: 测试超时时间（默认10秒）
- `retry_count`: 失败重试次数（默认3次）

## 📊 质量指标

### 测试覆盖率目标
- 总体覆盖率: > 80%
- 核心功能覆盖率: > 95%
- 关键路径覆盖率: 100%

### 测试质量
- 测试用例可执行性: 100%
- 测试步骤清晰度: > 90%
- 缺陷发现率: > 85%

## 🎨 测试模板

### 单元测试模板
```swift
import XCTest
@testable import {项目名称}

final class {模型名称}Tests: XCTestCase {
    var sut: {模型名称}!
    
    override func setUp() {
        super.setUp()
        sut = {模型名称}()
    }
    
    override func tearDown() {
        sut = nil
        super.tearDown()
    }
    
    func test{功能名称}_When{条件}_Should{预期结果}() {
        // Given
        let input = "test input"
        
        // When
        let result = sut.{方法名称}(input)
        
        // Then
        XCTAssertEqual(result, "expected output")
    }
    
    func test{功能名称}_WithInvalidInput_ShouldThrowError() {
        // Given
        let invalidInput = ""
        
        // Then
        XCTAssertThrowsError(try sut.{方法名称}(invalidInput))
    }
}
```

### UI测试模板
```swift
import XCTest

final class {功能名称}UITests: XCTestCase {
    var app: XCUIApplication!
    
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    func test{页面名称}_ShouldDisplayCorrectContent() {
        // Given
        let expectedTitle = "页面标题"
        
        // When
        let titleElement = app.staticTexts[expectedTitle]
        
        // Then
        XCTAssertTrue(titleElement.exists)
        XCTAssertTrue(titleElement.isHittable)
    }
    
    func test{交互名称}_WhenTapped_ShouldNavigateToNextScreen() {
        // Given
        let button = app.buttons["按钮名称"]
        
        // When
        button.tap()
        
        // Then
        let nextScreen = app.staticTexts["下一个页面标题"]
        XCTAssertTrue(nextScreen.waitForExistence(timeout: 2))
    }
}
```

### 测试步骤文档模板
```markdown
# {功能名称} - 测试步骤

## 测试场景
- **场景描述**: {描述测试场景}
- **前置条件**: {测试前需要满足的条件}
- **测试数据**: {使用的测试数据}

## 测试步骤
1. {步骤1描述}
2. {步骤2描述}
3. {步骤3描述}

## 预期结果
- {预期结果1}
- {预期结果2}

## 实际结果
- [ ] 通过
- [ ] 失败（备注原因）

## 缺陷记录（如适用）
- **缺陷描述**: 
- **重现步骤**:
- **严重程度**: 
- **优先级**: 
```

## 📈 性能指标

### 测试生成时间
- 小型项目: < 2分钟
- 中型项目: < 5分钟
- 大型项目: < 10分钟

### 测试有效性
- 测试用例通过率: > 95%
- 需求覆盖度: > 90%
- 缺陷发现有效性: > 80%

## 🔄 持续改进

### 测试优化
1. 分析测试执行结果
2. 优化测试用例设计
3. 改进测试数据生成

### 质量提升
- 跟踪测试覆盖率趋势
- 分析缺陷模式
- 优化测试策略

---

**注意**: 本skill是"一人公司自动开发流水线"的最终环节，完成测试后标记流水线完成，提供可交付的iOS应用。