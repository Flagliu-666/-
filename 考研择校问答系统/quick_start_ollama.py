"""
考研择校智能问答系统 - Ollama增强版
支持接入本地开源大模型
"""

import streamlit as st
import pandas as pd
import json
import os
import requests

# 页面配置
st.set_page_config(
    page_title="考研择校助手",
    page_icon="🎓",
    layout="wide"
)

# ==================== 配置 ====================
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b"

# ==================== 数据加载 ====================

@st.cache_data
def load_school_data():
    try:
        return pd.read_csv("./data/schools_data.csv")
    except:
        return None

@st.cache_data
def load_qa_data():
    try:
        with open("./data/grad_consult_qa.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# ==================== Ollama调用 ====================

def call_ollama(question: str, context: str = "") -> str:
    """调用Ollama大模型"""
    prompt = f"""你是一个专业的考研咨询顾问。请根据以下信息回答用户问题。

{context}

用户问题：{question}

请给出专业、准确的回答。如果信息不足，请基于你的知识给出合理建议。"""
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": DEFAULT_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            return None
    except:
        return None

def check_ollama_available() -> bool:
    """检查Ollama是否可用"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

# ==================== 规则引擎 ====================

def query_school(df, question):
    for school in df['学校名称'].values:
        if school in question:
            row = df[df['学校名称'] == school].iloc[0]
            return format_school_info(row)
    return None

def format_school_info(row):
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

def get_recommendations(df, score=None, level='985', top_n=6):
    filtered = df.copy()
    
    if level == '985':
        filtered = filtered[filtered['层次'] == '985']
    elif level == '211':
        filtered = filtered[filtered['层次'] == '211']
    elif level == '普通':
        filtered = filtered[filtered['层次'].isin(['普通', ''])]
    
    if score:
        filtered = filtered[filtered['2024复试分数线'] <= score + 30]
    
    filtered = filtered.sort_values('计算机学科评估', ascending=False)
    
    return [{
        '学校': row['学校名称'],
        '位置': row['所在地'],
        '层次': row['层次'],
        '评估': row['计算机学科评估'],
        '分数线': row['2024复试分数线'],
        '招生': row['招生人数'],
        '备注': row['备注']
    } for _, row in filtered.head(top_n).iterrows()]

def build_context(df, qa_data):
    """构建上下文信息"""
    context = "【院校信息】\n"
    for _, row in df.head(20).iterrows():
        context += f"- {row['学校名称']}: {row['层次']} | {row['所在地']} | 分数线{row['2024复试分数线']}分\n"
    
    context += "\n【常见问题解答】\n"
    for qa in qa_data[:15]:
        context += f"Q: {qa['instruction']}\n"
        context += f"A: {qa['output'][:200]}...\n\n"
    
    return context

def generate_response(question, df, qa_data, use_llm=True):
    """生成回复"""
    # 1. 查特定学校
    school_info = query_school(df, question)
    if school_info:
        return school_info, True
    
    # 2. 查推荐
    recommend_keywords = ['推荐', '选择', '择校', '考哪个', '什么学校好', '性价比']
    if any(kw in question for kw in recommend_keywords):
        level = '985'
        if '211' in question:
            level = '211'
        if '双非' in question or '普通' in question:
            level = '普通'
        
        recommendations = get_recommendations(df, level=level)
        if recommendations:
            response = "🎯 为你推荐以下院校：\n\n"
            for i, rec in enumerate(recommendations, 1):
                response += f"**{i}. {rec['学校']}** ({rec['评估']})\n"
                response += f"   📍 {rec['位置']} | 📈 {rec['分数线']}分 | 👥 {rec['招生']}人\n"
                response += f"   💡 {rec['备注']}\n\n"
            return response, True
    
    # 3. 知识库匹配
    for qa in qa_data:
        q_keywords = qa['instruction'].lower()
        words = [w for w in q_keywords if len(w) >= 3]
        for word in words:
            if word in question.lower() and word not in ['什么', '哪些', '怎么', '如何', '哪个', '是不是', '学校', '专业', '考研', '分数']:
                return qa['output'], True
    
    # 4. 调用Ollama（如果可用且启用）
    if use_llm and check_ollama_available():
        with st.spinner("🤔 AI正在思考..."):
            context = build_context(df, qa_data)
            answer = call_ollama(question, context)
            if answer:
                return f"💡 **AI智能回答：**\n\n{answer}", True
    
    # 5. 默认回复
    return """👋 我可以帮你解答这些问题：

🔹 **院校查询**: "清华大学怎么样"、"东北大学考什么"
🔹 **择校推荐**: "推荐计算机院校"、"985性价比高的学校"
🔹 **科目咨询**: "408是什么"、"学硕专硕区别"
🔹 **备考问题**: "分数线怎么划"、"英语怎么复习"

请告诉我你的情况（本科背景、目标分数、专业偏好），我来帮你分析！""", False

# ==================== 界面 ====================

def main():
    st.title("🎓 考研择校智能问答系统")
    st.markdown("*AI增强版 - 支持智能问答*")
    
    # 检查Ollama状态
    ollama_on = check_ollama_available()
    if ollama_on:
        st.success("🟢 Ollama已连接 - AI增强模式已开启")
    else:
        st.info("🔵 运行中 - 如需AI增强功能，请安装Ollama")
    
    df = load_school_data()
    qa_data = load_qa_data()
    
    if df is None:
        st.error("❌ 数据加载失败")
        return
    
    # 侧边栏
    with st.sidebar:
        st.markdown("## 📋 筛选条件")
        
        level = st.selectbox("院校层次", ["全部", "985", "211", "普通"], index=1)
        score = st.slider("预估分数", 260, 450, 330, 5)
        
        st.markdown("---")
        st.markdown("### 📊 数据统计")
        st.metric("收录院校", len(df))
        st.metric("问答知识", len(qa_data) if qa_data else 0)
        
        # 是否使用AI
        use_llm = st.checkbox("🤖 启用AI增强", value=ollama_on, disabled=not ollama_on)
        
        if not ollama_on:
            st.caption("💡 安装Ollama后可启用AI功能")
        
        if st.button("🔄 重置对话"):
            st.session_state.messages = []
            st.rerun()
    
    # 聊天界面
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            st.chat_message("user").write(msg['content'])
        else:
            st.chat_message("assistant").write(msg['content'])
    
    # 输入
    if prompt := st.chat_input("问我任何关于考研的问题..."):
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        st.chat_message("user").write(prompt)
        
        response, matched = generate_response(prompt, df, qa_data, use_llm)
        st.session_state.messages.append({'role': 'assistant', 'content': response})
        st.chat_message("assistant").write(response)

if __name__ == "__main__":
    main()
