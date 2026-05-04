# Attention for Long Context

## 它是什么

这个页面记录当前 wiki 中“长上下文注意力”这条主线。基于 `DeepSeek-V4` 技术报告，当前最完整、可公式化的方案是混合 `CSA + HCA`：

- `CSA`：`Compressed Sparse Attention`
- `HCA`：`Heavily Compressed Attention`

报告把它们描述为交错使用的混合注意力架构，用于把百万 token 上下文变成工程上可运行的配置。

## 它要解决什么问题

上下文长度极大时，注意力会成为主要瓶颈。问题不只在于理论复杂度，还在于：

- 单 token 推理时需要读取越来越长的历史状态；
- `KV cache` 会随序列长度线性膨胀；
- attention 的带宽和缓存成本会压过很多其他模块。

因此，长上下文注意力的核心目标是：

- 压缩历史表示；
- 减少真正参与注意力的历史位置数；
- 同时尽量保留局部依赖与远程检索能力。

## DeepSeek-V4 的总体思路

报告在 `2.3` 节给出的高层设计是：

- `CSA`：先把每 `m` 个 token 的 `KV` 压成一个条目，再对压缩条目做稀疏选择；
- `HCA`：把每 `m'` 个 token 压成一个条目，其中 $m' \gg m$，追求更强压缩，但不做稀疏选择；
- 两者交错组合，形成混合注意力架构。

可以先用一句话概括：

- `CSA` 偏向“压缩后再检索”；
- `HCA` 偏向“更重压缩但保持稠密聚合”。

## CSA：Compressed Sparse Attention

### 1. 压缩 KV entries

设输入隐藏状态序列为：

$$
H \in \mathbb{R}^{n \times d}
$$

其中 $n$ 是序列长度，$d$ 是隐藏维度。`CSA` 先构造两组 KV entries 和它们对应的压缩权重：

$$
C_a = H W_{KV}^a,\qquad C_b = H W_{KV}^b
$$

$$
Z_a = H W_Z^a,\qquad Z_b = H W_Z^b
$$

其中：

- $C_a, C_b \in \mathbb{R}^{n \times c}$
- $Z_a, Z_b \in \mathbb{R}^{n \times c}$
- $c$ 是 head dimension

然后，每 `m` 个 KV entries 会被压成一个 compressed entry。报告这里不是简单平均，而是引入：

- 两组压缩权重；
- 可学习位置偏置 $B_a, B_b \in \mathbb{R}^{m \times c}$；
- 重叠式压缩。

每个压缩条目 $C_i^{Comp}$ 的计算写成：

$$
[S^a_{mi:m(i+1)-1}; S^b_{m(i-1):mi-1}]
=
\mathrm{Softmax}_{row}
([Z^a_{mi:m(i+1)-1}+B_a;\; Z^b_{m(i-1):mi-1}+B_b])
$$

$$
C_i^{Comp}
=
\sum_{j=mi}^{m(i+1)-1} S_j^a \odot C_j^a
+
\sum_{j=m(i-1)}^{mi-1} S_j^b \odot C_j^b
$$

其中 $\odot$ 是逐元素乘法。

报告特别指出：虽然每个压缩条目来自 `2m` 个 KV entries，但相邻条目之间有重叠，因此**有效上是把序列长度压到原来的 $\frac{1}{m}$**。

### 2. 用 lightning indexer 做稀疏选择

得到压缩后的 $C^{Comp}$ 后，`CSA` 不会让 query 对所有压缩块都做注意力，而是先用 indexer 做筛选。

首先，用和上面同样的压缩操作得到 compressed indexer keys：

$$
K_{I}^{Comp} \in \mathbb{R}^{\frac{n}{m} \times c_I}
$$

然后对 query token $t$，先做低秩 query 压缩：

$$
c_t^Q = h_t W^{DQ}
$$

$$
[q_{t,1}^I; q_{t,2}^I; \dots; q_{t,n_h^I}^I]
=
q_t^I
=
c_t^Q W_{UQ}^I
$$

其中 $n_h^I$ 是 indexer query head 数量。

接着，报告定义 query token $t$ 与前面某个压缩块 $s$ 的 index score：

$$
[w_{t,1}^I; w_{t,2}^I; \dots; w_{t,n_h^I}^I]
=
w_t^I
=
h_t W_w
$$

$$
I_{t,s}
=
\sum_{h=1}^{n_h^I}
w_{t,h}^I \cdot \mathrm{ReLU}(q_{t,h}^I \cdot K_{s}^{IComp})
$$

最后，只保留 top-k 个压缩条目做后续注意力：

$$
C_t^{SprsComp}
=
\left\{
C_s^{Comp}\mid I_{t,s} \in \mathrm{Top}\text{-}k(I_{t,:})
\right\}
$$

这一步是 `CSA` 的核心，因为它让每个 query 只看少量压缩块，而不是看全部历史压缩块。

