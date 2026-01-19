# Minimalist MCP-Based AI Agent Skill System

一个极简的 Python 实现，展示如何构建基于 MCP 的 AI 智能体技能系统。

> 只需两行命令，即可启动一个具备动态技能加载能力的智能体，体验 AI 辅助编程的乐趣。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install openai rich mcp python-dotenv
```

### 2. 启动智能体
```bash
python main.py
```

就这么简单！第一次启动的时候它会询问你的 Deepseek API 密钥，你可以去platform.deepseek.com注册账号获取。

### 建议尝试的Prompt

```
请你阅读当前目录，告诉我技能系统是怎么工作的。
```

## ✨ 项目特点

这是一个为教育展示设计的极简设计。模型在启动的时候有一个极简的系统提示词，它会在接受命令后，动态加载所需的技能（MCP 服务器），并使用这些技能完成任务。

整个项目核心为`agent.py`和`main.py`，共计 500 行。其他所有技能均为独立的 MCP 服务器，易于理解和扩展。

### 代码质量与测试
- **类型安全**：使用 mypy 进行静态类型检查，确保代码健壮性
- **错误处理**：具体异常捕获，提供清晰的错误信息
- **测试覆盖率**：全面的单元测试和集成测试，覆盖率达 57% 以上
- **持续改进**：通过自动化测试确保代码质量持续提升

### 动态技能系统
智能体启动时仅有基础工具，需要什么技能就加载什么：
- **规划器**：基于文件的规划系统（Manus 风格）
- **编码助手**：代码调查、读取、搜索、编辑和执行命令
- **系统管理**：本地系统信息和 SSH 连接管理
- **操作系统操作**：文件系统操作
- **Git**：版本控制操作
- **网页抓取**：使用 Jina AI API 进行网页检索
- **文件压缩**：使用标准库（zipfile、tarfile、gzip、bz2）进行文件压缩和解压

## 🏗️ 内部架构（简要）

```
agent.py              # DeepSeekMCPAgent 实现
main.py               # 入口点：加载技能并启动聊天循环
servers/              # MCP 技能服务器（每个技能独立）
requirements.txt      # 依赖列表
```

每个技能都是独立的 MCP 服务器，遵循标准的协议格式，易于添加新技能。

## 🔧 代码质量与开发工作流

我们采用现代 Python 开发最佳实践来确保代码质量和一致性。

### 代码格式化
- 使用 [Black](https://github.com/psf/black) 进行自动代码格式化。
- 使用 [isort](https://github.com/PyCQA/isort) 对 import 语句进行排序。

### 静态类型检查
- 使用 [mypy](http://mypy-lang.org/) 进行静态类型检查，确保类型安全。

### 预提交钩子
项目包含一个 `.pre-commit-config.yaml` 配置文件，你可以安装 [pre-commit](https://pre-commit.com/) 来自动执行以下检查：
```bash
pip install pre-commit
pre-commit install
```
之后，每次提交代码时都会自动运行 black、isort、mypy 和基本的代码质量检查。

### 测试
- 使用 [pytest](https://docs.pytest.org/) 进行单元测试和集成测试。
- 测试覆盖率通过 [pytest-cov](https://pytest-cov.readthedocs.io/) 进行监控，目标覆盖率达到 80% 以上。

### 持续集成
项目包含 GitHub Actions 工作流配置（`.github/workflows/ci.yml`），在每次推送或拉取请求时自动运行：
- 多版本 Python (3.10‑3.13) 测试
- 静态类型检查（mypy）
- 代码格式化检查（black、isort）
- 测试覆盖率报告

## 📖 深入探索

如果你对内部实现感兴趣：

1. **查看技能实现**：浏览 `servers/` 目录下的各个技能
2. **阅读核心代码**：`agent.py` 展示了如何集成 MCP 客户端与 DeepSeek API
3. **尝试添加新技能**：参照现有模板，创建自己的技能服务器

## 🙏 致谢

- 基于 [MCP（模型上下文协议）](https://modelcontextprotocol.io/) 构建
- 使用 [DeepSeek API](https://platform.deepseek.com/)
- 受 Claude 技能系统和 Manus 规划启发
