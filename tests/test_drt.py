from tools.custom_tool import ProjectFileListTool

tool = ProjectFileListTool()

res = tool.run(
    directory=r"D:\IdeaProjects\lease",
)

with open("file_list.txt", "w") as f:
    f.write(res)