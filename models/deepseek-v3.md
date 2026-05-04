# DeepSeek-V3

## 状态

已基于 [[sources/deepseek-v3-technical-report]] 完成首轮整理。本页当前记录报告中可直接核验的核心事实与可复用设计；更细的章节级抽取仍可继续深化。

## 来源骨架

- [[sources/deepseek-v3-technical-report]]

## 已知事实

- 模型/报告名：`DeepSeek-V3`
- 报告标识：`arXiv:2412.19437v1`
- 架构关键词：`MoE`、`MLA`、`DeepSeekMoE`
- 规模：总参数 `671B`，每 token 激活参数 `37B`
- 预训练数据量：`14.8T tokens`
- 上下文扩展：先到 `32K`，再到 `128K`
- 训练效率声明：完整训练总计 `2.788M H800 GPU hours`

## 核心结论

- `DeepSeek-V3` 的主叙事不是“做一个更大的 dense 模型”，而是“把超大规模 `MoE` 训练与推理做得足够经济”。
- 模型层面的重点贡献集中在两点：`multi-token prediction` 和 `auxiliary-loss-free load balancing`。
- 系统层不是附属配角，而是主角之一：`FP8`、流水并行、跨节点通信内核与内存优化被当作规模化前提条件来叙述。
- 后训练阶段包含 `SFT`、`RL` 与来自 `DeepSeek-R1` 系列的推理蒸馏，这表明其目标不仅是基座能力，也包括推理与对话行为。

## 在本 wiki 中实例化的概念

- [[concepts/mixture-of-experts]]
- [[concepts/multi-head-latent-attention]]
- [[concepts/multi-token-prediction]]
- [[concepts/auxiliary-loss-free-load-balancing]]
- [[concepts/fp8-training]]

## 建议重点阅读的报告部分

- 架构（Architecture）
- 基础设施（Infrastructures）
- 预训练（Pre-Training）
- 后训练（Post-Training）
- 结论、局限与未来方向（Conclusion, Limitations, and Future Directions）

## 待继续抽取

- 报告中的 benchmark 表格与任务分类。
- `DeepSeekMoE`、`MLA` 与训练并行栈的更细机制。
- 哪些结论是 `V3` 特有的，哪些应该上升为通用概念页。
