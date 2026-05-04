# Multi-Head Latent Attention

## 它是什么

`Multi-Head Latent Attention`（`MLA`）是 `DeepSeek-V3` 报告在 `2.1.1` 节明确给出的注意力结构。它的核心思路是：不要像标准多头注意力那样把每个 token 的完整多头 `K/V` 都缓存起来，而是先把 `K/V` 压到一个低秩 latent 表示里，再在需要时恢复出各头使用的表示。

## 它要解决什么问题

标准 `MHA` 的主要问题之一是推理期 `KV cache` 很大。假设隐藏维度为 $d$，头数为 $n_h$，每头维度为 $d_h$，那么缓存成本大致随 $n_h d_h$ 和上下文长度线性增长。长上下文推理时，这会直接转化为：

- 更高的显存占用；
- 更高的带宽读取成本；
- 更低的并发吞吐。

`MLA` 的目标就是在尽量维持模型效果的前提下，把缓存从“完整多头 K/V”压缩成“低维 latent + 少量位置相关分量”。

## 报告中的基本构造

设第 $t$ 个 token 在某一层 attention 的输入为 $h_t \in \mathbb{R}^d$。

### 1. 对 Key/Value 做联合低秩压缩

报告先把输入下投影成一个共享的压缩 latent：

$$
c_t^{KV} = W^{DKV} h_t
$$

其中 $c_t^{KV} \in \mathbb{R}^{d_c}$，且 $d_c \ll d_h n_h$。

然后从这个 latent 中恢复各头共享内容部分的 key 和 value：

$$
[k_{t,1}^C; k_{t,2}^C; \dots; k_{t,n_h}^C] = k_t^C = W^{UK} c_t^{KV}
$$

$$
[v_{t,1}^C; v_{t,2}^C; \dots; v_{t,n_h}^C] = v_t^C = W^{UV} c_t^{KV}
$$

### 2. 单独构造携带位置编码的 key 分量

报告把带 `RoPE` 的部分从主压缩路径里拆出来：

$$
k_t^R = \mathrm{RoPE}(W^{KR} h_t)
$$

然后对每个头，把内容分量和位置分量拼接起来：

$$
k_{t,i} = [k_{t,i}^C; k_t^R]
$$

这里一个很关键的点是：**推理时只需要缓存 $c_t^{KV}$ 和 $k_t^R$**。报告明确指出，这两个蓝框向量就是生成阶段需要保留的缓存对象，因此 `KV cache` 会显著小于标准 `MHA`。

## Query 也做低秩压缩，但目标不同

对于 query，报告同样做低秩压缩，不过重点是降低训练时的激活内存，而不是缓存历史状态：

$$
c_t^Q = W^{DQ} h_t
$$

$$
[q_{t,1}^C; q_{t,2}^C; \dots; q_{t,n_h}^C] = q_t^C = W^{UQ} c_t^Q
$$

$$
[q_{t,1}^R; q_{t,2}^R; \dots; q_{t,n_h}^R] = q_t^R = \mathrm{RoPE}(W^{QR} c_t^Q)
$$

$$
q_{t,i} = [q_{t,i}^C; q_{t,i}^R]
$$

报告这里区分了两个压缩维度：

- $d_c$：`K/V` 压缩维度；
- $d_c'$：`Q` 压缩维度。

两者都远小于完整多头展开维度 $d_h n_h$。

## 注意力输出如何计算

在得到每个头的 $q_{t,i}$、$k_{j,i}$ 和 $v_{j,i}^C$ 后，报告给出的单头输出是：

$$
o_{t,i} =
\sum_{j=1}^{t}
\mathrm{Softmax}_j
\left(
\frac{q_{t,i}^{\top} k_{j,i}}{\sqrt{d_h + d_h^R}}
\right)
v_{j,i}^C
$$

最终多头拼接后再输出：

$$
u_t = W^O [o_{t,1}; o_{t,2}; \dots; o_{t,n_h}]
$$

这里的缩放项写成 $\sqrt{d_h + d_h^R}$，因为 query/key 里拼接了内容维和 RoPE 相关维。

## 可以怎样理解 MLA

从结构上看，`MLA` 做了两件事：

1. 用共享 latent 压缩大头的 `K/V` 信息；
2. 把位置相关部分单独保留，避免压缩后丢失关键位置信息。

所以它不是简单的 `GQA/MQA` 风格“共享 K/V 头”，也不是只在 kernel 层做压缩，而是直接改变了 `Q/K/V` 的参数化方式和缓存对象。

## 它为什么能省 KV cache

标准多头注意力通常需要缓存每个 token 的完整多头 `K/V`。而在 `MLA` 中，报告明确说缓存的是：

- 压缩 latent $c_t^{KV}$；
- 解耦出来的 RoPE key 分量 $k_t^R$。

这意味着历史状态的缓存规模不再直接等于“所有头的完整 K/V 展开”，而是等于“一个低维 latent 加一个较小的位置分量”，因此能显著降低推理缓存。

## 它与训练/推理分别有什么意义

- 对推理：主要收益是减少 `KV cache`。
- 对训练：query 的低秩压缩还能降低激活内存。

这也是为什么 `DeepSeek-V3` 把 `MLA` 作为“高效推理”和“成本可控训练”共同服务的基础部件。

## 在本 wiki 中

- [[models/deepseek-v3]] 把 `MLA` 作为基础架构的一部分。
- [[models/deepseek-v4]] 则把注意力主叙事转向 `CSA + HCA`，不再以 `MLA` 为主线。

## 相关页面

- [[concepts/attention-for-long-context]]
- [[concepts/kv-cache]]
- [[concepts/transformer-block]]
- [[sources/deepseek-v3-technical-report]]

## 待补充

- `MLA` 相对 `MHA/GQA` 的缓存规模定量对比。
- `DeepSeek-V2` 中更完整的 `MLA` 背景和实现细节。
