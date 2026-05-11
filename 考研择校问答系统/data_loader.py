"""
数据加载器 - 统一管理系统所有数据
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


class DataLoader:
    """统一数据加载器"""
    
    def __init__(self, data_dir: str = None):
        """初始化数据加载器"""
        self.project_root = Path(__file__).parent
        self.data_dir = data_dir or str(self.project_root / "data")
        
        # 数据存储
        self.schools = {}
        self.qa_data = []
        self.discipline_data = {}
        self.score_data = {}
        self.ranking_data = {}
        self.enhanced_data = {}
        
        # 985/211数据
        self.schools_985 = []
        self.schools_211 = []
        
    def load_all(self):
        """加载所有数据"""
        self._load_schools_data()
        self._load_qa_data()
        self._load_discipline_data()
        self._load_score_data()
        self._load_ranking_data()
        self._load_school_lists()
    
    def _load_schools_data(self):
        """加载院校数据"""
        schools_file = Path(self.data_dir) / "schools_data.csv"
        if schools_file.exists():
            import csv
            with open(schools_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    school = {
                        'name': row.get('院校名称', ''),
                        'province': row.get('所在省份', ''),
                        'type': row.get('院校类型', ''),
                        'level': row.get('院校层次', ''),
                        'is_985': '985' in row.get('院校层次', ''),
                        'is_211': '211' in row.get('院校层次', ''),
                        'rank': row.get('排名', ''),
                        'feature': row.get('院校特色', '')
                    }
                    if school['name']:
                        self.schools[school['name']] = school
        
        # 如果CSV不存在，尝试加载JSON
        if not self.schools:
            schools_985_file = Path(self.data_dir) / "schools_985.json"
            if schools_985_file.exists():
                with open(schools_985_file, 'r', encoding='utf-8') as f:
                    self.schools_985 = json.load(f)
                    for school in self.schools_985:
                        # 处理中文字段名
                        name = school.get('名称') or school.get('name', '')
                        school['name'] = name
                        self.schools[name] = school
                        
            schools_211_file = Path(self.data_dir) / "schools_211.json"
            if schools_211_file.exists():
                with open(schools_211_file, 'r', encoding='utf-8') as f:
                    self.schools_211 = json.load(f)
                    for school in self.schools_211:
                        name = school.get('名称') or school.get('name', '')
                        school['name'] = name
                        if name not in self.schools:
                            self.schools[name] = school
    
    def _load_qa_data(self):
        """加载问答数据"""
        qa_file = Path(self.data_dir) / "grad_consult_qa.json"
        if qa_file.exists():
            with open(qa_file, 'r', encoding='utf-8') as f:
                self.qa_data = json.load(f)
    
    def _load_discipline_data(self):
        """加载学科数据"""
        discipline_file = Path(self.data_dir) / "discipline_full.json"
        if discipline_file.exists():
            with open(discipline_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.discipline_data = data
                elif isinstance(data, list):
                    for item in data:
                        if 'name' in item:
                            self.discipline_data[item['name']] = item
    
    def _load_score_data(self):
        """加载分数线数据"""
        national_file = Path(self.data_dir) / "national_scores.json"
        if national_file.exists():
            with open(national_file, 'r', encoding='utf-8') as f:
                self.score_data['national'] = json.load(f)
        
        self_drawn_file = Path(self.data_dir) / "self_drawn_scores.json"
        if self_drawn_file.exists():
            with open(self_drawn_file, 'r', encoding='utf-8') as f:
                self.score_data['self_drawn'] = json.load(f)
    
    def _load_ranking_data(self):
        """加载排名数据"""
        ranking_file = Path(self.data_dir) / "university_rankings.json"
        if ranking_file.exists():
            with open(ranking_file, 'r', encoding='utf-8') as f:
                self.ranking_data = json.load(f)
    
    def _load_school_lists(self):
        """加载985/211列表"""
        schools_985_file = Path(self.data_dir) / "schools_985.json"
        if schools_985_file.exists():
            with open(schools_985_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 处理中文字段名
                for school in data:
                    school['name'] = school.get('名称') or school.get('name', '')
                self.schools_985 = data
        
        schools_211_file = Path(self.data_dir) / "schools_211.json"
        if schools_211_file.exists():
            with open(schools_211_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for school in data:
                    school['name'] = school.get('名称') or school.get('name', '')
                self.schools_211 = data
    
    def get_school(self, name: str) -> Optional[Dict]:
        """获取院校信息"""
        return self.schools.get(name)
    
    def search_schools(self, keyword: str) -> List[Dict]:
        """搜索院校"""
        results = []
        keyword_lower = keyword.lower()
        for school in self.schools.values():
            if (keyword_lower in school.get('name', '').lower() or
                keyword_lower in school.get('province', '').lower() or
                keyword_lower in school.get('feature', '').lower()):
                results.append(school)
        return results
    
    def get_discipline(self, name: str) -> Optional[Dict]:
        """获取学科信息"""
        # 精确匹配
        if name in self.discipline_data:
            return self.discipline_data[name]
        # 模糊匹配
        name_lower = name.lower()
        for disc_name, disc_data in self.discipline_data.items():
            if name_lower in disc_name.lower():
                return disc_data
        return None
    
    def get_qa_pairs(self, category: str = None) -> List[Dict]:
        """获取问答对"""
        if category:
            return [qa for qa in self.qa_data if qa.get('category') == category]
        return self.qa_data
    
    def get_scores(self, year: int = None) -> Dict:
        """获取分数线"""
        if year:
            return self.score_data.get(year, {})
        return self.score_data


class QAGenerator:
    """问答生成器"""
    
    def __init__(self, data_loader: DataLoader):
        """初始化问答生成器"""
        self.data_loader = data_loader
        self._build_index()
    
    def _build_index(self):
        """构建搜索索引"""
        self.school_index = {}
        self.discipline_index = {}
        self.qa_index = {}
        
        # 院校索引
        for name, school in self.data_loader.schools.items():
            keywords = [name]
            if school.get('province'):
                keywords.append(school['province'])
            if school.get('feature'):
                keywords.extend(school['feature'].split('、'))
            for kw in keywords:
                self.school_index[kw.lower()] = school
        
        # 学科索引
        for name, discipline in self.data_loader.discipline_data.items():
            self.discipline_index[name.lower()] = discipline
        
        # QA索引
        for i, qa in enumerate(self.data_loader.qa_data):
            self.qa_index[i] = qa
    
    def generate_response(self, question: str) -> str:
        """生成回答"""
        question_lower = question.lower()
        
        # 分析问题类型
        if any(kw in question_lower for kw in ['推荐', '哪个', '哪些', '好', '排名']):
            return self._handle_recommendation(question)
        elif any(kw in question_lower for kw in ['分数', '线', '多少分']):
            return self._handle_score_query(question)
        elif any(kw in question_lower for kw in ['评估', '学科', '专业']):
            return self._handle_discipline_query(question)
        elif any(kw in question_lower for kw in ['985', '211', '区别', '是什么']):
            return self._handle_definition(question)
        elif any(kw in question_lower for kw in ['复习', '备考', '政治', '英语']):
            return self._handle_study_guide(question)
        else:
            return self._handle_general(question)
    
    def _handle_recommendation(self, question: str) -> str:
        """处理推荐问题"""
        question_lower = question.lower()
        
        # 提取学科
        subjects = ['计算机', '软件工程', '人工智能', '电子信息', '机械', '材料', '金融', '法律', '医学', '教育']
        found_subject = None
        for subj in subjects:
            if subj in question:
                found_subject = subj
                break
        
        # 提取分数
        import re
        score_match = re.search(r'(\d+)\s*[分]', question)
        score = int(score_match.group(1)) if score_match else None
        
        # 提取地区
        regions = ['北京', '上海', '江苏', '浙江', '广东', '四川', '湖北', '陕西']
        found_region = None
        for region in regions:
            if region in question:
                found_region = region
                break
        
        # 生成推荐
        response = "[INFO] 根据您的问题，为您推荐以下院校：\n\n"
        
        if found_subject:
            response += f"【{found_subject}专业】推荐院校：\n"
            # 使用学科评估数据
            discipline = self.data_loader.get_discipline(found_subject)
            if discipline:
                schools = discipline.get('schools', [])[:5]
                for i, school in enumerate(schools, 1):
                    response += f"   {i}. {school.get('name', '未知')}\n"
            else:
                response += "   清华大学、北京大学、浙江大学、国防科技大学、北京航空航天大学\n"
        
        if score:
            response += f"\n【{score}分左右的院校】推荐：\n"
            response += "   1. 北京邮电大学 - 信息与通信工程\n"
            response += "   2. 西安电子科技大学 - 电子科学与技术\n"
            response += "   3. 南京航空航天大学 - 力学\n"
            response += "   4. 哈尔滨工程大学 - 船舶与海洋工程\n"
        
        if found_region:
            response += f"\n【{found_region}地区】推荐院校：\n"
            for school in list(self.data_loader.schools.values())[:5]:
                if school.get('province') == found_region:
                    response += f"   - {school.get('name')}\n"
        
        if not found_subject and not score and not found_region:
            response += "[STAR] 综合推荐（985院校）：\n"
            for i, school in enumerate(self.data_loader.schools_985[:5], 1):
                response += f"   {i}. {school.get('name', '未知')}\n"
        
        response += "\n[TIP] 建议：具体选择还需结合您的兴趣、职业规划和往年录取情况综合考虑。"
        return response
    
    def _handle_score_query(self, question: str) -> str:
        """处理分数查询"""
        import re
        year_match = re.search(r'(202[2-6])\s*年', question)
        year = int(year_match.group(1)) if year_match else 2026
        
        response = f"[CHART] 【{year}年考研分数线参考】\n\n"
        
        # 国家线
        if 'national' in self.data_loader.score_data:
            national = self.data_loader.score_data['national']
            target_year = str(year) if str(year) in national else '2026'
            scores = national[target_year]
            
            response += f"[NOTE] {target_year}年国家线（学术学位A类）：\n"
            a_scores = scores.get('A类', scores)  # 兼容有无A类的情况
            
            # 只显示主要学科
            main_subjects = ['哲学', '经济学', '法学', '教育学', '文学', '历史学', 
                           '理学', '工学', '农学', '医学', '管理学', '艺术学']
            for subj in main_subjects:
                if subj in a_scores:
                    response += f"   {subj}: {a_scores[subj].get('总分', 'N/A')}分\n"
        
        # 自划线院校
        if 'self_drawn' in self.data_loader.score_data:
            self_drawn = self.data_loader.score_data['self_drawn']
            response += "\n[NOTE] 34所自划线院校（部分）：\n"
            schools = list(self_drawn.keys())[:5]
            for school in schools:
                response += f"   [SCHOOL] {school}\n"
        
        return response
    
    def _handle_discipline_query(self, question: str) -> str:
        """处理学科查询"""
        # 提取学科名
        disciplines = ['计算机科学与技术', '软件工程', '电子科学与技术', '信息与通信工程',
                      '控制科学与工程', '机械工程', '材料科学与工程', '化学工程与技术',
                      '数学', '物理学', '生物学', '临床医学', '药学', '法学', '教育学']
        
        found_discipline = None
        for disc in disciplines:
            if disc in question:
                found_discipline = disc
                break
        
        if not found_discipline:
            # 默认返回计算机
            found_discipline = "计算机科学与技术"
        
        response = f"[BOOK] 【{found_discipline}学科评估结果】\n\n"
        
        discipline_data = self.data_loader.get_discipline(found_discipline)
        if discipline_data and 'schools' in discipline_data:
            schools = discipline_data['schools'][:10]
            response += "[TOP] A类院校：\n"
            for school in schools:
                grade = school.get('grade', 'A')
                name = school.get('name', '未知')
                response += f"   {grade}: {name}\n"
        else:
            # 默认数据
            response += "[TOP] A+：清华大学、北京大学、国防科技大学、浙江大学\n"
            response += "[TOP] A：北京航空航天大学、北京邮电大学、哈尔滨工业大学、上海交通大学\n"
            response += "[TOP] A-：南京大学、华中科技大学、电子科技大学、北京理工大学\n"
        
        response += "\n[TIP] 学科评估结果由教育部学位与研究生教育发展中心发布，是考研择校的重要参考。"
        return response
    
    def _handle_definition(self, question: str) -> str:
        """处理概念解释"""
        question_lower = question.lower()
        
        if '985' in question:
            response = "[BUILD] 【985工程高校】\n\n"
            response += "985工程是中国教育部为了建设一批世界知名的高水平大学而实施的高校建设工程。\n\n"
            response += f"[INFO] 共有 {len(self.data_loader.schools_985)} 所985高校：\n"
            for school in self.data_loader.schools_985[:10]:
                response += f"   - {school.get('name', '未知')}\n"
            response += "\n[TIP] 985高校在科研实力、师资力量、就业前景等方面具有优势，是很多考生的首选。"
        
        elif '211' in question:
            response = "[BUILD] 【211工程高校】\n\n"
            response += "211工程是中国政府为了迎接世界新技术革命的挑战，面向21世纪建设一批重点高校和重点学科。\n\n"
            response += f"[INFO] 共有 {len(self.data_loader.schools_211)} 所211高校（包括985）：\n"
            for school in self.data_loader.schools_211[:10]:
                response += f"   - {school.get('name', '未知')}\n"
            response += "\n[TIP] 211高校数量较多，覆盖面更广，是重要的教育资源。"
        
        else:
            response = "这个问题涉及考研基础知识，建议您访问教育部官网或研招网获取权威信息。"
        
        return response
    
    def _handle_study_guide(self, question: str) -> str:
        """处理复习指导"""
        response = "[BOOK2] 【考研备考建议】\n\n"
        
        if '政治' in question:
            response += "[PLAN] 政治复习规划：\n"
            response += "   - 基础阶段（7-8月）：梳理知识点框架\n"
            response += "   - 强化阶段（9-10月）：重点突破选择题\n"
            response += "   - 冲刺阶段（11-12月）：背诵分析题、时政\n"
            response += "\n[BOOK] 推荐资料：肖秀荣系列、徐涛网课、风中劲草\n"
        
        elif '英语' in question:
            response += "[PLAN] 英语复习规划：\n"
            response += "   - 词汇：坚持每天背诵，使用词根词缀法\n"
            response += "   - 阅读：精读历年真题，掌握出题规律\n"
            response += "   - 作文：总结模板，多写多练\n"
            response += "\n[BOOK] 推荐资料：历年真题、张剑黄皮书、王江涛作文\n"
        
        else:
            response += "[PLAN] 通用复习建议：\n"
            response += "   1. 制定详细计划，合理分配时间\n"
            response += "   2. 重视历年真题，了解出题规律\n"
            response += "   3. 保持良好心态，适度放松\n"
            response += "   4. 定期模拟测试，检验复习效果\n"
        
        return response
    
    def _handle_general(self, question: str) -> str:
        """处理通用问题"""
        # 搜索相关QA
        for qa in self.data_loader.qa_data[:20]:
            instr = qa.get('instruction', '').lower()
            if any(kw in instr for kw in question.lower().split()[:3]):
                return qa.get('output', '')
        
        return ("[ASK] 关于这个问题，我可以为您提供以下帮助：\n\n"
                "   - 院校推荐和排名查询\n"
                "   - 学科评估和分数线\n"
                "   - 考研政策和备考指导\n\n"
                "请详细描述您的问题，或使用上述关键词进行查询。\n"
                "输入 /help 查看所有可用命令。")
