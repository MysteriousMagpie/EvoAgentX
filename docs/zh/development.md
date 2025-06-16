# 开发指南

本文档介绍仓库结构以及在本地设置开发环境的方法。

## 仓库结构

- **`evoagentx/`** – 核心 Python 库，包含代理、工具、模型和工作流逻辑。
- **`examples/`** – 示例脚本和工作流。
- **`server/`** – 基于 FastAPI 的后端服务。
- **`client/`** – Vite + React 前端项目。
- **`intelligence-parser/`** – 独立的 TypeScript 工具包。
- **`tests/`** – Python 单元测试。
- **`docs/`** – MkDocs 文档源码。
- **`run_evoagentx.py`** – 根据目标生成并执行工作流的脚本。

## 环境搭建

安装开发依赖：

```bash
pip install -e .[dev]
# 或者
pip install -r requirements.txt
```

按照 [快速上手](quickstart.md#api%E9%92%A5--llm-%E9%85%8D%E7%BD%AE) 中的说明设置 `OPENAI_API_KEY`。

## 运行测试

提交代码前请确保测试通过：

```bash
pytest -q
```

## 构建文档

文档站点由 MkDocs 构建，可使用以下命令本地预览：

```bash
mkdocs serve
```

站点配置位于 `mkdocs.yml`。

## 全栈示例

仓库还提供一个简单的 FastAPI 后端和 React 前端，运行方法：

```bash
# 后端
python -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
uvicorn server.main:app --reload
```

```bash
# 前端
cd client
pnpm install
pnpm dev
```

更多细节参见 [README](../README-zh.md#quick-start-full-stack)。
