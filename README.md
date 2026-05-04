# LLM Wiki

这是一个本地优先、以 Markdown 维护的 LLM 知识 wiki。`raw/` 保存原始资料，其余页面负责把原始资料整理成可复用的知识层。

## 分层

- `raw/`：不可修改的原始文档。
- `sources/`：对应原始资料的一手摘要页。
- `concepts/`：可复用的概念层，是当前 wiki 的核心。
- `models/`：具体模型如何实例化这些概念。
- `entities/`：组织、产品、人物、数据集等实体。
- `notes/`：比较、问答产物、工作笔记。
- [[AGENTS]]：维护规范。

## 当前范围

当前主题是大模型知识本身，包括架构、模块、训练目标、优化器、数值精度、系统实现、推理与后训练。现有内容主要由两篇 DeepSeek 技术报告引入，因此部分页面仍带有明显的 DeepSeek 视角；后续需要继续补充更多来源。

## 组织原则

- 默认先沉淀到 `concepts/`，再回填到具体模型页。
- 模型页主要回答“某个模型采用了哪些概念、做了哪些改动”。
- 来源页只记录可核验事实、原文摘要和待进一步抽取的点。
- 对尚未被原始资料充分支撑的细节，明确标为“待补充”或“待核验”。

## 从这里开始

- [index.md](/Users/xiejh/code/playground/llm_wiki/index.md)
- [log.md](/Users/xiejh/code/playground/llm_wiki/log.md)
- [[concepts/llm-taxonomy]]
- [[concepts/transformer-block]]
- [[concepts/mixture-of-experts]]
- [[entities/deepseek]]
