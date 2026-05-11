"""
考研数据爬虫综合管理器
统一调度所有爬虫模块
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime

# 导入各爬虫模块
from chsi_crawler import ChsiCrawler
from discipline_crawler import DisciplineCrawler
from ranking_crawler import RankingCrawler
from score_line_crawler import ScoreLineCrawler


class CrawlerManager:
    """爬虫综合管理器"""
    
    def __init__(self):
        self.chsi = ChsiCrawler()
        self.discipline = DisciplineCrawler()
        self.ranking = RankingCrawler()
        self.score_line = ScoreLineCrawler()
        
        # 数据缓存
        self._cache = {}
    
    def search_schools(self, keyword: str = "") -> List[Dict]:
        """搜索院校"""
        return self.chsi.search_schools(keyword)
    
    def get_school_info(self, school_name: str) -> Dict:
        """获取院校详细信息"""
        # 获取基本信息
        basic_info = self.chsi.get_school_details(school_name)
        
        # 获取学科评估
        disciplines = self.discipline.get_school_discipline_rank(school_name)
        
        # 获取排名
        rankings = self.ranking.get_rankings()
        school_rank = None
        for r in rankings:
            if school_name in r['学校']:
                school_rank = r
                break
        
        # 获取分数线
        scores = self.score_line.get_school_score_lines(school_name)
        
        return {
            '基本信息': basic_info,
            '学科评估': disciplines[:10] if disciplines else [],
            '综合排名': school_rank,
            '分数线': scores,
            '更新时间': datetime.now().strftime('%Y-%m-%d')
        }
    
    def get_discipline_evaluation(self, discipline: str) -> Dict:
        """获取学科评估数据"""
        results = self.discipline.get_evaluation_results(discipline)
        
        # 按等级分组
        by_grade = {}
        for item in results:
            grade = item['等级']
            if grade not in by_grade:
                by_grade[grade] = []
            by_grade[grade].append(item['学校'])
        
        return {
            '学科': discipline,
            '评估结果': by_grade,
            '数据来源': '教育部第四轮学科评估（2016年）'
        }
    
    def get_score_lines(self, year: int = 2024, major: str = "") -> Dict:
        """获取分数线"""
        if major:
            return self.score_line.compare_score_lines(major, year)
        return self.score_line.get_national_score_line(year)
    
    def get_major_info(self, major_keyword: str) -> Dict:
        """获取专业详细信息"""
        # 搜索专业
        majors = self.chsi.search_majors(major_keyword)
        
        # 获取相关学科评估
        eval_data = self.discipline.get_evaluation_results(major_keyword)
        
        # 获取相关分数线
        score_data = self.score_line.get_subject_score_line(major_keyword)
        
        return {
            '专业列表': majors,
            '学科评估': eval_data[:20] if eval_data else [],
            '院校分数线': score_data,
            '数据来源': ['研招网', '学科评估中心', '各校研究生院']
        }
    
    def compare_schools(self, school1: str, school2: str) -> Dict:
        """对比两所学校"""
        info1 = self.get_school_info(school1)
        info2 = self.get_school_info(school2)
        
        return {
            '学校1': {
                '名称': school1,
                '基本信息': info1['基本信息'],
                '学科评估': info1['学科评估'][:5],
                '综合排名': info1['综合排名'],
                '分数线': info1['分数线']
            },
            '学校2': {
                '名称': school2,
                '基本信息': info2['基本信息'],
                '学科评估': info2['学科评估'][:5],
                '综合排名': info2['综合排名'],
                '分数线': info2['分数线']
            },
            '对比维度': ['学校层次', '学科实力', '录取难度', '地理位置', '就业前景']
        }
    
    def get_recommendations(self, user_profile: Dict) -> List[Dict]:
        """根据用户画像推荐院校"""
        recommendations = []
        
        target_major = user_profile.get('target_major', '')
        score_level = user_profile.get('score_level', '')
        location = user_profile.get('location', '')
        
        # 获取该专业的学科评估
        eval_data = self.discipline.get_evaluation_results(target_major)
        
        # 根据分数水平推荐
        if score_level == 'high':
            # 高分段：推荐A+、A档
            recommendations.extend(self._filter_by_grade(eval_data, ['A+', 'A']))
        elif score_level == 'medium':
            # 中分段：推荐A-、B+档
            recommendations.extend(self._filter_by_grade(eval_data, ['A-', 'B+']))
        else:
            # 低分段：推荐B、B+档
            recommendations.extend(self._filter_by_grade(eval_data, ['B+', 'B']))
        
        # 根据地区筛选
        if location:
            recommendations = [r for r in recommendations if r.get('学校') and location in r.get('学校', '')]
        
        return recommendations[:10]
    
    def _filter_by_grade(self, eval_data: List, grades: List) -> List:
        """根据等级筛选"""
        return [item for item in eval_data if item.get('等级') in grades]
    
    def export_all_data(self, output_dir: str = "../data") -> Dict:
        """导出所有数据到文件"""
        export_results = {}
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. 导出985高校数据
        schools_985_path = os.path.join(output_dir, "schools_985.json")
        with open(schools_985_path, 'w', encoding='utf-8') as f:
            json.dump(self.ranking.get_985_universities(), f, ensure_ascii=False, indent=2)
        export_results['985高校'] = schools_985_path
        
        # 2. 导出211高校数据
        schools_211_path = os.path.join(output_dir, "schools_211.json")
        with open(schools_211_path, 'w', encoding='utf-8') as f:
            json.dump(self.ranking.get_211_universities(), f, ensure_ascii=False, indent=2)
        export_results['211高校'] = schools_211_path
        
        # 3. 导出大学排名数据
        rankings_path = os.path.join(output_dir, "university_rankings.json")
        rankings = {
            '综合排名': self.ranking.get_rankings('综合排名'),
            '工科排名': self.ranking.get_rankings('工科排名'),
            '计算机排名': self.ranking.get_rankings('计算机排名'),
            '师范排名': self.ranking.get_rankings('师范排名'),
            '财经排名': self.ranking.get_rankings('财经排名'),
        }
        with open(rankings_path, 'w', encoding='utf-8') as f:
            json.dump(rankings, f, ensure_ascii=False, indent=2)
        export_results['大学排名'] = rankings_path
        
        # 4. 导出学科评估数据
        discipline_path = os.path.join(output_dir, "discipline_full.json")
        discipline_full = self.discipline.get_evaluation_results()
        with open(discipline_path, 'w', encoding='utf-8') as f:
            json.dump(discipline_full, f, ensure_ascii=False, indent=2)
        export_results['学科评估'] = discipline_path
        
        # 5. 导出国分数线数据
        scores_path = os.path.join(output_dir, "national_scores.json")
        national_scores = {
            '2024': self.score_line.get_national_score_line(2024),
            '2023': self.score_line.get_national_score_line(2023),
            '2022': self.score_line.get_national_score_line(2022),
        }
        with open(scores_path, 'w', encoding='utf-8') as f:
            json.dump(national_scores, f, ensure_ascii=False, indent=2)
        export_results['国家线'] = scores_path
        
        # 6. 导出自主划线数据
        self_drawn_path = os.path.join(output_dir, "self_drawn_scores.json")
        with open(self_drawn_path, 'w', encoding='utf-8') as f:
            json.dump(self.score_line.get_self_drawn_schools(), f, ensure_ascii=False, indent=2)
        export_results['自主划线'] = self_drawn_path
        
        return export_results
    
    def query(self, query_type: str, **kwargs) -> Dict:
        """统一查询接口"""
        query_map = {
            'school': self.get_school_info,
            'schools': lambda: self.search_schools(kwargs.get('keyword', '')),
            'discipline': lambda: self.get_discipline_evaluation(kwargs.get('discipline', '')),
            'score': lambda: self.get_score_lines(kwargs.get('year', 2024), kwargs.get('major', '')),
            'major': lambda: self.get_major_info(kwargs.get('major', '')),
            'compare': lambda: self.compare_schools(kwargs.get('school1', ''), kwargs.get('school2', '')),
            'recommend': lambda: self.get_recommendations(kwargs.get('profile', {})),
        }
        
        if query_type in query_map:
            return query_map[query_type]()
        
        return {'error': f'未知的查询类型: {query_type}'}


# 测试
if __name__ == "__main__":
    manager = CrawlerManager()
    
    print("=== 考研数据爬虫管理系统测试 ===\n")
    
    # 1. 测试院校搜索
    schools = manager.search_schools("计算机")
    print(f"院校搜索结果: {len(schools)}所")
    
    # 2. 测试院校信息查询
    info = manager.get_school_info("清华大学")
    print(f"\n清华大学信息:")
    print(f"  - 基本信息: {info['基本信息']['name'] if 'name' in info['基本信息'] else info['基本信息'].get('名称', 'N/A')}")
    print(f"  - 学科评估: {len(info['学科评估'])}个学科")
    
    # 3. 测试学科评估
    cs_eval = manager.get_discipline_evaluation("计算机")
    print(f"\n计算机学科评估:")
    for grade, schools_list in list(cs_eval['评估结果'].items())[:3]:
        print(f"  {grade}: {', '.join(schools_list[:3])}...")
    
    # 4. 测试分数线
    scores = manager.get_score_lines(2024)
    print(f"\n2024年国家线(A类)部分:")
    for category in ['工学', '理学', '经济学']:
        if category in scores['A类']:
            print(f"  {category}: {scores['A类'][category]['总分']}分")
    
    # 5. 导出数据
    print("\n正在导出数据...")
    results = manager.export_all_data()
    print("数据导出完成:")
    for name, path in results.items():
        print(f"  - {name}: {path}")
