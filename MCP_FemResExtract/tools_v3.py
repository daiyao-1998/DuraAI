from langchain.tools import StructuredTool
from .core import MCPToolKit
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Union, Tuple, Any

# 创建 MCPToolKit 实例
mcp_toolkit = MCPToolKit()


# 定义输入参数模型 - 包含file_category_map的基础模型
class FileCategoryMapInput(BaseModel):
    file_category_map: Dict[str, Dict[str, str]] = Field(
        description="字典，键为文件标识，值为包含'result_file'（结果文件路径）和'result_category'（结果类型）的字典"
    )


class GetAllNodeResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Mises', 'Strain', 'PlasticStrain', 'Displacement'）")


class GetMultiNodeResultsInput(FileCategoryMapInput):
    ids_per_case: Optional[Dict[int, List[int]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的节点ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的节点名称列表")
    query: str = Field(description="从日志文件中提取相关信息的查询需求，必须填写")


class GetAllElementResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（ 'Mises', 'Strain', 'PlasticStrain', 'Displacement'）")


class GetMultiElementResultsInput(FileCategoryMapInput):
    ids_per_case: Optional[Dict[int, List[int]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的单元ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的单元名称列表")
    query: str = Field(description="从日志文件中提取相关信息的查询需求，必须填写")


class GetMultiPartResultsInput(FileCategoryMapInput):
    ids_per_case: Optional[Dict[int, List[int]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的属性ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的属性名称列表")
    query: str = Field(description="从日志文件中提取相关信息的查询需求，必须填写")


class GetMultiMaterialResultsInput(FileCategoryMapInput):
    ids_per_case: Optional[Dict[int, List[int]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的材料ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的材料名称列表")
    query: str = Field(description="从日志文件中提取相关信息的查询需求，必须填写")


class GetMultiSetResultsInput(FileCategoryMapInput):
    ids_per_case: Optional[Dict[int, List[int]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的集合ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的集合名称列表（如LAC-51010131）")
    query: str = Field(description="从日志文件中提取相关信息的查询需求，必须填写")


class GetModelInfoInput(BaseModel):
    file_info_map: Dict[str, Dict[str, Any]] = Field(
        description="字典，键为文件标识，值为包含'result_file'、'info_types'（列表）和'result_category'的字典"
    )
    ids_per_case: Optional[Dict[int, List[int]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的实体ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的实体名称列表")
    query: str = Field(description="从日志文件中提取相关信息的查询需求，必须填写")


class GetMaxResultForEntitiesInput(FileCategoryMapInput):
    """获取指定实体最大结果的输入参数"""
    entity_type: str = Field(description="实体类型（'material', 'property', 'ansapart'）")
    ids_per_case: Optional[Dict[int, List[int]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的实体ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的实体名称列表")
    node_or_element_result: str = Field(default="node", description="结果类型（'node'或'element'，默认'node'）")
    query: str = Field(description="从日志文件中提取相关信息的查询需求，必须填写")


class CaptureScreenshotsInput(BaseModel):
    """截取云图的输入参数"""
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    entity_type: str = Field(description="实体类型（'material', 'property', 'ansapart'）")
    ids_per_case: Optional[Dict[int, List[int]]] = Field(
        default=None, 
        description="字典，键为工况ID，值为该工况下的实体ID列表（通过ID指定实体时使用）"
    )
    names_per_case: Optional[Dict[int, List[str]]] = Field(
        default=None, 
        description="字典，键为工况ID，值为该工况下的实体名称列表（通过名称指定实体时使用）"
    )
    output_dir: str = Field(
        default="/home/chehejia/agent-chat-ui-main/public/images", 
        description="截图输出目录（默认使用预设路径，可按需修改）"
    )
    node_or_element_result: str = Field(
        default="node", 
        description="云图显示结果类型（'node'表示节点结果，'element'表示单元结果，默认'node'）"
    )
    query: Optional[str] = Field(
        default=None, 
        description="查询需求描述，用于从日志中提取与截图相关的辅助信息（非必需，可省略）"
    )


def get_mcp_tools() -> list:
    """获取所有MCP工具列表，用于LangChain工具调用"""
    return [
        # 获取所有节点结果并生成CSV
        StructuredTool.from_function(
            func=mcp_toolkit.get_all_node_results,
            name="get_all_node_results",
            description=(
                "获取所有工况下所有节点结果并输出到CSV文件(输出Mises/Strain/PlasticStrain类型的结果时会自动输出节点位移结果)\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "返回:\n"
                "CSV文件路径和字段描述的元组"
            ),
            args_schema=GetAllNodeResultsInput
        ),
        
        # 获取单个或者多个节点结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_multi_node_results,
            name="get_multi_node_results",
            description=(
                "获取单个或者多个节点在指定一个或多个工况下的结果，支持多文件多结果类型批量查询\n"
                "参数:\n"
                "- file_category_map: 字典，键为文件标识，值为包含'result_file'和'result_category'的字典\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的节点ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的节点名称列表（可选）\n"
                "- query: 查询需求，用于从结果中提取相关信息（必须填写）\n"
                "示例:\n"
                "file_category_map = {\n"
                "    'file1': {'result_file': 'model1.h3d', 'result_category': 'Mises'},\n"
                "    'file2': {'result_file': 'model2.odb', 'result_category': 'Displacement'}\n"
                "}\n"
                "返回:\n"
                "结果查询日志文件内容，包含各工况的查询结果"
            ),
            args_schema=GetMultiNodeResultsInput
        ),
        
        # 获取所有单元结果并生成CSV
        StructuredTool.from_function(
            func=mcp_toolkit.get_all_element_results,
            name="get_all_element_results",
            description=(
                "获取所有工况下所有单元结果并输出到CSV文件\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "返回:\n"
                "CSV文件路径和字段描述的元组"
            ),
            args_schema=GetAllElementResultsInput
        ),
        
        # 获取单个或者多个单元结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_multi_element_results,
            name="get_multi_element_results",
            description=(
                "获取单个或者多个单元在指定一个或多个工况下的结果，支持多文件多结果类型批量查询\n"
                "参数:\n"
                "- file_category_map: 字典，键为文件标识，值为包含'result_file'和'result_category'的字典\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的单元ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的单元名称列表（可选）\n"
                "- query: 查询需求，用于从结果中提取相关信息（必须填写）\n"
                "返回:\n"
                "结果查询日志文件内容，包含各工况的查询结果"
            ),
            args_schema=GetMultiElementResultsInput
        ),
        
        # 获取多个部件结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_multi_part_results,
            name="get_multi_part_results",
            description=(
                "获取单个或者多个属性在指定一个或多个工况下的结果，支持多文件多结果类型批量查询\n"
                "参数:\n"
                "- file_category_map: 字典，键为文件标识，值为包含'result_file'和'result_category'的字典\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的属性ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的属性名称列表（可选）\n"
                "- query: 查询需求，用于从结果中提取相关信息（必须填写）\n"
                "返回:\n"
                "结果查询日志文件内容，包含各工况的查询结果"
            ),
            args_schema=GetMultiPartResultsInput
        ),
        
        # 获取多种材料结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_multi_material_results,
            name="get_multi_material_results",
            description=(
                "获取单种或者多种材料在指定一个或多个工况下的结果，支持多文件多结果类型批量查询\n"
                "参数:\n"
                "- file_category_map: 字典，键为文件标识，值为包含'result_file'和'result_category'的字典\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的材料ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的材料名称列表（可选）\n"
                "- query: 查询需求，用于从结果中提取相关信息（必须填写）\n"
                "返回:\n"
                "结果查询日志文件内容，包含各工况的查询结果"
            ),
            args_schema=GetMultiMaterialResultsInput
        ),
        
        # 获取多个集合结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_multi_set_results,
            name="get_multi_set_results",
            description=(
                "获取单个或者多个集合在指定一个或多个工况下的结果，支持多文件多结果类型批量查询\n"
                "参数:\n"
                "- file_category_map: 字典，键为文件标识，值为包含'result_file'和'result_category'的字典\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的集合ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的集合名称列表（可选）\n"
                "- query: 查询需求，用于从结果中提取相关信息（必须填写）\n"
                "返回:\n"
                "结果查询日志文件内容，包含各工况的查询结果"
            ),
            args_schema=GetMultiSetResultsInput
        ),
        
        # 获取模型信息
        StructuredTool.from_function(
            func=mcp_toolkit.get_model_info,
            name="get_model_info",
            description=(
                "获取模型未加载状态下的信息（载荷、约束、零件、属性、材料、集合等），支持多文件查询\n"
                "参数:\n"
                "- file_info_map: 字典，键为文件标识，值为包含'result_file'、'info_types'（列表）和'result_category'的字典\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的实体ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的实体名称列表（可选）\n"
                "- query: 查询需求，用于从日志文件中提取相关信息（必须填写）\n"
                "返回:\n"
                "模型信息查询日志文件内容，包含查询结果"
            ),
            args_schema=GetModelInfoInput
        ),
        
        # 获取指定实体的最大结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_max_result_for_entities,
            name="get_max_result_for_entities",
            description=(
                "获取指定单个或者多个实体（材料/属性/部件）的最大节点或单元结果，支持多文件多结果类型批量查询\n"
                "参数:\n"
                "- file_category_map: 字典，键为文件标识，值为包含'result_file'和'result_category'的字典\n"
                "- entity_type: 实体类型（'material', 'property', 'ansapart'）\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的实体ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的实体名称列表（可选）\n"
                "- node_or_element_result: 结果类型（'node'或'element'，默认'node'）\n"
                "- query: 查询需求，用于从结果中提取相关信息（必须填写）\n"
                "返回:\n"
                "结果查询日志文件内容，包含最大结果信息"
            ),
            args_schema=GetMaxResultForEntitiesInput
        ),
        
        # 截取云图
        StructuredTool.from_function(
            func=mcp_toolkit.capture_screenshots,
            name="capture_screenshots",
            description=(
                "多方位截取指定单个或多个实体的最大节点/单元结果云图\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "- entity_type: 实体类型（'material', 'property', 'ansapart'）\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的实体ID列表（通过ID指定实体时使用）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的实体名称列表（通过名称指定实体时使用）\n"
                "- output_dir: 截图输出目录（默认使用预设路径，可按需修改）\n"
                "- node_or_element_result: 云图显示结果类型（'node'表示节点结果，'element'表示单元结果，默认'node'）\n"
                "- query: 查询需求描述，用于从日志中提取与截图相关的辅助信息（非必需，可省略）\n"
                "返回:\n"
                "HTML格式的截图集合，包含每个工况的多角度视图"
            ),
            args_schema=CaptureScreenshotsInput
        ),
    ]


if __name__ == "__main__":
    # 简单测试工具列表是否能正确生成
    tools = get_mcp_tools()
    print(f"生成了 {len(tools)} 个MCP工具")
    for tool in tools:
        print(f"- {tool.name}: {tool.description[:80]}...")
    