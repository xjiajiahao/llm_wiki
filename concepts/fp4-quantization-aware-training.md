# FP4 Quantization-Aware Training

## 它是什么

`DeepSeek-V4` 在 `3.4` 节明确引入了 `FP4 Quantization-Aware Training`（`QAT`）。报告给出的定位很清楚：这是为了在部署阶段获得**推理加速**和**显存节省**，而在训练时就让模型适应量化带来的精度退化。

## 它要解决什么问题

对 `DeepSeek-V4` 这样的长上下文 `MoE` 模型，内存和带宽开销主要集中在几类对象上：

- `MoE` expert weights；
- 长上下文注意力里的缓存与读取；
- attention score 相关路径上的乘法与 top-k 选择。

单纯在训练后再做低比特量化，往往会带来明显精度退化。`QAT` 的目标就是：在训练阶段就把量化误差纳入优化过程，让部署时的低精度执行成为模型已经适应过的运行模式。

## DeepSeek-V4 具体量化了哪些部分

报告明确写了两类：

### 1. MoE expert weights

这是 GPU 显存占用的大头之一。

### 2. CSA indexer 的 Query-Key 路径

报告说，在 `CSA` 的 indexer 里，`QK` 激活会被：

- 缓存；
- 读取；
- 相乘；

并且这些过程**全部在 FP4 中执行**，以加速超长上下文下的 attention score 计算。

除此之外，报告还把 index scores $I_{:,:}$ 从 `FP32` 量化到 `BF16`，并给出了具体收益：

- top-k selector `2x` 加速；
- 同时保持 `99.7%` 的 KV entry recall。

## MoE expert weights 的 QAT 流程

报告给出的流程是：

1. 优化器维护 `FP32 master weights`；
2. 这些权重先被量化到 `FP4`；
3. 再反量化回 `FP8` 参与前向计算。

也就是说，训练时不是直接拿 `FP4` 做所有主计算，而是通过“`FP4` 约束 + `FP8` 计算”的方式，把量化影响注入训练。

## 为什么 FP4 到 FP8 的反量化可以无损

报告特别强调，它们的 `FP4 -> FP8` 反量化是 **lossless**。给出的理由是：

- `FP8 (E4M3)` 相比 `FP4 (E2M1)` 多了 `2` 个 exponent bits；
- 因此 `FP8` 有更大的动态范围；
- 只要一个 `FP8` 量化块内部，各个 `FP4` 子块的 scale factor 比值不超过某个阈值，这些更细粒度的 scale 信息就能被 `FP8` 的动态范围完全吸收。

报告还说明，他们经验上验证了当前权重满足这一条件。

## 这为什么很关键

因为它带来两个直接结果：

- 整个 `QAT` 流程可以**完全复用现有 FP8 训练框架**；
- 无需为了 `FP4` 再重写一套主训练路径。

这也是 `DeepSeek-V4` 工程上很重要的一点：不是从零另起炉灶，而是把更低精度方案嫁接到已成熟的 `FP8` 基础设施上。

## 反向传播怎么做

报告说，在 backward pass 中：

- 梯度是相对于前向里那份 `FP8` 权重计算出来的；
- 然后直接传播回 `FP32 master weights`。

这等价于通过量化操作使用 `Straight-Through Estimator`（`STE`）。

报告还指出，这样做还能避免重新量化转置权重。

## 推理和 RL rollout 阶段如何处理

在不需要 backward 的阶段，也就是：

- inference；
- RL training 里的 rollout；

报告说他们**直接使用真实的 FP4 量化权重**，而不是训练期的模拟量化。

这样做的意义有两层：

- 在线采样行为和真实部署保持一致；
- kernel 内存加载更少，从而获得真实速度提升和更低内存消耗。

`CSA` indexer 里的 `QK` 路径也采用了类似处理。

## 它和普通“训练后量化”的区别

如果只是训练后量化，模型训练时从没见过低比特误差；而 `QAT` 是在训练过程中就让模型适应这些误差。

因此 `DeepSeek-V4` 的 `FP4` 方案不是简单部署技巧，而是：

- 训练框架；
- 注意力路径；
- 推理路径；

三者联动的低精度设计。

## 报告中的收益表述

报告在摘要与基础设施部分给出的稳定说法包括：

- `FP4 QAT` 用于 `MoE` expert weights 和 `CSA` indexer 的 `QK` 路径；
- index scores 从 `FP32` 到 `BF16` 可使 top-k selector 获得 `2x` 加速；
- `routed expert parameters` 在推理中使用 `FP4 precision`；
- 当前硬件上 `FP4 × FP8` 的峰值 FLOPs 与 `FP8 × FP8` 相同，但未来硬件理论上可做到约 `1/3` 更高效率。

## 在本 wiki 中

- [[models/deepseek-v4]] 把 `FP4` 作为效率栈的一部分。
- 它可以视作 [[concepts/fp8-training]] 向更低精度、更强部署一致性方向的延伸。

## 相关页面

- [[concepts/fp8-training]]
- [[concepts/mixture-of-experts]]
- [[concepts/attention-for-long-context]]
- [[sources/deepseek-v4-technical-report]]
