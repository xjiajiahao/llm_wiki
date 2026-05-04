# Multi-Head Attention

## 它是什么

`Multi-Head Attention`（`MHA`）是在标准 attention 上做的并行多头扩展。它不是只做一次 $QK^\top$ 匹配，而是把特征维度拆成多个子空间，在多个 head 上分别计算 attention，再把结果拼接起来。

## 来源状态

这是一张通用基础概念页，当前内容基于稳定的标准 Transformer 数学形式整理，**尚未绑定本仓库 `raw/` 目录中的原始来源**。如果后续加入 Transformer 原始论文或教材型来源，应把这里升级为已核验版本。

## 它要解决什么问题

如果只做单头 attention，所有相关性判断都必须挤在同一个相似度空间里。这会带来两个限制：

- 不同类型的依赖关系会互相竞争同一套投影；
- 模型只能给每个 token 产出一组单一的注意力模式。

`MHA` 的想法是让不同 head 学习不同的关系模式，例如：

- 有的 head 更关注最近邻 token；
- 有的 head 更关注语法边界或分隔符；
- 有的 head 更偏向长距离依赖。

## 记号约定

仍然采用：

- 输入 $X \in \mathbb{R}^{n \times d}$；
- $n$ 是 token 个数；
- $d$ 是总特征维度。

再设：

- head 数为 $h$；
- 每个 head 的 query/key/value 维度为 $d_h$；
- 常见设置是 $d = h d_h$。

## 单头到多头的拆分

第 $m$ 个 head 有自己的一组投影矩阵：

$$
W_Q^{(m)}, W_K^{(m)}, W_V^{(m)} \in \mathbb{R}^{d \times d_h}
$$

因此第 $m$ 个 head 的投影结果为：

$$
Q^{(m)} = X W_Q^{(m)},\quad
K^{(m)} = X W_K^{(m)},\quad
V^{(m)} = X W_V^{(m)}
$$

其中：

$$
Q^{(m)}, K^{(m)}, V^{(m)} \in \mathbb{R}^{n \times d_h}
$$

## 每个 head 内部的 attention

第 $m$ 个 head 单独计算：

$$
H^{(m)} =
\mathrm{softmax}\left(
\frac{Q^{(m)} {K^{(m)}}^\top}{\sqrt{d_h}}
\right)V^{(m)}
$$

所以：

$$
H^{(m)} \in \mathbb{R}^{n \times d_h}
$$

如果是 decoder-only LLM，则同样要加因果掩码：

$$
H^{(m)} =
\mathrm{softmax}\left(
\frac{Q^{(m)} {K^{(m)}}^\top}{\sqrt{d_h}} + M
\right)V^{(m)}
$$

这里所有 head 共用同一个因果掩码 $M \in \mathbb{R}^{n \times n}$。

## 拼接与输出投影

把所有 head 的输出按特征维拼接：

$$
H = [H^{(1)}; H^{(2)}; \dots; H^{(h)}]
$$

这里的分号表示按列拼接，因此：

$$
H \in \mathbb{R}^{n \times (h d_h)}
$$

若采用常见设置 $d = h d_h$，则有：

$$
H \in \mathbb{R}^{n \times d}
$$

最后再经过输出投影矩阵：

$$
Y = H W_O
$$

其中：

$$
W_O \in \mathbb{R}^{(h d_h) \times d}, \quad Y \in \mathbb{R}^{n \times d}
$$

因此完整的多头注意力可以写成：

$$
\mathrm{MHA}(X) =
\mathrm{Concat}\left(
\mathrm{head}_1, \dots, \mathrm{head}_h
\right) W_O
$$

其中：

$$
\mathrm{head}_m =
\mathrm{Attention}(XW_Q^{(m)}, XW_K^{(m)}, XW_V^{(m)})
$$

## 形状为什么这样设计

`MHA` 的一个关键设计是：

- 在每个 head 内部，attention 只在较小维度 $d_h$ 上做相似度计算；
- 多个 head 并行学习不同子空间；
- 最后再把这些子空间重新组合回总维度 $d$。

这让模型既保留了总表示容量，又能获得更丰富的注意力模式。

## 从矩阵角度怎么理解

把单头 attention 看成“生成一张 $n \times n$ 的路由矩阵，再作用到 $V$ 上”，那么 `MHA` 就是在并行生成 $h$ 张不同的路由矩阵：

$$
A^{(m)} =
\mathrm{softmax}\left(
\frac{Q^{(m)} {K^{(m)}}^\top}{\sqrt{d_h}}
\right)
\in \mathbb{R}^{n \times n}
$$

每个 head 都有自己的一套：

- query 子空间；
- key 子空间；
- value 子空间；
- 路由权重矩阵。

所以多头的本质不是“把一个大 attention 拆小”，而是“并行学习多种不同的注意力关系”。

## 它的代价

`MHA` 的表达能力强，但也直接带来更高的 `K/V` 成本：

- 训练时有更多投影与激活；
- 推理时每个 head 都需要保留自己的历史 `K/V`；
- 长上下文下，`KV cache` 和带宽开销会随 head 数增长。

这也是为什么后续会出现 [[concepts/grouped-query-attention]]、`MQA`、[[concepts/multi-head-latent-attention]] 等变体。

## 它和基础 attention 的关系

- [[concepts/attention]] 给出的是“单次 attention 计算”的基本数学形式。
- `MHA` 则是在这个基本形式外面再包一层“多组投影 + 并行 head + 拼接输出”。

因此，理解顺序通常是：

1. 先理解单头 attention 的 $Q/K/V$ 与 $QK^\top$。
2. 再理解为什么要把 $d$ 拆成多个 $d_h$。
3. 最后再看 `GQA`、`MLA`、长上下文 attention 等变体如何修改 `MHA`。

## 在本 wiki 中

当前 wiki 里，很多注意力变体页都默认把 `MHA` 当作比较基线：

- [[concepts/grouped-query-attention]]：减少 `KV` 头数。
- [[concepts/multi-head-latent-attention]]：压缩 `KV` 表示。
- [[concepts/attention-for-long-context]]：进一步压缩或稀疏化序列维上的访问。

## 相关页面

- [[concepts/attention]]
- [[concepts/grouped-query-attention]]
- [[concepts/multi-head-latent-attention]]
- [[concepts/kv-cache]]
- [[concepts/transformer-block]]

## 待补充

- `MHA` 的参数量、FLOPs 与单头 attention 的对比。
- `MQA` 的单独概念页，以及它和 `GQA` 的定量比较。
