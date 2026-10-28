# 研究者需要执行的 GitHub 步骤

当前项目是独立本地 Git 候选，不指向官方远端，也未创建或推送 GitHub 仓库。建议在团队组织下创建全新 **Private** 仓库 SocioVerse2-TrackB（名称可自行确定），不沿用官方 origin，不创建公开 fork。

1. 审阅本地 README、DECISION_LOG、docs/ACCEPTANCE.md、暂存差异和共享文件白名单；确认研究材料许可及团队可见范围。当前本地提交仅为验收快照，不是研究批准。
2. 创建空 Private 仓库；确认组织和可见性，保留空初始状态。将该仓库提供的 HTTPS URL 设置为本地 origin；不要将本项目推送到 SocioVerse2 官方仓库。
3. 核对暂存内容与 provenance/RELEASE_FILES.json 后，将已审阅 main 推送；建议先由研究者人工检查远端文件页。
4. 配置 main 保护：必须 PR、至少1位非作者审核、敏感方法须研究负责人审核、必需 offline-check、新提交撤销旧审核、禁强推/删分支。CODEOWNERS 中填写真实 GitHub 用户或团队，核实该账号有写入权限。小团队若技术审核与研究审核由同一人承担，仍须分别记录两种结论。
5. 按确认后的名单人工邀请；普通成员仅授予所需权限。EJQ 题库保存在另一个受控位置，仅测量负责人可读；GitHub 私有仓库不等于题库保密隔离。
6. 启用可用的秘密扫描和推送保护；建立分支 PR 演练，确认 offline-check 与审核规则实际阻止未批准合并。当前仅完成本地合并演练，不能声称 GitHub 保护已生效。
7. 填写 TEAM_LINKS.md 中实际仓库 URL、报告相对路径、审批 PR 和受控外部存储索引。不要启用公开 Pages 或无认证 Dashboard。

示意链接形状为 https://github.com/<组织>/<仓库>，并非已创建的仓库地址。此任务没有邀请成员、调整权限或推送文件。
