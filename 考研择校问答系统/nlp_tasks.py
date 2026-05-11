"""
考研择校智能问答系统 - NLP任务模块
实现了5项NLP典型任务：
1. 分词 (Word Segmentation)
2. 意图识别 (Intent Recognition)
3. 关键词抽取 (Keyword Extraction)
4. 命名实体识别 / 信息抽取 (NER / Information Extraction)
5. 文本分类 (Text Classification)
"""

import re
import json
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# 尝试导入jieba进行中文分词
try:
    import jieba
    import jieba.posseg as pseg
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False


# ==================== 数据结构定义 ====================

class IntentType(Enum):
    """意图类型枚举"""
    SCHOOL_QUERY = "school_query"           # 院校查询
    SCHOOL_RECOMMEND = "school_recommend"    # 院校推荐
    POLICY_EXPLAIN = "policy_explain"        # 政策解读
    MAJOR_QUERY = "major_query"              # 专业查询
    SCORE_QUERY = "score_query"              # 分数线查询
    PREPARATION = "preparation"              # 备考咨询
    GREETING = "greeting"                    # 打招呼
    THANKS = "thanks"                        # 感谢
    UNKNOWN = "unknown"                      # 未知


@dataclass
class NLPResult:
    """NLP处理结果"""
    original_text: str                       # 原始文本
    tokens: List[str] = field(default_factory=list)  # 分词结果
    pos_tags: List[Tuple[str, str]] = field(default_factory=list)  # 词性标注
    intent: IntentType = IntentType.UNKNOWN  # 意图类型
    intent_confidence: float = 0.0           # 意图置信度
    keywords: Dict[str, List[str]] = field(default_factory=dict)  # 关键词
    entities: Dict[str, Any] = field(default_factory=dict)  # 实体
    sentiment: str = "neutral"               # 情感倾向
    summary: str = ""                        # 文本摘要


@dataclass
class Entity:
    """实体结构"""
    text: str                                # 实体文本
    type: str                                # 实体类型
    start_pos: int                           # 起始位置
    end_pos: int                             # 结束位置
    confidence: float = 1.0                  # 置信度


# ==================== 意图识别 ====================

