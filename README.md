# Docker Compose Generator

一个基于CrewAI框架的智能Docker Compose生成工具，通过多代理协作自动分析项目依赖并生成完整的Docker部署配置。

## 项目简介

Docker Compose Generator利用CrewAI框架的多代理协作能力，分析项目结构、依赖和服务需求，自动生成适用于项目的Dockerfile和docker-compose.yml配置文件。通过定义专业化的AI代理及其任务，实现了从项目分析到部署配置生成的端到端自动化。

## CrewAI框架优势

本项目基于CrewAI框架构建，具有以下优势：

- **多代理协作**：不同专业领域的AI代理协同工作，解决复杂问题
- **任务流定义**：通过YAML配置文件定义代理角色和任务描述
- **上下文传递**：代理之间可传递分析结果和生成内容
- **可扩展性**：轻松添加新的代理和任务，扩展系统功能
- **工作流可视化**：项目根目录下的`crewai_flow.html`提供了直观的工作流可视化展示

## 主要功能

- **项目分析**：分析项目结构和依赖，识别项目类型和运行环境
- **Dockerfile生成**：为项目构建产物自动生成优化的Dockerfile
- **Docker镜像构建**：在正确的构建上下文中自动构建Docker镜像
- **服务推断**：识别项目依赖的外部服务和中间件
- **Docker Compose配置生成**：生成包含所有必要服务的docker-compose.yml文件

## 系统架构

系统由多个协作的AI代理组成，每个代理专注于特定任务：

### Dockerfile生成流程
1. **dockerfile_generator**：分析项目构建产物，生成适当的Dockerfile
   - 自动识别合适的基础镜像
   - 配置正确的工作目录和COPY指令
   - 设置适当的ENTRYPOINT/CMD
   - 在指定构建上下文目录创建Dockerfile

### Docker Compose生成流程
1. **service_analyzer**：分析项目依赖的外部服务，生成服务配置
   - 将服务名称映射到Docker镜像
   - 配置环境变量、端口映射和卷挂载
2. **network_configurator**：设计容器网络结构
   - 配置服务间的网络依赖关系
   - 确保主应用能够访问所有依赖服务
3. **compose_integrator**：整合所有配置，生成完整的docker-compose.yml

## CrewAI Flow可视化

项目根目录下的`crewai_flow.html`文件提供了完整工作流的可视化展示：

- 直观展示代理之间的协作关系
- 显示任务执行顺序和数据流
- 帮助理解系统工作机制和调试潜在问题

打开`crewai_flow.html`文件，您可以看到整个工作流的图形化表示，包括每个代理、任务及其关系。

## 安装与使用

### 前提条件
- Python 3.8+
- Docker和Docker Compose
- OpenAI API密钥（用于CrewAI代理）

### 安装
```bash
# 克隆仓库
git clone https://github.com/yourusername/docker_compose_generator.git
cd docker_compose_generator

# 安装依赖
pip install -r requirements.txt
```

### 配置
在项目根目录创建一个`.env`文件，填入以下配置信息：

```
# OpenAI API配置
OPENAI_API_KEY=your_api_key_here

# 项目配置
PROJECT_NAME=your_project_name
PROJECT_PATH=/path/to/your/project
ARTIFACT_PATH=/path/to/your/artifact
```

### 使用方法

#### 使用.env文件配置
最简单的使用方式是在`.env`文件中填入相应信息，然后运行主程序：

```bash
python -m src.docker_compose_generator.main
```

程序会根据CrewAI工作流自动读取配置并按以下步骤执行：
1. 分析项目结构和依赖
2. 推断所需的外部服务和中间件
3. 生成Dockerfile并构建镜像
4. 生成完整的docker-compose.yml文件

#### 编程方式使用

##### 生成Dockerfile和构建镜像
```python
from docker_compose_generator.crews import DockerfileGenerator
from crewai import CrewOutput

# 提供项目分析结果和构建产物路径
result = DockerfileGenerator().crew().kickoff(
    inputs={
        "project_analysis_results": project_analysis_json,
        "artifact_path": "/path/to/your/artifact.jar",
    }
)

# 获取构建上下文路径和Dockerfile内容
build_context_path = result.pydantic.model_dump().get('build_context_path')
dockerfile_content = result.pydantic.model_dump().get('dockerfile_content')
```

