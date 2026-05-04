# RMSNorm

## 它是什么

`RMSNorm` 是一种按均方根尺度进行归一化的方法。它与 `LayerNorm` 的关键区别是：`RMSNorm` 不显式减去均值，只根据向量的整体幅度做缩放。

## 它要解决什么问题

深层网络训练中，隐藏状态的数值尺度容易在层间漂移。归一化的目标是让后续子层看到更稳定的输入分布，从而：

- 改善训练稳定性；
- 让更深层模型更容易优化；
- 减少对子层初始化和学习率的敏感性。

`RMSNorm` 的设计直觉是：很多时候只要控制向量尺度，就足够稳定，不一定需要像 `LayerNorm` 那样同时做中心化。

## 公式

给定隐藏状态向量 $x \in \mathbb{R}^d$，其均方根可写为：

$$
\mathrm{RMS}(x) = \sqrt{\frac{1}{d}\sum_{i=1}^{d} x_i^2 + \epsilon}
$$

一个常见的 `RMSNorm` 形式是：

$$
\mathrm{RMSNorm}(x) = \gamma \odot \frac{x}{\mathrm{RMS}(x)}
$$

其中：

- $\gamma \in \mathbb{R}^d$ 是可学习缩放参数；
- $\epsilon$ 是数值稳定项；
- $\odot$ 表示逐元素乘法。

## 每一步在做什么

- 先计算所有维度平方的平均值，估计当前向量的整体能量；
- 开方得到均方根尺度；
- 用这个尺度去除输入，使不同 token 的激活幅度落到相近范围；
- 再用可学习参数 $\gamma$ 恢复模型需要的各维度相对缩放。

## 为什么它经常比 LayerNorm 更受欢迎

`LayerNorm` 会先减均值，再除标准差；而 `RMSNorm` 只做后半部分的尺度归一化。这样带来几个结果：

- 计算更简单；
- 少了一步中心化；
- 在很多 decoder-only LLM 中足够稳定；
- 工程上常被认为更适合大规模自回归训练。

需要注意的是，这并不意味着 `RMSNorm` 在所有场景都“严格优于” `LayerNorm`，而是它在现代 LLM 这一特定分布上非常常见。

## 在 Transformer block 里的位置

现代 LLM 常把 `RMSNorm` 放在 pre-norm 结构里。例如：

$$
h = x + \mathrm{Attn}(\mathrm{RMSNorm}(x))
$$

$$
y = h + \mathrm{FFN}(\mathrm{RMSNorm}(h))
$$

这意味着每个子层都在接收尺度较稳定的输入。

## 关键超参数和实现细节

- $\epsilon$：防止分母太小，混合精度训练中尤其重要。
- 是否使用偏置：很多实现里没有额外 bias。
- 归一化维度：通常沿隐藏维做。

## 相关页面

- [[concepts/transformer-block]]
- [[concepts/manifold-constrained-hyper-connections]]

## 待补充

- 与 `LayerNorm` 在训练稳定性、吞吐和最终效果上的系统对比。
- `pRMSNorm`、`ScaleNorm` 等近邻变体。
