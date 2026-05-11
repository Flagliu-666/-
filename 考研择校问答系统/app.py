"""
考研择校智能问答系统 - Streamlit前端
基于RAG的智能考研咨询系统
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入RAG引擎
from rag_engine import GradSchoolRAG, SystemConfig

# 页面配置
st.set_page_config(
    page_title="考研择校智能问答系统",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入中文化JavaScript
st.markdown("""
<script>
// Streamlit 界面中文化
(function() {
    'use strict';
    
    const translations = {
        'Deploy this app': '部署此应用',
        'Settings': '设置',
        'Print': '打印',
        'Record a screencast': '录制屏幕',
        'About': '关于',
        'Documentation': '文档',
        'Ask a question': '提问',
        'Report a bug': '报告问题',
        'Theme': '主题',
        'Light theme': '浅色主题',
        'Dark theme': '深色主题',
        'Custom theme': '自定义主题',
        'Use default colors': '使用默认颜色',
        'Menu and toolbar visibility': '菜单和工具栏',
        'Follow': '关注',
        'Star': '星标',
        'Fork': '复刻',
    };
    
    function translateText(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent.trim();
            if (translations[text]) {
                node.textContent = node.textContent.replace(text, translations[text]);
            }
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            node.childNodes.forEach(child => translateText(child));
        }
    }
    
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                translateText(node);
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    translateText(document.body);
})();
</script>
""", unsafe_allow_html=True)

# 自定义CSS样式
st.markdown("""
<style>
    /* 主色调 */
    :root {
        --primary-color: #4A90D9;
        --secondary-color: #5C6BC0;
        --accent-color: #FF7043;
        --background-color: #F5F7FA;
    }
    
    /* 标题样式 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1A237E;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* 聊天消息样式 */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .bot-message {
        background: #FFFFFF;
        color: #333;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #4A90D9;
    }
    
    /* 学校卡片样式 */
    .school-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #4A90D9;
        transition: all 0.3s ease;
    }
    
    .school-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
    }
    
    /* 统计卡片 */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* 侧边栏样式 */
    .sidebar-section {
        background: #F8F9FA;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* 标签样式 */
    .tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.25rem;
    }
    
    .tag-985 {
        background: #E3F2FD;
        color: #1565C0;
    }
    
    .tag-211 {
        background: #E8F5E9;
        color: #2E7D32;
    }
    
    .tag-a {
        background: #FFF3E0;
        color: #E65100;
    }
    
    /* 进度指示器 */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin: 1rem 0;
    }
    
    .step {
        flex: 1;
        text-align: center;
        padding: 0.5rem;
        background: #E0E0E0;
        border-radius: 20px;
        margin: 0 0.25rem;
        font-size: 0.8rem;
    }
    
    .step.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .step.completed {
        background: #4CAF50;
        color: white;
    }
    
    /* 空消息占位 */
    .empty-chat {
        text-align: center;
        padding: 3rem;
        color: #9E9E9E;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态"""
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'background': None,
            'target_major': None,
            'target_score': None,
            'preference': None
        }
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []


@st.cache_resource
def load_rag_system():
    """加载RAG系统（带缓存）"""
    try:
        config = SystemConfig(
            embedding_model="BAAI/bge-large-zh-v1.5",
            persist_directory="./data/chroma_db",
            collection_name="grad_consult"
        )
        return GradSchoolRAG(config)
    except Exception as e:
        st.error(f"加载RAG系统失败: {e}")
        return None


