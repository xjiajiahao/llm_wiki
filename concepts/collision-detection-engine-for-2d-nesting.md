# Collision Detection Engine for 2D Nesting

## 它是什么

这里的 `Collision Detection Engine`（`CDE`）指一个把 `2D irregular C&P` 中几何可行性检测抽象出来的底层引擎。`Gardeyn` 2025 年论文给出的具体开源实现是 `jagua-rs`。

## 它要解决什么问题

`2D nesting` 的优化器想回答的是“怎样找到更好的摆放方案”，但它们往往先被更基础的问题卡住：

- 某个 item 放在某个位置是否会和别的 item 碰撞；
- 是否越出 container；
- 是否撞上 defect、quality zone 等额外空间约束。

如果这些几何判断没有通用引擎，每个算法都得从头实现，门槛高且难复用。

## 高层思路

这篇来源的核心主张是把几何和优化解耦：

- `CDE` 负责快速、保守且鲁棒地回答“这个 placement 是否可行”。
- 上层优化器只通过查询和更新接口与它交互，而不必掌握几何实现细节。

`2026` 年的 `sparrow` 就把 `jagua-rs` 当成底层几何服务来用。

## hazards 抽象

论文提出 `hazards` 作为统一空间约束抽象。若实体 `e` 诱导出的 hazard 为 `h`，其形状记为：

$$
S_h =
\begin{cases}
S_e & \text{若 } e \text{ 诱导 interior hazard} \\
S_e^c & \text{若 } e \text{ 诱导 exterior hazard}
\end{cases}
$$

若 container 当前 hazard 集合为 $H$，则：

$$
S_H = \bigcup_{h \in H} S_h
$$

对某个变换后的 item 形状 $S_i^T$，可行性条件写成：

$$
S_i^T \cap S_H = \varnothing
\iff
\forall h \in H: S_i^T \cap S_h = \varnothing
$$

这个抽象的意义是：item 碰撞、container 外部区域、quality zone 等都能被统一表示成 hazard。

## 论文强调的核心原则

根据当前来源，可稳定记下的四个关键词是：

- `hazards`：把不同空间约束统一成可碰撞对象。
- `two-phased approach`：先用更便宜的手段过滤，再做更精确的检查。
- `fail-fast surrogate`：先用保守 surrogate 尽快排除明显无效的 placement。
- `polygon simplification`：在不破坏保守性的前提下减少边数，降低查询与更新开销。

其中更细的实现细节，当前 wiki 先不脱离来源页单独展开。

## 为什么作者选择 trigonometry 路线

来源页把常见几何处理路线分成 raster、`NFP` 与 trigonometry。作者认为：

- raster 往往牺牲精度；
- `NFP` 需要鲁棒生成器，且高旋转自由度下预处理成本很高；
- trigonometry 在精度与鲁棒性上更强，但需要系统级优化来弥补速度劣势。

`jagua-rs` 的论点是：通过一系列工程和算法增强，trigonometric 路线也可以快到足以支撑竞争性优化器。

## 在本 wiki 中的实例

- [[sources/gardeyn-open-source-collision-detection-engine]]：`CDE / jagua-rs` 的来源页。
- [[sources/gardeyn-open-source-2d-nesting-heuristic]]：`sparrow` 把 `jagua-rs` 作为底层查询引擎。

## 相关页面

- [[concepts/2d-irregular-cutting-and-packing]]
- [[concepts/2d-irregular-strip-packing]]
- [[concepts/2d-nesting-taxonomy]]

## 待补充

- `two-phased approach` 与 `fail-fast surrogate` 的精确算法流程，当前仍应回到来源页核对。
- 如果后续加入更多几何论文，再拆独立页面比较 `raster / NFP / trigonometric` 路线。
