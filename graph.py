import os,json,asyncio
from typing import Dict,Any
from dotenv import load_dotenv 
from langchain_deepseek import ChatDeepSeek
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from langchain_tavily import TavilySearch
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_experimental.tools import PythonAstREPLTool
from langchain_openai import ChatOpenAI
import subprocess
import datetime
import MCP_FemResExtract
import MCP_Fig
import EnvConfig
import MCP_Chart
from langchain_mcp_adapters.client import MultiServerMCPClient
env = EnvConfig.EnvConfig()
tools =[]

#飞书工具
def load_servers(file_path: str ="servers_config.json" ) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f).get("mcpServers", {})
async def get_mcp_tools():
    client = MultiServerMCPClient(load_servers())
    tools = await client.get_tools()
    return tools
tools = asyncio.run(get_mcp_tools())



# ✅ 创建提示词模
with open(os.path.join(os.path.dirname(__file__),"prompt.txt"),'r',encoding="utf-8") as f:
    prompt = f.read()





# ✅ 创建模型
# model = ChatDeepSeek(model="deepseek-chat")
model = ChatOpenAI(
   model_name=env.li_model_v3,
   api_key=env.li_api_key,
   base_url=env.li_api_URL_v3,
   )

# model = ChatOpenAI(
#    model_name=env.li_model_r1,
#    api_key=env.li_api_key,
#    base_url=env.li_api_URL_r1,
#    )

# model = ChatOpenAI(
#    model_name=env.li_model_qwen,
#    api_key=env.li_api_key,
#    base_url=env.li_api_URL_qwen,
#    )

#内置sql工具
db = SQLDatabase.from_uri(f"mysql+pymysql://{env.user}:{env.password}@{env.host}:{env.port}/{env.database}")
tools.extend(SQLDatabaseToolkit(db=db, llm=model).get_tools())
#内置python解释器
# tools.append(PythonAstREPLTool())
# 内置搜索工具
# tools.append(TavilySearch(max_results=5, topic="general",tavily_api_key=env.TAVILY_API_KEY))
#内置文件处理工具
# tools.append(FileManagementToolkit(root_dir=env.manage_root_path).get_tools()[2])

#绘图工具
# tools.extend(MCP_Fig.get_mcp_tools())
#有限元结果查询工具
tools.extend(MCP_FemResExtract.get_mcp_tools())

#查看工具
for i in tools:
     print(i.name)
    #  print(i.description)
     print("_"*20)




# ✅ 创建图 （Agent）
graph = create_react_agent(model=model, tools=tools, prompt=prompt)

# # 测试大模型调用
# inputs = {"messages": [{"role": "user", "content": "你好"}]}
# # 打印输入，确认没有多余字段
# print("输入消息:", inputs)
# response = graph.invoke(inputs)
# print(response)