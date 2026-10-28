# 协作规则

从 main 建 `research/<短名>`、`fix/<短名>` 或 `docs/<短名>`；Codex 自动工作分支使用 codex/ 前缀。每个 PR 单一目的，列出改动文件、研究影响、旧/新 hash、测试、审批需求和未决问题。禁止直接写 main 或覆盖历史结果；输出使用新 run_id。

修改材料、人口/网络、评分规则或 Primary 时必须单独 PR，由研究者明确批准；软件维护者的通过、CI 绿色或模型建议均不是研究批准。新批准追加 DECISION_LOG，注明批准人、日期、范围、材料 hash 和证据链接，不改写旧记录。不凭历史条件批准推定新逐字文本批准。

合并至少一位非作者代码审核；涉及研究方法需研究负责人另行审核。EJQ 评分 PR 还需测量负责人审核；不向普通协作者提供题库。主分支保护和 CODEOWNERS 的实际成员需研究者在 GitHub 配置，当前模板不声称已强制。

每个 PR 运行 README 的 test、analyze、report 和 `python tools/review_export.py`。CI 不配置 DeepSeek 或任何模型密钥；仅授予 contents:read。PR 测试只执行 scripted；禁止 pull_request_target 执行贡献者代码。

结果不得手工改成预期方向。历史共享数据变更必须说明新版本原因、源工件 hash 和新旧索引；报告须区分 REAL_LLM、SCRIPTED、REPLAY 和 FALLBACK。不存在真实结果写“尚未运行”。冲突时保留双方决策和结果，由研究者选择，不能用“最新文件获胜”解决协议冲突。

提交前检查 git diff --cached，确认无 .env、凭证、个人本机路径、受限全文和私有测量；新增文件先进入白名单审查。README 安装依赖可联网，实验测试不联网。实际 GitHub 权限、邀请与推送由研究者确认后操作。
