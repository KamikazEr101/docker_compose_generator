from typing import Type, Tuple
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import os
import subprocess

class DockerBuildToolInput(BaseModel):
    '''Input schema for DockerBuildTool.'''

    build_context_path: str = Field(..., description="Path to the Dockerfile build context directory")
    image_name: str = Field(..., description="Name of the Docker image")
    image_tag: str = Field("latest", description="Tag for the Docker image, defaults to 'latest'")
    no_cache: bool = Field(True, description="Whether to disable cache during build, defaults to True")

class DockerBuildTool(BaseTool):
    name: str = "Docker Build Tool"
    description: str = "A tool to build Docker images."
    args_schema: Type[BaseModel] = DockerBuildToolInput

    def _run(
        self,
        build_context_path: str,
        image_name: str,
        image_tag: str = "latest",
        no_cache: bool = True
    ) -> Tuple[bool, str]:
        '''
        Builds a Docker image.

        Args:
            build_context_path: Path to the Dockerfile build context directory.
            image_name: Name of the Docker image.
            image_tag: Tag for the Docker image, defaults to 'latest'.
            no_cache: Whether to disable cache during build, defaults to True.

        Returns:
            Tuple[bool, str]: (Success status, output message or error message)
        '''
        cmd = ["docker", "build", "-t", f"{image_name}:{image_tag}"]

        if no_cache:
            cmd.append("--no-cache")

        cmd.append(".")

        original_dir = os.getcwd()

        try:
            os.chdir(build_context_path)
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
            success = process.returncode == 0
            if success:
                return True, process.stdout
            else:
                return False, process.stderr
        except Exception as e:
            return False, str(e)
        finally:
            os.chdir(original_dir) 