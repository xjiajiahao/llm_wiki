# Proximal Policy Optimization

## 它是什么

`PPO` 是一种基于 `policy gradient` 的强化学习算法。它的目标是：在保留较高样本效率的同时，限制每次策略更新不要偏离旧策略过远。

它通常被视为：

- 比朴素策略梯度更稳定；
- 比 `TRPO` 更容易实现；
- 在工程上非常常见的 `actor-critic` 基线。

## 它要解决什么问题

如果策略更新步长过大，采样数据所对应的分布会迅速失效，训练可能出现性能骤降或直接崩溃。`TRPO` 试图通过 trust region 约束解决这个问题，但实现需要较复杂的二阶优化。

`PPO` 的关键想法是：不用显式求解复杂约束，而是在目标函数里直接惩罚“新策略相对旧策略改动太大”的情况。

## 核心目标函数

把新旧策略在同一状态动作对上的概率比写成：

$$
r_t(\theta)=\frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{\mathrm{old}}}(a_t \mid s_t)}
$$

`PPO-Clip` 的核心目标通常写成：

$$
L^{\mathrm{CLIP}}(\theta)=\mathbb{E}_t\left[\min\left(r_t(\theta)A_t,\ \operatorname{clip}(r_t(\theta),1-\epsilon,1+\epsilon)A_t\right)\right]
$$

其中：

- $A_t$ 是优势函数；
- $\epsilon$ 是允许的策略偏移带宽，常见经验值约为 `0.2`。

这个目标的直觉是：

- 当某动作确实更好时，允许提高它的概率；
- 但如果提高得太多，就用 clipping 截住收益；
- 当某动作更差时，也同样限制“惩罚得过头”。

## 训练流程

现代 `PPO` 常见流程通常是：

1. 用旧策略采样一批轨迹。
2. 由价值函数估计每一步的优势 $A_t$。
3. 把同一批数据打乱成 mini-batch，重复多轮 `SGD` 更新。
4. 联合优化策略损失、价值损失和熵正则。

常见总目标可写成：

$$
L(\theta)=L^{\mathrm{CLIP}}(\theta)-c_1 L^{\mathrm{VF}}(\theta)+c_2 S[\pi_\theta]
$$

这里：

- $L^{\mathrm{VF}}$ 是价值函数损失，通常是对目标价值的回归；
- $S[\pi_\theta]$ 是熵项，用来维持探索；
- $c_1, c_2$ 是平衡不同损失量级的系数。

## 优势函数与 GAE

`PPO` 往往不直接使用原始回报，而是先估计优势。一个常见路线是 `GAE`：

$$
\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)
$$

$$
A_t = \delta_t + \gamma \lambda A_{t+1}
$$

其中：

- $\gamma$ 是折扣因子；
- $\lambda$ 控制偏差与方差的折中。

这使 `PPO` 比只靠整条轨迹回报的策略梯度更稳定。

在实现上，一个常见构造是先用旧价值函数算出 $A_t$，再令：

$$
V_{\mathrm{target}}(s_t)=V_{\mathrm{old}}(s_t)+A_t
$$

把它作为 critic 的回归目标。

## 为什么不准的 $V_{old}$ 不一定会把训练带崩

直觉上，很多人会担心：既然 $A_t$ 本身依赖 $V_{\mathrm{old}}$，那么一个很差的初始 value function 会不会导致“错误 target 训练错误 critic”，再把错误一层层放大。

从当前来源可保守总结出的关键点是：通常不会直接因此崩溃，因为 `PPO` 的 value target 并不只是“旧 value 的自我复制”，而是持续被真实奖励锚定。

把 `GAE` 展开后可以看到，$V_{\mathrm{target}}$ 里会反复出现真实的 $r_t$ 项，而 $V_{\mathrm{old}}(s_t)$ 本身会在

$$
\delta_t = r_t + \gamma V_{\mathrm{old}}(s_{t+1}) - V_{\mathrm{old}}(s_t)
$$

中部分抵消。结果是：

