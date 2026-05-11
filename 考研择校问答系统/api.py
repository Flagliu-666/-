"""
考研择校问答系统 - FastAPI接口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_engine import GradSchoolRAG, SystemConfig

# 创建FastAPI应用
app = FastAPI(
    title="考研择校智能问答系统API",
    description="基于RAG的智能考研咨询接口",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
rag_system = None


class QueryRequest(BaseModel):
    """查询请求"""
    question: str
    session_id: Optional[str] = None


class RecommendationRequest(BaseModel):
    """推荐请求"""
    score: Optional[int] = None
    level: Optional[str] = None
    major: Optional[str] = None
    location: Optional[str] = None


class SchoolInfo(BaseModel):
    """学校信息"""
    学校名称: str
    所在地: str
    层次: str
    学科评估: str
    分数线: str
    招生人数: str
    初试科目: str
    学制: str
    备注: str


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    global rag_system
    print("🚀 初始化RAG系统...")
    try:
        config = SystemConfig(
            embedding_model="BAAI/bge-large-zh-v1.5",
            persist_directory="./data/chroma_db",
            collection_name="grad_consult"
        )
        rag_system = GradSchoolRAG(config)
        print("✅ RAG系统初始化完成")
    except Exception as e:
        print(f"⚠️ RAG系统初始化失败: {e}")
        print("   将使用规则引擎模式")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "考研择校智能问答系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "rag_system": rag_system is not None
    }


@app.post("/api/query")
async def query(request: QueryRequest):
    """问答接口"""
    try:
        if rag_system:
            result = rag_system.query(request.question)
            return {
                "success": True,
                "answer": result["answer"],
                "sources": result.get("source_documents", [])
            }
        else:
            # 使用规则引擎
            from app import generate_rule_based_response
            answer = generate_rule_based_response(request.question)
            return {
                "success": True,
                "answer": answer,
                "sources": []
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recommend", response_model=List[SchoolInfo])
async def recommend(request: RecommendationRequest):
    """院校推荐接口"""
    try:
        if rag_system:
            recommendations = rag_system.get_school_recommendations(
                score=request.score,
                level=request.level,
                major=request.major,
                location=request.location
            )
            return recommendations
        else:
            from app import get_recommendations
            return get_recommendations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schools")
async def get_all_schools():
    """获取所有学校信息"""
    try:
        import pandas as pd
        df = pd.read_csv("./data/schools_data.csv")
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schools/{school_name}")
async def get_school(school_name: str):
    """获取特定学校信息"""
    try:
        import pandas as pd
        df = pd.read_csv("./data/schools_data.csv")
        school = df[df['学校名称'].str.contains(school_name, na=False)]
        if school.empty:
            raise HTTPException(status_code=404, detail="学校未找到")
        return school.iloc[0].to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/clear")
async def clear_chat(session_id: str):
    """清除对话历史"""
    if rag_system:
        rag_system.clear_memory()
    return {"message": "对话已清除"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