class IntentRecognizer:
    """
    意图识别器
    任务类型：文本分类
    """
    
    # 意图关键词映射
    INTENT_PATTERNS = {
        IntentType.SCHOOL_QUERY: [
            "多少分", "分数线", "招生人数", "招生", "考什么", "科目",
            "学费", "宿舍", "导师", "研究方向", "报录比", "复录比",
            "专业课", "初试", "复试", "调剂", "调剂吗"
        ],
        IntentType.SCHOOL_RECOMMEND: [
            "推荐", "选择", "择校", "性价比", "哪个学校", "什么学校好",
            "考哪所", "上岸", "稳", "冲", "保底", "帮忙", "分析",
            "推荐院校", "院校推荐", "学校推荐"
        ],
        IntentType.POLICY_EXPLAIN: [
            "区别", "是什么", "学硕", "专硕", "全日制", "非全日制",
            "408", "自命题", "国家线", "校线", "自划线", "A类", "B类",
            "预报名", "正式报名", "网上确认", "专项计划", "强军计划",
            "少数民族", "退役大学生", "流程", "怎么考"
        ],
        IntentType.MAJOR_QUERY: [
            "专业", "方向", "跨考", "跨专业", "考什么专业", "专业选择",
            "研究方向", "专硕", "学硕方向", "计算机类", "电子类"
        ],
        IntentType.SCORE_QUERY: [
            "国家线", "校线", "自划线", "自主划线", "历年分数",
            "分数", "多少分能上", "最低分", "最高分", "平均分"
        ],
        IntentType.PREPARATION: [
            "复习", "怎么学", "备考", "计划", "时间安排", "进度",
            "政治怎么复习", "英语怎么复习", "数学怎么复习", "专业课",
            "资料", "教材", "视频课", "报班", "真题", "模拟题"
        ],
        IntentType.GREETING: [
            "你好", "您好", "hi", "hello", "在吗", "在不在",
            "打扰一下", "请教一下", "咨询一下"
        ],
        IntentType.THANKS: [
            "谢谢", "感谢", "多谢", "辛苦了", "好的", "知道了",
            "明白了", "了解了"
        ]
    }
    
    # 意图优先级（用于冲突时决定）
    INTENT_PRIORITY = {
        IntentType.GREETING: 1,
        IntentType.THANKS: 1,
        IntentType.SCHOOL_RECOMMEND: 5,
        IntentType.SCHOOL_QUERY: 4,
        IntentType.POLICY_EXPLAIN: 3,
        IntentType.MAJOR_QUERY: 3,
        IntentType.SCORE_QUERY: 3,
        IntentType.PREPARATION: 2,
        IntentType.UNKNOWN: 0
    }
    
    def __init__(self):
        """初始化意图识别器"""
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        self.patterns = {}
        for intent, keywords in self.INTENT_PATTERNS.items():
            pattern = '|'.join(re.escape(kw) for kw in keywords)
            self.patterns[intent] = re.compile(pattern)
    
    def recognize(self, text: str) -> Tuple[IntentType, float]:
        """
        识别文本意图
        
        Args:
            text: 输入文本
        
        Returns:
            (意图类型, 置信度)
        """
        text_lower = text.lower()
        
        # 统计每个意图的匹配次数
        intent_scores = {}
        for intent, pattern in self.patterns.items():
            matches = pattern.findall(text_lower)
            if matches:
                intent_scores[intent] = len(matches)
        
        if not intent_scores:
            return IntentType.UNKNOWN, 0.0
        
        # 选择匹配次数最多的意图
        best_intent = max(intent_scores.keys(), 
                         key=lambda x: (intent_scores[x], self.INTENT_PRIORITY[x]))
        match_count = intent_scores[best_intent]
        
        # 计算置信度
        total_matches = sum(intent_scores.values())
        confidence = match_count / total_matches if total_matches > 0 else 0.0
        
        return best_intent, confidence
    
    def recognize_with_context(self, text: str, context: List[Dict]) -> Tuple[IntentType, float]:
        """
        结合上下文的意图识别
        
        Args:
            text: 当前输入
            context: 对话历史上下文
        
        Returns:
            (意图类型, 置信度)
        """
        # 简单策略：如果用户输入很短且上下文存在，可能是追问
        if len(text) < 20 and len(context) > 0:
            # 常见追问词
            follow_up_keywords = ["呢", "吗", "的", "多少", "怎么样", "呢", "还有"]
            if any(kw in text for kw in follow_up_keywords):
                # 继承上一轮的意图
                if context:
                    last_intent = context[-1].get('intent', IntentType.UNKNOWN)
                    if last_intent != IntentType.GREETING and last_intent != IntentType.THANKS:
                        return last_intent, 0.9
        
        return self.recognize(text)


# ==================== 分词处理 ====================

