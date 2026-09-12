# Research Wiki

这是一个本地优先、以 Markdown 维护的研究 wiki。`raw/` 保存原始资料，其余页面负责把原始资料整理成可复用的知识层。

## 分层

- `raw/`：不可修改的原始文档。
- `sources/`：对应原始资料的一手摘要页。
- `concepts/`：可复用的概念层，是当前 wiki 的核心。
- `models/`：模型类主题如何实例化这些概念；当前主要用于大模型领域。
- `entities/`：组织、产品、人物、数据集等实体。
- `notes/`：比较、问答产物、工作笔记。
- [[AGENTS]]：维护规范。

## 当前范围

当前 wiki 已从单一的大模型主题，扩展为可容纳多个研究方向的个人研究知识库。现有内容包括：

- 大模型：架构、模块、训练目标、优化器、数值精度、系统实现、推理与后训练。
- 2D Nesting：`2D irregular cutting and packing`、碰撞检测引擎、`2D irregular strip packing` 与开源启发式。

现有内容仍以少量来源为起点，因此部分页面会保留明显的来源簇视角；后续可继续增加新的研究方向与来源簇。

## 组织原则

- 默认先沉淀到 `concepts/`，再回填到具体实例页。
- 模型页主要回答“某个模型采用了哪些概念、做了哪些改动”；非模型领域则优先使用概念页、实体页与来源页。
- 来源页只记录可核验事实、原文摘要和待进一步抽取的点。
- 对尚未被原始资料充分支撑的细节，明确标为“待补充”或“待核验”。

## 从这里开始

- [index.md](./index.md)
- [log.md](./log.md)
- [[concepts/research-taxonomy]]
- [[concepts/llm-taxonomy]]
- [[concepts/2d-nesting-taxonomy]]
- [[concepts/transformer-block]]
- [[concepts/2d-irregular-cutting-and-packing]]
- [[entities/deepseek]]
