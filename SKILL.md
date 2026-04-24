---
name: openclaw-litecache
description: |
  零依赖问答缓存技能 - 缓存客观答案，减少同一对话中重复问题的 token 消耗。
  不需要 Redis、不需要 Embedding API、不需要向量数据库。
  仅适用于：有客观答案、短期不变的问题。
  不适用于：上下文依赖问题、时效性问题、操作请求。
homepage: https://github.com/ben3132/openclaw-litecache
metadata:
  openclaw:
    emoji: '📦'
---

# openclaw-litecache - 零依赖问答缓存技能

v1.0.0：使用关键词匹配 + 编辑距离实现语义相似度检测。零外部依赖，SQLite 单文件存储。

## 核心定位

**目标**：用最简单的方式减少/消除同一对话中，有客观答案且短期不变的问题的重复消耗。

**差异化**：
- ❌ 不需要 Redis
- ❌ 不需要 Embedding API
- ❌ 不需要向量数据库
- ✅ 纯 Python 标准库
- ✅ SQLite 单文件存储
- ✅ 复制即用

### ✅ 适用场景

- 客观定义："什么是REST API"、"HTTP状态码200表示什么"
- 操作步骤："Python怎么安装"、"Git提交命令是什么"
- 概念对比："list和tuple区别"、"GET和POST区别"
- 语法用法："Python如何定义函数"

### ❌ 不适用场景

- **上下文依赖**："这个是什么情况"、"刚才那个问题呢"、"那Mac上呢"
- **时效性问题**："今天天气"、"最新版本是多少"
- **操作请求**："帮我写个脚本"、"分析这段代码"
- **追问/承接**："继续上一步"、"呢"、"那..."

---

## ⚠️ 强制执行规则（最高优先级）

**每次回答用户问题前，必须执行以下流程：**

### 1. 查缓存（回答前）

```bash
python3 <SKILL_DIR>/scripts/lookup.py "<用户问题>"
```

- 返回 `{"hit": true, "answer": "..."}` → **直接返回该答案，跳过模型调用**
- 返回 `{"hit": false}` → 正常调用模型回答

### 2. 存缓存（回答后）

**仅当缓存未命中且已正常回答后，执行：**

```bash
python3 <SKILL_DIR>/scripts/store.py --question "<用户问题>" --answer "<你的回答>"
```

### 3. 执行顺序

```
用户提问
    ↓
调用 lookup.py 查缓存
    ↓
命中？
  ├─ 是 → 直接返回缓存答案（结束）
  └─ 否 → 调用模型生成答案
              ↓
         调用 store.py 存入缓存
              ↓
         返回答案
```

### 4. 例外情况（不查缓存）

以下情况跳过缓存查询，直接回答：
- 用户要求执行操作（非问答）
- 用户明确要求重新回答
- 问题包含时效关键词（今天、现在、最新）
- 问题过短（< 5 字）或过长（> 100 字）

---

## 工作流程

```
用户提问
    ↓
[预处理] 判断是否可缓存（长度、时效关键词、上下文依赖）
    ↓
[相似度检索] 在缓存中找相似问题
    ↓
命中且相似度 >= 阈值？
  ├─ 是 → 直接返回缓存答案 ✅
  └─ 否 → 返回 None，由 agent 调用模型
```

## 使用方式

### 1. 查缓存（回答前调用）

```bash
python3 <SCRIPT_PATH>/scripts/lookup.py "Python怎么安装"
```

返回：
- 命中：`{"hit": true, "answer": "...", "similarity": 0.85}`
- 未命中：`{"hit": false}`

### 2. 存缓存（回答后调用）

```bash
python3 <SCRIPT_PATH>/scripts/store.py --question "Python怎么安装" --answer "..."
```

### 3. 管理缓存

```bash
# 列出所有缓存
python3 <SCRIPT_PATH>/scripts/manage.py list

# 查看统计
python3 <SCRIPT_PATH>/scripts/manage.py stats

# 删除某条
python3 <SCRIPT_PATH>/scripts/manage.py delete <id>

# 清空过期
python3 <SCRIPT_PATH>/scripts/manage.py clean
```

## 配置 (config.json)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| similarity_threshold | 0.4 | 相似度阈值，高于此值才命中 |
| max_question_length | 100 | 超过此长度的问题不缓存 |
| default_ttl_hours | 24 | 默认缓存有效期（小时） |
| max_cache_size | 1000 | 最大缓存条目数 |
| auto_store | true | 是否自动存储新问答 |
| exclude_patterns | [...] | 包含这些关键词的问题不缓存 |

## 轻量化的设计选择

**为什么不用 Embedding？**
1. 需要额外 API 调用（消耗 token）
2. 需要 sentence-transformers 或 OpenAI API
3. 增加部署复杂度

**为什么用关键词+编辑距离？**
1. 对简单问题够用（80% 场景）
2. 纯 Python 标准库实现
3. 离线可用，零外部依赖

**SQLite vs Redis/向量数据库**
1. 单文件，备份就是一个文件
2. 不需要额外服务
3. 查看、调试、迁移都简单

## 后续优化方向

- [ ] 引入轻量 Embedding（all-MiniLM-L6-v2，本地运行）
- [ ] 时效性智能判断
- [ ] 上下文依赖检测
- [ ] 命中率统计 + 低命中率条目清理
