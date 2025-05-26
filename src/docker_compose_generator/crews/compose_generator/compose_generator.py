from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from typing import List
from pydantic import BaseModel, Field

class DockerComposeResult(BaseModel):
    """Docker Compose生成结果"""
    docker_compose_content: str = Field(description="完整的docker-compose.yml文件内容")


@CrewBase
class ComposeGenerator():
    """ComposeGenerator crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    
    @agent
    def service_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['service_analyzer'], # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool()],
        )

    @agent
    def network_configurator(self) -> Agent:
        return Agent(
            config=self.agents_config['network_configurator'], # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool()],
        )
        
    @agent
    def compose_integrator(self) -> Agent:
        return Agent(
            config=self.agents_config['compose_integrator'], # type: ignore[index]
            verbose=True,
        )

    
    @task
    def service_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['service_analysis_task'], # type: ignore[index]
        )

    @task
    def network_configuration_task(self) -> Task:
        return Task(
            config=self.tasks_config['network_configuration_task'], # type: ignore[index]
            context=[self.service_analysis_task()],
        )
        
    @task
    def compose_integration_task(self) -> Task:
        return Task(
            config=self.tasks_config['compose_integration_task'], # type: ignore[index]
            context=[self.service_analysis_task(), self.network_configuration_task()],
            output_file='output/docker-compose.yml',
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ComposeGenerator crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            name='compose_generator_crew', # type: ignore[index]
            description='Crew for generating Docker Compose files' # type: ignore[index]
        )
