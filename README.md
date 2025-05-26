# Docker Compose Generator

一个基于CrewAI框架的智能Docker Compose生成工具，通过多代理协作与流程编排，自动分析项目并生成完整的Docker部署配置。

## 项目简介

Docker Compose Generator 利用 CrewAI 框架的强大功能，通过一系列专业化的AI代理（Crews）协同工作，实现从项目源代码分析到完整 Docker Compose 部署配置生成的端到端自动化。项目定义了一个核心流程 (`AnalysisFlow`) 来编排这些Crews，每个Crew负责流程中的一个关键阶段。

## CrewAI 框架应用

本项目深度整合了CrewAI框架，主要体现在：

- **多Crew协作**：定义了四个核心Crews (`ProjectReader`, `ServiceInference`, `DockerfileGenerator`, `ComposeGenerator`)，每个Crew包含专门的AI代理和任务，以处理特定领域的分析和生成工作。
- **流程编排 (`AnalysisFlow`)**：在 `main.py` 中定义的 `AnalysisFlow` 负责按顺序触发各个Crew，并管理它们之间的数据依赖和传递，确保整个流程的顺畅执行。
- **任务驱动**：每个Crew内部的任务都清晰定义了目标、输入（上下文）和预期输出，指导AI代理完成具体工作。
- **配置文件驱动行为**：每个Crew的行为（代理角色、任务描述）都在其各自的 `config/agents.yaml` 和 `config/tasks.yaml` 文件中定义，方便调整和扩展。
- **工具集成**：集成了如 `SerperTool` 进行实时网络检索（例如，获取Docker最佳实践、解析未知服务依赖）和 `FileWriterTool` 进行文件操作。
- **工作流可视化**：项目执行后会在根目录生成 `crewai_flow.html`，提供 `AnalysisFlow` 中定义的Crews及其任务之间关系的直观可视化展示。

## 主要功能

- **全面的项目分析**：自动读取项目结构，分析如 `pom.xml` 或 `package.json` 等依赖文件，识别项目类型、语言、框架版本等。
- **外部服务推断**：根据项目依赖和文件内容，智能推断项目所需的外部服务（数据库、缓存、消息队列等）。
- **优化的Dockerfile生成**：为项目主应用（基于指定构建物）生成符合最佳实践的Dockerfile。
- **自动化Docker镜像构建**：使用生成的Dockerfile在正确的构建上下文中构建主应用的Docker镜像。
- **完整的Docker Compose配置生成**：基于分析结果和生成的镜像，创建包含主应用及所有推断出的外部服务的 `docker-compose.yml` 文件。
- **实时最佳实践与未知服务解析**：通过 `SerperTool` 查询最新的Docker配置最佳实践和处理在分析中遇到的未知服务依赖。

## 系统架构与工作流程 (`AnalysisFlow`)

系统的核心是定义在 `main.py` 中的 `AnalysisFlow`，它按顺序编排以下四个主要Crew的工作：

1.  **项目分析阶段 (`ProjectReader` Crew)**:
    *   **职责**: 分析指定项目路径 (`PROJECT_PATH`)，读取项目文件结构和依赖项（例如，Maven的 `pom.xml`）。
    *   **输入**: `PROJECT_PATH` (来自 `.env` 文件)。
    *   **输出**: `dependencies_analysis` (包含项目类型、语言、框架、依赖库等信息的结构化数据), `project_files_path` (项目文件列表，用于后续分析的上下文)。
    *   **触发**: `AnalysisFlow.read_project_structure` 方法。

2.  **服务推断阶段 (`ServiceInference` Crew)**:
    *   **职责**: 基于 `dependencies_analysis` 和 `project_files_path`，推断项目运行所需的外部服务和中间件（如MySQL, Redis, Kafka等）。
    *   **输入**: `dependencies_analysis`, `project_files_path` (来自上一阶段)。
    *   **输出**: `service_inference_res` (列出推断出的服务及其类型的结构化数据)。
    *   **触发**: `AnalysisFlow.service_inference` 方法。

3.  **应用Docker化阶段 (`DockerfileGenerator` Crew & `utils.docker_build`)**:
    *   **`DockerfileGenerator` Crew的职责**: 根据 `dependencies_analysis` (作为 `project_analysis_results`) 和主应用的构建物路径 (`ARTIFACT_PATH`)，生成优化的Dockerfile。
        *   **输入**: `dependencies_analysis`, `ARTIFACT_PATH` (来自 `.env` 文件)。
        *   **输出**: `dockerfile_content` (生成的Dockerfile内容), `build_context_path` (Dockerfile应存放的构建上下文目录路径)。
        *   **智能特性**: 利用 `SerperTool` 检索Dockerfile相关的最新最佳实践和安全建议。
    *   **镜像构建步骤**: `AnalysisFlow` 接收到 `build_context_path` 后，会调用 `src.docker_compose_generator.utils.docker_build.build_docker_image` 函数，使用 `PROJECT_NAME` (来自 `.env`) 和版本标签（如"1.0"）来构建主应用的Docker镜像。
        *   **输出**: 构建完成的Docker镜像，其名称 (`single_project_image_name`) 将用于后续Compose文件的生成。
    *   **触发**: `AnalysisFlow.image_builder` 方法 (该方法内部调用 `DockerfileGenerator` Crew 和构建工具函数)。

