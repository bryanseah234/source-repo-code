# 讨论：跨 IDE/跨代理 Skills 注册与 MCP 配置同步

> 状态：进行中 | 轮次：R4 | 日期：2026-04-22

## 🔵 当前焦点

- **技能推荐**：为 sourcerepo 推荐应添加的 Skills 集合
- **跨 IDE/代理架构**：如何让 Skills 同时支持 Cursor、Claude Code、Cline、VS Code 等
- **工作流拆分**：按关注点分离成多个独立 workflow
- **技能注册机制**：`npx skills add` 仅用于注册/激活，不含运行时依赖

## ⚪ 待讨论

- [ ] 用户希望支持哪些具体的 IDE / 编码代理组合
- [ ] 推荐的 Skills 列表是否需要优先级划分（必装 vs 可选）
- [ ] 工作流拆分粒度：是否需要 3 个独立 workflow
- [ ] MCP 配置格式：是否需要针对不同代理有不同的配置模板

## ✅ 已确认

- `npx skills add` 仅用于注册/激活 `.github/skills/*.md` 文件，不含运行时依赖
- 目标：跨 IDE / 跨代理支持
- 原则：按关注点分离工作流

## ❌ 已否决

## 📁 归档

| 问题 | 结论 | 详情 |
|------|------|------|
| R1 | 用户想表达项目级 Skills 部署方式 | - |
| R2 | 用户想扩展 sync.yml 支持 Skills + MCP | - |
| R3 | 理解用户架构：sourcerepo → sync → 所有项目仓库 | - |
