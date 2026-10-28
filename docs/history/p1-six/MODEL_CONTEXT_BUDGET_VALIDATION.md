# 模型上下文与预算终审

研究者本轮明确答复“未选模型”。`model`、`provider`、`exact_model_version`、价格及硬预算均仍为null；real_llm_enabled、paid_authorized、token_counter_verified均false。没有拿当前聊天所用模型当实验模型，也没有读取或输出密钥。

## 实际实现与未验收项

本地封装使用OpenAI SDK兼容的Chat Completions接口，代码默认base_url指向OpenAI `/v1`、可由环境配置覆盖；真实提供方/实际base_url未选择，也未读取环境凭据。调用是`chat.completions.create`、单条user JSON消息、response_format=json_object、temperature=0、max_tokens=预算输出上限。该封装不是已验证支持任何模型的声明。

SocioVerse运行环境当前未安装openai与tiktoken；本地计数借用系统Python已有tiktoken0.13.0和已缓存分词表，无环境安装/无模型请求。选定模型后须配置运行依赖与准确分词器、API兼容性、上下文窗口和输出/推理预算；这些项目目前无法验收。官方文档说明消息边界等也消耗token，输出限额可能包含不可见token；本地编码文本数不等于真实API账单。当前max_tokens还需按最终模型检查，不能先断言兼容推理模型。

官方说明：[token counting](https://developers.openai.com/api/docs/guides/token-counting)、[Chat Completions参数](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create)。本轮只读文档，未调用计数或生成API。

## 计数口径

o200k_base与cl100k_base为两种本地编码。下列数值对指定编码/字符串精确，但相对于未选模型均属预算估计。完整请求按实际user JSON文本分词，加原GuardedChannel的128保守代理开销；另存HTTP正文序列化计数，不能把外层JSON再重复收费。128不是已验证的服务方真实开销。

单卡完整显示：

|卡|字符|o200k文本token|cl100k文本token|
|---|---:|---:|---:|
|PUB:P101|368|238|341|
|PUB:P102|382|268|430|
|PUB:P103|427|266|437|
|PUB:P104|412|266|442|
|PUB:P105|395|271|425|
|PUB:P106|405|269|426|

六卡总字符2389；逐卡文本token相加o200k 1578、cl100k 2501。这些合计不含Persona、source_refs、JSON字段与历史，不能作为请求预算。

## 实际渲染与合法上限压力

实际短scripted渲染312条行为＋480条私有请求；私有请求经真正evaluate封装、含其response_format说明捕获，避免只算sidecar半成品。另对24名Persona、三SES、四臂、t1–t5执行1920条原生Provider最大长度输入检查，覆盖t2六卡、t3/t4累计历史及t5私有评测。

- ordinary_CJK：判断400、理由400、同伴正文180、后台解释400字符，合法且去重的全部可见来源/父帖；完整历史保留。
- byte_heavy_unicode：用合法四字节字符做同样检查，测试编码最坏风险；不是有意义的舆论、更不是预测模型会这样输出。
- 两组都使用原始24人固定画像，非无限扩展Persona；输入长度按每SES/Persona/时点保存，见audit/MODEL_BUDGET_FINAL.json。

|案例|请求种类|记录数|o200k+128范围|cl100k+128范围|
|---|---|---:|---|---|
|ACTUAL_SHORT_SCRIPTED|behavior|312|1743–5200|2230–7124|
|ACTUAL_SHORT_SCRIPTED|intention|240|1512–5500|1852–7501|
|ACTUAL_SHORT_SCRIPTED|EJQ|240|2265–6253|2870–8519|
|byte_heavy_unicode|behavior|384|1743–24525|2230–25989|
|byte_heavy_unicode|intention|288|5210–27993|5751–29511|
|byte_heavy_unicode|EJQ|288|5965–28746|6775–30529|
|ordinary_CJK|behavior|384|1743–8565|2230–12309|
|ordinary_CJK|intention|288|2410–9233|3351–13431|
|ordinary_CJK|EJQ|288|3165–9986|4375–14449|

结论：**12288对短脚本轨迹足够，但对当前规则允许的长输入不保证足够。** ordinary_CJK的行为cl100k最高12309、私有意愿13431、私有EJQ14449；高字节测试最高30529。不能把上轮短轨迹成功升级为普遍预算通过。

P1在t2完整六张固定排序；t3/t4各保留历史一份，不静默裁剪，不重复系统新增。动态正文180上限未变。此前未限制重复引用和added_interpretation，候选已改为来源/父帖去重、后台解释≤400；否则无法给这类字段有限输出包络。判断/理由原400保留。

## 输出空间单独验收

|合法结构示例|o200k内容token|cl100k内容token|
|---|---:|---:|
|byte_heavy_unicode / behavior|6078|6076|
|byte_heavy_unicode / intention|1673|1673|
|ordinary_CJK / behavior|1248|1936|
|ordinary_CJK / intention|273|473|
|private_EJQ_exactshape / EJQ|180|180|

1000输出token不能容纳所有合法行为JSON，普通最大字段示例已约1248/1936，高字节约6078；完整EJQ八题最小规定结构约180，但真实服务开销/推理仍未知。私有意愿原解释字段无明确长度上限、first_choices可重复，本候选限定解释≤400、首选专业不重复，只约束格式，不改量表题干/分值；400字高字节解释示例约1673。

真实调用封装已增加finish_reason检查：即使JSON可解析，length或其他非stop结束也记录并停止，不把截断输出当有效测量。fake测试验证此门槛；未宣称SDK/API已实连。输入超限在发请求前拒绝，不自动截断文本；输出截断后不接受部分值。

## 待批准调整

优先保留全部获准历史和完整材料，提议通用输入40960、输出8192。两种编码的本轮有限压力模式落在该范围内；合计至少49152上下文空间，仍须加真实模型接口/非可见token余量，不能仅凭模型宣称窗口刚好49152就放行。

提案独立保存在config/context_budget_proposal_FINAL.json；当前pilot仍12288/1000并明确标为压力未通过，没有默许将新预算用于真实调用。40960/8192不是所有Unicode内容或未来更长轮次的数学保证；选定模型后必须准确计数并fail closed。若选定模型仍不够，另批历史管理或更大窗口，不能删关键限制/压缩P1、悄悄丢轮次、把旧历史重新摘要后视作原实验。

6人E1/E3原定基础调用仍114（42行为/72私有），重试最多12时126；新分项在后台算，不增加模型调用。若所有126次均按提案最大额度预留，输入上界5160960、输出1032192 token（预算预留，非预计实际使用）。价格/硬预算未知，美元数为null。原拟5美元不是已批准金额，输出空间扩大后必须重算成本。实际本轮模型调用和费用均0。