### 3. 在选出的压缩块上做 MQA

在真正的 core attention 中，`CSA` 使用共享 `KV` 的 `MQA` 形式。

先从前面的压缩 query latent $c_t^Q$ 中恢复 attention queries：

$$
[q_{t,1}; q_{t,2}; \dots; q_{t,n_h}]
=
q_t
=
c_t^Q W^{UQ}
$$

然后对选中的压缩块做注意力：

$$
o_{t,i}
=
\mathrm{CoreAttn}
(
query=q_{t,i},
key=C_t^{SprsComp},
value=C_t^{SprsComp}
)
$$

这里每个压缩条目同时充当 `key` 和 `value`。

### 4. Grouped output projection

报告指出，直接把所有头输出 $o_t \in \mathbb{R}^{cn_h}$ 投回 $d$ 维会比较贵，因此采用 grouped output projection：

- 先把 $n_h$ 个头分成 $g$ 组；
- 每组先投到较小的中间维度 $d_g$；
- 再从所有组的中间输出投到最终隐藏状态。

这本质上是在输出端进一步降成本。

## HCA：Heavily Compressed Attention

`HCA` 的总体方向与 `CSA` 相似，但更激进。

### 1. 更重的压缩

`HCA` 不使用 `CSA` 的重叠压缩，而是直接把每 `m'` 个 token 压成一个条目，并且：

$$
m' \gg m
$$

设输入仍为 $H \in \mathbb{R}^{n \times d}$，则先构造：

$$
C = H W_{KV}
$$

$$
Z = H W_Z
$$

然后每个压缩条目 $C_i^{Comp}$ 计算为：

$$
S_{m'i:m'(i+1)-1}
=
\mathrm{Softmax}_{row}(Z_{m'i:m'(i+1)-1} + B)
$$

$$
C_i^{Comp}
=
\sum_{j=m'i}^{m'(i+1)-1} S_j \odot C_j
$$

这一步把序列长度压到原来的：

