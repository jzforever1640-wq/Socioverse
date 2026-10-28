# 已确定的协议与冻结边界

本文件整理现有研究，不重新设计实验。权威原配置保存在 Study inputs/config、config 和 docs/history；方法批准、逐字材料批准、软件验收和真实调用授权分别记录。

|条件|公共 P1 支持|动态同伴反馈|
|---|---|---|
|E1|无|关|
|E2|无|开|
|E3|t2 六卡|关|
|E4|t2 六卡|开|

24 名合成考生，lower/middle/higher 各8，四专业 CS/AUTO/EE/STAT。原人口文件与三个 seed 网络不可重采样；每人四个有序邻居，动态信息只用前一步。配对 seed 为 20271001、20271002、20271003。t0/t1 共史只计算一次，t2 分支，子分支 replay 不算新模型调用；t5 idle。t1 S1 四卡，t2–t4 按四槽补 F；P1 仅 E3/E4 t2；N1 不活动。F 补位不是模型失败 fallback。

唯一 Primary 是 feedback OFF 下 t5 CS 意愿的 E3−E1 配对支持差：mean_i[(I_CS_E3_t5−I_CS_COMMON_t1)−(I_CS_E1_t5−I_CS_COMMON_t1)]。分析单位为整组配对 seed/网络，固定24；三 seed 描述均值与范围。SES 仅描述，不做 SES 因果或显著性声称。其他比较保持 secondary/exploratory；不能看输出改 Primary。测量 T0=0、T1=1、T2=2、T3=5；t3/t4 NOT_SCHEDULED，缺失不能填0。

私有只读 sidecar 测量不得进入行为 Action、AgentMemory 或后续同伴上下文；意愿与风险不传入 EJQ 请求；EJQ 请求无答案键。两层原评分保留，辅助维度仍 proposed。题库由测量负责人保管；仓库外加载。

当前材料 P1-6CARD-v0.2-DRAFT-20261028 是六卡候选，不是冻结版本。旧 analysis_protocol_DRAFT.json 内 materials_version 仍写三卡版本；此不一致保留为历史元数据，不覆盖它，运行须以 active_materials 与实际资产 hash 明确绑定六卡。所有源文本截止规则 2026-10-24 23:59 UTC+8，事后取回不能证明历史字节。

正式运行仍待材料逐字批准、测量与完整运行器验收、无 shock 参照决定、指定模型/预算与授权。12288/1000 已不能覆盖已知合法压力案例；40960/8192 只是提案，不自动采用。模型别名并非不可变快照。A001 组件成功不能代替六人 Pilot、四臂或正式批准。
