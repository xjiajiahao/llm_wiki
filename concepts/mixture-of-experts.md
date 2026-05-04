# Mixture of Experts

## 它是什么

`Mixture of Experts`（`MoE`）是一种稀疏模型设计。与每个 token 都经过同一套 dense `FFN` 不同，`MoE` 会为每个 token 只激活少量专家子网络，从而在不让每 token 计算量线性增长的前提下，提高总参数量。

## 它要解决什么问题

dense 模型扩大规模有一个直接代价：总参数越大，每个 token 通常也要经过越多计算。`MoE` 想解决的问题是：

- 能否把模型总容量做大；
- 但让每个 token 只支付其中一小部分计算成本。

这使模型扩展从“纯计算问题”转向“路由、通信、负载均衡和内存问题”。

## 基本结构

在标准 Transformer block 中，`MoE` 最常替换的是前馈层。原来的 dense `FFN`：

$$
\mathrm{FFN}(x) = W_2 \sigma(W_1 x)
$$

会被替换为多个专家：

$$
E_1(x), E_2(x), \dots, E_N(x)
$$

同时增加一个路由器，为每个 token 选择要激活的专家。

## 路由流程

设 token 表示为 $x$，路由器输出每个专家的打分：

$$
s = W_r x
$$

再经过 softmax 或其他归一化形式得到路由概率：

$$
p_i = \frac{\exp(s_i)}{\sum_{j=1}^{N}\exp(s_j)}
$$

然后只选择 top-$k$ 个专家参与计算。若被选中的专家集合为 $\mathcal{T}(x)$，则常见输出形式可写为：

$$
y = \sum_{i \in \mathcal{T}(x)} \alpha_i E_i(x)
$$

其中 $\alpha_i$ 是归一化后的门控权重。

最常见的是 top-1 或 top-2 路由。

## 为什么它能扩大模型容量

假设有 $N$ 个专家，但每个 token 只激活 $k$ 个，且 $k \ll N$。那么：

- 总参数量大约随专家数增加；
- 单 token 计算量主要只与被选中的 $k$ 个专家相关。

这就是 `MoE` 的核心收益来源：高总容量、低激活计算。

## 主要工程难点

### 1. 负载均衡

如果大多数 token 都被分配给少数专家，就会出现：

- 某些专家过载；
- 某些专家几乎不学；
- 分布式通信严重失衡。

因此很多 `MoE` 工作都会设计负载均衡策略。

### 2. 容量限制

每个专家每步能处理的 token 数通常有限制，超出的 token 可能被丢弃、回退或重路由。容量设置会影响：

- 训练稳定性；
- token drop 率；
- 实际吞吐。

### 3. 跨设备通信

专家往往分布在不同设备上。token 被路由到远端专家时，需要 all-to-all 或类似通信，这常常成为大规模 `MoE` 的核心瓶颈。

## 它与 dense FFN 的关系

可以把 `MoE` 看成“把单个大 FFN 拆成很多专业子网络，再由路由器决定谁处理谁”。所以它不是另一类完全不同的架构，而更像是 Transformer block 里 FFN 的稀疏化版本。

## 在本 wiki 中的实例

- [[models/deepseek-v3]] 把 `DeepSeekMoE` 作为效率导向骨架的一部分。
- [[models/deepseek-v4]] 保留 `MoE` 骨架，同时围绕注意力、优化器和精度做进一步升级。

## 相关页面

- [[concepts/auxiliary-loss-free-load-balancing]]
- [[concepts/fp8-training]]
- [[concepts/fp4-quantization-aware-training]]
- [[concepts/multi-token-prediction]]
- [[concepts/transformer-block]]

## 待补充

- 更细的专家容量公式和 token dispatch 流程。
- 与 dense 模型、Switch Transformer、Mixtral 风格 `MoE` 的系统对比。
