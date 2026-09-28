# RSI Framework v2.2

> 多分支思考 + 中立验证 + 人工把关的自我升级。两个 Agent Skill，适用于 Claude（claude.ai / Claude Code）。

**只有输入 `/rsi` `/retry` `/rethink` 才运行，不是后台常驻流程。**

```
/rsi 想法
  ├─ 五分支（内部）：目的 · 第一性原理 · 限制 · 成功标准 · 可用资源
  ├─ ① 汇总 1：任务定义
  ├─ 方案（内部）：Plan A/B/C → divide 拆解 → 钢人反驳 → 验证 → 评分
  ├─ ② 汇总 2：一句话描述 · 评分 · 最强反驳 · 证据等级
  ├─ ③ 实际例子：真实案例 + 来源链接
  ├─ ④ 综合：决策变量，不重复方案
  ├─ 决策点：选择题确认方向（任何步骤不懂都会当场提问）
  └─ ⑤ 解决方案：本轮终点，停止

/retry [1|2]   目标不变，路径重算（至少换掉一项：方案/来源/拆法/验证/假设）
/rethink       复盘方法 → Patch → 评估（考题库 / 外部复核）→ 收题 → 开启下一轮
```

## 中立性（不被用户观点或某个方案带偏）

1. 用户的想法最多占一个方案，至少一个方案不用它
2. 成功标准和评分维度在生成方案前固定
3. 所有方案受同等强度的钢人反驳
4. 用户陈述分为「事实」和「偏好」；偏好只影响选择，不改分数
5. 结论强度看证据等级（L0 直觉 → L4 测算），不看是谁提出的

以上均由 `rsi_state.py check` 自动校验。

## 目录

```
skills/
├── rsi/
│   ├── SKILL.md              主流程 · 不变原则 · 经验库 · 考题库
│   ├── references/
│   │   ├── method.md         标签与证据等级 · 五分支 · 方案 · 反驳 · 评分 · 例子
│   │   └── control.md        提问 · /retry · 停止条件
│   ├── templates/            ①–⑤ 五个输出模板
│   ├── scripts/rsi_state.py  状态机：编号、追溯、证据、中立性校验、交接、外部复核包
│   └── evals/rubric.md       评分标准（锁死）
└── rethink/
    ├── SKILL.md              复盘 → Patch → 候选版本 → 评估 → 下一轮
    ├── references/review.md  复盘清单 · 经验写法 · Patch 格式 · 防过拟合
    └── templates/            复盘报告
```

## 评估方式

泛用框架没有固定考卷，改为两条路：

- **考题库**：每次 /rethink 用选择题问是否把本轮任务收入题库，题库随真实使用长出来（最多 10 道）
- **外部复核**：`rsi_state.py export` 生成复核包，复制给其他 AI 检查后贴回；外部意见逐条核对，不直接照收。复核包不标注哪个方案来自用户，避免外部审稿人被带偏

## 路线图

- [x] v2.2 个人版：考题库边用边收；外部 AI 复核
- [ ] 公司版：独立 agent 做客观验证；分级放权；无人值守循环与漂移警报

## 安装

**claude.ai（需电脑端）**：Settings → Capabilities → Skills，分别上传 `rsi.zip` 与 `rethink.zip`。

**Claude Code**：`cp -r skills/rsi skills/rethink ~/.claude/skills/`

依赖：`divide-into-several-pieces`（方案拆解）、Python 3.8+（无第三方库）。

## License

MIT
