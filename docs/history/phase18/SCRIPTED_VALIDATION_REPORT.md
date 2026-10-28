# SCRIPTED_VALIDATION_REPORT

版本：`1.8B-MAT-v0.3-CANDIDATE`；日期：2026-10-28（Asia/Shanghai）。

## 原生端到端结果

三个原有paired seed20271001/20271002/20271003，固定24人×E1–E4，全部通过。每组144条panel（t0–t5），每seed576，合计1728；每组独立实际DuckDB保存，非只有JSON。官方四接口、builder、loop、store、branch replay均实际执行，Core代码未改。

每seed新t1行为24次；子分支重放t1，各24行action_source=replay，inherited_decision_calls=0。行为完整渲染312份/seed，共936；v1私有渲染480份/seed，共1440。所有完整内容扫过条件ID/kind/组别/答案键等泄漏，真实调用路径使用同一渲染函数；本轮没有向真实模型发送。

| seed | 人数/组 | 每组panel | 前缀与分支不变量 | 真实LLM调用 |
|---|---|---|---|---|
| 20271001 | 24/4 | 144 | PASS | 0 |
| 20271002 | 24/4 | 144 | PASS | 0 |
| 20271003 | 24/4 | 144 | PASS | 0 |

## 实际暴露计数（各seed相同；每组24人）

下表S1在子分支是重放视图的记录数，不能把四组S1相加当384次新共同投放；全局COMMON只新增96人卡。

| 分支 | S1视图记录 | F实际投放 | P1新增 | 同伴投递 | 动态替换/静态补位 |
|---|---:|---:|---:|---:|---|
| E1 | 96 | 288 | 0 | 0 | 0/288 |
| E2 | 96 | 0 | 0 | 288 | 288/0 |
| E3 | 96 | 288 | 72 | 0 | 0/288 |
| E4 | 96 | 0 | 72 | 288 | 288/0 |

ON组本地脚本每位每轮都发合法占位帖，因此十二槽全被替换；这不是对真实Agent发帖率的预测。E4 t2脚本故意引用P101以检查t3来源链，不能当真实公共信息采用率。OFF保留帖子研究日志但无邻居投递；t5无新增feed/行为。超长181字符保持原值归档并拒收，下一轮用预定F补位，不截断；同轮、跨组/来源提前可见等拒收均测试。

## 完整测试和首次失败

- 研究工程：52项通过，覆盖原生分支、N1撤出、四/七卡t2差异、按轮F、完整渲染、来源父帖、超长补位、缺失和固定roster分母。
- 私人测量：65项通过，覆盖原题库/两层评分、别名和阶段资格、共同前缀复用、缺失状态及roster、SCA明确停止、答案/状态隔离。
- 原Core全量：首次231通过、57跳过、2失败；两失败均为本机127.0.0.1监听被执行环境权限阻止。随后只复核这两项本地服务测试，2项均通过。因此唯一测试共233通过、57跳过；不是首次整次全绿。跳过项含未启用真实LLM/可选伴随项目，未宣称已测。
- 原生入口首次因缺PYTHONPATH找不到skills，未开始运行；补明现有Core路径后通过。该失败与修复命令在日志说明中保留。

## 字符、历史与token

audit/PROMPT_SIZE_AND_HISTORY_AUDIT.json保留逐请求实际字符、UTF8字节、历史实例次数和来源文件；字符不当token。未选择真实模型，现有运行环境未配置已验证分词器，token_count=null、MODEL_NOT_SELECTED_COUNTER_NOT_VERIFIED。没有编造精确token量；这也是独立真实Pilot运行配置必须补齐的一项。没有把重复历史当系统新投放。

## 运行与复现

原生实际命令逐seed见audit/VALIDATION_SUMMARY.json，形式为：

```sh
PYTHONPATH=<已安装的SocioVerse2仓库> <sv-env>/bin/python <研究根>/scripts/run_native_scripted.py --seed 20271001 --out <新的空运行目录> --mode scripted
```

原运行目录拒绝覆盖。每组DuckDB、panel、exposures、messages、memory和完整rendered请求在原工程validation/B_FINAL_v03_RELEASE_seed…内，私人兼容输出在measurement_v2/validation/B_FINAL_v03_RELEASE_seed…内。交付包包含必要结果、数据库、审计、源变更、配置和引用索引，不打包巨大历史招生库。analysis_SOFTWARE_ONLY的数值仅测试夹具，不是干预发现。

数据schema见audit/VALIDATION_SUMMARY.json内每个数据库的真实describe panel和表计数。Source ledger/材料/配置/代码及修改前后hash均随包。技术测试通过不自动冻结材料、协议、题库或授权LLM。
