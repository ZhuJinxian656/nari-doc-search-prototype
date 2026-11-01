# 南瑞继保实习：文档搜索早期原型

2025.07–2025.10，面向公司文档开展文件搜索 Agent 开发，探索接入公司本地部署的 Qwen 模型。项目后续演进为 SophcAgent；本仓库仅整理实习阶段留存的两个早期组件，不包含完整 SophcAgent 或公司内部系统。

## 内容

- `file_search.py`：Flask + Whoosh 文件名/正文关键词检索，支持 PDF、DOCX 和文本提取、目录索引、结果高亮与索引统计。
- `examples/camel_model_demo.py`：原始 CAMEL 双 Agent 模型接入实验（小说家/物理学家示例），尚未与文件搜索服务连接。
- `.env.example`：模型服务配置占位。未包含公司地址、密钥、文档、实习周记、虚拟环境或第三方整包源码。

## 运行搜索服务

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python file_search.py
```

默认监听 `127.0.0.1:5000`。仅用于本地原型，接口未实现认证和目录访问隔离。

```bash
curl -X POST http://127.0.0.1:5000/index -H 'Content-Type: application/json' -d '{"directory":"./sample_documents"}'
curl -X POST http://127.0.0.1:5000/search -H 'Content-Type: application/json' -d '{"query":"robotics","max_results":10}'
curl http://127.0.0.1:5000/stats
```

请自行创建只含测试文档的 `sample_documents` 目录。`POST /clear` 清空索引，`GET /health` 检查服务状态。

## 边界与来源

这是关键词检索原型，未实现向量检索、中文专用分词、扫描件 OCR、权限继承或完整 Agent 工具调用链。旧版 `.doc` 不受支持，应转换为 `.docx`；DOCX 提取当前仅覆盖段落。

CAMEL 示例保留历史 API 写法；原归档未提供可确认的依赖版本，不能保证适配当前 CAMEL。它不在搜索服务依赖中，也未验证 Qwen 服务连接。使用时需根据实际部署适配模型客户端与响应类型。

源码分别整理自归档 `owl/owl/examples/file_search.py` 与 `project-agent/src/main.py`。整理时统一换行、关闭 Flask debug、限制默认监听地址，并修正 Whoosh 清空索引参数与 DOCX 扩展名判断。原始实验与此次整理改动分别记录，不将通用框架能力作为个人原创成果。

## 整理验证

使用 Flask 3.1.2、Whoosh 2.7.4、PyMuPDF 1.26.5 和 python-docx 1.2.0，在隔离目录用合成 TXT 文档验证了健康检查、索引、搜索、统计和清空接口。未连接公司 Qwen 服务，未对 CAMEL 历史示例进行集成验证。
