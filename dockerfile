# 使用官方Python镜像作为基础镜像
FROM python:3.8

# 设置工作目录为/app
WORKDIR /app

COPY requirements.txt /app/requirements.txt

# 使用pip命令安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将当前目录下的所有文件复制到容器的/app目录
COPY . /app

# 告诉Docker容器监听3000端口
EXPOSE 3000

# 定义环境变量
# ENV FLASK_APP=flaskr:create_app
# ENV FLASK_RUN_HOST=0.0.0.0
# ENV FLASK_RUN_PORT=3000

# 运行 Gunicorn 服务器来启动 Flask 应用
CMD gunicorn -w 1 -b 0.0.0.0:3000 "flaskr:create_app()"
# CMD flask run