- 即便 $V_{\mathrm{old}}$ 很粗糙，target 仍然包含来自环境的真实奖励信号；
- 如果初始 $V_{\mathrm{old}}$ 很差，critic loss 反而会更大，从而产生更强的修正梯度；
- 随着多轮 `epoch` 在同一批数据上拟合，critic 往往会快速从“近似零”收敛到一个更合理的尺度。

当前这份讲解来源给出的经验性结论是：`V_old` 更像一个用于减方差的基线，而不是唯一决定 target 的真值来源。

## $V_{old}$ 常见初始化方式

在讲解型资料里，最常见的初始化理解有两种：

- 让 critic 输出层从接近 `0` 的小值开始；
- 用标准随机初始化，使最初的 $V(s)$ 也接近 `0`。

如果一开始 $V_{\mathrm{old}}(s)\approx 0$，那么早期训练可近似看作“高方差但方向通常可用”的 Monte Carlo 式回归。随着 critic 逐步拟合回报，后续优势估计会更稳定。

这里应明确保留不确定性：

- “零初始化输出层”是常见工程做法之一，但不是本 wiki 当前来源能严格证明的唯一标准；
- 不同实现是否固定 `V_target`、是否在每轮重算优势，也会影响这个收敛过程的细节。

## Value Clipping

除了策略 clipping，一些 `PPO` 实现还会对价值函数更新加 clipping，以避免 critic 在单轮更新里漂移太远。一个常见写法是：

$$
L_{\mathrm{VF}}^{\mathrm{clip}}(\theta)=
\mathbb{E}_t\left[
\max\left(
(V_\theta(s_t)-V_{\mathrm{target}})^2,\,
(\operatorname{clip}(V_\theta(s_t),V_{\mathrm{old}}(s_t)-\epsilon_{\mathrm{vf}},V_{\mathrm{old}}(s_t)+\epsilon_{\mathrm{vf}})-V_{\mathrm{target}})^2
\right)
\right]
$$

它的作用是：

- 防止 critic 在一次更新中跳得过远；
- 降低“优势估计基线突然塌掉”带来的不稳定；
- 在多 epoch 复用同一批数据时，让 value 学习更保守。

并非所有实现都会启用这一步，但它是值得记录的 `PPO` 工程变体。

## 常见变体

- `PPO-Clip`：最常见版本，用 clipping 限制策略变化。
- `PPO-Penalty`：把 `KL` 惩罚直接放进目标中，并根据偏移程度动态调节系数。

从工程使用频率看，`PPO-Clip` 更常见。

## 在 LLM RLHF 中怎么用

在 `LLM RLHF` 里，`PPO` 的“动作”通常就是逐 token 生成。这里有几个关键点：

- 奖励模型往往读取完整 `prompt + response`，输出一个序列级标量分数；
- 这个最终分数常被放在最后一个生成位置，前面位置不直接得到任务奖励；
- 逐 token 的 `KL` 惩罚常作为稠密正则项，防止策略偏离参考模型过远；
- 价值函数负责把最终奖励向前传播，从而完成 token 级信用分配。

因此，`LLM RLHF` 里的 `PPO` 不是“每个 token 都有独立人工打分”，而是“序列级奖励 + 逐 token 正则 + 价值函数回传”的组合。

## 局限与权衡

- 仍然依赖超参数，尤其是学习率、clip 范围、batch 大小和优势估计质量。
- 如果价值函数学得很差，策略更新仍会有较大噪声。
- 在长序列 `LLM RLHF` 里，信用分配比传统短轨迹控制任务更困难。
- 随着 `DPO`、`GRPO` 等方法普及，`PPO` 不再是唯一主流路线，但仍是理解 `RLHF` 的经典基线。

## 在本 wiki 中

- [[concepts/policy-gradient]] 是它的前置概念。
- [[concepts/rlhf-dpo-grpo]] 记录它在大模型对齐流程中的位置。
- [[sources/ppo-algorithm-explanation-conversation]] 是当前引入本页的讲解型来源。

## 待补充

- 用 `PPO` 原始论文补出更正式的记号和变体差异。
- 单独拆出 `GAE` 页面。
- 加入 `TRL` 或 `OpenRLHF` 一类实现级来源，补足 `LLM PPO` 的工程细节。
