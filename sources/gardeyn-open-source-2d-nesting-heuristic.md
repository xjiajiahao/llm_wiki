# An Open-Source Heuristic to Reboot 2D Nesting Research

## 来源记录

- 原始文件：`raw/Gardeyn 等 - 2026 - An open-source heuristic to reboot 2D nesting research.pdf`
- 原始路径：[Gardeyn 等 - 2026 - An open-source heuristic to reboot 2D nesting research.pdf](../raw/Gardeyn%20%E7%AD%89%20-%202026%20-%20An%20open-source%20heuristic%20to%20reboot%202D%20nesting%20research.pdf)
- 文件名日期：`2026`
- 仓库文件时间戳：`2026-04-25`
- 文件大小：`4,254,599 bytes`
- SHA-256：`8452eef76ad9fd77734a05bbe0e423f9cb30a5145b0640ebccc77512712c81df`

## 书目信息

- 标题：`An open-source heuristic to reboot 2D nesting research`
- 作者：`Jeroen Gardeyn`、`Greet Vanden Berghe`、`Tony Wauters`
- arXiv 线索：`arXiv:2509.13329v3`

## 摘要

这篇论文在 `jagua-rs` 的几何基础设施之上，提出一个面向 `2D irregular strip packing problem`（`2DISPP`）的开源启发式 `sparrow`。作者的核心叙事不是“又一个 heuristic”，而是：

- 用开源可复现实现打破 `2D nesting` 长期停滞；
- 证明这个问题远未被优化到近最优；
- 用新 benchmark 暴露旧 benchmark 的盲点。

根据当前抽取，这篇文章的 durable 要点包括：

- `2DISPP` 被定义为：在固定宽度 `w`、可变长度 `l` 的矩形条带中放置不规则 item，目标最小化 `l`。
- 论文明确把主问题改写成 `a sequence of feasibility problems`：
  - 固定条带长度；
  - 允许暂时碰撞；
  - 通过局部搜索逐步消除碰撞；
  - 成功后继续缩短条带。
- `sparrow` 依赖 `jagua-rs` 回答“当前 placement 会撞到谁”，通过 query/update 接口把几何检测外包给 `CDE`。
- 为了让局部搜索有连续信号，作者没有直接依赖精确 penetration depth，而是构造基于 pole 的 overlap proxy，并为 minor collision 加入 decaying penetration depth。
- 算法整体分成两个阶段：
  - `exploration phase`
  - `compression phase`
- `exploration` 阶段在更大自由度下寻找结构；失败的局部最优会存入池中，再通过交换大 item 生成新起点。
- `compression` 阶段始终从当前最好可行解恢复，只做较小幅度压缩。
- 论文把 `sparrow` 描述为新的学术和开源 state of the art，并新增 `GARDEYN0-9` 十个真实世界导向 benchmark。
- 文中还点出一个重要弱点：对高同质实例，`sparrow` 能局部形成紧凑 pattern，但缺乏把 pattern 大规模重复铺开的机制。

## 值得记录的公式与定义

来源给出的 `2DISPP` 形式化可写成：

$$
\min l
$$

$$
t_i(S_i) \subseteq [0,w] \times [0,l] \quad \forall i \in I
$$

$$
t_a(S_a) \cap t_b(S_b) = \varnothing \quad \forall a,b \in I, a \ne b
$$

$$
t_i \in \mathbb{R}^2 \times [0,2\pi[ \times \{0,1\} \quad \forall i \in I
$$

在碰撞严重度量化部分，当前可稳定记录的是两点：

- 旧工作常用某种 `penetration depth` 变体。
- `sparrow` 改为用基于 pole 的 overlap proxy，并对小于阈值 $\varepsilon$ 的 penetration 使用 decaying 版本：

$$
\delta' =
\begin{cases}
\delta & \text{若 } \delta > \varepsilon \\
\frac{\varepsilon^2}{-\delta + 2\varepsilon} & \text{否则}
\end{cases}
$$

## 章节线索

- `2` 问题定义
- `3` `2DISPP` 现状综述
- `4` `a sequence of feasibility problems`
- `6` 碰撞严重度量化
- `9` 求解 `2DISPP` 的完整启发式
- `10` 实现
- `11-12` benchmark 与新实例
- `13` 结论与反思

## 开源实现线索

- `sparrow` GitHub：`https://github.com/JeroenGar/sparrow`
- 论文说明代码与文中算法编号直接对齐，可作为更正式的实现规范。

## 关联页面

- [[concepts/2d-irregular-cutting-and-packing]]
- [[concepts/2d-irregular-strip-packing]]
- [[concepts/collision-detection-engine-for-2d-nesting]]
- [[sources/gardeyn-open-source-collision-detection-engine]]

## 待继续处理

- `separate`、candidate move、best-fitting item 与并行 worker 的细节还未沉淀成概念页。
- `GARDEYN0-9` 新 benchmark 套件可在后续需要时单独成页。
- 文中性能结论目前只做定性记录；如果以后需要对比算法，应该再回到实验表格逐项摘录。
