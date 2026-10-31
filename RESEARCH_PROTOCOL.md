# 已确定的协议与冻结边界

当前完整六卡方案见 [CURRENT_SIX_CARD_STUDY.md](docs/CURRENT_SIX_CARD_STUDY.md)，待审核事项见 [PENDING_REVIEW.md](docs/PENDING_REVIEW.md)。本文件整理现有研究，不重新设计实验。权威原配置保存在 Study inputs/config、config 和 docs/history；方法批准、逐字材料批准、软件验收和真实调用授权分别记录。

|条件|公共 P1 支持|动态同伴反馈|
|---|---|---|
|E1|无|关|
|E2|无|开|
|E3|t2 六卡|关|
|E4|t2 六卡|开|

24 名合成考生，lower/middle/higher 各8，四专业 CS/AUTO/EE/STAT。原人口文件与三个 seed 网络不可重采样；每人四个有序邻居，动态信息只用前一步。配对 seed 为 20271001、20271002、20271003。t0/t1 共史只计算一次，t2 分支，子分支 replay 不算新模型调用；t5 idle。t1 S1 四卡，t2–t4 按四槽补 F；P1 仅 E3/E4 t2；N1 不活动。F 补位不是模型失败 fallback。

唯一 Primary 是 feedback OFF 下 t5 CS 意愿的 E3−E1 配对支持差：mean_i[(I_CS_E3_t5−I_CS_COMMON_t1)−(I_CS_E1_t5−I_CS_COMMON_t1)]。分析单位为整组配对 seed/网络，固定24；三 seed 描述均值与范围。SES 仅描述，不做 SES 因果或显著性声称。其他比较保持 secondary/exploratory；不能看输出改 Primary。测量 T0=0、T1=1、T2=2、T3=5；t3/t4 NOT_SCHEDULED，缺失不能填0。

私有只读 sidecar 测量不得进入行为 Action、AgentMemory 或后续同伴上下文；意愿与风险不传入 EJQ 请求；EJQ 请求无答案键。EJQ总分0–16与原四维评价结构、两层主评分保留（Q1 APPROVE_WITH_CHANGES）。辅助类别按最新题库重新核验直接应用、近迁移、独立迁移及数量运算，不预设任何题已具有独立迁移效度；S1理解评价独立于EJQ。最终题库及辅助分类尚未正式冻结。研究者已授权将原题库与答案键共享给当前私有仓库所有读取者；默认从仓库内加载并校验原hash。此访问授权不改变评分、行为隔离或真实运行审批。

P1六卡正文于2026-10-31获研究者批准，审批编号 MAT-P1-20261031-01，审批版本 P1-6CARD-v0.2-APPROVED-20261031。批准绑定原载荷及六卡内容hash，文本字节不改。源载荷版本ID保留以维护历史运行可比性；其旧pending字段为历史快照，当前审批以 approvals/P1_SIX_CARD_20261031.json 为准。analysis_protocol材料引用已同步当前六卡来源版本。

Q2已批准：正式研究仅保留E1–E4，不增加无shock参照组，不估计S1初始冲击独立因果效应；T0→T1仅描述性分析并明确因果限制。

Q4已被取代：原六人Pilot待执行审批方案取消，历史保留；以当前24人配对实验实际执行方案为准，不重启已完成分支，不影响正在运行或待恢复实验。scripted/TEST_ONLY结果不得计入正式实验。本仓库旧Pilot与运行配置仅为历史/原有配置，不能据此重启或推定当前在线参数。

Q5为PENDING_CURRENT_RUN_AUDIT：当前模型、提供方、实际调用数、输入输出token、费用、预算上限与重试策略须按当前原始日志只读审计。历史单人Pilot A的19次/42元/零重试不得套用当前24人运行。未经授权不得新增付费调用、修改预算或自动重试。

本轮仅更新审批状态、协议及必要引用，不修改冻结输入、运行配置、评分代码、已有结果或运行状态。最新待核验事项见 docs/PENDING_REVIEW.md。
