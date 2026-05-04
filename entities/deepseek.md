# DeepSeek

## 概述

DeepSeek 是当前这个 wiki 的主要来源簇，但不是这个 wiki 的最终本体。这里真正要维护的是“大模型知识”，而不是某一家模型公司的档案。因此，DeepSeek 页面主要承担两个作用：

- 提供具体模型与术语实例；
- 把可复用的设计抽取到 `concepts/`。

当前原始资料覆盖了该家族的两个相邻代际：

- [[models/deepseek-v3]]：一个以训练效率为核心叙事的大规模 `MoE` 模型，报告给出 `671B` 总参数、每 token 激活 `37B` 参数、`14.8T` 预训练 token，以及 `128K` 上下文扩展。
- [[models/deepseek-v4]]：一个以超长上下文与 agent 场景为核心叙事的预览系列，包含 `DeepSeek-V4-Pro` 与 `DeepSeek-V4-Flash` 两个子型号，重点放在 `1M token` 上下文、注意力压缩、优化器升级与更激进的精度方案上。

从这两份报告中可以抽出的连续主线是：DeepSeek 持续采用 `MoE` 骨架，持续把系统设计视为研究贡献的一部分，并且把目标从 `V3` 的训练成本效率，推进到 `V4` 的长上下文推理效率与 agent 工作负载适配。

## 相关模型

- [[models/deepseek-v3]]
- [[models/deepseek-v4]]

## 相关来源

- [[sources/deepseek-v3-technical-report]]
- [[sources/deepseek-v4-technical-report]]

## 由该来源簇引出的概念页

- [[concepts/mixture-of-experts]]
- [[concepts/multi-head-latent-attention]]
- [[concepts/multi-token-prediction]]
- [[concepts/auxiliary-loss-free-load-balancing]]
- [[concepts/fp8-training]]
- [[concepts/attention-for-long-context]]
- [[concepts/manifold-constrained-hyper-connections]]
- [[concepts/muon-optimizer]]
- [[concepts/fp4-quantization-aware-training]]
- [[concepts/on-policy-distillation]]

## 待补充

- 补充非 DeepSeek 来源，避免概念页长期继承单一厂商叙事。
- 补充组织层面的时间线、产品线与模型谱系。
- 随着更多来源进入，拆分 `DeepSeek-V3.2`、`DeepSeek-R1` 等关联型号页面。
