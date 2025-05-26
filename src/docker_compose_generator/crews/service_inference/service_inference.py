from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool, SerperDevTool
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class ServiceInference():
    """ServiceInference crew"""

    agents: List[BaseAgent]
    tasks: List[Task]


    @agent
    def service_inference_database_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['service_inference_database_agent'], # type: ignore[index]
            verbose=True,
            tools=[FileReadTool()]
        )
    
    @agent
    def service_inference_message_queue_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['service_inference_message_queue_agent'], # type: ignore[index]
            verbose=True,
            tools=[FileReadTool()]
        )
        
    @agent
    def service_inference_cache_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['service_inference_cache_agent'], # type: ignore[index]
            verbose=True,
            tools=[FileReadTool(), SerperDevTool()]
        )

    @agent
    def service_inference_custom_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['service_inference_custom_agent'], # type: ignore[index]
            verbose=True,
            tools=[FileReadTool()]
        )
        
    @agent
    def conclusion_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['conclusion_agent'], # type: ignore[index]
            verbose=True,
        )


    @task
    def service_inference_database_task(self) -> Task:
        return Task(
            config=self.tasks_config['service_inference_database_task'], # type: ignore[index]
        )
    
    @task
    def service_inference_message_queue_task(self) -> Task:
        return Task(
            config=self.tasks_config['service_inference_message_queue_task'], # type: ignore[index]
        )
        
    @task
    def service_inference_cache_task(self) -> Task:
        return Task(
            config=self.tasks_config['service_inference_cache_task'], # type: ignore[index]
        )
        
    @task
    def service_inference_custom_task(self) -> Task:
        return Task(
            config=self.tasks_config['service_inference_custom_task'], # type: ignore[index]
        )
    
    @task
    def conclusion_task(self) -> Task:
        return Task(
            config=self.tasks_config['conclusion_task'], # type: ignore[index]
            context=[self.service_inference_database_task(), self.service_inference_message_queue_task(), self.service_inference_cache_task(), self.service_inference_custom_task()],
            output_file=r'output/service_inference.txt'
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the ServiceInference crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential,
            name="ServiceInference", # type: ignore[index]
            description="A crew for inferring services from a codebase."
        )
