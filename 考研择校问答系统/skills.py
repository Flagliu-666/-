"""
考研择校智能问答系统 - Skills能力封装模块
将系统能力封装为独立的Skill组件
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ==================== Skill基类 ====================

class BaseSkill(ABC):
    """
    Skill基类
    所有Skill都应继承此类
    """
    
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
    def keywords(self) -> List[str]:
        """触发关键词"""
        return []
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Skill
        
        Args:
            params: 输入参数
        
        Returns:
            执行结果字典
        """
        pass
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """
        验证参数
        
        Args:
            params: 输入参数
        
        Returns:
            是否有效
        """
        return True


# ==================== 院校查询Skill ====================

class SchoolQuerySkill(BaseSkill):
    """
    院校查询Skill
    功能：查询院校信息、分数线、招生人数、考试科目等
    """
    
    @property
    def name(self) -> str:
        return "school_query"
    
    @property
    def description(self) -> str:
        return "查询院校信息，包括分数线、招生人数、考试科目、学科评估等"
    
    @property
    def keywords(self) -> List[str]:
        return ["查", "多少分", "招生", "考什么", "科目", "学费", "信息"]
    
    def __init__(self):
        """初始化"""
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        try:
            self.df = pd.read_csv("./data/schools_data.csv")
        except:
            self.df = pd.DataFrame()
        
        try:
            with open("./data/score_lines.json", 'r', encoding='utf-8') as f:
                self.score_data = json.load(f)
        except:
            self.score_data = {}
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行院校查询
        
        Args:
            params: {
                'school_name': str,      # 学校名称（可选）
                'query_type': str,       # 查询类型：info/score/list/all
                'user_profile': dict,     # 用户画像
                'keywords': dict          # 关键词
            }
        
        Returns:
            查询结果字典
        """
        query_type = params.get('query_type', 'info')
        school_name = params.get('school_name')
        entities = params.get('entities', {})
        
        # 优先使用实体中识别的学校名
        if not school_name and entities:
            school_name = entities.get('school')
        
        if query_type == 'info':
            return self._query_school_info(school_name)
        elif query_type == 'score':
            return self._query_score(school_name, params.get('year'))
        elif query_type == 'list':
            return self._query_school_list(params)
        elif query_type == 'major':
            return self._query_major_info(params.get('major'))
        else:
            return self._query_school_info(school_name)
    
    def _query_school_info(self, school_name: Optional[str]) -> Dict[str, Any]:
        """查询学校详细信息"""
        if not school_name:
            return {
                'success': False,
                'error': '请提供学校名称'
            }
        
        if self.df.empty:
            return {
                'success': False,
                'error': '院校数据加载失败'
            }
        
        # 模糊匹配学校名
        school_data = self.df[
            self.df['学校名称'].str.contains(school_name, na=False, regex=False)
        ]
        
        if school_data.empty:
            return {
                'success': False,
                'error': f'未找到与"{school_name}"相关的院校'
            }
        
        # 取第一个匹配结果
        row = school_data.iloc[0]
        
        result = {
            'success': True,
            'data': {
                'school': row['学校名称'],
                'location': row['所在地'],
                'level': row['层次'],
                'score_line': row.get('2024复试分数线', '暂无'),
                'enrollment': row.get('招生人数', '暂无'),
                'assessment': row.get('学科评估', '暂无'),
                'subjects': {
                    'politics': row.get('初试科目(政治)', ''),
                    'english': row.get('初试科目(英语)', ''),
                    'math': row.get('初试科目(数学)', ''),
                    'professional': row.get('初试科目(专业课)', '')
                },
                'notes': row.get('备注', '')
            },
            'answer': self._format_school_info(row),
            'source': '本地院校数据库'
        }
        
        return result
    
    def _format_school_info(self, row) -> str:
        """格式化学校信息"""
        return f"""
**{row['学校名称']}** 信息如下：

📍 **基本信息**
- 位置: {row['所在地']}
- 层次: {row['层次']}

📈 **分数线**
- 2024复试分数线: {row.get('2024复试分数线', '暂无')}分

👥 **招生情况**
- 招生人数: {row.get('招生人数', '暂无')}人

📚 **初试科目**
- {row.get('初试科目(政治)', '')}
- {row.get('初试科目(英语)', '')}
- {row.get('初试科目(数学)', '')}
- {row.get('初试科目(专业课)', '')}