class WordSegmenter:
    """
    中文分词器
    任务类型：分词 (Word Segmentation)
    """
    
    def __init__(self, use_jieba: bool = True):
        """
        初始化分词器
        
        Args:
            use_jieba: 是否使用jieba分词，False则使用简单分词
        """
        self.use_jieba = use_jieba and JIEBA_AVAILABLE
        
        if self.use_jieba:
            # 添加考研领域词典
            self._add_custom_dict()
    
    def _add_custom_dict(self):
        """添加自定义词典"""
        custom_words = [
            "考研", "择校", "院校", "分数线", "招生人数",
            "学硕", "专硕", "408", "自命题", "国家线",
            "自划线", "初试", "复试", "调剂", "二战",
            "计算机科学与技术", "软件工程", "人工智能",
            "电子信息", "控制科学与工程", "计算机组成原理",
            "操作系统", "计算机网络", "数据结构"
        ]
        for word in custom_words:
            jieba.add_word(word)
    
    def segment(self, text: str) -> List[str]:
        """
        分词
        
        Args:
            text: 输入文本
        
        Returns:
            分词结果列表
        """
        if self.use_jieba:
            return list(jieba.cut(text))
        else:
            # 简单分词（按标点和空格分割）
            import re
            tokens = re.split(r'[\s,，。、！？；：""''（）\(\)\[\]]+', text)
            return [t for t in tokens if t]
    
    def segment_with_pos(self, text: str) -> List[Tuple[str, str]]:
        """
        分词并标注词性
        
        Args:
            text: 输入文本
        
        Returns:
            [(词, 词性), ...]
        """
        if self.use_jieba:
            words = pseg.cut(text)
            return [(w.word, w.flag) for w in words]
        else:
            tokens = self.segment(text)
            # 简单估计词性
            pos_map = {
                'n': ['学校', '大学', '学院', '专业', '科目', '分数', '线'],
                'v': ['考', '复习', '推荐', '选择', '查询', '调剂'],
                'a': ['好', '难', '简单', '性价比'],
                'm': ['985', '211', 'A+', 'A', 'B+']
            }
            result = []
            for token in tokens:
                found_pos = 'n'  # 默认名词
                for pos, examples in pos_map.items():
                    if token in examples:
                        found_pos = pos
                        break
                result.append((token, found_pos))
            return result


# ==================== 关键词抽取 ====================

class KeywordExtractor:
    """
    关键词抽取器
    任务类型：关键词抽取 (Keyword Extraction)
    """
    
    # 关键词正则模式
    KEYWORD_PATTERNS = {
        'score': r'(\d{2,3})\s*分',
        'year': r'(20\d{2})\s*年',
        'percentage': r'(\d+)\s*%',
        'phone': r'1[3-9]\d{9}',
        'email': r'[\w.-]+@[\w.-]+\.\w+'
    }
    
    # 领域关键词库
    DOMAIN_KEYWORDS = {
        'school_level': ['985', '211', '双非', '普通', '一本', '二本', '三本'],
        'degree_type': ['学硕', '专硕', '全日制', '非全日制'],
        'exam_type': ['408', '自命题', '统考', '联考'],
        'region': [
            '北京', '上海', '天津', '重庆',
            '华北', '东北', '华东', '华中', '华南', '西南', '西北',
            '浙江', '江苏', '广东', '四川', '湖北', '陕西'
        ],
        'action': [
            '推荐', '选择', '查询', '考', '复习', '调剂',
            '报名', '备考', '跨考', '上岸', '冲刺', '保底'
        ],
        'subject': [
            '政治', '英语', '数学', '专业课', '408',
            '数据结构', '操作系统', '计算机网络', '组成原理'
        ]
    }
    
    def __init__(self):
        """初始化关键词抽取器"""
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式"""
        self.compiled_patterns = {}
        for key, pattern in self.KEYWORD_PATTERNS.items():
            self.compiled_patterns[key] = re.compile(pattern)
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        抽取关键词
        
        Args:
            text: 输入文本
        
        Returns:
            {关键词类型: [关键词列表]}
        """
        results = {
            'score': [],
            'year': [],
            'school_level': [],
            'degree_type': [],
            'exam_type': [],
            'region': [],
            'action': [],
            'subject': []
        }
        
        # 提取数值型关键词
        for key, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text)
            results[key] = list(set(matches))
        
        # 提取领域关键词
        for key, keywords in self.DOMAIN_KEYWORDS.items():
            found = [kw for kw in keywords if kw in text]
            if key in ['school_level', 'degree_type', 'exam_type', 'region', 'action', 'subject']:
                results[key].extend(found)
                results[key] = list(set(results[key]))
        
        return results
    
    def extract_by_type(self, text: str, keyword_type: str) -> List[str]:
        """
        提取指定类型的关键词
        
        Args:
            text: 输入文本
            keyword_type: 关键词类型
        
        Returns:
            关键词列表
        """
        if keyword_type in self.compiled_patterns:
            pattern = self.compiled_patterns[keyword_type]
            return pattern.findall(text)
        elif keyword_type in self.DOMAIN_KEYWORDS:
            keywords = self.DOMAIN_KEYWORDS[keyword_type]
            return [kw for kw in keywords if kw in text]
        return []


