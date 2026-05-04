# DeepSeek-V3 Technical Report

## 来源记录

- 原始文件：`raw/DeepSeek-AI et al. - 2024 - DeepSeek-V3 Technical Report.pdf`
- 原始路径：[DeepSeek-AI et al. - 2024 - DeepSeek-V3 Technical Report.pdf](../raw/DeepSeek-AI%20et%20al.%20-%202024%20-%20DeepSeek-V3%20Technical%20Report.pdf)
- 文件名日期：`2024`
- 首页报告日期：`2024-12-27`，来自 `arXiv:2412.19437v1`
- 仓库文件时间戳：`2025-02-06`
- 文件大小：`1,887,607 bytes`
- SHA-256：`a67e18a4ca6e2c81abc030239a3ee53705f656b79efab8ce1d6b5ac25630c2a5`

## 摘要

这份报告把 `DeepSeek-V3` 描述为一个“超大规模但强调效率”的 `MoE` 模型。根据摘要和引言，当前可直接抽出的四个主线是：

- 总参数 `671B`，但每个 token 只激活 `37B` 参数。
- 延续 `V2` 线的 `MLA` 与 `DeepSeekMoE`，目标是降低推理和训练成本。
- 两个重点模型级改动是 `auxiliary-loss-free load balancing` 与 `multi-token prediction`。
- 报告给出很强的系统效率声明：在 `14.8T` 预训练 token 下，完整训练只需 `2.788M H800 GPU hours`。

## 章节提纲

- `1` 引言（Introduction）
- `2` 架构（Architecture）
- `3` 基础设施（Infrastructures）
- `4` 预训练（Pre-Training）
- `5` 后训练（Post-Training）
- `6` 结论、局限与未来方向（Conclusion, Limitations, and Future Directions）

## 值得记录的说法

- 报告称完整训练过程中没有发生不可恢复的 loss spike，也没有回滚。
- 报告把 `FP8` 混合精度训练描述为超大模型场景下的一次大规模验证。
- 上下文长度分两阶段扩展：先到 `32K`，再到 `128K`。
- 后训练包含 `SFT`、`RL` 与来自 `DeepSeek-R1` 系列的推理蒸馏。
- `MLA` 的正文给出较完整公式：对 `K/V` 做联合低秩压缩，只缓存压缩 latent $c_t^{KV}$ 与解耦的 RoPE key 分量 $k_t^R$，以显著缩小推理期 `KV cache`。
- 报告同时对 query 做低秩压缩，用来降低训练时激活内存，而最终注意力仍由拼接后的内容分量与 RoPE 分量共同计算。

## 关联页面

- [[entities/deepseek]]
- [[models/deepseek-v3]]
- [[notes/deepseek-v3-v4-comparison]]

## 待继续处理

- 抽取 benchmark 表格并整理成可引用数据。
- 抽取限制与未来工作部分的明确表述。
- 对 `MLA`、`DeepSeekMoE`、并行系统和训练栈做更细颗粒拆解。