🏆 **学科评估**: {row.get('学科评估', '暂无')}

💡 **备注**: {row.get('备注', '暂无')}
"""
    
    def _query_score(self, school_name: Optional[str], year: Optional[str] = None) -> Dict[str, Any]:
        """查询分数线"""
        if school_name:
            # 特定学校分数线
            return self._query_school_info(school_name)
        else:
            # 返回国家线
            return self._query_national_score(year)
    
    def _query_national_score(self, year: Optional[str] = None) -> Dict[str, Any]:
        """查询国家线"""
        year_key = f"{year}年国家线" if year else "2024年国家线"
        
        if year_key in self.score_data:
            scores = self.score_data[year_key]
            lines = scores.get('A类', {})
            
            answer = f"**{year_key}A类考生国家线**：\n\n"
            for category, info in lines.items():
                if isinstance(info, dict):
                    answer += f"- **{category}**: 总分{info.get('总分', '暂无')}分 "
                    answer += f"(政治英语{info.get('政治英语', '')}, 专业课{info.get('专业课', '')}分)\n"
            
            return {
                'success': True,
                'data': lines,
                'answer': answer,
                'source': '教育部国家线数据'
            }
        
        return {
            'success': False,
            'error': f'未找到{year_key}数据'
        }
    
    def _query_school_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """查询学校列表"""
        if self.df.empty:
            return {
                'success': False,
                'error': '院校数据加载失败'
            }
        
        level = params.get('level_type') or params.get('user_profile', {}).get('level', '985')
        score = params.get('score') or params.get('user_profile', {}).get('score')
        
        filtered = self.df.copy()
        
        # 按层次筛选
        if level == '985':
            filtered = filtered[filtered['层次'] == '985']
        elif level == '211':
            filtered = filtered[filtered['层次'].isin(['985', '211'])]
        
        # 按分数筛选
        if score:
            filtered = filtered[filtered['2024复试分数线'] <= score + 30]
        
        # 按性价比排序
        filtered = filtered.sort_values('学科评估', ascending=False).head(10)
        
        schools = []
        for _, row in filtered.iterrows():
            schools.append({
                'name': row['学校名称'],
                'level': row['层次'],
                'location': row['所在地'],
                'score': row.get('2024复试分数线', '暂无'),
                'assessment': row.get('学科评估', '暂无')
            })
        
        return {
            'success': True,
            'data': {'schools': schools},
            'answer': self._format_school_list(schools),
            'source': '本地院校数据库'
        }
    
    def _format_school_list(self, schools: List[Dict]) -> str:
        """格式化学校列表"""
        if not schools:
            return "未找到符合条件的院校"
        
        answer = f"**为你找到{len(schools)}所院校**：\n\n"
        
        for i, school in enumerate(schools, 1):
            answer += f"{i}. **{school['name']}** ({school['level']})\n"
            answer += f"   📍 {school['location']} | 📈 {school['score']}分 | 🏆 {school['assessment']}\n\n"
        
        return answer
    
    def _query_major_info(self, major: Optional[str]) -> Dict[str, Any]:
        """查询专业信息"""
        try:
            with open("./data/major_knowledge.json", 'r', encoding='utf-8') as f:
                major_data = json.load(f)
        except:
            major_data = {}
        
        if major and major in major_data:
            info = major_data[major]
            answer = f"**{major}** 专业信息：\n\n"
            answer += f"- 学科代码: {info.get('code', '暂无')}\n"
            answer += f"- 学科门类: {info.get('category', '暂无')}\n"
            answer += f"- 初试科目: {info.get('subject1', '')}, {info.get('subject2', '')}, {info.get('subject3', '')}, {info.get('subject4', '')}\n"
            answer += f"- 就业前景: {', '.join(info.get('job_prospects', []))}\n"
            answer += f"- 难度等级: {info.get('difficulty', '暂无')}\n"
            
            return {
                'success': True,
                'data': info,
                'answer': answer,
                'source': '专业数据库'
            }
        
        return {
            'success': False,
            'error': '未找到该专业信息'
        }
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """验证参数"""
        return True  # 始终有效，未指定学校时返回列表


# ==================== 智能推荐Skill ====================

class SmartRecommendSkill(BaseSkill):
    """
    智能推荐Skill
    功能：根据用户画像推荐合适的院校
    """
    
    @property
    def name(self) -> str:
        return "smart_recommend"
    
    @property
    def description(self) -> str:
        return "根据用户画像（分数、本科层次、专业偏好、地区偏好）智能推荐院校"
    
    @property
    def keywords(self) -> List[str]:
        return ["推荐", "选择", "择校", "性价比", "哪个学校好", "上岸"]
    
    def __init__(self):
        """初始化"""
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        try:
            self.df = pd.read_csv("./data/schools_data.csv")
        except:
            self.df = pd.DataFrame()
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行智能推荐
        
        Args:
            params: {
                'recommend_type': str,      # 推荐类型：by_profile/by_score
                'user_profile': dict,        # 用户画像
                'entities': dict,            # 识别的实体
                'original_text': str          # 原始问题
            }
        
        Returns:
            推荐结果
        """
        user_profile = params.get('user_profile', {})
        entities = params.get('entities', {})
        
        # 提取推荐参数
        score = entities.get('score') or user_profile.get('score', 330)
        level = entities.get('level_type') or user_profile.get('background', '普通一本')
        major = entities.get('major') or user_profile.get('target_major', '计算机科学与技术')
        regions = user_profile.get('target_region', [])
        
        # 根据分数确定推荐策略
        if score >= 380:
            recommend_level = '985'
            advice = "以您的分数，可以冲击985顶尖院校！"
        elif score >= 340:
            recommend_level = '985'
            advice = "以您的分数，建议报考985中等院校或211强势专业。"
        elif score >= 310:
            recommend_level = '211'
            advice = "以您的分数，建议报考211院校或普通院校王牌专业。"
        elif score >= 280:
            recommend_level = '211'
            advice = "以您的分数，建议重点考虑211院校或普通院校。"
        else:
            recommend_level = '普通'
            advice = "以您的分数，建议选择普通院校，上岸机会更大。"
        
        # 执行推荐
        recommendations = self._get_recommendations(
            score=score,
            level=recommend_level,
            major=major,
            regions=regions,
            user_level=level
        )
        
        # 格式化回答
        answer = self._format_recommendations(recommendations, advice, score)
        
        return {
            'success': True,
            'data': recommendations,
            'answer': answer,
            'source': '智能推荐算法'
        }
    
    def _get_recommendations(self, score: int, level: str, major: str,
                            regions: List[str], user_level: str) -> List[Dict]:
        """
        获取推荐列表
        
        Args:
            score: 预估分数
            level: 目标院校层次
            major: 目标专业
            regions: 目标地区
            user_level: 用户本科层次
        
        Returns:
            推荐列表
        """
        if self.df.empty:
            return []
        
        filtered = self.df.copy()
        
        # 1. 按层次筛选
        if level == '985':
            filtered = filtered[filtered['层次'] == '985']
        elif level == '211':
            filtered = filtered[(filtered['层次'] == '985') | (filtered['层次'] == '211')]
        else:
            # 普通院校：选择211中分数线较低的
            filtered = filtered[
                (filtered['层次'] != '985') & (filtered['层次'] != '211')
            ]
            if len(filtered) == 0:
                filtered = self.df[self.df['层次'] == '211'].copy()
        
        # 2. 按分数筛选
        if score >= 340:
            filtered = filtered[filtered['2024复试分数线'] <= score - 10]
        elif score >= 280:
            filtered = filtered[
                (filtered['2024复试分数线'] <= score + 20) &
                (filtered['2024复试分数线'] >= score - 40)
            ]
        else:
            filtered = filtered.sort_values('2024复试分数线')
        
        # 3. 按地区偏好排序
        if regions:
            region_map = {
                '华北': ['北京', '天津', '河北', '山西', '内蒙古'],
                '东北': ['辽宁', '吉林', '黑龙江'],
                '华东': ['上海', '江苏', '浙江', '安徽', '福建', '江西', '山东'],
                '华中': ['湖北', '湖南', '河南'],
                '华南': ['广东', '广西', '海南'],
                '西南': ['四川', '重庆', '云南', '贵州', '西藏'],
                '西北': ['陕西', '甘肃', '青海', '宁夏', '新疆']
            }
            target_provinces = []
            for r in regions:
                if r in region_map:
                    target_provinces.extend(region_map[r])
            
            if target_provinces:
                filtered['in_region'] = filtered['所在地'].isin(target_provinces).astype(int)
                filtered = filtered.sort_values(['in_region', '学科评估'], ascending=[False, False])
        
        # 4. 计算性价比分数
        grade_map = {'A+': 10, 'A': 9, 'A-': 8, 'B+': 7, 'B': 6, 'B-': 5, 'C+': 4, 'C': 3, '-': 0, '': 0}
        filtered['grade_score'] = filtered['学科评估'].map(lambda x: grade_map.get(str(x), 0))
        filtered['value_score'] = filtered['grade_score'] - filtered['2024复试分数线'] / 50
        filtered = filtered.sort_values('value_score', ascending=False)
        
        # 5. 取前6所
        results = []
        for _, row in filtered.head(6).iterrows():
            # 计算稳妥程度
            diff = score - row['2024复试分数线']
            if diff >= 30:
                stability = "🟢 较稳"
            elif diff >= 15:
                stability = "🟡 中等"
            elif diff >= 0:
                stability = "🟠 有风险"
            else:
                stability = "🔴 难度大"
            
            results.append({
                'name': row['学校名称'],
                'level': row['层次'],
                'location': row['所在地'],
                'score': row['2024复试分数线'],
                'assessment': row['学科评估'] if row['学科评估'] else '-',
                'enrollment': row.get('招生人数', '暂无'),
                'stability': stability
            })
        
        return results
    
    def _format_recommendations(self, recommendations: List[Dict], 
                                advice: str, score: int) -> str:
        """格式化推荐结果"""
        if not recommendations:
            return f"{advice}\n\n当前条件下未找到合适的推荐院校，请调整分数或扩大范围。"
        
        answer = f"**{advice}**\n\n"
        answer += f"根据你的情况（预估{score}分），为你推荐以下院校：\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            answer += f"**{i}. {rec['name']}** ({rec['level']})\n"
            answer += f"   📍 {rec['location']} | 📈 {rec['score']}分 | {rec['stability']}\n"
            answer += f"   🏆 学科评估: {rec['assessment']} | 👥 招生: {rec['enrollment']}人\n\n"
        
        answer += "\n💡 **温馨提示**：以上推荐仅供参考，实际录取分数线每年会有波动，建议关注目标院校的历年数据和最新招生简章。"
        
        return answer
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """验证参数"""
        return True


