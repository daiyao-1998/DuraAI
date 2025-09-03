import os,json
from dotenv import load_dotenv
from typing import Dict,Any
class EnvConfig:
    def __init__(self, dotenv_path="./.env"):
        self._load_env_vars(dotenv_path)

    def _load_env_vars(self, dotenv_path):
        load_dotenv(override=True, dotenv_path=dotenv_path)
        self.host = os.environ.get("HOST")
        self.port = os.environ.get("PORT")
        self.user = os.environ.get("USER")
        self.password = os.environ.get("MYSQL_PW")
        self.database = os.environ.get("DB_NAME")
        self.TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
        self.model_name = os.environ.get("model_name")
        self.model_url = os.environ.get("mode_api_url")
        self.api_key = os.environ.get("api_key")
        self.deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.li_api_key = os.environ.get("LI_API_KEY")
        self.li_api_URL_r1 = os.environ.get("LI_API_URL_R1")
        self.li_model_r1 = os.environ.get("LI_MODEL_NAME_R1")
        self.li_api_URL_v3 = os.environ.get("LI_API_URL_V3")
        self.li_model_v3 = os.environ.get("LI_MODEL_NAME_V3")
        self.manage_root_path = os.environ.get("MANAGE_ROOT_PATH", "/data/work/")  # 默认值为 /data/work/
        self.metabath_path = os.environ.get("METABAT_PATH", r"/local_data/BETA_CAE/BETA_CAE_Systems/meta_post_v24.1.5/meta_post64.sh")
        self.font_path = os.environ.get("FONT_PATH", r"/usr/share/fonts/lixiangfont/LiciumFont2022-Light.otf")
        self.images_path = os.environ.get("IMAGES_PATH", "/home/chehejia/agent-chat-ui-main/public/images")
        self.feishu_app_id = os.environ.get("FEISHU_APP_ID")
        self.feishu_app_secret = os.environ.get("FEISHU_APP_SECRET")
        self.li_api_URL_qwen = os.environ.get("LI_API_URL_QWEN")
        self.li_model_qwen = os.environ.get("LI_MODEL_NAME_QWEN")
    

    def load_servers(self,file_path: str ="servers_config.json" ) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f).get("mcpServers", {})


