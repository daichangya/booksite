from flask import Flask, render_template, request, jsonify
import os

# 导入数据源
from datasources.local_file import LocalFileDataSource
from datasources.ddtkorea import DDTKoreaDataSource

app = Flask(__name__)

# 配置数据源
DATASOURCE_TYPE = os.environ.get('DATASOURCE_TYPE', 'local')  # 默认使用本地文件数据源

# 根据配置初始化数据源
if DATASOURCE_TYPE == 'ddtkorea':
    data_source = DDTKoreaDataSource()
else:  # 默认使用本地文件数据源
    data_source = LocalFileDataSource()

# 首页路由
@app.route('/')
def index():
    books = data_source.get_books()
    return render_template('index.html', books=books)

# 书籍详情页路由
@app.route('/book/<book_id>')
def book_detail(book_id):
    book = data_source.get_book_by_id(int(book_id))
    if book:
        chapters = data_source.get_chapters(int(book_id))
        return render_template('book.html', book=book, chapters=chapters)
    return '书籍不存在', 404

# 章节阅读页路由
@app.route('/book/<book_id>/chapter/<chapter_id>')
def read_chapter(book_id, chapter_id):
    book = data_source.get_book_by_id(int(book_id))
    if book:
        chapters = data_source.get_chapters(int(book_id))
        chapter = next((c for c in chapters if c['id'] == int(chapter_id)), None)
        
        if chapter:
            # 获取上一章和下一章的信息
            current_index = next(i for i, c in enumerate(chapters) if c['id'] == int(chapter_id))
            prev_chapter = chapters[current_index - 1] if current_index > 0 else None
            next_chapter = chapters[current_index + 1] if current_index < len(chapters) - 1 else None
            
            # 读取章节内容
            content = data_source.get_chapter_content(int(book_id), int(chapter_id))
            if content:
                return render_template('chapter.html', book=book, chapter=chapter, content=content,
                                     prev_chapter=prev_chapter, next_chapter=next_chapter)
    return '章节不存在', 404

# 搜索路由
@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = data_source.search_books(query)
    return render_template('search.html', books=results, query=query)

# 最近阅读路由
@app.route('/recent-reads')
def recent_reads():
    books = data_source.get_books()
    all_books = {str(b['id']): b for b in books}
    return render_template('recent_reads.html', all_books=all_books)

if __name__ == '__main__':
    app.run(debug=True)