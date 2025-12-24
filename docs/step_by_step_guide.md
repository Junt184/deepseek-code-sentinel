# 第三阶段：步进式开发手册 (Step-by-Step Guide)

> **角色**：安全开发架构师
> **项目**：LLM 代码安全检查系统 (FastAPI + Vue + DeepSeek)
> **版本**：v1.0.0

---

## 阶段一：基础设施冷启动 (Infrastructure Cold Start)

**目标**：打通 "Code Input -> Backend -> Mock LLM -> Frontend Display" 的最小闭环，不涉及真实 LLM 调用逻辑，仅验证架构连通性。

### 1.1 核心任务
1.  **后端 (FastAPI)**: 搭建基础脚手架，配置 Pydantic V2，设置 CORS，实现 `POST /api/v1/analyze` (Mock 返回)。
2.  **前端 (Vue 3 + Vite)**: 集成 `monaco-editor`，搭建左右分栏布局（左代码，右报告）。
3.  **配置管理**: 实现 `.env` 加载器，**严禁**将 DeepSeek API Key 硬编码。

### 1.2 Agent 指令标准
*   **准入 (Entry)**:
    > "初始化项目结构。后端要求使用 FastAPI Router 模式，禁止所有逻辑堆在 main.py。前端要求使用 Pinia 管理状态。创建 `.env.example` 模板。"
*   **准出 (Exit)**:
    > "运行 `pytest` 应通过基础健康检查。前端启动后，点击'检查'按钮，控制台能打印出后端返回的 Mock JSON 数据。检查代码库，确保没有任何 API Key 字符串存在。"

### 1.3 测试驱动 (TDD)
*   **Unit**: `test_health_check` (确保 API 服务存活).
*   **Integration**: `test_analyze_endpoint_structure` (验证 Request/Response Schema 是否符合契约，字段类型是否严格匹配).

---

## 阶段二：核心分析引擎构建 (Core Analysis Engine)

**目标**：接入 DeepSeek API，实现 Prompt 工程与结构化输出解析。

### 2.1 核心任务
1.  **LLM Client**: 封装 DeepSeek 调用层，实现重试机制 (Retrying) 和超时控制。
2.  **Prompt Manager**: 建立 Prompt 模板库（System Prompt + User Prompt），分离代码与提示词。
3.  **异步处理**: 使用 FastAPI `BackgroundTasks` 或 `asyncio` 处理耗时请求，避免阻塞主线程。

### 2.2 Agent 指令标准
*   **准入 (Entry)**:
    > "实现 `LLMService` 类。要求：仅支持异步调用 (`acreate`)。Prompt 必须包含'请以 JSON 格式输出，包含 severity, line, suggestion 字段'的强约束。"
*   **准出 (Exit)**:
    > "提供一段包含 SQL 注入漏洞的 Python 代码，系统能准确识别并返回 JSON 格式的漏洞报告。如果 DeepSeek 返回非 JSON 格式，系统应抛出自定义 `LLMOutputError` 而不是 500 崩溃。"

### 2.3 测试驱动 (TDD)
*   **Unit**: `test_prompt_rendering` (验证代码片段是否正确插入 Prompt).
*   **Mock**: `test_llm_parsing_failure` (模拟 LLM 返回乱码，验证解析器的容错与 fallback 机制).

---

## 阶段三：前端交互与流式反馈 (Frontend & Visualization)

**目标**：优化长耗时体验，实现 SSE (Server-Sent Events) 流式响应，Markdown 漏洞报告渲染。

### 3.1 核心任务
1.  **流式接口**: 将 `/analyze` 改造或新增 `/analyze/stream`，支持流式输出分析进度（如：“正在分析逻辑漏洞...” -> “发现 3 个风险”）。
2.  **可视化组件**: 封装 `VulnerabilityCard` 组件，根据风险等级（High/Medium/Low）渲染不同颜色。
3.  **代码高亮**: 利用 Monaco Editor 的 Decorators 功能，在问题代码行号处显示波浪线警告。

### 3.2 Agent 指令标准
*   **准入 (Entry)**:
    > "前端实现 `EventSource` 或 `fetch` 流式读取。后端使用 `StreamingResponse`。Markdown 渲染器必须配置 DOMPurify 防止 XSS。"
*   **准出 (Exit)**:
    > "上传 200 行代码，进度条应实时更新，不出现前端假死。分析完成后，Markdown 格式的修复建议能正确渲染代码块，且不高亮错位。"

