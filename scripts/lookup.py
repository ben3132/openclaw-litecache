#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查找缓存 - 主入口"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 路径
SCRIPT_DIR = Path(__file__).parent.parent
DATA_DIR = SCRIPT_DIR / "data"
DB_PATH = DATA_DIR / "cache.db"
CONFIG_PATH = SCRIPT_DIR / "config.json"

# 加载配置
def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "similarity_threshold": 0.7,
        "max_question_length": 100,
        "exclude_patterns": []
    }

# 导入相似度计算
sys.path.insert(0, str(SCRIPT_DIR / "scripts"))
from similarity import combined_similarity, extract_keywords

def is_cacheable(question: str, config: dict) -> tuple[bool, str]:
    """判断问题是否可缓存"""
    # 长度检查
    if len(question) > config.get("max_question_length", 100):
        return False, "问题过长"
    
    # 排除关键词检查
    exclude_patterns = config.get("exclude_patterns", [])
    for pattern in exclude_patterns:
        if pattern in question:
            return False, f"包含时效关键词: {pattern}"
    
    return True, ""

def lookup(question: str) -> dict:
    """
    查找缓存
    返回: {"hit": bool, "answer": str, "similarity": float, "reason": str}
    """
    config = load_config()
    
    # 检查是否可缓存
    cacheable, reason = is_cacheable(question, config)
    if not cacheable:
        return {"hit": False, "reason": reason}
    
    # 连接数据库
    if not DB_PATH.exists():
        return {"hit": False, "reason": "缓存数据库不存在"}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询所有未过期的缓存
    now = datetime.now().isoformat()
    cursor.execute("""
        SELECT id, question, answer, question_keywords, hit_count
        FROM cache
        WHERE expires_at > ?
        ORDER BY hit_count DESC, created_at DESC
        LIMIT 100
    """, (now,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return {"hit": False, "reason": "缓存为空"}
    
    # 计算相似度，找最佳匹配
    threshold = config.get("similarity_threshold", 0.7)
    best_match = None
    best_similarity = 0.0
    
    for row in rows:
        cached_id, cached_q, cached_a, cached_kw, hit_count = row
        similarity = combined_similarity(question, cached_q)
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = {
                "id": cached_id,
                "question": cached_q,
                "answer": cached_a,
                "similarity": similarity
            }
    
    # 判断是否命中
    if best_match and best_similarity >= threshold:
        # 更新命中统计
        update_hit(best_match["id"])
        
        return {
            "hit": True,
            "answer": best_match["answer"],
            "similarity": round(best_similarity, 3),
            "cached_question": best_match["question"],
            "cache_id": best_match["id"]
        }
    
    return {
        "hit": False,
        "reason": f"最佳相似度 {best_similarity:.3f} 低于阈值 {threshold}"
    }

def update_hit(cache_id: int):
    """更新命中统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE cache
        SET hit_count = hit_count + 1, last_hit_at = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), cache_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"hit": False, "reason": "缺少问题参数"}, ensure_ascii=False))
        sys.exit(1)
    
    question = sys.argv[1]
    result = lookup(question)
    print(json.dumps(result, ensure_ascii=False))
