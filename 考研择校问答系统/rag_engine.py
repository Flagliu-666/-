"""
考研择校问答系统 - 核心RAG引擎
基于LangChain + ChromaDB + Sentence Transformers
"""

import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# LangChain 组件
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

# 配置类
@dataclass
class SystemConfig:
    """系统配置"""
    embedding_model: str = "BAAI/bge-large-zh-v1.5"
    persist_directory: str = "./data/chroma_db"
    collection_name: str = "grad_consult"
    chunksize: int = 500
    chunkoverlap: int = 50
    top_k: int = 5

class GradSchoolRAG:
    """考研择校RAG系统"""
    
    def __init__(self, config: Optional[SystemConfig] = None):
        self.config = config or SystemConfig()
        self.vectorstore = None
        self.qa_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            return_messages=True
        )
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化组件"""
        print("🚀 初始化考研择校问答系统...")
        
        # 初始化嵌入模型
        print("📦 加载嵌入模型...")
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=self.config.embedding_model,
            model_kwargs={'device': 'cuda' if self._check_cuda() else 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 初始化向量数据库
        self._init_vectorstore()
        
        # 初始化对话链
        self._init_qa_chain()
        
        print("✅ 系统初始化完成!")
    
    def _check_cuda(self) -> bool:
        """检查CUDA是否可用"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def _init_vectorstore(self):
        """初始化向量数据库"""
        if os.path.exists(self.config.persist_directory):
            print("📂 加载已有向量数据库...")
            self.vectorstore = Chroma(
                persist_directory=self.config.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.config.collection_name
            )
        else:
            print("📚 创建新的向量数据库...")
            self._build_vectorstore()
    
    def _init_qa_chain(self):
        """初始化问答链"""
        # 自定义提示模板
        template = """你是一个专业的考研择校咨询顾问，名为"考研助手小智"。

根据提供的上下文信息，结合你的考研知识，帮助用户解答以下问题。

请注意：
1. 如果上下文中没有相关信息，使用你的知识来回答
2. 回答要专业、友好、有条理
3. 如果不确定，给出合理的建议
4. 结合用户具体情况给出个性化建议
5. 推荐学校时要给出具体的数据支撑

当前对话历史：
{chat_history}

上下文信息：
{context}

用户问题：{question}

请给出专业的回答："""

        PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"]
        )
        
        # 创建对话检索链
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self._get_llm(),
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": self.config.top_k}
            ),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": PROMPT},
            return_source_documents=True,
            verbose=True
        )
    
    def _get_llm(self):
        """获取LLM模型（支持Ollama或本地模型）"""
        try:
            from langchain_community.llms import Ollama
            return Ollama(model="qwen2.5:7b", base_url="http://localhost:11434")
        except:
            # 如果没有Ollama，返回一个模拟LLM
            print("⚠️ 未检测到Ollama，将使用规则引擎模式")
            return None
    
    def _build_vectorstore(self):
        """构建向量数据库"""
        documents = []
        
        # 1. 加载问答数据
        print("📖 加载问答数据...")
        qa_file = "./data/grad_consult_qa.json"
        if os.path.exists(qa_file):
            with open(qa_file, 'r', encoding='utf-8') as f:
                qa_data = json.load(f)
            for item in qa_data:
                text = f"问题：{item['instruction']}\n回答：{item['output']}"
                documents.append(Document(
                    page_content=text,
                    metadata={"source": "qa_knowledge_base", "type": "qa"}
                ))
        
        # 2. 加载院校数据
        print("📊 加载院校数据...")
        school_file = "./data/schools_data.csv"
        if os.path.exists(school_file):
            df = pd.read_csv(school_file)
            for _, row in df.iterrows():
                text = self._format_school_info(row)
                documents.append(Document(
                    page_content=text,
                    metadata={"source": "school_database", "type": "school", "school": row.get('学校名称', '')}
                ))
        
        # 3. 文本分割
        print("✂️ 文本分割...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunksize,
            chunk_overlap=self.config.chunkoverlap,
            separators=["\n\n", "\n", "。", "！", "？", "，"]
        )
        split_docs = text_splitter.split_documents(documents)
        print(f"   生成 {len(split_docs)} 个文本块")
        
        # 4. 创建向量数据库
        print("🔢 生成向量嵌入...")
        os.makedirs(self.config.persist_directory, exist_ok=True)
        self.vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            persist_directory=self.config.persist_directory,
            collection_name=self.config.collection_name
        )
        self.vectorstore.persist()
        print("   向量数据库已保存")
    
    def _format_school_info(self, row: pd.Series) -> str:
        """格式化院校信息"""
        info_parts = []
        
        school_name = row.get('学校名称', '')
        if pd.notna(school_name):
            info_parts.append(f"学校：{school_name}")
        
        # 基本信息
        basic_info = [
            ('所在地', 'location'),
            ('层次', 'level'),
            ('类型', 'type'),
            ('计算机学科评估', 'cs_rank'),
            ('软件工程评估', 'se_rank'),
        ]
        
        for label, key in basic_info:
            if key in row.index and pd.notna(row.get(key)):
                info_parts.append(f"{label}：{row.get(key)}")
        
        # 初试科目
        subjects = []
        for sub in ['初试科目(政治)', '初试科目(英语)', '初试科目(数学)', '初试科目(专业课)']:
            if sub in row.index and pd.notna(row.get(sub)):
                subjects.append(row.get(sub))
        if subjects:
            info_parts.append(f"初试科目：{' | '.join(subjects)}")
        
        # 分数线和招生
        if pd.notna(row.get('2024复试分数线')):
            info_parts.append(f"2024复试分数线：{row.get('2024复试分数线')}分")
        if pd.notna(row.get('招生人数')):
            info_parts.append(f"招生人数：约{row.get('招生人数')}人")
        if pd.notna(row.get('学制')):
            info_parts.append(f"学制：{row.get('学制')}")
        if pd.notna(row.get('备注')):
            info_parts.append(f"备注：{row.get('备注')}")
        
        return "，".join(info_parts)
    
    def query(self, question: str) -> Dict:
        """查询"""
        if self.qa_chain is None:
            return self._rule_based_query(question)
        
        try:
            result = self.qa_chain({"question": question})
            return {
                "answer": result["answer"],
                "source_documents": [doc.page_content for doc in result.get("source_documents", [])],
                "success": True
            }
        except Exception as e:
            print(f"查询出错: {e}")
            return self._rule_based_query(question)
    
    def _rule_based_query(self, question: str) -> Dict:
        """基于规则的查询（备用方案）"""
        # 加载数据
        school_file = "./data/schools_data.csv"
        qa_file = "./data/grad_consult_qa.json"
        
        df = pd.read_csv(school_file)
        with open(qa_file, 'r', encoding='utf-8') as f:
            qa_data = json.load(f)
        
        # 关键词匹配
        question_lower = question.lower()
        results = {"answer": "", "source_documents": [], "success": True}
        
        # 1. 检查是否询问特定学校
        for school in df['学校名称'].values:
            if school in question:
                row = df[df['学校名称'] == school].iloc[0]
                answer = self._format_school_info(row)
                results["answer"] = answer
                results["source_documents"].append(answer)
                return results
        
        # 2. 检查是否是择校推荐问题
        if any(kw in question for kw in ['推荐', '选择', '考研', '择校']):
            # 根据分数推荐
            score_keywords = ['分数', '分', '分数线']
            level_keywords = ['985', '211', '双非', '普通']
            
            for idx, row in df.iterrows():
                if row.get('层次') == '985' and row.get('计算机学科评估') in ['A+', 'A', 'A-']:
                    results["source_documents"].append(self._format_school_info(row))
            
            if results["source_documents"]:
                results["answer"] = "根据你的需求，我为你推荐以下高性价比的985院校：\n\n" + "\n\n".join([
                    f"{i+1}. {doc}" for i, doc in enumerate(results["source_documents"][:5])
                ])
                return results
        
        # 3. 返回通用回答
        results["answer"] = "我需要更多信息来帮你。请告诉我：\n1. 你的本科背景是什么？\n2. 你的目标分数是多少？\n3. 你想考什么专业方向？"
        return results
    
    def get_school_recommendations(
        self,
        score: Optional[int] = None,
        level: Optional[str] = None,
        major: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[Dict]:
        """获取院校推荐"""
        df = pd.read_csv("./data/schools_data.csv")
        
        filtered = df.copy()
        
        # 按分数筛选
        if score:
            # 假设分数线正态分布，这里筛选出分数线低于分数+20的院校
            filtered = filtered[filtered['2024复试分数线'] <= score + 30]
            filtered = filtered.sort_values('2024复试分数线', ascending=False)
        
        # 按层次筛选
        if level:
            if '985' in level:
                filtered = filtered[filtered['层次'] == '985']
            elif '211' in level:
                filtered = filtered[filtered['层次'] == '211']
        
        # 按地区筛选
        if location:
            filtered = filtered[filtered['所在地'].str.contains(location, na=False)]
        
        # 返回推荐结果
        recommendations = []
        for _, row in filtered.head(10).iterrows():
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
        
        return recommendations
    
    def clear_memory(self):
        """清除对话历史"""
        self.memory.clear()
    
    def get_chat_history(self) -> List:
        """获取对话历史"""
        return self.memory.load_memory_variables({}).get('chat_history', [])


def main():
    """测试函数"""
    print("=" * 60)
    print("🎓 考研择校智能问答系统")
    print("=" * 60)
    
    # 初始化系统
    rag = GradSchoolRAG()
    
    # 示例对话
    test_questions = [
        "我想考计算机专业，数学一般，有什么学校推荐？",
        "东北大学考研难不难？",
        "408和自命题有什么区别？"
    ]
    
    print("\n📝 测试问答:")
    for q in test_questions:
        print(f"\n❓ 用户: {q}")
        result = rag.query(q)
        print(f"🤖 助手: {result['answer'][:200]}...")
        print("-" * 40)


if __name__ == "__main__":
    main()
