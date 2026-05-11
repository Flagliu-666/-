# 考研择校智能问答系统 - 项目设计文档

## 一、项目概述

### 1.1 解决的具体问题

**问题背景**：
- 考研学生面临海量的院校信息，难以快速找到适合自己的目标院校
- 考研信息分散在各个官方网站，查询效率低
- 缺乏个性化的择校建议，往往依靠经验或道听途说

**核心问题**：
1. **信息过载**：全国招收计算机类研究生的高校超过300所，招生政策各不相同
2. **信息不对称**：分数线、报录比、复录比等关键数据难以获取
3. **个性化需求**：每个考生的背景（本科层次、分数、专业偏好、地区偏好）不同，需要个性化推荐
4. **决策困难**：面对众多选择，考生缺乏科学的择校方法论

### 1.2 核心功能

| 功能模块 | 描述 | 目标用户价值 |
|---------|------|-------------|
| 智能院校推荐 | 根据用户画像推荐合适院校 | 节省50%+的择校时间 |
| 分数线查询 | 国家线/校线/自划线查询 | 快速获取历年分数线 |
| 学科评估查询 | 查询各学科高校排名 | 了解院校学科实力 |
| 考研政策解读 | 学硕/专硕、408/自命题等 | 解答常见困惑 |
| 多轮对话咨询 | 支持追问和上下文理解 | 像咨询师一样对话 |
| 联网实时查询 | 获取最新招生信息 | 不遗漏重要通知 |

### 1.3 目标用户

- **主要用户**：计算机类（计算机、软件工程、人工智能等）考研学生
- **用户画像**：
  - 大三/大四在读本科生
  - 一战或二战考生
  - 在职考研人群
- **用户痛点**：
  - 不知道能考上什么学校
  - 不了解各学校考研难度
  - 不知道如何平衡学校层次与上岸率

---

## 二、系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户界面层 (Streamlit Web)               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  聊天界面   │  │  用户画像   │  │  结果展示   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent 任务调度层                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  意图识别  →  任务规划  →  Skill调用  →  结果整合            ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Skills 能力层                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ 院校查询 │ │ 智能推荐 │ │ 政策解读 │ │ 备考咨询 │            │
│  │  Skill  │ │  Skill  │ │  Skill  │ │  Skill  │            │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据层                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 院校数据库   │  │ 问答知识库   │  │ 学科评估库   │          │
│  │  (CSV)       │  │  (JSON)      │  │  (JSON)      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 分数线库    │  │ 政策知识库   │  │ 向量数据库   │          │
│  │  (JSON)     │  │  (JSON)      │  │ (Chroma)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      大模型API层                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                         │
│  │ 智谱GLM  │ │ OpenAI   │ │  Kimi    │                         │
│  └──────────┘ └──────────┘ └──────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心业务流程

```
用户输入问题
    │
    ▼
┌─────────────────┐
│  NLP预处理      │
│  1. 分词处理    │
│  2. 意图识别    │
│  3. 关键词抽取  │
│  4. 实体识别    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Agent调度      │
│  1. 意图分类    │
│  2. 任务规划    │
│  3. Skill选择   │
│  4. 结果整合    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Skill执行      │
│  • 院校查询    │
│  • 智能推荐    │
│  • 政策解读    │
│  • 备考咨询    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  结果生成      │
│  1. 知识检索    │
│  2. 上下文整合  │
│  3. 回答生成    │
│  4. 来源标注    │
└─────────────────┘
    │
    ▼
返回用户回答
```

---

## 三、NLP典型任务实现

本系统涉及以下 **5项** NLP典型任务：

### 3.1 意图识别 (Intent Recognition)

**任务定义**：判断用户问题的意图类型

**实现方法**：基于规则 + 关键词匹配

```python
# 意图类型定义
INTENTS = {
    "school_query": ["查", "多少分", "分数线", "招生", "考什么", "科目"],
    "school_recommend": ["推荐", "选择", "择校", "性价比", "哪个学校"],
    "policy_explain": ["区别", "是什么", "学硕", "专硕", "408", "自命题"],
    "major_query": ["专业", "方向", "跨考"],
    "score_query": ["国家线", "校线", "自划线"],
    "preparation": ["复习", "怎么学", "备考", "计划"]
}
```

**应用场景**：用户输入"推荐计算机985院校" → 识别为 `school_recommend` 意图