# ==================== 命名实体识别 / 信息抽取 ====================

class EntityRecognizer:
    """
    命名实体识别器
    任务类型：命名实体识别 (NER) / 信息抽取 (Information Extraction)
    """
    
    # 实体词典
    SCHOOLS = [
        "清华大学", "北京大学", "浙江大学", "复旦大学", "上海交通大学",
        "南京大学", "中国科学技术大学", "华中科技大学", "武汉大学",
        "中山大学", "西安交通大学", "哈尔滨工业大学", "北京航空航天大学",
        "北京理工大学", "同济大学", "天津大学", "东南大学", "中国人民大学",
        "北京师范大学", "厦门大学", "电子科技大学", "四川大学", "山东大学",
        "吉林大学", "中南大学", "大连理工大学", "华南理工大学", "兰州大学",
        "东北大学", "西北工业大学", "重庆大学", "湖南大学", "中国海洋大学",
        "国防科技大学", "中央民族大学", "西北农林科技大学", "华东师范大学",
        "西安电子科技大学", "北京邮电大学", "南京航空航天大学", "南京理工大学",
        "北京科技大学", "北京交通大学", "华东理工大学", "哈尔滨工程大学",
        "杭州电子科技大学", "重庆邮电大学", "深圳大学", "广东工业大学"
    ]
    
    MAJORS = [
        "计算机科学与技术", "软件工程", "人工智能", "电子信息",
        "控制科学与工程", "通信工程", "信息与通信工程", "网络空间安全",
        "集成电路科学与工程", "计算机技术", "软件工程", "大数据技术与工程",
        "机械工程", "电气工程", "自动化", "仪器科学与技术",
        "材料科学与工程", "化学工程与技术", "生物医学工程",
        "经济学", "金融学", "管理学", "工商管理", "会计学",
        "教育学", "心理学", "法律硕士", "非法学",
        "新闻传播学", "汉语言文学", "历史学", "哲学"
    ]
    
    ASSESSMENT_LEVELS = [
        'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-'
    ]
    
    def __init__(self):
        """初始化实体识别器"""
        self._build_entity_set()
    
    def _build_entity_set(self):
        """构建实体集合"""
        self.school_set = set(self.SCHOOLS)
        self.major_set = set(self.MAJORS)
        self.assessment_set = set(self.ASSESSMENT_LEVELS)
    
    def recognize(self, text: str) -> List[Entity]:
        """
        识别文本中的实体
        
        Args:
            text: 输入文本
        
        Returns:
            实体列表
        """
        entities = []
        
        # 识别学校实体
        for school in self.school_set:
            if school in text:
                start = text.find(school)
                entities.append(Entity(
                    text=school,
                    type='school',
                    start_pos=start,
                    end_pos=start + len(school),
                    confidence=1.0
                ))
        
        # 识别专业实体
        for major in self.major_set:
            if major in text:
                start = text.find(major)
                entities.append(Entity(
                    text=major,
                    type='major',
                    start_pos=start,
                    end_pos=start + len(major),
                    confidence=1.0
                ))
        
        # 识别评估等级
        for level in self.assessment_set:
            if level in text:
                start = text.find(level)
                entities.append(Entity(
                    text=level,
                    type='assessment_level',
                    start_pos=start,
                    end_pos=start + len(level),
                    confidence=1.0
                ))
        
        # 识别分数
        score_pattern = re.compile(r'(\d{2,3})\s*分')
        for match in score_pattern.finditer(text):
            entities.append(Entity(
                text=match.group(0),
                type='score',
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=1.0
            ))
        
        # 识别年份
        year_pattern = re.compile(r'(20\d{2})\s*年')
        for match in year_pattern.finditer(text):
            entities.append(Entity(
                text=match.group(0),
                type='year',
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=1.0
            ))
        
        # 按位置排序
        entities.sort(key=lambda x: x.start_pos)
        return entities
    
    def extract_entity_dict(self, text: str) -> Dict[str, Any]:
        """
        提取实体为字典格式
        
        Args:
            text: 输入文本
        
        Returns:
            {实体类型: 实体值}
        """
        entities = self.recognize(text)
        
        result = {
            'school': None,
            'major': None,
            'score': None,
            'year': None,
            'assessment_level': None,
            'level_type': None,  # 985/211
            'region': None
        }
        
        # 提取各类实体
        for entity in entities:
            if entity.type == 'school' and result['school'] is None:
                result['school'] = entity.text
            elif entity.type == 'major' and result['major'] is None:
                result['major'] = entity.text
            elif entity.type == 'score' and result['score'] is None:
                result['score'] = int(entity.text.replace('分', ''))
            elif entity.type == 'year' and result['year'] is None:
                result['year'] = entity.text
            elif entity.type == 'assessment_level' and result['assessment_level'] is None:
                result['assessment_level'] = entity.text
        
        # 提取院校层次
        if '985' in text:
            result['level_type'] = '985'
        elif '211' in text:
            result['level_type'] = '211'
        elif '双非' in text or '普通' in text:
            result['level_type'] = '普通'
        
        # 提取地区
        regions = {
            '华北': ['北京', '天津', '河北', '山西', '内蒙古'],
            '东北': ['辽宁', '吉林', '黑龙江'],
            '华东': ['上海', '江苏', '浙江', '安徽', '福建', '江西', '山东'],
            '华中': ['湖北', '湖南', '河南'],
            '华南': ['广东', '广西', '海南'],
            '西南': ['四川', '重庆', '云南', '贵州', '西藏'],
            '西北': ['陕西', '甘肃', '青海', '宁夏', '新疆']
        }
        for region, provinces in regions.items():
            for province in provinces:
                if province in text:
                    result['region'] = province
                    break
        
        return result