# ==================== 政策解读Skill ====================

class PolicyExplainSkill(BaseSkill):
    """
    政策解读Skill
    功能：解读考研政策、学硕专硕区别、408vs自命题等
    """
    
    @property
    def name(self) -> str:
        return "policy_explain"
    
    @property
    def description(self) -> str:
        return "解读考研政策，包括学硕vs专硕区别、408vs自命题、国家线vs校线等"
    
    @property
    def keywords(self) -> List[str]:
        return ["区别", "学硕", "专硕", "408", "自命题", "国家线", "政策", "流程"]
    
    def __init__(self):
        """初始化"""
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        try:
            with open("./data/policy_knowledge.json", 'r', encoding='utf-8') as f:
                self.policy_data = json.load(f)
        except:
            self.policy_data = {}
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行政策解读
        
        Args:
            params: {
                'topic': str,              # 话题类型
                'user_profile': dict,       # 用户画像
                'original_text': str        # 原始问题
            }
        """
        original_text = params.get('original_text', '')
        topic = params.get('topic', '')
        
        # 根据问题内容确定解读话题
        if '学硕' in original_text and '专硕' in original_text:
            return self._explain_degree_type()
        elif '408' in original_text or '自命题' in original_text:
            return self._explain_exam_type()
        elif '国家线' in original_text or '校线' in original_text:
            return self._explain_score_line()
        elif '流程' in original_text or '报名' in original_text:
            return self._explain_process()
        elif '跨考' in original_text:
            return self._explain_cross_exam()
        else:
            return self._explain_general(original_text)
    
    def _explain_degree_type(self) -> Dict[str, Any]:
        """解读学硕vs专硕"""
        answer = """**学硕 vs 专硕 区别详解**