$$
\frac{1}{m'}
$$

### 2. 不做稀疏选择，直接做压缩后的 MQA

`HCA` 没有 `CSA` 的 lightning indexer 和 top-k 选择，而是直接在全部压缩条目上做共享 `KV` 的 `MQA`。

query 仍是低秩生成：

$$
c_t^Q = h_t W^{DQ}
$$

$$
[q_{t,1}; q_{t,2}; \dots; q_{t,n_h}]
=
q_t
=
c_t^Q W^{UQ}
$$

然后：

$$
o_{t,i}
=
\mathrm{CoreAttn}
(
query=q_{t,i},
key=C^{Comp},
value=C^{Comp}
)
$$

最后同样使用 grouped output projection。

## CSA 和 HCA 的本质差别

可以把它们的差别概括成三点：

- `CSA` 压缩较轻，但进一步做 top-k 稀疏选择；
- `HCA` 压缩更重，但不做稀疏检索；
- `CSA` 更像“先检索再聚合”，`HCA` 更像“极限压缩后直接聚合”。

因此二者是互补关系，而不是简单替代关系。

## 报告中的额外细节

### 1. Query 和 compressed KV entry 都额外做 RMSNorm

报告说，在 core attention 之前，会对：

- 每个 head 的 query；
- compressed KV entry 的那一个 head；

额外做一次 `RMSNorm`，以避免 attention logits 爆炸，并改善训练稳定性。

### 2. Partial RoPE

对于 `CSA` 和 `HCA`，报告没有把 `RoPE` 用到全部维度，而是：

- 对 query 和 KV entry 的最后 `64` 维应用 `RoPE`；
- 因为 compressed KV entry 同时兼作 key 和 value，朴素 attention 输出会携带绝对位置信息；
- 因此又对每个 core attention output 的最后 `64` 维施加位置 `-i` 的 `RoPE`，让输出重新带有相对位置信息。

### 3. Sliding window branch

由于 `CSA/HCA` 都只让 query 访问**前面的压缩块**，同一个压缩块内的其他 token 无法直接被看到，而最近 token 往往又最重要。为此，报告额外加入了 sliding window attention 分支：

- 对每个 query token，再补一小段最近的未压缩 KV entries；
- 在 core attention 里把这些局部未压缩条目和压缩条目一起使用。

这一步本质上是给压缩注意力补局部细节。

### 4. Attention sink

报告还加入了可学习的 sink logits $\{z_1', \dots, z_{n_h}'\}$，把它们加到 softmax 分母上：

$$
s_{h,i,j}
=
\frac{\exp(z_{h,i,j})}
{\sum_k \exp(z_{h,i,k}) + \exp(z_h')}
$$

这允许某个 query head 的总注意力权重不必严格和为 `1`，甚至可以接近 `0`。

## 为什么混合 `CSA + HCA`

如果只用 `CSA`，虽然可以通过检索减少计算，但压缩率相对有限；如果只用 `HCA`，虽然压缩很强，但可能损失更多细节。

把二者交错组合的直觉是：

- `CSA` 负责更细粒度的远程检索；
- `HCA` 负责更大尺度的序列压缩；
- sliding window 分支负责局部精细依赖。

这样，模型既能保留局部建模能力，又能把远距离上下文读写成本压下来。

## 报告中的效率结论

报告在 `2.3.4` 节给出的几个稳定结论包括：

- `KV entries` 采用混合存储：`RoPE` 维度用 `BF16`，其余维度用 `FP8`，相对纯 `BF16` 能把 `KV cache` 近乎减半；
- lightning indexer 内部的 attention 计算用 `FP4`，以加速超长上下文场景；
- 相比 `DeepSeek-V3.2`，`DeepSeek-V4` 采用更小的 attention top-k；
- 以 head dimension 为 `128` 的 `BF16 GQA8` 为基线时，`DeepSeek-V4` 在 `1M` 上下文下的 `KV cache` 可降到基线的大约 `2%`；
- 在 `1M token` 场景下，`DeepSeek-V4-Pro` 的单 token FLOPs 是 `DeepSeek-V3.2` 的 `27%`，KV cache 是 `10%`；`DeepSeek-V4-Flash` 则进一步到 `10%` FLOPs 和 `7%` KV cache。

## DeepSeek-V4 的具体超参数配置

报告在 `4.2.1 Model Setups` 里给出了 `CSA/HCA` 的模型级配置。

### DeepSeek-V4-Flash

- Transformer 层数：`43`
- 隐藏维度 $d$：`4096`
- 前 `2` 层：纯 sliding window attention
- 后续层：`CSA` 与 `HCA` 交错

`CSA` 配置：

- 压缩率 $m = 4$
- indexer query head 数 $n_h^I = 64$
- indexer head 维度 $c_I = 128$
- sparse attention 的 top-k：`512`

`HCA` 配置：

- 压缩率 $m' = 128$

`CSA/HCA` 共用的 attention 配置：

- query head 数 $n_h = 64$
- head 维度 $c = 512$
- query 压缩维度 $d_c = 1024$
- output projection group 数 $g = 8$
- 每组中间输出维度 $d_g = 1024$
- sliding window 大小 $n_{win} = 128$

### DeepSeek-V4-Pro

- Transformer 层数：`61`
- 隐藏维度 $d$：`7168`
- 前 `2` 层：`HCA`
- 后续层：`CSA` 与 `HCA` 交错

`CSA` 配置：

- 压缩率 $m = 4$
- indexer query head 数 $n_h^I = 64$
- indexer head 维度 $c_I = 128$
- sparse attention 的 top-k：`1024`

`HCA` 配置：

- 压缩率 $m' = 128$

`CSA/HCA` 共用的 attention 配置：

- query head 数 $n_h = 128$
- head 维度 $c = 512$
- query 压缩维度 $d_c = 1536$
- output projection group 数 $g = 16$
- 每组中间输出维度 $d_g = 1024$
- sliding window 大小 $n_{win} = 128$

## 配置差异可以怎样理解

从这组配置可以看出几件事：

- `Flash` 和 `Pro` 共享同样的压缩率：`CSA` 都是 $m=4$，`HCA` 都是 $m'=128$。
- 主要差异不在压缩率，而在容量和检索强度：`Pro` 的 head 数更多，query 压缩维度更大，top-k 也从 `512` 提升到 `1024`。
- `HCA` 的压缩非常激进：相对 `CSA` 的 `4x` 压缩，`HCA` 是 `128x` 压缩，因此它更像大尺度全局摘要通道。
- `n_{win}=128` 说明即使在强压缩架构里，报告仍然保留了相当明确的一段局部未压缩上下文。

## 相关训练阶段设置

报告在 `4.2.2 Training Setups` 中还给出了一些会直接影响 `CSA/HCA` 使用方式的训练设置：

- 训练序列长度从 `4K` 逐步扩展到 `16K`、`64K`、`1M`
- 前 `1T tokens` 先使用 dense attention warmup
- 到 `64K` 序列长度时引入 sparse attention
- 引入稀疏注意力时，先单独 warm up `CSA` 的 lightning indexer，再进入长期稀疏训练阶段

这说明 `CSA/HCA` 不是从训练一开始就全量开启，而是随着上下文长度和训练阶段逐步引入。

## 在本 wiki 中

- [[models/deepseek-v4]] 把混合 `CSA + HCA` 作为核心结构升级之一。
- 这条线与 [[concepts/kv-cache]]、[[concepts/fp4-quantization-aware-training]]、[[concepts/grouped-query-attention]] 紧密相关。

## 相关页面

- [[concepts/kv-cache]]
- [[concepts/flashattention]]
- [[concepts/grouped-query-attention]]
- [[concepts/fp4-quantization-aware-training]]
- [[models/deepseek-v4]]
- [[sources/deepseek-v4-technical-report]]