4.  **Docker Compose编排阶段 (`ComposeGenerator` Crew)**:
    *   **职责**: 整合之前阶段的所有信息，包括 `dependencies_analysis`, `service_inference_res`, 以及主应用的 `single_project_image_name`，生成一个完整、可运行的 `docker-compose.yml` 文件。
        *   **子任务**: 其内部代理 (`service_analyzer`, `network_configurator`, `compose_integrator`) 分别负责外部服务配置转换、网络设计和最终文件整合。
        *   **输入**: `dependencies_analysis`, `service_inference_res`, `single_project_image_name`。
        *   **输出**: `docker_compose_content` (最终的 `docker-compose.yml` 文件内容，通常会由 `FileWriterTool` 保存到 `output/docker-compose.yml`)。
        *   **智能特性**: `service_analyzer` 和 `compose_integrator` 利用 `SerperTool` 处理未明确定义的外部服务，并检索Compose相关的最佳实践。
    *   **触发**: (在 `AnalysisFlow` 中，这一步会在 `image_builder` 之后，接收其产出的镜像名以及先前步骤的分析结果来执行。当前 `main.py` 可能需要显式添加或调整此步骤的调用)。

## CrewAI Flow 可视化

项目执行 `AnalysisFlow().export_flow_chart()` (或在特定配置下自动生成) 后，会在项目根目录创建 `crewai_flow.html` 文件。此文件提供了 `AnalysisFlow` 中定义的各个Crews及其任务之间关系的图形化表示，帮助用户：

-   直观理解代理的协作方式和任务的执行顺序。
-   追踪数据在不同阶段间的流动。
-   辅助调试和优化整个工作流程。

**工作流快照：**

[CrewAI Flow Snapshot](crewai_flow_snapshot.png)

## 安装与使用

### 前提条件
- Python 3.8+
- Docker 和 Docker Compose
- OpenAI API 密钥 (用于CrewAI代理)
- Serper API 密钥 (用于网络检索功能)

### 安装
```bash
# 克隆仓库
git clone https://github.com/yourusername/docker_compose_generator.git
cd docker_compose_generator

# 安装依赖
pip install -r requirements.txt
```

### 配置
在项目根目录创建一个 `.env` 文件，并填入以下信息：

```env
# API 配置
OPENAI_API_KEY="your_openai_api_key_here"
SERPER_API_KEY="your_serper_api_key_here"

# 项目核心配置
PROJECT_NAME="your_project_name" # 用于Docker镜像命名等
PROJECT_PATH="/path/to/your/project" # 项目源代码的绝对路径
ARTIFACT_PATH="/path/to/your/project/target/your_artifact.jar" # 主应用构建物的绝对路径
```

### 运行项目
配置好 `.env` 文件后，通过以下命令启动整个分析和生成流程：

```bash
python -m src.docker_compose_generator.main
```

此命令将触发 `AnalysisFlow`，依次执行上述四个主要阶段。最终生成的 `Dockerfile` (在对应的 `build_context_path`下) 和 `docker-compose.yml` (通常在 `output/` 目录下) 可用于部署项目。

### 编程方式与单个Crew交互
除了运行完整的 `AnalysisFlow`，您也可以在代码中单独初始化并运行特定的Crew，例如：

```python
from docker_compose_generator.crews import ProjectReader # 或其他Crew

# 示例：单独运行ProjectReader Crew
project_reader_crew = ProjectReader().crew()
project_analysis_output = project_reader_crew.kickoff(
    inputs={
        "project_path": "/path/to/your/project"
    }
)
print(project_analysis_output)
```

## 项目结构

```
src/docker_compose_generator/
├── __init__.py
├── main.py             # 主入口，定义并运行 AnalysisFlow
├── utils/              # 通用工具函数
│   ├── __init__.py
│   └── docker_build.py # Docker镜像构建函数
├── tools/              # CrewAI 自定义工具 (如有)
│   ├── __init__.py
│   └── project_file_list_tool.py # 示例工具
└── crews/              # CrewAI Crews定义
    ├── __init__.py     # 导出所有Crews
    ├── project_reader/
    │   ├── __init__.py
    │   ├── project_reader.py # ProjectReader Crew 定义
    │   └── config/         # ProjectReader Crew的代理与任务配置
    │       ├── agents.yaml
    │       └── tasks.yaml
    ├── service_inference/
    │   ├── __init__.py
    │   ├── service_inference.py # ServiceInference Crew 定义
    │   └── config/
    │       ├── agents.yaml
    │       └── tasks.yaml
    ├── dockerfile_generator/
    │   ├── __init__.py
    │   ├── dockerfile_generator.py # DockerfileGenerator Crew 定义
    │   └── config/
    │       ├── agents.yaml
    │       └── tasks.yaml
    └── compose_generator/
        ├── __init__.py
        ├── compose_generator.py # ComposeGenerator Crew 定义
        └── config/
            ├── agents.yaml
            └── tasks.yaml
```

## 自定义与扩展

-   **调整代理行为**: 修改对应Crew的 `config/agents.yaml` (角色、目标、背景) 和 `config/tasks.yaml` (任务描述、预期输出)。
-   **扩展Crew功能**: 在Crew的Python定义文件中添加新的 `@agent` 或 `@task`。
-   **修改流程**: 调整 `main.py` 中的 `AnalysisFlow` 定义，改变Crew的调用顺序或依赖关系。
-   **添加新Crew**: 创建新的Crew目录结构，并在 `crews/__init__.py` 和 `main.py` 中集成。

## 注意事项

-   确保 `.env` 文件中的路径为绝对路径且正确无误。
-   AI代理的输出质量依赖于OpenAI模型的版本和提示词的清晰度。
-   生成的配置文件（Dockerfile, docker-compose.yml）建议在生产部署前进行人工审查和测试。


