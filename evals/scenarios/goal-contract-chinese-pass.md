# Goal Contract Chinese Label Pass Fixture

Target Reader: Goal Contract linter maintainers and Groundwork reviewers.
Reader Action Needed: Use this fixture to confirm Chinese field labels are accepted while code identifiers remain literal.
Decision Supported: Whether `scripts/lint_goal_contract.py` supports Chinese labels and Chinese content without translating `/goal`, runtime IDs, paths, or result package names.
Scope: Positive linter fixture for Chinese labels only.
Out of Scope: Runtime execution, dispatch package generation, and product acceptance.
Evidence Level: Derived from `docs/prd-dispatch-runtime-router.md` FR-7 and FR-8.

## 目标合同

- 目标命令: /goal 为 Groundwork 增加 Goal Contract 规范与最小 lint 工具。
- 结果: 产出一个共享规范和一个可复用的轻量检查脚本。
- 事实源: `docs/prd-dispatch-runtime-router.md` 与 `artifacts/dispatch-runtime-router/issue-map.md`。
- 验收标准映射: FR-7 对应共享规范，FR-8 对应 lint 脚本，AC-9/AC-10 对应可执行任务边界和不发明产品事实。
- 验证: 运行命令 `python3 scripts/lint_goal_contract.py evals/scenarios/goal-contract-chinese-pass.md`。
- 约束: 只修改 Goal Contract 相关文档、脚本和验证 fixture，不提交、不推送、不改远端。
- 边界: 不修改 `skills/to-issues/`、`skills/triage/`、dispatch 行为、依赖文件或运行时目录。
- 迭代策略: 先做一次聚焦实现；如果本变更导致验证失败，只做一次窄修复并重跑相关检查。
- 完成条件: 中文标签 fixture 输出 `Goal Contract Lint: pass`，负向 fixture 输出 `Goal Contract Lint: fail`。
- 暂停条件: 文件位置与仓库约定冲突、需要安装依赖、需要远端写入或验收来源不清。
- 非目标: 不实现 dispatch，不修改 runtime adapter，不创建任务数据库。
- 风险/门禁: lint 只做轻量全文扫描，不做结构化 Markdown 解析。
- 首选运行时: codex_app_managed_worktree_thread
- 预期结果包: review_package
