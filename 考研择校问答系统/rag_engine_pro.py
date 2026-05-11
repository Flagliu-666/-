"""
考研择校问答系统 - 专业版
RAG + 大模型API + 联网查询
支持：智谱AI、OpenAI、Kimi
"""

import os
import json
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import requests

# 尝试导入可选依赖
try:
    from langchain_community.embeddings import HuggingFaceBgeEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.docstore.document import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# 爬虫模块
from crawler.chsi_crawler import ChsiCrawler


@dataclass
class LLMConfig:
    """大模型配置"""
    provider: str = "zhipu"  # zhipu, openai, kimi
    api_key: str = ""
    model: str = "glm-4"
    base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    temperature: float = 0.7
    max_tokens: int = 1000


class LLMWrapper:
    """大模型包装器 - 支持多种API"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._init_client()
    
    def _init_client(self):
        """初始化客户端"""
        if self.config.provider == "zhipu":
            self._call = self._call_zhipu
        elif self.config.provider == "openai":
            self._call = self._call_openai
        elif self.config.provider == "kimi":
            self._call = self._call_kimi
        else:
            raise ValueError(f"不支持的 provider: {self.config.provider}")
    
    def _call_zhipu(self, messages: List[Dict]) -> str:
        """调用智谱AI"""
        url = f"{self.config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"智谱API错误: {response.status_code} - {response.text}")
    
    def _call_openai(self, messages: List[Dict]) -> str:
        """调用OpenAI API"""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API错误: {response.status_code}")
    
    def _call_kimi(self, messages: List[Dict]) -> str:
        """调用Kimi API"""
        url = "https://api.moonshot.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Kimi API错误: {response.status_code}")
    
    def chat(self, prompt: str, system_prompt: str = "") -> str:
        """对话"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return self._call(messages)


