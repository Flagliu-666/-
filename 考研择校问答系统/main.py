"""
考研择校问答系统 - 主程序入口
统一运行整个系统的所有功能
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ==================== 核心模块导入 ====================
from data_loader import DataLoader, QAGenerator
from model_optimizer import ModelTrainer, ModelEvaluator, SelfImprover

# 爬虫管理器（可选导入）
CrawlerManager = None

# ==================== 配置文件 ====================
CONFIG = {
    "name": "考研择校问答系统",
    "version": "2.0.0",
    "author": "AI Assistant",
    "description": "基于大语言模型的考研择校智能问答系统"
}


class GraduateSchoolSystem:
    """考研择校问答系统主类"""
    
    def __init__(self, data_dir: str = None):
        """初始化系统"""
        self.project_root = Path(__file__).parent
        self.data_dir = data_dir or str(self.project_root / "data")
        
        print("=" * 60)
        print(f"[SYSTEM] {CONFIG['name']} v{CONFIG['version']}")
        print("=" * 60)
        print()
        
        # 初始化各模块
        self.data_loader = None
        self.qa_generator = None
        self.model_trainer = None
        
        # 加载数据
        self._load_data()
    
    def _load_data(self):
        """加载所有数据"""
        print("[INFO] Loading data...")
        try:
            self.data_loader = DataLoader(self.data_dir)
            self.data_loader.load_all()
            
            print(f"[OK] Data loaded!")
            print(f"     Schools: {len(self.data_loader.schools)}")
            print(f"     QA Data: {len(self.data_loader.qa_data)}")
            print(f"     Disciplines: {len(self.data_loader.discipline_data)}")
            print()
        except Exception as e:
            print(f"[WARNING] Data loading warning: {e}")
            print()
    
    def initialize_modules(self):
        """初始化所有模块"""
        print("[INFO] Initializing modules...")
        
        # 初始化问答生成器
        self.qa_generator = QAGenerator(self.data_loader)
        
        print("[OK] Modules initialized!")
        print()
    
    def chat(self):
        """启动交互式对话"""
        self.initialize_modules()
        
        print("=" * 60)
        print("[CHAT] Entering chat mode (type 'quit' to exit)")
        print("=" * 60)
        print()
        
        while True:
            try:
                user_input = input("\n[YOU] ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n[BYE] Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # 生成回答
                response = self.qa_generator.generate_response(user_input)
                
                print(f"\n[BOT] {response}")
                
            except KeyboardInterrupt:
                print("\n\n[BYE] Goodbye!")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}")
    
    def ask(self, question: str) -> str:
        """单次问答接口"""
        if not self.qa_generator:
            self.initialize_modules()
        return self.qa_generator.generate_response(question)
    
    def get_school_info(self, school_name: str) -> dict:
        """获取院校信息"""
        return self.data_loader.get_school(school_name) or {}
    
    def get_discipline_info(self, discipline_name: str) -> dict:
        """获取学科信息"""
        return self.data_loader.get_discipline(discipline_name) or {}
    
    def get_score_info(self, year: int = 2024) -> dict:
        """获取分数线"""
        return self.data_loader.get_scores(year)


# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description="Graduate School Selection Q&A System"
    )
    parser.add_argument(
        '--mode', '-m',
        choices=['chat', 'train'],
        default='chat',
        help='Mode: chat or train'
    )
    parser.add_argument(
        '--question', '-q',
        type=str,
        help='Direct question (non-interactive mode)'
    )
    parser.add_argument(
        '--data-dir', '-d',
        type=str,
        default=None,
        help='Data directory path'
    )
    
    args = parser.parse_args()
    
    # 创建系统实例
    system = GraduateSchoolSystem(data_dir=args.data_dir)
    
    if args.mode == 'chat':
        if args.question:
            # 单次问答模式
            response = system.ask(args.question)
            print(f"\n[BOT] {response}")
        else:
            # 交互式对话模式
            system.chat()
    
    elif args.mode == 'train':
        print("\n[TRAIN] Starting training...")
        system.initialize_modules()
        trainer = ModelTrainer(system.data_loader)
        print("\n[TRAIN] Training completed!")


if __name__ == "__main__":
    main()
