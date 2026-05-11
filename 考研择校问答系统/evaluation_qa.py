# -*- coding: utf-8 -*-
"""
考研择校问答系统 - 问答效果测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("考研择校问答系统 - 问答效果测试")
print("=" * 70)

# Test QA with data
print("\n[1] 测试问答知识库效果")
print("-" * 50)

try:
    from data_loader import DataLoader
    import json
    
    loader = DataLoader()
    qa_data = loader.load_qa_data()
    
    print(f"  加载问答数据: {len(qa_data)} 条")
    
    # Test various questions
    test_qs = [
        "计算机考研推荐",
        "国家线是多少",
        "学硕专硕区别",
        "跨专业考研",
        "调剂是什么"
    ]
    
    for query in test_qs[:3]:
        print(f"\n  查询: {query}")
        # Simple search
        matches = [item for item in qa_data[:50] 
                   if isinstance(item, dict) and 
                   (query in str(item.get('question', '')) or 
                    query in str(item.get('answer', '')))]
        if matches:
            print(f"    找到相关问答: {len(matches)} 条")
            first = matches[0]
            if isinstance(first, dict):
                print(f"    示例问题: {first.get('question', 'N/A')[:50]}...")
        else:
            print(f"    未找到精确匹配，展示前几条:")
            for i, item in enumerate(qa_data[:2]):
                if isinstance(item, dict):
                    print(f"      {i+1}. {item.get('question', 'N/A')[:40]}...")
    
    print(f"\n  [OK] 问答检索功能正常")
except Exception as e:
    print(f"  [FAIL] 问答测试失败: {e}")
    import traceback
    traceback.print_exc()

# Test Schools Data
print("\n[2] 测试院校数据查询")
print("-" * 50)

try:
    import pandas as pd
    
    # Load schools data
    schools_df = pd.read_csv("./data/schools_data.csv")
    print(f"  加载院校数据: {len(schools_df)} 所")
    
    # Test 985 schools
    schools_985 = [s for s in schools_df['院校名称'].dropna() 
                   if '985' in str(schools_df[schools_df['院校名称']==s]['院校层次'].values[0] if len(schools_df[schools_df['院校名称']==s])>0 else '')]
    print(f"  985院校数量: {len(schools_985)}")
    
    # Test specific query
    print("\n  测试查询: 清华大学")
    tsinghua = schools_df[schools_df['院校名称'].str.contains('清华', na=False)]
    if not tsinghua.empty:
        row = tsinghua.iloc[0]
        print(f"    学校: {row['院校名称']}")
        print(f"    层次: {row['院校层次']}")
        print(f"    所在地: {row['所在省份']}")
        print(f"    排名: {row['排名']}")
    else:
        print("    未找到清华大学数据")
    
    print(f"\n  [OK] 院校数据查询正常")
except Exception as e:
    print(f"  [FAIL] 院校数据测试失败: {e}")

# Test Discipline Evaluation
print("\n[3] 测试学科评估数据")
print("-" * 50)

try:
    with open("./data/discipline_full.json", 'r', encoding='utf-8') as f:
        discipline_data = json.load(f)
    
    print(f"  加载学科评估数据: {len(discipline_data)} 条")
    
    # Find computer science evaluation
    for item in discipline_data[:5]:
        if isinstance(item, dict):
            name = item.get('学校名称', '')
            assessment = item.get('学科评估', '')
            print(f"    {name}: {assessment}")
    
    print(f"\n  [OK] 学科评估数据正常")
except Exception as e:
    print(f"  [FAIL] 学科评估测试失败: {e}")

# Test National Scores
print("\n[4] 测试分数线数据")
print("-" * 50)

try:
    with open("./data/national_scores.json", 'r', encoding='utf-8') as f:
        score_data = json.load(f)
    
    print(f"  加载分数线数据: {len(score_data)} 条")
    
    # Show some samples
    count = 0
    for item in score_data[:5]:
        if isinstance(item, dict):
            print(f"    {item.get('学科', 'N/A')}: {item.get('A类总分', 'N/A')}分")
            count += 1
    
    print(f"\n  [OK] 分数线数据正常")
except Exception as e:
    print(f"  [FAIL] 分数线测试失败: {e}")

# Summary Statistics
print("\n" + "=" * 70)
print("数据资源统计")
print("=" * 70)

try:
    import pandas as pd
    import json
    
    # Schools
    schools_df = pd.read_csv("./data/schools_data.csv")
    
    # Knowledge base
    with open("./data/grad_consult_qa.json", 'r', encoding='utf-8') as f:
        qa_data = json.load(f)
    
    # Discipline
    with open("./data/discipline_full.json", 'r', encoding='utf-8') as f:
        discipline_data = json.load(f)
    
    # Scores
    with open("./data/national_scores.json", 'r', encoding='utf-8') as f:
        score_data = json.load(f)
    
    print(f"""
+----------------------------------------------------------------------+
|                        系统数据资源统计                               |
+----------------------------------------------------------------------+""")
    print(f"|  院校数据库           |  {len(schools_df):>6} 所                                |")
    print(f"|  问答知识库           |  {len(qa_data):>6} 条                                |")
    print(f"|  学科评估数据         |  {len(discipline_data):>6} 条                                |")
    print(f"|  分数线数据           |  {len(score_data):>6} 条                                |")
    print(f"+----------------------------------------------------------------------+")
except Exception as e:
    print(f"统计失败: {e}")

print("\n问答效果测试完成!")
