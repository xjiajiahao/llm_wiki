# FlashAttention

## 它是什么

`FlashAttention` 不是一种新的注意力数学定义，而是一类以内存访问优化为核心的 attention 实现方法。它的目标是让标准注意力在真实硬件上跑得更快、更省显存。

## 它要解决什么问题

标准 attention 的理论计算式很简单，但直接实现时有一个大问题：中间张量很大，尤其是完整的 attention score 矩阵会带来巨大的显存读写开销。

在 GPU 上，很多时候真正的瓶颈不是浮点乘加本身，而是高带宽显存（HBM）和片上 SRAM 之间的数据搬运。`FlashAttention` 要解决的正是这种 IO 瓶颈。

## 核心思路

它通常会做三件事：

- 分块处理 `Q/K/V`，避免一次性物化完整注意力矩阵；
- 把多个计算步骤融合起来，减少中间结果写回显存；
- 在片上 SRAM 中完成更多局部计算，再把最终结果写回。

因此，`FlashAttention` 的本质是“重新安排计算顺序和数据流”，而不是改写注意力公式。

## 与标准注意力的关系

目标仍然是计算：

$$
\mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

区别在于实现方式：

- 标准朴素实现可能先显式构造 $QK^\top$；
- `FlashAttention` 倾向于按块流式处理，并在块内完成 softmax 所需的归约统计。

## 为什么它很重要

- 序列长度变长时，attention 的中间状态会迅速膨胀；
- 如果显存带宽成为瓶颈，单纯堆更多算力也未必有效；
- 长上下文模型、推理服务和训练基础设施都严重依赖 attention kernel 的质量。

所以 `FlashAttention` 这种“实现层创新”会直接影响模型是否跑得起来、能跑多长、吞吐有多高。

## 和概念层的边界

它属于“实现与系统”层，而不是“建模”层。也就是说：

- `GQA`、`MLA`、`CSA/HCA` 这些更像是在改结构；
- `FlashAttention` 更像是在同样结构下把 kernel 写得更合理。

当然，现实里两者会相互影响，因为某些结构只有在高效 kernel 存在时才有工程价值。

## 相关页面

- [[concepts/transformer-block]]
- [[concepts/kv-cache]]
- [[concepts/attention-for-long-context]]

## 待补充

- `FlashAttention-2`、`FlashAttention-3` 等版本差异。
- 与 paged attention、块稀疏 attention kernel 的关系。
