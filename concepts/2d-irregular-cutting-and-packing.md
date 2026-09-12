# 2D Irregular Cutting and Packing

## 它是什么

`2D irregular cutting and packing`（常简称 `2D irregular C&P`，也常被叫作 `nesting`）是一类把不规则二维形状放入更大容器中的优化问题。这里的“不规则”指 item、container，或两者都不是简单矩形。

## 它要解决什么问题

这类问题通常同时包含两层困难：

- 几何挑战：某个放置是否可行，也就是 item 是否完全在容器内、是否与其他 item 或禁区碰撞。
- 优化挑战：在满足可行性的前提下，怎样让解更好，例如减少用料、缩短条带长度、提高利用率，或减少容器数量。

`Gardeyn` 的两篇文章都强调，这两个挑战长期被绑在一起，导致研究门槛高、实现难复现。

## 常见问题变体

- `strip packing`：容器宽度固定、长度可变，目标通常是最小化长度。
- `bin packing`：容器数量有限或待决，目标通常是减少容器数或提高利用率。
- 带额外空间约束的真实工业问题：例如 defect、quality zone、工艺边界或旋转限制。

## 常见几何处理路线

根据 `Gardeyn` 2025 年的来源页，文中把常见路线概括为三类：

- raster：把形状离散成像素网格，鲁棒但有精度与内存代价。
- `no-fit polygon`：把碰撞区域预先编码成 `NFP`，查询快，但生成鲁棒 `NFP` 很难，且旋转自由度高时组合数爆炸。
- trigonometry：直接做几何相交/包含判断，精确、通用，但若没有额外优化，通常被认为太慢。

## 为什么“解耦几何和优化”重要

如果每个新算法都必须自己重做碰撞检测、容器边界判断、特殊约束建模和数值鲁棒性处理，那么：

- 新研究者进入门槛很高；
- 论文很难完整复现；
- 几何层改进无法被不同优化器自动复用。

这也是 [[concepts/collision-detection-engine-for-2d-nesting]] 试图解决的问题。

## 在本 wiki 中的实例

- [[sources/gardeyn-open-source-collision-detection-engine]]：提出 `CDE` 与 `jagua-rs`。
- [[sources/gardeyn-open-source-2d-nesting-heuristic]]：在 `CDE` 之上实现 `2DISPP` 启发式 `sparrow`。

## 相关页面

- [[concepts/2d-irregular-strip-packing]]
- [[concepts/collision-detection-engine-for-2d-nesting]]
- [[concepts/2d-nesting-taxonomy]]

## 待补充

- 更系统地整理各类 `nesting` 目标函数与 benchmark 族谱。
- 等来源更多后，再决定是否拆出 `NFP`、raster 与质量区约束等独立概念页。