📊 **培养目标**
- **学硕**：培养学术研究人才，侧重科研能力
- **专硕**：培养应用型专业人才，侧重实践能力

📚 **考试科目**
- **学硕**：通常考英语一+数学一（工科），难度较大
- **专硕**：通常考英语二+数学二（部分专业），难度较小

⏰ **学制**
- **学硕**：通常3年
- **专硕**：通常2-3年

💰 **学费**
- **学硕**：通常8000元/年
- **专硕**：通常10000-20000元/年

🎓 **读博**
- **学硕**：可直接申请硕博连读/直博
- **专硕**：需参加统考或申请考核

📈 **适合人群**
- **学硕**：想读博、进高校、做科研
- **专硕**：想就业、提升学历、快速上岸

💡 **建议**：如果不确定未来方向，专硕是更稳妥的选择；如果有读博打算，学硕更有优势。
"""
        return {
            'success': True,
            'data': {'type': 'degree_comparison'},
            'answer': answer,
            'source': '考研政策知识库'
        }
    
    def _explain_exam_type(self) -> Dict[str, Any]:
        """解读408vs自命题"""
        answer = """**408统考 vs 自命题 深度对比**

📋 **408计算机学科专业基础**

考试内容（约300分）：
- 数据结构（约45分）
- 计算机组成原理（约45分）
- 操作系统（约35分）
- 计算机网络（约25分）

