# sourcerepo

本仓库是所有项目仓库的同步源，负责统一维护并分发配置、Skills 和 MCP 模板。

## 核心职能

- 同步 GitHub Actions 通用配置（Dependabot、labels、greetings、TruffleHog）
- 通过 `npx skills` 安装规范的 Agent Skills，并同步到所有仓库
- 传播 MCP 配置模板与说明文档
- 统一仓库设置（description、homepage、issue/wiki/project/discussion 等）及合并策略
- 维护 AGENTS.md 作为 Agent 行为规范

## 仓库设置同步

本仓库通过 GitHub Actions 自动为所有仓库统一配置以下设置：

### 基本信息
- `description`: "Give me 1 ⭐ if it's cool."
- `homepage`: https://www.hong-yi.me
- `visibility`: 保留现有值（不覆盖）

### 功能开关
- `has_issues`: `true`（启用 Issues）
- `has_wiki`: `true`（启用 Wiki）
- `has_projects`: `true`（启用 Projects）
- `has_discussions`: `true`（启用 Discussions）
- `has_downloads`: `true`（启用 downloads）
- `has_pages`: `false`

### 合并策略
- `allow_squash_merge`: `true`（允许 Squash Merge）
- `allow_merge_commit`: `true`（允许 Merge Commit）
- `allow_rebase_merge`: `true`（允许 Rebase Merge）

### 合并与分支
- `allow_auto_merge`: `true`（允许自动合并）
- `delete_branch_on_merge`: `true`（合并后删除分支）
- `allow_forking`: `true`（允许 Forking）

- `web_commit_signoff_required`: `false`（不要求 Web 提交签名）

这些设置会在每个仓库创建或修改时被统一应用。

## Skills 管理

本仓库使用 `npx skills` 安装公开 skills，并将安装结果同步到其他仓库。

### 已安装 Skills

- `web-design-guidelines`：UI/UX、可访问性、前端审查
- `vercel-react-best-practices`：React/Next.js 性能与最佳实践
- `vercel-composition-patterns`：React 组件组合模式
- `vercel-react-view-transitions`：React 视图过渡动画
- `conventional-commit`：规范 commit message
- `pin-github-actions`：GitHub Actions SHA 固定
- `verify-pr-logs`：CI 日志诊断
- `verify-readme-features`：README 与实现一致性核验
- `diataxis`：文档体系治理
- `mcp-builder`：MCP server 设计与构建

### Skills 安装方式

在 `sourcerepo` 中 project-level 安装，再将结果同步出去。不在每个目标仓库重复执行安装命令。

详细清单与来源参见 [`docs/skills-manifest.md`](<kfile name="skills-manifest.md" path="docs/skills-manifest.md">docs/skills-manifest.md</kfile>)。

## MCP 配置

- 当前阶段：传播配置模板与支持文档，不承诺所有 IDE/Agent 自动读取同一文件
- 详细策略与支持矩阵参见 [`docs/mcp-support-matrix.md`](<kfile name="mcp-support-matrix.md" path="docs/mcp-support-matrix.md">docs/mcp-support-matrix.md</kfile>)

## 同步工作流

本仓库维持三个独立的同步 workflow，实现关注点分离：

- [`sync-skills.yml`](<kfile name="sync-skills.yml" path=".github/workflows/sync-skills.yml">.github/workflows/sync-skills.yml</kfile>)：同步 Skills（`.agents/skills`、`.claude/skills`、`docs/skills-manifest.md`）
- [`sync-mcp.yml`](<kfile name="sync-mcp.yml" path=".github/workflows/sync-mcp.yml">.github/workflows/sync-mcp.yml</kfile>)：同步 MCP 模板与文档（`templates/mcp`、`docs/mcp-support-matrix.md`）
- [`sync-repo-settings.yml`](<kfile name="sync-repo-settings.yml" path=".github/workflows/sync-repo-settings.yml">.github/workflows/sync-repo-settings.yml</kfile>)：同步仓库设置与通用配置（GitHub Actions、Dependabot、labels、AGENTS.md 等）

## 如何使用

- **新增/更新 Skills**：在 `sourcerepo` 使用 `npx skills add` 安装（project-level），同步workflow 会自动传播
- **新增/更新配置**：修改仓库内相关文件，对应的 workflow 会自动传播
- **手动触发**：在 GitHub Actions 中可选择对应 workflow 运行 `workflow_dispatch`
- **未来新仓库**：定时任务会自动将配置同步到新仓库

## License

SPDX-License-Identifier: MIT
