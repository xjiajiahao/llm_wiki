# KV Cache

## 它是什么

`KV cache` 是自回归推理中保存历史 `K` 和 `V` 的机制。这样在生成第 $t$ 个 token 时，不必重新计算前面所有 token 的 `K/V`。

## 它要解决什么问题

如果没有缓存，那么生成每个新 token 时，模型都要重新处理全部历史上下文。设当前序列长度为 $t$，那么第 $t$ 步会重复计算前 $t-1$ 个 token 的 attention 相关状态，造成大量冗余。

`KV cache` 的核心目的就是把“历史 token 的 K/V 表示”存下来，让后续 step 只计算新 token 对历史的注意力。

## 基本机制

在第 $t$ 步，模型会：

1. 仅对新 token 计算当前层的 query、key、value；
2. 把新的 $K_t, V_t$ 追加进缓存；
3. 用当前 query $Q_t$ 与历史缓存里的所有 $K_{1:t}$ 计算注意力；
4. 用得到的权重对缓存中的 $V_{1:t}$ 做加权和。

因此，单步 attention 可写成：

$$
\mathrm{Attention}(Q_t, K_{1:t}, V_{1:t}) =
\mathrm{softmax}\left(\frac{Q_t K_{1:t}^\top}{\sqrt{d_k}}\right)V_{1:t}
$$

## 它为什么能提速

缓存以后，不再需要每一步都重新投影和重算历史 token 的 `K/V`。这把自回归生成从“重复处理整段前缀”变成“增量处理新 token”。

## 它为什么又会成为瓶颈

`KV cache` 节省了重复计算，但引入了新的成本：

- 显存占用很大；
- 长上下文时读取带宽压力很高；
- 多 batch、多并发服务时缓存管理复杂。

一个粗略的缓存规模关系可以写成：

$$
\text{cache size} \propto L \times T \times h_{kv} \times d_{head}
$$

其中：

- $L$ 是层数；
- $T$ 是上下文长度；
- $h_{kv}$ 是 `KV heads` 数；
- $d_{head}$ 是每个 head 的维度。

因此，长上下文系统里很多工作其实都在围绕这个式子动手：

- 降低 $h_{kv}$，例如 `GQA`；
- 压缩序列维度，例如长上下文压缩注意力；
- 改进存储布局、分页和 kernel。

## 与训练的区别

`KV cache` 主要是推理概念。训练时通常是并行处理整段序列，不按 token 逐步生成，所以不会按同样方式维护推理缓存。

## 相关页面

- [[concepts/grouped-query-attention]]
- [[concepts/flashattention]]
- [[concepts/attention-for-long-context]]
- [[concepts/multi-head-latent-attention]]

## 待补充

- paged KV cache、cache eviction、多轮对话复用等工程话题。
- 不同注意力结构下的缓存布局差异。
