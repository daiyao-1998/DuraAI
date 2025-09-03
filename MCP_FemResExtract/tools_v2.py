from langchain.tools import StructuredTool
from .core import MCPToolKit
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Union, Tuple, Any

# 创建 MCPToolKit 实例
mcp_toolkit = MCPToolKit()


# 定义输入参数模型
class GetAllNodeResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Mises', 'Strain', 'PlasticStrain', 'Displacement'）")


class GetMultiNodeResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    ids_per_case: Dict[int, List[int]] = Field(description="字典，键为工况ID，值为该工况下的节点ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的节点名称列表")
    query: str = Field(default=None, description="从日志文件中提取相关信息的查询需求,必须填写")


class GetAllElementResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（ 'Mises', 'Strain', 'PlasticStrain', 'Displacement'）")


class GetMultiElementResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    ids_per_case: Dict[int, List[int]] = Field(description="字典，键为工况ID，值为该工况下的单元ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的单元名称列表")
    query: str = Field(default=None, description="从日志文件中提取相关信息的查询需求,必须填写")


class GetMultiPartResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    ids_per_case: Dict[int, List[int]] = Field(description="字典，键为工况ID，值为该工况下的属性ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的属性名称列表")
    query: str = Field(default=None, description="从日志文件中提取相关信息的查询需求,必须填写")


class GetMultiMaterialResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    ids_per_case: Dict[int, List[int]] = Field(description="字典，键为工况ID，值为该工况下的材料ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的材料名称列表")
    query: str = Field(default=None, description="从日志文件中提取相关信息的查询需求,必须填写")


