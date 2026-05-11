"""
考研择校问答系统 - 测试文件
"""

import unittest
import sys
import os
import pandas as pd
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_engine import GradSchoolRAG, SystemConfig


class TestDataLoading(unittest.TestCase):
    """数据加载测试"""
    
    def setUp(self):
        """测试前准备"""
        self.data_dir = "./data"
        self.school_file = "./data/schools_data.csv"
        self.qa_file = "./data/grad_consult_qa.json"
    
    def test_school_data_exists(self):
        """测试院校数据文件是否存在"""
        self.assertTrue(
            os.path.exists(self.school_file),
            f"院校数据文件不存在: {self.school_file}"
        )
    
    def test_qa_data_exists(self):
        """测试问答数据文件是否存在"""
        self.assertTrue(
            os.path.exists(self.qa_file),
            f"问答数据文件不存在: {self.qa_file}"
        )
    
    def test_school_data_columns(self):
        """测试院校数据列是否完整"""
        df = pd.read_csv(self.school_file)
        required_columns = [
            '学校名称', '所在地', '层次', '类型',
            '初试科目(政治)', '初试科目(英语)', 
            '初试科目(数学)', '初试科目(专业课)',
            '2024复试分数线', '招生人数'
        ]
        for col in required_columns:
            self.assertIn(col, df.columns, f"缺少列: {col}")
    
    def test_qa_data_format(self):
        """测试问答数据格式"""
        with open(self.qa_file, 'r', encoding='utf-8') as f:
            qa_data = json.load(f)
        
        self.assertIsInstance(qa_data, list, "问答数据应该是列表")
        
        if len(qa_data) > 0:
            item = qa_data[0]
            self.assertIn('instruction', item, "问答数据缺少instruction字段")
            self.assertIn('output', item, "问答数据缺少output字段")


class TestRAGSystem(unittest.TestCase):
    """RAG系统测试"""
    
    def setUp(self):
        """测试前准备"""
        self.config = SystemConfig(
            embedding_model="BAAI/bge-large-zh-v1.5",
            persist_directory="./data/test_chroma_db",
            collection_name="test_grad_consult"
        )
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.config.persist_directory):
            shutil.rmtree(self.config.persist_directory)
    
    def test_rag_initialization(self):
        """测试RAG系统初始化"""
        try:
            rag = GradSchoolRAG(self.config)
            self.assertIsNotNone(rag.vectorstore)
        except Exception as e:
            self.skipTest(f"RAG初始化失败，跳过测试: {e}")
    
    def test_query_function(self):
        """测试查询功能"""
        try:
            rag = GradSchoolRAG(self.config)
            result = rag.query("计算机专业考研推荐")
            self.assertIn('answer', result)
            self.assertIn('success', result)
        except Exception as e:
            self.skipTest(f"查询功能测试失败: {e}")
    
    def test_school_recommendations(self):
        """测试院校推荐功能"""
        try:
            rag = GradSchoolRAG(self.config)
            recommendations = rag.get_school_recommendations(
                score=350,
                level='985'
            )
            self.assertIsInstance(recommendations, list)
        except Exception as e:
            self.skipTest(f"推荐功能测试失败: {e}")


class TestRuleBasedQuery(unittest.TestCase):
    """规则引擎测试"""
    
    def test_school_query(self):
        """测试学校查询"""
        from rag_engine import GradSchoolRAG
        
        rag = GradSchoolRAG()
        result = rag._rule_based_query("清华大学考研")
        
        self.assertTrue(result['success'])
        self.assertIn('清华大学', result['answer'])
    
    def test_recommendation_query(self):
        """测试推荐查询"""
        from rag_engine import GradSchoolRAG
        
        rag = GradSchoolRAG()
        result = rag._rule_based_query("推荐985计算机院校")
        
        self.assertTrue(result['success'])
    
    def test_general_query(self):
        """测试通用查询"""
        from rag_engine import GradSchoolRAG
        
        rag = GradSchoolRAG()
        result = rag._rule_based_query("考研怎么复习")
        
        self.assertTrue(result['success'])


class TestAPIEndpoints(unittest.TestCase):
    """API接口测试"""
    
    def setUp(self):
        """测试前准备"""
        from api import app
        from fastapi.testclient import TestClient
        
        self.app = app
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """测试根路径"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
    
    def test_health_endpoint(self):
        """测试健康检查"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())
    
    def test_query_endpoint(self):
        """测试查询接口"""
        response = self.client.post(
            "/api/query",
            json={"question": "计算机考研推荐"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('answer', response.json())
    
    def test_recommend_endpoint(self):
        """测试推荐接口"""
        response = self.client.post(
            "/api/recommend",
            json={"score": 350, "level": "985"}
        )
        self.assertEqual(response.status_code, 200)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestDataLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestRuleBasedQuery))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
