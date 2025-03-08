FROM python:3.10-slim  

# 设置工作目录  
WORKDIR /app  

# 复制依赖文件  
COPY requirements.txt .  

# 安装依赖  
RUN pip install --no-cache-dir -r requirements.txt  

# 复制项目文件  
COPY . .  

# 暴露端口  
EXPOSE 8000  

# 启动命令  
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]