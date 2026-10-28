# SocioVerse2 Track B 团队研究工作区

研究社会媒体信息、公共信息支持与同伴传播如何关联模拟考生的专业意愿，并描述 SES 异质性。24 名合成考生、固定网络、E1–E4 配对条件沿用现有研究，不代表真实考生总体。

**候选协作副本，尚未创建 GitHub 仓库。P1 六卡未最终批准；Pilot 和正式真实实验尚未运行。** A001 仅完成单时点组件诊断。scripted 数据仅供软件验证。先读 RESEARCH_PROTOCOL.md、DECISION_LOG.md。

## 快速开始（Python 3.12）

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/team.py test
.venv/bin/python tools/team.py analyze
.venv/bin/python tools/team.py report --out artifacts-local/report.html
```

打开 `reports/research_report.html` 可直接离线阅读现有结果，无需安装、密钥、服务或联网。重新生成使用保存 JSON，绝不调用模型。`test` 在临时新目录执行原四臂 scripted 运行器并逐行比对已保存 panel；主动阻断网络连接。默认不执行原 `test_phase18.py`（它包含需要受限题库的检查）。`tools/team.py scripted --out runs/my-unique-run` 可运行独立无费用验证，目录已存在则拒绝覆盖。

正式配置入口 `configs/formal.json`；Pilot 配置入口 `configs/pilot.json`；实验性修改放 `configs/experimental/`。三者均不授予真实运行权限。Study 当前名称沿用 controlled_major_phase18，目录为 `studies/controlled_major/`，原注册模块在 native/studies 内。官方运行时固定版本保存在 vendor，研究目录明确受版本控制，未继承官方默认忽略研究的规则。

## 数据与权限

`shared/` 是经字段筛选的只读共享快照；`shared/MANIFEST.json` 校验全部共享文件，编辑结果须另建版本，禁止原地修饰历史结果。`RUN_REGISTRY.md` 和 JSON 登记证据类型及材料、代码 hash。历史完整性范围见 `docs/ACCEPTANCE.md`。

EJQ 评分代码可审查，题干、答案键、私有逐题响应和单人分数不进 Git。测量负责人经独立授权后，在本机设置 `SV2_EJQ_BANK` 指向受限题库，先按 `shared/EXTERNAL_ARTIFACTS.json` 的原始 SHA-256 验证；未设置时评分请求失败，不生成替代题库。默认 scripted 测试无需题库。旧完整测试和真实运行入口仅作源代码保留，不在快速开始或 CI 调用。

大型 DuckDB、原始请求账本保留原处，外部索引只有文件标识、大小和 hash；storage_uri 为空表示未上传。研究者可在私有受控对象存储上传后填写 URI 与访问组，不能填公开下载地址或凭证。没有将本地 Dashboard 暴露公网。

官方来源与许可证见 `provenance/UPSTREAM.json`、`vendor/SocioVerse2/LICENSE` 和 `NOTICE`。研究材料与第三方摘要未因此获得 Apache 再许可。完整材料与来源索引在 Study materials，保留来源时间未核实标识；不包含抓取的第三方全文。

协作与上线步骤见 CONTRIBUTING.md 和 docs/GITHUB_SETUP.md。共享仓库链接位置：研究者创建并确认后填写 `docs/TEAM_LINKS.md`，目前未分配真实链接。
