# MiddleAPI

## 简介

MiddleAPI 是一个中间层 API，旨在不更改 OpenWeb UI 和 mindcraft 源代码的前提下，将 GPT-Sovits 接入 OpenWeb UI TTS 以及与mindcraft交互，并提供一个简单的 WEB UI 进行参数调节。它支持多种功能，包括 TTS 推理、API 代理、配置管理、音频清理等。

## 功能特点

- **TTS 推理**：支持文本到语音的转换，提供多种语言和语音选项。
- **API 代理**：代理外部 API 请求，支持自定义配置。
- **配置管理**：通过 WEB UI 或 API 动态调整 TTS 参数。
- **音频清理**：自动清理旧音频文件，支持自定义保留文件数量。
- **WEB UI**：提供直观的用户界面，支持多种页面（主页、设置、音频列表、清理等）。
- **模块化设计**：易于扩展和维护。

## 快速开始

### 安装依赖

确保安装以下依赖：

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
uvicorn MiddleAPI:app --host 0.0.0.0 --port 8000
```

### 访问 WEB UI

打开浏览器访问：[http://localhost:8000](http://localhost:8000)

## API 文档

### Web UI

#### 路径
| 方法  |          API          |   功能   | 请求体 |
|:---:|:---------------------:|:------:|:---:|
| GET | http://localhost:8000 | Web UI |  无  |

### TTS 推理

#### 路径
|  方法  |                 API                 |   功能   | 请求体  |
|:----:|:-----------------------------------:|:------:|:----:|
| POST | http://localhost:8000/audio/speech | TTS推理 | JSON |

#### 请求体
|  参数   |  值   |
|:-----:|:----:|
| input | 输入文本 |
| voice | 目标语言 |

#### 示例请求
```json
{
  "input": "你好，欢迎使用 MiddleAPI！",
  "voice": "中文"
}
```

#### 响应
```json
{
  "status": "success",
  "code": 200,
  "message": "音频生成成功",
  "data": {
    "file_path": "/files/audio_12345.wav"
  }
}
```

### TTS 推理参数读取

#### 路径
|  方法  |                 API                 |   功能   | 请求体  |
|:----:|:-----------------------------------:|:------:|:----:|
| POST | http://localhost:8000/app/getconfig | TTS推理参数读取 | JSON |

#### 请求体
|   参数    |   值   |
|:-------:|:-----:|
| section | 配置节点名 |
|   key   |  配置名  |

#### 示例请求
```json
{
  "section": "gpt",
  "key": "temperature"
}
```

#### 响应
```json
{
  "status": "success",
  "code": 200,
  "value": 0.65
}
```

### TTS 推理参数设置

#### 路径
|  方法  |                 API                 |   功能   | 请求体  |
|:----:|:-----------------------------------:|:------:|:----:|
| POST | http://localhost:8000/app/setconfig | TTS推理参数设置 | JSON |

#### 请求体
|   参数    |   值   |
|:-------:|:-----:|
| section | 配置节点名 |
|   key   |  配置名  |
|  value  |  配置值  |

#### 示例请求
```json
{
  "section": "gpt",
  "key": "temperature",
  "value": 0.8
}
```

#### 响应
```json
{
  "status": "success",
  "code": 200,
  "message": "参数设置成功",
  "updated": 1
}
```

### 音频清理

#### 路径
|  方法  |                 API                 |   功能   | 请求体  |
|:----:|:-----------------------------------:|:------:|:----:|
| POST | http://localhost:8000/audio/cleanup | 音频清理 | JSON |

#### 请求体
|   参数    |   值   |
|:-------:|:-----:|
| keep_last | 保留的文件数量 |

#### 示例请求
```json
{
  "keep_last": 5
}
```

#### 响应
```json
{
  "status": "success",
  "code": 200,
  "message": "音频清理成功",
  "data": {
    "keep_last": 5
  }
}
```

## 配置文件说明

配置文件位于 `config.yaml`，以下是默认配置：

```yaml
cutting:
  cutting_mode: Slice once every 4 sentences
global:
  use_new_api: false
gpt:
  temperature: 0.4
  top_k: 15
  top_p: 0.6
  speed: 1
  if_freeze: false
reference:
  no_reference_mode: false
  reference_audio_local: ''
  reference_audio_url: https://fs-im-kefu.7moor-fs1.com/ly/4d2c3f00-7d4c-11e5-af15-41bf63ae4ea0/1739002890857/audio.wav
  reference_audio_language: Chinese
  reference_audio_text: 阿米娅看上去还是这么瘦弱，这个年纪的孩子，个子是不是应该更高一点才对？她到底有没有好好吃饭呢。
  inp_refs: null
inference:
  inference_text_language: 中英混合
minecraft_api_key:
  minecraft_api_key: sk-12345678abcdefhg12345678abcdefhg12345678abcdefhg
mode:
  mode: tts
```

## 二次开发

### 克隆项目

```bash
git clone git@github.com:LynchPin1634/MiddleAPI.git
```

### 项目结构

```
MiddleAPI/
├── MiddleAPI.py              # 主程序
└── utils/                    # 功能存放区
    ├── GradioUtils.py        # Gradio 客户端工具
    ├── ProxyService.py       # API 代理服务
    ├── PydanticUtils.py      # 数据模型定义
    ├── ResponseUtils.py      # 响应处理工具
    ├── TextUtils.py          # 文本处理工具
    ├── ConfigUtils.py        # 配置文件管理工具
├── requirements.txt      # 依赖文件
├── config.yaml           # 配置文件
└── www/                  # 静态资源目录
    ├── index.html        # 主页
    ├── settings.html     # 设置页面
    ├── audio_list.html   # 音频列表页面
    ├── cleanup.html      # 音频清理页面
    ├── abyss.html        # Abyss 页面
    └── lynchpin.html     # LynchPin 页面
      └── files/*         # 网页资源目录
    
```

### 自定义功能

1. **添加新路由**：在 `MiddleAPI.py` 中注册新路由。
2. **扩展工具类**：在 `GradioUtils.py` 或其他工具文件中添加新功能。
3. **更新配置**：在 `ConfigUtils.py` 中添加新的配置项。

## FAQ

### 如何更改 TTS 语音？

1.通过网页交互

2.通过 `/audio/speech` API 的 `voice` 参数指定语音类型，例如 `"中文"` 或 `"英文"`。

### 如何清理旧音频？

1.通过网页交互

2.使用 `/audio/cleanup` API，设置 `keep_last` 参数为需要保留的文件数量。

### 如何重置配置？

1.通过网页交互

2.使用 `/app/resetconfig` API，发送 POST 请求并确认重置。

## 致谢

感谢所有贡献者和开源社区的支持！