##### 生成Docker Compose配置
```python
from docker_compose_generator.crews import ComposeGenerator
from crewai import CrewOutput

# 提供项目依赖分析、服务推断结果和主项目镜像名
result = ComposeGenerator().crew().kickoff(
    inputs={
        "dependencies_analysis": dependencies_analysis_json,
        "service_inference_res": service_inference_json,
        "single_project_image_name": "your-project:1.0"
    }
)

# 获取生成的docker-compose内容
docker_compose_content = result.pydantic.model_dump().get('docker_compose_content')
```

## 项目结构

```
src/docker_compose_generator/
├── __init__.py
├── main.py             # 主入口文件
├── utils/              # 工具函数
│   ├── __init__.py
│   └── docker_build.py # Docker构建工具
├── tools/              # CrewAI工具
│   ├── __init__.py
│   └── project_file_list_tool.py
└── crews/              # CrewAI代理和任务
    ├── __init__.py
    ├── project_reader/         # 项目分析代理
    │   ├── __init__.py
    │   ├── project_reader.py
    │   └── config/
    │       ├── agents.yaml     # 代理配置
    │       └── tasks.yaml      # 任务配置
    ├── service_inference/      # 服务推断代理
    │   ├── __init__.py
    │   ├── service_inference.py
    │   └── config/
    │       ├── agents.yaml
    │       └── tasks.yaml
    ├── dockerfile_generator/   # Dockerfile生成代理
    │   ├── __init__.py
    │   ├── dockerfile_generator.py
    │   └── config/
    │       ├── agents.yaml
    │       └── tasks.yaml
    └── compose_generator/      # Compose生成代理
        ├── __init__.py
        ├── compose_generator.py
        └── config/
            ├── agents.yaml
            └── tasks.yaml
```

## 工作流程

本项目基于CrewAI的顺序工作流模式(Process.sequential)，按照以下步骤执行：

1. **项目分析**：分析项目结构和依赖，识别项目类型和运行环境
2. **服务推断**：根据项目依赖识别所需的外部服务和中间件
3. **Dockerfile生成**：为项目构建产物生成Dockerfile
4. **Docker镜像构建**：在正确的构建上下文中构建Docker镜像
5. **Docker Compose生成**：生成包含所有必要服务的docker-compose.yml

整个工作流程可以通过项目根目录下的`crewai_flow.html`可视化查看。

## 核心代理与任务

每个CrewAI代理都有特定的角色和任务：

1. **dockerfile_generator**
   - 角色：Dockerfile工程师
   - 任务：根据构建产物生成优化的Dockerfile

2. **service_analyzer**
   - 角色：外部服务与中间件分析专家
   - 任务：将项目依赖服务转换为docker-compose配置

3. **network_configurator**
   - 角色：Docker网络配置专家
   - 任务：设计容器网络结构

4. **compose_integrator**
   - 角色：Docker Compose集成专家
   - 任务：整合所有服务配置，生成完整的docker-compose.yml

## 示例输出

### 生成的Dockerfile示例
```dockerfile
# 构建上下文目录: /path/to/project
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/my-app.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 生成的docker-compose.yml示例
```yaml
version: '3.8'

services:
  app:
    image: my-project:1.0
    ports:
      - "8080:8080"
    environment:
      - SPRING_DATASOURCE_URL=jdbc:mysql://mysql:3306/mydb
      - SPRING_REDIS_HOST=redis
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy

  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=mydb
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6.2
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  mysql_data:
  redis_data:

networks:
  default:
    name: my-project-network
```

## 自定义与扩展

您可以通过修改`crews`目录下的配置文件来自定义代理行为：

- `agents.yaml`：定义代理角色、目标和背景故事
- `tasks.yaml`：定义任务描述和预期输出

要添加新的代理或任务，只需创建相应的配置文件并在相应的Python类中引用它们。