### 3.2 关键词抽取 (Keyword Extraction)

**任务定义**：从用户问题中提取关键信息

**实现方法**：
1. 正则表达式匹配（分数、学校名、专业名）
2. 停用词过滤
3. 词性标注（使用jieba分词）

```python
# 关键词类型
KEYWORDS = {
    "score": r"(\d{2,3})\s*分",
    "school": r"[\u4e00-\u9fa5]{2,10}(?:大学|学院|研究所)",
    "major": r"(计算机|软件|人工智能|电子信息|自动化)",
    "level": r"(985|211|双非|普通)",
    "region": r"(北京|上海|杭州|武汉|成都|西安)"
}
```

**应用场景**：
- 输入："东北大学考什么科目" → 提取关键词：{school: "东北大学", action: "考什么科目"}

### 3.3 命名实体识别 (NER) / 信息抽取

**任务定义**：识别文本中的实体并分类

**实现方法**：基于规则的实体识别

```python
# 实体类型
ENTITIES = {
    "school": ["清华大学", "北京大学", "浙江大学", ...],
    "major": ["计算机科学与技术", "软件工程", "人工智能"],
    "discipline_level": ["A+", "A", "A-", "B+", "B", "B-", ...]
}
```

**应用场景**：
- 提取学校名、专业名、分数、地区等实体

### 3.4 文本分类 (Text Classification)

**任务定义**：对用户问题进行分类

**实现方法**：多级分类器

```python
# 一级分类：问题类型
CLASS_LEVEL1 = [
    "咨询类",  # 问政策、问流程
    "查询类",  # 查分数线、查院校
    "推荐类",  # 求推荐、求建议
    "闲聊类"   # 打招呼、感谢
]

# 二级分类：专业方向
CLASS_LEVEL2 = [
    "计算机类", "电子类", "机械类", 
    "经济管理类", "文科类", "其他"
]
```

### 3.5 检索与匹配 (Retrieval & Matching)

**任务定义**：从知识库中检索相关内容

**实现方法**：
1. 关键词匹配（BM25算法思想）
2. 向量相似度检索（Chroma向量数据库）
3. 混合检索策略

```python
# 检索流程
def retrieve(query, top_k=5):
    # 1. 关键词检索
    keyword_results = keyword_search(query, top_k=10)
    
    # 2. 向量检索
    vector_results = vector_search(query, top_k=10)
    
    # 3. 结果融合
    combined = fusion(keyword_results, vector_results)
    
    return combined[:top_k]
```

---

## 四、Agent任务规划与调度

### 4.1 Agent架构

```python
class GradSchoolAgent:
    """
    考研择校智能问答Agent
    负责任务规划、Skill调度、结果整合
    """
    
    def __init__(self):
        self.nlp_processor = NLPProcessor()    # NLP处理模块
        self.skill_registry = SkillRegistry()   # Skill注册表
        self.context_manager = ContextManager() # 上下文管理
        self.llm = LLMWrapper()                 # 大模型包装器
    
    def process(self, user_input, user_profile):
        """
        处理用户输入的主流程
        """
        # 1. NLP预处理
        nlp_result = self.nlp_processor.process(user_input)
        
        # 2. 意图分类
        intent = nlp_result['intent']
        
        # 3. 任务规划
        task_plan = self.plan_task(intent, user_profile)
        
        # 4. Skill调用
        skill_results = self.execute_skills(task_plan)
        
        # 5. 结果整合
        final_answer = self.integrate_results(skill_results, nlp_result)
        
        return final_answer
```

### 4.2 任务规划流程

```
用户问题：推荐一个性价比高的985院校，我预估350分
    │
    ▼
┌─────────────────────────────────────────────┐
│  意图识别结果                                │
│  • intent: school_recommend                 │
│  • keywords: ["推荐", "性价比", "985", "350分"]│
│  • entities: {level: "985", score: 350}    │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  任务规划                                    │
│  • 主任务: 智能推荐 (priority=1)            │
│  • 子任务:                                  │
│    1. 查询985院校列表                       │
│    2. 筛选分数线<350的院校                 │
│    3. 按性价比排序                          │
│    4. 生成推荐理由                          │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  Skill调度                                  │
│  • Skill: school_query → 获取院校数据       │
│  • Skill: smart_recommend → 智能推荐       │
│  • Skill: answer_generator → 生成回答       │
└─────────────────────────────────────────────┘
```

