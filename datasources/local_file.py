import json
from pathlib import Path
from typing import List, Dict, Optional, Any

from .base import DataSource

class LocalFileDataSource(DataSource):
    """本地文件数据源，从本地JSON文件读取数据"""
    
    def __init__(self, books_dir: str = 'data/books', books_info_file: str = 'data/books.json'):
        """初始化本地文件数据源
        
        Args:
            books_dir (str): 书籍目录路径
            books_info_file (str): 书籍信息文件路径
        """
        self.books_dir = Path(books_dir)
        self.books_info_file = Path(books_info_file)
        
        # 确保必要的目录存在
        self.books_dir.mkdir(parents=True, exist_ok=True)
        self.books_info_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_books(self) -> List[Dict[str, Any]]:
        """获取所有书籍列表"""
        try:
            with open(self.books_info_file, 'r', encoding='utf-8') as f:
                return json.load(f)['books']
        except FileNotFoundError:
            return []
    
    def get_book_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取书籍详情"""
        try:
            with open(self.books_info_file, 'r', encoding='utf-8') as f:
                books = json.load(f)['books']
                return next((b for b in books if b['id'] == int(book_id)), None)
        except FileNotFoundError:
            return None
    
    def get_chapters(self, book_id: int) -> List[Dict[str, Any]]:
        """获取指定书籍的所有章节"""
        try:
            chapters_file = self.books_dir / str(book_id) / 'chapters.json'
            with open(chapters_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def get_chapter_content(self, book_id: int, chapter_id: int) -> Optional[str]:
        """获取指定章节的内容"""
        try:
            content_file = self.books_dir / str(book_id) / f'{chapter_id}.txt'
            with open(content_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
    
    def search_books(self, query: str) -> List[Dict[str, Any]]:
        """搜索书籍"""
        books = self.get_books()
        if not query:
            return books
        
        query = query.lower()
        return [b for b in books if query in b['title'].lower() or query in b['author'].lower()]