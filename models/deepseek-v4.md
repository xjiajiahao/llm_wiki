# DeepSeek-V4

## 状态

已基于 [[sources/deepseek-v4-technical-report]] 完成首轮整理。本页聚焦于 `V4` 相对 `V3` 的结构升级与叙事重心变化；更细的技术细节仍需随着更多来源继续核验。

## 来源骨架

- [[sources/deepseek-v4-technical-report]]

## 已知事实

- 模型/报告名：`DeepSeek-V4`
- 系列组成：`DeepSeek-V4-Pro`、`DeepSeek-V4-Flash`
- 规模：
  - `V4-Pro`：总参数 `1.6T`，激活参数 `49B`
  - `V4-Flash`：总参数 `284B`，激活参数 `13B`
- 上下文目标：原生支持 `1M token`
- 预训练规模：
  - `V4-Flash`：`32T tokens`
  - `V4-Pro`：`33T tokens`
- 相对 `V3` 的升级关键词：`CSA`、`HCA`、`mHC`、`Muon`、`FP4 quantization-aware training`

## 关键架构配置

- `DeepSeek-V4-Flash`
  - `43` 层，隐藏维度 `4096`
  - 前 `2` 层用纯 sliding window attention，后续层交错使用 `CSA/HCA`
  - `CSA`：`m=4`，`n_h^I=64`，`c_I=128`，top-k=`512`
  - `HCA`：`m'=128`
  - 共享 attention 配置：`n_h=64`，`c=512`，`d_c=1024`，`g=8`，`d_g=1024`，`n_win=128`
- `DeepSeek-V4-Pro`
  - `61` 层，隐藏维度 `7168`
  - 前 `2` 层用 `HCA`，后续层交错使用 `CSA/HCA`
  - `CSA`：`m=4`，`n_h^I=64`，`c_I=128`，top-k=`1024`
  - `HCA`：`m'=128`
  - 共享 attention 配置：`n_h=128`，`c=512`，`d_c=1536`，`g=16`，`d_g=1024`，`n_win=128`

## 核心结论

- `V4` 延续了 `MoE + MTP` 的基本骨架，但明显把资源重新投向长上下文推理和 agent 场景，而不是只追求常规 benchmark 扩张。
- 相比 `V3`，注意力机制成为最大的结构性改动之一：报告强调 `CSA + HCA` 的混合注意力，以降低 `1M token` 场景下的 FLOPs 与 KV cache 成本。
- 从具体配置上看，`Flash` 和 `Pro` 共享相同的 `CSA/HCA` 压缩率，但 `Pro` 通过更多 query heads、更大的 query 压缩维度和更高 top-k 提升检索容量。
- 报告同时引入 `mHC`、`Muon` 与 `FP4` 方案，说明 `V4` 的效率故事不是单点优化，而是架构、优化器、数值格式和推理系统的联合改造。
- 现有来源集对这些新概念的数学细节披露仍有限，因此本 wiki 中相关概念页会保留“已知用途”和“待核验机制”的分层写法。

## 在本 wiki 中实例化的概念

- [[concepts/mixture-of-experts]]
- [[concepts/multi-token-prediction]]
- [[concepts/attention-for-long-context]]
- [[concepts/manifold-constrained-hyper-connections]]
- [[concepts/muon-optimizer]]
- [[concepts/fp4-quantization-aware-training]]
- [[concepts/on-policy-distillation]]

## 建议重点阅读的报告部分

- 架构（Architecture）
- 通用基础设施（General Infrastructures）
- 预训练（Pre-Training）
- 后训练（Post-Training）
- 结论、局限与未来方向（Conclusion, Limitations, and Future Directions）

## 待继续抽取

- `CSA` 与 `HCA` 的更正式定义、压缩策略与复杂度表达。
- `mHC` 的具体计算图与它相对标准 residual 的区别。
- `Muon` 的更新规则、状态量与适用参数类型。
