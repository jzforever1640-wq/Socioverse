# MATERIAL_DIFF_AND_PROVENANCE

版本：`1.8B-MAT-v0.3-CANDIDATE`；日期：2026-10-28（Asia/Shanghai）。

## 版本与活动差异

| 基线 | 本轮变化 | 保存方式 |
|---|---|---|
| v0.1/v0.2文稿 | 不覆盖；v0.2三张校园N退出，剩余19张标题/正文逐字保留 | 原outputs路径，哈希核对；新增v0.3版本目录 |
| 旧phase18工程 | S1重复补位改按轮F；P1/N1二选一改额外P1/不追加；输入别名、来源验证、评测与分析门禁接入 | versions/pre_B_FINAL_20261028含原代码/输入/材料/配置；原运行目录保留 |
| 当前材料 | 4S＋3P＋12F；N1_active=false，缺少N1为合法配置 | materials/versions/1.8B-MAT-v0.3-CANDIDATE/payloads.json；config/active_materials.json指定 |
| 当前测量演练 | 原入口会重建N1，现只读原生v0.3快照；SCA旧主张停止 | measurement_v2旧代码也在上述工程归档内；题库和key未改 |
| 估计对象 | 额外P1支持vs不额外支持 | 配对匹配、Primary终点不变；更新分析标签与解释 |

版本选择记录在config/version_history.json：研究者明确NEW_VERSION。研究目录是原有自定义项目，不是单一官方study.yaml根；因此保留项目源快照并登记新材料版本；每个验证运行内部仍用官方scaffold/init_manifest/create_branch/check_branch_invariant/resolve_warm_start，不以自造循环替代原生执行器。旧版复现可在归档根使用同一已安装Core另开输出目录运行，历史结果不覆盖。

## 来源复核与时间状态

本轮没有开放式搜集新刺激或添加正负材料，基于v0.2来源核验记录和已保存片段复审；“核验日期2026-10-28”指本轮审查，不伪称重新下载原网页。source_ledger将原始发表、页面更新、实际检索、研究者核验、截止前正文存在证据分开。无可信历史原字节证明的来源均保持UNVERIFIED_HISTORICAL_BYTES。

