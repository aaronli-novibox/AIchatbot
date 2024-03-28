# 使用官方Python镜像作为基础镜像
FROM python:3.8-slim

# 设置工作目录为/app
WORKDIR /app

# 将当前目录下的所有文件复制到容器的/app目录
COPY . /app

RUN pip install torch --cache-dir=~/mnt

# 使用pip命令安装依赖
RUN pip install --cache-dir=~/mnt -r requirements.txt

# 告诉Docker容器监听3000端口
EXPOSE 3000

# 定义环境变量
# ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=3000

# 启动Flask应用
CMD flask --app flaskr run
