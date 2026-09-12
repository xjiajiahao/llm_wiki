# 日志

## [2026-05-03] bootstrap | 仓库初始化

- 根据 `llm-wiki.md` 建立 wiki 基本结构。
- 在 `AGENTS.md` 中加入维护 schema。
- 创建索引、日志、实体页、模型页、来源页与初始化笔记页。
- 登记两份现有 DeepSeek PDF 原始报告。

## [2026-05-03] ingest | DeepSeek 技术报告首轮摄取

- 安装本地 PDF 抽取依赖 `pypdf`，用于读取原始报告。
- 抽取 `V3` 与 `V4` 报告的开头页面和章节提纲。
- 将来源页从元数据占位稿升级为首轮摘要。
- 增加模型级摘要和跨代比较笔记。

## [2026-05-03] refactor | 转为概念优先的 wiki 结构

- 将仓库重新定位为“大模型知识 wiki”，而不是仅面向 DeepSeek 的资料夹。
- 更新 schema，明确可复用知识优先落到 `concepts/`。
- 增加架构、目标、精度、优化与长上下文机制等概念页。
- 更新索引和模型/实体页，使 DeepSeek 被视为概念抽取的来源簇。

## [2026-05-03] expand | 扩展基础概念层

- 增加 `transformer block`、`RoPE`、`RMSNorm`、`GQA`、`FlashAttention`、`KV cache`、`AdamW`、`RLHF/DPO/GRPO` 等基础页面。
- 增加顶层 taxonomy 页面，便于后续来源稳定落位。
- 更新主索引和 `README`，让入口转向概念优先浏览。

## [2026-05-03] normalize | 中文化与概念页深化

- 将 wiki 入口页、索引、实体页、模型页、来源页和笔记页统一为中文表述。
- 将概念页重写为“定义、问题、机制、公式、流程、超参数/权衡”的结构。
- 将原先用反引号书写的公式改为 Markdown 数学公式。
- 对来源不足以支撑的细节显式标记为“待补充”或“待核验”。

## [2026-05-03] deepen | 从技术报告补全 MLA、mHC、Muon 与 FP4

- 从 `DeepSeek-V3` 技术报告 `2.1.1` 节抽取 `MLA` 的正式结构与公式。
- 从 `DeepSeek-V4` 技术报告 `2.2`、`2.4`、`3.4` 节抽取 `mHC`、`Muon`、`FP4 QAT` 的正文机制。
- 将对应概念页升级为基于原文的可核验版本，并同步更新来源页摘要。

## [2026-05-03] deepen | 从技术报告补全 CSA 与 HCA

- 从 `DeepSeek-V4` 技术报告 `2.3` 节抽取 `CSA/HCA` 的正式结构与公式。
- 将长上下文注意力页升级为包含压缩、indexer、共享 `KV` MQA、滑窗分支与 attention sink 的正式概念页。
- 同步更新 `DeepSeek-V4` 来源页摘要、主索引与日志。

## [2026-05-03] deepen | 抽取 DeepSeek-V4 的 CSA/HCA 超参数

- 从 `4.2.1 Model Setups` 和 `4.2.2 Training Setups` 中抽取 `CSA/HCA` 的具体配置。
- 补充 `Flash` 与 `Pro` 的压缩率、top-k、head 数、query 压缩维度、输出分组与滑窗大小。
- 记录稀疏注意力的引入时机：`1T tokens` dense warmup、`64K` 阶段引入 sparse attention 与 indexer warmup。

## [2026-05-04] tool | PDF 论文公式抽取 workflow skill

- 在 `skills/pdf-paper-formula-workflow/` 下创建可复用 skill。
- 增加 `extract_pdf_context.py`，支持按页和按关键词抽取 PDF 局部上下文。
- 将“原生文本 PDF 优先、局部页窗口抽取、保守公式重建、跨模型适配”整理为可复用 skill 工作流。

## [2026-05-03] expand | 补充基础 attention 与 MHA 概念页

- 新增基础 `attention` 页面，统一采用输入矩阵 $n \times d$ 的形状约定。
- 补充 `Q/K/V` 投影、score 矩阵、softmax 权重、因果掩码与输出形状推导。
- 新增 `multi-head attention` 页面，说明多头拆分、每头计算、拼接与输出投影。
- 更新 taxonomy、transformer block 相关页与主索引，补上这两层基础概念入口。

## [2026-05-04] ingest | 摄取 PPO 讲解问答 JSON

- 为 `raw/讲解PPO算法：近端策略优化-20260318211727.json` 新建来源页，记录元数据、来源性质与可稳定抽出的要点。
- 新增 `policy gradient` 与 `PPO` 两个概念页，把策略梯度、clip 目标、`GAE` 与 `LLM RLHF` 中的奖励分配整理成可复用知识。
- 更新 `RLHF/DPO/GRPO` 总览页，补充经典 `PPO` 型 `RLHF` 的位置与 token 级 `KL` 正则说明。
- 同步更新 taxonomy 与主索引。

## [2026-05-04] deepen | 补充 PPO 对话中的降方差与 RLHF 奖励解释

- 在 `policy gradient` 页面补入 baseline 不改变期望梯度、但可降低方差的推导。
- 在 `PPO` 页面补入 `V_old`、`V_target`、critic 冷启动与 value clipping 的解释，并保留实现差异的待核验边界。
- 在 `RLHF/DPO/GRPO` 页面补入序列级奖励、末端总分注入、逐 token `KL` 惩罚与 critic 信用分配机制。
- 更新来源页摘要与主索引描述，反映这次深化。

## [2026-05-04] deepen | 补全 policy gradient 的降方差解释

- 在 `policy gradient` 页面补充 baseline 如何通过最小化条件二阶矩来降低方差，而不只是保持无偏。
- 增加最优 baseline 的形式、与 `V(s)` 之间的近似关系，以及“去掉状态级公共噪声”的直觉说明。

## [2026-05-04] refactor | 将仓库内绝对路径改为相对路径

- 将 `sources/` 页面中指向 `raw/` 的绝对文件路径统一改为相对路径，便于跨机器使用。
- 将 `README.md` 中指向仓库内页面的绝对路径链接改为相对链接。
- 在 `index.md` 同步记录来源页原始路径链接采用相对 `raw/` 路径的约定。

## [2026-06-06] refactor | 从 LLM wiki 扩展为跨领域研究 wiki

- 将仓库入口与 `AGENTS.md` 从“大模型知识 wiki”改写为可容纳多个研究方向的研究 wiki。
- 新增仓库级 [[concepts/research-taxonomy]]，并把 `index.md` 改为“跨领域总览 + 领域分区”结构。
- 保留 `concepts/` 优先原则，同时明确 `models/` 目录目前主要服务于大模型领域。

## [2026-06-06] ingest | 摄取两篇 Gardeyn 的 2D Nesting 论文

- 为 `Gardeyn` 的 `CDE / jagua-rs` 论文与 `sparrow / 2DISPP` 论文各建立一个 `sources/` 页面，记录元数据、摘要、公式与待继续处理项。
- 新增 `2D nesting taxonomy`、`2D irregular C&P`、`2D irregular strip packing` 与 `collision detection engine for 2D nesting` 四个概念页。
- 在索引中增加 `2D Nesting` 领域分区，把来源页和概念页纳入主入口。