### 4.3 上下文管理

```python
class ContextManager:
    """
    管理多轮对话上下文
    支持指代消解、话题跟踪
    """
    
    def __init__(self):
        self.conversation_history = []  # 对话历史
        self.mentioned_entities = {}   # 提到的实体
        self.current_topic = None       # 当前话题
    
    def update(self, user_input, assistant_response):
        """更新上下文"""
        # 1. 提取用户提到的实体
        entities = extract_entities(user_input)
        self.mentioned_entities.update(entities)
        
        # 2. 更新对话历史
        self.conversation_history.append({
            'user': user_input,
            'assistant': assistant_response,
            'entities': entities
        })
        
        # 3. 指代消解
        self.resolve_references(user_input)
    
    def resolve_references(self, text):
        """
        指代消解
        "他们学校" → "东北大学"
        "这个专业" → "计算机科学与技术"
        """
        reference_map = {
            "他们": self.mentioned_entities.get('school', '某学校'),
            "它": self.mentioned_entities.get('school', '某学校'),
            "这个学校": self.mentioned_entities.get('school', '某学校'),
            "该校": self.mentioned_entities.get('school', '某学校'),
        }
        # 替换指代词为具体实体
        for ref, entity in reference_map.items():
            if ref in text:
                return entity
        return None
```

---

## 五、Skills能力封装

### 5.1 Skills架构

```
Skills层
├── school_query_skill      # 院校查询Skill
│   ├── query_by_name()     # 按名称查询
│   ├── query_by_score()    # 按分数查询
│   ├── query_by_region()   # 按地区查询
│   └── get_details()       # 获取详细信息
│
├── smart_recommend_skill   # 智能推荐Skill
│   ├── recommend_by_profile()   # 根据用户画像推荐
│   ├── recommend_by_score()     # 根据分数推荐
│   ├── recommend_by_major()      # 根据专业推荐
│   └── get_analysis_report()     # 生成分析报告
│
├── policy_explain_skill    # 政策解读Skill
│   ├── explain_degree_type()    # 学硕/专硕区别
│   ├── explain_exam_type()      # 408/自命题区别
│   ├── explain_policy()         # 考研政策解读
│   └── get_timeline()           # 考研时间线
│
└── preparation_consult_skill  # 备考咨询Skill
    ├── get_review_plan()        # 复习计划
    ├── get_material_recommend() # 资料推荐
    └── answer_common_question() # 常见问题解答
```

### 5.2 Skill接口定义

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseSkill(ABC):
    """Skill基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Skill名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Skill描述"""
        pass
    
    @property
    @abstractmethod
    def keywords(self) -> List[str]:
        """触发关键词"""
        pass
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行Skill"""
        pass
    
    @abstractmethod
    def validate(self, params: Dict[str, Any]) -> bool:
        """验证参数"""
        pass
```

### 5.3 院校查询Skill示例

```python
class SchoolQuerySkill(BaseSkill):
    """
    院校查询Skill
    功能：查询院校信息、分数线、招生人数等
    """
    
    @property
    def name(self) -> str:
        return "school_query"
    
    @property
    def description(self) -> str:
        return "查询院校信息，包括分数线、招生人数、考试科目、学科评估等"
    
    @property
    def keywords(self) -> List[str]:
        return ["查", "多少分", "招生", "考什么", "科目", "学费"]
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行院校查询
        
        Args:
            params: {
                'school_name': str,  # 学校名称
                'query_type': str,   # 查询类型：info/score/enrollment
                'user_profile': dict # 用户画像
            }
        
        Returns:
            查询结果字典
        """
        school_name = params.get('school_name')
        query_type = params.get('query_type', 'info')
        
        # 加载数据
        df = load_school_data()
        
        # 查询学校
        school_data = df[df['学校名称'] == school_name]
        
        if school_data.empty:
            return {'success': False, 'error': '未找到该院校'}
        
        row = school_data.iloc[0]
        
        result = {
            'success': True,
            'school': school_name,
            'location': row['所在地'],
            'level': row['层次'],
            'score_line': row['2024复试分数线'],
            'enrollment': row['招生人数'],
            'subjects': {
                'politics': row['初试科目(政治)'],
                'english': row['初试科目(英语)'],
                'math': row['初试科目(数学)'],
                'professional': row['初试科目(专业课)']
            },
            'assessment': row['学科评估'],
            'notes': row['备注']
        }
        
        return result
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """验证参数"""
        return 'school_name' in params and params['school_name']