优点：
✅ 全国统一命题，真题资料丰富
✅ 复习资料容易获取
✅ 调剂时选择多

缺点：
❌ 难度大，覆盖面广
❌ 需要复习4门课
❌ 题目灵活，不易拿高分

📋 **自命题院校**

常见科目：
- 数据结构+程序设计
- 电路+数字电路
- 信号与系统

优点：
✅ 只考1-2门课，复习量小
✅ 可能遇到历年原题
✅ 针对性复习效率高

缺点：
❌ 真题资料难找
❌ 调剂受限
❌ 可能临时换大纲

💡 **选择建议**：
- 冲好学校 → 选408（有更多选择）
- 求稳上岸 → 选自命题（复习压力小）
"""
        return {
            'success': True,
            'data': {'type': 'exam_comparison'},
            'answer': answer,
            'source': '考研政策知识库'
        }
    
    def _explain_score_line(self) -> Dict[str, Any]:
        """解读分数线"""
        answer = """**考研分数线详解**

📊 **国家线**
- 由教育部统一划定
- 是考生进入复试的最低分数线
- 分为A类（东部）和B类（西部）
- B类通常比A类低10分

📊 **校线（院校分数线）**
- 由各招生单位自行确定
- 通常高于或等于国家线
- 是考生进入该院校复试的分数线

📊 **自划线（34所自主划线）**
- 34所985高校自主划定分数线
- 通常高于国家线
- 可早于国家线公布，早于国家线复试

⚠️ **提醒**：
1.过了国家线不一定能进复试
2.过了校线才能参加该院校复试
3.34所自划线院校可早于国家线确定复试名单
"""
        return {
            'success': True,
            'data': {'type': 'score_line_explanation'},
            'answer': answer,
            'source': '考研政策知识库'
        }
    
    def _explain_process(self) -> Dict[str, Any]:
        """解读考研流程"""
        answer = """**考研全流程时间线**

📅 **备考阶段**（1月-12月）
- 确定目标院校和专业
- 制定复习计划
- 基础+强化+冲刺复习

📝 **预报名**（每年9月下旬）
- 对象：应届本科毕业生
- 报名成功即有效，可修改信息

📝 **正式报名**（每年10月5日-25日）
- 对象：所有考生
- 最终报名机会，仔细核对信息

📋 **网上确认**（每年11月初）
- 不确认=报名无效！
- 准备身份证、证件照、学历证明

📝 **初试**（每年12月最后一个周末）
- 政治、英语、数学、专业课
- 提前订房，熟悉考场

📊 **成绩公布**（次年2月中下旬）
- 渠道：研招网、各省教育考试院

📈 **国家线公布**（次年3月中旬）
- A类（东部）和B类（西部）

📝 **复试**（次年3-4月）
- 专业课笔试+综合面试+英语

📝 **调剂**（次年3月底-4月底）
- 早联系、早准备、主动出击
"""
        return {
            'success': True,
            'data': {'type': 'process_explanation'},
            'answer': answer,
            'source': '考研政策知识库'
        }
    
    def _explain_cross_exam(self) -> Dict[str, Any]:
        """解读跨考"""
        answer = """**跨专业考研指南**

🎯 **跨考最容易上岸的专业**

1. **法律硕士(非法学)**
   - 不考数学，只考法律基础知识
   - 跨考门槛低，文科理科都能考
   - 招生规模大，上岸几率高

