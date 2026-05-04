# Transformer Block

## 它是什么

`Transformer block` 是大多数现代 LLM 的基本堆叠单元。一个 block 通常包含四类部件：

- 归一化；
- 注意力子层；
- 前馈子层；
- 把各子层串起来的残差路径。

无论模型是 dense、`MoE`、长上下文变体还是多种注意力改造，绝大多数变化都发生在 block 内部，而不是完全脱离这个骨架。

## 它要解决什么问题

单个 block 的职责可以理解为两部分：

- 注意力子层负责跨 token 交互，把序列里的其他位置引入当前 token 表示；
- 前馈子层负责逐 token 的非线性特征变换，提高表示能力。

把很多 block 堆叠起来，模型就可以逐层整合局部上下文、全局依赖和抽象特征。

## 典型 pre-norm 结构

现代 LLM 最常见的是 pre-norm 结构，即先归一化，再进入子层。设输入为 $x$，注意力子层记为 $\mathrm{Attn}(\cdot)$，前馈子层记为 $\mathrm{FFN}(\cdot)$，归一化记为 $\mathrm{Norm}(\cdot)$，则一个典型 block 可写成：

$$
h = x + \mathrm{Attn}(\mathrm{Norm}(x))
$$

$$
y = h + \mathrm{FFN}(\mathrm{Norm}(h))
$$

这里的两个加法就是残差连接。它保证子层不是“从零开始重写表示”，而是在旧表示上做增量修正。

## 每个部件在做什么

### 1. 归一化

归一化层通常使用 `RMSNorm` 或 `LayerNorm`。它的作用是控制激活尺度，降低深层网络训练时的数值不稳定。

### 2. 注意力子层

注意力会根据当前 token 的 query 与其他 token 的 key 相似度，对 value 做加权汇总。标准缩放点积注意力可写为：

$$
\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

在实际 LLM 中，注意力子层还会包含：

- 多头拆分；
- 位置编码，例如 `RoPE`；
- K/V 共享或压缩，例如 `GQA`、`MLA`、长上下文压缩注意力；
- 推理时的 `KV cache`。

### 3. 前馈子层

前馈层通常是对每个 token 独立施加的 MLP。最基础的两层形式可以写成：

$$
\mathrm{FFN}(x) = W_2 \sigma(W_1 x)
$$

现代 LLM 更常见的是 `SwiGLU` 或其他 gated MLP 变体，例如：

$$
\mathrm{FFN}(x) = W_o \left( \mathrm{SiLU}(W_g x) \odot W_u x \right)
$$

如果把 dense FFN 换成专家集合和路由器，就会得到 `MoE` block。

### 4. 残差连接

残差路径保证信息与梯度能够跨层稳定传播。很多“训练更深模型”的工作，本质上都在改造残差路径、归一化位置或初始化方式。

## 为什么 block 是理解架构的最好入口

因为几乎所有架构创新都可以定位到 block 的某个部件：

- 改注意力：`MHA`、`MQA`、`GQA`、`MLA`、`CSA/HCA`
- 改前馈：dense `FFN`、`SwiGLU`、`MoE`
- 改归一化：`LayerNorm`、`RMSNorm`
- 改残差：gating、`mHC`、更深层稳定化技巧

这意味着只要 block 的骨架足够清楚，很多模型页就可以写成“在这个骨架上替换了哪些零件”。

## 常见变体

- `pre-norm`：先归一化再进子层，现代大模型最常见。
- `post-norm`：子层输出后再归一化，早期 Transformer 较常见。
- `sandwich norm` 或其他变体：在一些更深或更特殊的网络中出现。
- `decoder-only block`：LLM 最常见，只用因果注意力。
- `encoder-decoder block`：额外包含 cross-attention，常见于翻译或 seq2seq 模型。

## 相关页面

- [[concepts/attention]]
- [[concepts/multi-head-attention]]
- [[concepts/mixture-of-experts]]
- [[concepts/rmsnorm]]
- [[concepts/rope]]
- [[concepts/grouped-query-attention]]
- [[concepts/attention-for-long-context]]
- [[concepts/manifold-constrained-hyper-connections]]

## 待补充

- `post-norm` 与 `pre-norm` 在超深网络中的稳定性差异。
- 不同 FFN 变体的参数量与 FLOPs 对比。
