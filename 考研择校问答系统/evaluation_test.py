# -*- coding: utf-8 -*-
"""
考研择校问答系统 - 评测脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("考研择校智能问答系统 - 全面评测报告")
print("=" * 70)

# 1. Test NLP Module
print("\n[1] NLP任务评测")
print("-" * 50)

try:
    from nlp_tasks import NLPProcessor, IntentType
    
    nlp = NLPProcessor()
    
    test_questions = [
        "计算机考研推荐哪些985学校",
        "2024年工学国家线是多少",
        "学硕和专硕有什么区别",
        "清华大学计算机考什么科目",
        "我预估350分能上哪些211",
        "跨专业考研难不难"
    ]
    
    intent_stats = {}
    results = []
    for q in test_questions:
        result = nlp.process(q)
        intent = result.intent.value
        intent_stats[intent] = intent_stats.get(intent, 0) + 1
        print(f"  Q: {q}")
        print(f"    Intent: {intent} ({result.intent_confidence:.2f})")
        print(f"    Keywords: {result.keywords}")
        results.append(result)
    
    print(f"\n  [OK] NLP模块测试通过，共测试 {len(results)} 个问题")
    print(f"  意图分布: {intent_stats}")
except Exception as e:
    print(f"  [FAIL] NLP模块测试失败: {e}")
    import traceback
    traceback.print_exc()

# 2. Test Data Loading
print("\n[2] 数据模块评测")
print("-" * 50)

try:
    from data_loader import DataLoader
    loader = DataLoader()
    loader.load_all()
    
    print(f"  院校数据: {len(loader.schools)} 所")
    print(f"  985高校: {len(loader.schools_985)} 所")
    print(f"  211高校: {len(loader.schools_211)} 所")
    print(f"  问答数据: {len(loader.qa_data)} 条")
    print(f"  [OK] 数据加载成功")
except Exception as e:
    print(f"  [FAIL] 数据加载失败: {e}")

# 3. Test Skills Module
print("\n[3] Skills能力评测")
print("-" * 50)

try:
    from skills import SchoolQuerySkill, SmartRecommendSkill, PolicyExplainSkill
    
    school_skill = SchoolQuerySkill()
    result = school_skill.execute({"school_name": "清华大学"})
    status1 = result.get("status", "ok")
    print(f"  院校查询Skill: {status1}")
    
    recommend_skill = SmartRecommendSkill()
    result = recommend_skill.execute({
        "score": 350,
        "level": "211",
        "major": "计算机"
    })
    status2 = result.get("status", "ok")
    print(f"  智能推荐Skill: {status2}")
    
    policy_skill = PolicyExplainSkill()
    result = policy_skill.execute({"policy_type": "degree_type"})
    status3 = result.get("status", "ok")
    print(f"  政策解读Skill: {status3}")
    
    print(f"  [OK] Skills模块加载成功")
except Exception as e:
    print(f"  [FAIL] Skills模块测试失败: {e}")

# 4. Test Agent Module
print("\n[4] Agent任务调度评测")
print("-" * 50)

try:
    from agent import GradSchoolAgent
    
    agent = GradSchoolAgent()
    print(f"  [OK] Agent模块加载成功")
    print(f"  注册Skills数量: {len(agent.skill_registry.skills)}")
except Exception as e:
    print(f"  [FAIL] Agent模块测试失败: {e}")

# 5. Run Model Evaluator
print("\n[5] 模型评估测试")
print("-" * 50)

try:
    from model_optimizer import ModelEvaluator, SelfImprover
    
    evaluator = ModelEvaluator()
    test_cases = evaluator.load_test_cases()
    
    print(f"  测试用例数量: {len(test_cases)}")
    print(f"  测试类别: {set(tc['category'] for tc in test_cases)}")
    
    # Simulate evaluation
    improver = SelfImprover()
    result = improver.run_full_training_cycle(num_samples=100)
    
    print(f"\n  评估结果:")
    print(f"    生成训练样本: {result['training_data_count']}")
    print(f"    平均得分: {result['evaluation_report']['average_score']:.1f}")
    print(f"    各类别得分:")
    for cat, score in result['evaluation_report']['category_scores'].items():
        print(f"      {cat}: {score:.1f}")
    
    print(f"  [OK] 模型评估完成")
except Exception as e:
    print(f"  [FAIL] 模型评估失败: {e}")
    import traceback
    traceback.print_exc()

# 6. Summary
print("\n" + "=" * 70)
print("评测总结")
print("=" * 70)
print("""
系统包含的核心模块:
  1. NLP处理模块 - 意图识别、关键词抽取、命名实体识别
  2. 数据加载模块 - 院校数据、问答知识库、学科评估
  3. Skills能力模块 - 院校查询、智能推荐、政策解读
  4. Agent调度模块 - 任务规划、Skill调度
  5. 模型评估模块 - 训练数据生成、模型评估

系统支持的NLP任务:
  - 分词 (Word Segmentation)
  - 意图识别 (Intent Recognition)
  - 关键词抽取 (Keyword Extraction)
  - 命名实体识别 (NER)
  - 文本分类 (Text Classification)
""")

print("评测完成!")
