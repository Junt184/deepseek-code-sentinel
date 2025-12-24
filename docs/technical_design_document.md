# 第二阶段：技术方案设计文档 (TDD)

> **角色**：安全开发架构师
> **项目**：LLM 代码安全检查系统
> **版本**：v1.0.0

---

## 1. 架构反思 (Brutal Honesty)

我们需要诚实地面对 [FastAPI + Vue + DeepSeek] 这一技术栈在当前场景下的先天缺陷。

### 1.1 Python/FastAPI 的并发软肋
*   **缺陷**: 虽然 FastAPI 支持 `async`，但 Python 的 GIL (全局解释器锁) 依然存在。如果我们在主线程中进行了任何 CPU 密集型操作（如正则表达式清洗大段代码、复杂的 AST 解析），会瞬间阻塞整个 Event Loop，导致其他用户的请求卡死。
*   **补偿**:
    *   **严格异步**: 所有 IO 操作（包括读写日志）必须 `await`。
    *   **进程隔离**: 复杂的代码预处理（AST Check）如果耗时超过 10ms，必须下放到 `ProcessPoolExecutor` 或 Celery Worker 中，**严禁**在 HTTP 请求处理函数中直接运行。

### 1.2 Vue Client-Side 的渲染瓶颈
*   **缺陷**: Monaco Editor 是重量级组件，且 Markdown 渲染（特别是带语法高亮的）非常消耗浏览器主线程。当 LLM 快速吐出大量 Token 时，频繁触发 DOM 更新会导致页面掉帧、打字机效果卡顿。
*   **补偿**:
    *   **节流 (Throttling)**: 对 SSE 接收到的数据流进行缓冲，每 100ms 或每接收 50 字符才触发一次 UI 渲染，而不是每收到 1 个 Token 就渲染一次。
    *   **Web Worker**: 将 Markdown 解析 (`marked.js` 或 `markdown-it`) 放入 Web Worker 线程运行。

### 1.3 DeepSeek API 的不可控性
*   **缺陷**: 作为外部依赖，它的延迟（Latency）和可用性（Availability）完全不可控。且模型输出格式（Json Mode）偶尔会抽风，输出半截 JSON 或夹带私货（如 "Here is the json:"）。
*   **补偿**:
    *   **鲁棒解析器**: 实现一个 "Fuzzy JSON Parser"，尝试从非标文本中提取 JSON 对象，而不是直接 `json.loads` 报错。
    *   **超时熔断**: 设定 30s 硬超时，超时后自动取消请求并向用户报错，避免连接堆积耗尽服务器资源。

---

## 2. 数据建模 (Data Modeling)

本系统是“无状态”倾向的，但为了审计和缓存，我们需要轻量级存储。建议使用 **SQLite** (开发/单机) 或 **PostgreSQL** (生产)。

### 2.1 核心表结构 Schema

**Table: `analysis_tasks`**

| Field | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | 任务唯一标识 |
| `code_hash` | CHAR(64) | Index | 源代码内容的 SHA-256 哈希（用于缓存去重） |
| `source_code` | TEXT | NOT NULL | 用户上传的原始代码 |
| `language` | VARCHAR(20) | | 编程语言 (python, java, etc.) |
| `status` | ENUM | Index | `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED` |
| `result_json` | JSONB | NULL | LLM 返回的结构化结果 |
| `error_msg` | TEXT | NULL | 失败原因 |
| `created_at` | TIMESTAMP | | 创建时间 |
| `duration_ms` | INT | | 耗时统计 |

**索引设计建议**:
*   `CREATE INDEX idx_code_hash ON analysis_tasks(code_hash);` -> 核心优化点：如果两个用户上传了一模一样的代码，直接查库返回之前的分析结果，**秒级响应且省钱**。

---

## 3. 接口规范 (API Contract)

### 3.1 创建分析任务
**POST** `/api/v1/analyze`

**Request**:
```json
{
  "code": "import os...",
  "language": "python",
  "stream": true
}
```

**Response (202 Accepted)**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "stream_url": "/api/v1/analyze/550e8400/stream"
}
```

### 3.2 获取流式结果 (SSE)
**GET** `/api/v1/analyze/{task_id}/stream`

**Events**:
*   `event: progress` -> `data: {"stage": "scanning", "percent": 30}`
*   `event: chunk` -> `data: {"delta": "SQL Injection found..."}` (报告文本片段)
*   `event: result` -> `data: {...}` (最终完整的 JSON 结构)
*   `event: error` -> `data: {"code": "LLM_TIMEOUT", "msg": "DeepSeek is busy"}`
*   `event: close` -> `data: "DONE"`

---

## [风险预警] (Risk Warning)

本架构设计在以下场景会失效：

1.  **数据库连接耗尽**:
    *   如果使用了 `BackgroundTasks` 且并发量极大，每个任务都持有一个 DB 连接写入日志，SQLite 会立刻锁死 (`database is locked`)，PostgreSQL 也会连接池枯竭。
    *   *规避*: 日志写入必须解耦（写入队列，由单独 Worker 消费入库）。

2.  **SSE 中间件缓冲**:
    *   Nginx 或企业负载均衡器 (LB) 默认会开启 Response Buffering。它们会等攒够 4KB 数据才发给客户端，导致流式效果变成了“一段一段”的卡顿，甚至最后一次性吐出。
    *   *规避*: 必须在 Nginx 配置中显式关闭缓冲 (`proxy_buffering off;`)，并设置 `X-Accel-Buffering: no` 响应头。
