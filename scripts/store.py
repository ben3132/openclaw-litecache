#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""存入缓存"""

import sqlite3
import json
import sys
import argparse
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

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"default_ttl_hours": 24, "max_cache_size": 1000}

sys.path.insert(0, str(SCRIPT_DIR / "scripts"))
from similarity import extract_keywords

def store(question: str, answer: str, ttl_hours: int = None) -> dict:
    """存入缓存"""
    config = load_config()
    
    if ttl_hours is None:
        ttl_hours = config.get("default_ttl_hours", 24)
    
    # 检查数据库
    if not DB_PATH.exists():
        return {"success": False, "reason": "数据库不存在，请先运行 init_db.py"}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查缓存大小
    cursor.execute("SELECT COUNT(*) FROM cache")
    count = cursor.fetchone()[0]
    max_size = config.get("max_cache_size", 1000)
    
    if count >= max_size:
        # 删除最旧且命中率最低的
        cursor.execute("""
            DELETE FROM cache
            WHERE id IN (
                SELECT id FROM cache
                ORDER BY hit_count ASC, created_at ASC
                LIMIT ?
            )
        """, (count - max_size + 1,))
    
    # 提取关键词
    keywords = extract_keywords(question)
    keywords_str = ",".join(sorted(keywords))
    
    # 计算过期时间
    expires_at = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
    
    # 插入
    cursor.execute("""
        INSERT INTO cache (question, answer, question_keywords, expires_at)
        VALUES (?, ?, ?, ?)
    """, (question, answer, keywords_str, expires_at))
    
    cache_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "cache_id": cache_id,
        "expires_at": expires_at,
        "keywords_count": len(keywords)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="存入问答缓存")
    parser.add_argument("--question", "-q", required=True, help="问题")
    parser.add_argument("--answer", "-a", required=True, help="答案")
    parser.add_argument("--ttl", "-t", type=int, help="有效期（小时）")
    
    args = parser.parse_args()
    
    result = store(args.question, args.answer, args.ttl)
    print(json.dumps(result, ensure_ascii=False))
