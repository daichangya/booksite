# 小说网站

一个基于Python Flask的在线小说阅读网站，支持多数据源小说内容聚合。

## 功能特点

- 多数据源支持：可从多个小说网站聚合内容
- 智能缓存：自动缓存已获取的小说内容，提升访问速度
- 响应式设计：完美适配PC和移动端
- 阅读体验优化：专业的排版和阅读界面
- 搜索功能：支持小说标题和作者搜索

## 技术架构

- 后端：Python Flask
- 前端：HTML5 + CSS3
- 数据抓取：BeautifulSoup4
- 数据存储：本地文件系统缓存

## 数据源

目前支持以下数据源：

- DDTKorea：韩国小说网站
- 本地文件：支持本地小说文件导入

## 安装部署

1. 克隆项目

```bash
git clone [项目地址]
cd booksite
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 启动服务

```bash
python app.py
```

访问 http://localhost:5000 即可使用

## 项目结构

```
booksite/
├── app.py              # 应用入口
├── datasources/        # 数据源实现
│   ├── __init__.py
│   ├── base.py        # 数据源基类
│   ├── ddtkorea.py    # 韩国小说数据源
│   └── local_file.py  # 本地文件数据源
├── templates/         # 前端模板
│   ├── layout.html    # 基础布局
│   ├── index.html     # 首页
│   ├── book.html      # 书籍详情
│   └── chapter.html   # 章节阅读
├── data/              # 数据存储目录
│   └── cache/         # 缓存目录
└── tests/             # 测试用例
```

## 主要特性

### 1. 数据源抽象

采用抽象基类设计数据源接口，便于扩展新的数据源：

```python
class DataSource:
    def get_books(self) -> List[Dict[str, Any]]:
        """获取书籍列表"""
        pass

    def get_book_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        """获取书籍详情"""
        pass

    def get_chapters(self, book_id: int) -> List[Dict[str, Any]]:
        """获取章节列表"""
        pass

    def get_chapter_content(self, book_id: int, chapter_id: int) -> Optional[str]:
        """获取章节内容"""
        pass
```

### 2. 智能缓存

- 自动缓存已获取的内容
- 支持缓存过期时间设置
- 分级缓存策略

### 3. 响应式界面

- 现代化的UI设计
- 完美适配各种设备
- 优化的阅读体验

## 开发计划

- [ ] 添加更多数据源支持
- [ ] 用户系统
- [ ] 阅读历史同步
- [ ] 书架功能
- [ ] 阅读进度记录
- [ ] 移动端APP

## 贡献指南

1. Fork 本仓库
2. 创建新特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件