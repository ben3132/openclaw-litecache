#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""相似度计算工具"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import re
from collections import Counter
from difflib import SequenceMatcher

def extract_keywords(text: str) -> set:
    """提取关键词（简化版：分词 + 去停用词）"""
    # 中文分词简化：按字符切分，提取2-4字的词组
    # 英文按空格切分
    
    keywords = set()
    
    # 提取中文词组（2-4字）
    chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
    for segment in chinese_chars:
        for length in range(2, min(5, len(segment) + 1)):
            for i in range(len(segment) - length + 1):
                keywords.add(segment[i:i+length])
        # 单字也加入
        for char in segment:
            keywords.add(char)
    
    # 提取英文单词
    english_words = re.findall(r'[a-zA-Z]+', text)
    keywords.update(w.lower() for w in english_words if len(w) > 1)
    
    # 提取数字
    numbers = re.findall(r'\d+', text)
    keywords.update(numbers)
    
    return keywords

def jaccard_similarity(set1: set, set2: set) -> float:
    """Jaccard 相似度"""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def edit_distance_ratio(s1: str, s2: str) -> float:
    """编辑距离相似度"""
    return SequenceMatcher(None, s1, s2).ratio()

def combined_similarity(q1: str, q2: str) -> float:
    """
    综合相似度 = 0.6 * 关键词Jaccard + 0.4 * 编辑距离
    """
    kw1 = extract_keywords(q1)
    kw2 = extract_keywords(q2)
    
    jaccard = jaccard_similarity(kw1, kw2)
    edit = edit_distance_ratio(q1, q2)
    
    return 0.6 * jaccard + 0.4 * edit

if __name__ == "__main__":
    # 测试
    test_cases = [
        ("Python怎么安装", "如何安装Python"),
        ("Python怎么安装", "Python安装教程"),
        ("今天天气怎么样", "今天天气"),
        ("怎么写一个函数", "如何定义函数"),
        ("完全不同的问题", "毫不相关的内容"),
    ]
    
    for q1, q2 in test_cases:
        sim = combined_similarity(q1, q2)
        print(f"'{q1}' vs '{q2}' -> {sim:.3f}")
