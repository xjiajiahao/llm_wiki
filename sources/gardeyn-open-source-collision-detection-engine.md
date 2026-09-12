# Decoupling Geometry from Optimization in 2D Irregular Cutting and Packing Problems

## 来源记录

- 原始文件：`raw/Gardeyn 等 - 2025 - Decoupling Geometry from Optimization in 2D Irregular Cutting and Packing Problems an Open-Source C.pdf`
- 原始路径：[Gardeyn 等 - 2025 - Decoupling Geometry from Optimization in 2D Irregular Cutting and Packing Problems an Open-Source C.pdf](../raw/Gardeyn%20%E7%AD%89%20-%202025%20-%20Decoupling%20Geometry%20from%20Optimization%20in%202D%20Irregular%20Cutting%20and%20Packing%20Problems%20an%20Open-Source%20C.pdf)
- 文件名日期：`2025`
- 仓库文件时间戳：`2026-04-25`
- 文件大小：`1,004,673 bytes`
- SHA-256：`ee43300a41f7f958d6c288cc69ece0af4170eeda6084a7f869effc1389858e65`

## 书目信息

- 标题：`Decoupling Geometry from Optimization in 2D Irregular Cutting and Packing Problems: an Open-Source Collision Detection Engine`
- 作者：`Jeroen Gardeyn`、`Greet Vanden Berghe`、`Tony Wauters`
- 版本线索：`Author-accepted manuscript`
- 期刊线索：`INFORMS Journal on Computing`
- DOI：`10.1287/ijoc.2024.1025`
- arXiv 线索：`arXiv:2508.08341v4`

## 摘要

这篇论文的主张是：`2D irregular cutting and packing` 长期被同时卡在“几何可行性检测”和“优化搜索”两件事上，而几何部分本应被抽象成可复用基础设施。作者因此提出一个开源 `Collision Detection Engine`（`CDE`），并给出 Rust 实现 `jagua-rs`。

根据当前抽取，这篇文章的 durable 要点包括：

- 明确区分两类挑战：
  - 几何挑战：placement 是否与 item、container 边界或额外空间约束碰撞。
  - 优化挑战：在可行解空间里找到更高质量布局。
- 把常见几何路线概括为：
  - raster
  - `no-fit polygon`
  - trigonometry
- 作者选择以 trigonometry 为基础，因为它在精度和鲁棒性上最强，但需要额外工程手段把速度做上来。
- 论文提出的核心设计关键词是：
  - `hazards`
  - `two-phased approach`
  - `fail-fast surrogate`
  - `polygon simplification`
- `hazards` 被用来统一表达 item、container 外部区域，以及 `quality zones` 这类额外空间约束。
- 文中把 `jagua-rs` 的价值说成“让研究者可以把几何问题外包出去，专注于上层优化器”。
- 论文明确把后续 `sparrow` 视为验证 `jagua-rs` 设计是否真的够强的上层应用。

## 值得记录的公式与定义

来源给出 hazard 形状定义：

$$
S_h =
\begin{cases}
S_e & \text{若 } e \text{ 诱导 interior hazard} \\
S_e^c & \text{若 } e \text{ 诱导 exterior hazard}
\end{cases}
$$

并把可行放置写成：

$$
S_H = \bigcup_{h \in H} S_h
$$

$$
S_i^T \cap S_H = \varnothing
\iff
\forall h \in H: S_i^T \cap S_h = \varnothing
$$

对于 polygon simplification，来源还要求简化后的 hazard 必须保守覆盖原 hazard：

$$
S_h \subseteq S_h'
$$

这意味着 interior hazard 只能向外膨胀，exterior hazard 只能向内收缩。

## 章节线索

- `1` 引言
- `2` `2D irregular C&P` 中处理几何的通用路线
- `5` `hazards`
- `8` `polygon simplification`
- `10` 验证与评测
- `11` 结论

## 开源实现线索

- `jagua-rs` GitHub：`https://github.com/JeroenGar/jagua-rs`
- 文中描述其目标是支持不规则 item 与 container、连续旋转与平移，并可扩展到更多空间约束。

## 关联页面

- [[concepts/2d-irregular-cutting-and-packing]]
- [[concepts/collision-detection-engine-for-2d-nesting]]
- [[concepts/2d-irregular-strip-packing]]
- [[sources/gardeyn-open-source-2d-nesting-heuristic]]

## 待继续处理

- `two-phased approach` 与 `fail-fast surrogate` 的正文细节还没有完整抄清。
- 若后续继续围绕该文展开，可单独整理 `raster / NFP / trigonometric` 三路线比较。
- `jagua-rs` 的分层架构图和 benchmark 细节，当前还只在来源页层面记录。
