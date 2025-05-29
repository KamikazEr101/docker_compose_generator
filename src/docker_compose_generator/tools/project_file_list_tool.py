import os
from typing import Type, List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from contants import *

PROJECT_FILES = ""

# 添加安全读取文件的函数
def safe_read_file(file_path):
    """
    尝试用不同编码安全地读取文件
    """
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'latin1', 'iso-8859-1', 'gbk', 'ascii']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    # 如果所有编码都失败，尝试以二进制模式读取
    try:
        with open(file_path, 'rb') as f:
            return "[二进制文件，无法显示内容]"
    except Exception as e:
        return f"Error reading file: {str(e)}"

# 保持原有的其他代码不变...

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
        global PROJECT_FILES
        
        exclude_dirs = ignored_directories
        exclude_files = ignored_files
            
        if directory.endswith("/") or directory.endswith("\\"):
            directory = directory[:-1]
            
        files_list = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for filename in files:
                exclude = False
                for pattern in exclude_files:
                    if pattern.startswith('*') and filename.endswith(pattern[1:]):
                        exclude = True
                        break
                    elif filename == pattern:
                        exclude = True
                        break
                
                if not exclude:
                    rel_path = os.path.join(root, filename).replace(directory, '').lstrip(os.path.sep)
                    rel_path = rel_path.replace('\\', '/')
                    files_list.append(f"{directory}/{rel_path}")
        
        files_list.sort()
        
        result = "Project file list: \n- " + "\n- ".join(files_list)
        PROJECT_FILES = result

        if not os.path.exists("output"):
            os.makedirs("output")
        if not os.path.exists("output/project_file_list.txt"):
            with open("output/project_file_list.txt", "w", encoding="utf-8") as f:
                f.write(result)
        return result