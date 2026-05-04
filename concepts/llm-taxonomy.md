# LLM Taxonomy

## 目的

这个页面提供当前 wiki 的概念地图，帮助后续新来源知道该把知识沉淀到哪里。

## 架构

- [[concepts/transformer-block]]：大多数 LLM 的基本骨架。
- [[concepts/attention]]：缩放点积注意力的基础数学形式。
- [[concepts/multi-head-attention]]：标准 `MHA` 的多头拆分、拼接与输出投影。
- [[concepts/mixture-of-experts]]：前馈层稀疏化与专家路由。
- [[concepts/grouped-query-attention]]：通过共享 `K/V` 降低缓存成本。
- [[concepts/multi-head-latent-attention]]：`DeepSeek-V3` 报告中的注意力改造。
- [[concepts/attention-for-long-context]]：围绕 `CSA/HCA` 的长上下文注意力线索。
- [[concepts/manifold-constrained-hyper-connections]]：`DeepSeek-V4` 残差路径改造。

## 位置编码与归一化

- [[concepts/rope]]：旋转位置编码。
- [[concepts/rmsnorm]]：现代 decoder-only 模型常见归一化。

## 训练目标与后训练

- [[concepts/policy-gradient]]：直接优化随机策略的基础路线。
- [[concepts/proximal-policy-optimization]]：经典稳定化策略梯度与 `RLHF` 基线之一。
- [[concepts/multi-token-prediction]]：多步未来预测目标。
- [[concepts/rlhf-dpo-grpo]]：偏好优化与后训练总览。
- [[concepts/on-policy-distillation]]：后训练末段的统一化蒸馏。

## 优化器与数值效率

- [[concepts/adamw]]：标准优化器基线。
- [[concepts/muon-optimizer]]：`DeepSeek-V4` 提到的优化器升级。
- [[concepts/fp8-training]]：低精度训练路线之一。
- [[concepts/fp4-quantization-aware-training]]：更激进的低精度量化感知训练。

## 推理与系统

- [[concepts/kv-cache]]：自回归推理的基础缓存机制。
- [[concepts/flashattention]]：attention kernel 与 IO 优化。
- [[concepts/auxiliary-loss-free-load-balancing]]：`MoE` 路由与专家负载控制。

## 说明

这个 taxonomy 不是固定不变的学科树，而是当前 wiki 的工作性索引。随着来源增加，它会继续拆分、合并或重命名。
