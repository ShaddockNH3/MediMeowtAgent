# MediMeow Backend - 快速启动指南

## 📁 项目结构

```
MediMeowBackend/
├── app/
│   ├── __init__.py           # 应用初始化
│   ├── models/               # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py          # 用户模型
│   │   ├── doctor.py        # 医生模型
│   │   ├── department.py    # 科室模型
│   │   ├── questionnaire.py # 问卷模型
│   │   ├── submission.py    # 提交记录模型
│   │   └── visit.py         # 就诊记录模型
│   ├── routers/              # API 路由
│   │   ├── __init__.py
│   │   ├── user.py          # 用户相关接口 (/user/*)
│   │   ├── doctor.py        # 医生相关接口 (/doctor/*)
│   │   ├── department.py    # 科室相关接口 (/department/*)
│   │   └── questionnaire.py # 问卷相关接口 (/questionnaires/*)
│   ├── schemas/              # Pydantic 数据模型
│   │   ├── __init__.py
│   │   ├── user.py          # 用户请求/响应模型
│   │   ├── doctor.py        # 医生请求/响应模型
│   │   ├── department.py    # 科室请求/响应模型
│   │   └── questionnaire.py # 问卷请求/响应模型
│   ├── services/             # 业务逻辑层
│   │   ├── __init__.py
│   │   └── ai_service.py    # AI 分析服务 (待集成)
│   └── utils/                # 工具函数
│       ├── __init__.py
│       ├── auth.py          # JWT 认证和授权
│       ├── database.py      # 数据库连接和会话
│       └── responses.py     # 统一响应格式
├── uploads/                  # 文件上传目录
├── logs/                     # 日志文件目录
├── .env.example             # 环境变量示例
├── .gitignore               # Git 忽略文件
├── docker-compose.yml       # Docker Compose 配置
├── Dockerfile               # Docker 镜像构建
├── init.sql                 # 数据库初始化脚本
├── main.py                  # FastAPI 应用入口
├── requirements.txt         # Python 依赖
├── reset_db.sh             # 数据库重置脚本
├── view_data.sh            # 数据查看脚本
├── PROJECT_CHECKLIST.md    # 项目检查清单
└── README.md               # 本文件
```

### 核心模块说明

| 模块 | 功能 | 文件 |
|------|------|------|
| **认证授权** | JWT token 验证、用户身份验证 | `app/utils/auth.py` |
| **数据库** | SQLAlchemy ORM 模型、数据库会话 | `app/models/*`, `app/utils/database.py` |
| **用户管理** | 注册、登录、信息查询、修改 | `app/routers/user.py` |
| **医生管理** | 登录、队列管理、病情摘要 | `app/routers/doctor.py` |
| **问卷系统** | 问卷获取、提交、Excel 导入 | `app/routers/questionnaire.py` |
| **科室管理** | 科室列表查询 | `app/routers/department.py` |
| **AI 服务** | 图片分析、症状识别 (待实现) | `app/services/ai_service.py` |
| **统一响应** | 标准化 API 响应格式 | `app/utils/responses.py` |

## 🚀 快速开始

### 方式一：Docker Compose (推荐)

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 SECRET_KEY 等

# 2. 启动所有服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f backend

# 4. 访问服务
# API: http://localhost:8000
# 文档: http://localhost:8000/docs
```

### 方式二：本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 初始化数据库
./reset_db.sh

# 4. 启动服务
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 环境要求

- Python 3.12+
- MySQL/MariaDB 8.0+
- Docker & Docker Compose (可选)

## 🔧 配置说明

### 必须配置项

```env
# 数据库连接
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/medimoew_db

# JWT 密钥 (生产环境必须修改!)
SECRET_KEY=your-secret-key-change-in-production

# CORS 允许的源
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 可选配置项

```env
# JWT 算法和过期时间
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 文件上传
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
```

## 🧪 测试账号

### 用户账号
| 手机号 | 密码 | 姓名 |
|--------|------|------|
| 13850136583 | ShenMiDaZhi | 凉柚 |
| 13900000002 | 12345678 | 李明 |
| 13900000003 | 12345678 | 王芳 |