# 新增集合查询输入模型
class GetMultiSetResultsInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    ids_per_case: Optional[Dict[int, List[int]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的集合ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的集合名称列表（如LAC-51010131）")
    query: str = Field(default=None, description="从日志文件中提取相关信息的查询需求,必须填写")


class GetModelInfoInput(BaseModel):
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    info_type: str = Field(description="信息类型（'loads', 'spc', 'ansapart', 'property', 'material', 'set'）")
    result_category: str = Field(default="Mises", description="结果类型（默认'Mises'，仅用于设置）")
    ids_per_case: Optional[Dict[int, List[int]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的实体ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的实体名称列表")
    query: str = Field(default=None, description="从日志文件中提取相关信息的查询需求,必须填写")


class GetMaxResultForEntitiesInput(BaseModel):
    """获取指定实体最大结果的输入参数"""
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    entity_type: str = Field(description="实体类型（'material', 'property', 'ansapart', 'set'）")
    ids_per_case: Optional[Dict[int, List[int]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的实体ID列表")
    names_per_case: Optional[Dict[int, List[str]]] = Field(default=None, description="字典，键为工况ID，值为该工况下的实体名称列表")
    node_or_element_result: str = Field(default="node", description="结果类型（'node'或'element'，默认'node'）")
    query: str = Field(default=None, description="从日志文件中提取相关信息的查询需求,必须填写")


class CaptureScreenshotsInput(BaseModel):
    """截取云图的输入参数"""
    result_file: str = Field(description="结果文件路径（.h3d或.odb）")
    result_category: str = Field(description="结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）")
    entity_type: str = Field(description="实体类型（'material', 'property', 'ansapart', 'set'）")
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
        
        # 获取单个或者多个节点结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_multi_node_results,
            name="get_multi_node_results",
            description=(
                "获取单个或者多个节点在指定一个或多个工况下的结果，支持两种查询方式：\n"
                "1. 通过ID指定：ids_per_case = {1: [1001, 1002], 2: [1003, 1004]}\n"
                "2. 通过名称指定：names_per_case = {1: ['NODE-1', 'NODE-2']}\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement','Mises', 'Strain', 'PlasticStrain'）\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的节点ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的节点名称列表（可选）\n"
                "- query: 查询需求，用于从结果中提取相关信息（可选）\n"
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
        
        # 获取单个或者多个单元结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_multi_element_results,
            name="get_multi_element_results",
            description=(
                "获取单个或者多个单元在指定一个或多个工况下的结果，支持两种查询方式：\n"
                "1. 通过ID指定：ids_per_case = {1: [101, 102], 2: [103, 104]}\n"
                "2. 通过名称指定：names_per_case = {1: ['ELEM-1', 'ELEM-2']}\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的单元ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的单元名称列表（可选）\n"
                "- query: 查询需求，用于从结果中提取相关信息（可选）\n"
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
                "获取单个或者多个属性在指定一个或多个工况下的结果，支持两种查询方式：\n"
                "1. 通过ID指定：ids_per_case = {1: [5, 6], 2: [7, 8]}\n"
                "2. 通过名称指定：names_per_case = {1: ['STU-0000116263_C611']}\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的属性ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的属性名称列表（可选）\n"
                "- query: 查询需求，用于从结果中提取相关信息（可选）\n"
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
                "获取单种或者多种材料在指定一个或多个工况下的结果，支持两种查询方式：\n"
                "1. 通过ID指定：ids_per_case = {1: [1, 2], 2: [3, 4]}\n"
                "2. 通过名称指定：names_per_case = {1: ['HC340LAD+Z']}\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的材料ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的材料名称列表（可选）\n"
                "- query: 查询需求，用于从结果中提取相关信息（可选）\n"
                "返回:\n"
                "结果查询日志文件内容，包含各工况的查询结果"
            ),
            args_schema=GetMultiMaterialResultsInput
        ),
        
        # 新增：获取多个集合结果
        StructuredTool.from_function(
            func=mcp_toolkit.get_multi_set_results,
            name="get_multi_set_results",
            description=(
                "获取单个或者多个集合在指定一个或多个工况下的结果，支持两种查询方式：\n"
                "1. 通过ID指定：ids_per_case = {1: [10, 11], 2: [12, 13]}\n"
                "2. 通过名称指定：names_per_case = {1: ['LAC-51010131', 'LAC-51010132']}\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的集合ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的集合名称列表（可选）\n"
                "- query: 查询需求，用于从结果中提取相关信息（可选）\n"
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
                "获取模型未加载状态下的信息（载荷、约束、材料、属性、集合、部件等）\n"
                "支持按ID或名称查询，通过ids_per_case或names_per_case指定不同工况下的查询对象\n"
                "当两个参数都为空时，查询所有信息\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- info_type: 信息类型（'loads', 'spc', 'ansapart', 'property', 'material','set'）\n"
                "- result_category: 结果类型（默认'Mises'，可选'Strain', 'PlasticStrain', 'Displacement'）\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的实体ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的实体名称列表（可选）\n"
                "- query: 查询需求，用于从结果中提取相关信息（可选）\n"
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
                "获取指定单个或者多个实体（材料/属性/部件/集合）的最大节点或单元结果\n"
                "支持两种实体指定方式，二选一即可：\n"
                "1. 通过ID指定：传入ids_per_case（字典，键为工况ID，值为实体ID列表）\n"
                "2. 通过名称指定：传入names_per_case（字典，键为工况ID，值为实体名称列表）\n"
                "当两个参数都为空时，默认查询全部模型结果\n"
                "参数:\n"
                "- result_file: 结果文件路径（.h3d或.odb）\n"
                "- result_category: 结果类型（'Displacement', 'Mises', 'Strain', 'PlasticStrain'）\n"
                "- entity_type: 实体类型（'material', 'property', 'ansapart', 'set'）\n"
                "- ids_per_case: 字典，键为工况ID，值为该工况下的实体ID列表（可选）\n"
                "- names_per_case: 字典，键为工况ID，值为该工况下的实体名称列表（可选）\n"
                "- node_or_element_result: 输出节点结果还是单元结果（'node'或'element'，默认'node'）\n"
                "- query: 查询需求，用于从结果中提取相关信息（可选）\n"
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
                    "多方位截取指定单个或多个实体的最大节点/单元结果云图，支持两种实体指定方式，二选一即可：\n"
                    "\n方法1：通过实体ID指定（适合已知实体ID的场景）\n"
                    "  - 需传入 `ids_per_case`：字典结构，键为工况ID（整数），值为该工况下需截图的实体ID列表（整数列表）；\n"
                    "\n方法2：通过实体名称指定（适合已知实体名称的场景）\n"
                    "  - 需传入 `names_per_case`：字典结构，键为工况ID（整数），值为该工况下需截图的实体名称列表（字符串列表）；\n"
                    "  - 注意：当实体类型为'ansapart'时，仅支持通过名称指定；\n"
                    "\n关键参数说明：\n"
                    "- result_file：必须传入有效的结果文件路径，支持.h3d或.odb格式；\n"
                    "- result_category：必须从['Displacement', 'Mises', 'Strain', 'PlasticStrain']中选择；\n"
                    "- entity_type：必须从['material', 'property', 'ansapart', 'set']中选择，需与实体指定方式匹配；\n"
                    "- node_or_element_result：默认'node'（节点结果），可指定为'element'（单元结果）；\n"
                    "\n返回结果：\n"
                    "HTML格式的截图集合，包含每个工况的7个角度视图（等轴测、正/背/左/右/顶/底视图），可直接在页面渲染查看。"
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
