from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv
import re

load_dotenv()

class Settings(BaseSettings):
    bot_token: str
    openrouter_token: str
    yookassa_shop_id: str
    yookassa_secret_key: str
    price: int = 490
    yandex_metrika_counter_id: str = "87546909"
    yandex_metrika_token: str = "y0__xD8q5uiARiwhTsgqcra5hT4ixj2j20LcJo1Zh3ftBPYXWR0Og"  
    support_username: str = "@support"
    database_url: str
    log_level: str = "INFO"
    admin_ids: List[int] = [] 

    class Config:
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if admin_ids_str:
            nums = re.findall(r'\d+', admin_ids_str)
            self.admin_ids = [int(num) for num in nums if num.isdigit()]


settings = Settings()