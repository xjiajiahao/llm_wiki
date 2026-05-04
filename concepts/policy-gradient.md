# Policy Gradient

## 它是什么

`Policy Gradient` 是一类直接优化策略 $\pi_\theta(a \mid s)$ 的强化学习方法。与先学 `Q(s,a)` 再做 $\arg\max$ 的价值型方法不同，它直接把“在状态下输出动作分布”的策略本身当作优化对象。

它特别适合：

- 需要随机策略的场景；
- 连续动作空间；
- 希望直接用梯度方法更新策略网络的场景。

## 它要解决什么问题

价值型方法在离散动作空间中很有效，但它们往往：

- 难以自然处理连续动作；
- 最终容易收敛到确定性策略；
- 通过 $\arg\max$ 选动作时，不便于直接对策略本身求导。

`Policy Gradient` 的核心目标是：直接最大化策略在环境中的期望回报。

## 基本目标

把一条完整轨迹记为 $\tau$，其总回报记为 $R(\tau)$。策略优化目标通常写成：

$$
J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}[R(\tau)]
$$

借助对数导数技巧，可以得到一个经典的无偏梯度形式：

$$
\nabla_\theta J(\theta)
=
\mathbb{E}_{\tau \sim \pi_\theta}
\left[
\sum_t \nabla_\theta \log \pi_\theta(a_t \mid s_t)\, R_t
\right]
$$

其中 $R_t$ 可以是整条轨迹回报，也可以是从时刻 $t$ 开始的未来回报。

这个式子的直觉是：

- 如果某次采样最终回报高，就提高这条轨迹上已采取动作的概率；
- 如果最终回报低，就降低这些动作的概率。

## 它怎么工作

最朴素的 `REINFORCE` 路线通常分三步：

1. 用当前策略与环境交互，采样轨迹。
2. 计算每一步对应的回报或未来回报。
3. 按 $\nabla_\theta \log \pi_\theta(a_t \mid s_t)$ 加权更新策略参数。

在实现上，这意味着：

- 前向时从策略分布中采样动作；
- 反向时根据 `log-prob × return` 的形式更新参数；
- 用梯度上升最大化期望回报。

## 为什么它不够

纯 `Policy Gradient` 的主要问题是高方差和信用分配困难。

- 高方差：如果直接用整条轨迹回报作为权重，同一轨迹中的好坏动作会被同样表扬或批评。
- 信用分配困难：最终结果往往只由部分关键动作决定，但基础方法很难准确区分。
- 样本效率有限：很多简单策略梯度方法一批数据只更新一次。

## 常见改进

为了降低方差，通常会引入 baseline 或 value function。一个常见写法是用优势函数：

$$
A(s_t, a_t) = Q(s_t, a_t) - V(s_t)
$$

把梯度改写为：

$$
\nabla_\theta J(\theta)
=
\mathbb{E}
\left[
\sum_t \nabla_\theta \log \pi_\theta(a_t \mid s_t)\, A_t
\right]
$$

这样可以把“这一步比平均策略好多少”作为更稳定的学习信号。

## 为什么 baseline 能降方差

`Policy Gradient` 里最常见的降方差技巧，是把原本直接乘回报的项

$$
\nabla_\theta \log \pi_\theta(a_t \mid s_t)\, R_t
$$

改成减去 baseline 之后的形式：

$$
\nabla_\theta \log \pi_\theta(a_t \mid s_t)\, (R_t - b(s_t))
$$

关键点不只是“经验上更稳”，而是这个改写在合适条件下不改变梯度期望。

对任意只依赖状态、而不依赖已采样动作的 baseline $b(s_t)$，有：

$$
\mathbb{E}_{a_t \sim \pi_\theta(\cdot \mid s_t)}
\left[
\nabla_\theta \log \pi_\theta(a_t \mid s_t)\, b(s_t)
\right]
=
b(s_t)\sum_{a_t}\pi_\theta(a_t \mid s_t)\nabla_\theta \log \pi_\theta(a_t \mid s_t)
$$

再利用

$$
\pi_\theta(a \mid s)\nabla_\theta \log \pi_\theta(a \mid s)=\nabla_\theta \pi_\theta(a \mid s)
$$

可得

$$
b(s_t)\sum_{a_t}\nabla_\theta \pi_\theta(a_t \mid s_t)
=
b(s_t)\nabla_\theta \sum_{a_t}\pi_\theta(a_t \mid s_t)
=
b(s_t)\nabla_\theta 1
=
0
$$

因此，减去这样的 baseline 不会引入偏差，但通常会显著降低方差。

直觉上，它把“绝对回报”改成“相对平均水平的超额收益”。这样更新时更关心“这一步比预期好还是坏”，而不是让每一步都背负整条轨迹的总噪声。

## 为什么方差会更小

“无偏”只说明均值没变，还没有解释为什么波动会变小。对单步梯度估计器，记：

