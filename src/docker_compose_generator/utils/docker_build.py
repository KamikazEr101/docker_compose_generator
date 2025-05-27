import os
import subprocess
from typing import Optional, Dict, Tuple

def build_docker_image(
    build_context_path: str, 
    image_name: str,
    image_tag: str = "latest",
    no_cache: bool = False
) -> Tuple[bool, str]:
    """
    构建Docker镜像
    
    Args:
        build_context_path: Dockerfile所在的构建上下文目录路径
        image_name: 镜像名称
        image_tag: 镜像标签，默认为latest
        no_cache: 是否禁用缓存
        
    Returns:
        Tuple[bool, str]: (是否成功, 输出信息)
    """
    # 构建docker build命令
    cmd = ["docker", "build", ".", "-t", f"{image_name}:{image_tag}"]
    
    # 是否禁用缓存
    if no_cache:
        cmd.append("--no-cache")
    
    # 添加当前目录作为构建上下文
    cmd.append(".")
    
    # 记录完整命令
    cmd_str = " ".join(cmd)
    
    # 保存当前目录
    original_dir = os.getcwd()
    
    try:
        # 切换到构建上下文目录
        os.chdir(build_context_path)
        
        # 执行构建命令
        process = subprocess.run(
            cmd,
            shell=True,
            check=False,
            capture_output=True,
            text=True
        )
        
        # 判断是否成功
        success = process.returncode == 0
        
        return success
        
    except Exception as e:
        return False, str(e)
        
    finally:
        # 切回原始目录
        os.chdir(original_dir) 