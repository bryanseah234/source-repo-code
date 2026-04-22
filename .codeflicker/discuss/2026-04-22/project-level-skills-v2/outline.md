# 讨论：跨 IDE/跨代理 Skills 注册与 MCP 配置同步

> 状态：进行中 | 轮次：R5 | 日期：2026-04-22

## 🔵 当前焦点

- **重建 Skills 策略**：删除现有手写 skills 文档，改为使用 `npx skills` 规范来源重建
- **技能来源筛选**：从公开 skills 仓库中挑选适合用户多仓库场景的 skills
- **工作流拆分**：明确 3 个独立 workflow 的职责边界
- **跨代理传播模型**：sourcerepo 中安装 project-level skills → sync 到所有仓库

## ⚪ 待讨论

- [ ] 是否仅选择通用开发类 skills，还是也纳入领域型 skills（如 Base、Stitch）
- [ ] 安装方式是将 sourcerepo 作为“已安装后的结果仓库”同步，还是保存安装命令清单再在每个目标仓库执行
- [ ] MCP 配置是否与 skills workflow 完全独立
- [ ] 是否维护一个“推荐 skills 清单”文档，便于未来增删

## ✅ 已确认

- 现有 `.github/skills/*.md` 不再视为有效资产，用户倾向于删除并重新建立
- `npx skills` 是实际来源，skills 需要通过该工具安装后才算规范接入
- 目标是让安装后的文件传播到当前和未来所有仓库
- 用户同意按关注点分离拆分为 3 个 workflow

## ❌ 已否决

- 继续沿用当前手写 `.github/skills/*.md` 作为正式 skills 来源

## 📁 归档

| 问题 | 结论 | 详情 |
|------|------|------|
| R1 | 用户想表达项目级 Skills 部署方式 | - |
| R2 | 用户想扩展 sync.yml 支持 Skills + MCP | - |
| R3 | 理解用户架构：sourcerepo → sync → 所有项目仓库 | - |
| R4 | `npx skills add` 仅用于注册/激活 skills | - |
