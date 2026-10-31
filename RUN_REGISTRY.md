> 2026-10-31更新：以下为已保存历史工件登记。当前24人实验的正式分支进度、模型和费用仍待原始日志审计，不能把本地未登记视为尚未运行。原六人Pilot待执行方案已SUPERSEDED；SCRIPTED/TEST_ONLY不得计入正式运行。详见 docs/Q5_CURRENT_RUN_AUDIT.md。本轮不改历史机器登记或任何结果。

# 运行登记

机器记录见 shared/RUN_REGISTRY.json，材料 hash 绑定实际六卡，代码按文件 hash 追溯，不能将本团队新提交当作旧运行 commit。

|run_id|类型|模型|seed|新增调用|状态|
|---|---|---|---|---|---|
|P1_FINAL_REVISION_seed20271001_RELEASE|SCRIPTED|None|20271001|0|SAVED_REFERENCE|
|DEEPSEEK_SINGLE_STUDENT_T1_V01|REAL_LLM_COMPONENT_DIAGNOSTIC|deepseek-flash|20271001|3|PASS_COMPONENT_ONLY|
|A001_OFFLINE_REPLAY|REPLAY|deepseek-flash (original responses)|20271001|0|PASS_SAVED_RESPONSES|
|SIX_AGENT_PILOT|REAL_LLM|None|20271001|None|尚未运行|
|FORMAL_THREE_SEEDS|REAL_LLM|None|[20271001, 20271002, 20271003]|None|尚未运行|
|DEEPSEEK_CONNECTION_PROBE|OFFLINE_PREFLIGHT|None|None|0|NO_GO_TOKEN_BOUND_AND_SEPARATE_APPROVAL_REQUIRED|
|DEEPSEEK_CONNECTION_PROBE_V02|OFFLINE_PREFLIGHT|None|None|0|AWAITING_LOCAL_CREDENTIAL_ENTRY|

A001 未向团队公开私有分数。scripted 四臂共576 panel，只有 seed20271001 同版本已保存；另两 seed 仅有输入。早期连接预检摘要为旧状态；随后已有首次真实连接账本。账本的 reservation 与 completion 是同一次请求，按实际账本计1次。真实记录合计4次：输入6086、输出615 token，估计 ¥0.017092，未核对平台账单。费用只统计本地已有可核证记录，未宣称覆盖未知外部运行。

每次新增 scripted 验证也应另记 run_id 与软件测试用途；本轮验收使用临时目录，收据见 docs/ACCEPTANCE.md。正式运行开始前填妥 templates/run_manifest.json，完成后封存 manifest、usage、材料/代码 hash 和状态，追加登记；失败和中止也保留。

|DEEPSEEK_FIRST_CONNECTION_LIVE|REAL_LLM_CONNECTION_DIAGNOSTIC|deepseek-flash|无|1|VALID_CONNECTION_ONLY|

A001 原始17项资产绑定另见 provenance/A001_ORIGINAL_ASSETS.json；团队搬机版本 hash 不代替原版本。

## 旧版本 scripted 运行

这些早期运行包含不同材料/实现版本与六人 scripted 子集，不与当前六卡结果或真实 Pilot 合并。完整逐文件 hash 见外部索引。没有保存的版本号/代码 commit 明确留空或 NOT_RECORDED。

|run_id|seed|人数|状态|材料版本|
|---|---|---|---|---|
|phase18-validation/B_FINAL_v03_FINAL_seed20271001|20271001|24|PASS_NATIVE_SCRIPTED_ONLY|1.8B-MAT-v0.3-CANDIDATE|
|phase18-validation/B_FINAL_v03_FINAL_seed20271002|20271002|24|PASS_NATIVE_SCRIPTED_ONLY|1.8B-MAT-v0.3-CANDIDATE|
|phase18-validation/B_FINAL_v03_FINAL_seed20271003|20271003|24|PASS_NATIVE_SCRIPTED_ONLY|1.8B-MAT-v0.3-CANDIDATE|
|phase18-validation/B_FINAL_v03_RELEASE_seed20271001|20271001|24|PASS_NATIVE_SCRIPTED_ONLY|1.8B-MAT-v0.3-CANDIDATE|
|phase18-validation/B_FINAL_v03_RELEASE_seed20271002|20271002|24|PASS_NATIVE_SCRIPTED_ONLY|1.8B-MAT-v0.3-CANDIDATE|
|phase18-validation/B_FINAL_v03_RELEASE_seed20271003|20271003|24|PASS_NATIVE_SCRIPTED_ONLY|1.8B-MAT-v0.3-CANDIDATE|
|phase18-validation/B_FINAL_v03_seed20271001|20271001|24|PASS_NATIVE_SCRIPTED_ONLY|1.8B-MAT-v0.3-CANDIDATE|
|phase18-validation/B_FINAL_v03_seed20271002|20271002|24|PASS_NATIVE_SCRIPTED_ONLY|1.8B-MAT-v0.3-CANDIDATE|
|phase18-validation/B_FINAL_v03_seed20271003|20271003|24|PASS_NATIVE_SCRIPTED_ONLY|1.8B-MAT-v0.3-CANDIDATE|
|phase18-validation/native_scripted_20271001|20271001|24|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|phase18-validation/native_scripted_20271001_r2|20271001|24|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|phase18-validation/native_scripted_20271001_r3|20271001|24|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|phase18-validation/native_scripted_20271002|20271002|24|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|phase18-validation/native_scripted_20271002_r2|20271002|24|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|phase18-validation/native_scripted_20271002_r3|20271002|24|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|phase18-validation/native_scripted_20271003|20271003|24|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|phase18-validation/native_scripted_20271003_r2|20271003|24|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|phase18-validation/native_scripted_20271003_r3|20271003|24|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|phase18-validation/native_scripted_pilot6|20271001|6|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|phase18-validation/native_scripted_pilot6_r2|20271001|6|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|phase18-validation/native_scripted_pilot6_r3|20271001|6|PASS_NATIVE_SCRIPTED_ONLY|NOT_RECORDED|
|p1-six-validation/P1_FINAL_REVISION_seed20271001_RELEASE|20271001|24|PASS_NATIVE_SCRIPTED_ONLY|P1-6CARD-v0.2-DRAFT-20261028|
