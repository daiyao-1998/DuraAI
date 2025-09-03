from langchain.tools import StructuredTool
from .core import MCPToolKit
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Union, Tuple

# 创建 MCPToolKit 实例
mcp_toolkit = MCPToolKit()


# 定义输入参数模型
class GetAllNodeResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Mises', 'Strain', 'PlasticStrain'）")


class GetSingleNodeResultInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    case_ids: Union[int, List[int]] = Field(default=3, description="工况ID或工况ID列表（默认3）")
    node_id: int = Field(description="节点ID")
    query: str = Field(description="从日志文件中提取相关信息的查询需求")


class GetMultiNodeResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    case_ids: Union[int, List[int]] = Field(default=3, description="工况ID或工况ID列表（默认3）")
    node_ids: List[int] = Field(description="节点ID列表，例如[288, 296, 302]")
    query: str = Field(description="从日志文件中提取相关信息的查询需求")


class GetAllElementResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（ 'Mises', 'Strain', 'PlasticStrain'）")


class GetSingleElementResultInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    case_ids: Union[int, List[int]] = Field(description="工况ID或工况ID列表")
    element_id: int = Field(description="单元ID")
    query: str = Field(description="从日志文件中提取相关信息的查询需求")


class GetMultiElementResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    case_ids: Union[int, List[int]] = Field( description="工况ID或工况ID列表")
    element_ids: List[int] = Field(description="单元ID列表，例如[101, 102, 103]")
    query: str = Field(description="从日志文件中提取相关信息的查询需求")


class GetMultiPartResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    case_ids: Union[int, List[int]] = Field( description="工况ID或工况ID列表")
    part_ids: List[int] = Field(description="属性ID列表，例如[5, 6, 7]")
    query: str = Field(description="从日志文件中提取相关信息的查询需求")


class GetMultiMaterialResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    case_ids: Union[int, List[int]] = Field(description="工况ID或工况ID列表")
    material_ids: List[int] = Field(description="材料ID列表，例如[1, 2, 3]")
    query: str = Field(description="从日志文件中提取相关信息的查询需求")



class GetModelInfoInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    info_type: str = Field(description="信息类型（'loads', 'spc', 'ansapart', 'property', 'material', 'set'）")
    result_category: str = Field(default="Mises", description="结果类型（默认'Mises'，仅用于设置）")
    case_ids: Union[int, List[int]] = Field(description="工况ID或工况ID列表（0表示不指定工况，为模型原始状态）")
    query: str = Field(description="从日志文件中提取相关信息的查询需求")


