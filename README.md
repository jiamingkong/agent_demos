# Minimalist MCP-Based AI Agent Skill System

一个极简的 Python 实现，展示如何构建基于 MCP 的 AI 智能体技能系统。

> 只需两行命令，即可启动一个具备动态技能加载能力的智能体，体验 AI 辅助编程的乐趣。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install openai rich mcp python-dotenv
```

### 2. 设置 API 密钥
在项目根目录创建 `api_key.txt` 文件，填入你的 DeepSeek API 密钥。

### 3. 启动智能体
```bash
python main.py
```

就这么简单！智能体会自动加载所有技能，并进入交互式对话模式。

## ✨ 项目特点

### 极简的 Python 实现
- **代码量小**：核心逻辑仅几百行，便于理解与扩展
- **纯 Python**：不依赖复杂框架，直接使用标准库和轻量级 MCP 协议
- **即插即用**：技能以独立 MCP 服务器形式存在，动态加载

### 动态技能系统
智能体启动时仅有基础工具，需要什么技能就加载什么：
- **规划器**：基于文件的规划系统（Manus 风格）
- **编码助手**：代码调查、读取、搜索、编辑和执行命令
- **系统管理**：本地系统信息和 SSH 连接管理
- **操作系统操作**：文件系统操作
- **Git**：版本控制操作
- **网页抓取**：使用 Jina AI API 进行网页检索

### 学习价值
这个项目不是为了生产环境而设计，而是为了**展示 AI 智能体的内部工作原理**：
- 了解 MCP（模型上下文协议）的实际应用
- 学习如何为 AI 智能体构建工具系统
- 掌握动态技能加载的设计模式

## 🏗️ 内部架构（简要）

```
agent.py              # DeepSeekMCPAgent 实现
main.py               # 入口点：加载技能并启动聊天循环
servers/              # MCP 技能服务器（每个技能独立）
requirements.txt      # 依赖列表
```

每个技能都是独立的 MCP 服务器，遵循标准的协议格式，易于添加新技能。

## 📖 深入探索

如果你对内部实现感兴趣：

1. **查看技能实现**：浏览 `servers/` 目录下的各个技能
2. **阅读核心代码**：`agent.py` 展示了如何集成 MCP 客户端与 DeepSeek API
3. **尝试添加新技能**：参照现有模板，创建自己的技能服务器

## 🧪 测试

项目已配置 pytest 测试套件和自动化 CI 流水线。

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行单个测试文件
python -m pytest tests/test_agent.py -v

# 使用测试技能（需启动代理）
# 代理启动后，可加载 testing 技能并使用 run_pytest 等工具
```

### 测试技能
我们创建了一个专门的 **testing** 技能，提供以下工具：
- `run_pytest` – 运行 pytest 并返回结果
- `list_test_files` – 列出所有测试文件
- `run_test_file` – 运行指定测试文件
- `get_test_coverage` – 生成覆盖率报告（需 pytest‑cov）

### 持续集成
GitHub Actions 配置文件位于 `.github/workflows/ci.yml`，会在推送或拉取请求时自动运行测试。

### 编写新测试
- 单元测试放在 `tests/` 目录下，文件命名遵循 `test_*.py`
- 集成测试放在 `tests/integration/` 目录下
- 参考 `tests/test_agent.py` 中的示例

## 🤔 常见问题

**Q：这个项目适合生产环境吗？**  
A：这是一个教学演示项目，适合学习和实验。生产环境需要更多安全性和稳定性考虑。

**Q：需要多少 Python 经验？**  
A：基本了解 Python 即可运行。要理解内部原理，建议有中级 Python 知识。

**Q：可以添加新技能吗？**  
A：当然！技能系统设计为可扩展的。只需在 `servers/` 下创建新目录并实现 MCP 服务器。

## 🙏 致谢

- 基于 [MCP（模型上下文协议）](https://modelcontextprotocol.io/) 构建
- 使用 [DeepSeek API](https://platform.deepseek.com/)
- 受 Claude 技能系统和 Manus 规划启发
