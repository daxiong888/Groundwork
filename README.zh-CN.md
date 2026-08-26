# Groundwork

[English](README.md) | 简体中文

Groundwork 是一个轻量的 Codex 插件，面向证据优先（evidence-first）的研发工作。它帮助 Codex 处理非平凡任务，同时避免把每个请求都变成繁重的流程。

当任务需要更清晰的需求、有边界的实现、验证证据、紧凑的交接、分发打包或项目 Wiki 维护时，可以使用它。小而明显、低风险的问题应保持直接处理。

目标读者：正在评估或安装 Groundwork 的 Codex 用户。
维护者文档：仓库维护、架构与证据规则请参见 [docs/maintainer-workflows.md](docs/maintainer-workflows.md)、[docs/plugin-architecture.md](docs/plugin-architecture.md) 和 [AGENTS.md](AGENTS.md)。

## 什么时候使用它

当正确性依赖于代码编辑之外的更多因素时，Groundwork 会很有用：

- 将粗略的意图整理成小型 PRD/规格；
- 将已接受的工作切分为有边界的任务；
- 判断工作已就绪、受阻，还是需要人工输入；
- 在明确的证据边界内规划或实现代码变更；
- 检查某个声明是否有源码、测试、运行时证据、文档或 UAT 的支持；
- 将已接受的就绪工作打包给其他运行时，但不声称该运行时已执行；
- 在会话之间保留紧凑的交接上下文；
- 维护一份有源码引用的项目 Wiki。

不要用 Groundwork 来回答简单问题、做明显的一行改动、替代人工审查、绕过 CI、用本地文档伪造发布证据，或自动化远程写操作。

## 技能

安装后的插件暴露十个公开技能：

| 技能 | 用途 |
| --- | --- |
| `to-prd` | 将粗略或模糊的意图整理成紧凑的 PRD/规格。 |
| `to-issues` | 将已接受的范围切分为纵向任务草稿。 |
| `triage` | 对就绪度、阻塞、严重度、状态或收尾进行分类。 |
| `write-plan` | 在改动之前为已接受的工作产出实现计划。 |
| `prototype` | 构建或评审一次性的 UI、逻辑、状态或契约原型。 |
| `implement` | 基于源码事实做聚焦的代码或文档改动。 |
| `verify` | 将声明映射到证据，报告已覆盖和缺失的证明。 |
| `handoff` | 为另一个会话或评审者保留紧凑的续作状态。 |
| `dispatch` | 为已接受的就绪任务产出仅打包（package-only）的运行时指令。 |
| `wiki` | 创建、查询、审计、更新或修复项目级 LLM Wiki 笔记。 |

## 包边界

Groundwork 分为一个小型已安装运行时包和一个更大的维护者仓库。

被打包的内容：

- `.codex-plugin/`
- `skills/`
- `hooks/hooks.json`
- `scripts/codex-hooks/`
- 由 `README.runtime.md` 生成的 `README.md`
- `LICENSE`

仅存在于源码仓库的内容：

- `AGENTS.md`
- `docs/`
- `tests/`
- `artifacts/`
- `research/`
- `scripts/codex-hooks/` 之外的维护者脚本
- 本地状态，如 `.git/`、`.codegraph/`、`.groundwork/`、`.trellis/`、`dist/` 和 `refer/`

内置的路由可观测性 hook 默认处于休眠状态。除非项目显式启用，或受控流程强制启用，否则它们什么都不做。Hook 候选信号、历史记录、文档和普通源码/包检查是改进证据；它们本身并不能证明运行时行为、缓存刷新、发布就绪、UAT 就绪、客户就绪、市场就绪或 hook 可信度。

## 本地安装

Groundwork 目前面向通过生成的 Codex marketplace 进行本地个人安装。不要把 Codex 直接指向这个开发检出的仓库，也不要指向它的符号链接。

在本地检出中执行：

```bash
python3 scripts/build_local_marketplace.py
codex plugin marketplace add ./dist/groundwork-local-marketplace
codex plugin add groundwork@groundwork
```

对于克隆在 Codex 插件目录下的未发布检出：

```bash
git clone https://github.com/daxiong888/Groundwork.git ~/.codex/plugins/groundwork
cd ~/.codex/plugins/groundwork
python3 scripts/build_local_marketplace.py --output ~/.codex/plugins/groundwork-local-marketplace
codex plugin marketplace add ~/.codex/plugins/groundwork-local-marketplace
codex plugin add groundwork@groundwork
```

如果 Codex 已经打开，安装后请重启应用或刷新插件列表。

构建器只会替换带有其 `.groundwork-marketplace-output` 标记的输出目录。它会拒绝没有标记的输出目录，包括由旧版本构建的 marketplace。请自行检查并删除标记出现之前的输出目录，或选择一个新的 `--output` 路径；构建器不会自行推断归属并自动删除。

## 本地更新

在本地检出中执行：

```bash
cd ~/.codex/plugins/groundwork
git pull --ff-only
python3 scripts/build_local_marketplace.py --output ~/.codex/plugins/groundwork-local-marketplace
codex plugin add groundwork@groundwork
```

如果本地 marketplace 曾直接指向工作检出目录，请用 `scripts/build_local_marketplace.py` 重新构建，重新添加生成的 marketplace 路径，并重新安装。一个健康的已安装缓存应只包含运行时包，不应包含仅属于源码仓库的 docs、tests、artifacts、维护者历史或本地临时状态。

## 隐私

Groundwork 是本地优先的。它没有服务后端、分析端点、账号系统或遥测收集。内置的技能和脚本只操作本地文件和用户批准的 Codex 工具行为。网络访问、远程追踪器变更、部署、迁移、破坏性操作、数据写入、提交、推送和拉取请求仍需要用户的明确意图以及相应的证据门控。

## 下一步

- 我想使用它：阅读 [README.runtime.md](README.runtime.md) 了解已安装包的契约，然后从生成的 marketplace 安装。
- 我想了解工作流：阅读 [docs/maintainer-workflows.md](docs/maintainer-workflows.md)。
- 我想维护或评审它：阅读 [AGENTS.md](AGENTS.md) 和 [docs/plugin-architecture.md](docs/plugin-architecture.md)。
- 我想看证据细节：阅读 [docs/release-evidence-claim-boundary.md](docs/release-evidence-claim-boundary.md)。
- 我想看版本历史：阅读 [CHANGELOG.md](CHANGELOG.md)。