def render_header():
    """渲染页面头部"""
    st.markdown('<h1 class="main-title">🎓 考研择校智能问答系统</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; margin-bottom: 2rem;">基于RAG技术的智能考研咨询平台 - 让AI帮你找到最适合的学校</p>', unsafe_allow_html=True)


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("## 📋 用户信息卡片")
        
        # 用户画像输入
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**👤 基本信息**")
        
        background = st.selectbox(
            "本科背景",
            options=["", "985/211", "普通一本", "二本/三本", "专科"],
            index=0
        )
        
        target_major = st.selectbox(
            "目标专业",
            options=["", "计算机科学与技术", "软件工程", "人工智能", 
                     "电子信息", "控制科学与工程", "机械工程", "其他"],
            index=0
        )
        
        target_score = st.slider(
            "预估分数",
            min_value=260,
            max_value=450,
            value=330,
            step=5,
            help="你的预估初试分数"
        )
        
        preference = st.multiselect(
            "偏好设置",
            options=["985优先", "211优先", "一线城市", "离家近", "好就业"],
            default=[]
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 快速统计
        st.markdown("### 📊 数据统计")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("收录院校", "31所", "985+211")
        with col2:
            st.metric("问答知识", "12条", "持续更新")
        
        # 操作按钮
        st.markdown("### 🔧 操作")
        
        if st.button("🔄 重置对话", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.rag_system:
                st.session_state.rag_system.clear_memory()
            st.rerun()
        
        if st.button("📥 导出推荐结果", use_container_width=True):
            export_recommendations()
        
        # 系统信息
        st.markdown("### ℹ️ 系统信息")
        st.caption("技术栈: LangChain + ChromaDB + Streamlit")
        st.caption(f"版本: 1.0.0 | {datetime.now().strftime('%Y-%m-%d')}")
        
        return {
            'background': background,
            'target_major': target_major,
            'target_score': target_score,
            'preference': preference
        }


def render_chat_interface():
    """渲染聊天界面"""
    # 聊天容器
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            # 空状态
            st.markdown("""
            <div class="empty-chat">
                <h3>👋 你好，我是考研助手小智</h3>
                <p>我可以帮你解答考研相关问题，推荐适合你的院校</p>
                <br>
                <p>试试这样问我：</p>
                <p>• "我想考计算机，数学一般，推荐什么学校？"</p>
                <p>• "东北大学考研难吗？考什么科目？"</p>
                <p>• "408和自命题有什么区别？"</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 显示消息历史
            for msg in st.session_state.messages:
                if msg['role'] == 'user':
                    st.markdown(f'<div class="user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-message">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    # 输入区域
    st.markdown("---")
    
    # 快捷问题
    st.markdown("**💡 快捷问题**")
    quick_questions = [
        "推荐几所性价比高的985院校",
        "计算机专业考408还是自命题？",
        "学硕和专硕怎么选？"
    ]
    
    cols = st.columns(len(quick_questions))
    for i, q in enumerate(quick_questions):
        if cols[i].button(q, key=f"quick_{i}"):
            handle_user_input(q)
    
    # 用户输入
    user_input = st.chat_input("输入你的问题...", key="chat_input")
    
    return user_input


def render_recommendations(recommendations):
    """渲染推荐结果"""
    if not recommendations:
        return
    
    st.markdown("---")
    st.markdown("## 🏫 推荐院校")
    
    for rec in recommendations:
        with st.expander(f"**{rec['学校名称']}**", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**📍 位置**: {rec['所在地']}")
                st.markdown(f"**🎓 层次**: {rec['层次']}")
                st.markdown(f"**⭐ 学科评估**: {rec['学科评估']}")
            
            with col2:
                st.markdown(f"**📈 分数线**: {rec['分数线']}分")
                st.markdown(f"**👥 招生人数**: {rec['招生人数']}人")
                st.markdown(f"**⏰ 学制**: {rec['学制']}")
            
            with col3:
                st.markdown(f"**📚 初试科目**:")
                st.code(rec['初试科目'])
            
            if rec.get('备注'):
                st.markdown(f"**💡 备注**: {rec['备注']}")


def handle_user_input(question: str):
    """处理用户输入"""
    if not question.strip():
        return
    
    # 添加用户消息
    st.session_state.messages.append({
        'role': 'user',
        'content': question,
        'timestamp': datetime.now()
    })
    
    # 获取RAG系统回复
    if st.session_state.rag_system is None:
        st.session_state.rag_system = load_rag_system()
    
    if st.session_state.rag_system:
        try:
            result = st.session_state.rag_system.query(question)
            answer = result['answer']
        except Exception as e:
            # 使用规则引擎
            answer = generate_rule_based_response(question)
    else:
        answer = generate_rule_based_response(question)
    
    # 添加助手消息
    st.session_state.messages.append({
        'role': 'assistant',
        'content': answer,
        'timestamp': datetime.now()
    })
    
    # 检查是否需要更新推荐
    if any(kw in question for kw in ['推荐', '选择', '什么学校', '考哪里']):
        recommendations = get_recommendations()
        st.session_state.recommendations = recommendations
    
    st.rerun()


def generate_rule_based_response(question: str) -> str:
    """生成基于规则的回复"""
    question_lower = question.lower()
    
    # 加载数据
    try:
        df = pd.read_csv("./data/schools_data.csv")
        with open("./data/grad_consult_qa.json", 'r', encoding='utf-8') as f:
            qa_data = json.load(f)
    except:
        return "抱歉，数据加载失败。请确保data目录下有相应的数据文件。"
    
    # 1. 检查是否询问特定学校
    for school in df['学校名称'].values:
        if school in question:
            row = df[df['学校名称'] == school].iloc[0]
            return f"""**{school}** 信息如下：

📍 **所在地**: {row['所在地']} | 🎓 **层次**: {row['层次']}

📈 **2024复试分数线**: {row['2024复试分数线']}分
👥 **招生人数**: 约{row['招生人数']}人
⏰ **学制**: {row['学制']}

📚 **初试科目**:
- {row['初试科目(政治)']}
- {row['初试科目(英语)']}
- {row['初试科目(数学)']}
- {row['初试科目(专业课)']}

💡 **备注**: {row['备注']}

需要了解更多信息吗？"""
    
    # 2. 检查是否询问通用问题
    for qa in qa_data:
        if any(keyword in question for keyword in qa['instruction'].split()[:3]):
            return qa['output']
    
    # 3. 默认回复
    return """我需要更多具体信息来帮你分析。请告诉我：

1. **你的本科背景**是什么？（985/211/普通本科/专科）
2. **你的目标分数**大概是多少？
3. **想考什么专业**？（计算机/软件/电子等）
4. 有**地域偏好**吗？（一线城市/家乡附近等）

告诉我这些信息，我可以给你更精准的推荐！"""


def get_recommendations() -> list:
    """获取推荐结果"""
    try:
        df = pd.read_csv("./data/schools_data.csv")
        
        # 简单推荐逻辑：按性价比排序
        recommendations = []
        for _, row in df.iterrows():
            if row['层次'] in ['985', '211'] and row.get('计算机学科评估') in ['A+', 'A', 'A-', 'B+', 'B']:
                recommendations.append({
                    "学校名称": row['学校名称'],
                    "所在地": row['所在地'],
                    "层次": row['层次'],
                    "学科评估": row.get('计算机学科评估', '无'),
                    "分数线": row.get('2024复试分数线', '暂无'),
                    "招生人数": row.get('招生人数', '暂无'),
                    "初试科目": f"{row.get('初试科目(英语)', '')} + {row.get('初试科目(数学)', '')} + {row.get('初试科目(专业课)', '')}",
                    "学制": row.get('学制', ''),
                    "备注": row.get('备注', ''),
                })
        
        return recommendations[:10]
    except:
        return []


def export_recommendations():
    """导出推荐结果"""
    if st.session_state.recommendations:
        df = pd.DataFrame(st.session_state.recommendations)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 下载CSV",
            data=csv,
            file_name="考研推荐结果.csv",
            mime="text/csv"
        )
    else:
        st.info("暂无推荐结果，请先进行问答咨询")


def main():
    """主函数"""
    # 初始化
    init_session_state()
    
    # 渲染头部
    render_header()
    
    # 渲染侧边栏并获取用户信息
    user_profile = render_sidebar()
    
    # 主内容区
    col_main, col_recommend = st.columns([2, 1])
    
    with col_main:
        # 渲染聊天界面
        user_input = render_chat_interface()
        
        # 处理用户输入
        if user_input:
            handle_user_input(user_input)
    
    with col_recommend:
        # 推荐院校侧边栏
        st.markdown("### 🏫 精选推荐")
        
        recommendations = get_recommendations()
        for rec in recommendations[:5]:
            with st.container():
                st.markdown(f"""
                **{rec['学校名称']}**  
                📍 {rec['所在地']} | ⭐ {rec['学科评估']}  
                📈 {rec['分数线']}分 | 👥 {rec['招生人数']}人
                ---
                """)
        
        if st.button("查看全部推荐", use_container_width=True):
            st.session_state.show_all_recommendations = True


def main_interface():
    """备用：简洁界面"""
    st.title("🎓 考研择校智能问答系统")
    
    # 初始化RAG系统
    if st.session_state.rag_system is None:
        with st.spinner("🔄 正在加载系统..."):
            st.session_state.rag_system = load_rag_system()
    
    # 聊天历史
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                st.chat_message("user").write(msg['content'])
            else:
                st.chat_message("assistant").write(msg['content'])
    
    # 用户输入
    if prompt := st.chat_input("输入你的问题..."):
        # 添加用户消息
        st.session_state.messages.append({
            'role': 'user',
            'content': prompt
        })
        st.chat_message("user").write(prompt)
        
        # 获取回复
        if st.session_state.rag_system:
            result = st.session_state.rag_system.query(prompt)
            answer = result['answer']
        else:
            answer = generate_rule_based_response(prompt)
        
        # 添加助手消息
        st.session_state.messages.append({
            'role': 'assistant',
            'content': answer
        })
        st.chat_message("assistant").write(answer)


# 运行
if __name__ == "__main__":
    # 尝试使用新界面
    try:
        main()
    except Exception as e:
        st.error(f"界面加载出错: {e}")
        main_interface()
