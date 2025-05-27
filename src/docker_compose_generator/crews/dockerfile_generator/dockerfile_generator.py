from pathlib import Path
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, FileWriterTool, DirectoryReadTool, FileReadTool, TXTSearchTool
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field

from typing import List

class DockerfileResult(BaseModel):
    dockerfile_content: str = Field(description="Dockerfile 内容")
    build_context_path: str = Field(description="build context 目录, 路径不要包含Dockerfile文件名, 以文件路径分隔符结尾")

knowledge_path = (Path(__file__).resolve().parent / ".." / "knowledge" / "DockerfileBestPracticesAndExamples.txt").resolve()

rag_tool = TXTSearchTool(txt=str(knowledge_path))

@CrewBase
class DockerfileGenerator():
    """Dockerfile generation crew"""

    agents: List[BaseAgent]
    tasks: List[Task]


    @agent
    def dockerfile_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['dockerfile_generator'], # type: ignore[index]
            verbose=True,
            tools=[DirectoryReadTool(), FileWriterTool(), FileReadTool(), SerperDevTool(), rag_tool],
        )
    

    @task
    def dockerfile_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['dockerfile_generation_task'], # type: ignore[index]
            output_file=r"output/Dockerfile_result.txt",
            output_pydantic=DockerfileResult
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
