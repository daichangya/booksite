import requests
import re
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup

from .base import DataSource

class DDTKoreaDataSource(DataSource):
    """韩国小说网站数据源，通过爬虫从DDTKorea获取数据"""
    
    def __init__(self, base_url: str = 'https://www.ddtkorea.com', cache_dir: str = 'data/cache/ddtkorea'):
        """初始化DDTKorea数据源
        
        Args:
            base_url (str): DDTKorea基础URL
            cache_dir (str): 缓存目录路径
        """
        self.base_url = base_url
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 请求头，模拟浏览器访问
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _get_html(self, url: str) -> str:
        """获取网页HTML内容
        
        Args:
            url (str): 网页URL
            
        Returns:
            str: HTML内容
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'  # 确保韩文正确解码
            return response.text
        except Exception as e:
            print(f"获取页面失败: {url}, 错误: {e}")
            return ""
    
    def _cache_data(self, cache_file: Path, data: Any) -> None:
        """缓存数据到本地文件
        
        Args:
            cache_file (Path): 缓存文件路径
            data (Any): 要缓存的数据
        """
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            if isinstance(data, str):
                f.write(data)
            else:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _get_cached_data(self, cache_file: Path, max_age: int = 86400) -> Optional[Any]:
        """获取缓存数据
        
        Args:
            cache_file (Path): 缓存文件路径
            max_age (int): 最大缓存时间（秒），默认1天
            
        Returns:
            Optional[Any]: 缓存数据，如果缓存不存在或已过期则返回None
        """
        if not cache_file.exists():
            return None
            
        # 检查缓存是否过期
        file_time = cache_file.stat().st_mtime
        if time.time() - file_time > max_age:
            return None
            
        try:
            if cache_file.suffix == '.json':
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            return None
    
    def get_books(self) -> List[Dict[str, Any]]:
        """获取所有书籍列表"""
        cache_file = self.cache_dir / 'books.json'
        
        # 尝试从缓存获取
        cached_data = self._get_cached_data(cache_file)
        if cached_data:
            return cached_data
        
        books = []
        try:
            # 获取首页内容
            html = self._get_html(f"{self.base_url}/novel/")
            if not html:
                return []
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找小说列表
            book_items = soup.select('.novel-list .novel-item')
            for i, item in enumerate(book_items):
                try:
                    link = item.select_one('a.novel-title')
                    if not link:
                        continue
                        
                    book_url = link.get('href')
                    if not book_url.startswith('http'):
                        book_url = self.base_url + book_url
                        
                    title = link.text.strip()
                    author = item.select_one('.novel-author').text.strip() if item.select_one('.novel-author') else '未知作者'
                    cover = item.select_one('.novel-cover img').get('src') if item.select_one('.novel-cover img') else ''
                    description = item.select_one('.novel-desc').text.strip() if item.select_one('.novel-desc') else '暂无简介'
                    
                    # 从URL中提取ID
                    book_id = re.search(r'/novel/([\d]+)', book_url)
                    if not book_id:
                        continue
                        
                    books.append({
                        'id': int(book_id.group(1)),
                        'title': title,
                        'author': author,
                        'cover': cover,
                        'description': description,
                        'source_url': book_url
                    })
                    
                    # 限制爬取数量
                    if len(books) >= 10:
                        break
                except Exception as e:
                    print(f"解析书籍信息失败: {e}")
                    continue
        except Exception as e:
            print(f"获取书籍列表失败: {e}")
        
        # 缓存结果
        if books:
            self._cache_data(cache_file, books)
        
        return books
    
    def get_book_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取书籍详情"""
        # 直接访问书籍详情页
        book_url = f"{self.base_url}/novel/{book_id}"
        
        cache_file = self.cache_dir / f"book_{book_id}.json"
        
        # 尝试从缓存获取
        cached_data = self._get_cached_data(cache_file)
        if cached_data:
            return cached_data
        
        try:
            html = self._get_html(book_url)
            if not html:
                return None
                
            soup = BeautifulSoup(html, 'html.parser')
            
            title = soup.select_one('.novel-title').text.strip() if soup.select_one('.novel-title') else '未知标题'
            author = soup.select_one('.novel-author').text.strip() if soup.select_one('.novel-author') else '未知作者'
            cover = soup.select_one('.novel-cover img').get('src') if soup.select_one('.novel-cover img') else ''
            description = soup.select_one('.novel-desc').text.strip() if soup.select_one('.novel-desc') else '暂无简介'
            
            book = {
                'id': book_id,
                'title': title,
                'author': author,
                'cover': cover,
                'description': description,
                'source_url': book_url
            }
            
            # 缓存结果
            self._cache_data(cache_file, book)
            return book
        except Exception as e:
            print(f"获取书籍详情失败: {e}")
            return None
    
    def get_chapters(self, book_id: int) -> List[Dict[str, Any]]:
        """获取指定书籍的所有章节"""
        book = self.get_book_by_id(book_id)
        if not book:
            return []
            
        cache_file = self.cache_dir / str(book_id) / 'chapters.json'
        
        # 尝试从缓存获取
        cached_data = self._get_cached_data(cache_file)
        if cached_data:
            return cached_data
        
        chapters = []
        try:
            # 获取章节列表页面
            chapters_url = f"{self.base_url}/novel/{book_id}/chapters"
            html = self._get_html(chapters_url)
            if not html:
                return []
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找章节列表
            chapter_items = soup.select('.chapter-list .chapter-item')
            for i, item in enumerate(chapter_items):
                try:
                    link = item.select_one('a')
                    if not link:
                        continue
                        
                    chapter_url = link.get('href')
                    if not chapter_url.startswith('http'):
                        chapter_url = self.base_url + chapter_url
                    
                    # 从URL中提取章节ID
                    chapter_id = re.search(r'/chapter/([\d]+)', chapter_url)
                    if not chapter_id:
                        continue
                        
                    chapters.append({
                        'id': int(chapter_id.group(1)),
                        'title': link.text.strip(),
                        'source_url': chapter_url
                    })
                except Exception as e:
                    print(f"解析章节信息失败: {e}")
                    continue
        except Exception as e:
            print(f"获取章节列表失败: {e}")
        
        # 缓存结果
        if chapters:
            self._cache_data(cache_file, chapters)
            
            # 预先缓存前几章内容
            for chapter in chapters[:3]:
                self.get_chapter_content(book_id, chapter['id'])
        
        return chapters
    
    def get_chapter_content(self, book_id: int, chapter_id: int) -> Optional[str]:
        """获取指定章节的内容"""
        cache_file = self.cache_dir / str(book_id) / f"{chapter_id}.txt"
        
        # 尝试从缓存获取
        cached_data = self._get_cached_data(cache_file)
        if cached_data:
            return cached_data
        
        try:
            # 直接访问章节内容页
            chapter_url = f"{self.base_url}/chapter/{chapter_id}"
            html = self._get_html(chapter_url)
            if not html:
                return None
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取章节内容
            content_div = soup.select_one('.chapter-content')
            if not content_div:
                return None
                
            # 处理内容
            content = content_div.text.strip()
            # 替换多余的换行符
            content = re.sub(r'\n+', '\n\n', content)
            # 去除可能的广告文本
            content = re.sub(r'(ddtkorea\.com|http://\S+)', '', content)
            
            # 缓存结果
            if content:
                self._cache_data(cache_file, content)
            
            return content
        except Exception as e:
            print(f"获取章节内容失败: {e}")
            return None
    
    def search_books(self, query: str) -> List[Dict[str, Any]]:
        """搜索书籍"""
        if not query:
            return self.get_books()
            
        cache_file = self.cache_dir / f"search_{query}.json"
        
        # 尝试从缓存获取
        cached_data = self._get_cached_data(cache_file, max_age=3600)  # 搜索缓存时间较短
        if cached_data:
            return cached_data
        
        results = []
        try:
            # 构建搜索URL
            search_url = f"{self.base_url}/search?q={query}"
            html = self._get_html(search_url)
            if not html:
                return []
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找搜索结果
            result_items = soup.select('.search-results .novel-item')
            for i, item in enumerate(result_items):
                try:
                    link = item.select_one('a.novel-title')
                    if not link:
                        continue
                        
                    book_url = link.get('href')
                    if not book_url.startswith('http'):
                        book_url = self.base_url + book_url
                        
                    # 从URL中提取ID
                    book_id = re.search(r'/novel/([\d]+)', book_url)
                    if not book_id:
                        continue
                        
                    title = link.text.strip()
                    author = item.select_one('.novel-author').text.strip() if item.select_one('.novel-author') else '未知作者'
                    cover = item.select_one('.novel-cover img').get('src') if item.select_one('.novel-cover img') else ''
                    description = item.select_one('.novel-desc').text.strip() if item.select_one('.novel-desc') else '暂无简介'
                    
                    results.append({
                        'id': int(book_id.group(1)),
                        'title': title,
                        'author': author,
                        'cover': cover,
                        'description': description,
                        'source_url': book_url
                    })
                    
                    # 限制结果数量
                    if len(results) >= 10:
                        break
                except Exception as e:
                    print(f"解析搜索结果失败: {e}")
                    continue
        except Exception as e:
            print(f"搜索书籍失败: {e}")
            return []
        
        # 缓存结果
        if results:
            self._cache_data(cache_file, results)
        
        return results