2. **教育学**
   - 不考数学，专业课纯记忆
   - 就业前景好，教师需求大

3. **新闻与传播**
   - 不考数学，跨考友好
   - 实践性强，就业面广

4. **社会工作**
   - 冷门专业，竞争小
   - 不考数学，国家线低

📚 **跨考建议**

- **文科→法律、教育、新传**：不考数学，复习量相对较小
- **理科→计算机**：难但香，但需要补数据结构等基础
- **工科→管理类**：数学优势明显，复习压力小

⚠️ **注意事项**
1. 部分专业不接收跨考（如医学）
2. 跨考需加试专业课
3. 理工科跨考文科通常较容易
"""
        return {
            'success': True,
            'data': {'type': 'cross_exam_explanation'},
            'answer': answer,
            'source': '考研政策知识库'
        }
    
    def _explain_general(self, text: str) -> Dict[str, Any]:
        """通用政策解读"""
        return {
            'success': True,
            'data': {'type': 'general'},
            'answer': "关于考研政策，如果还有其他疑问，欢迎继续提问！我可以帮你解答学硕专硕区别、408与自命题对比、国家线与校线、考研流程等各种问题。",
            'source': '考研政策知识库'
        }
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """验证参数"""
        return True


# ==================== 备考咨询Skill ====================

class PreparationConsultSkill(BaseSkill):
    """
    备考咨询Skill
    功能：提供复习计划、资料推荐、常见问题解答
    """
    
    @property
    def name(self) -> str:
        return "preparation_consult"
    
    @property
    def description(self) -> str:
        return "提供考研复习计划、备考资料推荐、常见问题解答"
    
    @property
    def keywords(self) -> List[str]:
        return ["复习", "备考", "计划", "资料", "怎么学", "时间安排"]
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行备考咨询
        """
        original_text = params.get('original_text', '')
        user_profile = params.get('user_profile', {})
        
        # 根据问题内容确定咨询类型
        if '计划' in original_text or '安排' in original_text:
            return self._give_review_plan(user_profile)
        elif '资料' in original_text or '教材' in original_text:
            return self._recommend_materials(user_profile)
        elif '政治' in original_text:
            return self._consult_politics()
        elif '英语' in original_text:
            return self._consult_english()
        elif '数学' in original_text:
            return self._consult_math()
        else:
            return self._consult_general(user_profile)
    
    def _give_review_plan(self, user_profile: Dict) -> Dict[str, Any]:
        """给出复习计划"""
        progress = user_profile.get('progress', '基础阶段')
        
        if progress == '刚开始':
            plan = """**基础阶段复习计划（现在-6月）**

📚 **英语**
- 背单词：每天50-100个，使用墨墨/扇贝
- 长难句：田静《句句真研》
- 语法基础：系统学习英语语法

📐 **数学**
- 过一遍教材：高数、线代、概率
- 看基础视频：张宇/汤家凤基础班
- 做课后习题：打牢基础

💻 **专业课**
- 考408：开始数据结构、组成原理
- 自命题：按目标院校大纲复习

📅 **每日时间**：4-6小时
"""
        elif progress == '基础阶段':
            plan = """**强化阶段复习计划（7-9月）**

📚 **英语**
- 背单词：继续，每天复习
- 做阅读：历年真题阅读部分
- 开始作文：积累素材

📐 **数学**
- 看强化视频
- 做习题集：660题、330题
- 整理知识框架

💻 **专业课**
- 完成408四门课基础
- 开始做历年真题
- 整理笔记和重点

📅 **每日时间**：8-10小时
"""
        else:
            plan = """**冲刺阶段复习计划（10-12月）**

📚 **英语**
- 作文模板背诵
- 全真模拟真题
- 保持做题手感

📐 **数学**
- 做历年真题（近15年）
- 模拟题：张宇8+4、李林6+4
- 查漏补缺

💻 **专业课**
- 二刷、三刷真题
- 背诵重点知识点
- 全真模拟

📅 **每日时间**：10-12小时

💡 **最后两周**：调整作息，查漏补缺，保持状态
"""
        
        return {
            'success': True,
            'data': {'type': 'review_plan', 'stage': progress},
            'answer': plan,
            'source': '备考咨询知识库'
        }
    
    def _recommend_materials(self, user_profile: Dict) -> Dict[str, Any]:
        """推荐资料"""
        answer = """**考研备考资料推荐**

📚 **政治**
- 教材：肖秀荣《精讲精练》/ 徐涛《核心考案》
- 视频：徐涛强化班
- 刷题：肖秀荣《1000题》
- 冲刺：肖秀荣《肖4》《肖8》
- 押题：腿姐技巧班、冲刺班

📝 **英语**
- 单词：墨墨背单词 /《红宝书》
- 真题：张剑《黄皮书》/《考研真相》
- 作文：王江涛《高分写作》
- 阅读：唐迟《阅读的逻辑》

📐 **数学**
- 教材：张宇《基础30讲》/ 汤家凤《复习大全》
- 视频：张宇/汤家凤/武忠祥
- 习题：张宇《1000题》/ 李永乐《660题》
- 真题：张宇/李永乐真题
- 模拟：张宇8+4 / 李林6+4 / 合工大超越

💻 **专业课（408）**
- 教材：王道《408复习指导》/ 天勤《高分笔记》
- 视频：王道/咸鱼学姐
- 真题：历年统考真题

💡 **建议**：资料不在多，在于吃透！选择一套适合自己的，坚持到底。
"""
        return {
            'success': True,
            'data': {'type': 'materials'},
            'answer': answer,
            'source': '备考咨询知识库'
        }
    
    def _consult_politics(self) -> Dict[str, Any]:
        """咨询政治"""
        answer = """**考研政治备考建议**

⏰ **什么时候开始**
- 建议7-8月开始
- 不用太早，9月也来得及
- 太早开始会占用其他科目时间

📚 **复习策略**
- **7-9月**：看视频+做选择题
- **10月**：二刷选择题，重点章节
- **11月**：做肖8，关注时政
- **12月**：背肖4，做模拟题

📊 **分值分布**
- 单选16分 + 多选34分 = 选择50分
- 分析题50分

💡 **高分技巧**
1. 选择题是重点，得选择者得天下
2. 分析题拉不开差距，背好肖4
3. 字迹工整，分点作答
4. 结合材料，结合时政

📈 **目标分数**
- 过线：60分左右
- 较高：70分
- 高分：80+
"""
        return {
            'success': True,
            'data': {'type': 'politics_consult'},
            'answer': answer,
            'source': '备考咨询知识库'
        }
    
    def _consult_english(self) -> Dict[str, Any]:
        """咨询英语"""
        answer = """**考研英语备考建议**

⏰ **单词背诵**
- 贯穿全程，每天坚持
- 推荐APP：墨墨、扇贝、不背
- 《红宝书》或《恋练有词》
- 核心词汇约5500，每天50-100个

📖 **阅读理解**
- 得阅读者得英语！
- 用历年真题复习，不要做模拟题
- 唐迟阅读视频课
- 精读：每篇阅读都要分析长难句

📝 **作文**
- 10月开始准备
- 背诵模板，但不要照抄
- 整理自己的模板
- 练习写历年真题作文

🕐 **时间安排**
- 现在-6月：背单词+长难句
- 7-9月：阅读+真题
- 10-12月：作文+模拟+保持手感

💡 **英语一 vs 英语二**
- 英语一：难度略大，文章选材学术
- 英语二：相对简单，文章选材日常
- 复习方法通用，但真题不要混用
"""
        return {
            'success': True,
            'data': {'type': 'english_consult'},
            'answer': answer,
            'source': '备考咨询知识库'
        }
    
    def _consult_math(self) -> Dict[str, Any]:
        """咨询数学"""
        answer = """**考研数学备考建议**

📐 **数一/数二/数三区别**
- 数一：高数60%+线代20%+概率20%（最难）
- 数二：高数80%+线代20%（内容最少）
- 数三：高数60%+线代20%+概率20%（经济类）

📚 **复习资料选择**
- 张宇：适合基础好、追求高分
- 汤家凤：适合基础一般、扎实复习
- 武忠祥：适合想快速提升
- 李永乐：线代跟李永乐准没错

📈 **复习阶段**
- **基础（现在-6月）**：过教材，看基础班，做课后题
- **强化（7-9月）**：看强化班，做习题集，整理框架
- **冲刺（10-12月）**：做真题，做模拟题，查漏补缺

💡 **高分技巧**
1. 大量做题是王道！不做题等于没复习
2. 整理错题本，定期回顾
3. 真题至少做两遍
4. 模拟题用来查漏补缺，不要太在意分数
5. 公式要背熟，考场没时间推导
"""
        return {
            'success': True,
            'data': {'type': 'math_consult'},
            'answer': answer,
            'source': '备考咨询知识库'
        }
    
    def _consult_general(self, user_profile: Dict) -> Dict[str, Any]:
        """通用备考咨询"""
        return {
            'success': True,
            'data': {'type': 'general'},
            'answer': "考研备考方面，如果还有其他疑问，欢迎继续提问！我可以帮你解答政治、英语、数学、专业课的复习方法和资料推荐等问题。",
            'source': '备考咨询知识库'
        }
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """验证参数"""
        return True


