# Minimalist MCP-Based AI Agent Skill System

一个极简的 Python 实现，展示如何构建基于 MCP 的 AI 智能体技能系统。

> 只需两行命令，即可启动一个具备动态技能加载能力的智能体，体验 AI 辅助编程的乐趣。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
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
- **委托分发**：任务委派与并行执行
- **系统管理**：本地系统信息和 SSH 连接管理
- **操作系统操作**：文件系统操作
- **Git**：版本控制操作
- **网页抓取**：使用 Jina AI API 进行网页检索
- **文件压缩**：使用标准库（zipfile、tarfile、gzip、bz2）进行文件压缩和解压
- **数据可视化**：使用 matplotlib 和 pandas 绘制图表（折线图、柱状图、散点图、直方图、箱线图等）
- **办公文档阅读**：读取 PDF、DOCX、PPTX、XLSX 等 Office 文档并转换为 Markdown
- **测试**：运行 pytest、列出测试文件、生成覆盖率报告
- **笔记**：增强的笔记管理，支持标签、元数据（创建/修改时间）、全文搜索、标签列表等高级功能
- **数据库操作**：SQLite、PostgreSQL、MySQL 的数据库连接和查询
- **HTTP API 客户端**：通用 HTTP 请求（GET、POST、PUT、DELETE 等）
- **图像处理**：使用 Pillow 进行图像调整大小、裁剪、旋转、滤镜、格式转换
- **数据清洗**：使用 pandas 进行 CSV 数据清洗（缺失值处理、重复值删除、数据归一化等）
- **演示技能**：简单的问候和计算工具（演示用）
- **CSV 操作**：读取、写入 CSV 文件，列出列名
- **JSON 操作**：读取、写入 JSON 文件，验证 JSON 字符串
- **时间工具**：获取当前时间、格式化时间戳、时间计算
- **哈希计算**：计算字符串和文件的 MD5、SHA-1、SHA-256 哈希值
- **自然语言处理**：使用 TextBlob 进行情感分析、名词短语提取、分词和语言检测
- **电子邮件发送**：通过 SMTP 发送电子邮件
- **Docker 操作**：使用 Docker CLI 列出容器、镜像、运行容器等
- **数据分析**：使用 pandas 进行数据聚合、分组、透视表、合并、排序、过滤
- **系统监控**：使用 psutil 监控 CPU、内存、磁盘使用情况，管理进程
- **包管理**：使用 pip 安装、卸载、列出、搜索 Python 包
- **机器学习基础**：使用 scikit-learn 进行回归、分类、聚类、模型评估
- **加密**：使用 cryptography 库进行对称/非对称加密、签名和哈希
- **文件监控**：使用 watchdog 监控目录变化，捕获文件创建、修改、删除事件
- **YAML 操作**：读写 YAML 文件，验证 YAML 语法
- **正则表达式工具**：正则表达式匹配、搜索、替换和提取
- **PDF 文本提取**：从 PDF 文件中提取文本、元数据，并转换为文本文件
- **网络爬虫**：使用 BeautifulSoup 和 requests 进行网页抓取、链接提取和 CSS 选择器元素查找
- **数据验证**：使用 Pydantic 进行数据验证和模型创建，支持 JSON Schema
- **配置管理**：读取和写入配置文件（env、ini、json、yaml）以及环境变量管理

### 近期改进与增强
- **新增技能**：添加了网络爬虫、数据验证和配置管理三个新技能，扩展了智能体的网页抓取、数据验证和配置管理能力
- **数据可视化**：新增箱线图（box plot）支持
- **图像处理**：新增技能，提供基础的图像处理能力（调整大小、裁剪、旋转、滤镜、格式转换）
- **笔记技能增强**：新增标签系统、元数据管理（创建/修改时间）、全文搜索、标签列表、笔记导出等高级功能
- **数据清洗技能**：新增技能，提供对 CSV 文件的基本数据清洗操作（缺失值处理、重复值删除、数据归一化等）
- **技能系统优化**：改进了技能加载的稳定性和错误处理
- **新增技能**：添加了 CSV、JSON、时间、哈希四个新技能，扩展了数据处理能力
- **新增数据分析、系统监控、包管理技能**：进一步扩展了智能体的数据处理、系统监控和包管理能力
- **新增机器学习基础、加密、文件监控技能**：扩展了智能体的机器学习、加密安全和文件监控能力
- **新增 YAML、正则表达式、PDF 处理技能**：扩展了智能体的配置管理、文本处理和文档解析能力
- **新增自然语言处理、电子邮件发送和 Docker 操作技能**：进一步扩展了智能体的能力范围
- **模块改进**：增强了爬虫、数据下载、数据清洗、数据分析和编码助手模块。新增工具包括：Selenium支持、文件下载、分类编码、相关性分析、代码行数统计等。
- **未来计划**：更多技能增强（数据库连接池、高级 Git 功能、机器学习基础工具等）正在进行中

### 示例用法
启动智能体后，你可以尝试如下指令：

```
请加载数据可视化技能，并绘制一个箱线图，数据系列为 [[1,2,3,4,5], [2,3,4,5,6], [3,4,5,6,7]]，标签为 A、B、C。
```

```
请加载图像处理技能，将图片 /path/to/image.jpg 调整为 200x200 像素并保存为 /tmp/resized.png。
```

智能体会自动加载相应技能并执行任务。

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


## New Skills Added

The project now includes six additional skills to extend its capabilities:

1. **Notification Skill** – send messages to Slack, Telegram, Discord, and generic webhooks.
2. **WebSocket Skill** – connect to WebSocket servers and host simple echo servers (placeholder implementation).
3. **Schedule Skill** – schedule one‑time and cron‑based tasks using APScheduler (placeholder implementation).
4. **Translation Skill** – translate text between languages using Google Translate (googletrans).
5. **Weather Skill** – get current weather data for any city using OpenWeatherMap API.
6. **Summarization Skill** – generate extractive summaries of long texts using sumy library.

These skills are located in `servers/notification_skill`, `servers/websocket_skill`, `servers/schedule_skill`, `servers/translation_skill`, `servers/weather_skill`, and `servers/summarization_skill`. To use them, install the extra dependencies:

```bash
pip install apscheduler websockets googletrans==4.0.0rc1 sumy
```

For usage examples, see `artifacts/new_skills_examples.md`.

## Planned Improvements

Based on the earlier analysis, the following improvements are planned:

- Refactor `chat_loop` to reduce cyclomatic complexity.
- Add timeout and retry logic for skill server connections.
- Enhance error handling and resource cleanup.
- Improve test coverage for existing skills.

Contributions and feedback are welcome!
