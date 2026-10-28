# 决策与批准记录

以下均为现有工件整理，不新增研究者批准。原证据见 docs/history；未记录具名签署的地方不补造姓名或日期。

|记录|现有状态|证据/边界|
|---|---|---|
|Phase18 A1 Primary|CONDITIONALLY_APPROVED_A1|Study config/analysis_protocol_DRAFT.json；状态/分母修正仍需检查|
|B-01…B-08 方法修改|APPROVED_WITH_CHANGES_IMPLEMENTED|config/go_no_go_B_FINAL.json；材料逐字确认另行处理|
|三卡 1.8B-MAT-v0.3|旧活动版本，非六卡冻结|history/phase18；只作版本史|
|P1 六卡 v0.2|PENDING_RESEARCHER_APPROVAL|active_materials.json；frozen=false|
|A001 单时点诊断|PASS，限定组件用途|shared/a001/receipt.json；3 calls，P1未暴露|
|A001 离线重放|PASS，0新增调用|receipt offline_replay；source=replay|
|六人 Pilot|尚未运行/未授权|configs/pilot.json；原六人名单未改变|
|正式三 seed 真实研究|尚未运行/未授权|configs/formal.json|
|预算上界证明|DEFERRED_BY_RESEARCHER|receipt；不将费用估计称作上界|
|团队 GitHub 仓库与权限|待研究者确认方案|docs/GITHUB_SETUP.md；无远端操作|

未决：六卡逐字批准与来源历史核验；EJQ 修订/测量适用性决定；旧三卡分析元数据；完整 live 分支与私有隔离验收；正式 no-shock 参照决定；模型/分词器/上下文/总调用预算确认；指定审核人员和受限数据访问组。

新增记录格式：decision_id、提出人、研究批准人、批准时间（时区）、scope、status、旧/新材料与协议 hash、PR链接、批准证据、是否授权真实运行。没有批准证据则保持 PENDING。

## 2026-10-29 · 团队仓库上传授权

研究者在本聊天明确要求将相关研究文件推送到 https://github.com/jzforever1640-wq/Socioverse。已核实目标为 Private 且具有推送权限；仅上传审查后的代码、材料、共享数据和文档。不包含私有题库、密钥、原始敏感日志或外部原始数据库；不修改成员或权限。此上传授权不等于材料、测量、Pilot 或正式运行的研究批准。

## 2026-10-29 · 题库共享授权

研究者在获知同仓库无法按文件夹隔离读取权限后，明确选择“直接放入当前私有仓库”。授权共享原32题四卷和答案键给所有仓库读取者。原始题库hash不变，审批文件见 provenance/EJQ_REPOSITORY_ACCESS.json；单人测量结果和原始请求日志仍不上传。不授予真实运行或测量修改批准。