| 来源 | 活动用途 | 原始日期字段 | 更新时间 | 检索/本轮核验 | 截止前正文状态 |
|---|---|---|---|---|---|
| [X01](https://www.v2ex.com/t/1217897) | EXT:S01、EXT:F204 | 正文明确2026；页面Jun 4 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [ST019](https://www.ruanyifeng.com/blog/2026/03/weekly-issue-389.html) | EXT:S02、EXT:F304 | 2026-03-20 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [N01](https://www.v2ex.com/t/1140972) | EXT:S03 | 2025-06-25 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [X02](https://news.cctv.cn/2026/03/18/ARTILJb495gePh8EhPtjtwvF260318.shtml) | EXT:S04 | 2026-03-18 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [EV08A](https://www.microsoft.com/en-us/research/publication/the-effects-of-generative-ai-on-high-skilled-work-evidence-from-three-field-experiments-with-software-developers/) | PUB:P101 | June 2025 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [EV09](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) | PUB:P101 | 2025-07-10 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [EV10](https://metr.org/blog/2026-02-24-uplift-update/) | PUB:P101 | 2026-02-24 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [EDU-CS](https://eecs.pku.edu.cn/info/1083/5201.htm) | PUB:P102 | 2022-09-01 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [EV06/EV07](https://www.bls.gov/ooh/computer-and-information-technology/software-developers.htm) | PUB:P102 | 创建/发布日期未独立确认 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [EDU-AUTO2](https://bkzs.sxist.edu.cn/info/1241/3261.htm) | PUB:P102 | 2025-04-27 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [EDU-EE](https://gcxy.shou.edu.cn/dqgcjqzdh/list.htm) | PUB:P103 | 创建/发布日期未独立确认 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [EDU-STAT3](https://zsb.sanxiau.edu.cn/info/1121/2167.htm) | PUB:P103 | 2025-05-29（当前站页显示） | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [N05](https://v2ex.com/t/1182900) | EXT:F201、EXT:F401 | 创建/发布日期未独立确认 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [N08](https://v2ex.com/t/1224757) | EXT:F202、EXT:F404 | 创建/发布日期未独立确认 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [N03](https://www.v2ex.com/t/1141317) | EXT:F203、EXT:F403 | 2025-06-26；#17为2025-06-27 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [N06](https://www.v2ex.com/t/1228794) | EXT:F301、EXT:F402 | 创建/发布日期未独立确认 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [N02](https://www.v2ex.com/t/1140969) | EXT:F302 | 2025-06-25 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |
| [C4=ST020](https://v2ex.com/t/1200380) | EXT:F303 | 创建/发布日期未独立确认 | 未确认 | 2026-10-27 / 2026-10-28 | UNVERIFIED_HISTORICAL_BYTES |

S02/F304同一ST019文章，继续曝光而非独立新证据。X01用于S01/F204，N08用于F202/F404，N05用于F201/F401，N03用于F203/F403，N06用于F301/F402，均在后台保留共同source_ref和具体楼层。F202/F404的N08原页与本地快照要义相符，仍属个人经验，不升为企业实证。原上传N05 #1/#3/#15无法取得正文，已不在活动材料；原天津自动化页只取到导航的问题通过v0.2已选可读官方AUTO2解决，不宣称旧链接已核成功。

## 修改前后SHA-256

完整代码/配置/文档before/after见audit/AUTHORIZED_CHANGES_FINAL.json；原25个输入的比较另见audit/INPUT_AND_OUTPUT_HASH_CHANGES.json；所有原工程快照核对通过，原Population、三网络、旧payload和原EJQ题库未改。新文件和本轮measurement_v2变化见PACKAGE_MANIFEST与engineering_patch。核心框架代码未修改。

| 已有活动文件 | 修改前 | 修改后 |
|---|---|---|
| config/analysis_protocol_DRAFT.json | `788423a3e24a3309589ff0e774b79bcd8b4224c6368a946a32c4b0a3e3b7f4d2` | `a2916a9791d35b7e46ac4e34c160e7262b638117c4401553ba21cd5feb6c8e46` |
| scripts/analyze_outcomes.py | `c3596915ac0491e6bca3464bb52c9b173540fa1ff85c781bfb7c45ab105fe79a` | `26ee240582fcd28de9b0d05e343ea47e888b70b388a53b74d9b66979eea30291` |
| scripts/test_phase18.py | `d829e70e17944ece984340d5754b348a4640e397e148b1e32db3c7e271f88d8b` | `63e85609971c870ac1f292fad929c26e3d8c627da0068c9dd862c63295be8ae2` |
| scripts/run_native_scripted.py | `6ef9c67f27c5114d598adac97ad332fed7d07189769fcd75f0c022873c0d7fa5` | `a14fb462c1004f8cdce990ec867767c56b5103aac333e4b7435b771af0c628e1` |
| scripts/measurement_sidecar.py | `5e27e2c27c3bd08b49279184f4fcb1fdeb2fe1414ae0a8d1b5b4037d0f43c295` | `e600a6e4c3c95c7afc0b8cea08931afc9e92642307edc5917c36100e4930892d` |
| scripts/private_llm_measurement.py | `255b8a797f27a35278cba3fb8ab536add4c7dc1d9f78abacd2f04deedf549127` | `eeac527021d2fdaae9a67b7a0bb0560a18c50b2f18e1db9bc6850e53ef934428` |
| native/studies/controlled_major_phase18/model.py | `2887e466164bdd2b48aba8a456181342d9e2a07d2cc59c5b18e8377212e56e65` | `4704b14f06f58e229911f4c918a82451f2ba80a7c289019bdcec46093d88bc85` |
