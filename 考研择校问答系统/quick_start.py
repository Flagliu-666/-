"""
考研择校智能问答系统
快速启动脚本 - 极简版
无需安装额外依赖，直接运行
"""

import streamlit as st
import pandas as pd
import json
import os

# 页面配置
st.set_page_config(
    page_title="考研择校助手",
    page_icon="🎓",
    layout="wide"
)

# ==================== 数据加载 ====================

@st.cache_data
def load_school_data():
    """加载院校数据"""
    try:
        df = pd.read_csv("./data/schools_data.csv")
        return df
    except:
        return None

@st.cache_data
def load_qa_data():
    """加载问答数据"""
    try:
        with open("./data/grad_consult_qa.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# ==================== 规则引擎 ====================

def query_school(df, question):
    """查询学校"""
    for school in df['学校名称'].values:
        if school in question:
            row = df[df['学校名称'] == school].iloc[0]
            return format_school_info(row)
    return None

def format_school_info(row):
    """格式化学校信息"""
    return f"""
**{row['学校名称']}** 

📍 位置: {row['所在地']} | 🎓 层次: {row['层次']}

📈 分数线: {row['2024复试分数线']}分
👥 招生: {row['招生人数']}人
⏰ 学制: {row['学制']}

📚 初试科目:
- {row['初试科目(政治)']}
- {row['初试科目(英语)']}
- {row['初试科目(数学)']}  
- {row['初试科目(专业课)']}

💡 {row['备注']}
"""

def get_recommendations(df, score=None, level='普通', top_n=5):
    """获取推荐"""
    filtered = df.copy()
    
    # 院校层次筛选
    if level == '985':
        filtered = filtered[filtered['层次'] == '985']
    elif level == '211':
        filtered = filtered[(filtered['层次'] == '211') | (filtered['层次'] == '985')]
    elif level == '普通':
        filtered = filtered[filtered['层次'].isin(['211', '985']) == False]
        if len(filtered) == 0:
            # 如果没有普通院校数据，选择211中分数线较低的
            filtered = df[df['层次'] == '211'].sort_values('2024复试分数线').head(20)
    
    # 分数筛选
    if score:
        if score >= 340:
            # 高分用户：推荐的学校分数线应该比用户分数低
            filtered = filtered[
                (filtered['2024复试分数线'] <= score - 10) & 
                (filtered['2024复试分数线'] >= 200)
            ]
        elif score >= 280:
            # 中等分数：推荐接近用户分数的院校
            filtered = filtered[
                (filtered['2024复试分数线'] <= score + 20) & 
                (filtered['2024复试分数线'] >= score - 40)
            ]
        else:
            # 低分用户：推荐分数线最低的院校
            filtered = filtered.sort_values('2024复试分数线')
    
    # 按性价比排序（评估等级高 + 分数线相对低 = 性价比高）
    if len(filtered) > 0:
        # 评估等级映射
        grade_map = {'A+': 10, 'A': 9, 'A-': 8, 'B+': 7, 'B': 6, 'B-': 5, 'C+': 4, 'C': 3, 'C-': 2, '-': 0, '': 0}
        filtered = filtered.copy()
        filtered['评估分数'] = filtered['学科评估'].map(lambda x: grade_map.get(str(x), 0))
        filtered['性价比'] = filtered['评估分数'] - filtered['2024复试分数线'] / 50
        filtered = filtered.sort_values('性价比', ascending=False)
    
    results = []
    for _, row in filtered.head(top_n).iterrows():
        results.append({
            '学校': row['学校名称'],
            '位置': row['所在地'],
            '层次': row['层次'],
            '评估': row['学科评估'] if row['学科评估'] else '-',
            '分数线': row['2024复试分数线'],
            '招生': row['招生人数'],
            '备注': row['备注']
        })
    
    return results

def generate_response(question, df, qa_data):
    """生成回复 - 智能匹配"""
    question_lower = question.lower()
    
    # ===== 1. 优先：查特定学校 =====
    school_info = query_school(df, question)
    if school_info:
        return school_info
    
    # ===== 2. 查推荐学校 =====
    recommend_keywords = ['推荐', '选择', '择校', '考哪个', '什么学校好', '性价比', '帮忙', '分析']
    if any(kw in question for kw in recommend_keywords):
        # 从问题中提取用户信息
        import re
        user_score = None
        user_background = None
        
        # 提取分数
        score_match = re.search(r'(\d{2,3})\s*分', question)
        if score_match:
            user_score = int(score_match.group(1))
        
        # 提取背景信息
        if '二本' in question or '普通本科' in question or '双非' in question:
            user_background = '普通'
        
        # 根据分数智能推荐合适层次的院校
        if user_score:
            if user_score >= 380:
                level = '985'
                advice = f"以您的{user_score}分，可以冲985顶尖院校！"
            elif user_score >= 340:
                level = '985'
                advice = f"以您的{user_score}分，建议985中等院校或211强势专业。"
            elif user_score >= 310:
                level = '211'
                advice = f"以您的{user_score}分，推荐211院校或普通院校王牌专业。"
            elif user_score >= 280:
                level = '211'
                advice = f"以您的{user_score}分，建议重点考虑211院校或普通院校。"
            else:
                level = '普通'
                advice = f"以您的{user_score}分，建议选择普通院校的上岸机会更大。"
        else:
            level = '普通'
            advice = "请告诉我您的预估分数，我好给您更精准的推荐。"
        
        # 允许用户手动指定院校层次
        if '985' in question and '211' not in question:
            level = '985'
        if '211' in question and '985' not in question:
            level = '211'
        if '双非' in question or '普通' in question or '二本' in question:
            level = '普通'
        
        recommendations = get_recommendations(df, score=user_score, level=level, top_n=6)
        if recommendations:
            response = f"**{advice}**\n\n为你推荐以下{level}院校：\n\n"
            for i, rec in enumerate(recommendations, 1):
                response += f"**{i}. {rec['学校']}** ({rec['评估']})\n"
                response += f"   位置: {rec['位置']} | 分数线: {rec['分数线']}分 | 招生: {rec['招生']}人\n"
                response += f"   {rec['备注']}\n\n"
            return response
        else:
            return f"{advice} 当前筛选条件暂无符合条件的院校，请调整分数或院校层次。"
    
    # ===== 3. 通用问题匹配 =====
    # 构建关键词->回答映射
    qa_map = {
        '408': '408是计算机学科专业基础综合的代号，由教育部统一命题。考试内容包含数据结构、计算机组成原理、操作系统和计算机网络四门课程。考408的高校通常是好学校，因为题目难度大、覆盖面广。',
        '学硕': '学硕(学术型硕士)和专硕(专业型硕士)的主要区别:\n1. 培养目标: 学硕侧重科研，专硕侧重实践\n2. 学制: 学硕3年，专硕2-3年\n3. 学费: 学硕通常8000/年，专硕10000+/年\n4. 读博: 学硕可直接转博，专硕需统考\n5. 考试难度: 学硕英语一+数学一，专硕相对简单\n计算机专业建议: 想读博选学硕，想就业选专硕。',
        '专硕': '专硕(专业型硕士)特点:\n1. 侧重实践应用\n2. 学制通常2-3年\n3. 学费较高(10000+/年)\n4. 读博需参加统考\n5. 考试科目相对简单(英语二+数学二)\n适合目标以就业为主的同学，性价比高。',
        '分数线': '考研分数线分两种:\n1. 国家线: 教育部统一划定，是上岸最低门槛\n2. 院校线: 各校自主划定，通常高于国家线\n34所985可自主划线，分数可能远高于国家线。\n例如计算机A类国家线310，但清华线可能380+。',
        '数学': '计算机考研数学:\n学硕考数学一，专硕考数学二。\n数学一内容: 高数+线代+概率论\n数学二内容: 高数+线代(不考概率)\n难度: 数学一 > 数学二\n建议数学基础弱的同学优先考虑考数学二的专硕。',
        '英语': '考研英语区别:\n英语一: 学硕考，难度较高，词汇量要求大\n英语二: 专硕考，难度相对较低\n英语一和英语二在题型上相似，但英语一文章难度更大。',
        '调剂': '考研调剂要点:\n1. 只能调剂到相关专业(相近学科代码)\n2. 调剂需要等调剂系统开放\n3. 学硕可调专硕，专硕一般不能调学硕\n4. 热门学校调剂竞争激烈\n5. 建议提前联系导师',
        '难': '考研难度取决于:\n1. 学校层次: 985 > 211 > 普通\n2. 专业排名: A+ > A > B+\n3. 地区热度: 北京上海 > 省会 > 一般城市\n4. 招生人数: 人数少难度大\n建议根据自己的实力合理选择，不要盲目冲高。'
    }
    
    # 智能匹配
    for keyword, answer in qa_map.items():
        if keyword in question_lower:
            return answer
    
    # ===== 4. 匹配问答知识库 =====
    for qa in qa_data:
        # 检查问题关键词是否在用户问题中
        q_keywords = qa['instruction'].lower()
        # 提取3个以上字符的关键词
        words = [w for w in q_keywords if len(w) >= 3]
        for word in words:
            if word in question_lower and word not in ['什么', '哪些', '怎么', '如何', '哪个', '是不是']:
                return qa['output']
    
    # ===== 5. 默认回复 =====
    return """👋 我可以帮你解答这些问题：

🔹 **院校查询**: "清华大学怎么样"、"东北大学考什么"
🔹 **择校推荐**: "推荐计算机院校"、"985性价比高的学校"
🔹 **科目咨询**: "408是什么"、"学硕专硕区别"
🔹 **备考问题**: "分数线怎么划"、"数学一和数学二区别"

请告诉我你的情况（本科背景、目标分数、专业偏好），我来帮你分析！"""

# ==================== 界面 ====================

def main():
    st.title("🎓 考研择校智能问答系统")
    st.markdown("*基于规则的智能考研咨询助手*")
    
    # 加载数据
    df = load_school_data()
    qa_data = load_qa_data()
    
    if df is None:
        st.error("❌ 数据加载失败，请确保 data/schools_data.csv 存在")
        return
    
    # 侧边栏
    with st.sidebar:
        st.markdown("## 📋 筛选条件")
        
        level = st.selectbox(
            "院校层次",
            ["全部", "985", "211", "普通"],
            index=1
        )
        
        score = st.slider(
            "预估分数",
            260, 450, 330, 5,
            help="你的预估初试分数"
        )
        
        st.markdown("---")
        st.markdown("### 📊 数据统计")
        st.metric("收录院校", len(df))
        st.metric("问答知识", len(qa_data) if qa_data else 0)
        
        # 快速推荐
        if st.button("🔍 查看推荐", use_container_width=True):
            recommendations = get_recommendations(df, score, level)
            st.session_state.recommendations = recommendations
    
    # 主界面
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 聊天历史
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                st.chat_message("user").write(msg['content'])
            else:
                st.chat_message("assistant").write(msg['content'])
        
        # 输入
        if prompt := st.chat_input("问我任何关于考研的问题..."):
            # 用户消息
            st.session_state.messages.append({
                'role': 'user',
                'content': prompt
            })
            st.chat_message("user").write(prompt)
            
            # 助手回复
            response = generate_response(prompt, df, qa_data)
            st.session_state.messages.append({
                'role': 'assistant',
                'content': response
            })
            st.chat_message("assistant").write(response)
    
    with col2:
        # 推荐列表
        st.markdown("### 🏫 精选推荐")
        
        if 'recommendations' in st.session_state:
            for rec in st.session_state.recommendations:
                with st.container():
                    st.markdown(f"""
                    **{rec['学校']}**  
                    ⭐ {rec['评估']} | 📈 {rec['分数线']}分  
                    📍 {rec['位置']} | 👥 {rec['招生']}人
                    """)
                    st.divider()
        else:
            # 默认显示几所
            recommendations = get_recommendations(df, 330, '985', 3)
            for rec in recommendations:
                with st.container():
                    st.markdown(f"**{rec['学校']}** ({rec['评估']})")
                    st.caption(f"📈 {rec['分数线']}分 | 📍 {rec['位置']}")
                    st.divider()

# ==================== 运行 ====================

if __name__ == "__main__":
    main()
