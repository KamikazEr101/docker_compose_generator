import os
from typing import Type, List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from contants.useless_project_file_list import *

class ProjectFileListToolInput(BaseModel):
    """Input schema for ProjectFileListTool."""

    directory: str = Field(..., description="Path to the project directory")


class ProjectFileListTool(BaseTool):
    name: str = "Project File List Tool"
    description: str = (
        "A tool for recursively listing all files in a project directory"
    )
    args_schema: Type[BaseModel] = ProjectFileListToolInput

    def _run(self, directory: str) -> str:
        """
        Recursively reads all files in a project directory
        
        Args:
            directory (str): Path to the project directory
            
        Returns:
            str: Formatted string of file list
        """
        exclude_dirs = ignored_directories
        exclude_files = ignored_files
            
        # Normalize directory path
        if directory.endswith("/") or directory.endswith("\\"):
            directory = directory[:-1]
            
        # Recursively get file list
        files_list = []
        for root, dirs, files in os.walk(directory):
            # Modify dirs in-place to exclude specified directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for filename in files:
                # Check if file should be excluded
                exclude = False
                for pattern in exclude_files:
                    if pattern.startswith('*') and filename.endswith(pattern[1:]):
                        exclude = True
                        break
                    elif filename == pattern:
                        exclude = True
                        break
                
                if not exclude:
                    # Use format similar to DirectoryReadTool
                    rel_path = os.path.join(root, filename).replace(directory, '').lstrip(os.path.sep)
                    rel_path = rel_path.replace('\\', '/')  # Standardize to forward slashes
                    files_list.append(f"{directory}/{rel_path}")
        
        # Sort file list alphabetically
        files_list.sort()
        
        # Format output
        files = "\n- ".join(files_list)
        return f"Project file list: \n- {files}"