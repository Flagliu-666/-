"""
考研择校智能问答系统 - 专业版前端
多轮对话 + RAG + 联网查询 + 大模型API
"""

import streamlit as st
import pandas as pd
import json
import time
import os
from datetime import datetime

# ==================== 初始化配置 ====================

def init_config():
    """初始化配置"""
    if 'config_initialized' not in st.session_state:
        # 尝试从.env加载API配置
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            if key == 'LLM_API_KEY' and value:
                                st.session_state.api_config = {
                                    'provider': 'zhipu',
                                    'api_key': value.strip()
                                }
        st.session_state.config_initialized = True

# 页面配置
st.set_page_config(
    page_title="考研择校智能问答系统",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .status-online { background: #4CAF50; color: white; }
    .status-offline { background: #9E9E9E; color: white; }
    .source-tag {
        background: #E3F2FD;
        color: #1565C0;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    .school-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    .info-box {
        background: #F5F7FA;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .chat-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 4px 18px;
        max-width: 75%;
        float: right;
        clear: both;
    }
    .chat-assistant {
        background: white;
        color: #333;
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 18px 4px;
        max-width: 75%;
        float: left;
        clear: both;
        border-left: 3px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)


# ==================== 配置面板 ====================

def render_config_sidebar():
    """渲染配置侧边栏"""
    with st.sidebar:
        # API配置 - 从.env自动读取，不显示UI
        
        # 联网设置
        st.markdown("### 🌐 联网设置")
        use_online = st.toggle("启用联网查询", value=True)
        
        st.markdown("---")
        
        # 用户画像
        st.markdown("### 👤 用户画像")
        
        # 基本信息
        st.markdown("**📋 基本信息**")
        
        user_bg = st.selectbox(
            "本科层次",
            ["", "985", "211", "普通一本", "二本", "专科"],
            index=0,
            help="你的本科院校层次"
        )
        
        user_school = st.text_input(
            "本科院校名称",
            placeholder="如：东北大学、杭州电子科技大学",
            help="填写你的本科学校（选填）"
        )
        
        user_major = st.selectbox(
            "本科专业",
            ["", "计算机科学与技术", "软件工程", "人工智能", "电子信息", "自动化", "机械类", "数学", "物理", "文科类", "其他理工科", "其他"],
            index=0,
            help="你本科学习的专业"
        )
        
        is_cross = st.checkbox("跨专业考研", help="是否跨专业报考")
        
        st.markdown("---")
        
        # 考研目标
        st.markdown("**🎯 考研目标**")
        
        user_major_target = st.selectbox(
            "目标专业",
            ["", "计算机科学与技术", "软件工程", "人工智能", "电子信息", "控制科学与工程", "机械工程", "材料科学与工程", "通信工程", "光学工程", "数学", "物理学", "经济学", "管理学", "法学", "新闻传播学", "教育学", "其他"],
            index=0,
            help="想要报考的研究生专业"
        )
        
        target_degree = st.radio(
            "学位类型",
            ["学硕", "专硕", "都可以"],
            horizontal=True,
            help="学术型还是专业型硕士"
        )
        
        st.markdown("---")
        
        # 分数与实力
        st.markdown("**📊 分数评估**")
        
        user_score = st.slider(
            "预估分数",
            260, 450, 330, 5,
            help="根据模考或估分情况"
        )
        
        math_level = st.select_slider(
            "数学水平",
            options=["较弱", "一般", "中等", "较好", "很强"],
            value="中等",
            help="你的数学基础和复习水平"
        )
        
        st.markdown("---")
        
        # 偏好与规划
        st.markdown("**🌟 偏好与规划**")
        
        target_region = st.multiselect(
            "目标地区",
            ["华北地区", "东北地区", "华东地区", "华中地区", "华南地区", "西南地区", "西北地区", "全国均可"],
            default=[],
            help="想去哪些地区读研（可多选）"
        )
        
        target_city = st.text_input(
            "偏好城市",
            placeholder="如：北京、上海、杭州",
            help="有特别想去城市可以填"
        )
        
        user_goal = st.selectbox(
            "考研目的",
            ["", "科研深造（读博）", "好就业", "转行换专业", "提升学历", "名校情结"],
            index=0,
            help="考研的主要目的"
        )
        
        user_progress = st.select_slider(
            "复习进度",
            options=["刚开始", "基础阶段", "强化阶段", "冲刺阶段", "已模拟过"],
            value="基础阶段",
            help="当前复习进度"
        )
        
        st.markdown("---")
        
        # 保存用户信息
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {}
        
        # 更新用户画像
        if user_bg:
            st.session_state.user_profile['background'] = user_bg
        if user_school:
            st.session_state.user_profile['school'] = user_school
        if user_major:
            st.session_state.user_profile['major'] = user_major
        if is_cross:
            st.session_state.user_profile['is_cross'] = True
            st.session_state.user_profile['cross_major'] = user_major_target
        if user_major_target:
            st.session_state.user_profile['target_major'] = user_major_target
        st.session_state.user_profile['score'] = user_score
        st.session_state.user_profile['math_level'] = math_level
        st.session_state.user_profile['target_degree'] = target_degree
        if target_region:
            st.session_state.user_profile['target_region'] = target_region
        if target_city:
            st.session_state.user_profile['target_city'] = target_city
        if user_goal:
            st.session_state.user_profile['goal'] = user_goal
        st.session_state.user_profile['progress'] = user_progress
        
        st.markdown("---")
        
        # 状态显示
        st.markdown("### 📊 系统状态")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("院校数据", "50+所")
        with col2:
            st.metric("知识库", "50+条")
        
        # 显示当前用户画像摘要
        if 'user_profile' in st.session_state and st.session_state.user_profile:
            profile = st.session_state.user_profile
            st.markdown("**👤 你的画像摘要**")
            summary_parts = []
            if profile.get('score'):
                summary_parts.append(f"预估{profile['score']}分")
            if profile.get('background'):
                summary_parts.append(f"{profile['background']}背景")
            if profile.get('target_major'):
                summary_parts.append(f"目标{profile['target_major']}")
            if summary_parts:
                st.markdown(" | ".join(summary_parts))
        
        # 来源显示
        if 'last_sources' in st.session_state:
            st.markdown("**📡 数据来源**")
            for source in st.session_state.last_sources:
                st.markdown(f'<span class="source-tag">{source}</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 操作
        if st.button("🔄 清空对话", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_context = {}
            st.rerun()
        
        if st.button("📥 导出记录", use_container_width=True):
            export_conversation()


# ==================== 主界面 ====================

def render_main():
    """渲染主界面"""
    st.markdown('<h1 class="main-title">🎓 考研择校智能问答系统</h1>', unsafe_allow_html=True)
    st.markdown("*多轮对话 · RAG检索 · 联网查询 · 大模型AI*")
    
    # 系统状态
    col_status = st.columns([1, 1, 1])
    with col_status[0]:
        st.markdown('<span class="status-badge status-online">🟢 系统运行中</span>', unsafe_allow_html=True)
    with col_status[1]:
        if 'api_config' in st.session_state:
            st.markdown('<span class="status-badge status-online">🤖 AI增强模式</span>', unsafe_allow_html=True)
    with col_status[2]:
        if st.session_state.get('use_online', True):
            st.markdown('<span class="status-badge status-online">🌐 联网模式</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 初始化
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    
    # 聊天区域
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            # 欢迎信息
            st.markdown("""
            <div class="info-box">
                <h3>👋 欢迎使用考研择校智能问答系统！</h3>
                <p>我可以帮你：</p>
                <ul>
                    <li>📚 <strong>院校查询</strong> - 了解目标院校的分数线、招生人数、考试科目</li>
                    <li>🎯 <strong>择校推荐</strong> - 根据你的情况推荐合适的院校</li>
                    <li>📖 <strong>考研咨询</strong> - 解答学硕/专硕、408/自命题等常见问题</li>
                    <li>🌐 <strong>实时查询</strong> - 联网获取最新研招信息</li>
                </ul>
                <p><strong>试试这样问我：</strong></p>
                <p>• "计算机专业有哪些性价比高的985院校？"</p>
                <p>• "东北大学的计算机考研难吗？考什么科目？"</p>
                <p>• "人工智能专业跨考有哪些选择？"</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 显示消息历史
            for msg in st.session_state.messages:
                if msg['role'] == 'user':
                    st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-assistant">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
                    if msg.get('sources'):
                        st.caption(f"📡 来源: {' + '.join(msg['sources'])}")
            
            # 显示用户画像提醒
            profile = st.session_state.get('user_profile', {})
            if profile and profile.get('score'):
                st.markdown("---")
                st.info(f"💡 当前根据你的画像推荐：预估{profile.get('score')}分 | {profile.get('target_major', '计算机专业')} | {profile.get('background', '')}背景")
    
    # 输入区域
    
    # 输入区域
    st.markdown("---")
    
    user_input = st.chat_input("输入你的问题，按Enter发送...")
    
    if user_input:
        handle_question(user_input)


def handle_question(question: str):
    """处理用户问题 - 支持追问和多轮对话"""
    if not question.strip():
        return
    
    # 初始化对话历史（用于多轮上下文）
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # 初始化当前对话中提到的学校列表（用于指代消解）
    if 'mentioned_schools' not in st.session_state:
        st.session_state.mentioned_schools = []
    
    # 追踪用户问题中提到的学校名称
    import re
    school_pattern = r'[\u4e00-\u9fa5]{2,10}(?:大学|学院|研究所)'
    mentioned = re.findall(school_pattern, question)
    if mentioned:
        # 过滤常见词汇，保留真正的学校名
        stop_words = ['某大学', '某学院', '这个大学', '那个大学', '其他大学', '相关大学']
        for school in mentioned:
            if school not in stop_words and len(school) > 3:
                if school not in st.session_state.mentioned_schools:
                    st.session_state.mentioned_schools.append(school)
        # 保持最近提到的5所学校
        if len(st.session_state.mentioned_schools) > 5:
            st.session_state.mentioned_schools = st.session_state.mentioned_schools[-5:]
    
    # 判断是否为追问（根据问题简短程度和上下文）
    is_follow_up = len(question) < 30 and len(st.session_state.messages) > 0
    
    # 添加用户消息
    st.session_state.messages.append({
        'role': 'user',
        'content': question,
        'timestamp': datetime.now().isoformat(),
        'is_follow_up': is_follow_up
    })
    
    # 添加到对话历史（用于构建上下文）
    st.session_state.conversation_history.append({
        'role': 'user',
        'content': question
    })
    
    # 保持对话历史在合理长度
    if len(st.session_state.conversation_history) > 10:
        st.session_state.conversation_history = st.session_state.conversation_history[-10:]
    
    # 显示加载状态
    with st.spinner("🤔 正在分析你的问题..."):
        answer, sources = get_answer(question, is_follow_up)
    
    # 添加助手消息
    st.session_state.messages.append({
        'role': 'assistant',
        'content': answer,
        'sources': sources,
        'timestamp': datetime.now().isoformat()
    })
    
    # 添加到对话历史
    st.session_state.conversation_history.append({
        'role': 'assistant',
        'content': answer[:200]  # 保存摘要以节省空间
    })
    
    # 更新来源
    st.session_state.last_sources = sources
    
    st.rerun()


def get_answer(question: str, is_follow_up: bool = False) -> tuple[str, list]:
    """获取回答 - 优先使用大模型，支持联网查询"""
    sources = []
    
    # 检查是否启用联网
    use_online = st.session_state.get('use_online', True)
    
    # 构建上下文
    context = build_context_for_llm(is_follow_up)
    
    # 如果启用联网且问题是关于最新信息，尝试联网搜索
    online_info = ""
    if use_online:
        online_info = get_online_info(question)
        if online_info:
            sources.append('联网搜索')
    
    # 检查是否配置了大模型
    use_llm = 'api_config' in st.session_state and st.session_state.api_config.get('api_key')
    
    if use_llm:
        try:
            import requests
            
            api_config = st.session_state.api_config
            api_key = api_config['api_key']
            provider = api_config['provider']
            
            # 构建系统提示词 - 更智能的AI
            system_prompt = """你是一个专业、热情的考研咨询顾问，名为"考研小助手"。

【核心能力】
1. 根据用户的背景（分数、本科层次、目标专业、地区偏好）给出精准推荐
2. 解答考研政策、复习方法、院校选择等问题
3. 支持追问，能够记住对话上下文
4. 推荐院校时会考虑：分数线、招生人数、学科评估、地区等因素

【回答风格】
- 专业、热情、有条理
- 给出具体院校名称和分数
- 如有必要，解释原因
- 适当使用emoji增加可读性

【重要提示】
- 分数线只是参考，每年会有波动
- 推荐时要结合用户的实际情况
- 如果不确定，可以说明需要更多信息

【代词指代规则】
- 当用户提到"他们学校"、"它"、"这个学校"等指代词时，必须结合对话历史确定指代对象
- "他们"指的是"上面提到的学校"或"上面推荐的学校"
- 优先引用最近一次提到的学校信息进行回答
- 如果不确定指代哪所学校，可以询问用户确认"""
            
            # 构建用户提示词
            online_section = ""
            if online_info:
                online_section = f"\n【联网搜索结果】（如有最新信息请优先参考）\n{online_info}\n"
            
            follow_up_section = ""
            if is_follow_up:
                follow_up_section = "\n【追问】请结合之前的对话上下文给出更精准的回答。"
            
            user_content = f"""{context}{online_section}

【当前问题】
{question}
{follow_up_section}

请给出专业、准确、有条理的回答。"""
            
            # 调用大模型
            if provider == 'zhipu':
                url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
                model = "glm-4"
            elif provider == 'openai':
                url = "https://api.openai.com/v1/chat/completions"
                model = "gpt-4"
            else:
                url = "https://api.moonshot.cn/v1/chat/completions"
                model = "moonshot-v1-8k"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
                sources = ['智谱AI', '知识库']
                return answer, sources
            else:
                print(f"API调用失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"大模型调用出错: {e}")
    
    # 回退到规则引擎
    answer = fallback_answer(question)
    sources = ['本地知识库']
    return answer, sources


def build_context_for_llm(is_follow_up: bool = False) -> str:
    """为LLM构建上下文 - 智能院校推荐"""
    context = ""
    
    # ===== 0. 添加指代上下文（最近提到的学校）=====
    mentioned_schools = st.session_state.get('mentioned_schools', [])
    if mentioned_schools and is_follow_up:
        context += "【对话中最近提到的学校】\n"
        context += "请特别注意，当用户使用'他们'、'它'、'这个学校'等指代词时，"
        context += f"应指代以下学校：{', '.join(mentioned_schools[-3:])}\n\n"
    
    # 添加对话历史摘要
    history = st.session_state.get('conversation_history', [])
    if history and is_follow_up:
        context += "【最近对话历史】（用于理解上下文和指代关系）：\n"
        # 只取最近3轮对话
        recent_history = history[-6:] if len(history) > 6 else history
        for i, msg in enumerate(recent_history):
            role = "用户" if msg.get('role') == 'user' else "助手"
            content = msg.get('content', '')[:300]  # 限制长度
            context += f"- {role}：{content}\n"
        context += "\n"
    
    # ===== 1. 添加用户画像信息 =====
    user_profile = st.session_state.get('user_profile', {})
    if user_profile:
        context += "【当前用户画像】\n"
        if user_profile.get('background'):
            context += f"- 本科层次: {user_profile['background']}\n"
        if user_profile.get('school'):
            context += f"- 本科院校: {user_profile['school']}\n"
        if user_profile.get('major'):
            context += f"- 本科专业: {user_profile['major']}\n"
        if user_profile.get('is_cross'):
            context += f"- 是否跨考: 是（跨考{user_profile.get('cross_major', '相关专业')}）\n"
        if user_profile.get('target_major'):
            context += f"- 目标专业: {user_profile['target_major']}\n"
        if user_profile.get('target_degree'):
            context += f"- 学位类型: {user_profile['target_degree']}\n"
        if user_profile.get('score'):
            context += f"- 预估分数: {user_profile['score']}分\n"
        if user_profile.get('math_level'):
            context += f"- 数学水平: {user_profile['math_level']}\n"
        if user_profile.get('target_region'):
            context += f"- 目标地区: {', '.join(user_profile['target_region'])}\n"
        if user_profile.get('target_city'):
            context += f"- 偏好城市: {user_profile['target_city']}\n"
        if user_profile.get('goal'):
            context += f"- 考研目的: {user_profile['goal']}\n"
        if user_profile.get('progress'):
            context += f"- 复习进度: {user_profile['progress']}\n"
        context += "\n【重要提示】回答时必须综合考虑用户的分数、本科背景、目标专业、地区偏好等因素，给出精准、个性化的推荐！\n\n"
    
    # ===== 2. 添加院校信息 - 智能筛选 =====
    try:
        df = pd.read_csv("./data/schools_data.csv")
        if not df.empty:
            context += "【院校数据库】\n"
            
            score = user_profile.get('score', 330)
            target_major = user_profile.get('target_major', '计算机科学与技术')
            target_region = user_profile.get('target_region', [])
            is_cross = user_profile.get('is_cross', False)
            math_level = user_profile.get('math_level', '中等')
            background = user_profile.get('background', '普通一本')
            
            # 根据分数计算浮动范围
            score_margin = 30 if score > 350 else 25 if score > 320 else 20
            
            # 基础筛选：分数线在范围内的学校
            filtered = df[
                (df['2024复试分数线'] >= score - score_margin) & 
                (df['2024复试分数线'] <= score + 20)
            ].copy()
            
            # 按推荐优先级排序
            # 1. 考虑地区偏好
            if target_region:
                region_map = {
                    '华北地区': ['北京', '天津', '河北', '山西', '内蒙古'],
                    '东北地区': ['辽宁', '吉林', '黑龙江'],
                    '华东地区': ['上海', '江苏', '浙江', '安徽', '福建', '江西', '山东'],
                    '华中地区': ['湖北', '湖南', '河南'],
                    '华南地区': ['广东', '广西', '海南'],
                    '西南地区': ['四川', '重庆', '云南', '贵州', '西藏'],
                    '西北地区': ['陕西', '甘肃', '青海', '宁夏', '新疆']
                }
                target_provinces = []
                for r in target_region:
                    if r in region_map:
                        target_provinces.extend(region_map[r])
                if target_provinces:
                    # 优先推荐目标地区的学校
                    filtered['in_region'] = filtered['所在地'].isin(target_provinces).astype(int)
                    filtered = filtered.sort_values('in_region', ascending=False)
            
            # 2. 考虑本科背景选择适合的学校层次
            if background in ['二本', '专科']:
                # 二本/专科优先推荐性价比高的学校
                filtered['priority'] = filtered.apply(
                    lambda x: 1 if x['层次'] == '211' and x['2024复试分数线'] < score - 10
                    else (2 if x['层次'] == '985' and x['2024复试分数线'] < score - 5
                    else (3 if x['层次'] == '普通' 
                    else 4)), axis=1
                )
                filtered = filtered.sort_values(['priority', '2024复试分数线'])
            elif background in ['普通一本']:
                filtered = filtered.sort_values('2024复试分数线')
            
            # 3. 根据数学水平调整推荐
            if math_level in ['较弱', '一般']:
                # 数学弱的推荐分数线稍低的学校
                filtered = filtered[filtered['2024复试分数线'] <= score + 5]
            elif math_level in ['很强', '较好']:
                # 数学强的可以冲好学校
                filtered = filtered.sort_values('2024复试分数线', ascending=False)
            
            # 取前15所推荐
            recommended = filtered.head(15)
            
            if len(recommended) > 0:
                context += f"【根据你的情况（预估{score}分），推荐以下院校】：\n\n"
                for idx, (_, row) in enumerate(recommended.iterrows(), 1):
                    level = row['层次']
                    location = row['所在地']
                    score_line = row.get('2024复试分数线', '暂无')
                    enrollment = row.get('招生人数', '暂无')
                    assessment = row.get('计算机学科评估', '暂无')
                    notes = row.get('备注', '')
                    
                    # 竞争程度评估
                    if score_line != '暂无' and score - score_line >= 30:
                        difficulty = "🟢 较稳"
                    elif score_line != '暂无' and score - score_line >= 15:
                        difficulty = "🟡 中等"
                    elif score_line != '暂无' and score - score_line >= 0:
                        difficulty = "🟠 有风险"
                    else:
                        difficulty = "🔴 难度大"
                    
                    context += f"{idx}. **{row['学校名称']}** ({level})\n"
                    context += f"   📍 {location} | 📈 分数线{score_line}分 | {difficulty}\n"
                    context += f"   👥 招生{enrollment}人 | 学科评估:{assessment}\n"
                    if notes:
                        context += f"   💡 {notes}\n"
                    context += "\n"
            else:
                context += "未找到完全匹配的院校，请调整分数或扩大搜索范围。\n\n"
            context += "\n"
    except Exception as e:
        context += f"[院校数据加载失败: {e}]\n\n"
    
    # ===== 3. 添加问答知识 - 按专业分类 =====
    try:
        with open("./data/grad_consult_qa.json", 'r', encoding='utf-8') as f:
            qa_data = json.load(f)
        if qa_data:
            context += "【考研知识库】\n"
            # 根据目标专业优先展示相关问答
            target_major = user_profile.get('target_major', '')
            relevant_qa = []
            general_qa = []
            
            for qa in qa_data:
                instruction = qa['instruction'].lower()
                if target_major and any(m.lower() in instruction for m in target_major.split('/')):
                    relevant_qa.append(qa)
                elif any(kw in instruction for kw in ['学硕', '专硕', '考研', '复习', '跨考', '国家线', '二战', '调剂', '报名']):
                    general_qa.append(qa)
            
            # 先展示相关专业的问答
            for qa in (relevant_qa + general_qa)[:15]:
                context += f"Q: {qa['instruction']}\nA: {qa['output'][:300]}...\n\n"
    except Exception as e:
        context += f"[知识库加载失败: {e}]\n\n"
    
    # ===== 4. 添加学科评估数据 =====
    try:
        with open("./data/discipline_evaluation.json", 'r', encoding='utf-8') as f:
            discipline_data = json.load(f)
        if discipline_data and target_major:
            # 匹配目标专业的学科评估
            for major_key, schools in discipline_data.items():
                if target_major and target_major.split('/')[0] in major_key:
                    context += f"【{major_key}学科评估】\n"
                    for school in schools[:8]:
                        context += f"- {school['学校']}: {school['等级']}\n"
                    context += "\n"
                    break
    except Exception as e:
        pass
    
    # ===== 5. 添加最新分数线参考 =====
    try:
        with open("./data/score_lines.json", 'r', encoding='utf-8') as f:
            score_data = json.load(f)
        if score_data and '2024年国家线' in score_data:
            latest_scores = score_data['2024年国家线']['A类']
            context += "【2024年A类国家线参考】\n"
            for category in ['工学', '理学', '经济学', '管理学', '教育学', '文学']:
                if category in latest_scores:
                    score_info = latest_scores[category]
                    context += f"- {category}: {score_info['总分']}分\n"
            context += "\n"
    except Exception as e:
        pass
    
    return context if context else "暂无额外上下文信息。"


def get_online_info(question: str) -> str:
    """联网查询最新考研信息"""
    # 需要联网查询的关键词
    online_keywords = ['最新', '2025', '2026', '今年', '招生简章', '大纲', '报名时间', '初试', '复试']
    need_online = any(kw in question for kw in online_keywords)
    
    if not need_online:
        return ""
    
    try:
        import requests
        
        # 提取查询关键词
        search_terms = question.replace('?', '').replace('？', '').replace('考研', '')
        
        # 使用百度搜索API（如果有的话）或模拟搜索
        # 这里可以集成真实的联网搜索API
        # 由于隐私和API限制，这里提供一个示例框架
        
        # 检查是否配置了联网搜索API
        if 'online_api_key' not in st.session_state:
            # 返回提示信息
            return f"""【提示】检测到您询问的是最新信息，请参考以下通用信息：
- 2025年考研预报名时间：预计9月24-27日
- 正式报名时间：预计10月5-25日
- 初试时间：预计2025年12月21-23日
- 复试时间：预计2026年3-4月

更多详细信息建议访问：
- 中国研究生招生信息网：https://yz.chsi.com.cn
- 目标院校研究生院官网"""
        
        # 如果配置了API，执行真实搜索
        api_key = st.session_state.get('online_api_key')
        # 这里可以添加真实的联网搜索逻辑
        # 使用DuckDuckGo或Bing搜索API
        
        return ""
        
    except Exception as e:
        print(f"联网查询出错: {e}")
        return ""


def search_online(query: str) -> str:
    """执行联网搜索"""
    try:
        import requests
        import urllib.parse
        
        encoded_query = urllib.parse.quote(f"考研 {query}")
        
        # 使用 DuckDuckGo Instant Answer API (免费，无需API Key)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_redirect=1"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('AbstractText'):
                return data['AbstractText'][:500]
            elif data.get('RelatedTopics'):
                for topic in data['RelatedTopics'][:3]:
                    if 'Text' in topic:
                        return topic['Text'][:300]
        
        return ""
    except:
        return ""


def fallback_answer(question: str) -> str:
    """备用回答（规则引擎）"""
    try:
        import pandas as pd
        import json
        
        df = pd.read_csv("./data/schools_data.csv")
        with open("./data/grad_consult_qa.json", 'r', encoding='utf-8') as f:
            qa_data = json.load(f)
        
        # 检查学校
        for school in df['学校名称'].values:
            if school in question:
                row = df[df['学校名称'] == school].iloc[0]
                return f"""**{school}** 信息如下：

📍 位置: {row['所在地']} | 🎓 层次: {row['层次']}
📈 分数线: {row.get('2024复试分数线', '暂无')}分
👥 招生人数: {row.get('招生人数', '暂无')}人
📚 初试科目:
• {row.get('初试科目(政治)', '')}
• {row.get('初试科目(英语)', '')}
• {row.get('初试科目(数学)', '')}
• {row.get('初试科目(专业课)', '')}

💡 备注: {row.get('备注', '')}"""
        
        # 检查知识库
        for qa in qa_data:
            keywords = [w for w in qa['instruction'] if len(w) >= 3]
            if any(kw in question.lower() for kw in keywords):
                return qa['output']
        
        # 推荐
        if any(kw in question for kw in ['推荐', '选择', '什么学校']):
            filtered = df[df['层次'] == '985'].head(6)
            response = "🎯 为你推荐以下985院校：\n\n"
            for i, (_, row) in enumerate(filtered.iterrows(), 1):
                response += f"{i}. **{row['学校名称']}** ({row.get('计算机学科评估', '无')})\n"
                response += f"   📍 {row['所在地']} | 📈 {row.get('2024复试分数线', '暂无')}分\n\n"
            return response
        
    except Exception as e:
        print(f"规则引擎出错: {e}")
    
    return """👋 我可以帮你解答考研相关问题！

请试试这样问我：
• "推荐计算机985院校"
• "东北大学考什么科目"
• "学硕和专硕区别"
• "人工智能跨考方向"

或者告诉我你的情况（分数、专业偏好），我来帮你分析！"""


def export_conversation():
    """导出对话记录"""
    if 'messages' in st.session_state and st.session_state.messages:
        export_data = {
            'export_time': datetime.now().isoformat(),
            'messages': st.session_state.messages,
            'user_profile': st.session_state.get('user_profile', {})
        }
        
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 下载对话记录",
            data=json_str,
            file_name=f"考研咨询记录_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )


# ==================== 运行 ====================

def main():
    init_config()  # 初始化配置（自动加载.env中的API密钥）
    render_config_sidebar()
    render_main()


if __name__ == "__main__":
    main()
