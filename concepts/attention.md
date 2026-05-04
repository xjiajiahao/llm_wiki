# Attention

## 它是什么

`Attention` 是 Transformer 里最核心的序列交互机制。它让每个 token 的表示不再只依赖当前位置，而是能够根据“相似度”从前面或整段序列中选择性读取其他 token 的信息。

在 LLM 里，最常见的是缩放点积注意力（scaled dot-product attention）。

## 来源状态

这是一张通用基础概念页，当前内容基于稳定的标准 Transformer 数学形式整理，**尚未绑定本仓库 `raw/` 目录中的原始来源**。如果后续加入 Transformer 论文或教材型来源，应回填来源页并把这里的表述升级为已核验版本。

## 它要解决什么问题

如果只靠逐 token 的 MLP 或固定窗口卷积，模型很难灵活处理：

- 长距离依赖；
- 不同位置之间的重要性差异；
- “当前 token 应该读取哪些历史 token” 这个动态选择问题。

`Attention` 的做法是：先为每个 token 构造 query、key、value，再用 query 和所有 key 的匹配分数决定应该如何汇总 value。

## 记号约定

本页统一采用用户约定的矩阵形状：

- 输入序列表示为 $X \in \mathbb{R}^{n \times d}$；
- $n$ 表示当前可见 token 个数；
- $d$ 表示每个 token 的特征维度。

其中第 $i$ 行 $x_i \in \mathbb{R}^{1 \times d}$ 表示第 $i$ 个 token 的表示。

## 基本公式

给定输入 $X \in \mathbb{R}^{n \times d}$，先通过三个线性映射得到：

$$
Q = X W_Q,\quad K = X W_K,\quad V = X W_V
$$

其中：

$$
W_Q, W_K \in \mathbb{R}^{d \times d_k}, \quad W_V \in \mathbb{R}^{d \times d_v}
$$

所以：

$$
Q, K \in \mathbb{R}^{n \times d_k}, \quad V \in \mathbb{R}^{n \times d_v}
$$

随后计算 attention score 矩阵：

$$
S = \frac{QK^\top}{\sqrt{d_k}}
$$

这里：

- $QK^\top \in \mathbb{R}^{n \times n}$；
- 第 $(i,j)$ 个元素表示第 $i$ 个 token 的 query 与第 $j$ 个 token 的 key 的匹配强度；
- 除以 $\sqrt{d_k}$ 是为了避免内积维度变大后数值过大，导致 softmax 过于尖锐。

对每一行做 softmax，得到注意力权重矩阵：

$$
A = \mathrm{softmax}(S)
$$

其中 $A \in \mathbb{R}^{n \times n}$，并且每一行加和为 $1$。

最后用这些权重对 value 加权求和：

$$
Y = AV
$$

因此输出为：

$$
Y \in \mathbb{R}^{n \times d_v}
$$

把这些步骤合起来，标准缩放点积注意力可以写成：

$$
\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

## 逐行理解这个公式

对第 $i$ 个 token 而言，它的输出是：

$$
y_i = \sum_{j=1}^{n} a_{ij} v_j
$$

其中：

- $a_{ij}$ 是第 $i$ 个 token 对第 $j$ 个 token 的注意力权重；
- $v_j$ 是第 $j$ 个 token 的 value 向量。

也就是说，第 $i$ 个输出向量本质上是“对所有 token 的 value 做一次加权平均”，只是这个平均的权重由 query-key 相似度动态决定。

## 因果注意力

在 decoder-only LLM 中，通常不能看到未来 token，所以真正使用的是因果掩码（causal mask）版本。

设掩码矩阵 $M \in \mathbb{R}^{n \times n}$，其中：

$$
M_{ij} =
\begin{cases}
0, & j \le i \\
-\infty, & j > i
\end{cases}
$$

那么因果注意力可写为：

$$
A = \mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}} + M\right)
$$

$$
Y = AV
$$

这样第 $i$ 个 token 只能关注自己和前面的 token，不能读取未来位置的信息。

## 为什么输出形状仍然是 $n \times d_v$

容易混淆的一点是：attention 在序列维上做“信息重组”，但不会改变 token 个数。

- 输入有 $n$ 个 token；
- 输出仍然对应这 $n$ 个 token；
- 每个输出 token 都是从全部可见 token 的 value 中汇总出来的。

因此 attention 的作用更像是“在序列内部做动态信息交换”，而不是增删 token。

## 它和 MLP 的分工

- `Attention` 负责 token 与 token 之间的信息路由。
- `MLP/FFN` 负责每个 token 内部的非线性特征变换。

这也是为什么 Transformer block 通常把两者串联起来：先跨 token 混合，再逐 token 变换。

## 它在大模型里的几个关键维度

- 序列长度 $n$ 决定了 score 矩阵大小是 $n \times n$，这也是长上下文成本高的直接原因。
- 特征维度 $d$ 决定了投影矩阵大小和每个 token 的表示容量。
- 是否加因果掩码决定这是双向注意力还是自回归注意力。

如果继续把特征维拆成多个头，就得到 [[concepts/multi-head-attention]]。

## 相关页面

- [[concepts/multi-head-attention]]
- [[concepts/transformer-block]]
- [[concepts/kv-cache]]
- [[concepts/flashattention]]

## 待补充

- cross-attention 在 encoder-decoder 结构中的单独写法。
- 从 score 矩阵到时间复杂度、空间复杂度的更系统推导。