$$
g_t=\nabla_\theta \log \pi_\theta(a_t \mid s_t)\,(R_t-b(s_t))
$$

在固定状态 $s_t$ 的条件下，baseline 唯一在做的事，就是把随机变量 $R_t$ 平移成 $R_t-b(s_t)$。虽然这不会改变期望梯度，但会改变估计器的二阶矩，也就是波动大小。

如果把

$$
z_t=\nabla_\theta \log \pi_\theta(a_t \mid s_t)
$$

记作 score function，那么条件二阶矩可以写成：

$$
\mathbb{E}\left[\|g_t\|^2 \mid s_t\right]
=
\mathbb{E}\left[\|z_t\|^2 (R_t-b(s_t))^2 \mid s_t\right]
$$

因为方差等于“二阶矩减去均值平方”，而 baseline 不改变均值，所以要让方差变小，本质上就是要让上面的量尽量小。

把它看成关于 $b(s_t)$ 的二次函数，可以得到最优 baseline：

$$
b^*(s_t)=
\frac{
\mathbb{E}\left[\|z_t\|^2 R_t \mid s_t\right]
}{
\mathbb{E}\left[\|z_t\|^2 \mid s_t\right]
}
$$

这说明最理想的 baseline，本质上是在“以梯度幅度为权重”的意义下，去拟合当前状态下的平均回报。

如果进一步忽略不同动作对应的 $\|z_t\|^2$ 差异，把它粗略当成变化不大的量，那么上式会近似退化成：

$$
b^*(s_t)\approx \mathbb{E}[R_t \mid s_t]=V(s_t)
$$

这就是为什么状态价值函数会成为最自然、最常见的 baseline。

## 直觉上到底去掉了什么噪声

没有 baseline 时，梯度项会把两类信息混在一起：

- 状态本身“容易还是困难”；
- 这个动作相对于该状态平均水平“到底更好还是更坏”。

其中第一类信息往往会带来很大的共享波动，但它对“该不该增加这个动作概率”并没有那么直接。

减去 $b(s_t)$ 之后：

- 每个动作不再背负这个状态的公共回报偏置；
- 真正留下来的，是“相对该状态平均水平的残差”；
- 因而不同采样轨迹之间更容易互相抵消状态噪声，而不是把它放大到梯度里。

一个直观例子是：假设某个状态天然就容易得到高分，那么在这个状态里几乎所有动作的 $R_t$ 都偏大。若不减 baseline，所有采样动作都会被整体推高；减去 $V(s_t)$ 后，只有那些比该状态平均动作更好的动作，才会保留明显正优势。

## 为什么 value function 不是“完美 baseline”也依然有用

真实最优 baseline 依赖未知分布，通常无法直接算出，所以工程里会学习一个近似的 $V(s_t)$。它不需要完全精确，仍然可能显著降方差：

- 只要它能解释掉一部分“状态级公共波动”，剩余残差就会更小；
- 残差更小，梯度估计更稳定；
- 梯度更稳定，就能用更少样本得到更可靠的更新方向。

因此，baseline 的收益不是“把问题变成无噪声”，而是把原本由整条轨迹总回报主导的粗糙信号，压缩成更接近动作相对优劣的信号。

## 为什么 value function 是好的 baseline

如果把 baseline 取成状态价值函数 $V(s_t)$，就得到优势函数：

$$
A(s_t,a_t)=Q(s_t,a_t)-V(s_t)
$$

它衡量的是：

- 当前动作带来的未来回报；
- 相对于“在这个状态下平均能拿到多少回报”的偏离。

这比直接用 $R_t$ 更有针对性，因为：

- 状态本身的难度被 $V(s_t)$ 吸收掉了；
- 真正驱动更新的是“动作是否比这个状态下的平均选择更好”；
- 当 value function 学得更准时，策略梯度的方差会继续下降。

这一路线会自然通向：

- `actor-critic`：策略网络负责选动作，价值网络负责提供 baseline；
- `GAE`：更稳定地估计 $A_t$；
- [[concepts/proximal-policy-optimization]]：在策略梯度之上进一步限制更新步长。

## 在 LLM 后训练里的意义

当 `RLHF` 用强化学习微调大语言模型时，模型本质上也是在优化一个“给定上下文时，下一个 token 的策略分布”。因此：

- `LLM` 的 token 生成策略可以看作一个高维、离散但可微的随机策略；
- `PPO` 等方法是在 `policy gradient` 框架上，为这种 token 级策略更新增加稳定化约束；
- 奖励模型给出的序列级评分，需要再通过价值函数或相对比较机制分配到 token 级更新。

## 相关页面

- [[concepts/proximal-policy-optimization]]
- [[concepts/rlhf-dpo-grpo]]
- [[sources/ppo-algorithm-explanation-conversation]]

## 待补充

- 增补 `REINFORCE` 原始论文来源。
- 单独拆出 `actor-critic` 与 `advantage estimation` 页面。
