import subprocess
import pandas as pd
import csv
from typing import List, Dict, Union, Optional, Tuple, Any
from pydantic import BaseModel, Field
from collections import defaultdict
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
import EnvConfig
from PIL import Image, ImageDraw, ImageFont
import os, datetime, json

env = EnvConfig.EnvConfig()

# 初始化大模型
# model = ChatDeepSeek(model="deepseek-chat",api_key=env.deepseek_api_key)
model = ChatOpenAI(
    model_name=env.li_model_v3,
    api_key=env.li_api_key,
    base_url=env.li_api_URL_v3,
)


class MCPToolKit:
    """有限元分析结果查询工具集，支持完整操作链（优化后支持多ID和名称批量查询）"""
    
    def __init__(self, meta_post_path: str = env.metabath_path):
        self.meta_post_path = meta_post_path
        self.output_dir = "./"
        # 实体类型与命令参数映射表，新增name参数支持
        self.entity_type_map = {
            "node": ("Nodes", "nodeoutput", "id.range", "name"),
            "element": ("Elements", "elemoutput", "id.range", "name"),
            "part": ("Parts", "partoutput", "id.range", "name"),
            "material": ("Materials", "matoutput", "id.range", "name"),
            "set": ("Groups", "nodeoutput", "id.range", "name"),  # 新增集合类型
        }
    
    def _stitch_screenshots(self, screenshot_paths: List[str], output_path: str = None) -> str:
        """
        将多个截图纵向拼接成一张图片，并在每张图片下方添加视图角度标注，完成后删除原始图片
        :param screenshot_paths: 截图文件路径列表
        :param output_path: 输出文件路径，默认为None，将在第一个截图同目录下生成
        :return: 拼接后的图片HTML格式字符串
        """
        if not screenshot_paths:
            raise ValueError("截图路径列表不能为空")
        
        # 打开所有图片
        # 检查文件是否存在
        for path in screenshot_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"文件不存在: {path}")
        
        images = [Image.open(path) for path in screenshot_paths]
        
        # 获取每张图片的宽度和高度
        widths, heights = zip(*(img.size for img in images))
        
        # 计算拼接后图片的总高度和最大宽度
        total_height = sum(heights)
        max_width = max(widths)
        
        # 创建新的空白图片，预留空间用于文字标注（每张图片下方预留50像素）
        stitched_image = Image.new('RGB', (max_width, total_height + len(images)*50), color='white')
        
        # 准备绘制文字
        draw = ImageDraw.Draw(stitched_image)
        # 修改字体加载方式，使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except OSError:
            font = ImageFont.load_default()
        
        # 将每张图片粘贴到新图片上，并添加标注
        y_offset = 0
        for i, (img, path) in enumerate(zip(images, screenshot_paths)):
            # 获取视图角度（从文件名中提取）
            view_name = os.path.basename(path).split('_')[-2].replace('_', ' ')
            
            # 粘贴图片
            stitched_image.paste(img, (0, y_offset))
            
            # 添加视图角度标注
            draw.text((10, y_offset + img.size[1] + 10), 
                     f"视图角度: {view_name}", 
                     fill="black", 
                     font=font)
            
            y_offset += img.size[1] + 50
        
        # 如果没有指定输出路径，则在第一个截图同目录下生成
        if output_path is None:
            base_dir = os.path.dirname(screenshot_paths[0])
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(base_dir, f"stitched_image_{timestamp}.png")
        
        # 保存拼接后的图片
        stitched_image.save(output_path)
        
        # 删除原始图片
        for path in screenshot_paths:
            try:
                os.remove(path)
            except OSError as e:
                print(f"删除文件{path}失败: {e}")
        
        # 返回HTML格式字符串
        filename = os.path.basename(output_path)
        return f"<img src='/images/{filename}' style='max-width: 100%; height: auto;'>"

    def _run_commands(self, commands: List[str], query: str = None) -> str:
        """执行META命令序列并返回日志
        :param commands: 命令列表
        :param query: 查询需求，用于从日志中提取相关信息
        :return: 执行结果或提取的相关信息
        """
        with open('./commands.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(commands))
        try:
            # 构建完整命令字符串（用分号分隔）
            command_str = ';'.join(commands)
            # print(command_str)
            full_command = [
                'sudo', '-E',
                self.meta_post_path,
                '-b', '-noses','-fastses', '-exec',
                f"{command_str}"
            ]
            # 执行命令
            out = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            # print(out)
            return self._extract_log_content(query)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _extract_log_content(self, query: str = None) -> str:
        """读取当前工作目录下的META_post.log文件内容
        :param query: 查询需求，用于从日志中提取相关信息
        :return: 日志内容或提取的相关信息
        """
        try:
            current_dir = os.getcwd()
            log_file = os.path.join(current_dir, "META_post.log")
            
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 如果提供了查询需求，则通过大模型提取相关信息
                if query:
                    return self._extract_relevant_info(content, query)
                
                return content
            else:
                return f"Log file not found at: {log_file}"
        except Exception as e:
            return f"An error occurred while extracting log content: {str(e)}"
    
    def _extract_relevant_info(self, log_content: str, query: str) -> str:
        """使用大模型从日志内容中提取与查询需求相关的信息
        :param log_content: 日志内容
        :param query: 查询需求
        :return: 提取的相关信息
        """
        try:
            # 构造提示词
            prompt = f"""
            你是一个专业的有限元分析结果处理助手。用户需要从下面的日志内容中提取与查询需求相关的信息。
            
            查询需求: {query}
            
            日志内容:
            {log_content}
            
            请根据查询需求，从日志内容中提取出相关的信息并以清晰的格式返回。只返回提取出的相关信息，不要包含其他内容。
            
            在分析日志时，请特别注意以下几点：
            1. 涉及到工况中载荷相关的分析时，载荷的id表示的是该载荷位于第几个工况（例如CLOAD id: 1表明其后面的载荷为第一个工况的载荷，CLOAD id: 2表明为第二个工况的载荷）。
            2. part翻译为属性  ansapart翻译为零件  
            3. 当用户询问特定工况的载荷情况时，只需要提取对应id后的载荷信息，不要包含其他工况的载荷数据。
            4. 请确保提取的信息完整且准确，以简洁的信息格式返回需要的信息。如果查询需求无法满足，请返回"未找到相关信息"。
            5. 如果查询的节点存在局部坐标系，需要同时提取并返回全局坐标及局部坐标系下的位移
            6. 日志文件中以Reading开头的行表示正在读取的结果文件，这些行信息包含结果文件中的工况数量信息：
                对于ODB文件需要特殊注意。例如日志内容为:
                Reading "STEP 1        (AnonymousSTEP1),TIME 0.00000000E+00"
                Reading "STEP 1        (AnonymousSTEP1),TIME 1.00000000E+00"
                Reading "STEP 2        (AnonymousSTEP2),TIME 1.00000000E+00"
                Reading "STEP 2        (AnonymousSTEP2),TIME 1.10302734E+00"
                Reading "STEP 2        (AnonymousSTEP2),TIME 1.36381531E+00"
                Reading "STEP 2        (AnonymousSTEP2),TIME 2.00000000E+00"
                Reading "STEP 3        (AnonymousSTEP3),TIME 2.00000000E+00"
                Reading "STEP 3        (AnonymousSTEP3),TIME 3.00000000E+00"
                其中共有三个分析步骤，STEP 1包含两个时间点（0和1），STEP 2包含四个时间点（1、1.103、1.364和2），STEP 3包含两个时间点（2和3）。
                注意：STEP 1工况的TIME 1与STEP 2工况的TIME 0是等效的，在提取工况信息时，请特别注意这种时间点的等效性，避免重复提取或遗漏信息。第一个时间节点开始的工况编号为0，依次类推(STEP 3        (AnonymousSTEP3),TIME 3.00000000E+00的id为7)。
                所以最终有效的工况为：
                STEP 1        (AnonymousSTEP1),TIME 1.00000000E+00 (case_id: 1)
                STEP 2        (AnonymousSTEP2),TIME 1.10302734E+00 (case_id: 3)
                STEP 2        (AnonymousSTEP2),TIME 1.36381531E+00 (case_id: 4)
                STEP 2        (AnonymousSTEP2),TIME 2.00000000E+00 (case_id: 5)
                STEP 3        (AnonymousSTEP3),TIME 3.00000000E+00 (case_id: 7)
            """
            
            # 调用大模型
            response = model.invoke(prompt)
            
            # 返回提取的信息
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"An error occurred while extracting relevant information: {str(e)}"

    def _build_geometry_path(self, result_file: str) -> str:
        """根据结果文件自动推断几何文件路径
        :param result_file: 结果文件路径
        :return: 几何文件路径
        """
        base_path = os.path.splitext(result_file)[0]
        ext = os.path.splitext(result_file)[1].lower()
        self.output_dir = os.path.dirname(result_file)
        
        if ext == ".h3d":
            fem_path = base_path + ".fem"
            if os.path.exists(fem_path):
                return fem_path
            raise FileNotFoundError(f"找不到对应的几何文件: {fem_path}")
        
        elif ext == ".odb":
            inp_path = base_path + ".inp"
            if os.path.exists(inp_path):
                return inp_path
            return result_file  # .odb本身包含几何信息
        
        raise ValueError(f"不支持的结果文件类型: {ext}")
    
    def _build_result_commands(self, result_file: str, result_category: str) -> List[str]:
        """构建加载结果的完整命令序列
        :param result_file: 结果文件路径
        :param result_category: 结果类型（如Displacement, Mises等）
        :return: 命令列表
        """
        try:
            geometry_file = self._build_geometry_path(result_file)
        except (FileNotFoundError, ValueError) as e:
            return [f"echo '{str(e)}'"]
        
        ext = os.path.splitext(result_file)[1].lower()
        result_type = "Hypermesh" if ext == ".h3d" else "Abaqus" if ext == ".odb" else "Unknown"
        
        commands = [f"read geom AUTO {geometry_file}"]
        
        if result_type == "Hypermesh":
            if result_category == "Displacement":
                commands.extend([
                    f"read dis Hypermesh {result_file} all Displacement",
                    f"read onlyfun Hypermesh {result_file} all Displacement,Magnitude"
                ])
            elif result_category == "Mises":
                commands.extend([
                    f"read dis Hypermesh {result_file} all Displacement",
                    f"read onlyfun Hypermesh {result_file} all ElementStresses(2D&3D),VonMises,Max",
                ])
        
        elif result_type == "Abaqus":
            if result_category == "Displacement":
                commands.extend([
                    f'read dis Abaqus {result_file} all Displacements',
                    f"read onlyfun Abaqus {result_file} all Displacements,Magnitude"
                ])
            elif result_category == "Mises":
                commands.extend([
                    f'read dis Abaqus {result_file} all Displacements',
                    f"read onlyfun Abaqus {result_file} all Stresscomponents,VonMises,MaxofInOut/AllLayers,Centroid"
                ])
            elif result_category == "Strain":
                commands.extend([
                    f'read dis Abaqus {result_file} all Displacements',
                    f"read onlyfun Abaqus {result_file} all Straincomponents,Triaxiality,MaxofInOut/AllLayers,Centroid"
                ])
            elif result_category == "PlasticStrain":
                commands.extend([
                    f'read dis Abaqus {result_file} all Displacements',
                    f"read onlyfun Abaqus {result_file} all Equivalentplasticstrain,MaxofInOut/AllLayers,Centroid"
                ])
        
        return commands
    
    def get_all_node_results(
        self, 
        result_file: str, 
        result_category: str, 
    ) -> Tuple[str, str]:
        """获取所有工况下所有节点结果（输出到CSV文件）
        :param result_file: 结果文件路径
        :param result_category: 结果类型（如Displacement, Mises等）
        :return: CSV文件路径和字段描述
        """
        commands = self._build_result_commands(result_file, result_category)
        
        base_path = os.path.splitext(result_file)[0]
        output_path = f'{base_path}_all_node_{result_category}_results.csv'
        commands.extend([
            'identify outopts multistates enable',
            'identify outopts multilabels include disp all',
            'identify outopts multilabels include scalar all',
            'identify outopts multistates include all',
            'identify outopts multistates exclude 0',
            'identify node outopts origposx on',
            'identify node outopts origposy on',
            'identify node outopts origposz on',
            'identify node outopts posx off',
            'identify node outopts posy off',
            'identify node outopts posz off',
            'identify node outopts comment off',
            'identify node outopts ldispx off',
            'identify node outopts ldispy off',
            'identify node outopts ldispz off',
            'identify node outopts name off',
            'identify node outopts scalartop off',
            'identify node outopts scalarbot off',
            'identify node outopts functop on',
            'identify node outopts funcbot off',
            'identify node outopts udispx off',
            'identify node outopts udispy off',
            'identify node outopts udispz off',
            'identify node outopts vectorbot off',
            'identify node outopts vectortop off',
            'identify node outopts xfunctop off',
            'identify node outopts xfuncbot off',
            'identify node outopts yfunctop off',
            'identify node outopts yfuncbot off',
            'identify node outopts zfunctop off',
            'identify node outopts zfuncbot off',
            f'identify node lres all "{output_path}"'
        ])
        
        self._run_commands(commands)
        
        if not os.path.exists(output_path):
            return f"结果文件未生成: {output_path}", ""
        
        field_description = '''
            CSV文件采用多工况块循环结构，每个工况块包含三部分：
                1. 工况名称行：单独1行，以STEP或Subcase开头（如'STEP 1 XXXX', 'Subcase 2 XXX'）
                2. 字段名称行：紧随工况行
                3. 数据行：紧随字段行，每行对应一个节点的数值数据
            可能存在的字段含义:
                - Id: 节点ID
                - Pid: 部件ID
                - Dispx, Dispy, Dispz: X/Y/Z方向位移
                - Disptotal: 总位移
                - origPosx, origPosy, origPosz: 原始坐标
                - FunctionTop: 标量结果值（应变/塑性应变/Mises应力等）
        '''
        return output_path, field_description

    
    def get_all_element_results(
        self, 
        result_file: str, 
        result_category: str, 
    ) -> Tuple[str, str]:
        """获取所有工况下所有单元结果（输出到CSV文件）
        :param result_file: 结果文件路径
        :param result_category: 结果类型（如Displacement, Mises等）
        :return: CSV文件路径和字段描述
        """
        commands = self._build_result_commands(result_file, result_category)
        
        base_path = os.path.splitext(result_file)[0]
        output_path = f'{base_path}_all_element_{result_category}_results.csv'
        commands.extend([
            'identify outopts multistates enable',
            'identify outopts multilabels include disp all',
            'identify outopts multilabels include scalar all',
            'identify outopts multistates include all',
            'identify outopts multistates exclude 0',
            'identify element outopts cog off',
            'identify element outopts cornbot off',
            'identify element outopts corntop off',
            'identify element outopts elemname off',
            'identify element outopts comment off',
            'identify element outopts scalartop off',
            'identify element outopts scalarbot off',
            'identify element outopts funcbot off',
            'identify element outopts functop on',
            'identify element outopts funccorn off',
            "identify element outopts vectormagtop off",
            "identify element outopts vectormagbot off",
            "identify element outopts vectortop off",
            "identify element outopts vectorbottom off",
            "identify element outopts vectorcomponents off",
            'identify element outopts nodes off',
            'identify element outopts principaltensor off',
            f'identify element lres all "{output_path}"'
        ])
        
        self._run_commands(commands)
        
        if not os.path.exists(output_path):
            return f"结果文件未生成: {output_path}", ""
        
        field_description = '''
            CSV文件采用多工况块循环结构，每个工况块包含三部分：
                1. 工况名称行：单独1行，以STEP或Subcase开头
                2. 字段名称行：紧随工况行
                3. 数据行：紧随字段行，每行对应一个单元的数值数据
            可能存在的字段含义:
                - Id: 单元ID
                - Pid: 部件ID
                - PidName: 部件名称
                - FunctionTop: 标量结果值（应变/塑性应变/应力等）
        '''
        return output_path, field_description

    def _get_multi_entity_results(
        self,
        result_file: str,
        result_category: str,
        entity_type: str,
        ids_per_case: Dict[int, List[int]] = None,
        names_per_case: Dict[int, List[str]] = None,
        query: str = None
    ) -> str:
        """
        通用多实体结果查询底层方法（支持不同工况对应不同实体ID或名称）
        :param result_file: 结果文件路径
        :param result_category: 结果类型
        :param entity_type: 实体类型（node/element/part/material/set）
        :param ids_per_case: 字典，键为工况ID，值为该工况下的实体ID列表
        :param names_per_case: 字典，键为工况ID，值为该工况下的实体名称列表
        :param query: 查询需求，用于从日志中提取相关信息
        :return: 查询结果日志或提取的相关信息
        """
        # 参数验证 - 必须提供ID或名称中的一种
        if not ids_per_case and not names_per_case:
            return "必须提供ids_per_case或names_per_case参数中的至少一个"
        if entity_type not in self.entity_type_map:
            return f"不支持的实体类型: {entity_type}，支持类型：{list(self.entity_type_map.keys())}"
        
        # 确定使用ID还是名称查询
        use_ids = bool(ids_per_case)
        case_entity_map = ids_per_case if use_ids else names_per_case
        case_ids = list(case_entity_map.keys())
        
        # 获取实体类型映射信息
        entity_name, output_type, id_param, name_param = self.entity_type_map[entity_type]
        
        # 构建基础命令链
        commands = self._build_result_commands(result_file, result_category)
        
        # 添加每个工况的查询命令
        for case_id, entities in case_entity_map.items():
            if not entities:
                continue
                
            # 构建实体范围字符串（逗号分隔）
            entity_range = ','.join(map(str, entities))
            
            commands.append(f'options message "----- 开始查询工况 {case_id} 的{entity_type} {"ID" if use_ids else "名称"}列表 [{entity_range}] 结果 -----"')
            commands.append(f'options state "{case_id}"')
            
            # 构建advfilter命令（支持ID和名称两种方式）
            filter_param = id_param if use_ids else name_param
            filter_cmd = f'identify advfilter {output_type} add:{entity_name}:{filter_param}:{entity_range}:Keep All'
            commands.append(filter_cmd)
        
        # 执行命令并返回日志
        result = self._run_commands(commands, query)
        return f"多{entity_type}结果查询日志:\n{result}"

    def get_multi_node_results(
        self,
        result_file: str,
        result_category: str,
        ids_per_case: Dict[int, List[int]] = None,
        names_per_case: Dict[int, List[str]] = None,
        query: str = None
    ) -> str:
        """
        获取单个或者多个节点在指定工况下的结果（支持不同工况对应不同节点ID或名称）
        :param result_file: 结果文件路径
        :param result_category: 结果类型
        :param ids_per_case: 字典，键为工况ID，值为该工况下的节点ID列表
        :param names_per_case: 字典，键为工况ID，值为该工况下的节点名称列表
        :param query: 查询需求，用于从日志中提取相关信息
        :return: 查询结果日志或提取的相关信息
        """
        return self._get_multi_entity_results(
            result_file=result_file,
            result_category=result_category,
            entity_type="node",
            ids_per_case=ids_per_case,
            names_per_case=names_per_case,
            query=query
        )

    def get_multi_element_results(
        self,
        result_file: str,
        result_category: str,
        ids_per_case: Dict[int, List[int]] = None,
        names_per_case: Dict[int, List[str]] = None,
        query: str = None
    ) -> str:
        """
        获取单个或者多个单元在指定工况下的结果（支持不同工况对应不同单元ID或名称）
        :param result_file: 结果文件路径
        :param result_category: 结果类型
        :param ids_per_case: 字典，键为工况ID，值为该工况下的单元ID列表
        :param names_per_case: 字典，键为工况ID，值为该工况下的单元名称列表
        :param query: 查询需求，用于从日志中提取相关信息
        :return: 查询结果日志或提取的相关信息
        """
        return self._get_multi_entity_results(
            result_file=result_file,
            result_category=result_category,
            entity_type="element",
            ids_per_case=ids_per_case,
            names_per_case=names_per_case,
            query=query
        )


    def get_multi_part_results(
        self,
        result_file: str,
        result_category: str,
        ids_per_case: Dict[int, List[int]] = None,
        names_per_case: Dict[int, List[str]] = None,
        query: str = None
    ) -> str:
        """
        获取单个或者多个属性（常见属性Pshell/Psolid等等）在指定工况下的结果
        支持通过ID或名称查询，如STU-0000116263_C611
        :param result_file: 结果文件路径
        :param result_category: 结果类型
        :param ids_per_case: 字典，键为工况ID，值为该工况下的部件ID列表
        :param names_per_case: 字典，键为工况ID，值为该工况下的部件名称列表
        :param query: 查询需求，用于从日志中提取相关信息
        :return: 查询结果日志或提取的相关信息
        """
        return self._get_multi_entity_results(
            result_file=result_file,
            result_category=result_category,
            entity_type="part",
            ids_per_case=ids_per_case,
            names_per_case=names_per_case,
            query=query
        )

    def get_multi_material_results(
        self,
        result_file: str,
        result_category: str,
        ids_per_case: Dict[int, List[int]] = None,
        names_per_case: Dict[int, List[str]] = None,
        query: str = None
    ) -> str:
        """
        获取单种或者多种材料在指定工况下的结果
        支持通过ID或名称查询，如HC340LAD+Z
        :param result_file: 结果文件路径
        :param result_category: 结果类型
        :param ids_per_case: 字典，键为工况ID，值为该工况下的材料ID列表
        :param names_per_case: 字典，键为工况ID，值为该工况下的材料名称列表
        :param query: 查询需求，用于从日志中提取相关信息
        :return: 查询结果日志或提取的相关信息
        """
        return self._get_multi_entity_results(
            result_file=result_file,
            result_category=result_category,
            entity_type="material",
            ids_per_case=ids_per_case,
            names_per_case=names_per_case,
            query=query
        )

    def get_multi_set_results(
        self,
        result_file: str,
        result_category: str,
        ids_per_case: Dict[int, List[int]] = None,
        names_per_case: Dict[int, List[str]] = None,
        query: str = None
    ) -> str:
        """
        新增：获取单个或多个集合（set）在指定工况下的结果
        支持通过ID或名称查询，如LAC-51010131
        :param result_file: 结果文件路径
        :param result_category: 结果类型
        :param ids_per_case: 字典，键为工况ID，值为该工况下的集合ID列表
        :param names_per_case: 字典，键为工况ID，值为该工况下的集合名称列表
        :param query: 查询需求，用于从日志中提取相关信息
        :return: 查询结果日志或提取的相关信息
        """
        return self._get_multi_entity_results(
            result_file=result_file,
            result_category=result_category,
            entity_type="set",
            ids_per_case=ids_per_case,
            names_per_case=names_per_case,
            query=query
        )

    def get_max_result_for_entities(
        self,
        result_file: str,
        result_category: str,
        entity_type: str,
        ids_per_case: Dict[int, List[int]] = None,
        names_per_case: Dict[int, List[str]] = None,
        node_or_element_result: str = "node",
        query: str = None
    ) -> str:
        """
        获取指定实体（材料/属性/部件）的最大节点或单元结果
        当ids_per_case和names_per_case都为空时，默认查询全部模型结果
        :param result_file: 结果文件路径
        :param result_category: 结果类型
        :param entity_type: 实体类型（material/property/ansapart）
        :param ids_per_case: 字典，键为工况ID，值为该工况下的实体ID列表
        :param names_per_case: 字典，键为工况ID，值为该工况下的实体名称列表
        :param node_or_element_result: 结果类型（node或element,node输出单元节点上的结果，element输出单元中心点结果）
        :param query: 查询需求，用于从日志中提取相关信息
        :return: 查询结果日志或提取的相关信息
        """
        # 参数验证
        if entity_type not in ["material", "property", "ansapart"]:
            return f"不支持的实体类型: {entity_type}，支持类型：['material', 'property', 'ansapart']"
        
        # 处理实体ID与工况的映射关系，都为空则查询全部模型
        if not ids_per_case and not names_per_case:
            case_entity_map = {0: []}  # 使用0作为默认工况
            use_all = True
        elif ids_per_case:
            case_entity_map = ids_per_case
            use_ids = True
            use_all = False
        else:
            case_entity_map = names_per_case
            use_ids = False
            use_all = False
        
        # 构建基础命令链
        commands = self._build_result_commands(result_file, result_category)
        # 先隐藏所有实体
        commands.append('erase all')
        
        # 添加工况查询命令
        for case_id, entities in case_entity_map.items():
            commands.append(f'options message "----- 开始查询工况 {case_id} 的{entity_type} 最大结果 -----"')
            commands.append(f'options state "{case_id}"')
            
            if use_all:
                # 查询全部模型
                commands.append('erase none')  # 不清除任何实体，显示全部
            else:
                if not entities:
                    continue
                
                # 构建实体范围字符串
                if use_ids:
                    entity_range = ','.join(map(str, entities))
                    if entity_type == "material":
                        commands.append(f'add mid {entity_range}')
                    elif entity_type == "property":
                        commands.append(f'add pid {entity_range}')
                else:
                    entity_range = ','.join(entities)
                    if entity_type == "material":
                        commands.append(f'add mid name {entity_range}')
                    elif entity_type == "property":
                        commands.append(f'add pid name {entity_range}')
                    elif entity_type == "ansapart":
                        commands.append(f'add ansapart name {entity_range}')
            
            # 根据结果类型决定是节点还是单元结果
            if node_or_element_result == "node":
                # 节点结果
                commands.append('function info nodal visible')
            elif node_or_element_result == "element":
                # 单元结果
                commands.append('function info visible')
            else:
                return "不支持的结果类型"
        
        # 执行命令并返回日志
        result = self._run_commands(commands, query)
        return f"{entity_type}最大结果查询日志:\n{result}"

    def get_model_info(
        self,
        result_file: str,
        info_type: str,
        result_category: str = "Mises",
        ids_per_case: Dict[int, List[int]] = None,
        names_per_case: Dict[int, List[str]] = None,
        query: str = None
    ) -> str:
        """
        获取模型未加载状态下载荷/约束/零件/属性/材料/集的信息
        支持按ID或名称查询，通过ids_per_case或names_per_case指定不同工况下的查询对象
        当两个参数都为空时，查询所有信息
        :param result_file: 结果文件路径
        :param info_type: 信息类型（loads, spc, ansapart, property, material, set）
        :param result_category: 结果类型
        :param ids_per_case: 字典，键为工况ID，值为该工况下的实体ID列表
        :param names_per_case: 字典，键为工况ID，值为该工况下的实体名称列表
        :param query: 查询需求，用于从日志中提取相关信息
        :return: 查询结果日志或提取的相关信息
        """
        try:
            # 验证信息类型
            valid_info_types = ["loads", "spc", "ansapart", "property", "material", "set"]
            if info_type.lower() not in valid_info_types:
                return f"不支持的信息类型: {info_type}，支持类型：{valid_info_types}"

            # 处理查询对象与工况的映射关系，都为空则查询全部
            if not ids_per_case and not names_per_case:
                case_entity_map = {0: []}  # 使用0作为默认工况
                use_all = True
            elif ids_per_case:
                case_entity_map = ids_per_case
                use_ids = True
                use_all = False
            else:
                case_entity_map = names_per_case
                use_ids = False
                use_all = False

            # 构建基础命令链
            commands = self._build_result_commands(result_file, result_category)
            
            # 添加工况查询命令
            for case_id, entities in case_entity_map.items():
                if case_id != 0:
                    commands.append(f'options state "{case_id}"')
                commands.append(f'options message "----- 开始查询工况 {case_id} 的模型{info_type}信息 -----"')
                
                # 构建查询命令
                base_cmds = {
                    "loads": "identify loads",
                    "spc": "identify spc",
                    "ansapart": "identify ansapart",
                    "property": "identify part",
                    "material": "identify mid",
                    "set": "identify set"  # 新增集合查询支持
                }
                
                base_cmd = base_cmds.get(info_type.lower())
                if not base_cmd:
                    return "不支持的信息类型"
                
                if use_all:
                    # 查询全部信息
                    commands.append(f"{base_cmd} all")
                else:
                    if not entities:
                        continue
                    
                    entity_range = ','.join(map(str, entities))
                    if use_ids:
                        commands.append(f"{base_cmd} {entity_range}")
                    else:
                        commands.append(f"{base_cmd} name {entity_range}")
            
            return f"模型信息查询日志文件内容:\n{self._run_commands(commands, query)}"
        except (FileNotFoundError, ValueError) as e:
            return str(e)
            
    def capture_screenshots(
        self,
        result_file: str,
        result_category: str,
        entity_type: str,
        ids_per_case: Dict[int, List[int]] = None,
        names_per_case: Dict[int, List[str]] = None,
        output_dir: str = env.images_path,
        query: str = None,
        node_or_element_result: str = "node"
    ) -> str:
        """
        多方位截取指定实体的最大节点或单元结果云图
        当ids_per_case和names_per_case都为空时，默认截取全部模型结果
        :param result_file: 结果文件路径
        :param result_category: 结果类型
        :param entity_type: 实体类型（material/property/ansapart）
        :param ids_per_case: 字典，键为工况ID，值为该工况下的实体ID列表
        :param names_per_case: 字典，键为工况ID，值为该工况下的实体名称列表
        :param output_dir: 输出目录
        :param node_or_element_result: 云图显示结果类型（node或element）
        :param query: 查询需求，用于从日志中提取相关信息
        :return: 截图文件路径列表
        """
        # 参数验证
        if entity_type not in ["material", "property", "ansapart"]:
            raise ValueError("entity_type必须是'material', 'property', 'ansapart'之一")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 处理实体ID与工况的映射关系，都为空则查询全部模型
        if not ids_per_case and not names_per_case:
            case_entity_map = {0: []}  # 使用0作为默认工况
            use_all = True
            use_ids = False
        elif ids_per_case:
            case_entity_map = ids_per_case
            use_ids = True
            use_all = False
        else:
            case_entity_map = names_per_case
            use_ids = False
            use_all = False
        
        # 定义视图角度
        views = [
            "default isometric",
            "default top",
            "default front",
            "default left",
            "default btm",
            "default back",
            "default right",
        ]
        
        # 构建基础命令链
        base_commands = self._build_result_commands(result_file, result_category)
        # 启用云图显示
        base_commands.extend([
            'grstyle scalarfringe enable',
            'options metadefaults read ./META.default',
            'identify showres format fixed',
            'identify showres format digits 1',
            'identify showres enable',
            'identify showres showfunc on',
            'identify showres showtopscalar on',
            'identify showres showbotscalar on',
            '!function info filter max on',
            '!function info filter min off',
            'identify showres showtot off',
            'identify showres showz off',
            'identify showres showy off',
            'identify showres showx off',
            'identify showres showposz off',
            'identify showres showposy off',
            'identify showres showposx off',
            'identify font "宋体,30,-1,5,50,0,0,0,0,0,常规"',
            'write options transparent enable',
            'identify options drawfunclabel disable',
            'options fringebar format enabled Fixed',
            'options fringebar format enabled digits 1',
            'color delete "255"',
            'color new "255" 255,255,255,255',
            'color fringebar update "default" "255_85_0_255,255_242_53_255,Yellow,170_255_0_255,85_255_0_255,Green,0_255_85_255,0_255_170_255,Cyan,0_170_255_255,236_230_230_255,255"',
        ])

        html_results = []  # 存储每个工况的HTML结果
        
        for case_id, entities in case_entity_map.items():
            # 复制基础命令
            commands = base_commands.copy()
            
            if use_all:
                # 显示整个模型
                commands.append('options message "----- 开始查询工况 {case_id} 的整个模型最大结果 -----"')
                commands.append('erase none')  # 不清除任何实体
            else:
                # 隐藏所有实体并添加指定实体
                commands.append('erase all')
                
                if not entities:
                    continue
                
                # 构建实体范围字符串
                if use_ids:
                    entity_range = ','.join(map(str, entities))
                    commands.append(f'options message "----- 开始查询工况 {case_id} 的{entity_type} ID列表 [{entity_range}] 最大结果 -----"')
                else:
                    entity_range = ','.join(entities)
                    commands.append(f'options message "----- 开始查询工况 {case_id} 的{entity_type} 名称列表 [{entity_range}] 最大结果 -----"')
                
                # 根据实体类型构建相应的命令
                if use_ids:
                    if entity_type == "material":
                        commands.append(f'add mid {entity_range}')
                    elif entity_type == "property":
                        commands.append(f'add pid {entity_range}')
                else:
                    if entity_type == "material":
                        commands.append(f'add mid name {entity_range}')
                    elif entity_type == "property":
                        commands.append(f'add pid name {entity_range}')
                    elif entity_type == "ansapart":
                        commands.append(f'add ansapart name {entity_range}')
            
            commands.append(f'options state "{case_id}"')
            
            # 取消上一步的结果数值显示
            commands.append('identify reset')

            # 根据结果类型决定是节点还是单元结果
            if node_or_element_result.lower() == "node":
                # 节点结果
                commands.append('grstyle scalarfringe onnode')
                commands.append('function info nodal visible')
            elif node_or_element_result.lower() == "element":
                # 单元结果
                commands.append('grstyle scalarfringe onelement')
                commands.append('function info visible')
            else:
                raise ValueError("node_or_element_result必须是'node'或'element'")
            
            commands.append('view center')
            
            # 多角度截图
            screenshot_paths = []
            for view in views:
                # 设置视图
                commands.append(f'view {view}')
                
                # 生成文件名
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                if use_all:
                    # 整个模型的截图
                    filename = f"{os.path.basename(result_file).split('.')[0]}_{result_category}_entire_model_{case_id}_{view.replace(' ', '_')}_{timestamp}.png"
                elif use_ids:
                    filename = f"{os.path.basename(result_file).split('.')[0]}_{result_category}_{entity_type}_{case_id}_{view.replace(' ', '_')}_{timestamp}.png"
                else:
                    filename = f"{os.path.basename(result_file).split('.')[0]}_{result_category}_{entity_type}_{case_id}_{view.replace(' ', '_')}_{timestamp}_by_name.png"
                filepath = os.path.join(output_dir, filename)
                
                # 截图命令
                commands.append(f'write png "{filepath}"')
                screenshot_paths.append(filepath)
            
            # 执行截图命令
            self._run_commands(commands, query)
            
            # 拼接截图并返回HTML格式
            case_html = self._stitch_screenshots(screenshot_paths)
            
            # 添加工况标题
            if use_all:
                title = f"<h3>工况 {case_id} 整个模型结果</h3>"
            else:
                title = f"<h3>工况 {case_id} 结果</h3>"
            html_results.append(title + case_html)
        
        # 返回所有工况的HTML结果
        return "<div>" + "".join(html_results) + "</div>"
    