class GradSchoolRAGPro:
    """考研择校问答系统专业版"""
    
    SYSTEM_PROMPT = """你是一个专业、热情的考研咨询顾问，名为"小智"。

你的职责：
1. 根据用户的情况推荐合适的院校和专业
2. 解答考研相关问题（科目、分数线、学硕专硕区别等）
3. 提供备考建议

回答原则：
- 专业、准确、有条理
- 结合用户具体情况给出个性化建议
- 推荐院校时要给出具体数据支撑
- 如果不确定，诚实告知用户
- 使用友好的语气，像朋友聊天一样

你可以使用的参考信息在上下文中提供。如果上下文信息不足，使用你的知识来回答。"""
    
    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        api_key: Optional[str] = None,
        llm_provider: str = "zhipu"
    ):
        self.llm = None
        self.crawler = ChsiCrawler()
        self.df = self._load_school_data()
        self.qa_data = self._load_qa_data()
        self.vectorstore = None
        self.conversation_history: List[Dict] = []
        
        # 初始化大模型
        if api_key:
            config = llm_config or LLMConfig(
                provider=llm_provider,
                api_key=api_key
            )
            self.llm = LLMWrapper(config)
        
        # 初始化向量数据库（如果LangChain可用）
        if LANGCHAIN_AVAILABLE:
            self._init_vectorstore()
    
    def _load_school_data(self) -> pd.DataFrame:
        """加载院校数据"""
        try:
            return pd.read_csv("./data/schools_data.csv")
        except:
            return pd.DataFrame()
    
    def _load_qa_data(self) -> List[Dict]:
        """加载问答数据"""
        try:
            with open("./data/grad_consult_qa.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _init_vectorstore(self):
        """初始化向量数据库"""
        try:
            # 使用BGE嵌入
            embeddings = HuggingFaceBgeEmbeddings(
                model_name="BAAI/bge-large-zh-v1.5",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # 构建文档
            documents = []
            
            # 添加院校数据
            for _, row in self.df.iterrows():
                text = f"{row['学校名称']}：位于{row['所在地']}，{row['层次']}，计算机学科评估{row.get('计算机学科评估', '无')}。"
                documents.append(Document(page_content=text))
            
            # 添加QA数据
            for qa in self.qa_data:
                text = f"问题：{qa['instruction']}\n回答：{qa['output']}"
                documents.append(Document(page_content=text))
            
            # 创建向量库
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory="./data/chroma_db_pro"
            )
        except Exception as e:
            print(f"向量数据库初始化失败: {e}")
    
    def search_online(self, query: str) -> Dict:
        """联网查询"""
        # 尝试从研招网获取数据
        result = {
            'query': query,
            'data': None,
            'source': '研招网',
            'timestamp': datetime.now().isoformat()
        }
        
        # 检测查询类型
        query_lower = query.lower()
        
        if any(kw in query for kw in ['学校', '院校', '大学']):
            # 查院校
            school_name = self._extract_school_name(query)
            if school_name:
                result['data'] = self.crawler.get_online_data('school_info', school_name=school_name)
        
        elif any(kw in query for kw in ['专业', '方向', '考什么']):
            # 查专业
            major = self._extract_major(query)
            if major:
                result['data'] = self.crawler.get_online_data('major_search', keyword=major)
        
        elif any(kw in query for kw in ['分数线', '分数']):
            # 查分数线
            result['data'] = {
                'info': '2024年计算机A类国家线: 310分',
                'details': '政治英语: 47分，业务课: 71分'
            }
        
        return result
    
    def _extract_school_name(self, query: str) -> Optional[str]:
        """提取学校名称"""
        schools = self.df['学校名称'].tolist() if not self.df.empty else []
        for school in schools:
            if school in query:
                return school
        return None
    
    def _extract_major(self, query: str) -> Optional[str]:
        """提取专业关键词"""
        majors = ['计算机', '软件', '人工智能', '电子', '自动化', '机械', '通信', '控制']
        for major in majors:
            if major in query:
                return major
        return None
    
    def build_context(self) -> str:
        """构建上下文"""
        context = "【参考信息】\n\n"
        
        # 院校信息
        if not self.df.empty:
            context += "📍 **院校信息**\n"
            top_schools = self.df.head(15)
            for _, row in top_schools.iterrows():
                context += f"- {row['学校名称']}: {row['层次']} | {row['所在地']} | 分数线{row.get('2024复试分数线', '暂无')}分\n"
            context += "\n"
        
        # 问答知识
        if self.qa_data:
            context += "💡 **常见问题解答**\n"
            for qa in self.qa_data[:10]:
                context += f"Q: {qa['instruction']}\n"
                context += f"A: {qa['output'][:150]}...\n\n"
        
        return context
    
    def query(
        self,
        question: str,
        use_online: bool = True,
        use_llm: bool = True
    ) -> Dict:
        """查询"""
        result = {
            'question': question,
            'answer': '',
            'sources': [],
            'online_data': None,
            'success': True,
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. 联网查询
        if use_online:
            result['online_data'] = self.search_online(question)
        
        # 2. 构建上下文
        context = self.build_context()
        
        # 3. 构建提示词
        prompt = f"""参考信息：
{context}

用户问题：{question}

请根据参考信息回答用户问题。如果参考信息不足，使用你的知识补充。回答要专业、有条理，并给出具体建议。"""
        
        # 4. 调用大模型
        if self.llm and use_llm:
            try:
                answer = self.llm.chat(prompt, self.SYSTEM_PROMPT)
                result['answer'] = answer
            except Exception as e:
                result['answer'] = self._fallback_answer(question)
                result['error'] = str(e)
        else:
            result['answer'] = self._fallback_answer(question)
        
        # 5. 添加来源
        if result['online_data'] and result['online_data'].get('data'):
            result['sources'].append('研招网')
        if self.qa_data:
            result['sources'].append('知识库')
        
        return result
    
    def _fallback_answer(self, question: str) -> str:
        """备用回复（无大模型时）"""
        # 检查知识库
        for qa in self.qa_data:
            keywords = [w for w in qa['instruction'] if len(w) >= 3]
            if any(kw in question.lower() for kw in keywords):
                return qa['output']
        
        # 检查院校数据
        school_name = self._extract_school_name(question)
        if school_name:
            row = self.df[self.df['学校名称'] == school_name].iloc[0]
            return f"""**{school_name}** 信息如下：

📍 位置: {row['所在地']} | 🎓 层次: {row['层次']}
📈 分数线: {row.get('2024复试分数线', '暂无')}分
👥 招生人数: {row.get('招生人数', '暂无')}人
📚 初试科目: {row.get('初试科目(英语)', '')} + {row.get('初试科目(数学)', '')} + {row.get('初试科目(专业课)', '')}

💡 备注: {row.get('备注', '')}"""
        
        return "抱歉，我需要更多信息来回答你的问题。请告诉我你的情况（专业偏好、分数、目标院校类型），我来帮你分析！"
    
    def get_recommendations(
        self,
        score: Optional[int] = None,
        level: str = "985",
        major: str = "计算机",
        location: Optional[str] = None
    ) -> List[Dict]:
        """获取院校推荐"""
        if self.df.empty:
            return []
        
        filtered = self.df.copy()
        
        # 筛选层次
        if level == "985":
            filtered = filtered[filtered['层次'] == '985']
        elif level == "211":
            filtered = filtered[filtered['层次'].isin(['985', '211'])]
        
        # 筛选分数
        if score:
            filtered = filtered[filtered['2024复试分数线'] <= score + 30]
        
        # 按性价比排序
        filtered = filtered.sort_values('计算机学科评估', ascending=False)
        
        recommendations = []
        for _, row in filtered.head(10).iterrows():
            recommendations.append({
                '学校': row['学校名称'],
                '位置': row['所在地'],
                '层次': row['层次'],
                '评估': row.get('计算机学科评估', '无'),
                '分数线': row.get('2024复试分数线', '暂无'),
                '招生': row.get('招生人数', '暂无'),
                '科目': f"{row.get('初试科目(英语)', '')} + {row.get('初试科目(数学)', '')}",
                '备注': row.get('备注', '')
            })
        
        return recommendations
    
    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []


def create_with_api_key(api_key: str, provider: str = "zhipu") -> GradSchoolRAGPro:
    """便捷创建函数"""
    return GradSchoolRAGPro(api_key=api_key, llm_provider=provider)


# 测试
if __name__ == "__main__":
    # 初始化（不需要API Key的测试）
    rag = GradSchoolRAGPro()
    
    # 测试查询
    result = rag.query("推荐计算机专业的985院校")
    print("查询结果:", result['answer'][:200])
