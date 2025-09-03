import os
import json
import datetime
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import asyncio
from concurrent.futures import ThreadPoolExecutor
from matplotlib.font_manager import FontProperties
import EnvConfig

# 初始化环境配置
env = EnvConfig.EnvConfig()

class FigGenerator:
    """绘图工具核心类"""
    
    # 预定义颜色（RGB转换为0-1范围）
    COLORS = {
        "dark_green": (13/255, 87/255, 80/255),
        "gray": (192/255, 184/255, 187/255),
        "gold": (206/255, 164/255, 114/255),
        "orange": (234/255, 112/255, 13/255),
        "green": (0/255, 175/255, 80/255)
    }
    
    def __init__(self, base_dir=None, ui_dir=env.images_path, font_path=env.font_path):
        """
        初始化绘图工具
        
        Args:
            base_dir: 图像保存的基础目录
            ui_dir: UI端图像保存目录
            font_path: 中文字体文件路径
        """
        self.base_dir = os.path.dirname(__file__)
        self.ui_dir = ui_dir
        self.font_path = font_path 
        self.executor = ThreadPoolExecutor(max_workers=4)  # 线程池用于异步执行
        
        # 确保目录存在
        self.images_dir = os.path.join(self.base_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.ui_dir, exist_ok=True)
        
        # 设置中文字体
        self.chinese_font = FontProperties(fname=self.font_path)
        # 全局设置matplotlib字体，确保所有文字默认使用中文字体
        plt.rcParams["font.family"] = [self.chinese_font.get_name()]
    
    def apply_chinese_font(self, ax=None):
        """应用中文到图表所有元素，包括刻度值"""
        if ax is None:
            ax = plt.gca()
        
        # 设置标题、标签等使用中文字体
        title = ax.get_title()
        if title:
            ax.set_title(title, fontproperties=self.chinese_font)
        
        xlabel = ax.get_xlabel()
        if xlabel:
            ax.set_xlabel(xlabel, fontproperties=self.chinese_font)
        
        ylabel = ax.get_ylabel()
        if ylabel:
            ax.set_ylabel(ylabel, fontproperties=self.chinese_font)
        
        # 设置坐标轴刻度文字
        for label in ax.get_xticklabels():
            label.set_fontproperties(self.chinese_font)
        for label in ax.get_yticklabels():
            label.set_fontproperties(self.chinese_font)
        
        # 设置图例使用中文
        legend = ax.get_legend()
        if legend:
            for text in legend.get_texts():
                text.set_fontproperties(self.chinese_font)  
    
    def add_data_labels(self, ax, bars=None):
        """在图表上添加数据标签"""
        if bars is None:
            bars = ax.containers
        
        for container in bars:
            if hasattr(container, '__len__') and len(container) > 0:
                # 柱状图标签
                if hasattr(container[0], 'get_height'):
                    for bar in container:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                                f'{height:.2f}', ha='center', va='bottom',
                                fontproperties=self.chinese_font)
                # 其他类型图表可以根据需要扩展
    
    async def execute_code(self, py_code, fname="fig"):
        """
        异步执行绘图代码并保存图像
        
        Args:
            py_code: Python绘图代码
            fname: 图像对象的变量名
            
        Returns:
            成功返回图像路径，失败返回错误信息
        """
        # 使用线程池异步执行绘图操作，避免阻塞主线程
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self._sync_execute_code, 
            py_code, 
            fname
        )
    
    def _sync_execute_code(self, py_code, fname="fig"):
        """同步执行绘图代码的内部方法，供线程池调用"""
        # 保存当前后端设置
        current_backend = matplotlib.get_backend()
        matplotlib.use('Agg')
        
        # 准备执行环境
        local_vars = {
            "plt": plt, 
            "pd": pd, 
            "sns": sns,
            "chinese_font": self.chinese_font,
            "li_colors": self.COLORS
        }
        
        try:
            
            exec(py_code, {}, local_vars)
            
            # 获取图像对象
            fig = local_vars.get(fname, None)
            if not fig:
                return "⚠️ 图像对象未找到，请确认变量名正确并为 matplotlib 图对象。"
            
            # 应用中文设置到所有元素
            if hasattr(fig, 'axes'):
                for ax in fig.axes:
                    self.apply_chinese_font(ax)
                    # self.add_data_labels(ax)
            
            # 生成文件名并保存
            time_stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            image_filename = f"{fname}_{time_stamp}.png"
            rel_path = os.path.join("images", image_filename)
            
            # 保存到两个目录
            fig.savefig(os.path.join(self.ui_dir, image_filename), bbox_inches='tight')
            fig.savefig(os.path.join(self.images_dir, image_filename), bbox_inches='tight')
            
            return (f"<img src='{rel_path}'>", f"图片绝对路径：{os.path.join(self.images_dir, image_filename)}")
            
        except Exception as e:
            return f"❌ 执行失败：{str(e)}"
        finally:
            plt.close('all')
            matplotlib.use(current_backend)

# MCP工具封装部分
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("FigGeneratorServer")

# 创建工具实例
fig_generator = FigGenerator()

@mcp.tool()
async def fig_inter(py_code: str, fname: str = "fig") -> str:
    """
    MCP工具接口：异步生成图表
    :param py_code: Python绘图代码字符串
    :param fname: 图像对象的变量名，默认为"fig"
    :return: 包含图片路径信息的JSON字符串
    """
    try:
        # 异步调用生成图表
        result = await fig_generator.execute_code(py_code, fname)
        
        # 统一返回格式为字符串（MCP工具要求返回字符串）
        if isinstance(result, tuple):
            # 将元组转换为JSON字符串
            return json.dumps({
                "status": "success",
                "html_tag": result[0],
                "absolute_path": result[1]
            }, ensure_ascii=False)
        else:
            # 错误信息直接返回
            return json.dumps({
                "status": "error",
                "message": result
            }, ensure_ascii=False)
            
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"工具调用失败：{str(e)}"
        }, ensure_ascii=False)


if __name__ == "__main__":
    print("启动图表生成MCP服务器...")
    mcp.run(transport='stdio')