```

---

## 六、数据来源与知识库构建

### 6.1 数据来源

| 数据类型 | 来源 | 说明 |
|---------|------|------|
| 院校基本信息 | 研招网(yz.chsi.com.cn)、各高校研究生院 | 招生简章、专业目录 |
| 分数线数据 | 教育部、34所自划线高校官网 | 2022-2024年 |
| 学科评估 | 教育部学位与研究生教育发展中心 | 第四轮学科评估(2016) |
| 大学排名 | 公开排名数据(武书连、校友会等) | 综合排名、专业排名 |
| 考研政策 | 教育部、各省教育考试院 | 招生政策、报考须知 |

### 6.2 知识库规模

```
data/
├── grad_consult_qa.json      # 1216条问答知识
├── schools_985.json          # 39所985高校
├── schools_211.json          # 115所211高校
├── schools_data.csv          # 50+所高校详细信息
├── discipline_evaluation.json # 学科评估数据
├── national_scores.json      # 历年国家线
├── self_drawn_scores.json    # 34所自划线
├── policy_knowledge.json     # 考研政策
├── major_knowledge.json      # 专业知识
└── school_details.json       # 院校详细信息
```

### 6.3 知识库构建流程

```
原始数据
    │
    ▼
┌─────────────────┐
│  数据清洗       │
│  • 去重         │
│  • 格式统一     │
│  • 缺失值处理   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  结构化处理     │
│  • CSV存储      │
│  • JSON存储     │
│  • 字段标准化   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  向量化处理     │
│  • BGE嵌入模型  │
│  • Chroma向量库 │
│  • 索引构建     │
└─────────────────┘
    │
    ▼
可检索知识库
```

---

## 七、系统价值（与普通ChatGPT的区别）

### 7.1 核心差异对比

| 特性 | 普通ChatGPT | 本系统 |
|-----|------------|--------|
| **数据来源** | 通用知识，可能过时 | 专业实时数据，知识库持续更新 |
| **个性化** | 无用户画像，千人一面 | 根据用户背景定制推荐 |
| **专业性** | 泛泛而谈 | 针对考研场景优化 |
| **信息准确性** | 可能"幻觉" | 基于知识库检索，准确可靠 |
| **功能集成** | 仅对话 | 对话+查询+推荐+分析 |
| **业务场景** | 通用场景 | 垂直领域深度服务 |

### 7.2 系统独特价值

1. **垂直领域深度优化**
   - 专门针对考研场景训练/优化
   - 理解考研专业术语和政策
   - 提供精准的院校推荐算法

2. **用户画像驱动**
   - 自动收集用户信息（分数、背景、偏好）
   - 基于画像进行个性化推荐
   - 记住用户历史对话

3. **专业数据支撑**
   - 1216条专业问答知识
   - 50+所高校详细信息
   - 历年分数线数据

4. **可量化评估**
   - 推荐理由有数据支撑
   - 分数线、报录比等信息透明
   - 给出上岸概率参考

---

## 八、技术栈

| 层级 | 技术 | 说明 |
|-----|------|------|
| **前端** | Streamlit | Web界面框架 |
| **后端** | Python 3.8+ | 主开发语言 |
| **大模型** | 智谱GLM-4/OpenAI GPT-4/Kimi | LLM支持 |
| **向量库** | Chroma | 向量数据库 |
| **NLP** | jieba | 分词、词性标注 |
| **数据** | Pandas, JSON, CSV | 数据处理 |
| **爬虫** | Requests, BeautifulSoup | 数据采集 |

---

## 九、运行说明

### 9.1 快速启动

```bash
# 1. 安装依赖
pip install -r requirements_pro.txt

# 2. 配置API（可选）
# 创建.env文件，添加 LLM_API_KEY=你的API密钥

# 3. 启动应用
streamlit run app_pro.py

# 4. 访问
# 浏览器打开 http://localhost:8501
```

### 9.2 命令行模式

```bash
# 问答模式
python main.py -m chat -q "推荐计算机985院校"

# API模式
python api.py
```

---

*文档版本: v1.0*
*更新日期: 2026-04-28*
