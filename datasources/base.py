from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class DataSource(ABC):
    """数据源基类，定义所有数据源必须实现的接口"""
    
    @abstractmethod
    def get_books(self) -> List[Dict[str, Any]]:
        """获取所有书籍列表
        
        Returns:
            List[Dict[str, Any]]: 书籍列表，每本书包含id, title, author, cover, description等信息
        """
        pass
    
    @abstractmethod
    def get_book_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取书籍详情
        
        Args:
            book_id (int): 书籍ID
            
        Returns:
            Optional[Dict[str, Any]]: 书籍详情，如果不存在返回None
        """
        pass
    
    @abstractmethod
    def get_chapters(self, book_id: int) -> List[Dict[str, Any]]:
        """获取指定书籍的所有章节
        
        Args:
            book_id (int): 书籍ID
            
        Returns:
            List[Dict[str, Any]]: 章节列表，每个章节包含id, title等信息
        """
        pass
    
    @abstractmethod
    def get_chapter_content(self, book_id: int, chapter_id: int) -> Optional[str]:
        """获取指定章节的内容
        
        Args:
            book_id (int): 书籍ID
            chapter_id (int): 章节ID
            
        Returns:
            Optional[str]: 章节内容，如果不存在返回None
        """
        pass
    
    @abstractmethod
    def search_books(self, query: str) -> List[Dict[str, Any]]:
        """搜索书籍
        
        Args:
            query (str): 搜索关键词
            
        Returns:
            List[Dict[str, Any]]: 符合条件的书籍列表
        """
        pass