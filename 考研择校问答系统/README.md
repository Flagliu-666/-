# 考研择校智能问答系统

基于大语言模型的考研择校咨询系统，支持智能推荐、分数线查询、学科评估等功能。

## 功能特性

- 智能院校推荐：根据考生背景推荐合适院校
- 分数线查询：支持国家线、校线、自主划线查询
- 学科评估查询：第四轮学科评估A类院校
- 多轮对话：支持上下文理解和追问
- 政策解读：考研政策、流程、注意事项

## 项目结构

```
考研择校问答系统/
├── app_pro.py              # 主应用（Streamlit）
├── rag_engine_pro.py        # RAG检索引擎
├── api.py                   # API服务
├── model_optimizer.py       # 模型训练器
├── auto_trainer.py          # 多轮自动训练
├── requirements_pro.txt     # 依赖
├── crawler/                 # 数据爬虫模块
│   ├── chsi_crawler.py      # 研招网爬虫
│   ├── discipline_crawler.py # 学科评估爬虫
│   ├── ranking_crawler.py    # 大学排名爬虫
│   ├── score_line_crawler.py # 分数线爬虫
│   └── crawler_manager.py    # 爬虫管理器
├── data/                    # 知识库数据
│   ├── grad_consult_qa.json  # 问答知识库（1216条）
│   ├── schools_985.json      # 985高校
│   ├── schools_211.json      # 211高校
│   ├── discipline_full.json   # 学科评估
│   ├── national_scores.json  # 历年国家线
│   ├── self_drawn_scores.json # 自主划线
│   ├── university_rankings.json # 大学排名
│   ├── training/            # 训练数据
│   └── enhancements/         # 增强模块
└── tests/                   # 测试
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements_pro.txt
```

### 启动应用

```bash
streamlit run app_pro.py
```

## 数据来源

| 数据类型 | 来源 | 更新日期 |
|---------|------|---------|
| 院校信息 | 研招网、各高校研究生院 | 持续更新 |
| 国家线 | 教育部、研招网 | 2024年 |
| 学科评估 | 教育部学位中心 | 第四轮（2016） |
| 大学排名 | 公开排名数据 | 持续更新 |
| 分数线 | 各校研究生院 | 2024年 |

## 知识库规模

- 问答知识库：1216 条
- 985高校数据：39 所
- 211高校数据：115 所
- 学科评估：26 个学科门类
- 历年分数线：2022-2024年

## 训练模块

```bash
# 运行单次训练
python model_optimizer.py

# 运行多轮自动训练
python auto_trainer.py
```

## 技术栈

- **后端**：Python 3.8+
- **框架**：Streamlit、FastAPI
- **模型**：支持多种LLM（Ollama/OpenAI/DeepSeek等）
- **数据**：JSON、CSV、向量数据库
