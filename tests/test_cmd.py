import os
import subprocess

build_context_path = r"D:\IdeaProjects\lease\web\web-admin\target"

os.chdir(build_context_path)
        
# 执行构建命令
process = subprocess.run(
    ["dir"],
    shell=True,
    check=False,
    capture_output=True,
    text=True
)

print(process.stdout)