### 医生账号
| 用户名 | 密码 | 科室 | 职称 |
|--------|------|------|------|
| 张医生 | doctor123 | 内科 | 主任医师 |
| 李医生 | doctor123 | 儿科 | 副主任医师 |
| 王医生 | doctor123 | 皮肤科 | 主治医师 |

## 📚 API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔍 常用命令

### 数据库管理

```bash
# 重置数据库
./reset_db.sh

# 查看数据
./view_data.sh
```

### Docker 管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f backend

# 重启服务
docker-compose restart backend

# 进入容器
docker-compose exec backend bash
```

### 开发调试

```bash
# 热重载运行
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 查看路由
python -c "from main import app; from fastapi.routing import APIRoute; [print(f'{r.methods} {r.path}') for r in app.routes if isinstance(r, APIRoute)]"

# 生成数据库迁移
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head
```

## 🐛 故障排查

### 数据库连接失败

```bash
# 检查 MySQL 是否运行
mysql -h127.0.0.1 -P3306 -uroot -p123456 -e "SELECT 1"

# 检查数据库是否存在
mysql -h127.0.0.1 -P3306 -uroot -p123456 -e "SHOW DATABASES LIKE 'medimoew_db'"

# 重置数据库
./reset_db.sh
```

### 端口被占用

```bash
# 查看端口占用
lsof -i :8000
netstat -tulpn | grep 8000

# 修改端口
# 编辑 .env 或 docker-compose.yml 中的 BACKEND_PORT
```

### JWT 认证失败

```bash
# 检查 SECRET_KEY 是否配置
echo $SECRET_KEY

# 重新登录获取新 token
curl -X POST "http://localhost:8000/user/login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"13850136583","password":"ShenMiDaZhi"}'
```

### 导入依赖失败

```bash
# 更新 pip
pip install --upgrade pip

# 使用清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 单独安装问题依赖
pip install fastapi uvicorn sqlalchemy pymysql
```

## 📊 健康检查

```bash
# 检查服务健康
curl http://localhost:8000/health

# 预期返回
{"status":"healthy","version":"1.0.0"}
```

## 🔐 安全建议

### 生产环境部署

1. **必须修改 SECRET_KEY**
   ```bash
   # 生成强密钥
   openssl rand -hex 32
   ```

2. **使用环境变量管理敏感信息**
   - 不要将 .env 文件提交到版本控制
   - 使用 Docker Secrets 或环境变量注入

3. **配置 HTTPS**
   - 使用 Nginx 配置 SSL 证书
   - 启用 HSTS

4. **限制 CORS**
   - 只允许可信域名
   - 不要使用 `*` 通配符

5. **数据库安全**
   - 使用强密码
   - 限制数据库访问 IP
   - 定期备份

## 📝 日志位置

- 应用日志: `./logs/app.log`
- Docker 日志: `docker-compose logs`
- 数据库日志: `/var/log/mysql/` (容器内)

## 🔄 更新部署

```bash
# 拉取最新代码
git pull

# 重建镜像
docker-compose build

# 重启服务
docker-compose up -d

# 执行数据库迁移 (如果有)
docker-compose exec backend alembic upgrade head
```

## 💡 开发建议

1. 使用 `.env.example` 作为环境配置模板
2. 开发时使用 `--reload` 模式
3. 定期运行 `./reset_db.sh` 重置测试数据
4. 使用 Swagger UI 测试 API
5. 查看 `PROJECT_CHECKLIST.md` 了解项目完整状态

## 📧 问题反馈

如遇到问题，请提供：
- 错误日志
- 环境信息 (Python 版本、系统版本)
- 复现步骤
- 配置文件 (移除敏感信息)

## 🎯 下一步

1. 阅读 API 文档: http://localhost:8000/docs
2. 查看测试数据: `./view_data.sh`
3. 测试 API 接口: 参考 `API_TEST_GUIDE.md`
4. 了解数据库结构: 参考 `DATABASE_GUIDE.md`
