import os
import fitz  # fitz
from docx import Document
from pathlib import Path
from datetime import datetime
from whoosh import index
from whoosh.writing import CLEAR
from whoosh.fields import Schema, TEXT, ID, DATETIME, NUMERIC
from whoosh.analysis import StandardAnalyzer
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.highlight import highlight, ContextFragmenter, HtmlFormatter
from flask import Flask, request, jsonify

class WhooshFileSearcher:
    def __init__(self, index_dir="file_index"):
        self.index_dir = index_dir
        self.schema = Schema(
            filepath=ID(stored=True, unique=True),
            filename=TEXT(stored=True, analyzer=StandardAnalyzer()),
            content=TEXT(stored=True,analyzer=StandardAnalyzer()),
            file_type=ID(stored=True),
            file_size=NUMERIC(stored=True),
            modified_at=DATETIME(stored=True)
        )
        self.ix = self.create_or_open_index()
    
    def create_or_open_index(self):
        """创建或打开索引"""
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
        
        if index.exists_in(self.index_dir):
            return index.open_dir(self.index_dir)
        else:
            return index.create_in(self.index_dir, self.schema)
    
    def extract_text_from_file(self, file_path):
        """从不同类型文件提取文本"""
        ext = Path(file_path).suffix.lower()
        
        try:
            if ext == '.pdf':
                return self.extract_pdf_text(file_path)
            elif ext == '.docx':
                return self.extract_docx_text(file_path)
            elif ext in ['.txt', '.py', '.js', '.html', '.css', '.md', '.json', '.xml']:
                return self.extract_text_file(file_path)
            else:
                return ""
        except Exception as e:
            print(f"提取文本失败 {file_path}: {e}")
            return ""
    
    def extract_pdf_text(self, file_path):
        """提取PDF文本"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            return text
        except Exception as e:
            print(f"PDF提取失败 {file_path}: {e}")
            return ""
    
    def extract_docx_text(self, file_path):
        """提取Word文档文本"""
        try:
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"DOCX提取失败 {file_path}: {e}")
            return ""
    
    def extract_text_file(self, file_path):
        """提取纯文本文件"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin1', 'cp1252']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        return ""
    
    def index_directory(self, directory_path, update_existing=True):
        """索引整个目录"""
        directory_path = Path(directory_path)
        writer = self.ix.writer()
        
        indexed_count = 0
        skipped_count = 0
        
        try:
            for file_path in directory_path.rglob('*'):
                if file_path.is_file() and not self.should_skip_file(file_path):
                    try:
                        # 检查文件是否已存在且未修改
                        if not update_existing and self.is_file_indexed(str(file_path)):
                            skipped_count += 1
                            continue
                        
                        content = self.extract_text_from_file(file_path)
                        stat = file_path.stat()
                        
                        writer.update_document(
                            filepath=str(file_path),
                            filename=file_path.name,
                            content=content,
                            file_type=file_path.suffix.lower(),
                            file_size=stat.st_size,
                            modified_at=datetime.fromtimestamp(stat.st_mtime)
                        )
                        
                        indexed_count += 1
                        if indexed_count % 100 == 0:
                            print(f"已索引 {indexed_count} 个文件...")
                        
                    except Exception as e:
                        print(f"索引失败 {file_path}: {e}")
                        skipped_count += 1
            
            writer.commit()
            print(f"索引完成: {indexed_count} 个文件已索引, {skipped_count} 个文件跳过")
            
        except Exception as e:
            writer.cancel()
            raise e
        
        return {"indexed": indexed_count, "skipped": skipped_count}
    
    def should_skip_file(self, file_path):
        """判断是否跳过文件"""
        skip_dirs = {'__pycache__', '.git', 'node_modules', '.DS_Store', 
                    '.vscode', '.idea', 'build', 'dist', 'target'}
        skip_extensions = {'.exe', '.dll', '.so', '.dylib', '.bin', '.iso', 
                          '.img', '.dmg', '.zip', '.rar', '.7z'}
        
        # 跳过特定目录
        if any(part in skip_dirs for part in file_path.parts):
            return True
        
        # 跳过特定扩展名
        if file_path.suffix.lower() in skip_extensions:
            return True
        
        # 跳过大文件 (超过50MB)
        try:
            if file_path.stat().st_size > 50 * 1024 * 1024:
                return True
        except:
            return True
        
        # 跳过隐藏文件
        if file_path.name.startswith('.'):
            return True
        
        return False
    
    def is_file_indexed(self, filepath):
        """检查文件是否已被索引"""
        with self.ix.searcher() as searcher:
            results = searcher.documents(filepath=filepath)
            return len(list(results)) > 0
    
    def search(self, query_text, max_results=100):
        """搜索文件"""
        with self.ix.searcher() as searcher:
            # 创建多字段查询解析器
            query_parser = MultifieldParser(
                ["filename", "content"], 
                schema=self.ix.schema
            )
            
            query = query_parser.parse(query_text)
            
            # 执行搜索
            results = searcher.search(query, limit=max_results)
            
            # 格式化结果
            formatted_results = []
            for result in results:
                # 获取高亮片段
                highlights = {}
                if result['content']:
                    highlights['content'] = result.highlights('content', top=3)
                if result['filename']:
                    highlights['filename'] = result.highlights('filename')
                
                formatted_results.append({
                    'filepath': result['filepath'],
                    'filename': result['filename'],
                    'file_type': result['file_type'],
                    'file_size': result['file_size'],
                    'modified_at': result['modified_at'].isoformat() if result['modified_at'] else None,
                    'score': result.score,
                    'highlights': highlights
                })
            
            return {
                'total': len(results),
                'results': formatted_results
            }
    
    def get_index_stats(self):
        """获取索引统计信息"""
        with self.ix.searcher() as searcher:
            doc_count = searcher.doc_count()
            
            # 按文件类型统计
            file_types = {}
            for doc in searcher.documents():
                file_type = doc.get('file_type', 'unknown')
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            return {
                'total_documents': doc_count,
                'file_types': file_types,
                'index_size': self.get_index_size()
            }
    
    def get_index_size(self):
        """获取索引大小"""
        total_size = 0
        for root, dirs, files in os.walk(self.index_dir):
            for file in files:
                total_size += os.path.getsize(os.path.join(root, file))
        return total_size
    
    def clear_index(self):
        """清空索引"""
        writer = self.ix.writer()
        writer.commit(mergetype=CLEAR)