# ==================== 回答生成Skill ====================

class AnswerGeneratorSkill(BaseSkill):
    """
    回答生成Skill
    功能：根据上下文生成最终回答
    """
    
    @property
    def name(self) -> str:
        return "answer_generator"
    
    @property
    def description(self) -> str:
        return "根据对话上下文和用户问题生成最终回答"
    
    @property
    def keywords(self) -> List[str]:
        return []  # 作为默认Skill，不需要特定关键词
    
    def __init__(self):
        """初始化"""
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        try:
            with open("./data/grad_consult_qa.json", 'r', encoding='utf-8') as f:
                self.qa_data = json.load(f)
        except:
            self.qa_data = []
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成回答
        """
        original_text = params.get('original_text', '')
        
        # 尝试从知识库中找相似问题
        answer = self._find_similar_qa(original_text)
        
        if answer:
            return {
                'success': True,
                'answer': answer,
                'source': '知识库匹配'
            }
        
        # 默认回答
        return {
            'success': True,
            'answer': self._get_default_response(original_text),
            'source': '智能生成'
        }
    
    def _find_similar_qa(self, question: str) -> Optional[str]:
        """查找相似问答"""
        if not self.qa_data:
            return None
        
        question_lower = question.lower()
        
        for qa in self.qa_data:
            instruction = qa.get('instruction', '').lower()
            # 简单关键词匹配
            keywords = [w for w in instruction if len(w) >= 3]
            match_count = sum(1 for kw in keywords if kw in question_lower)
            
            if match_count >= 2:
                return qa.get('output', '')
        
        return None
    
    def _get_default_response(self, question: str) -> str:
        """获取默认回答"""
        question_lower = question.lower()
        
        # 打招呼
        if any(w in question_lower for w in ['你好', '您好', 'hi', 'hello']):
            return """你好！👋 我是考研择校小助手，很高兴为你服务！

