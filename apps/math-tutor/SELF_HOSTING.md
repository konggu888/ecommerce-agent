# 自有服务器部署（Docker Compose）

这是数学小老师项目的自托管运行骨架。Netlify 不是运行依赖；GitHub 仅用于代码托管和 CI。

## 当前能力边界

- 前端由 Nginx 提供静态文件，/api/* 反向代理到同一 Compose 私有网络内的 FastAPI。
- FastAPI 使用 /data/math_tutor.sqlite3；SQLite 文件放在命名卷 math-tutor-data 中，容器重建不会自动删除该卷。
- 后端端口不直接发布到宿主机。
- Web 默认只绑定宿主机 127.0.0.1:8080，可用 MATH_TUTOR_PORT 更改本机端口。
- **目前仍是早期骨架，没有家长/学生登录鉴权，也没有完整学习业务 API。不得把它直接公开到互联网。** 在接入公网之前，必须完成身份验证/访问控制、HTTPS、备份与恢复演练、日志脱敏和安全测试。

## 在自己的 Linux 服务器进行本机烟雾测试

前提：服务器已安装 Docker Engine 与 Docker Compose v2，仓库已克隆到服务器。不要把 .env、API 密钥、数据库凭据提交到 Git。

从仓库根目录执行：

    docker compose -f apps/math-tutor/docker-compose.yml config
    docker compose -f apps/math-tutor/docker-compose.yml up -d --build
    docker compose -f apps/math-tutor/docker-compose.yml ps
    curl --fail http://127.0.0.1:8080/healthz
    curl --fail http://127.0.0.1:8080/api/health

第二个请求应返回 FastAPI 健康 JSON。此结果只证明容器启动和健康接口，不证明数学学习功能已交付。

查看日志：

    docker compose -f apps/math-tutor/docker-compose.yml logs --tail=100

停止服务但保留数据卷：

    docker compose -f apps/math-tutor/docker-compose.yml down

只有在明确要删除所有本地学习数据时，才执行带 -v 的 down 命令。执行前必须先备份并确认目标卷。

## 对外发布前的硬性门槛

1. 实现并测试认证、会话安全和授权边界。
2. 配置域名、HTTPS、反向代理和防火墙；不要直接公开未鉴权的端口。
3. 建立 SQLite 一致性备份、异机保存、恢复演练和保留策略。
4. 确认上传文件大小/类型限制、儿童数据删除/导出、日志脱敏。
5. 配置服务端 AI 密钥；不得放进 Vue 环境变量或浏览器构建产物。
6. 在目标服务器实际执行上述命令并记录系统版本、部署 SHA、测试输出；CI 通过不等于已部署到用户服务器。

## 未来数据库迁移

当前部署骨架使用 SQLite，适合单机、早期私用和开发验证。若后续切换 PostgreSQL 或其他数据库，需实现并测试可重复迁移、备份恢复与并发行为；不依赖 Netlify 或 Supabase 专有托管功能。
