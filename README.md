

# MiddleAPI

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.10+-brightgreen.svg)
![Framework](https://img.shields.io/badge/framework-FastAPI-critical.svg)

一个为 [GPT-Sovits](https://github.com/RVC-Boss/GPT-SoVITS) 等语音模型设计的中间件（Middleware），旨在无缝对接到 [OpenWebUI](https://github.com/open-webui/open-webui) 和 [mindcraft](https://github.com/mindcraft-bots/mindcraft) 等应用，并提供一个简洁的 Web UI 来动态调整推理参数。



## 目录

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [系统架构](#系统架构)
- [部署指南](#部署指南)
  - [环境要求](#环境要求)
  - [本地开发启动](#本地开发启动)
  - [生产环境部署](#生产环境部署-推荐)
    - [使用 Uvicorn/Gunicorn](#使用-uvicorngunicorn)
    - [使用 Nginx 反向代理](#使用-nginx-反向代理)
- [API 文档](#api-文档)
- [项目结构](#项目结构)
- [未来计划 (Roadmap)](#未来计划-roadmap)
- [已知问题与不足](#已知问题与不足)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [致谢](#致谢)

## 项目简介

`MiddleAPI` 的核心目标是在不修改上游应用（如 OpenWebUI）和下游模型服务（如 GPT-Sovits）源代码的前提下，充当一个智能“适配器”。它拦截、处理并转发请求，同时将复杂的模型参数配置通过一个友好的 Web 界面暴露出来，极大地简化了集成和调试过程。

## 核心功能

- ✨ **TTS 推理接口**：提供标准的 TTS API 接口 (`/audio/speech`)，并内置音频缓存机制，减少重复生成。
- 🔌 **API 代理**：作为 OpenAI 格式的代理，可将请求转发到任何兼容的外部 API 服务。
- ⚙️ **动态配置管理**：通过 Web UI 实时调整所有 TTS 相关参数，无需重启服务。配置持久化到 `config.yaml`。
- 🗑️ **智能音频清理**：提供自动和手动的音频缓存文件清理功能，防止磁盘空间滥用。
- 🖥️ **现代化 Web UI**：基于 FastAPI 和 Bulma 构建，提供直观的设置、音频列表、清理等管理页面。
- 🧩 **模块化设计**：代码结构清晰，功能高度解耦，易于二次开发和功能扩展。

## 系统架构

![System Architecture Diagram](https://www.plantuml.com/plantuml/png/RLJVJnfB67tVlsAkBnSIXPlRDsE8Q69heWafcAQnFWpB53PT5i8kHjBuWiNQAcXRVzHMssAr9Mr5ZR5OgFhFx2pmN_HRFbbsj3wPCzyvP_QRSnZM3PeniabL-iT8i2GZiqeqGpL3aj9KVaBZZFGrrolMKisixvlrrttagKJWZyf6AaFmf0DCFs1HCZLEFDRPQklh4j-kU6S8rGd0W0uDUSRwLIMUCA9gbda30MdUPJ2fn68g2uR62Q-lWsRNP7gCwaO7NYirlnyzqZpEf2-TG_qH465Qp7OOGOTuXZ7DjkXeE2RMJf6_BFEJV5Uzus0sFZVN5l4Cz4EPr5mkp3ApYimS2pVOOzxDq9YI8f58cF3g7gm1RuZmbA6ekYE0sAYgCDYhJPw_SJTUE-25cbKfyzqjuNhjGh5vKSLZ41zDQO-Lk2ZkmdeyQ-k0Nsqvl8dK3P8DY0p-fWZBTnZtcPvEQJeJQGugSaEv62H6aOdz1H-MWTv5H7eF5I-x-TpQ-U5OHzYS8V8S19SdPCVQEBQALVEyn0_VyhmJdHWrQ9JgC21tzkFBqQJQrzlNcAAo6uFsIxO_dhRtNdMbO3gOXPSBGzR1JF3b-vljXGe61qt5JE39Z9tBS3_GjRWTUnn3BWcE4oTuvkKo_v8dDAtuxlptFrLyikQzHGR_Vyd0m03XXTFcQODNtvc_NjY0X4M4VmFNXHiahQlthV8AjbQI48Lpfp23v5ua4Y9slLh72o00jsYLQdnrirq-Q-_kzHDhTGtek62l97M9829K0fI0RTPBn2ydgE6NKycqoWm5WkBc22rmSQYzOR-UPanE2FD2s830zvz1LJ6dmg0GAnYqFfNRtrPQHpNh92yCkgfYB-YeuUUBsrWnOGxRWKFLOtwnWNMI9E6pnMLw-6817fN_pbk71xXGY85NfFXyWTklFmDi_1cwlh8aR0euOh0S4hhWErkb2WW8pBz_Chnlgte9NtnxrgcPlSFp0kXXCtjF3tSH6c4_OxKCWzWR63SRFoMt9p1SZUjjdJmCJawGQu8q3EBPfFe7)

系统主要由 **Web UI (前端)**, **FastAPI (后端)**, **工具模块**, **外部服务 (Gradio 和 AI API)**, 和 **数据存储 (配置文件和音频缓存)** 构成。用户通过 Web UI 与 FastAPI 后端交互，后端通过 `GradioUtils` 调用 GPT-Sovits 服务，通过 `ProxyService` 代理 AI 请求，并通过 `ConfigUtils` 管理配置。

## 部署指南

### 环境要求

1.  **Python**: 3.10或以上
2.  **OpenWebUI**: 请确保OpenWebUI正确配置，见[此处](https://www.yuque.com/deckdes/vl0k6z/mbssaorn5phock0l#tBHLz)
3.  **GPT-SoVITS webui 推理服务**: 一个正在运行的 **GPT-SoVITS-WebUI** 实例，并确保其 API (`:9872`) 可从 MiddleAPI 服务器访问。
4.  **依赖**: `pip install -r requirements.txt`

### 本地开发启动

适用于快速测试和开发。

```bash
# 安装所有依赖
pip install -r requirements.txt

# 启动服务 (开启热重载)
uvicorn MiddleAPI:app --host 0.0.0.0 --port 8000 --reload
```
在浏览器中访问 `http://localhost:8000`。

### 生产环境部署 (推荐)

#### 使用 Uvicorn/Gunicorn

使用专业的应用服务器来运行，以获得更好的性能和稳定性。

```bash
# 启动4个工作进程
uvicorn MiddleAPI:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 使用 Nginx 反向代理

建议在 `uvicorn` 前面配置一个反向代理服务器（如 Nginx），用于处理 HTTPS、负载均衡、静态文件服务等。

**Nginx 配置示例 (`/etc/nginx/sites-available/middleapi`)**:
```nginx
server {
    listen 80;
    server_name your_domain.com; # 替换为你的域名

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## API 文档

| 方法      | API                                  | 功能                 | 请求体/查询参数          |
| :-------- | :----------------------------------- | :------------------- | :----------------------- |
| `GET`     | `/`                                  | 访问 Web UI 首页     | `?html=page.html` (可选) |
| `POST`    | `/audio/speech`                      | TTS 推理             | JSON (`input`, `voice`)  |
| `POST`    | `/chat/completions`                  | 代理 OpenAI 格式请求 | JSON (OpenAI format)     |
| `POST`    | `/app/setconfig`                     | 设置单个或多个配置项 | JSON (`section`, `key`, `value`) |
| `GET/POST`| `/app/getconfig`                     | 读取配置项           | JSON/Query (`section`, `key`) |
| `POST`    | `/app/resetconfig`                   | 重置为默认配置       | JSON (`confirm: true`)   |
| `POST`    | `/audio/cleanup`                     | 清理音频文件         | Query (`keep_last=N`)    |
| `GET`     | `/audio/list`                        | 获取音频文件列表     | 无                       |


## 项目结构
```
MiddleAPI/
├── MiddleAPI.py                  # 主程序入口，定义 FastAPI 应用和路由
├── README.md                     # 本文档
├── requirements.txt              # Python 依赖列表
├── config/                       # 配置文件目录
│   ├── config.example            # 配置文件示例
│   └── tts_audio_storage/        # TTS 音频缓存目录
└── utils/                        # 工具模块存放区
│   ├── GradioUtils.py            # Gradio 客户端封装，负责调用 TTS 模型
│   ├── ProxyService.py           # API 代理服务逻辑
│   ├── PydanticUtils.py          # Pydantic 数据模型，用于请求体验证
│   ├── ResponseUtils.py          # 统一的 API 响应和错误处理工具
│   ├── TextUtils.py              # 文本清理和格式转换工具
│   ├── ConfigUtils.py            # 配置文件 (YAML) 读写管理工具
│   └── LogUtils.py               # 日志配置和管理工具
└── www/                          # 静态 Web 资源目录
    ├── files/                    # CSS, JS, 图片等静态资源
    ├── index.html                # 主页
    ├── settings.html             # 设置页面
    ├── audiolist.html            # 音频列表页面
    ├── cleanup.html              # 音频清理页面
    └── ...                       # 其他 HTML 页面
```

## 未来计划 (Roadmap)
- [ ] **用户认证系统**：为 Web UI 和 API 添加可选的登录认证。
- [ ] **WebSocket 支持**：为前端提供实时的日志或状态更新。
- [ ] **更完善的前端**：使用 Vue/React 等现代框架重构前端，提升交互体验。
- [ ] **单元与集成测试**：增加测试用例，保证代码质量和稳定性。
- [ ] **插件化支持**：允许用户通过插件扩展更多类型的模型服务。

## 已知问题与不足
- **安全**: 当前版本没有任何形式的用户认证，请勿直接暴露在公网上。建议使用 Nginx 等反向代理并配置身份验证。
- **功能实现**: 部分功能（如上传参考音频）暂未实现，将在后续根本更新。

## 贡献指南

我们欢迎任何形式的贡献！无论是提交 Issue、修复 Bug 还是实现新功能。

1.  **Fork** 本仓库。
2.  创建您的特性分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4.  将您的分支推送到远程仓库 (`git push origin feature/AmazingFeature`)。
5.  创建一个 **Pull Request**。

请确保您的代码遵循现有风格，并为新功能添加必要的注释。

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

## 致谢

感谢所有贡献者和开源社区的支持！