# 决策与批准记录

当前治理状态：Q1 APPROVE_WITH_CHANGES、Q2 APPROVE、Q4 SUPERSEDED、Q5 PENDING_CURRENT_RUN_AUDIT，详见 approvals/REVIEW_Q1_Q2_Q4_Q5_20261031.json。六卡正文批准仍有效。下表及先前记录保留其历史时点含义；当前24人实验状态不能由旧记录推定。

|记录|现有状态|证据/边界|
|---|---|---|
|Phase18 A1 Primary|CONDITIONALLY_APPROVED_A1|Study config/analysis_protocol_DRAFT.json；状态/分母修正仍需检查|
|B-01…B-08 方法修改|APPROVED_WITH_CHANGES_IMPLEMENTED|config/go_no_go_B_FINAL.json；材料逐字确认另行处理|
|三卡 1.8B-MAT-v0.3|旧活动版本，非六卡冻结|history/phase18；只作版本史|
|P1 六卡 v0.2|APPROVED，2026-10-31|approvals/P1_SIX_CARD_20261031.json；仅冻结六卡文字|
|A001 单时点诊断|PASS，限定组件用途|shared/a001/receipt.json；3 calls，P1未暴露|
|A001 离线重放|PASS，0新增调用|receipt offline_replay；source=replay|
|六人 Pilot|尚未运行/未授权|configs/pilot.json；原六人名单未改变|
|正式三 seed 真实研究|尚未运行/未授权|configs/formal.json|
|预算上界证明|DEFERRED_BY_RESEARCHER|receipt；不将费用估计称作上界|
|团队 GitHub 仓库与权限|待研究者确认方案|docs/GITHUB_SETUP.md；无远端操作|

当前待核验：最新题库与辅助分类、S1独立理解评价、24人实际运行身份/分支状态，以及当前模型、usage、费用、预算和重试策略。Q2及原六人Pilot不再列为待批准事项。

新增记录格式：decision_id、提出人、研究批准人、批准时间（时区）、scope、status、旧/新材料与协议 hash、PR链接、批准证据、是否授权真实运行。没有批准证据则保持 PENDING。

## 2026-10-29 · 团队仓库上传授权

研究者在本聊天明确要求将相关研究文件推送到 https://github.com/jzforever1640-wq/Socioverse。已核实目标为 Private 且具有推送权限；仅上传审查后的代码、材料、共享数据和文档。不包含私有题库、密钥、原始敏感日志或外部原始数据库；不修改成员或权限。此上传授权不等于材料、测量、Pilot 或正式运行的研究批准。

## 2026-10-29 · 题库共享授权

研究者在获知同仓库无法按文件夹隔离读取权限后，明确选择“直接放入当前私有仓库”。授权共享原32题四卷和答案键给所有仓库读取者。原始题库hash不变，审批文件见 provenance/EJQ_REPOSITORY_ACCESS.json；单人测量结果和原始请求日志仍不上传。不授予真实运行或测量修改批准。

## 2026-10-31 · MAT-P1-20261031-01

研究者明确表示“目前我觉得六卡已经可以审批通过 可以在GitHub上更新状态”。批准当前P101–P106原文，hash绑定见 approvals/P1_SIX_CARD_20261031.json；未修改字句。不扩大为EJQ修订、来源历史真实性、协议整体冻结或真实付费运行批准。最新方案统一入口为 docs/CURRENT_SIX_CARD_STUDY.md，当前未决事项为 docs/PENDING_REVIEW.md。

## 2026-10-31 · REVIEW-Q1-Q2-Q4-Q5-20261031

依据研究者本聊天明确决定：Q1为APPROVE_WITH_CHANGES，保留EJQ 0–16及原四维结构，辅助分类与最终题库未冻结，S1理解评价独立；Q2为APPROVE，正式仅E1–E4，无shock参照不增加，T0→T1仅描述；Q4为SUPERSEDED，取消原六人Pilot待审批执行方案，按当前24人实际配对执行；Q5为PENDING_CURRENT_RUN_AUDIT，19次/42元/零重试仅属历史Pilot A，当前参数须原日志核验。

本次只改治理状态和协议引用；未重启已完成臂、未干预正在运行或待恢复实验，未修改冻结输入、运行配置、主评分或已有结果，未新增付费调用或重试。历史文稿快照见 docs/history/approval_review/pre_Q_decisions_20261031/。只读审计缺口见 docs/Q5_CURRENT_RUN_AUDIT.md。
