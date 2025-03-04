import unittest
from unittest.mock import patch, MagicMock
import json
import os
from pathlib import Path
import tempfile
import shutil
from datasources.ddtkorea import DDTKoreaDataSource

class TestDDTKoreaDataSource(unittest.TestCase):
    def setUp(self):
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / 'cache'
        self.data_source = DDTKoreaDataSource(cache_dir=str(self.cache_dir))
        
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.temp_dir)
        
    @patch('requests.get')
    def test_get_html(self, mock_get):
        # 模拟成功的请求
        mock_response = MagicMock()
        mock_response.text = '<html>테스트 내용</html>'
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        html = self.data_source._get_html('http://test.com')
        self.assertEqual(html, '<html>테스트 내용</html>')
        
        # 模拟请求失败
        mock_get.side_effect = Exception('网络错误')
        html = self.data_source._get_html('http://test.com')
        self.assertEqual(html, '')
        
    def test_cache_operations(self):
        # 测试缓存写入
        test_data = {'test': 'data'}
        cache_file = self.cache_dir / 'test.json'
        self.data_source._cache_data(cache_file, test_data)
        
        # 验证缓存读取
        cached_data = self.data_source._get_cached_data(cache_file)
        self.assertEqual(cached_data, test_data)
        
        # 测试缓存过期
        import time
        # 修改文件时间为过去
        old_time = time.time() - 90000  # 超过一天
        os.utime(cache_file, (old_time, old_time))
        
        cached_data = self.data_source._get_cached_data(cache_file)
        self.assertIsNone(cached_data)
        
    @patch('requests.get')
    def test_get_books(self, mock_get):
        # 模拟首页HTML
        mock_response = MagicMock()
        mock_response.text = '''
        <div class="novel-list">
            <div class="novel-item">
                <a class="novel-title" href="/novel/123">테스트 소설</a>
                <div class="novel-author">작가 이름</div>
                <div class="novel-cover"><img src="/cover.jpg"></div>
                <div class="novel-desc">소설 설명</div>
            </div>
        </div>
        '''
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        books = self.data_source.get_books()
        self.assertTrue(len(books) > 0)
        self.assertEqual(books[0]['id'], 123)
        self.assertEqual(books[0]['title'], '테스트 소설')
        self.assertEqual(books[0]['author'], '작가 이름')
        
    @patch('requests.get')
    def test_get_chapters(self, mock_get):
        # 模拟书籍详情页HTML
        book_response = MagicMock()
        book_response.text = '''
        <div class="novel-title">테스트 소설</div>
        <div class="novel-author">작가 이름</div>
        <div class="novel-cover"><img src="/cover.jpg"></div>
        <div class="novel-desc">소설 설명</div>
        '''
        
        # 模拟章节列表页HTML
        chapters_response = MagicMock()
        chapters_response.text = '''
        <div class="chapter-list">
            <div class="chapter-item">
                <a href="/chapter/456">제1장</a>
            </div>
            <div class="chapter-item">
                <a href="/chapter/457">제2장</a>
            </div>
        </div>
        '''
        
        # 设置mock按顺序返回不同的响应
        mock_get.side_effect = [book_response, chapters_response]
        
        chapters = self.data_source.get_chapters(123)
        self.assertTrue(len(chapters) > 0)
        self.assertEqual(chapters[0]['id'], 456)
        self.assertEqual(chapters[0]['title'], '제1장')
        
    @patch('requests.get')
    def test_get_chapter_content(self, mock_get):
        # 模拟章节内容页HTML
        mock_response = MagicMock()
        mock_response.text = '''
        <div class="chapter-content">
            테스트 소설의 내용입니다.
            이것은 테스트를 위한 내용입니다.
        </div>
        '''
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        content = self.data_source.get_chapter_content(123, 456)
        self.assertIsNotNone(content)
        self.assertTrue('테스트 소설의 내용입니다' in content)
        
    @patch('requests.get')
    def test_search_books(self, mock_get):
        # 模拟搜索结果页HTML
        mock_response = MagicMock()
        mock_response.text = '''
        <div class="search-results">
            <div class="novel-item">
                <a class="novel-title" href="/novel/123">검색된 소설</a>
                <div class="novel-author">작가 이름</div>
                <div class="novel-cover"><img src="/cover.jpg"></div>
                <div class="novel-desc">소설 설명</div>
            </div>
        </div>
        '''
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        results = self.data_source.search_books('테스트')
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['id'], 123)
        self.assertEqual(results[0]['title'], '검색된 소설')
        
    def test_error_handling(self):
        # 测试无效的book_id
        chapters = self.data_source.get_chapters(999)
        self.assertEqual(chapters, [])
        
        # 测试无效的chapter_id
        content = self.data_source.get_chapter_content(1, 999)
        self.assertIsNone(content)
        
if __name__ == '__main__':
    unittest.main()