# Flask API应用
app = Flask(__name__)
searcher = WhooshFileSearcher()

@app.route('/search', methods=['POST'])
def search_files():
    """搜索文件API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供JSON数据'}), 400
        
        query = data.get('query', '').strip()
        max_results = data.get('max_results', 100)
        
        if not query:
            return jsonify({'error': '查询内容不能为空'}), 400
        
        if len(query) > 100:
            return jsonify({'error': '查询内容过长'}), 400
        
        start_time = datetime.now()
        results = searcher.search(query, max_results)
        search_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return jsonify({
            'success': True,
            'query': query,
            'search_time_ms': round(search_time, 2),
            **results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'搜索失败: {str(e)}'
        }), 500

@app.route('/index', methods=['POST'])
def index_directory():
    """索引目录API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供JSON数据'}), 400
        
        directory = data.get('directory', '').strip()
        update_existing = data.get('update_existing', True)
        
        if not directory:
            return jsonify({'error': '目录路径不能为空'}), 400
        
        if not os.path.exists(directory):
            return jsonify({'error': '目录不存在'}), 400
        
        if not os.path.isdir(directory):
            return jsonify({'error': '路径不是目录'}), 400
        
        start_time = datetime.now()
        stats = searcher.index_directory(directory, update_existing)
        index_time = (datetime.now() - start_time).total_seconds()
        
        return jsonify({
            'success': True,
            'directory': directory,
            'index_time_seconds': round(index_time, 2),
            **stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'索引失败: {str(e)}'
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """获取索引统计信息"""
    try:
        stats = searcher.get_index_stats()
        return jsonify({
            'success': True,
            **stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取统计失败: {str(e)}'
        }), 500

@app.route('/clear', methods=['POST'])
def clear_index():
    """清空索引"""
    try:
        searcher.clear_index()
        return jsonify({
            'success': True,
            'message': '索引已清空'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'清空失败: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("文件搜索系统启动中...")
    print("API端点:")
    print("  POST /search - 搜索文件")
    print("  POST /index - 索引目录")
    print("  GET /stats - 获取统计信息")
    print("  POST /clear - 清空索引")
    print("  GET /health - 健康检查")
    
    app.run(host='127.0.0.1', port=5000, debug=False)