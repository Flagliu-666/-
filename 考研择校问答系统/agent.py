"""
考研择校智能问答系统 - Agent模块
负责任务规划、Skill调度、结果整合
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# 导入NLP模块
try:
    from nlp_tasks import NLPProcessor, IntentType, NLPResult
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    IntentType = None


# ==================== 数据结构定义 ====================

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """任务定义"""
    task_id: str
    skill_name: str                    # 调用的Skill名称
    params: Dict[str, Any] = field(default_factory=dict)  # Skill参数
    priority: int = 1                  # 优先级（数字越大优先级越高）
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None                 # 任务结果
    error: str = ""                    # 错误信息
    dependencies: List[str] = field(default_factory=list)  # 依赖任务


@dataclass
class TaskPlan:
    """任务规划结果"""
    tasks: List[Task] = field(default_factory=list)  # 任务列表
    main_intent: str = ""             # 主意图
    context_summary: str = ""         # 上下文摘要


@dataclass
class AgentResponse:
    """Agent响应"""
    answer: str                        # 最终回答
    sources: List[str] = field(default_factory=list)  # 数据来源
    skills_used: List[str] = field(default_factory=list)  # 使用的Skill
    task_plan: Optional[TaskPlan] = None  # 任务规划
    confidence: float = 0.0           # 回答置信度
    needs_human_confirm: bool = False  # 是否需要人工确认


# ==================== Skill注册表 ====================

class SkillRegistry:
    """
    Skill注册表
    管理所有可用的Skill
    """
    
    def __init__(self):
        """初始化Skill注册表"""
        self.skills: Dict[str, Any] = {}
        self._register_default_skills()
    
    def _register_default_skills(self):
        """注册默认Skills"""
        # 延迟导入避免循环依赖
        try:
            from skills import (
                SchoolQuerySkill, 
                SmartRecommendSkill, 
                PolicyExplainSkill,
                PreparationConsultSkill
            )
            
            self.register('school_query', SchoolQuerySkill())
            self.register('smart_recommend', SmartRecommendSkill())
            self.register('policy_explain', PolicyExplainSkill())
            self.register('preparation_consult', PreparationConsultSkill())
            self.register('answer_generator', AnswerGeneratorSkill())
            
        except ImportError:
            # 如果skills模块不存在，使用空注册
            pass
    
    def register(self, name: str, skill_instance: Any):
        """
        注册Skill
        
        Args:
            name: Skill名称
            skill_instance: Skill实例
        """
        self.skills[name] = skill_instance
    
    def get(self, name: str) -> Optional[Any]:
        """
        获取Skill
        
        Args:
            name: Skill名称
        
        Returns:
            Skill实例
        """
        return self.skills.get(name)
    
    def list_skills(self) -> List[str]:
        """列出所有Skill"""
        return list(self.skills.keys())
    
    def get_by_intent(self, intent: str) -> List[str]:
        """
        根据意图获取适合的Skill
        
        Args:
            intent: 意图类型
        
        Returns:
            Skill名称列表
        """
        intent_to_skills = {
            'school_query': ['school_query', 'answer_generator'],
            'school_recommend': ['smart_recommend', 'school_query', 'answer_generator'],
            'policy_explain': ['policy_explain', 'answer_generator'],
            'major_query': ['school_query', 'policy_explain', 'answer_generator'],
            'score_query': ['school_query', 'answer_generator'],
            'preparation': ['preparation_consult', 'answer_generator'],
            'greeting': ['answer_generator'],
            'thanks': ['answer_generator']
        }
        return intent_to_skills.get(intent, ['answer_generator'])


# ==================== 上下文管理器 ====================

class ContextManager:
    """
    上下文管理器
    管理多轮对话上下文，支持指代消解
    """
    
    def __init__(self, max_history: int = 10):
        """
        初始化上下文管理器
        
        Args:
            max_history: 最大保留历史轮数
        """
        self.conversation_history: List[Dict] = []
        self.mentioned_entities: Dict[str, Any] = {}
        self.current_topic: str = ""
        self.user_profile: Dict[str, Any] = {}
        self.max_history = max_history
    
    def update(self, user_input: str, assistant_output: str, 
               nlp_result: Optional[Any] = None,
               entities: Optional[Dict] = None):
        """
        更新上下文
        
        Args:
            user_input: 用户输入
            assistant_output: 助手回复
            nlp_result: NLP处理结果
            entities: 识别的实体
        """
        # 更新对话历史
        self.conversation_history.append({
            'user': user_input,
            'assistant': assistant_output,
            'timestamp': datetime.now().isoformat()
        })
        
        # 保持历史在限制内
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        # 更新实体
        if entities:
            for key, value in entities.items():
                if value is not None and value not in ['', [], {}]:
                    self.mentioned_entities[key] = value
        
        # 更新话题
        if nlp_result:
            self.current_topic = str(nlp_result.intent)
    
    def resolve_reference(self, text: str) -> str:
        """
        指代消解
        
        Args:
            text: 包含指代词的文本
        
        Returns:
            消解后的文本
        """
        reference_map = {
            '他们': self.mentioned_entities.get('school', '该校'),
            '它': self.mentioned_entities.get('school', '该校'),
            '这个学校': self.mentioned_entities.get('school', '该校'),
            '该校': self.mentioned_entities.get('school', '该校'),
            '这个专业': self.mentioned_entities.get('major', '该专业'),
        }
        
        resolved_text = text
        for ref, entity in reference_map.items():
            if ref in resolved_text:
                resolved_text = resolved_text.replace(ref, str(entity))
        
        return resolved_text
    
    def get_history_context(self, n_round: int = 3) -> str:
        """
        获取历史上下文摘要
        
        Args:
            n_round: 最近的n轮对话
        
        Returns:
            上下文摘要字符串
        """
        if not self.conversation_history:
            return ""
        
        recent = self.conversation_history[-n_round:] if len(self.conversation_history) >= n_round else self.conversation_history
        context_parts = []
        
        for i, turn in enumerate(recent):
            context_parts.append(f"[第{len(self.conversation_history)-n_round+i+1}轮]")
            context_parts.append(f"用户: {turn['user'][:50]}...")
            context_parts.append(f"助手: {turn['assistant'][:50]}...")
        
        return "\n".join(context_parts)
    
    def set_user_profile(self, profile: Dict[str, Any]):
        """
        设置用户画像
        
        Args:
            profile: 用户画像字典
        """
        self.user_profile.update(profile)
    
    def get_user_profile(self) -> Dict[str, Any]:
        """获取用户画像"""
        return self.user_profile.copy()


# ==================== 任务规划器 ====================

class TaskPlanner:
    """
    任务规划器
    根据意图生成任务计划
    """
    
    def __init__(self):
        """初始化任务规划器"""
        self._init_planning_rules()
    
    def _init_planning_rules(self):
        """初始化规划规则"""
        # 意图到任务的映射规则
        self.planning_rules = {
            'school_query': {
                'tasks': [
                    {'skill': 'school_query', 'priority': 2, 'params_template': {'query_type': 'info'}}
                ],
                'summary_template': '查询院校信息'
            },
            'school_recommend': {
                'tasks': [
                    {'skill': 'smart_recommend', 'priority': 3, 'params_template': {'recommend_type': 'by_profile'}},
                    {'skill': 'school_query', 'priority': 1, 'params_template': {'query_type': 'list'}}
                ],
                'summary_template': '智能推荐院校'
            },
            'policy_explain': {
                'tasks': [
                    {'skill': 'policy_explain', 'priority': 2, 'params_template': {}}
                ],
                'summary_template': '解读考研政策'
            },
            'major_query': {
                'tasks': [
                    {'skill': 'school_query', 'priority': 2, 'params_template': {'query_type': 'major'}},
                    {'skill': 'policy_explain', 'priority': 1, 'params_template': {'topic': 'major'}}
                ],
                'summary_template': '查询专业信息'
            },
            'score_query': {
                'tasks': [
                    {'skill': 'school_query', 'priority': 2, 'params_template': {'query_type': 'score'}}
                ],
                'summary_template': '查询分数线'
            },
            'preparation': {
                'tasks': [
                    {'skill': 'preparation_consult', 'priority': 2, 'params_template': {}}
                ],
                'summary_template': '备考咨询'
            },
            'greeting': {
                'tasks': [],
                'summary_template': '问候'
            },
            'thanks': {
                'tasks': [],
                'summary_template': '感谢'
            },
            'unknown': {
                'tasks': [
                    {'skill': 'answer_generator', 'priority': 1, 'params_template': {}}
                ],
                'summary_template': '通用回答'
            }
        }
    
    def plan(self, nlp_result: Any, 
             user_profile: Dict[str, Any],
             entities: Dict[str, Any]) -> TaskPlan:
        """
        生成任务计划
        
        Args:
            nlp_result: NLP处理结果
            user_profile: 用户画像
            entities: 识别的实体
        
        Returns:
            TaskPlan对象
        """
        # 获取意图
        intent = str(nlp_result.intent)
        
        # 获取规划规则
        rule = self.planning_rules.get(intent, self.planning_rules['unknown'])
        
        # 生成任务
        tasks = []
        for task_def in rule['tasks']:
            task = Task(
                task_id=f"task_{len(tasks) + 1}",
                skill_name=task_def['skill'],
                priority=task_def['priority'],
                params=self._fill_params(task_def['params_template'], entities, user_profile, nlp_result)
            )
            tasks.append(task)
        
        # 按优先级排序
        tasks.sort(key=lambda x: x.priority, reverse=True)
        
        return TaskPlan(
            tasks=tasks,
            main_intent=intent,
            context_summary=rule['summary_template']
        )
    
    def _fill_params(self, template: Dict, entities: Dict, 
                     user_profile: Dict, nlp_result: Any) -> Dict[str, Any]:
        """
        填充参数模板
        
        Args:
            template: 参数模板
            entities: 实体
            user_profile: 用户画像
            nlp_result: NLP结果
        
        Returns:
            填充后的参数
        """
        params = template.copy()
        
        # 合并实体
        if entities:
            params.update({k: v for k, v in entities.items() if v})
        
        # 合并用户画像
        params['user_profile'] = user_profile
        
        # 添加NLP结果
        params['keywords'] = getattr(nlp_result, 'keywords', {})
        params['original_text'] = nlp_result.original_text
        
        return params


# ==================== Skill执行器 ====================

class SkillExecutor:
    """
    Skill执行器
    负责执行Skill并整合结果
    """
    
    def __init__(self, skill_registry: SkillRegistry):
        """
        初始化Skill执行器
        
        Args:
            skill_registry: Skill注册表
        """
        self.registry = skill_registry
    
    def execute(self, task: Task) -> Any:
        """
        执行任务
        
        Args:
            task: Task对象
        
        Returns:
            执行结果
        """
        skill = self.registry.get(task.skill_name)
        
        if skill is None:
            return {
                'success': False,
                'error': f"Skill '{task.skill_name}' not found"
            }
        
        try:
            # 验证参数
            if hasattr(skill, 'validate') and not skill.validate(task.params):
                return {
                    'success': False,
                    'error': "Invalid parameters"
                }
            
            # 执行Skill
            if hasattr(skill, 'execute'):
                result = skill.execute(task.params)
                return result
            else:
                return {
                    'success': False,
                    'error': "Skill has no execute method"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_plan(self, plan: TaskPlan) -> List[Any]:
        """
        执行任务计划
        
        Args:
            plan: TaskPlan对象
        
        Returns:
            所有任务的结果列表
        """
        results = []
        
        for task in plan.tasks:
            # 检查依赖是否完成
            deps_satisfied = all(
                results[i].get('success', False) 
                for i, t in enumerate(plan.tasks[:len(results)]) 
                if t.task_id in task.dependencies
            )
            
            if not deps_satisfied:
                task.status = TaskStatus.FAILED
                task.error = "Dependencies not satisfied"
                results.append({'success': False, 'error': task.error})
                continue
            
            # 执行任务
            task.status = TaskStatus.RUNNING
            result = self.execute(task)
            results.append(result)
            
            if result.get('success', False):
                task.status = TaskStatus.COMPLETED
                task.result = result
            else:
                task.status = TaskStatus.FAILED
                task.error = result.get('error', 'Unknown error')
        
        return results


# ==================== Agent主类 ====================

class GradSchoolAgent:
    """
    考研择校智能问答Agent
    整合NLP、任务规划、Skill调度
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化Agent
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 初始化组件
        self.nlp_processor = NLPProcessor() if NLP_AVAILABLE else None
        self.context_manager = ContextManager()
        self.skill_registry = SkillRegistry()
        self.task_planner = TaskPlanner()
        self.skill_executor = SkillExecutor(self.skill_registry)
        
        # 加载数据
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        try:
            self.df = pd.read_csv("./data/schools_data.csv")
        except:
            self.df = pd.DataFrame()
        
        try:
            with open("./data/grad_consult_qa.json", 'r', encoding='utf-8') as f:
                self.qa_data = json.load(f)
        except:
            self.qa_data = []
    
    def process(self, user_input: str, 
                user_profile: Optional[Dict] = None,
                use_online: bool = True) -> AgentResponse:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
            user_profile: 用户画像
            use_online: 是否使用联网查询
        
        Returns:
            AgentResponse对象
        """
        # 0. 处理指代
        resolved_input = self.context_manager.resolve_reference(user_input)
        
        # 1. NLP处理
        nlp_result = self._process_nlp(resolved_input)
        
        # 2. 更新上下文
        if user_profile:
            self.context_manager.set_user_profile(user_profile)
        
        # 3. 任务规划
        task_plan = self.task_planner.plan(
            nlp_result,
            self.context_manager.get_user_profile(),
            nlp_result.entities
        )
        
        # 4. 执行任务
        task_results = self.skill_executor.execute_plan(task_plan)
        
        # 5. 整合结果
        response = self._integrate_results(
            resolved_input,
            task_plan,
            task_results,
            nlp_result
        )
        
        # 6. 更新上下文
        self.context_manager.update(
            user_input,
            response.answer,
            nlp_result,
            nlp_result.entities
        )
        
        return response
    
    def _process_nlp(self, text: str) -> Any:
        """
        NLP处理
        
        Args:
            text: 输入文本
        
        Returns:
            NLPResult对象
        """
        if self.nlp_processor:
            return self.nlp_processor.process(text)
        else:
            # 简单的后备实现
            return NLPResult(
                original_text=text,
                tokens=text.split(),
                intent=IntentType.UNKNOWN if IntentType else "unknown",
                intent_confidence=0.0
            )
    
    def _integrate_results(self, user_input: str,
                          task_plan: TaskPlan,
                          task_results: List[Any],
                          nlp_result: Any) -> AgentResponse:
        """
        整合结果
        
        Args:
            user_input: 用户输入
            task_plan: 任务计划
            task_results: 任务结果
            nlp_result: NLP结果
        
        Returns:
            AgentResponse对象
        """
        # 收集所有结果
        all_results = []
        sources = []
        skills_used = []
        
        for task, result in zip(task_plan.tasks, task_results):
            skills_used.append(task.skill_name)
            
            if result.get('success', False):
                if 'data' in result:
                    all_results.append(result['data'])
                elif 'answer' in result:
                    all_results.append(result['answer'])
                if 'source' in result:
                    sources.append(result['source'])
        
        # 构建回答
        answer = self._build_answer(user_input, all_results, nlp_result)
        
        # 计算置信度
        success_count = sum(1 for r in task_results if r.get('success', False))
        confidence = success_count / len(task_results) if task_results else 0.5
        
        return AgentResponse(
            answer=answer,
            sources=sources,
            skills_used=skills_used,
            task_plan=task_plan,
            confidence=confidence
        )
    
    def _build_answer(self, user_input: str, 
                     results: List[Any],
                     nlp_result: Any) -> str:
        """
        构建回答
        
        Args:
            user_input: 用户输入
            results: 结果列表
            nlp_result: NLP结果
        
        Returns:
            回答文本
        """
        if not results:
            return "抱歉，我暂时无法回答您的问题，请换个方式提问。"
        
        # 如果有文本结果
        text_results = [r for r in results if isinstance(r, str)]
        if text_results:
            return text_results[0]
        
        # 如果有结构化结果
        return self._format_structured_results(results)
    
    def _format_structured_results(self, results: List[Any]) -> str:
        """
        格式化结构化结果
        
        Args:
            results: 结构化结果列表
        
        Returns:
            格式化文本
        """
        output_parts = []
        
        for result in results:
            if isinstance(result, dict):
                if 'schools' in result:
                    output_parts.append("以下是推荐的院校：")
                    for school in result['schools'][:5]:
                        output_parts.append(f"- {school}")
                elif 'info' in result:
                    output_parts.append(result['info'])
        
        return "\n".join(output_parts) if output_parts else "信息已获取"
    
    def reset(self):
        """重置Agent状态"""
        self.context_manager = ContextManager()
    
    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        return self.context_manager.get_history_context()


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 测试Agent
    print("=" * 60)
    print("Agent模块测试")
    print("=" * 60)
    
    # 创建Agent
    agent = GradSchoolAgent()
    
    # 测试用例
    test_cases = [
        "推荐一个性价比高的985院校，我预估350分",
        "东北大学考什么科目？",
        "学硕和专硕有什么区别？",
        "你好，我想咨询考研的问题"
    ]
    
    for text in test_cases:
        print(f"\n用户: {text}")
        response = agent.process(text, user_profile={'score': 350})
        print(f"助手: {response.answer[:100]}...")
        print(f"使用Skill: {response.skills_used}")
        print(f"置信度: {response.confidence:.2f}")
        print("-" * 60)
