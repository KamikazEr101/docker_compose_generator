from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool
from crewai.agents.agent_builder.base_agent import BaseAgent

from typing import List

from tools.project_file_list_tool import ProjectFileListTool


@CrewBase
class ProjectReader():
    """ProjectReader crew"""
    
    agents: List[BaseAgent]
    tasks: List[Task]


    @agent
    def project_language_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['project_language_analyst'], # type: ignore[index]
            verbose=True,
            tools=[ProjectFileListTool()]
        )

    @agent
    def project_dependency_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['project_dependency_analyst'], # type: ignore[index]
            verbose=True,
            tools=[FileReadTool()],
        )
        
    @agent
    def project_type_inference_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['project_type_inference_agent'], # type: ignore[index]
            verbose=True,
            tools=[FileReadTool()],
        )
    

    @task
    def project_language_task(self) -> Task:
        return Task(
            config=self.tasks_config['project_language_task'], # type: ignore[index]
        )

    @task
    def project_dependency_task(self) -> Task:
        return Task(
            config=self.tasks_config['project_dependency_task'], # type: ignore[index]
            context=[self.project_language_task()]
        )
    @task
    def project_type_inference_task(self) -> Task:
        return Task(
            config=self.tasks_config['project_type_inference_task'], # type: ignore[index]
            output_file=r'output/dependency_analysis.txt',
            context=[self.project_dependency_task(), self.project_language_task()]
        )
        
        
    @crew
    def crew(self) -> Crew:
        """Creates the ProjectReader crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            name="ProjectReader",
            description="A crew to read the project and analyze its language and dependencies.",
        )

if __name__ == "__main__":
    project_reader = ProjectReader()
    res = project_reader.crew().kickoff(inputs={"project_path": r"D:\IdeaProjects\lease"})

    
    print(res)