# ==================== 文本分类 ====================

class TextClassifier:
    """
    文本分类器
    任务类型：文本分类 (Text Classification)
    """
    
    # 一级分类：问题类型
    QUESTION_TYPES = [
        '咨询类',   # 问政策、问流程
        '查询类',   # 查分数线、查院校
        '推荐类',   # 求推荐、求建议
        '闲聊类'    # 打招呼、感谢
    ]
    
    # 二级分类：专业方向
    MAJOR_CATEGORIES = [
        '计算机类',      # 计算机、软件、网络安全等
        '电子类',        # 电子、通信、自动化等
        '机械类',        # 机械、车辆、仪器等
        '经济管理类',    # 金融、会计、管理等
        '文科类',        # 文学、历史、哲学等
        '理科类',        # 数学、物理、化学等
        '其他'           # 其他专业
    ]
    
    # 专业类别关键词
    MAJOR_KEYWORDS = {
        '计算机类': ['计算机', '软件', '人工智能', '网络', '安全', '数据', '大数据', '408'],
        '电子类': ['电子', '通信', '信息', '自动化', '控制', '电气', '集成'],
        '机械类': ['机械', '车辆', '仪器', '材料', '能源', '动力'],
        '经济管理类': ['经济', '金融', '管理', '会计', '审计', '工商', '物流'],
        '文科类': ['文学', '历史', '哲学', '教育', '法律', '政治', '社会'],
        '理科类': ['数学', '物理', '化学', '生物', '统计']
    }
    
    def __init__(self):
        """初始化分类器"""
        self.intent_recognizer = IntentRecognizer()
    
    def classify(self, text: str) -> Dict[str, str]:
        """
        文本分类
        
        Args:
            text: 输入文本
        
        Returns:
            {'question_type': 类型, 'major_category': 专业类别}
        """
        # 一级分类：基于意图识别
        intent, _ = self.intent_recognizer.recognize(text)
        
        intent_to_question_type = {
            IntentType.GREETING: '闲聊类',
            IntentType.THANKS: '闲聊类',
            IntentType.SCHOOL_QUERY: '查询类',
            IntentType.SCORE_QUERY: '查询类',
            IntentType.MAJOR_QUERY: '查询类',
            IntentType.SCHOOL_RECOMMEND: '推荐类',
            IntentType.POLICY_EXPLAIN: '咨询类',
            IntentType.PREPARATION: '咨询类',
            IntentType.UNKNOWN: '咨询类'
        }
        question_type = intent_to_question_type.get(intent, '咨询类')
        
        # 二级分类：基于关键词
        major_category = self._classify_major(text)
        
        return {
            'question_type': question_type,
            'major_category': major_category
        }
    
    def _classify_major(self, text: str) -> str:
        """
        分类专业方向
        
        Args:
            text: 输入文本
        
        Returns:
            专业类别
        """
        scores = {}
        
        for category, keywords in self.MAJOR_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            scores[category] = score
        
        if max(scores.values()) > 0:
            return max(scores.keys(), key=lambda x: scores[x])
        else:
            return '其他'


