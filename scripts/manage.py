#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""缓存管理"""

import sqlite3
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 路径
SCRIPT_DIR = Path(__file__).parent.parent
DATA_DIR = SCRIPT_DIR / "data"
DB_PATH = DATA_DIR / "cache.db"

def list_cache(limit: int = 20, offset: int = 0) -> None:
    """列出缓存"""
    if not DB_PATH.exists():
        print("❌ 数据库不存在")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, question, hit_count, created_at, expires_at
        FROM cache
        ORDER BY hit_count DESC, created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    rows = cursor.fetchall()
    total = cursor.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
    conn.close()
    
    print(f"\n📦 缓存列表 (共 {total} 条，显示 {len(rows)} 条)\n")
    print(f"{'ID':<6} {'命中':<6} {'问题':<40} {'创建时间':<20}")
    print("-" * 80)
    
    for row in rows:
        cache_id, question, hit_count, created_at, expires_at = row
        # 截断问题
        q_display = question[:38] + ".." if len(question) > 40 else question
        created = created_at[:16] if created_at else ""
        print(f"{cache_id:<6} {hit_count:<6} {q_display:<40} {created:<20}")

def stats() -> None:
    """统计信息"""
    if not DB_PATH.exists():
        print("❌ 数据库不存在")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总数
    total = cursor.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
    
    # 总命中
    total_hits = cursor.execute("SELECT SUM(hit_count) FROM cache").fetchone()[0] or 0
    
    # 过期数
    now = datetime.now().isoformat()
    expired = cursor.execute("SELECT COUNT(*) FROM cache WHERE expires_at < ?", (now,)).fetchone()[0]
    
    # 高命中条目
    top_hits = cursor.execute("""
        SELECT question, hit_count FROM cache
        ORDER BY hit_count DESC LIMIT 5
    """).fetchall()
    
    conn.close()
    
    print(f"\n📊 缓存统计\n")
    print(f"  总条目数: {total}")
    print(f"  总命中数: {total_hits}")
    print(f"  已过期:   {expired}")
    print(f"  命中率:   {(total_hits / (total_hits + total) * 100):.1f}%" if total > 0 else "  命中率:   0%")
    
    if top_hits and top_hits[0][1] > 0:
        print(f"\n  🔥 热门问题:")
        for q, h in top_hits:
            q_display = q[:35] + ".." if len(q) > 35 else q
            print(f"     - {q_display} ({h} 次)")

def delete(cache_id: int) -> None:
    """删除条目"""
    if not DB_PATH.exists():
        print("❌ 数据库不存在")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT question FROM cache WHERE id = ?", (cache_id,))
    row = cursor.fetchone()
    
    if not row:
        print(f"❌ 未找到 ID={cache_id} 的条目")
        conn.close()
        return
    
    cursor.execute("DELETE FROM cache WHERE id = ?", (cache_id,))
    conn.commit()
    conn.close()
    
    print(f"✅ 已删除: {row[0][:50]}...")

def clean() -> None:
    """清理过期条目"""
    if not DB_PATH.exists():
        print("❌ 数据库不存在")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    cursor.execute("SELECT COUNT(*) FROM cache WHERE expires_at < ?", (now,))
    expired_count = cursor.fetchone()[0]
    
    if expired_count == 0:
        print("✅ 没有过期条目")
        conn.close()
        return
    
    cursor.execute("DELETE FROM cache WHERE expires_at < ?", (now,))
    conn.commit()
    conn.close()
    
    print(f"✅ 已清理 {expired_count} 条过期条目")

def clear_all() -> None:
    """清空所有缓存"""
    if not DB_PATH.exists():
        print("❌ 数据库不存在")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cache")
    count = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ 已清空 {count} 条缓存")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="缓存管理")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # list
    list_parser = subparsers.add_parser("list", help="列出缓存")
    list_parser.add_argument("--limit", "-l", type=int, default=20)
    list_parser.add_argument("--offset", "-o", type=int, default=0)
    
    # stats
    subparsers.add_parser("stats", help="统计信息")
    
    # delete
    delete_parser = subparsers.add_parser("delete", help="删除条目")
    delete_parser.add_argument("id", type=int, help="缓存ID")
    
    # clean
    subparsers.add_parser("clean", help="清理过期条目")
    
    # clear
    subparsers.add_parser("clear", help="清空所有缓存")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_cache(args.limit, args.offset)
    elif args.command == "stats":
        stats()
    elif args.command == "delete":
        delete(args.id)
    elif args.command == "clean":
        clean()
    elif args.command == "clear":
        clear_all()
    else:
        parser.print_help()
