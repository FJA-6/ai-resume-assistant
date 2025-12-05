# AI简历助手

基于Flask和纯HTML/CSS/JavaScript的全栈AI简历助手应用，提供简历上传、AI分析和面试题目生成功能。

## 功能特性

- 用户注册和登录
- PDF简历上传和解析（支持拖拽上传）
- AI简历分析（使用阿里云千问）
- 智能面试题目生成
- 现代化的Web界面
- RESTful API接口

## 技术栈

### 后端
- Flask 3.0.0
- SQLAlchemy（数据库ORM）
- DashScope（阿里云千问API）
- PyPDF2（PDF解析）

### 前端
- 纯HTML5
- CSS3（响应式设计）
- 原生JavaScript（ES6+）
- Fetch API（HTTP请求）

## 快速开始

### 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 启动应用

```bash
# 运行Flask服务器
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 访问应用

启动成功后，在浏览器中访问：`http://localhost:5000`

应用会自动跳转到登录页面：`http://localhost:5000/login.html`

### 页面路由

- `/` - 首页（自动跳转到登录页）
- `/login.html` - 登录页面
- `/register.html` - 注册页面
- `/dashboard.html` - 用户仪表板（需要登录）
- `/resume.html?id=<resume_id>` - 简历详情页（需要登录）

## API接口文档

### 1. 用户注册
- **URL**: `/api/register`
- **方法**: `POST`
- **请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```
- **响应**: 返回用户信息

### 2. 用户登录
- **URL**: `/api/login`
- **方法**: `POST`
- **请求体**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```
- **响应**: 返回用户信息

### 3. 上传简历
- **URL**: `/api/upload-resume`
- **方法**: `POST`
- **请求类型**: `multipart/form-data`
- **参数**:
  - `file`: PDF文件
  - `user_id`: 用户ID
- **响应**: 返回简历信息

### 4. 分析简历
- **URL**: `/api/analyze-resume/<resume_id>`
- **方法**: `POST`
- **响应**: 返回分析结果

### 5. 生成面试题目
- **URL**: `/api/generate-questions/<resume_id>`
- **方法**: `POST`
- **请求体**（可选）:
```json
{
  "num_questions": 10
}
```
- **响应**: 返回生成的题目列表

### 6. 获取用户简历列表
- **URL**: `/api/resumes/<user_id>`
- **方法**: `GET`
- **响应**: 返回简历列表

### 7. 获取简历的面试题目
- **URL**: `/api/questions/<resume_id>`
- **方法**: `GET`
- **响应**: 返回题目列表

## 数据库模型

- **User**: 用户表
- **Resume**: 简历表
- **InterviewQuestion**: 面试题目表

## 项目结构

```
ai-helper/
├── app.py                  # Flask主应用
├── config.py               # 配置文件
├── models.py               # 数据库模型
├── routes.py               # API路由
├── ai_service.py           # AI服务（简历分析和题目生成）
├── utils.py                # 工具函数（PDF解析等）
├── requirements.txt        # Python依赖
├── templates/              # HTML模板
│   ├── login.html         # 登录页面
│   ├── register.html      # 注册页面
│   ├── dashboard.html     # 仪表板页面
│   └── resume.html        # 简历详情页面
├── static/                 # 静态文件
│   ├── css/
│   │   └── style.css      # 样式文件
│   └── js/
│       ├── api.js         # API调用封装
│       ├── auth.js        # 登录注册逻辑
│       ├── dashboard.js   # 仪表板逻辑
│       └── resume.js       # 简历详情逻辑
└── uploads/               # 上传文件存储目录（自动创建）
```

## 使用流程

1. **注册账号** → 访问注册页面，填写用户名、邮箱和密码
2. **登录系统** → 使用注册的账号登录
3. **上传简历** → 在仪表板页面点击或拖拽上传PDF简历
4. **查看详情** → 点击简历列表中的"查看详情"按钮
5. **分析简历** → 在简历详情页点击"开始分析"按钮
6. **生成题目** → 设置题目数量，点击"生成题目"按钮

## 注意事项

1. `uploads` 目录会在首次上传文件时自动创建
2. API密钥已配置在 `config.py` 中，生产环境建议使用环境变量
3. 数据库使用SQLite，生产环境建议使用PostgreSQL或MySQL
4. 前端使用原生JavaScript，无需构建工具，直接通过Flask提供静态文件服务
5. 用户登录状态通过localStorage保存在浏览器本地

