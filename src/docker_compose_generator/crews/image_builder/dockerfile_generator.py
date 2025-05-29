from pathlib import Path
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, FileWriterTool, DirectoryReadTool, FileReadTool, TXTSearchTool
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field

from typing import List

from tools import DockerBuildTool

class DockerfileResult(BaseModel):
    dockerfile_content: str = Field(description="Dockerfile 内容")
    build_context_path: str = Field(description="build context 目录, 路径不要包含Dockerfile文件名, 以文件路径分隔符结尾")

class ImageBuildResult(BaseModel):
    image_name: str = Field(description="镜像名称")
    success: bool = Field(description="构建是否成功")
    error_message: str = Field(description="构建失败时的错误信息")

knowledge_path = (Path(__file__).resolve().parent / ".." / "knowledge" / "DockerfileBestPracticesAndExamples.txt").resolve()

rag_tool = TXTSearchTool(txt=str(knowledge_path))

@CrewBase
class ImageBuilder():
    """Dockerfile generation and image building crew"""

    agents: List[BaseAgent]
    tasks: List[Task]


    @agent
    def dockerfile_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['dockerfile_generator'], # type: ignore[index]
            verbose=True,
            tools=[DirectoryReadTool(), FileWriterTool(), FileReadTool(), SerperDevTool(), rag_tool],
        )
    
    @agent
    def docker_build_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['docker_build_agent'], # type: ignore[index]
            verbose=True,
            tools=[DockerBuildTool()],
        )

    @task
    def dockerfile_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['dockerfile_generation_task'], # type: ignore[index]
            output_file=r"output/Dockerfile_result.txt",
            output_pydantic=DockerfileResult,
            markdown=False
        )
        
    @task
    def docker_build_task(self) -> Task:
        return Task(
            config=self.tasks_config['docker_build_task'], # type: ignore[index]
            context=[self.dockerfile_generation_task()],
            output_pydantic=ImageBuildResult,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Dockerfile generation crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            name='dockerfile_generator_crew', # type: ignore[index]
            description='Crew for generating Dockerfiles' # type: ignore[index]
        )
