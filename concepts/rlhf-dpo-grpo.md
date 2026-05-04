# RLHF, DPO, and GRPO

## 它们是什么

这是一个对齐与后训练总览页，覆盖三类常见路线，并补充它们与经典 `PPO` 型 `RLHF` 的关系：

- `RLHF`：用人类偏好或奖励信号驱动强化学习优化。
- `DPO`：直接从偏好对构造目标函数，绕开显式奖励模型加 RL rollout 的整套链条。
- `GRPO`：一种基于组内相对比较的策略优化方法，当前 wiki 的 DeepSeek 来源明确提到它。

如果把 `RLHF` 再细分，经典实现里最常见的强化学习优化器之一就是 [[concepts/proximal-policy-optimization]]。

## 它们要解决什么问题

预训练模型学到的是“预测下一个 token”的能力，但聊天、工具使用、推理风格、安全边界和指令遵循，往往需要额外优化。后训练方法要解决的是：

- 如何把“会续写文本”变成“更符合人类偏好或任务目标”；
- 如何在质量、稳定性、成本之间做平衡；
- 如何在不完全可微的人类偏好信号下继续训练模型。

## RLHF 的基本流程

一个经典 `RLHF` 流程通常包括：

1. 先做 `SFT`，得到基本可对话的初始策略。
2. 收集偏好数据，例如同一提示下多个回答的排序。
3. 训练奖励模型 $r_\phi(x, y)$。
4. 用强化学习更新策略 $\pi_\theta(y \mid x)$，经典实现常选 `PPO` 一类稳定化策略梯度方法。

强化学习阶段通常会优化类似下面的目标：

$$
\max_{\theta}\ \mathbb{E}_{y \sim \pi_\theta(\cdot \mid x)}
\left[r_\phi(x, y)\right] - \beta \, \mathrm{KL}\!\left(\pi_\theta(\cdot \mid x)\,\|\,\pi_{\text{ref}}(\cdot \mid x)\right)
$$

其中 `KL` 项用于防止策略偏离参考模型过快。

## PPO 在 RLHF 里的位置

当 `RLHF` 采用 `PPO` 时，一个常见实现方式是：

- 奖励模型读取完整 `prompt + response`，输出一个序列级总分；
- 这个总分通常只在最后一个生成位置注入；
- 每个 token 同时会承担相对参考模型的 `KL` 惩罚；
- 价值函数负责把最终奖励向前传播，完成 token 级信用分配。

这意味着，大模型里的 `PPO` 虽然仍是策略梯度方法，但它面对的是长文本序列，而不是传统控制任务中的短时状态转移。

## RLHF 的单步奖励怎么构造

对 `LLM RLHF` 来说，一个关键区别是：奖励模型通常只给完整 `prompt + response` 一个标量总分，而不是逐 token 提供人工标注奖励。

当前来源描述的一种典型构造是：

$$
r_t^{\mathrm{RM}}=
\begin{cases}
0, & t < T \\
R_{\mathrm{final}}, & t = T
\end{cases}
$$

其中：

- $T$ 是生成结束位置；
- $R_{\mathrm{final}}$ 是奖励模型对整段回答的最终打分。

也就是说，主奖励往往是典型的稀疏奖励：大部分位置没有任务奖励，最后一个位置承接整段回答的总分。

## 为什么中间 token 仍然能学到东西

如果中间位置的主奖励都是 `0`，训练信号并不会消失，因为 value function 会承担信用分配工作。

在一阶近似下，中间位置的优势仍可以写成：

$$
A_t \approx r_t + \gamma V(s_{t+1}) - V(s_t)
$$

于是当 $t < T$ 且 $r_t = 0$ 时：

- 如果某个 token 让后续更可能通向高分回答，那么 $V(s_{t+1})$ 会高于 $V(s_t)$ 的折扣基线；
- 该 token 仍会得到正优势；
- 反之，如果某一步让后续回答质量预期下降，优势就会变负。

因此，序列级奖励并不是“只有最后一个 token 被训练”，而是“最后的总奖励先落在末端，再由 critic 向前传播成整段 token 的更新信号”。

## KL 惩罚为什么重要

除了最终奖励，`RLHF` 中常见的另一个逐 token 项是相对参考模型的 `KL` 惩罚。可写成：

$$
r_t = r_t^{\mathrm{RM}} + r_t^{\mathrm{KL}}
$$

其中常见的正则部分是：

$$
r_t^{\mathrm{KL}} = -\beta \log \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\mathrm{ref}}(a_t \mid s_t)}
$$

它提供的是逐 token 的稠密信号，用来：

- 防止策略为了刷高奖励模型分数而快速偏离参考分布；
- 保持语言流畅性和基本可读性；
- 缓解 reward hacking 和模式坍塌。

从这个角度看，`LLM PPO` 的奖励往往不是单一一项，而是“末端序列分数 + 逐 token KL 正则”的组合。

## 局限

这种奖励构造依赖两个前提：

- critic 必须足够准，才能把末端分数合理分配到前面 token；
- 序列不能长到让信用分配信号完全衰减。

这也是为什么后续会出现：

- 强调偏好监督直接优化的 `DPO`；
- 强调组内相对比较的 `GRPO`；
- 强调过程级奖励的 `PRM` 路线。

## DPO 的基本思想

`DPO` 的核心思路是：直接利用“偏好回答 $y^+$ 优于非偏好回答 $y^-$”这一监督信号，而不显式训练奖励模型再跑 RL。

一个常见形式会鼓励：

$$
\log \pi_\theta(y^+ \mid x) - \log \pi_\theta(y^- \mid x)
$$

相对参考模型有更高优势。直观上，它直接把偏好学习写成一个监督式目标，而不是显式 rollout + critic 的强化学习管线。

## GRPO 的高层理解

当前来源把 `GRPO` 描述为一种 group-relative 的策略优化方法。保守理解是：

- 它不一定依赖传统 actor-critic 那样的显式价值函数建模；
- 它会在一组候选输出内部做相对比较；
- 通过组内相对优势来更新策略。

在缺少更细原始公式前，本页不进一步补写它的精确目标函数。

## 三者的对比

- `RLHF`：表达能力强，可把复杂奖励纳入目标，但系统复杂、成本高。
- `DPO`：路径更直接，工程门槛通常更低，但依赖高质量偏好对。
- `GRPO`：强调组内相对优化，可能降低某些传统 RL 组件负担，但具体性质仍需看原始实现。

## 在本 wiki 中

- [[models/deepseek-v3]] 明确提到 `GRPO` 所在的后训练脉络。
- [[concepts/on-policy-distillation]] 可以看作更靠后的能力统一阶段，而不是偏好学习本身。

## 相关页面

- [[concepts/on-policy-distillation]]
- [[concepts/policy-gradient]]
- [[concepts/proximal-policy-optimization]]
- [[sources/deepseek-v3-technical-report]]
- [[sources/deepseek-v4-technical-report]]
- [[sources/ppo-algorithm-explanation-conversation]]

## 待补充

- `GRPO` 的正式目标函数。
- `RLAIF`、`IPO`、`ORPO` 等近邻方法。
