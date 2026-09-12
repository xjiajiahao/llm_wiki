# 2D Irregular Strip Packing

## 它是什么

`2D irregular strip packing problem`（`2DISPP`）是在固定宽度、可变长度的矩形条带中摆放不规则 item 的问题，目标通常是让条带长度尽可能短。

## 它要解决什么问题

相比一般 `2D irregular C&P`，`2DISPP` 的 container 形状固定为矩形条带，因此优化目标更集中：在保证所有 item 都在条带内且互不碰撞的前提下，最小化长度。

这也是 `Gardeyn` 2026 年论文用来展示开源启发式 `sparrow` 的主问题。

## 形式化定义

按来源页给出的记号，item 集合记为 $I$，条带宽度为 $w$、长度为 $l$，每个 item 的刚体变换记为 $t_i$。问题可写成：

$$
\min l
$$

约束包括：

$$
t_i(S_i) \subseteq [0,w] \times [0,l] \quad \forall i \in I
$$

$$
t_a(S_a) \cap t_b(S_b) = \varnothing \quad \forall a,b \in I, a \ne b
$$

$$
t_i \in \mathbb{R}^2 \times [0,2\pi[ \times \{0,1\} \quad \forall i \in I
$$

这里的变换包含平移，以及按问题设定允许的旋转和反射。来源同时说明：真实论文里常见的是连续平移加离散旋转，连续旋转与反射并不总是开放。

## 一个关键重写：sequence of feasibility problems

`sparrow` 的核心想法不是直接在目标函数上做一次性优化，而是把问题改写成一串固定长度的可行性问题：

- 先固定条带长度 $l$；
- 暂时允许 item 之间发生碰撞；
- 再通过局部搜索逐步消除碰撞，尝试恢复可行性；
- 若恢复成功，再进一步缩短条带。

来源文中明确把这个思路称为 `a sequence of feasibility problems`。它和很多只讨论“最小重叠量”的表述不同，更强调真正的目标是“消除重叠直到可行”。

## `sparrow` 中的高层流程

根据当前来源，可稳定概括为两阶段：

- `exploration phase`：从一个可行初解出发，较大幅度缩短条带；若分离失败，则从 infeasible local optimum 池中挑选方案并通过交换大 item 重新扰动，再继续尝试。
- `compression phase`：始终从当前最好可行解恢复，做更小、更保守的缩短，只求在不大幅改变整体布局的前提下继续压缩长度。

这种分工对应“先保留自由度找结构，再在好结构附近抠最后一点紧致度”。

## 碰撞严重度的度量

来源指出，`jagua-rs` 提供的是二值碰撞判断，而局部搜索还需要“碰撞有多严重”的连续信号。`sparrow` 没有直接用精确 penetration depth，而是构造了基于 pole 的 overlap proxy，并在小重叠区域加入 decaying penetration depth，以便：

- 支持连续旋转；
- 对复杂多边形边数不那么敏感；
- 给 minor collision 也提供平滑搜索信号。

更细的算法与公式，后续若继续围绕这篇论文深挖，可以再拆单独页面。

## 在本 wiki 中的实例

- [[sources/gardeyn-open-source-2d-nesting-heuristic]]：`sparrow` 的来源页。
- [[sources/gardeyn-open-source-collision-detection-engine]]：底层 `jagua-rs / CDE` 来源页。

## 相关页面

- [[concepts/2d-irregular-cutting-and-packing]]
- [[concepts/collision-detection-engine-for-2d-nesting]]
- [[concepts/2d-nesting-taxonomy]]

## 待补充

- `sparrow` 的 `separate`、candidate move、并行搜索与参数表，当前还没整理成稳定概念层。
- benchmark 与 `GARDEYN0-9` 新实例集可在后续来源增加时单独成页。
