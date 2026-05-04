# Grouped-Query Attention

## 它是什么

`Grouped-Query Attention`（`GQA`）是介于标准多头注意力和 `MQA` 之间的一种折中设计。它的核心思想是：

- query heads 仍然很多；
- 但多个 query heads 共享较少数量的 key/value heads。

## 它要解决什么问题

标准 `MHA` 的表达能力强，但推理时 `KV cache` 很大，因为每个 head 都要保留独立的 `K/V`。`MQA` 则让所有 query heads 共享一套 `K/V`，显著节省缓存，但表达能力可能损失更大。

`GQA` 的目标是在两者之间找平衡：

- 比 `MHA` 更省内存和带宽；
- 比 `MQA` 保留更多多头表达能力。

## 基本机制

设 query head 数为 $h_q$，key/value head 数为 $h_{kv}$，并且通常有 $h_{kv} < h_q$。那么每个 KV head 会服务一组 query heads。组大小可写为：

$$
g = \frac{h_q}{h_{kv}}
$$

如果第 $j$ 个 query head 属于第 $k$ 个组，那么它会与该组共享的 $K_k, V_k$ 交互，而不是拥有自己独立的 $K_j, V_j$。

单个 query head 的注意力仍然是标准形式：

$$
\mathrm{Attention}(Q_j, K_k, V_k) = \mathrm{softmax}\left(\frac{Q_j K_k^\top}{\sqrt{d_k}}\right)V_k
$$

但多个 query heads 会复用同一组 `K/V`。

## 为什么它能节省成本

推理时 `KV cache` 的主要开销与 `KV heads` 数量成正比。把 `h_q` 个 K/V 头缩减到 `h_{kv}` 个后，缓存大小大致按比例缩小：

$$
\text{KV cache reduction ratio} \approx \frac{h_{kv}}{h_q}
$$

同时，读取历史 `K/V` 的带宽需求也会下降，这对长上下文推理尤其重要。

## 和 MHA、MQA 的对比

- `MHA`：每个 query head 都有自己的 `K/V`，表达能力最强，缓存最大。
- `MQA`：所有 query heads 共享一套 `K/V`，缓存最省，但共享过于激进。
- `GQA`：按组共享 `K/V`，表达能力和缓存开销都位于两者之间。

## 在 LLM 里的意义

`GQA` 是一种非常实用的推理优化手段，因为它改动相对局部：

- 不需要彻底改变 Transformer 骨架；
- 不改变注意力的基本数学形式；
- 但能明显改善长序列推理的内存与吞吐表现。

## 相关页面

- [[concepts/transformer-block]]
- [[concepts/kv-cache]]
- [[concepts/attention-for-long-context]]

## 待补充

- 训练时从 `MHA` 迁移到 `GQA` 的具体做法。
- 它和 `MLA`、压缩注意力在缓存效率上的更系统对比。
