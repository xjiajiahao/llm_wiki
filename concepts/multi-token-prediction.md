# Multi-Token Prediction

## 它是什么

`Multi-token prediction`（`MTP`）是一类训练目标：模型在给定当前上下文时，不只预测“下一个 token”，而是同时学习预测更远的多个未来 token。

## 它要解决什么问题

标准自回归语言模型通常只优化一步预测：

$$
\mathcal{L}_{\text{next}} = -\sum_t \log p(x_{t+1} \mid x_{\le t})
$$

这种目标很自然，但也有局限：

- 它只直接监督一步之后的局部正确性；
- 对更长跨度的规划或未来结构感知监督较弱；
- 在某些推理或加速设置里，模型对多步未来缺少直接训练信号。

`MTP` 的目标是给模型更丰富的未来监督。

## 基本形式

如果同时监督未来 $K$ 个位置，则一个抽象化目标可以写成：

$$
\mathcal{L}_{\text{MTP}} =
- \sum_t \sum_{k=1}^{K} w_k \log p(x_{t+k} \mid x_{\le t})
$$

其中：

- $K$ 是预测跨度；
- $w_k$ 是不同步长的权重；
- 具体实现里，也可能不是所有未来步共享同一头部或同一结构。

## 它可能带来的收益

- 让表示对更长程的未来结构更敏感；
- 在推理或草稿生成类方法里，给并行或块级预测提供训练基础；
- 在相同上下文下，增加每个位置的监督信号密度。

## 主要实现差异

不同论文里，`MTP` 可能有不同实现：

- 共享主干、增加多个预测头；
- 用额外模块做未来 token 预测；
- 只在训练阶段存在，推理阶段仍按标准自回归方式解码。

因此，读具体模型报告时要区分“概念名一样”和“实现完全一样”这两件事。

## 在本 wiki 中

- [[models/deepseek-v3]] 把 `MTP` 作为重点模型贡献之一。
- [[models/deepseek-v4]] 在改动注意力和系统栈的同时，仍然保留了 `MTP`。

这说明在当前来源集中，`MTP` 被视为一个值得沿用的有效方向。

## 相关页面

- [[concepts/mixture-of-experts]]
- [[concepts/transformer-block]]
- [[sources/deepseek-v3-technical-report]]
- [[sources/deepseek-v4-technical-report]]

## 待补充

- DeepSeek 报告中的 `MTP` 具体结构与损失加权方式。
- 它与 speculative decoding、blockwise decoding 的关系。
