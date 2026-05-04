# Muon Optimizer

## 它是什么

`Muon` 是 `DeepSeek-V4` 在 `2.4` 节明确使用的主要优化器。报告说它被用于 `V4` 中“大多数模块”，理由是**收敛更快、训练更稳定**。

## 它要解决什么问题

`AdamW` 很稳，也很通用，但在超大模型训练里仍然存在几个成本：

- 收敛速度未必最优；
- 优化器状态较重；
- 某些模块的更新矩阵未必最适合逐元素自适应更新。

`Muon` 的思路不是像 `AdamW` 那样按元素维护一阶/二阶矩，而是把一个“逻辑独立的权重矩阵”作为矩阵对象来处理，并通过近似正交化得到更新方向。

## DeepSeek-V4 中的基本算法

报告在 Algorithm 1 给出了 `DeepSeek-V4` 使用的 `Muon` 版本。设某个逻辑独立的权重矩阵为：

$$
W \in \mathbb{R}^{n \times m}
$$

学习率为 $\eta$，动量系数为 $\mu$，权重衰减系数为 $\lambda$，更新重标定系数为 $\gamma$。

每一步更新流程如下。

### 1. 计算梯度

$$
G_t = \nabla_W L_t(W_{t-1})
$$

### 2. 更新动量缓冲

$$
M_t = \mu M_{t-1} + G_t
$$

### 3. 用 Nesterov trick 和 hybrid Newton-Schulz 得到正交化更新

$$
O_t' = \mathrm{HybridNewtonSchulz}(\mu M_t + G_t)
$$

这里报告明确说使用了 `Nesterov trick`。

### 4. 重标定更新矩阵的 RMS

$$
O_t = O_t' \cdot \sqrt{\max(n,m)} \cdot \gamma
$$

### 5. 做 weight decay 并更新参数

$$
W_t = W_{t-1}(1 - \eta \lambda) - \eta O_t
$$

可以看到，`Muon` 在 `DeepSeek-V4` 里的最终参数更新式仍然保留了与 `AdamW` 类似的 decoupled weight decay 形式，但核心更新方向来自矩阵级正交化，而不是逐元素自适应缩放。

## 哪些参数用 Muon，哪些不用

报告没有把所有参数都交给 `Muon`。它明确保留 `AdamW` 给下面这些模块：

- embedding 模块；
- prediction head；
- `mHC` 的静态 bias 和 gating factors；
- 所有 `RMSNorm` 模块的权重。

其余大多数模块才使用 `Muon`。这说明 `DeepSeek-V4` 实际上采用的是**混合优化器策略**，而不是全模型统一换掉 `AdamW`。

## Hybrid Newton-Schulz 是什么

对一个矩阵 $M$，设其奇异值分解为：

$$
M = U \Sigma V^{\top}
$$

`Newton-Schulz` 迭代的目标是把它近似正交化到：

$$
UV^{\top}
$$

通常先做归一化：

$$
M_0 = \frac{M}{\lVert M \rVert_F}
$$

然后每一步迭代：

$$
M_k =
a M_{k-1}
+ b (M_{k-1} M_{k-1}^{\top}) M_{k-1}
+ c (M_{k-1} M_{k-1}^{\top})^2 M_{k-1}
$$

`DeepSeek-V4` 采用的是 **hybrid Newton-Schulz**，共做 `10` 步：

- 前 `8` 步用系数

$$
(a,b,c) = (3.4445,\,-4.7750,\,2.0315)
$$

- 后 `2` 步切换到

$$
(a,b,c) = (2,\,-1.5,\,0.5)
$$

报告给出的解释是：

- 前一阶段追求快速把奇异值推近 `1`；
- 后一阶段追求把奇异值更稳定地固定在 `1` 附近。

## 它和 AdamW 的主要差别

从 `DeepSeek-V4` 的实现看，`Muon` 和 `AdamW` 的差别主要在更新方向构造方式：

- `AdamW`：逐元素追踪一阶/二阶矩，再按元素缩放。
- `Muon`：把矩阵当作整体，先做动量累积，再经过近似正交化得到更新。

因此 `Muon` 更像“矩阵几何结构驱动的更新”，而不是逐元素自适应学习率。

## 报告中的额外工程点

### 1. 复用 AdamW 的超参数体系

报告说他们会对更新矩阵的 RMS 做 rescale，以便复用原有 `AdamW` 超参数。

### 2. 不使用 QK-Clip

由于 `DeepSeek-V4` 的 attention 结构能直接对 query 和 KV entries 做 `RMSNorm`，报告说它们没有采用 `QK-Clip`。

### 3. 与 ZeRO 的冲突及解决

在 `3.5.1` 节，报告明确指出 `Muon` 需要完整梯度矩阵来计算更新，这与为逐元素优化器设计的传统 `ZeRO` 方式不完全兼容。

他们采用了混合 ZeRO bucket 策略：

- 对 dense 参数，限制 ZeRO 并行规模，再用 knapsack 分配矩阵到各 rank；
- 对 `MoE` 参数，按专家矩阵独立优化，并把同形状连续参数自动合并做 batched Newton-Schulz；
- 在数据并行通信中，把 `MoE` 梯度随机舍入到 `BF16` 再同步，以减半通信量；
- 再用 `all-to-all + 本地 FP32 求和` 替代常规 reduce-scatter，以维持数值稳健性。

## 在本 wiki 中

- [[models/deepseek-v4]] 将 `Muon` 列为训练栈升级的一部分。
- 它适合与 [[concepts/adamw]] 对照阅读，因为 `DeepSeek-V4` 实际上是“部分参数保留 AdamW，主体模块改用 Muon”。

## 相关页面

- [[concepts/adamw]]
- [[concepts/manifold-constrained-hyper-connections]]
- [[concepts/fp4-quantization-aware-training]]
- [[sources/deepseek-v4-technical-report]]
