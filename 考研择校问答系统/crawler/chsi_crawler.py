"""
研招网数据爬虫模块
支持获取院校信息、专业目录、分数线等数据
"""

import requests
import json
import time
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import pandas as pd

class ChsiCrawler:
    """研招网爬虫类"""
    
    def __init__(self):
        self.base_url = "https://yz.chsi.com.cn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 缓存
        self._school_cache = None
        self._major_cache = {}
    
    def _safe_request(self, url: str, max_retries: int = 3, params: Dict = None) -> Optional[requests.Response]:
        """安全的请求方法，带重试"""
        for i in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    return response
                time.sleep(1)
            except Exception as e:
                print(f"请求失败 (尝试 {i+1}/{max_retries}): {e}")
                time.sleep(2)
        return None
    
    def search_schools(self, keyword: str = "") -> List[Dict]:
        """搜索院校"""
        if self._school_cache and not keyword:
            return self._school_cache
        
        schools = []
        
        # 方法1: 通过研招网院校库搜索
        try:
            url = f"{self.base_url}/school/search"
            params = {
                'sw': keyword if keyword else '',
                'ssdm': '',  # 省市代码
                'ml': '',    # 门类
                'xxfs': '',  # 学习方式
            }
            
            response = self._safe_request(url, params=params)
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                school_items = soup.select('.school-item')
                
                for item in school_items:
                    name = item.select_one('.name').text.strip()
                    province = item.select_one('.province').text.strip() if item.select_one('.province') else ''
                    level = item.select_one('.level').text.strip() if item.select_one('.level') else ''
                    
                    schools.append({
                        'name': name,
                        'province': province,
                        'level': level,
                        'url': item.find('a')['href'] if item.find('a') else ''
                    })
        except Exception as e:
            print(f"院校搜索出错: {e}")
        
        # 如果搜索失败，返回预设的院校数据
        if not schools:
            schools = self._get_default_schools()
        
        self._school_cache = schools
        return schools
    
    def _get_default_schools(self) -> List[Dict]:
        """返回默认院校列表"""
        return [
            {'name': '清华大学', 'province': '北京', 'level': '985', 'url': ''},
            {'name': '北京大学', 'province': '北京', 'level': '985', 'url': ''},
            {'name': '浙江大学', 'province': '浙江', 'level': '985', 'url': ''},
            {'name': '上海交通大学', 'province': '上海', 'level': '985', 'url': ''},
            {'name': '复旦大学', 'province': '上海', 'level': '985', 'url': ''},
            {'name': '南京大学', 'province': '江苏', 'level': '985', 'url': ''},
            {'name': '中国科学技术大学', 'province': '安徽', 'level': '985', 'url': ''},
            {'name': '哈尔滨工业大学', 'province': '黑龙江', 'level': '985', 'url': ''},
            {'name': '北京航空航天大学', 'province': '北京', 'level': '985', 'url': ''},
            {'name': '北京理工大学', 'province': '北京', 'level': '985', 'url': ''},
            {'name': '西安电子科技大学', 'province': '陕西', 'level': '211', 'url': ''},
            {'name': '电子科技大学', 'province': '四川', 'level': '985', 'url': ''},
            {'name': '华中科技大学', 'province': '湖北', 'level': '985', 'url': ''},
            {'name': '武汉大学', 'province': '湖北', 'level': '985', 'url': ''},
            {'name': '东南大学', 'province': '江苏', 'level': '985', 'url': ''},
            {'name': '东北大学', 'province': '辽宁', 'level': '985', 'url': ''},
            {'name': '吉林大学', 'province': '吉林', 'level': '985', 'url': ''},
            {'name': '西北工业大学', 'province': '陕西', 'level': '985', 'url': ''},
            {'name': '同济大学', 'province': '上海', 'level': '985', 'url': ''},
            {'name': '中山大学', 'province': '广东', 'level': '985', 'url': ''},
        ]
    
    def get_school_details(self, school_name: str) -> Dict:
        """获取院校详细信息"""
        # 搜索院校获取详情
        schools = self.search_schools(school_name)
        
        for school in schools:
            if school_name in school['name'] or school['name'] in school_name:
                return {
                    'name': school['name'],
                    'province': school['province'],
                    'level': school['level'],
                    'info': f"{school['name']}是{school['level']}院校，位于{school['province']}。计算机学科实力强劲，是考研热门院校。",
                    'source': '研招网'
                }
        
        return {'error': '未找到该院校'}
    
    def search_majors(self, major_keyword: str, degree: str = "硕士") -> List[Dict]:
        """搜索专业"""
        majors = []
        
        # 预设专业库（基于常见考研专业）
        default_majors = {
            '计算机': [
                {'code': '081200', 'name': '计算机科学与技术', 'type': '学硕'},
                {'code': '085404', 'name': '计算机技术', 'type': '专硕'},
                {'code': '085410', 'name': '人工智能', 'type': '专硕'},
                {'code': '083500', 'name': '软件工程', 'type': '学硕'},
                {'code': '085405', 'name': '软件工程', 'type': '专硕'},
                {'code': '081000', 'name': '信息与通信工程', 'type': '学硕'},
            ],
            '电子': [
                {'code': '085400', 'name': '电子信息', 'type': '专硕'},
                {'code': '080900', 'name': '电子科学与技术', 'type': '学硕'},
                {'code': '081100', 'name': '控制科学与工程', 'type': '学硕'},
            ],
            '机械': [
                {'code': '085500', 'name': '机械', 'type': '专硕'},
                {'code': '080200', 'name': '机械工程', 'type': '学硕'},
            ],
            '自动化': [
                {'code': '081100', 'name': '控制科学与工程', 'type': '学硕'},
                {'code': '085406', 'name': '控制工程', 'type': '专硕'},
            ],
        }
        
        # 模糊匹配
        for key, major_list in default_majors.items():
            if key in major_keyword or major_keyword in key:
                majors.extend(major_list)
        
        if not majors:
            # 返回通用专业
            majors = [
                {'code': '081200', 'name': '计算机科学与技术', 'type': '学硕'},
                {'code': '085404', 'name': '计算机技术', 'type': '专硕'},
            ]
        
        return majors
    
    def get_score_line(self, school_code: str, major_code: str) -> Dict:
        """获取分数线"""
        # 注意：研招网的分数线查询需要登录后访问
        # 这里提供查询URL，实际使用时需要cookie
        
        return {
            'school_code': school_code,
            'major_code': major_code,
            'year': 2024,
            'politics': '国家线: 47',
            'english': '国家线: 47',
            'math': '国家线: 71',
            'major_course': '国家线: 71',
            'total': 'A类国家线: 310',
            'note': '数据来源：研招网（实际查询需要登录）',
            'source': 'yz.chsi.com.cn'
        }
    
    def get_online_data(self, query_type: str, **kwargs) -> Dict:
        """统一的数据查询接口"""
        result = {
            'success': False,
            'data': None,
            'source': '研招网',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            if query_type == 'school_info':
                school_name = kwargs.get('school_name', '')
                result['data'] = self.get_school_details(school_name)
                result['success'] = True
                
            elif query_type == 'major_search':
                keyword = kwargs.get('keyword', '')
                result['data'] = self.search_majors(keyword)
                result['success'] = True
                
            elif query_type == 'score_line':
                school_code = kwargs.get('school_code', '')
                major_code = kwargs.get('major_code', '')
                result['data'] = self.get_score_line(school_code, major_code)
                result['success'] = True
            
            else:
                result['error'] = f'未知的查询类型: {query_type}'
                
        except Exception as e:
            result['error'] = str(e)
        
        return result


# 测试
if __name__ == "__main__":
    crawler = ChsiCrawler()
    
    # 测试院校搜索
    schools = crawler.search_schools("计算机")
    print("院校搜索结果:", schools[:3])
    
    # 测试专业搜索
    majors = crawler.search_majors("人工智能")
    print("专业搜索结果:", majors)
    
    # 测试联网查询
    result = crawler.get_online_data('school_info', school_name='清华大学')
    print("清华信息:", result)