# ==================== NLP处理流程 ====================

class NLPProcessor:
    """
    NLP处理器
    整合所有NLP任务，提供统一的处理接口
    """
    
    def __init__(self):
        """初始化NLP处理器"""
        self.segmenter = WordSegmenter()
        self.keyword_extractor = KeywordExtractor()
        self.entity_recognizer = EntityRecognizer()
        self.intent_recognizer = IntentRecognizer()
        self.classifier = TextClassifier()
    
    def process(self, text: str, context: List[Dict] = None) -> NLPResult:
        """
        完整的NLP处理流程
        
        Args:
            text: 输入文本
            context: 对话上下文（可选）
        
        Returns:
            NLPResult对象
        """
        # 1. 分词
        tokens = self.segmenter.segment(text)
        pos_tags = self.segmenter.segment_with_pos(text)
        
        # 2. 意图识别
        if context:
            intent, confidence = self.intent_recognizer.recognize_with_context(text, context)
        else:
            intent, confidence = self.intent_recognizer.recognize(text)
        
        # 3. 关键词抽取
        keywords = self.keyword_extractor.extract(text)
        
        # 4. 实体识别
        entities = self.entity_recognizer.extract_entity_dict(text)
        
        # 5. 文本分类
        classification = self.classifier.classify(text)
        
        # 6. 情感分析（简单实现）
        sentiment = self._analyze_sentiment(text)
        
        return NLPResult(
            original_text=text,
            tokens=tokens,
            pos_tags=pos_tags,
            intent=intent,
            intent_confidence=confidence,
            keywords=keywords,
            entities=entities,
            sentiment=sentiment,
            summary=text[:100] if len(text) > 100 else text
        )
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        简单情感分析
        
        Args:
            text: 输入文本
        
        Returns:
            情感倾向：positive/negative/neutral
        """
        positive_words = ['好', '棒', '赞', '喜欢', '感谢', '谢谢', '满意', '不错']
        negative_words = ['难', '差', '不好', '糟糕', '失望', '纠结', '焦虑']
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'


# ==================== 工具函数 ====================

def load_nlp_processor() -> NLPProcessor:
    """
    加载NLP处理器
    
    Returns:
        NLPProcessor实例
    """
    return NLPProcessor()


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 测试NLP处理
    processor = NLPProcessor()
    
    test_cases = [
        "推荐一个性价比高的985院校，我预估350分",
        "东北大学考什么科目？分数线是多少？",
        "学硕和专硕有什么区别？",
        "计算机408和自命题哪个难？",
        "你好，我想咨询一下考研的问题"
    ]
    
    print("=" * 60)
    print("NLP任务测试")
    print("=" * 60)
    
    for text in test_cases:
        print(f"\n输入: {text}")
        result = processor.process(text)
        print(f"  分词: {result.tokens}")
        print(f"  意图: {result.intent.value} (置信度: {result.intent_confidence:.2f})")
        print(f"  实体: {result.entities}")
        print(f"  关键词: {result.keywords}")
        print("-" * 60)
