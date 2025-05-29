#!/usr/bin/env python

import os
from crewai import CrewOutput
from time import time
from pydantic import BaseModel
from crewai.flow import Flow, listen, start, persist, and_
from crews import ProjectReader, ServiceInference, ImageBuilder, ComposeGenerator
from contants import preset_dependencies_analysis, preset_service_inference
from dotenv import load_dotenv

load_dotenv()

class AnalysisState(BaseModel):
    """Analysis state model"""
    project_name: str = "project_" + str(int(time()))[5:]
    project_path: str = ""
    artifact_path: str = ""
    project_files_path: str = ""
    dependencies_analysis: str = preset_dependencies_analysis
    service_inference_res: str = preset_service_inference
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
        build_result: CrewOutput = ImageBuilder().crew().kickoff(
            inputs={
                "project_analysis_results": self.state.dependencies_analysis,
                "artifact_path": self.state.artifact_path,
                "project_name": self.state.project_name,
                }
        )
        
        result_dict = build_result.pydantic.model_dump()
        if result_dict['success']:
            self.state.single_project_image_name = result_dict['image_name']
            print(f"成功构建镜像: {self.state.single_project_image_name}")
        else:
            print("构建镜像失败")
            print(result_dict['error_message'])
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
    