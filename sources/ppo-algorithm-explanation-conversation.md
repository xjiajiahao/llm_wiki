# PPO 算法讲解对话

## 来源记录

- 原始文件：`raw/讲解PPO算法：近端策略优化-20260318211727.json`
- 原始路径：[讲解PPO算法：近端策略优化-20260318211727.json](/Users/xiejh/code/playground/llm_wiki/raw/%E8%AE%B2%E8%A7%A3PPO%E7%AE%97%E6%B3%95%EF%BC%9A%E8%BF%91%E7%AB%AF%E7%AD%96%E7%95%A5%E4%BC%98%E5%8C%96-20260318211727.json)
- 文件名日期：`2026-03-18`
- 仓库文件时间戳：`2026-05-04 10:26:32 CST`
- 文件大小：`52,785 bytes`
- SHA-256：`c2e75c29f1196adee67525b11a68fc7c97ef5d3c7620c2809c25f573d5bd7abc`
- 来源类型：讲解型问答记录，不是 `PPO` 或 `RLHF` 的原始论文

## 摘要

这份原始材料是一段围绕 `PPO` 的中文讲解对话，内容从 [[concepts/policy-gradient]] 起步，逐步解释 [[concepts/proximal-policy-optimization]]、`GAE`、价值函数训练，以及 `LLM RLHF` 中“序列级奖励如何变成 token 级训练信号”。

作为二手讲解材料，它的价值主要在于：

- 用连续问答形式把 `policy gradient -> actor-critic -> GAE -> PPO -> RLHF` 串成一条学习路径；
- 给出 `PPO-Clip` 的核心目标函数、优势函数递推和价值损失的直观解释；
- 明确指出 `LLM RLHF` 往往只对完整回答打一个最终分数，而中间 token 的信用分配主要依赖价值函数；
- 补充了 `KL` 惩罚在 `RLHF` 中作为逐 token 稠密奖励的作用。

## 可稳定抽出的要点

- `PPO` 的核心目标是保留 `TRPO` 的“限制策略更新幅度”思想，但用更简单的一阶优化与 clipping 目标替代显式 trust region 求解。
- `PPO-Clip` 的核心比率是

$$
r_t(\theta)=\frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{\mathrm{old}}}(a_t \mid s_t)}
$$

并通过

$$
L^{\mathrm{CLIP}}(\theta)=\mathbb{E}_t\left[\min\left(r_t(\theta)A_t,\ \operatorname{clip}(r_t(\theta),1-\epsilon,1+\epsilon)A_t\right)\right]
$$

来抑制过大的策略步长。
- 对话把 `GAE` 写成优势估计的标准路径：先算

$$
\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)
$$

再做

$$
A_t = \delta_t + \gamma \lambda A_{t+1}
$$

的反向递推。
- `PPO` 往往配合 `actor-critic` 架构使用，策略损失之外还会联合优化价值损失和熵正则。
- 在 `LLM RLHF` 语境里，奖励模型通常读取完整 `prompt + response` 后输出一个标量总分；常见实现是把这个总分放在最后一个生成位置，而中间位置只拿到 `KL` 惩罚等稠密正则项。
- 对话还给出了一段有用的解释链条：baseline 为什么不改变期望梯度、为什么较差的 `V_old` 通常不会单独导致训练崩溃，以及为什么“只有最终总分”的 `RLHF` 仍能训练中间 token。

## 关联页面

- [[concepts/policy-gradient]]
- [[concepts/proximal-policy-optimization]]
- [[concepts/rlhf-dpo-grpo]]

## 待继续处理

- 用 `PPO` 原始论文和 `GAE` 原始论文校正这里的讲解性表述。
- 单独补出 `advantage estimation` 页面，避免把 `GAE` 长期只附着在 `PPO` 页面中。
- 如后续加入 `InstructGPT`、`TRL` 或 `OpenRLHF` 等更接近 `LLM RLHF` 实作的来源，可再把本页中的 `RLHF` 细节升级为更可核验版本。
