"""
多轮自动化训练脚本
持续优化考研问答系统模型
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List
from model_optimizer import ModelTrainer, ModelEvaluator, SelfImprover


class MultiRoundTrainer:
    """多轮训练器"""
    
    def __init__(self, rounds: int = 5):
        self.rounds = rounds
        self.self_improver = SelfImprover()
        self.all_results = []
        
    def run_training_rounds(self) -> Dict:
        """运行多轮训练"""
        print("=" * 60)
        print("考研问答系统 - 多轮自动化训练")
        print("=" * 60)
        print(f"计划训练轮数: {self.rounds}")
        print("-" * 60)
        
        for round_num in range(1, self.rounds + 1):
            print(f"\n>>> 第 {round_num}/{self.rounds} 轮训练 <<<")
            
            # 每轮增加样本量
            samples = 150 + round_num * 30
            
            # 运行训练
            result = self.self_improver.run_full_training_cycle(num_samples=samples)
            
            # 记录结果
            self.all_results.append({
                'round': round_num,
                'timestamp': datetime.now().isoformat(),
                'samples': result['training_data_count'],
                'avg_score': result['evaluation_report']['average_score'],
                'weak_categories': self._find_weak_categories(
                    result['evaluation_report']['category_scores']
                )
            })
            
            print(f"本轮完成: {result['training_data_count']} 样本, "
                  f"得分: {result['evaluation_report']['average_score']:.1f}")
            
            # 短暂休息
            if round_num < self.rounds:
                time.sleep(0.5)
        
        return self._generate_final_report()
    
    def _find_weak_categories(self, scores: Dict) -> list:
        """找出薄弱类别"""
        return [cat for cat, score in scores.items() if score < 75]
    
    def _generate_final_report(self) -> Dict:
        """生成最终报告"""
        print("\n" + "=" * 60)
        print("多轮训练完成报告")
        print("=" * 60)
        
        total_samples = sum(r['samples'] for r in self.all_results)
        avg_scores = [r['avg_score'] for r in self.all_results]
        
        # 找出进步最大的类别
        print(f"\n总训练样本: {total_samples}")
        print(f"平均得分变化: {avg_scores[0]:.1f} -> {avg_scores[-1]:.1f}")
        
        # 保存最终报告
        report = {
            'total_rounds': self.rounds,
            'total_samples_generated': total_samples,
            'score_progression': avg_scores,
            'score_improvement': avg_scores[-1] - avg_scores[0],
            'round_details': self.all_results,
            'generated_at': datetime.now().isoformat()
        }
        
        os.makedirs('data/training_history', exist_ok=True)
        report_path = f'data/training_history/report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细报告已保存: {report_path}")
        
        # 合并所有训练数据
        self._merge_all_training_data()
        
        return report
    
    def _merge_all_training_data(self):
        """合并所有训练数据"""
        training_dir = 'data/training'
        if not os.path.exists(training_dir):
            return
        
        all_data = []
        for filename in os.listdir(training_dir):
            if filename.endswith('.json') and filename != 'all_training_data.json':
                path = os.path.join(training_dir, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data)
        
        # 保存合并后的数据
        merged_path = os.path.join(training_dir, 'merged_training_data.json')
        with open(merged_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"合并训练数据: {len(all_data)} 条 -> {merged_path}")


class KnowledgeBaseEnhancer:
    """知识库增强器 - 基于训练结果优化知识库"""
    
    def __init__(self):
        self.weak_categories = []
        
    def analyze_and_enhance(self):
        """分析薄弱环节并增强知识库"""
        print("\n[知识库增强分析]")
        
        # 读取训练历史
        try:
            with open('data/improvement/improvement_log.json', 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            print("未找到改进日志")
            return
        
        # 统计薄弱类别
        weak_count = {}
        for log in logs:
            for rec in log.get('recommendations', []):
                if '需要重点优化' in rec or '表现一般' in rec:
                    category = rec.split(':')[0].strip()
                    weak_count[category] = weak_count.get(category, 0) + 1
        
        # 生成增强数据
        enhancements = {
            'school_recommendation': self._generate_school_recommendations(),
            'discipline_evaluation': self._generate_discipline_evaluations(),
            'school_knowledge': self._generate_school_knowledge(),
            'exam_subject': self._generate_exam_subjects(),
        }
        
        # 保存增强数据
        os.makedirs('data/enhancements', exist_ok=True)
        for category, data in enhancements.items():
            path = f'data/enhancements/{category}_enhanced.json'
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"已生成 {len(enhancements)} 个增强模块")
        return enhancements
    
    def _generate_school_recommendations(self) -> list:
        """生成院校推荐增强数据"""
        return [
            {
                'type': 'comprehensive_recommendation',
                'data': {
                    '计算机A类院校推荐': {
                        '顶尖': ['清华大学(370+)', '北京大学(365+)', '浙江大学(360+)'],
                        '强校': ['北京航空航天大学(355+)', '北京邮电大学(350+)', 
                                '哈尔滨工业大学(350+)', '上海交通大学(365+)'],
                        '优质': ['中国科学技术大学(345+)', '南京大学(355+)', 
                                '华中科技大学(350+)', '电子科技大学(340+)'],
                        '性价比': ['西安电子科技大学(330+)', '杭州电子科技大学(300+)',
                                  '重庆邮电大学(290+)', '南京邮电大学(295+)']
                    }
                }
            },
            {
                'type': 'region_based_recommendation',
                'data': {
                    '北京计算机院校': ['清华大学', '北京大学', '北京航空航天大学', 
                                     '北京邮电大学', '北京理工大学', '北京交通大学'],
                    '上海计算机院校': ['上海交通大学', '复旦大学', '同济大学', '华东师范大学'],
                    '江浙计算机院校': ['浙江大学', '南京大学', '东南大学', '杭州电子科技大学'],
                }
            }
        ]
    
    def _generate_discipline_evaluations(self) -> list:
        """生成学科评估增强数据"""
        return [
            {
                'type': 'discipline_rankings',
                'data': {
                    '计算机科学与技术': {
                        'A+': ['清华大学', '北京大学', '浙江大学', '国防科技大学'],
                        'A': ['北京航空航天大学', '北京邮电大学', '哈尔滨工业大学', 
                             '上海交通大学', '南京大学', '华中科技大学', '电子科技大学'],
                    },
                    '软件工程': {
                        'A+': ['北京航空航天大学', '浙江大学'],
                        'A': ['北京大学', '清华大学', '华东师范大学', '南京大学', '武汉大学'],
                    },
                    '电子科学与技术': {
                        'A+': ['电子科技大学', '西安电子科技大学'],
                        'A': ['北京大学', '清华大学', '北京邮电大学', '复旦大学', 
                             '南京大学', '东南大学'],
                    }
                }
            }
        ]
    
    def _generate_school_knowledge(self) -> list:
        """生成院校知识增强数据"""
        return [
            {
                'type': 'school_features',
                'data': {
                    '清华大学': '顶尖工科院校，计算机A+，分数线高，招生严格',
                    '北京大学': '文理顶尖，计算机A+，地理位置优越',
                    '浙江大学': '综合实力强，计算机A+，录取人数多',
                    '北京航空航天大学': '工科强校，计算机A+，计算机体系结构方向很强',
                    '北京邮电大学': '计算机A，通信与计算机特色鲜明，就业好',
                    '电子科技大学': '电子信息强校，计算机A+，网络安全方向突出',
                    '西安电子科技大学': '电子信息强校，计算机A+，人工智能方向强',
                    '哈尔滨工业大学': '工科老牌强校，计算机A，航天方向突出',
                    '华中科技大学': '工科强校，计算机A，光电方向突出',
                    '杭州电子科技大学': '性价比高，计算机B+，电子信息特色',
                }
            }
        ]
    
    def _generate_exam_subjects(self) -> list:
        """生成考试科目增强数据"""
        return [
            {
                'type': 'exam_subject_comparison',
                'data': {
                    '计算机学硕': {
                        '科目': '政治、英语一、数学一、408计算机学科专业基础',
                        '难度': '高',
                        '特点': '内容多、难度大、分数线相对低'
                    },
                    '计算机专硕': {
                        '科目': '政治、英语二、数学二、408或自命题',
                        '难度': '中高',
                        '特点': '内容相对少、竞争激烈'
                    },
                    '法律硕士(非法学)': {
                        '科目': '政治、英语一、专业课（法学基础+法学综合）',
                        '难度': '中',
                        '特点': '不考数学，跨考友好'
                    },
                    '金融硕士': {
                        '科目': '政治、英语二、经济类联考/数学三、专业课',
                        '难度': '高',
                        '特点': '热门专业，竞争激烈'
                    }
                }
            }
        ]


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  考研问答系统 - 多轮自动化训练")
    print("=" * 60)
    
    # 运行多轮训练
    trainer = MultiRoundTrainer(rounds=5)
    report = trainer.run_training_rounds()
    
    # 增强知识库
    enhancer = KnowledgeBaseEnhancer()
    enhancements = enhancer.analyze_and_enhance()
    
    print("\n" + "=" * 60)
    print("  所有训练任务完成!")
    print("=" * 60)
    print(f"\n最终成果:")
    print(f"  - 训练样本总数: {report['total_samples_generated']}")
    print(f"  - 得分提升: {report['score_progression'][0]:.1f} -> {report['score_progression'][-1]:.1f}")
    print(f"  - 增强模块: {len(enhancements) if enhancements else 0} 个")
