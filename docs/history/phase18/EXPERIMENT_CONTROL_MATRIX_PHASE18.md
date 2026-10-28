# EXPERIMENT_MATRIX_UPDATED

版本：`1.8B-MAT-v0.3-CANDIDATE`；日期：2026-10-28（Asia/Shanghai）。

| 时点 | E1 无额外支持/无动态 | E2 无额外支持/有动态 | E3 有额外支持/无动态 | E4 有额外支持/有动态 |
|---|---|---|---|---|
| t0 | 共同情境、四专业卡、私人T0 | 共同前缀 | 共同前缀 | 共同前缀 |
| t1 | S1四卡、共同判断/可选帖、私人T1 | 同一已实现历史原生重放 | 同左 | 同左 |
| t2 | F201–204 | 上轮邻居帖/对应F补位 | F201–204，后接P101–103 | 上轮邻居帖/对应F补位，后接P101–103 |
| t3 | F301–304 | 上轮邻居帖/对应F补位 | F301–304 | 上轮邻居帖/对应F补位 |
| t4 | F401–404 | 上轮邻居帖/对应F补位 | F401–404 | 上轮邻居帖/对应F补位 |
| t5 | 无新增信息/行为，只读私人T3 | 同左 | 同左 | 同左 |

无N1、无新中性补齐卡、无空支持槽供Agent阅读。E1/E2的“NO_ADDITIONAL_INTERVENTION_MATERIAL”只写后台暴露日志，属于合法处理分配，不是测量缺失。每人E1/E2共16个新增feed位置，E3/E4为19；固定卡220上限、动态body180，超长拒收不裁剪。OFF仍有完整十二F，不能称无信息。

## 估计对象

唯一Primary保持t5 CS独立意愿E3−E1，同一seed/身份配对；共享T1相减抵消。

The total effect of providing an additional public information support package versus providing no additional support, under the same static social-information environment, within the simulated system.

中文：相同静态社会信息环境中，额外提供公共支持包相对于不额外支持，对模拟考生CS报考意愿的整体条件差异。额外信息量、文字量、机构权威和认知活动均在信息包中，不能由该对比分解，不宣称排除了注意或额外阅读影响。

E4−E2为动态制度下支持分配的条件差异，E2−E1为动态反馈制度整体差异；(E4−E2)−(E3−E1)为模型内交互，不是事实扭曲的因果中介。动态替换改变信息构成，不是相同固定文本多传几次。固定24人、各seed完整网络轨迹为重复运行单位，SES仅描述；Mock或人工oracle结果只验证软件，不能报告为干预效果。

## 共同历史与五类记录

每个seed t1仅24次新行为请求，子分支重放24个保存行动，无再次请求；重放生成的状态和待投递队列与共同历史一致。子分支t1暴露行标记replay_rehydration，不累计为新的系统广播。t2以后环境/队列独立。

暴露entries分别记录S/F/P系统投放、同伴实际投递、动态替换的F ID、静态补位及原因；请求审计逐次记录历史实例进入完整请求的次数、字符和字节；语义转述是否保留原主张仍需人工编码，不能仅由source_ref存在自动判对。token_count为空并标MODEL_NOT_SELECTED_COUNTER_NOT_VERIFIED，不用字符数冒充token。
