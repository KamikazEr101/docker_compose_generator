#!/usr/bin/env python

import os
from crewai import CrewOutput
from time import time
from pydantic import BaseModel
from crewai.flow import Flow, listen, start, persist, and_
from crews import ProjectReader, ServiceInference, DockerfileGenerator, ComposeGenerator
from utils import build_docker_image
from contants import preset_dependencies_analysis, preset_service_inference
from dotenv import load_dotenv

load_dotenv()

class AnalysisState(BaseModel):
    """Analysis state model"""
    project_name: str = "project_" + str(int(time()))[5:]
    project_path: str = ""
    artifact_path: str = ""
    project_files_path: str = ""
    dependencies_analysis: str = ""
    service_inference_res: str = ""
    single_project_image_name: str = ""
    
class AnalysisFlow(Flow[AnalysisState]):
    """Analysis flow for project analysis"""
    
    @start()
    def initialize_state(self):
        """Initializes the flow"""
        self.state.project_path = os.getenv("PROJECT_PATH")
        self.state.artifact_path = os.getenv("ARTIFACT_PATH")
        self.state.project_name = os.getenv("PROJECT_NAME")
        return "initialize_state completed"
    
    @persist(verbose=False)
    @listen(initialize_state)
    def read_project_structure(self, _):
        """Reads the project structure"""
        dependencies_analysis: CrewOutput = ProjectReader().crew().kickoff(inputs={"project_path": self.state.project_path})

        self.state.dependencies_analysis = dependencies_analysis.raw
        
        with open("output/project_file_list.txt", "r", encoding="utf-8") as f:
            project_files_content = f.read()
            self.state.project_files_path = project_files_content

        return "read_project_structure completed"

    @listen(read_project_structure)
    def service_inference(self, _):
        """Infers services from the project structure"""
        service_inference_res = ServiceInference().crew().kickoff(
            inputs={
                "project_files_path": self.state.project_files_path,
                "dependencies_analysis": self.state.dependencies_analysis,
                }
            )
        self.state.service_inference_res = service_inference_res.raw
        
        return "service_inference completed"
    
    @listen(read_project_structure)
    def image_builder(self, _):
        """Builds the docker image"""
        dockerfile_result: CrewOutput = DockerfileGenerator().crew().kickoff(
            inputs={
                "project_analysis_results": self.state.dependencies_analysis,
                "artifact_path": self.state.artifact_path,
                }
            )
        
        # 获取构建上下文路径
        build_context_path = dockerfile_result.pydantic.model_dump().get('build_context_path')
        print(f"构建上下文路径: {build_context_path}")
        
        # 构建Docker镜像
        success, output = build_docker_image(
            build_context_path=build_context_path,
            image_name=self.state.project_name,
        )
        
        self.state.single_project_image_name = self.state.project_name + ":latest"
        
        if success:
            print(f"Docker镜像构建成功: {self.state.single_project_image_name}")
        else:
            print(output)
        
        return "image_builder completed"
    
    @listen(and_(image_builder, service_inference))
    def compose_generator(self, _):
        """Generates the docker compose file"""
        compose_generator_result: CrewOutput = ComposeGenerator().crew().kickoff(
            inputs={
                "dependencies_analysis": self.state.dependencies_analysis,
                "service_inference_res": self.state.service_inference_res,
                "single_project_image_name": self.state.single_project_image_name,
                }
            )
        
        return compose_generator_result.raw

def kickoff():
    AnalysisFlow().kickoff()

def plot():
    AnalysisFlow().plot()
    
if __name__ == "__main__":
    res = kickoff()
    
    print("kickoff completed")
    
    plot()
    
