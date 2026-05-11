# 爬虫模块

本目录包含多个数据源的爬虫模块，用于采集考研相关数据。

## 模块列表

| 文件 | 数据源 | 功能 |
|------|--------|------|
| `chsi_crawler.py` | 研招网 | 院校、专业、分数线查询 |
| `discipline_crawler.py` | 学科评估网 | 第四轮学科评估数据 |
| `ranking_crawler.py` | 大学排名 | 各类大学排名数据 |
| `score_line_crawler.py` | 历年分数线 | 国家线、校线、自划线 |
| `crawler_manager.py` | 综合管理 | 统一调度所有爬虫 |

## 使用方法

```python
from crawler_manager import CrawlerManager

# 初始化管理器
manager = CrawlerManager()

# 查询院校信息
schools = manager.search_schools("计算机")

# 查询学科评估
evaluation = manager.get_discipline_evaluation("计算机")

# 获取历年分数线
scores = manager.get_score_lines(2024)

# 导出完整数据
manager.export_all_data()
```
