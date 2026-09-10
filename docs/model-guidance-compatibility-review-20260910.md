# 模型指导兼容性审查（2026-09-10）

Target Reader: Groundwork 维护者与本轮独立评审者。
Reader Action Needed: 核对四项具体冲突的最小修正及保留边界。
Decision Supported: 这些源码规则是否对齐授权延续、拓扑推断与按决策加载的条件。
Artifact Type: 源码规则审查记录。
Source of Truth: 当次打开的 OpenAI/Anthropic 官方资料、当前 skill 文本、用户授权范围与本地检查结果。
Scope: implement、verify 及直接相关 git/生命周期审批条件；只读检查 to-prd、triage。
Out of Scope: PRD 设计、telemetry、路由分类器、提交推送、插件安装、真实模型试验与生产操作。
Evidence Level: 静态合同与生成包验证；模型执行效果、安装缓存、runtime、release、UAT 均 unverified。
Safe to Share / Redaction Notes: 可分享；不含凭据、个人数据或私有运行日志。

## 官方事实与使用边界

以下页面均在 2026-09-10 实际打开核实；它们是本轮外部依据，Groundwork skills 是被审对象，不作为本轮评审框架或试验准入协议。

| 来源 | 官方事实 | 本轮推论及限制 |
| --- | --- | --- |
| [OpenAI Model guidance — Astra](https://developers.openai.com/api/docs/guides/latest-model) | 提醒含糊或冲突的 skill 指导可能导致过早暂停；建议明确用户指令优先、沿用已给授权，并先完成已授权的可审准备。 | 核对入口与引用是否冲突；不据此认定所有旧机制失效，也不取消宿主权限与用户指定审批。 |
| [OpenAI Harness engineering](https://openai.com/index/harness-engineering/) | 使用简短入口指向按需知识，以机械检查维护边界和一致性。 | 缩小无关引用触发条件；该文章的自主提交/合并实践不构成本项目授权。 |
| [Anthropic Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 追求最小充分上下文与按需检索，同时指出最小不等于一律简短。 | 保留真正影响当前判断的证据合同；不能仅凭篇幅删掉澄清或验证规则。 |
| [Anthropic Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) | 记录随模型能力变化逐项移除 context resets、sprint 结构，并保留仍有价值的 planner/evaluator。 | 逐项寻找具体冲突及反例；该实验不证明 Groundwork 多轮评审或任何其他机制已无用。 |

## 已修正的具体冲突

| 项目与被审源码 | 改前行为约束 | 改后行为约束 | 依据、推论与验证边界 |
| --- | --- | --- | --- |
| MG-01：`skills/implement/SKILL.md`、`skills/implement/IMPLEMENT-BRANCHES.md`、`skills/verify/SKILL.md`、`skills/_shared/GIT-BOUNDARY.md`、`skills/_shared/GIT-TOPOLOGY-GATE.md`、`skills/_shared/LIFECYCLE-PREFLIGHT.md` | implement 入口仅在实际需批准时输出门禁；分支及生命周期 Risk Gate 按类别前置审批展示，verify 也按 paired action 无条件输出审批门，没有清楚扣除已有授权。 | 明确用户指令相对 skill 指导的优先级及更高优先级/宿主权限边界。已明确的任务无需另补 PRD 或 bypass 口令；核对动作、目标、范围、风险，沿用充分授权，先完成已授权本地准备，只拦缺授权或证据的具体动作。 | OpenAI 官方事实支持消歧。可检查的是各入口/引用的条件一致性；减少模型实际停工是尚未验证的预期。 |
| MG-02：`skills/_shared/GIT-TOPOLOGY-GATE.md` 及 implement 引用 | 修改共享项目文件或需要可审交付就被视为 PR-bound；无关脏文件直接要求 worktree 或 blocked。用户明确要求当前目录时没有例外。 | PR-bound 由用户/已接受任务/适用项目规则的实际 PR 要求确定。用户明确拓扑优先于 skill 默认；检查差异、保护无关修改，可安全分离则原地编辑，实际冲突只阻止受影响写入。 | OpenAI 的指令优先与授权延续；由源码推断旧默认可能覆盖用户要求。保留 PR 明确要求、脏文件保护、危险 git 与外部状态写入门禁；原地修改不产生提交/推送授权。 |
| MG-03：`skills/verify/VERIFY-ROUTER-BRANCHES.md` | 仅 source-truth 或 UAT/release 主题就触发生命周期预检，继而载入状态机、产物和拓扑规则；与入口的按 claim 最小证据范围冲突。 | 只有判断依赖恢复、生命周期/任务状态转移（含 closeout）或下游产物提升时才加载预检；仅拓扑动作直接读取拓扑详约，普通来源核验走匹配的证据分支。 | OpenAI 与 Anthropic 的按需上下文指导。静态检查能证明触发条件收窄；不能证明实际 token 降幅或运行效果。 |
| MG-04：`skills/implement/IMPLEMENT-BRANCHES.md`、`skills/_shared/LIFECYCLE-PREFLIGHT.md` | 实现分支仍因可能写文件而加载预检；预检触发段、拓扑字段和 implement 模式又泛化为 implementation/shared-file/before-writes，未贯通入口已有的按需规则。 | 普通单次修复保留本地源码、git/diff、脏文件保护、轻量计划和聚焦检查；普通来源缺口先查源或作实质澄清。生命周期详约只在恢复、状态转移或下游产物提升影响下一决策时加载，并在该范围解决流程/来源/宿主冲突；拓扑、证据和状态机分别按对应决策/主张加载。 | 属于原有条件加载遗漏，不是新增强制流程回归。预检本来即为 transient、不默认写 STATE。源码检查确认触发条件及引用关系，未观察或证明实际模型停工。 |

## 正例与反例

下列为人工核对的预期合同边界，不是模型执行结果，也不是路由分类器的新规则。

| 情景 | 应有行为 | 仍需保留的边界 |
| --- | --- | --- |
| 用户明确“在当前目录修已复现问题并跑相关检查，不切分支、不提交” | 保留源码/git/diff/轻量计划/聚焦检查后执行已授权修复；不因写源码或运行本地测试加载完整生命周期详约。 | 不提交、推送或创建 worktree；不能覆盖其他任务的修改，也不默认写 STATE。 |
| 工作区另有无关文档修改，但本任务文件不重叠 | 检查差异，保持当前目录，精确编辑本任务文件。 | 若同一文件/范围确有不可安全分离的冲突，暂停受影响写入并说明。 |
| 未指定拓扑，当前为 main，明确要求 PR，且存在可安全分离的无关脏文件 | 先满足 PR 分支/worktree 要求，再考虑是否可保留无关修改。 | 脏文件可分离不覆盖前面的 PR 拓扑条件；不据此在 main 实施 PR 交付。 |
| 用户要求“只评审，修改前先让我确认” | 完成只读评审，到写入前遵守用户指定暂停点。 | 本轮优化不能把只读授权升级成修复授权。 |
| 用户已批准目标分支推送，要求先验证后推送 | 完成验证；若目标、范围、风险未变且权限允许，沿用该授权。 | 验证失败、用户另设 checkpoint、目标改变或宿主仍需许可时不越过。 |
| 修复发现必须迁移数据或扩大到未授权共享组件 | 继续不依赖该决策的安全检查，说明具体扩展和影响。 | 不从“修 bug”推导迁移、破坏性动作或外部状态写入授权。 |
| 用户新增明确的本地修正范围 | 将新指令作为新的范围依据继续检查/修正。 | 新增内容仍有实质业务歧义、风险或权限缺口时只澄清这些缺口。 |
| 只有“改善审批流程”，关键角色与状态转换不明 | 使用可得来源定位问题，提出影响下一步的澄清。 | 不伪造产品事实，也不把模糊意图视为完整实施契约。 |
| “只看这份 PRD 和测试摘要，结论有证据吗？” | 检查命名材料，给 claim、covered、missing 与有限结论；不因 source-truth 字样加载生命周期流程。 | 摘要或源码不能证明当前 runtime、UAT 或 release 已通过。 |
| “依据已完成验证，判断 task 是否能 closeout” | 加载与真实状态转移相关的来源和生命周期检查。 | 判断可关闭不等于已授权关闭远端 issue。 |
| “继续已有 STATE 中暂停的工作，并推进当前阶段” | 核对当前来源与恢复状态，加载对应生命周期/状态转移详约。 | 普通修复的轻量路径不豁免实际恢复检查。 |
| “先准备补丁和相关检查，部署前等我确认” | 完成已授权本地准备，到部署处遵守 checkpoint；按具体动作加载门禁。 | 未来部署要求不提前阻断所有本地修复，也不产生部署授权。 |
| 已授权在现有 feature 分支验证后创建 PR，没有恢复或状态转移需求 | verify 直接按需读取拓扑详约和动作门禁，不因单独 topology 检查加载完整生命周期预检。 | 既有授权必须覆盖目标、范围、风险；未知权限或用户 checkpoint 仍须处理。 |
| 普通修复只报告本地测试结果及 runtime 未验证 | 保留 source/check 证据边界，不因提到 runtime/release 的未验证状态就加载整套生命周期流程。 | 真正要主张 runtime/cache/release/UAT 或独立评审通过时，仍需对应证据详约。 |

## 检查后保留的规则

- `to-prd/SKILL.md` 已区分紧凑会话与持久输出，默认不加载大模板；只在缺失信息会实质改变 spec 时停在澄清。完整持久文档的内容检查也允许准确标注剩余未知。本轮未确认需要修改的具体冲突。
- `triage/SKILL.md` 已限定只有实际需要批准时才展示审批字段，agent brief/Goal Contract 绑定可执行任务分类；本轮没有把普通分类要求扩写为实施门槛。
- implement 的内部 mini-plan、根因充分性、verify 的 claim/covered/missing、证据真实性及独立评审边界有明确用途。没有模型行为证据证明应整体删除，故保留。

## 本地验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_model_guidance_compatibility tests.test_pipeline_ownership tests.test_review_contract`：25 tests，OK；其中本任务 11 个静态合同测试。
- `python3 scripts/check_runtime_package_boundary.py`：本次补修后重新运行，通过。当前生成包为 114 files / 9858 lines；hook 为 4 files / 1315 lines；skill 为 105 files / 8395 lines；public entry reference depth 为 19。
- `python3 -m json.tool .codex-plugin/plugin.json >/dev/null`：通过。
- `git diff --check`：通过。
- 最终 fresh-context 只读复核：无剩余阻塞性源码合同发现；reviewer 独立重跑上述 25 项测试及 `git diff --check` 均通过，未独立重跑包检查或模型行为验证。

`scripts/runtime_package_manifest.json` 的预算维护归 telemetry 任务与父任务协调；本轮 telemetry 将 hook 行数上限调整为 1320，包总行数上限为 9900，skill 行数上限仍为 8400。本任务未修改预算或包形状，未刷新安装缓存。

专用测试检查入口与引用的授权条件、PR 推断、脏文件保护及按需加载边界。MG-04 的新增回归跨 implement/verify 调用方、预检触发段、拓扑字段、模式规则和状态机引用检查条件绑定，防止单独 topology/写文件重新成为生命周期触发，并检查本地验证、恢复、checkpoint 与实质证据主张要求仍存在；原宽触发无法通过这些检查。它们不是全文语义证明，不执行 prompt，也不包含本地 case-to-route 模拟器，不能据此证明模型实际少加载或少停工。包检查覆盖当次共用目录的生成包，不能把其他并行改动归为本任务贡献。

真实模型试验、安装/缓存刷新、runtime、release 与 UAT 验证未运行：本任务明确不授权这些动作。后续若要主张实际减少重复审批或停工，仍需单独授权、覆盖上述正反例的运行验证。
