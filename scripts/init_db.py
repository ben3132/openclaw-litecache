#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""初始化缓存数据库"""

import sqlite3
import os
import sys
from pathlib import Path

# Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 数据库路径
SCRIPT_DIR = Path(__file__).parent.parent
DATA_DIR = SCRIPT_DIR / "data"
DB_PATH = DATA_DIR / "cache.db"

def init_db():
    """创建数据库表"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 缓存表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            question_keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            hit_count INTEGER DEFAULT 0,
            last_hit_at TIMESTAMP
        )
    """)
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_created_at ON cache(created_at)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成: {DB_PATH}")

if __name__ == "__main__":
    init_db()
