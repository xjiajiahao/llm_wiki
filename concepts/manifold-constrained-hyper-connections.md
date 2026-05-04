# Manifold-Constrained Hyper-Connections

## 它是什么

`Manifold-Constrained Hyper-Connections`（`mHC`）是 `DeepSeek-V4` 在 `2.2` 节明确引入的残差路径升级。报告将其定义为：在标准 `Hyper-Connections`（`HC`）基础上，对残差映射施加流形约束，以增强深层堆叠时信号传播的稳定性。

## 它要解决什么问题

普通残差连接可以写成“输入直接加上子层输出”，而 `HC` 则把残差流从单一向量扩展成更宽的 residual stream，以增加表达能力。但报告指出，标准 `HC` 在多层堆叠时经常出现数值不稳定，阻碍其继续扩展。

`mHC` 的目标是同时保留两件事：

- `HC` 带来的更强残差表达能力；
- 深层训练时足够稳定的前向与反向信号传播。

## 标准 HC 的写法

报告先定义标准 `HC`。设第 $l$ 层之前的 residual state 为：

$$
X_l = [x_{l,1}; \dots; x_{l,n_{hc}}]^{\top} \in \mathbb{R}^{n_{hc} \times d}
$$

也就是说，残差流的宽度从 $\mathbb{R}^d$ 扩展到了 $\mathbb{R}^{n_{hc} \times d}$。

标准 `HC` 使用三个线性映射：

- 输入映射 $A_l \in \mathbb{R}^{1 \times n_{hc}}$
- 残差变换 $B_l \in \mathbb{R}^{n_{hc} \times n_{hc}}$
- 输出映射 $C_l \in \mathbb{R}^{n_{hc} \times 1}$

更新式为：

$$
X_{l+1} = B_l X_l + C_l F_l(A_l X_l)
$$

其中 $F_l$ 是第 $l$ 层实际计算模块，例如一个 `MoE` 层。注意：真正进入层内计算的输入 $A_l X_l$ 仍是 $d$ 维，因此残差宽度扩张不会直接改写内部层结构。

## mHC 的核心约束

`mHC` 的核心创新是：把残差映射矩阵 $B_l$ 约束到**双随机矩阵流形**上，也就是 Birkhoff polytope：

$$
B_l \in \mathcal{M} \triangleq
\{ M \in \mathbb{R}^{n \times n} \mid
M \mathbf{1}_n = \mathbf{1}_n,\;
\mathbf{1}_n^{\top} M = \mathbf{1}_n^{\top},\;
M \ge 0
\}
$$

这个约束的意义，报告说得很明确：

- $\lVert B_l \rVert_2 \le 1$，因此残差变换是 non-expansive；
- 前向传播和反向传播都更稳定；
- 这类矩阵集合对乘法封闭，因此深层堆叠时稳定性更容易保持。

## 为什么还要约束 A 和 C

除了 $B_l$ 之外，报告还要求：

- $A_l$
- $C_l$

也通过 `Sigmoid` 约束成非负且有界，避免信号相互抵消带来的数值风险。

## 动态参数化

`mHC` 不是给每层固定写死 $A_l, B_l, C_l$，而是把它们设计成“动态分量 + 静态分量”。

先对输入做展平和归一化：

$$
\hat{X}_l = \mathrm{RMSNorm}(\mathrm{vec}(X_l)) \in \mathbb{R}^{1 \times n_{hc}d}
$$

再生成未约束的原始参数：

$$
\tilde{A}_l = \alpha_l^{pre} (\hat{X}_l W_l^{pre}) + S_l^{pre}
$$

$$
\tilde{B}_l = \alpha_l^{res} \cdot \mathrm{Mat}(\hat{X}_l W_l^{res}) + S_l^{res}
$$

$$
\tilde{C}_l = \alpha_l^{post} (\hat{X}_l W_l^{post})^{\top} + S_l^{post}
$$

其中：

- $W_l^{pre}, W_l^{res}, W_l^{post}$ 负责生成输入相关的动态分量；
- $S_l^{pre}, S_l^{res}, S_l^{post}$ 是输入无关的静态偏置；
- $\alpha_l^{pre}, \alpha_l^{res}, \alpha_l^{post}$ 是可学习门控因子，且初始化很小。

这意味着 `mHC` 不是“每层一个固定残差矩阵”，而是会随当前 residual state 动态调整。

## 约束如何施加

对输入和输出映射，报告直接使用 `Sigmoid`：

$$
A_l = \sigma(\tilde{A}_l)
$$

$$
C_l = 2 \sigma(\tilde{C}_l)
$$

对残差映射 $\tilde{B}_l$，则投影到双随机矩阵流形上。报告采用 `Sinkhorn-Knopp` 算法：

先做指数，保证正性：

$$
M^{(0)} = \exp(\tilde{B}_l)
$$

然后迭代做列归一化和行归一化：

$$
M^{(t)} = T_r(T_c(M^{(t-1)}))
$$

最终得到：

$$
B_l = M^{(t_{max})}
$$

报告给出的实用设置是：

$$
t_{max} = 20
$$

## 可以怎样理解 mHC

`mHC` 的重点不是“多加一条残差边”，而是：

- 先把残差流扩成多路；
- 再让这些残差路之间做受约束的混合；
- 同时保证这种混合不会在深层网络里放大信号。

这比标准 residual 更灵活，也比不受约束的 `HC` 更稳定。

## 工程代价

报告在 `3.5.2` 节也明确说了，`mHC` 会增加：

- 激活内存；
- pipeline stage 之间的通信量。

为降低代价，他们做了三类工程优化：

- 训练和推理都实现 fused kernels；
- 通过 selective recomputation 节省内存；
- 调整 `DualPipe 1F1B` 重叠方案，兼容更高通信量。

报告声称，这些优化把 `mHC` 的 wall-time 开销压到了重叠后 `1F1B` pipeline stage 的 `6.7%`。

## 在本 wiki 中

- [[models/deepseek-v4]] 把 `mHC` 列为架构升级的一部分。
- 它应该和 [[concepts/transformer-block]]、[[concepts/rmsnorm]] 一起阅读，因为它本质上在改 block 间的残差路径。

## 相关页面

- [[concepts/transformer-block]]
- [[concepts/rmsnorm]]
- [[concepts/muon-optimizer]]
- [[sources/deepseek-v4-technical-report]]
