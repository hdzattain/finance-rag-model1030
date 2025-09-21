# finance-rag-model1030

综合量化投研平台，结合缠论思想、Agentic RAG 与多平台回测能力，支持大模型驱动的投研流程。

## 架构总览

平台按照分层架构设计，覆盖从大模型接入到硬件适配的十个核心模块：

1. **大模型接入层**（`quant_platform/llm`）：支持 OpenAI、Anthropic、DeepSeek、通义千问等主流模型，提供统一路由与降级策略。
2. **Agentic RAG 层**（`quant_platform/rag`）：使用 BAAI 的 BGE 嵌入与 Reranker，结合余弦相似度与 BM25 混合检索，可接入 Qdrant 或回退至内存检索。
3. **新知识拉取层**（`quant_platform/ingestion`）：对接雪球、A 股指数与金融机构研报，支持定时抓取并写入 RAG。
4. **平台对接层**（`quant_platform/backtesting`）：封装缠论策略回测与三方平台适配器，可通过 token 提交回测任务。
5. **研究层**（`quant_platform/research`）：自动论文检索 + 人工笔记并行管理，生成投研报告。
6. **前端层**（`quant_platform/frontend`）：规划 React Shell + Vue 组件协同的登录页面蓝图。
7. **Agent 能力对接层**（`quant_platform/agents`）：集成 UI-TARS 等 Agentics 助手能力注册表。
8. **虚拟容器层**（`quant_platform/virtualization`）：模拟人工登录流程，统一管理需要人机验证的网站任务。
9. **架构优化层**（`quant_platform/architecture_layer`）：聚合业内优秀框架，持续反思并输出设计模式建议。
10. **底层调优适配层**（`quant_platform/hardware`）：根据不同硬件资源调整模型选择与批量参数。

## 主要组件

- `app.py`：Flask API，统一暴露推荐、回测、研究、Agent、虚拟登录等接口。
- `quant_platform/`：核心 Python 包，囊括十个模块的实现。
- `scripts/`：示例脚本，演示 RAG 推理、数据采集、缠论回测与架构自检流程。

## 快速开始

1. 安装依赖（根据实际需求选择）：
   ```bash
   pip install flask pandas requests sentence-transformers FlagEmbedding qdrant-client rank-bm25
   ```
2. 配置必要的环境变量（可选）：
   ```bash
   export OPENAI_API_KEY=...  # 或其他模型 token
   export QDRANT_HOST=localhost
   export QDRANT_PORT=6333
   ```
3. 启动 API：
   ```bash
   python app.py
   ```
4. 运行示例脚本：
   ```bash
   python scripts/rag_inference.py
   python scripts/strategy_backtesting.py
   python scripts/data_preprocessing.py
   python scripts/model_training.py
   ```

## 接口示例

- 推荐接口：
  ```bash
  curl -X POST http://localhost:5000/recommend \
       -H "Content-Type: application/json" \
       -d '{"query": "银行板块缠论策略怎么构建？", "rounds": 2}'
  ```
- 本地回测：
  ```bash
  curl -X POST http://localhost:5000/backtest/local \
       -H "Content-Type: application/json" \
       -d '{"market_data": [{"close": 100}, {"close": 101}, {"close": 99}]}'
  ```

## 目录结构

```
├── app.py
├── quant_platform/
│   ├── llm/ ...
│   ├── rag/ ...
│   ├── ingestion/ ...
│   ├── backtesting/ ...
│   ├── research/ ...
│   ├── frontend/ ...
│   ├── agents/ ...
│   ├── virtualization/ ...
│   ├── architecture_layer/ ...
│   └── hardware/ ...
└── scripts/
    ├── rag_inference.py
    ├── strategy_backtesting.py
    ├── data_preprocessing.py
    └── model_training.py
```

## 说明

- 所有外部依赖均采用“尽力而为”策略：缺少 token 或第三方依赖时自动回退到 Dummy 实现，保证系统可用性。
- 缠论策略示例为轻量化实现，可按需替换为生产级算法。
- 可结合 AgentRegistry 与 VirtualLoginSandbox 扩展对复杂登录流程及人机验证的支持。
