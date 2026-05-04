# DeepSeek-V4 Technical Report

## 来源记录

- 原始文件：`raw/DeepSeek-AI - 2026 - DeeppSeek-V4 Technical Report.pdf`
- 原始路径：[DeepSeek-AI - 2026 - DeeppSeek-V4 Technical Report.pdf](../raw/DeepSeek-AI%20-%202026%20-%20DeeppSeek-V4%20Technical%20Report.pdf)
- 文件名日期：`2026`
- 仓库文件时间戳：`2026-04-25`
- 文件大小：`4,479,907 bytes`
- SHA-256：`f4cbe4fcbd2888b25b2890a98cc6ef4ce0489df7c93e140b6f853c451d3f5c52`

## 摘要

这份报告把 `DeepSeek-V4` 描述为一个围绕百万 token 上下文效率构建的预览系列。根据当前首轮抽取，摘要层面的重点有：

- 两个型号：
  - `DeepSeek-V4-Pro`：总参数 `1.6T`，激活参数 `49B`
  - `DeepSeek-V4-Flash`：总参数 `284B`，激活参数 `13B`
- 结构升级集中在：
  - 基于 `CSA` 与 `HCA` 的混合长上下文注意力
  - 用 `mHC` 强化残差路径
  - 用 `Muon` 改进收敛速度与训练稳定性
  - 用 `FP4 quantization-aware training` 与额外推理基础设施降低长上下文成本

## 章节提纲

- `1` 引言（Introduction）
- `2` 架构（Architecture）
- `3` 通用基础设施（General Infrastructures）
- `4` 预训练（Pre-Training）
- `5` 后训练（Post-Training）
- `6` 结论、局限与未来方向（Conclusion, Limitations, and Future Directions）

## 值得记录的说法

- 两个模型都在预训练后原生支持 `1M token` 上下文。
- 在 `1M token` 场景下，报告称 `DeepSeek-V4-Pro` 的单 token 推理 FLOPs 只需要 `DeepSeek-V3.2` 的 `27%`，KV cache 只需要 `10%`。
- 报告称 `DeepSeek-V4-Flash` 可进一步降到 `DeepSeek-V3.2` 的 `10%` 单 token FLOPs 与 `7%` KV cache。
- 预训练规模报告为：`V4-Flash` 使用 `32T tokens`，`V4-Pro` 使用 `33T tokens`。
- `CSA` 的正式机制是：先把每 `m` 个 token 的 `KV` 压成一个 compressed entry，再用 lightning indexer 对这些压缩条目做 top-k 稀疏选择，最后在选中条目上做共享 `KV` 的 `MQA`。
- `HCA` 的正式机制是：把每 `m'` 个 token 的 `KV` 压成一个 compressed entry，其中 $m' \gg m$，再直接在全部压缩条目上做共享 `KV` 的 `MQA`，不再做稀疏选择。
- `CSA/HCA` 共同引入了额外 `RMSNorm`、partial `RoPE`、sliding window branch 和 attention sink，用于稳定训练并补足局部依赖。
- `mHC` 的核心是把残差映射矩阵约束到双随机矩阵流形上，并通过 `Sinkhorn-Knopp` 投影增强深层训练稳定性。
- `Muon` 被用作大多数模块的主优化器；报告给出完整算法，并使用 `hybrid Newton-Schulz` 迭代做矩阵正交化更新。
- `FP4 QAT` 被应用到 `MoE` expert weights 和 `CSA` indexer 的 `QK` 路径；其中 index scores 从 `FP32` 量化到 `BF16` 可将 top-k selector 加速 `2x`，同时保持 `99.7%` 的 KV entry recall。
- `DeepSeek-V4-Flash` 的 attention 配置是：`CSA m=4`、top-k=`512`、`HCA m'=128`、`n_h=64`、`c=512`、`d_c=1024`、`g=8`、`d_g=1024`、`n_win=128`。
- `DeepSeek-V4-Pro` 的 attention 配置是：`CSA m=4`、top-k=`1024`、`HCA m'=128`、`n_h=128`、`c=512`、`d_c=1536`、`g=16`、`d_g=1024`、`n_win=128`。
- 两个模型都从 `4K` 序列长度起步，逐步扩展到 `16K`、`64K`、`1M`；前 `1T tokens` 使用 dense attention warmup，并在 `64K` 阶段引入 sparse attention 与 `CSA` lightning indexer warmup。

## 关联页面

- [[entities/deepseek]]
- [[models/deepseek-v4]]
- [[notes/deepseek-v3-v4-comparison]]

## 备注

- 原始文件名里写的是 `DeeppSeek-V4`，包含双 `p`。本 wiki 将页面标题规范化为 `DeepSeek-V4`，但保留原始文件名以便校验。

## 待继续处理

- 抽取报告里的评测与消融证据，区分“结构收益”和“系统收益”。
- 判断哪些 `V4` 设计已经足够稳定，可以升级成更通用的概念页。
- 如果继续细化，可单独整理 `Flash` 与 `Pro` 的完整训练超参数表。
