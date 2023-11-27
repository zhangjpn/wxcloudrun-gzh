import os

# 是否开启debug模式
DEBUG = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# openai
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# 读取数据库环境变量
username = os.environ.get("MYSQL_USERNAME", 'root')
password = os.environ.get("MYSQL_PASSWORD", 'root')
db_address = os.environ.get("MYSQL_ADDRESS", '127.0.0.1:3306')
