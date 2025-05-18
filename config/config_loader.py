import json
import os

# 配置文件路径
CONFIG_FILE = "config.json"

def load_config():
    """加载保存的配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """保存配置到文件"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)