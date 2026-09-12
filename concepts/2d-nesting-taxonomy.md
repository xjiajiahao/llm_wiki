# 2D Nesting Taxonomy

## 目的

这个页面提供当前 wiki 中 `2D nesting` / `2D irregular cutting and packing` 方向的概念地图。

## 问题与任务

- [[concepts/2d-irregular-cutting-and-packing]]：`2D irregular C&P` 的总览，区分几何挑战与优化挑战。
- [[concepts/2d-irregular-strip-packing]]：`2DISPP` 的条带装箱定义、形式化约束，以及“把优化转成一串可行性问题”的思路。

## 几何与可行性

- [[concepts/collision-detection-engine-for-2d-nesting]]：把几何可行性检测从优化里解耦出来的 `CDE` 思路。

## 来源簇

- [[sources/gardeyn-open-source-collision-detection-engine]]：`jagua-rs` 与 `CDE` 的来源页。
- [[sources/gardeyn-open-source-2d-nesting-heuristic]]：`sparrow` 与 `2DISPP` 启发式的来源页。

## 备注

- 当前 taxonomy 仍以 `Gardeyn` 这组来源为中心。
- 若后续引入更多 `nesting` 论文，可继续拆出 `NFP`、raster、trigonometric collision detection、benchmark 等独立概念页。
