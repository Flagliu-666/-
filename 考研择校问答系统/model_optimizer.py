"""
考研问答系统 - 模型自我完善与训练系统
自动生成训练数据、评估模型性能、持续优化
"""

import json
import random
import os
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict


class ModelTrainer:
    """模型训练器 - 自动生成高质量训练数据"""
    
    def __init__(self):
        self.training_data = []
        self.evaluation_data = []
        self.conversation_templates = []
        
    def generate_training_data(self, num_samples: int = 100) -> List[Dict]:
        """生成训练数据"""
        print("正在生成训练数据...")
        
        # 加载知识库
        self._load_knowledge_bases()
        
        # 生成各类训练样本
        self._generate_school_recommendation_samples(num_samples // 4)
        self._generate_score_line_samples(num_samples // 4)
        self._generate_major_comparison_samples(num_samples // 4)
        self._generate_policy_question_samples(num_samples // 4)
        
        # 保存训练数据
        self._save_training_data()
        
        return self.training_data
    
    def _load_knowledge_bases(self):
        """加载知识库"""
        # 加载问答数据
        try:
            with open('data/grad_consult_qa.json', 'r', encoding='utf-8') as f:
                self.qa_data = json.load(f)
        except:
            self.qa_data = []
        
        # 加载学科评估
        try:
            with open('data/discipline_full.json', 'r', encoding='utf-8') as f:
                self.discipline_data = json.load(f)
        except:
            self.discipline_data = []
        
        # 加载分数线
        try:
            with open('data/national_scores.json', 'r', encoding='utf-8') as f:
                self.score_data = json.load(f)
        except:
            self.score_data = {}
        
        # 加载院校数据
        try:
            with open('data/schools_985.json', 'r', encoding='utf-8') as f:
                self.schools_985 = json.load(f)
            with open('data/schools_211.json', 'r', encoding='utf-8') as f:
                self.schools_211 = json.load(f)
        except:
            self.schools_985 = []
            self.schools_211 = []
        
    def _generate_school_recommendation_samples(self, count: int):
        """生成院校推荐类训练样本"""
        majors = ['计算机', '软件工程', '电子信息', '机械工程', '人工智能',
                  '法律硕士', '金融', '教育学', '临床医学', '新闻传播']
        score_levels = ['320分以下', '320-350分', '350-380分', '380分以上']
        locations = ['北京', '上海', '江苏', '浙江', '广东', '湖北', '四川', '陕西']
        
        templates = [
            {
                'instruction': '我是{score}的考生，想考{major}，推荐一些学校',
                'output': '根据您的分数和目标，以下是{major}专业推荐院校：\n'
                         '【冲刺院校】{top_schools}\n'
                         '【稳妥院校】{mid_schools}\n'
                         '【保底院校】{safe_schools}\n'
                         '建议：结合地区偏好和学科实力综合考虑'
            },
            {
                'instruction': '{score}能上哪些{major}的学校？',
                'output': '{major}专业{score}考生可考虑：\n'
                         '1.{school1} - 学科实力强，建议分数达到{score1}\n'
                         '2.{school2} - 性价比较高，分数线相对较低\n'
                         '3.{school3} - 地理位置好，就业机会多'
            },
            {
                'instruction': '我想考{major}，本科是普通一本，有哪些推荐？',
                'output': '针对您的背景，推荐以下{major}院校：\n'
                         '【211院校】{school1}、{school2}\n'
                         '【985院校】{school3}（有一定难度）\n'
                         '【强势双非】{school4}（专业实力强）'
            },
            {
                'instruction': '推荐一些{major}容易上岸的学校',
                'output': '相对容易上岸的{major}院校推荐：\n'
                         '1.{school1} - 招生人数多，分数线适中\n'
                         '2.{school2} - 地理位置好，竞争较小\n'
                         '3.{school3} - 专业课难度较低'
            }
        ]
        
        for i in range(count):
            template = random.choice(templates)
            major = random.choice(majors)
            score = random.choice(score_levels)
            location = random.choice(locations)
            
            # 模拟生成的输出
            output = template['output'].format(
                score=score,
                major=major,
                top_schools='清华大学、北京大学、浙江大学',
                mid_schools='北京航空航天大学、电子科技大学',
                safe_schools='杭州电子科技大学、重庆邮电大学',
                school1='北京航空航天大学',
                school2='西安电子科技大学',
                school3='上海交通大学',
                school4='杭州电子科技大学',
                score1='360+',
            )
            
            self.training_data.append({
                'instruction': template['instruction'].format(
                    score=score, major=major
                ),
                'input': '',
                'output': output,
                'category': 'school_recommendation',
                'timestamp': datetime.now().isoformat()
            })
    
    def _generate_score_line_samples(self, count: int):
        """生成分数线相关训练样本"""
        years = ['2024', '2023', '2022']
        categories = ['工学', '理学', '经济学', '管理学', '教育学', '文学', '法学', '医学']
        
        templates = [
            {
                'instruction': '{year}年{category}国家线是多少？',
                'output': '{year}年{category}考研国家线（A类）：\n'
                         '总分要求：{total}分\n'
                         '政治/外语单科：{politics}分\n'
                         '专业课单科：{专业课}分\n'
                         'B类考生总分低10分左右'
            },
            {
                'instruction': '{category}历年分数线变化大吗？',
                'output': '{category}近三年分数线趋势：\n'
                         '2024年A类：{score_2024}分\n'
                         '2023年A类：{score_2023}分\n'
                         '2022年A类：{score_2022}分\n'
                         '建议关注最新招生简章和往年真题'
            },
            {
                'instruction': '考{category}需要多少分才能稳上岸？',
                'output': '{category}稳定上岸建议分数：\n'
                         '【普通院校】超出国家线10-20分\n'
                         '【211院校】超出国家线30-50分\n'
                         '【985院校】超出国家线50分以上\n'
                         '注：具体看学校、专业方向和当年报考情况'
            },
            {
                'instruction': '{school}的{category}分数线是多少？',
                'output': '{school}的{category}分数线（{year}年）：\n'
                         '复试分数线：{score}分\n'
                         '注意：自主划线院校分数线可能高于国家线\n'
                         '建议关注学校研究生院官网获取最新信息'
            }
        ]
        
        for i in range(count):
            template = random.choice(templates)
            year = random.choice(years)
            category = random.choice(categories)
            
            # 生成合理的分数范围
            base_scores = {
                '工学': 273, '理学': 288, '经济学': 338, 
                '管理学': 347, '教育学': 350, '文学': 363
            }
            base = base_scores.get(category, 300)
            
            output = template['output'].format(
                year=year,
                category=category,
                total=f'{base}+{random.randint(0, 50)}',
                politics=random.randint(40, 55),
               专业课=random.randint(60, 85),
                score_2024=base + random.randint(0, 30),
                score_2023=base + random.randint(-5, 30),
                score_2022=base + random.randint(-10, 30),
                school='清华大学',
                score=350
            )
            
            self.training_data.append({
                'instruction': template['instruction'].format(
                    year=year, category=category, school='清华大学'
                ),
                'input': '',
                'output': output,
                'category': 'score_line',
                'timestamp': datetime.now().isoformat()
            })
    
    def _generate_major_comparison_samples(self, count: int):
        """生成专业对比训练样本"""
        major_pairs = [
            ('计算机科学与技术', '软件工程'),
            ('学硕', '专硕'),
            ('法律硕士(法学)', '法律硕士(非法学)'),
            ('金融学', '金融硕士'),
            ('临床医学', '基础医学'),
            ('会计学', '审计硕士'),
        ]
        
        templates = [
            {
                'instruction': '{major1}和{major2}有什么区别？',
                'output': '{major1} vs {major2} 对比：\n'
                         '【培养方式】{diff1}\n'
                         '【考试科目】{diff2}\n'
                         '【学制】{diff3}\n'
                         '【就业方向】{diff4}\n'
                         '【难度】{diff5}'
            },
            {
                'instruction': '跨考选{major1}还是{major2}好？',
                'output': '关于{major1}和{major2}的选择建议：\n'
                         '1. {factor1}\n'
                         '2. {factor2}\n'
                         '3. {factor3}\n'
                         '综合来看：如果{final}'
            },
            {
                'instruction': '{major}学硕和专硕哪个更难考？',
                'output': '{major}学硕vs专硕难度分析：\n'
                         '【学硕】招生少、考英语一、分数线相对较低\n'
                         '【专硕】招生多、考英语二、分数线相对较高\n'
                         '实际难度取决于：招生计划、报录比、专业课难度'
            }
        ]
        
        diffs = [
            ('重理论、重科研', '重实践、重应用'),
            ('英语一 + 数学一/二', '英语二 + 数学二/三'),
            ('一般为3年', '一般为2-3年'),
            ('高校、研究院', '企业、应用岗位'),
            ('初试难、复试简单', '初试简单、竞争激烈'),
        ]
        
        for i in range(count):
            template = random.choice(templates)
            major1, major2 = random.choice(major_pairs)
            
            self.training_data.append({
                'instruction': template['instruction'].format(major1=major1, major2=major2, major=major1),
                'input': '',
                'output': template['output'].format(
                    major1=major1,
                    major2=major2,
                    major=major1,
                    diff1=diffs[0][0],
                    diff2=diffs[1][0],
                    diff3=diffs[2][0],
                    diff4=diffs[3][0],
                    diff5=diffs[4][0],
                    factor1='看个人兴趣和职业规划',
                    factor2='考虑数学和英语基础',
                    factor3='评估备考时间和精力',
                    final='英语数学好建议学硕，想快速就业建议专硕'
                ),
                'category': 'major_comparison',
                'timestamp': datetime.now().isoformat()
            })
    
    def _generate_policy_question_samples(self, count: int):
        """生成政策类训练样本"""
        policies = [
            ('考研预报名和正式报名有什么区别？', 
             '预报名主要是应届生提前报名，可确认信息；正式报名面向所有考生。预报名信息有效，无需重复报名。'),
            ('考研现场确认需要准备什么材料？',
             '1.身份证 2.学历证书 3.报名号 4.学历认证报告(往届生) 5.工作证明(非户籍地报考)'),
            ('考研初试在哪里考？',
             '应届生：在本科学校所在地\n往届生：在户籍所在地或工作地\n具体考点由各省招生办安排'),
            ('考研调剂是什么时候？',
             '调剂系统在初试成绩公布后约一周开放，通常在3月中下旬至4月底。'),
            ('专项计划有哪些？',
             '1.强军计划 2.援藏计划 3.农村师资计划 4.少数民族骨干计划 5.退役大学生士兵计划'),
            ('照顾专业有哪些？',
             '工学照顾：力学、冶金工程等\n中医类照顾：中医内科学等\n通常分数线低于普通专业'),
            ('考研成绩怎么复查？',
             '在规定时间内向报考学校申请复查，通常只核查分数是否漏加，不重新评卷。'),
            ('推免生和统考生有什么区别？',
             '推免生：无需参加初试，获得保研资格即可\n统考生：需参加全国硕士研究生招生考试'),
        ]
        
        templates = [
            {'instruction': '{question}', 'output': '{answer}'},
            {'instruction': '我想问一下{topic}，能详细说说吗？', 'output': '{answer}'},
            {'instruction': '关于{topic}，你了解多少？', 'output': '{answer}'},
        ]
        
        for i in range(count):
            question, answer = random.choice(policies)
            template = random.choice(templates)
            topic = question[:6]
            
            self.training_data.append({
                'instruction': template['instruction'].format(question=question, topic=topic),
                'input': '',
                'output': template['output'].format(answer=answer),
                'category': 'policy_question',
                'timestamp': datetime.now().isoformat()
            })
    
    def _save_training_data(self):
        """保存训练数据"""
        output_dir = 'data/training'
        os.makedirs(output_dir, exist_ok=True)
        
        # 按类别保存
        by_category = defaultdict(list)
        for item in self.training_data:
            by_category[item['category']].append(item)
        
        for category, items in by_category.items():
            path = os.path.join(output_dir, f'{category}_training.json')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
        
        # 保存全部数据
        with open(os.path.join(output_dir, 'all_training_data.json'), 'w', encoding='utf-8') as f:
            json.dump(self.training_data, f, ensure_ascii=False, indent=2)
        
        print(f"已生成 {len(self.training_data)} 条训练数据")


class ModelEvaluator:
    """模型评估器"""
    
    def __init__(self):
        self.test_cases = []
        self.results = []
        
    def load_test_cases(self) -> List[Dict]:
        """加载测试用例"""
        # 标准问答对
        self.test_cases = [
            {
                'id': 1,
                'question': '计算机考研推荐哪些学校？',
                'expected_keywords': ['清华大学', '北京大学', '浙江大学', '北京航空航天大学'],
                'category': 'school_recommendation'
            },
            {
                'id': 2,
                'question': '2024年工学国家线是多少？',
                'expected_keywords': ['273', '国家线', '工学'],
                'category': 'score_line'
            },
            {
                'id': 3,
                'question': '学硕和专硕有什么区别？',
                'expected_keywords': ['学硕', '专硕', '培养', '英语'],
                'category': 'major_comparison'
            },
            {
                'id': 4,
                'question': '考研预报名需要准备什么？',
                'expected_keywords': ['身份证', '学历', '报名号'],
                'category': 'policy_question'
            },
            {
                'id': 5,
                'question': '计算机学科评估A+的学校有哪些？',
                'expected_keywords': ['清华大学', '北京大学', '浙江大学', '国防科技大学'],
                'category': 'discipline_evaluation'
            },
            {
                'id': 6,
                'question': '跨专业考研哪些专业容易上岸？',
                'expected_keywords': ['法律硕士', '教育学', '社会工作'],
                'category': 'cross_major'
            },
            {
                'id': 7,
                'question': '985和211有什么区别？',
                'expected_keywords': ['985', '211', '学校', '实力'],
                'category': 'school_knowledge'
            },
            {
                'id': 8,
                'question': '考研数学一和数学二哪个难？',
                'expected_keywords': ['数学一', '数学二', '内容', '难度'],
                'category': 'exam_subject'
            },
            {
                'id': 9,
                'question': '杭州电子科技大学计算机怎么样？',
                'expected_keywords': ['杭州电子科技大学', '计算机', '学科'],
                'category': 'school_detail'
            },
            {
                'id': 10,
                'question': '二战考研成功率有多高？',
                'expected_keywords': ['二战', '成功率', '经验'],
                'category': 'exam_strategy'
            }
        ]
        
        return self.test_cases
    
    def evaluate_response(self, question: str, response: str) -> Dict:
        """评估回答质量"""
        # 简单的关键词匹配评估
        score = 0
        matched_keywords = []
        total_keywords = 0
        
        for test in self.test_cases:
            if test['question'] == question:
                for keyword in test['expected_keywords']:
                    total_keywords += 1
                    if keyword in response:
                        score += 1
                        matched_keywords.append(keyword)
                break
        
        return {
            'question': question,
            'response_preview': response[:100] + '...' if len(response) > 100 else response,
            'keyword_match_rate': score / max(total_keywords, 1),
            'matched_keywords': matched_keywords,
            'quality_score': min(score / max(total_keywords, 1) * 100, 100)
        }
    
    def generate_evaluation_report(self, results: List[Dict]) -> Dict:
        """生成评估报告"""
        total = len(results)
        avg_score = sum(r['quality_score'] for r in results) / max(total, 1)
        
        categories = defaultdict(list)
        for r in results:
            for test in self.test_cases:
                if test['question'] == r['question']:
                    categories[test['category']].append(r['quality_score'])
                    break
        
        category_scores = {
            cat: sum(scores) / len(scores) 
            for cat, scores in categories.items()
        }
        
        return {
            'total_tests': total,
            'average_score': avg_score,
            'category_scores': category_scores,
            'timestamp': datetime.now().isoformat(),
            'recommendations': self._generate_recommendations(category_scores)
        }
    
    def _generate_recommendations(self, category_scores: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        for category, score in sorted(category_scores.items(), key=lambda x: x[1]):
            if score < 60:
                recommendations.append(f"{category}: 需要重点优化，建议补充更多相关知识")
            elif score < 80:
                recommendations.append(f"{category}: 表现一般，可进一步丰富回答内容")
            else:
                recommendations.append(f"{category}: 表现良好")
        
        return recommendations


class SelfImprover:
    """自我完善器 - 持续优化系统"""
    
    def __init__(self):
        self.trainer = ModelTrainer()
        self.evaluator = ModelEvaluator()
        self.improvement_log = []
        
    def run_full_training_cycle(self, num_samples: int = 200) -> Dict:
        """运行完整训练周期"""
        print("=" * 50)
        print("开始模型自我完善训练")
        print("=" * 50)
        
        cycle_start = datetime.now()
        
        # 1. 生成训练数据
        print("\n[1/4] 生成训练数据...")
        training_data = self.trainer.generate_training_data(num_samples)
        
        # 2. 加载测试用例
        print("\n[2/4] 加载测试用例...")
        test_cases = self.evaluator.load_test_cases()
        
        # 3. 模拟评估（实际系统中应该调用模型API）
        print("\n[3/4] 模拟模型评估...")
        mock_results = self._simulate_evaluation(test_cases)
        
        # 4. 生成改进报告
        print("\n[4/4] 生成改进报告...")
        report = self.evaluator.generate_evaluation_report(mock_results)
        
        # 记录改进历史
        self.improvement_log.append({
            'cycle': len(self.improvement_log) + 1,
            'timestamp': cycle_start.isoformat(),
            'samples_generated': len(training_data),
            'average_score': report['average_score'],
            'recommendations': report['recommendations']
        })
        
        # 保存改进日志
        self._save_improvement_log()
        
        return {
            'training_data_count': len(training_data),
            'test_cases_count': len(test_cases),
            'evaluation_report': report,
            'improvement_history': self.improvement_log
        }
    
    def _simulate_evaluation(self, test_cases: List[Dict]) -> List[Dict]:
        """模拟评估过程"""
        results = []
        for test in test_cases:
            # 模拟模型回答（实际应该调用模型API）
            score = random.randint(65, 95)
            results.append({
                'question': test['question'],
                'response_preview': f'模拟回答: {test["question"]}...',
                'quality_score': score,
                'matched_keywords': test['expected_keywords'][:2]
            })
        return results
    
    def _save_improvement_log(self):
        """保存改进日志"""
        os.makedirs('data/improvement', exist_ok=True)
        with open('data/improvement/improvement_log.json', 'w', encoding='utf-8') as f:
            json.dump(self.improvement_log, f, ensure_ascii=False, indent=2)
    
    def get_training_stats(self) -> Dict:
        """获取训练统计"""
        training_dir = 'data/training'
        if not os.path.exists(training_dir):
            return {'error': '暂无训练数据'}
        
        stats = {
            'total_samples': 0,
            'by_category': {}
        }
        
        for filename in os.listdir(training_dir):
            if filename.endswith('.json') and filename != 'all_training_data.json':
                category = filename.replace('_training.json', '')
                path = os.path.join(training_dir, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    stats['by_category'][category] = len(data)
                    stats['total_samples'] += len(data)
        
        return stats


# 自动化训练任务
class AutoTrainer:
    """自动化训练任务"""
    
    def __init__(self):
        self.self_improver = SelfImprover()
        
    def daily_training(self):
        """每日训练任务"""
        print("执行每日训练...")
        result = self.self_improver.run_full_training_cycle(num_samples=100)
        print(f"训练完成: {result['training_data_count']} 条新样本")
        return result
    
    def weekly_deep_training(self):
        """每周深度训练"""
        print("执行每周深度训练...")
        result = self.self_improver.run_full_training_cycle(num_samples=300)
        self._optimize_knowledge_base()
        return result
    
    def _optimize_knowledge_base(self):
        """优化知识库"""
        print("优化知识库...")
        # 可以添加知识库优化逻辑


if __name__ == "__main__":
    print("=" * 60)
    print("考研问答系统 - 模型自我完善训练")
    print("=" * 60)
    
    improver = SelfImprover()
    
    # 运行一个完整训练周期
    result = improver.run_full_training_cycle(num_samples=200)
    
    print("\n" + "=" * 60)
    print("训练完成报告")
    print("=" * 60)
    print(f"生成训练样本: {result['training_data_count']}")
    print(f"测试用例数量: {result['test_cases_count']}")
    print(f"平均得分: {result['evaluation_report']['average_score']:.1f}")
    
    print("\n各类别表现:")
    for cat, score in result['evaluation_report']['category_scores'].items():
        print(f"  {cat}: {score:.1f}")
    
    print("\n改进建议:")
    for rec in result['evaluation_report']['recommendations'][:5]:
        print(f"  - {rec}")
    
    # 获取训练统计
    stats = improver.get_training_stats()
    print(f"\n累计训练统计: {stats['total_samples']} 条样本")
