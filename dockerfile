# 使用官方 Node.js 镜像作为基础镜像
FROM node:latest

# 设置工作目录
WORKDIR /app

# 将应用程序的依赖项安装到容器中
COPY package*.json ./
RUN npm install

# 将应用程序源代码复制到容器中
COPY . .

# 暴露容器内应用程序运行的端口（如果有需要的话）
EXPOSE 3000

# 定义容器启动时运行的命令
CMD ["npm", "start"]