class GetModelInfoInputByNames(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    info_type: str = Field(description="信息类型（'loads', 'spc', 'ansapart', 'property', 'material', 'set'）")
    result_category: str = Field(default="Mises", description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    case_ids: Union[int, List[int]] = Field(description="工况ID或工况ID列表（0表示不指定工况，为模型原始状态）")
    names: list = Field(default=None, description="名称列表（默认None，表示获取所有）")
    query: str = Field(description="查询需求，用于从结果中提取相关信息")


class GetMaxResultForEntitiesInput(BaseModel):
    """获取指定实体最大结果的输入参数"""
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    entity_type: str = Field(description="实体类型（'material', 'property', 'ansapart'）")
    entity_ids: List[int] = Field(default=None, description="实体ID列表")
    entity_names: List[str] = Field(default=None, description="实体名称列表")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    case_ids: Union[int, List[int]] = Field(description="工况ID或工况ID列表（0表示不指定工况，为模型原始状态）")
    query: str = Field(description="查询需求，用于从结果中提取相关信息")


class CaptureScreenshotsInput(BaseModel):
    """截取云图的输入参数"""
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    entity_type: str = Field(description="实体类型（'material', 'property', 'ansapart'）")
    entity_ids: List[int] = Field(default=None, description="实体ID列表")
    entity_names: List[str] = Field(default=None, description="实体名称列表")
    output_dir: str = Field(default="/home/chehejia/agent-chat-ui-main/public/images", description="输出目录")
    case_ids: Union[int, List[int]] = Field(description="工况ID或工况ID列表（0表示不指定工况，为模型原始状态）")


def get_mcp_tools() -> list:
    """获取所有MCP工具列表，用于LangChain工具调用"""
    return [
        # 获取所有节点结果并生成CSV
        StructuredTool.from_function(
            func=lambda result_file, result_category: 
                (lambda path, desc: f"CSV文件路径: {path}\n字段描述: {desc}")
                (*mcp_toolkit.get_all_node_results(result_file, result_category)),
            name="get_all_node_results",
            description=(
                "获取所有工况下所有节点结果并输出到CSV文件(输出Mises/Strain/PlasticStrain类型的结果时会自动输出节点位移结果)\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "返回:\n"
                "CSV文件路径和字段描述的格式化字符串"
            ),
            args_schema=GetAllNodeResultsInput
        ),
        
        # 获取单个节点结果
        # StructuredTool.from_function(
        #     func=mcp_toolkit.get_single_node_result,
        #     name="get_single_node_result",
        #     description=(
        #         "获取单个节点在指定一个或多个工况下的结果\n"
        #         "参数:\n"
        #         "- result_file: 结果文件路径（.h3d或.odb）\n"
        #         "- result_category: 结果类型（'Displacement','Mises', 'Strain', 'PlasticStrain'）\n"
        #         "- case_ids: 工况ID或工况ID列表（默认3）\n"
        #         "- node_id: 节点ID\n"
        #         "- query: 查询需求，用于从结果中提取相关信息\n"
        #         "返回:\n"
        #         "结果查询日志文件内容，包含各工况的查询结果"
        #     ),
        #     args_schema=GetSingleNodeResultInput
        # ),
        
        # 获取单个或者多个节点结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_multi_node_results,
            name="get_multi_node_results",
            description=(
                "获取单个或者多个节点在指定一个或多个工况下的结果\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement','Mises', 'Strain', 'PlasticStrain'）\n"
                "- case_ids: 工况ID或工况ID列表（0表示不指定工况，为模型原始状态）\n"
                "- node_ids: 节点ID列表，例如[288, 296, 302]\n"
                "- query: 查询需求，用于从结果中提取相关信息\n"
                "返回:\n"
                "结果查询日志文件内容，包含各工况的查询结果"
            ),
            args_schema=GetMultiNodeResultsInput
        ),
        
        # 获取所有单元结果并生成CSV
        StructuredTool.from_function(
            func=lambda result_file, result_category: 
                (lambda path, desc: f"CSV文件路径: {path}\n字段描述: {desc}")
                (*mcp_toolkit.get_all_element_results(result_file, result_category)),
            name="get_all_element_results",
            description=(
                "获取所有工况下所有单元结果并输出到CSV文件\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "返回:\n"
                "CSV文件路径和字段描述的格式化字符串"
            ),
            args_schema=GetAllElementResultsInput
        ),
        
        # 获取单个单元结果
        # StructuredTool.from_function(
        #     func=mcp_toolkit.get_single_element_result,
        #     name="get_single_element_result",
        #     description=(
        #         "获取单个单元在指定一个或多个工况下的结果\n"
        #         "参数:\n"
        #         "- result_file: 结果文件路径（.h3d或.odb）\n"
        #         "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
        #         "- case_ids: 工况ID或工况ID列表（0表示不指定工况，为模型原始状态）\n"
        #         "- element_id: 单元ID\n"
        #         "- query: 查询需求，用于从结果中提取相关信息\n"
        #         "返回:\n"
        #         "结果查询日志文件内容，包含各工况的查询结果"
        #     ),
        #     args_schema=GetSingleElementResultInput
        # ),
        
        # 获取单个或多个单元结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_multi_element_results,
            name="get_multi_element_results",
            description=(
                "获取单个或者多个单元在指定一个或多个工况下的结果\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "- case_ids: 工况ID或工况ID列表（0表示不指定工况，为模型原始状态）\n"
                "- element_ids: 单元ID列表，例如[101, 102, 103]\n"
                "- query: 查询需求，用于从结果中提取相关信息\n"
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
                "获取单个或者多个属性在指定一个或多个工况下的结果\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "- case_ids: 工况ID或工况ID列表（0表示不指定工况，为模型原始状态）\n"
                "- part_ids: 部件ID列表，例如[5, 6, 7]\n"
                "- query: 查询需求，用于从结果中提取相关信息\n"
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
                "获取单种或者多种材料在指定一个或多个工况下的结果\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "- case_ids: 工况ID或工况ID列表（0表示不指定工况，为模型原始状态）\n"
                "- material_ids: 材料ID列表，例如[1, 2, 3]\n"
                "- query: 查询需求，用于从结果中提取相关信息\n"
                "返回:\n"
                "结果查询日志文件内容，包含各工况的查询结果"
            ),
            args_schema=GetMultiMaterialResultsInput
        ),
        
        
        # 获取模型所有信息
        StructuredTool.from_function(
            func=mcp_toolkit.get_model_info,
            name="get_model_info",
            description=(
                "获取模型在指定一个或多个工况下的信息（载荷、约束、材料、属性、集合、部件等）\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- info_type: 信息类型（'loads', 'spc', 'ansapart', 'property', 'material','set'）\n"
                "- result_category: 结果类型（默认'Mises'，可选'Strain', 'PlasticStrain', 'Displacement'）\n"
                "- case_ids: 工况ID或工况ID列表（0表示不指定工况，查询模型原始状态信息）\n"
                "- query: 查询需求，用于从结果中提取相关信息\n"
                "如果case_ids包含非0值，则返回对应工况下的模型信息及result_category结果信息\n"
                "返回:\n"
                "模型信息查询日志文件内容，包含各工况的查询结果"
            ),
            args_schema=GetModelInfoInput
        ),
        
        # 根据名称获取模型信息
        StructuredTool.from_function(
            func=mcp_toolkit.get_model_info_by_names,
            name="get_model_info_by_names",
            description=(
                "根据名称列表获取模型在指定一个或多个工况下的信息（载荷、约束、材料、属性、集合、部件等）\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- info_type: 信息类型（'loads', 'spc', 'ansapart', 'property', 'material','set'）\n"
                "- result_category: 结果类型（默认'Mises'，可选'Strain', 'PlasticStrain', 'Displacement'）\n"
                "- case_ids: 工况ID或工况ID列表（0表示不指定工况，查询模型原始状态信息）\n"
                "- names: 名称列表（默认None，表示获取所有）\n"
                "- query: 查询需求，用于从结果中提取相关信息\n"
                "返回:\n"
                "模型信息查询日志文件内容，包含各工况的查询结果"
            ),
            args_schema=GetModelInfoInputByNames
        ),
        
        # 获取指定实体的最大结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_max_result_for_entities,
            name="get_max_result_for_entities",
            description=(
                "获取指定单个或者多个实体（材料/属性/部件）的最大节点或单元结果\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- entity_type: 实体类型（'material', 'property', 'ansapart'）\n"
                "- entity_ids: 实体ID列表\n"
                "- entity_names: 实体名称列表\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "- node_or_element: 输出节点结果还是单元结果（'node'或'element'，默认'node'）\n"
                "- case_ids: 工况ID或工况ID列表（0表示不指定工况，为模型原始状态）\n"
                "- query: 查询需求，用于从结果中提取相关信息\n"
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
                "多方位截取指定单个或者多个实体的最大节点或单元结果云图\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "- entity_type: 实体类型（'material', 'property', 'ansapart'）\n"
                "- entity_ids: 实体ID列表\n"
                "- entity_names: 实体名称列表\n"
                "- output_dir: 输出目录\n"
                "- node_or_element: 显示云图是节点结果还是单元结果（'node'或'element'，默认'node'）\n"
                "- case_ids: 工况ID或工况ID列表（0表示不指定工况，为模型原始状态）\n"
                "返回:\n"
                "截图文件路径列表"
            ),
            args_schema=CaptureScreenshotsInput
        ),
    ]


if __name__ == "__main__":
    # 简单测试工具列表是否能正确生成
    tools = get_mcp_tools()
    print(f"生成了 {len(tools)} 个MCP工具")
    for tool in tools:
        print(f"- {tool.name}: {tool.description[:50]}...")