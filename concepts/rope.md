# Rotary Position Embedding

## 它是什么

`RoPE` 是一种把位置信息注入注意力的方法。它不是把位置向量直接加到 token embedding 上，而是对 `Q` 和 `K` 的各二维子空间施加位置相关旋转。

## 它要解决什么问题

注意力本身并不知道“第几个 token 在前、哪个 token 在后”。位置编码就是为了解决这个问题。`RoPE` 的目标是：

- 让注意力感知相对位置信息；
- 保持与点积注意力的兼容性；
- 让长上下文外推更自然一些。

## 高层机制

把一个 head 的向量维度两两配对，例如第 `2i` 维和第 `2i+1` 维组成一个二维平面。对位置 $p$，在第 $i$ 个二维平面上施加角度 $\theta_i p$ 的旋转。

对二维向量 $(x_{2i}, x_{2i+1})$，旋转后得到：

$$
\begin{pmatrix}
x'_{2i} \\
x'_{2i+1}
\end{pmatrix}
=
\begin{pmatrix}
\cos(p\theta_i) & -\sin(p\theta_i) \\
\sin(p\theta_i) & \cos(p\theta_i)
\end{pmatrix}
\begin{pmatrix}
x_{2i} \\
x_{2i+1}
\end{pmatrix}
$$

对 `Q` 和 `K` 都做这件事后，注意力分数中的内积会自然携带相对位置信息。

## 为什么它能表达相对位置

`RoPE` 的关键不是“给每个位置一个静态 embedding”，而是“让内积随位置差而变化”。因为旋转后的 $Q$ 和 $K$ 在做点积时，结果依赖于它们的旋转角差，所以模型能更自然地利用相对位置关系。

直观上看：

- token 越往后，旋转角越大；
- 两个位置之间的角差会影响相似度；
- 这种影响直接体现在注意力打分里。

## 在注意力中的位置

通常做法是：

1. 先从隐藏状态投影出 `Q` 和 `K`；
2. 对 `Q` 和 `K` 应用 `RoPE`；
3. 再计算缩放点积注意力：

$$
\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\left(\frac{\mathrm{RoPE}(Q)\mathrm{RoPE}(K)^\top}{\sqrt{d_k}}\right)V
$$

## 为什么它对长上下文重要

现代长上下文技巧很多并不是替换掉 `RoPE`，而是修改它的频率分布、缩放方式或外推策略。例如：

- 调整基础频率；
- 对位置做插值或重标定；
- 设计面向更长长度的变体。

所以理解长上下文，经常要先理解 `RoPE` 是“原始位置机制”。

## 优点与局限

优点：

- 与标准注意力兼容；
- 能较自然地表达相对位置；
- 在现代 decoder-only LLM 里非常常见。

局限：

- 极长上下文时，原始频率设计可能外推不足；
- 不同 head、不同频段上的位置解析能力并不一样；
- 真正的长上下文能力还取决于数据、注意力实现和推理系统，而不只取决于 `RoPE`。

## 相关页面

- [[concepts/transformer-block]]
- [[concepts/attention-for-long-context]]
- [[concepts/kv-cache]]

## 待补充

- 复数形式的写法与更完整推导。
- `NTK-aware scaling`、`YaRN`、`LongRoPE` 等外推策略。
- 与 `ALiBi`、绝对位置编码的系统对比。
