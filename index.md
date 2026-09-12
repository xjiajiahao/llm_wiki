# 索引

## 总览

- [[README]] - 仓库入口与维护原则概览。
- [[concepts/research-taxonomy]] - 当前 wiki 的跨领域概念地图。
- [[concepts/llm-taxonomy]] - 大模型领域的概念地图。
- [[concepts/2d-nesting-taxonomy]] - `2D nesting` 领域的概念地图。

## 领域组织

- 当前 wiki 已从单一的大模型 wiki，扩展为可容纳多个研究方向的研究 wiki。
- 组织原则仍然是“概念优先”，但索引改为先按领域分区，再在每个领域内部列出概念、来源与实例入口。
- `models/` 目录目前仍主要服务于大模型主题；`2D nesting` 这类非模型领域，暂时以 `concepts/`、`sources/` 和 `entities/` 为主。

## 大模型

- [[concepts/transformer-block]] - 组织架构知识的基础骨架页。
- [[concepts/mixture-of-experts]] - 稀疏专家模型的核心概念页。
- [[entities/deepseek]] - 当前主要来源簇与示例模型家族。

### 概念

- [[concepts/llm-taxonomy]] - 按架构、训练、优化、推理组织的顶层分类。
- [[concepts/transformer-block]] - 大多数 LLM 的标准 block 结构、变体与插拔点。
- [[concepts/attention]] - 基础缩放点积注意力的 `Q/K/V` 定义、因果掩码与 `n \times d` 形状约定。
- [[concepts/multi-head-attention]] - 标准 `MHA` 的多头拆分、拼接、输出投影与形状推导。
- [[concepts/rope]] - 现代 LLM 常用的位置编码机制与长上下文外推起点。
- [[concepts/rmsnorm]] - 现代 decoder-only 模型常见的归一化方法。
- [[concepts/grouped-query-attention]] - 介于 MHA 与 MQA 之间的 K/V 共享注意力设计。
- [[concepts/flashattention]] - 以内存访问优化为核心的 attention 实现族。
- [[concepts/kv-cache]] - 自回归推理中的 K/V 缓存机制与成本来源。
- [[concepts/adamw]] - LLM 训练中最常见的优化器基线之一。
- [[concepts/policy-gradient]] - 直接优化随机策略的强化学习基础路线，以及 baseline 如何降方差。
- [[concepts/proximal-policy-optimization]] - 以 clipping 限制策略更新步长的经典 RL 算法，并补充 `V_old` 与 value target 的稳定性解释。
- [[concepts/rlhf-dpo-grpo]] - 对齐与后训练阶段的常见优化路线，以及 `LLM PPO` 中序列级奖励如何变成 token 级信号。
- [[concepts/mixture-of-experts]] - 稀疏专家架构、路由、容量与负载均衡。
- [[concepts/multi-head-latent-attention]] - `MLA` 的低秩 `KV` 压缩、解耦 `RoPE` 与缓存缩减机制。
- [[concepts/multi-token-prediction]] - 一次预测多个未来 token 的训练目标。
- [[concepts/auxiliary-loss-free-load-balancing]] - DeepSeek-V3 强调的无辅助损失负载均衡。
- [[concepts/fp8-training]] - 以 `FP8` 为核心的混合精度训练方案。
- [[concepts/attention-for-long-context]] - `CSA/HCA` 的压缩、稀疏选择、滑窗补偿与效率机制。
- [[concepts/manifold-constrained-hyper-connections]] - `mHC` 如何用双随机矩阵约束稳定残差传播。
- [[concepts/muon-optimizer]] - `Muon` 的矩阵级正交化更新与 `DeepSeek-V4` 实现要点。
- [[concepts/fp4-quantization-aware-training]] - `FP4 QAT` 在 `MoE` 权重与 `CSA` indexer 路径上的落地方式。
- [[concepts/on-policy-distillation]] - DeepSeek-V4 描述的统一化蒸馏阶段。

### 来源

- 来源页中的“原始路径”链接统一使用相对 `raw/` 路径，便于跨机器迁移。
- [[sources/deepseek-v3-technical-report]] - 2024 年 `DeepSeek-V3` 技术报告的来源页。
- [[sources/deepseek-v4-technical-report]] - 2026 年 `DeepSeek-V4` 技术报告的来源页。
- [[sources/ppo-algorithm-explanation-conversation]] - 一份围绕 `PPO`、`GAE` 与 `LLM RLHF` 的讲解型问答来源。

### 模型

- [[models/deepseek-v3]] - `DeepSeek-V3` 的模型摘要页。
- [[models/deepseek-v4]] - `DeepSeek-V4` 系列的模型摘要页。

### 笔记

- [[notes/wiki-bootstrap]] - 仓库初始化与早期结构说明。
- [[notes/deepseek-v3-v4-comparison]] - `DeepSeek-V3` 与 `DeepSeek-V4` 的对照笔记。

## 2D Nesting

- [[concepts/2d-irregular-cutting-and-packing]] - `2D irregular C&P / nesting` 的总览，区分几何挑战与优化挑战。
- [[concepts/2d-irregular-strip-packing]] - `2DISPP` 的形式化定义与“可行性问题序列”思路。
- [[concepts/collision-detection-engine-for-2d-nesting]] - 把几何可行性从上层优化器中解耦出来的 `CDE` 概念页。

### 概念

- [[concepts/2d-nesting-taxonomy]] - 当前 `2D nesting` 方向的工作性 taxonomy。
- [[concepts/2d-irregular-cutting-and-packing]] - 不规则切割与装箱问题的通用抽象。
- [[concepts/2d-irregular-strip-packing]] - 不规则条带装箱的约束与目标。
- [[concepts/collision-detection-engine-for-2d-nesting]] - `hazards`、保守碰撞判断与几何/优化解耦。

### 来源

- [[sources/gardeyn-open-source-collision-detection-engine]] - 2025 年 `CDE / jagua-rs` 论文来源页。
- [[sources/gardeyn-open-source-2d-nesting-heuristic]] - 2026 年 `sparrow / 2DISPP` 论文来源页。
