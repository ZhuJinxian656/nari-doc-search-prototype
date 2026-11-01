# ����̱�ʵϰ���ĵ���������ԭ��

2025.07�C2025.10������˾�ĵ���չ�ļ����� Agent ������̽�����빫˾���ز���� Qwen ģ�͡���Ŀ�����ݽ�Ϊ SophcAgent�����ֿ������ʵϰ�׶����������������������������� SophcAgent ��˾�ڲ�ϵͳ��

## ����

- `file_search.py`��Flask + Whoosh �ļ���/���Ĺؼ��ʼ�����֧�� PDF��DOCX ���ı���ȡ��Ŀ¼�������������������ͳ�ơ�
- `examples/camel_model_demo.py`��ԭʼ CAMEL ˫ Agent ģ�ͽ���ʵ�飨С˵��/����ѧ��ʾ��������δ���ļ������������ӡ�
- `.env.example`��ģ�ͷ�������ռλ��δ������˾��ַ����Կ���ĵ���ʵϰ�ܼǡ����⻷�������������Դ�롣

## ������������

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python file_search.py
```

Ĭ�ϼ��� `127.0.0.1:5000`�������ڱ���ԭ�ͣ��ӿ�δʵ����֤��Ŀ¼���ʸ��롣

```bash
curl -X POST http://127.0.0.1:5000/index -H 'Content-Type: application/json' -d '{"directory":"./sample_documents"}'
curl -X POST http://127.0.0.1:5000/search -H 'Content-Type: application/json' -d '{"query":"robotics","max_results":10}'
curl http://127.0.0.1:5000/stats
```

�����д���ֻ�������ĵ��� `sample_documents` Ŀ¼��`POST /clear` ���������`GET /health` ������״̬��

## �߽�����Դ

���ǹؼ��ʼ���ԭ�ͣ�δʵ����������������ר�÷ִʡ�ɨ��� OCR��Ȩ�޼̳л����� Agent ���ߵ��������ɰ� `.doc` ����֧�֣�Ӧת��Ϊ `.docx`��DOCX ��ȡ��ǰ�����Ƕ��䡣

CAMEL ʾ��������ʷ API д����ԭ�鵵δ�ṩ��ȷ�ϵ������汾�����ܱ�֤���䵱ǰ CAMEL���������������������У�Ҳδ��֤ Qwen �������ӡ�ʹ��ʱ�����ʵ�ʲ�������ģ�Ϳͻ�������Ӧ���͡�

Դ��ֱ������Թ鵵 `owl/owl/examples/file_search.py` �� `project-agent/src/main.py`������ʱͳһ���С��ر� Flask debug������Ĭ�ϼ�����ַ�������� Whoosh ������������� DOCX ��չ���жϡ�ԭʼʵ����˴������Ķ��ֱ��¼������ͨ�ÿ��������Ϊ����ԭ���ɹ���

## 整理验证

2026-11-01 使用 Flask 3.1.2、Whoosh 2.7.4、PyMuPDF 1.26.5、python-docx 1.2.0，在隔离测试目录用合成 TXT 文档验证了 `/health`、`/index`、`/search`、`/stats`、`/clear`。以上接口检查通过；未连接公司 Qwen 服务，未对 CAMEL 历史示例进行集成验证。
