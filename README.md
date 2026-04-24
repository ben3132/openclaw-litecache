# qcache - OpenClaw 问答缓存技能

[![Version](https://img.shields.io/badge/version-0.1.1-blue.svg)](https://github.com/ben3132/qcache)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://www.python.org/)

📦 减少同一对话中重复问题的 token 消耗

---

## 概述

qcache 是一个 OpenClaw 技能，用于缓存有客观答案且短期不变的问题。当用户重复提问或用不同表述问同样问题时，直接返回缓存答案，跳过模型调用。

**核心特性**：
- ✅ 语义相似度匹配（关键词 + 编辑距离）
- ✅ 自动排除时效性问题、上下文依赖问题、操作请求
- ✅ 自动触发，无需手动调用
- ✅ SQLite 存储，轻量高效

---

## 适用场景

### ✅ 适用（会缓存）

| 类型 | 示例 |
|------|------|
| 客观定义 | "什么是 REST API" |
| 操作步骤 | "Python 怎么安装" |
| 概念对比 | "list 和 tuple 区别" |
| 语法用法 | "Python 如何定义函数" |

### ❌ 不适用（不缓存）

| 类型 | 示例 | 原因 |
|------|------|------|
| 上下文依赖 | "这个是什么情况" | 依赖当前对话 |
| 追问/承接 | "那 Mac 上呢" | 依赖上一轮 |
| 时效性问题 | "今天天气" | 答案会变 |
| 操作请求 | "帮我写个脚本" | 非问答 |

---

## 安装

### 方法 1：复制到 skills 目录

```bash
cp -r qcache ~/.openclaw/workspace/skills/
```

### 方法 2：克隆

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/ben3132/qcache.git
```

### 验证安装

```bash
python scripts/manage.py stats
```

---

## 使用

### 自动模式（推荐）

加载 SKILL.md 后，Agent 会自动执行缓存逻辑：
1. 回答前 → 查缓存（`lookup.py`）
2. 命中 → 直接返回缓存答案
3. 未命中 → 正常回答 → 存缓存（`store.py`）

### 手动管理

```bash
# 查看统计
python scripts/manage.py stats

# 列出所有缓存
python scripts/manage.py list

# 删除某条
python scripts/manage.py delete <id>

# 清理过期缓存
python scripts/manage.py clean

# 清空所有缓存
python scripts/manage.py clear
```

---

## 配置

编辑 `config.json`：

```json
{
  "similarity_threshold": 0.4,        // 相似度阈值（0-1）
  "max_question_length": 100,        // 最大问题长度
  "default_ttl_hours": 24,           // 缓存有效期（小时）
  "max_cache_size": 1000,            // 最大缓存条目数
  "exclude_patterns": [...]          // 排除关键词列表
}
```

---

## 工作原理

```
用户提问
    ↓
[预处理] 长度检测、时效关键词排除
    ↓
[相似度检索] 关键词提取 + 编辑距离计算
    ↓
命中且相似度 >= 阈值？
  ├─ 是 → 返回缓存答案 ✅
  └─ 否 → 调用模型 → 存入缓存 → 返回
```

**相似度算法**（简化版）：

```
综合相似度 = 0.6 × 关键词Jaccard相似度 + 0.4 × 编辑距离相似度
```

---

## 项目结构

```
qcache/
├── SKILL.md           # 技能文档（强制执行规则）
├── meta.json          # 元数据
├── config.json        # 配置
└── scripts/
    ├── init_db.py     # 初始化数据库
    ├── similarity.py  # 相似度计算
    ├── lookup.py      # 查缓存（主入口）
    ├── store.py       # 存缓存
    └── manage.py      # 管理命令
```

---

## 限制（简化版）

- 使用关键词匹配，非向量嵌入（精度略低）
- 时效判断靠关键词列表（非智能分类）
- 上下文依赖检测靠关键词（非语义分析）

---

## 后续优化方向

- [ ] 引入向量嵌入（sentence-transformers）
- [ ] 时效性智能判断
- [ ] 上下文依赖检测
- [ ] 命中率统计与低命中率条目清理

---

## License

[MIT](LICENSE)

---

## 作者

Made for OpenClaw

---

## 相关链接

- [OpenClaw](https://github.com/ben3132/openclaw) - 主项目