我可以帮你：
📚 查询院校分数线、招生信息
🎯 根据你的情况推荐合适院校
📖 解答学硕专硕、408自命题等政策问题
💡 提供备考建议和复习计划

请告诉我你的情况（预估分数、目标专业等），我来帮你分析！
"""
        
        # 感谢
        if any(w in question_lower for w in ['谢谢', '感谢', '多谢']):
            return "不客气！祝你考研顺利，一战成硕！🎓 如有其他问题随时问我。"
        
        # 通用回复
        return """你说的这个问题我可能理解不够准确。

请换个方式问我，比如：
• "推荐计算机985院校"
• "东北大学考什么科目"
• "学硕和专硕有什么区别"
• "政治怎么复习"

或者告诉我你的情况（分数、专业偏好），我来帮你分析！
"""


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Skills模块测试")
    print("=" * 60)
    
    # 测试院校查询
    school_skill = SchoolQuerySkill()
    result = school_skill.execute({
        'query_type': 'info',
        'school_name': '东北大学'
    })
    print(f"\n院校查询结果: {result.get('success')}")
    if result.get('success'):
        print(f"学校: {result['data']['school']}")
    
    # 测试智能推荐
    recommend_skill = SmartRecommendSkill()
    result = recommend_skill.execute({
        'user_profile': {'score': 350, 'background': '普通一本'},
        'recommend_type': 'by_profile'
    })
    print(f"\n智能推荐结果: {result.get('success')}")
    if result.get('success'):
        print(f"推荐数量: {len(result['data'])}所院校")
    
    # 测试政策解读
    policy_skill = PolicyExplainSkill()
    result = policy_skill.execute({
        'original_text': '学硕和专硕有什么区别？'
    })
    print(f"\n政策解读结果: {result.get('success')}")
    
    print("\n" + "=" * 60)