### 3.3 测试驱动 (TDD)
*   **E2E (Cypress/Playwright)**: 模拟用户点击分析 -> 等待流式响应结束 -> 验证页面是否存在“高危”红色标签。

---

## 阶段四：安全加固与边界防御 (Security Hardening)

**目标**：防止恶意代码攻击系统本身，控制 Token 成本。

### 4.1 核心任务
1.  **输入清洗**: 限制上传代码大小（如 max 10KB），过滤掉可能导致 Prompt Injection 的特殊字符（虽然 LLM 自身有防御，但应用层需兜底）。
2.  **API 限流**: 基于 IP 或 Session 实现 Rate Limiting (Token Bucket 算法)，防止恶意刷接口消耗 DeepSeek 额度。
3.  **敏感词过滤**: 在发送给 LLM 前，使用 Regex 扫描代码中的 `sk-`, `password` 等硬编码凭据，进行掩码处理 `***`。

### 4.2 Agent 指令标准
*   **准入 (Entry)**:
    > "实现 `InputValidator` 中间件。实现内存版限流器（暂不需要 Redis）。实现 `CredentialScrubber` 函数。"
*   **准出 (Exit)**:
    > "尝试上传 10MB 文件，接口应秒回 413 错误。尝试 1 秒内并发请求 10 次，第 N 次后应返回 429 错误。上传包含 `AWS_SECRET_KEY` 的代码，日志中看到的发送给 LLM 的 Payload 必须是掩码后的。"

### 4.3 测试驱动 (TDD)
*   **Security**: `test_prompt_injection` (尝试在代码注释中写入 "Ignore previous instructions", 验证系统是否仍按原逻辑执行).
*   **Unit**: `test_scrubber_regex` (验证常见 Key 格式是否被正确替换).

---

## 阶段五：生产交付 (Deployment & Delivery)

**目标**：Docker 化交付，日志监控。

### 5.1 核心任务
1.  **Dockerfile**: 编写 Multi-stage build Dockerfile (Python Slim + Nginx/Static)。
2.  **Logging**: 配置结构化日志 (JSON logs)，记录 `request_id`, `tokens_used`, `latency`。
3.  **CI Pipeline**: GitHub Actions 脚本，并在 Commit 时运行 Lint (Ruff) 和 Tests。

### 5.2 Agent 指令标准
*   **准入 (Entry)**:
    > "创建 Dockerfile，产物镜像大小不得超过 500MB。配置 Loguru 记录器，确保每条 LLM 调用日志都包含 token 消耗量（如有）。"
*   **准出 (Exit)**:
    > "执行 `docker run`，容器能正常启动。访问 `localhost:80` 能看到页面。查看容器日志，能看到请求的 Trace ID 贯穿全链路。"

### 5.3 测试驱动 (TDD)
*   **Infra**: `test_docker_build` (构建脚本不报错).
*   **Smoke**: `test_container_health` (容器启动后 `/health` 接口返回 200).

---

## [风险预警] (Risk Warning)

本方案在以下**极端情况**下会失效或造成严重后果：

1.  **上下文雪崩 (Context Avalanche)**:
    *   **场景**: 用户上传超长代码（如 5000 行单文件）。
    *   **后果**: 超过 DeepSeek 上下文窗口，导致截断或 API 报错。
    *   **规避**: 必须在前端和后端双重限制字符数。对于超大文件，需按函数/类进行 AST 切分（本项目暂不包含此复杂逻辑，需在 PRD 明确不支持）。

2.  **幻觉注入 (Hallucination Injection)**:
    *   **场景**: 代码逻辑极其晦涩（如复杂的位运算混淆），LLM 无法理解但强行解释。
    *   **后果**: 产生一本正经的胡说八道，误导开发者删除核心安全逻辑。
    *   **规避**: UI 必须醒目提示“AI 建议仅供参考，请人工复核”。

3.  **合规黑洞 (Compliance Blackhole)**:
    *   **场景**: 用户上传公司核心算法代码或包含 PII (个人隐私信息) 的数据。
    *   **后果**: 代码被发送至第三方 LLM 服务器，违反 GDPR 或公司数据安全红线。
    *   **规避**: 部署前必须签署数据处理协议，或仅支持私有化部署模型（DeepSeek 暂不支持本地，这是架构硬伤）。
