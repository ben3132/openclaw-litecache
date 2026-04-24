# openclaw-litecache - 零依赖问答缓存 | 5分钟配置，立省30% token

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/ben3132/openclaw-litecache)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-yellow.svg)](https://www.python.org/)

📦 **零依赖** · **开箱即用** · **SQLite存储** · **自动省token**

> 最轻量的 OpenClaw 问答缓存方案 —— 不需要 Redis、不需要 Embedding API、不需要向量数据库。

---

## 一句话介绍

**openclaw-litecache** 是一个零依赖的 OpenClaw 技能，通过缓存客观问题的答案，**减少重复提问的 token 消耗**。适合不想折腾基础设施的个人开发者和小团队。

---

## 为什么选择 openclaw-litecache

| 特性 | openclaw-litecache | GPTCache | openclaw-semantic-cache |
|------|-------------------|----------|------------------------|
| **外部依赖** | ❌ 无 | ✅ Redis/Milvus | ✅ Redis |
| **Embedding API** | ❌ 不需要 | ✅ 需要 | ✅ 需要 |
| **部署难度** | 🟢 复制即用 | 🔴 需运维 | 🟡 需配置 |
| **存储方式** | SQLite 单文件 | 向量数据库 | Redis |
| **适合场景** | 个人/小团队 | 企业/高并发 | 需深度语义匹配 |

**核心优势：**
- ✅ **零依赖** — 纯 Python 标准库，无需 pip install 任何东西
- ✅ **SQLite 存储** — 一个文件就是全部，备份、迁移、查看都简单
- ✅ **不需要 Embedding API** — 省掉一次 API 调用，离线也能跑
- ✅ **自动过滤** — 智能排除时效性问题，不会缓存"今天天气"
- ✅ **自动触发** — 加载即用，无需手动调用

---

## 适用场景

### ✅ 适用（会缓存，帮你节省 token）

| 类型 | 示例 | 节省效果 |
|------|------|---------|
| 客观定义 | "什么是 REST API" | 重复问直接返回答案，零消耗 |
| 操作步骤 | "Python 怎么安装" | 换种问法也能命中缓存 |
| 概念对比 | "list 和 tuple 区别" | 多次询问只消耗一次 token |
| 语法用法 | "Python 如何定义函数" | 大幅降低重复消耗 |

### ❌ 不适用（不缓存，避免错误答案）

| 类型 | 示例 | 原因 |
|------|------|------|
| 上下文依赖 | "这个是什么情况" | 依赖当前对话 |
| 追问/承接 | "那 Mac 上呢" | 依赖上一轮 |
| 时效性问题 | "今天天气" | 答案会变 |
| 操作请求 | "帮我写个脚本" | 非问答 |

---

## 安装 | 5分钟配置

### 方法 1：复制到 skills 目录

```bash
cp -r openclaw-litecache ~/.openclaw/workspace/skills/
```

### 方法 2：克隆仓库

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/ben3132/openclaw-litecache.git
```

### 验证安装

```bash
python scripts/manage.py stats
```

---

## 使用 | 自动减少消耗

### 自动模式（推荐）

加载 SKILL.md 后，Agent 会自动执行缓存逻辑：
1. 回答前 → 查缓存（`lookup.py`）
2. 命中 → 直接返回缓存答案，**token 消耗为零**
3. 未命中 → 正常回答 → 存缓存（`store.py`）

### 手动管理

```bash
# 查看统计（命中率、节省情况）
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

## 配置 | 调整节省策略

编辑 `config.json`：

```json
{
  "similarity_threshold": 0.4,        // 相似度阈值（0-1），越高越严格
  "max_question_length": 100,        // 最大问题长度
  "default_ttl_hours": 24,           // 缓存有效期（小时）
  "max_cache_size": 1000,            // 最大缓存条目数
  "exclude_patterns": [...]          // 排除关键词列表
}
```

---

## 工作原理 | 如何帮你减少消耗

```
用户提问
    ↓
[预处理] 长度检测、时效关键词排除
    ↓
[相似度检索] 关键词提取 + 编辑距离计算
    ↓
命中且相似度 >= 阈值？
  ├─ 是 → 返回缓存答案 ✅（零 token 消耗）
  └─ 否 → 调用模型 → 存入缓存 → 返回
```

**相似度算法**（轻量版）：

```
综合相似度 = 0.6 × 关键词Jaccard相似度 + 0.4 × 编辑距离相似度
```

**为什么不用 Embedding？**
- Embedding 需要额外 API 调用（消耗 token）
- 需要 sentence-transformers 或 OpenAI API
- 对简单问题，关键词+编辑距离够用

---

## 项目结构

```
openclaw-litecache/
├── SKILL.md           # 技能文档（强制执行规则）
├── meta.json          # 元数据
├── config.json        # 配置
├── README.md          # 本文件
└── scripts/
    ├── init_db.py     # 初始化数据库
    ├── similarity.py  # 相似度计算
    ├── lookup.py      # 查缓存（主入口）
    ├── store.py       # 存缓存
    └── manage.py      # 管理命令
```

---

## 限制（轻量化的代价）

- 使用关键词匹配，非向量嵌入（精度略低但够用）
- 时效判断靠关键词列表（非智能分类）
- 上下文依赖检测靠关键词（非语义分析）

**适合谁用：**
- 不想折腾基础设施的个人开发者
- 小团队，没有运维资源
- 离线/内网环境，不能连外部服务
- 预算敏感，Embedding API 也是钱

**不适合谁用：**
- 需要企业级高并发（选 GPTCache）
- 需要深度语义匹配（选 openclaw-semantic-cache）
- 要 97% 成本削减（选模型路由方案）

---

## 后续优化方向

- [ ] 引入轻量 Embedding（如 all-MiniLM-L6-v2，本地运行）
- [ ] 时效性智能判断
- [ ] 上下文依赖检测
- [ ] 命中率统计与低命中率条目清理

---

## License

[MIT](LICENSE)

---

## 作者

Made for OpenClaw by [ben3132](https://github.com/ben3132)

---

## 相关链接

- [GitHub 仓库](https://github.com/ben3132/openclaw-litecache)
- [提交 Issue](https://github.com/ben3132/openclaw-litecache/issues)

---

## 关键词

openclaw skill, token saving, cost reduction, 减少消耗, 节省token, 降低AI成本, 问答缓存, 语义相似度, 智能缓存, API成本优化, lightweight cache, sqlite cache, zero dependency
