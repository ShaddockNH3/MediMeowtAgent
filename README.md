# MediMeowtAgent
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-0-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<p align="center">
<!-- 这里你可以放上你们超棒的Logo图片URL -->
<img src="docs/img/logo.png" width="150" alt="MedMind Logo">
</p>

<p align="center">
  <strong>基于LLM智能体的医院预诊系统</strong>
  <br>
  <em>“让信息多跑路，让医生少写字。” — “让 AI 先问诊，让医生更专注。”</em>
</p>

<p align="center">
<img src="https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vuedotjs" alt="Vue.js">
<img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi" alt="FastAPI">
<img src="https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?logo=pytorch" alt="PyTorch">
</p>

## 🎯 项目简介 (Introduction)

**MedMind (医智)** 是一款基于大语言模型（LLM）的智能预诊与病历生成系统。它致力于帮助医院实现“AI辅助采集病情 → 医生快速审核诊断”的高效闭环，将医生从繁琐的重复性文书工作中解放出来，让他们能更专注于诊断与治疗本身。

## 😫 解决的痛点 (The Problem)

* **医生端**: 需花费大量时间进行重复性问询和繁琐的病历录入，有效诊疗时间被压缩。
* **患者端**: 候诊时间长，面诊时紧张，常常无法规范、完整地描述病情。
* **机构端**: 临床文书多为非结构化数据，导致“信息孤岛”，数据难以复用。

## 💡 核心流程 (Core Flow)

我们的解决方案是一个**三阶段AI分析流程**，实现多模态输入、RAG检索和结构化病历生成：

### 阶段一：多模态描述输入

此阶段通过多种方式收集患者的病情信息。

1. **患者输入**: 患者填写问卷，使用自然语言描述症状，支持文本、图片等多模态输入。
2. **AI 预处理**: 系统对输入进行初步分析和实体识别。

### 阶段二：RAG检索增强

基于输入信息进行智能检索和知识增强。

1. **RAG检索**: 使用LangChain和Chroma向量数据库，根据患者描述检索相关医学知识库。
2. **知识融合**: 将检索到的医学文档与患者信息进行融合，为后续生成提供依据。

### 阶段三：结构化病历生成

生成规范化的医疗病历。

1. **LLM推理**: 基于zhipuGLM模型，结合检索结果生成结构化病历内容。
2. **医生审核**: AI生成草稿后，由医生进行最终审核和完善，形成权威病历。

## 🏗️ 系统架构 (Architecture)

本项目采用五层分层架构，确保系统的高内聚、低耦合与高可扩展性。

**(系统架构图)**
<!-- ![系统架构图](./docs/img/architecture.svg) -->
<img src="./docs/img/architecture.svg" alt="系统架构图" width="600px">

* **用户交互层**: `Web患者端` 和 `医生审核界面`。
* **API网关层**: `HTTP Handler` 和 `gRPC Client` (内部通信)。
* **应用服务层**: `对话状态管理器` 和 `实体抽取服务`。
* **数据层**: `业务数据库 (MariaDB)` 和 `向量数据库 (Chroma)`。
* **AI 核心层**: `zhipuGLM (LLM Core)` 和 `RAG 检索增强模块`。

## 🛠️ 技术栈 (Tech Stack)

### 前端 (Frontend)
- **Vue 3**: 现代化的渐进式JavaScript框架
- **Vite**: 快速的构建工具和开发服务器
- **Tailwind CSS**: 实用优先的CSS框架

### 后端 (Backend)
- **FastAPI**: 现代化的高性能Web框架
- **SQLAlchemy**: Python SQL工具包和ORM
- **MySQL**: 关系型数据库管理系统

### AI服务 (AI Services)
- **LangChain**: 用于构建LLM应用的框架
- **Chroma**: 向量数据库，用于RAG检索
- **zhipuGLM**: 智谱GLM大语言模型
- **gRPC**: 高性能RPC框架，用于服务间通信

## 🚀 快速开始 (Getting Started)

在linux环境下，使用python3.12.3

### 1. 配置环境变量

**后端配置** (`MediMeowBackend/.env`)
```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/MediMeow_db
SECRET_KEY=your-secret-key-here-change-in-production
```

**AI服务配置** (`MediMeowAI/.env`)
```env
GLM_API_KEY=your_glm_api_key_here
```

### 2. 启动后端服务

```bash
cd MediMeowBackend
python3 -m venv venv-backend
source venv-backend/bin/activate
pip install -r requirements.txt

# 初始化数据库
bash init_db.sh

# 启动服务
python run.py
```

### 3. 启动AI服务

```bash
cd MediMeowAI
python3 -m venv venv-ai
source venv-ai/bin/activate
pip install -r requirements.txt

export HF_ENDPOINT=https://hf-mirror.com

# 启动服务
python ai.py
```

### 4. 启动前端

```bash
cd MediMeowFrontend
npm install
npm run dev
```

### 测试账号

- **医生**: 用户名为科室名(如`儿科`)，密码 `123`
- **患者**: 自行注册

## Contributors ✨

[CONTRIBUTER](/docs/CONTRIBUTER.md)
