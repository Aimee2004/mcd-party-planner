# workbuddy.md —— WorkBuddy 开发记录

本项目的 Skill（麦麦派对策划师）完全在腾讯 WorkBuddy 智能体中开发完成，符合麦当劳程序员创意开发大赛 WorkBuddy 专项奖励的参与条件。

## 开发环境

- 工具：腾讯 WorkBuddy（桌面端，Agent 模式）
- 连接器：自定义 MCP 连接器 `mcd-mcp`（Streamable HTTP，`https://mcp.mcd.cn`），Token 经麦当劳 MCP 开放平台申请，配置使用环境变量占位符
- 工作区：`mcd-workbuddy-skill`

## 开发过程（与 WorkBuddy 的对话上下文摘要）

1. **规则调研**：通过 WorkBuddy 抓取活动仓库 `M-China-Official/mcd-developer-innovation-challenge` 的 README、activityGuidelines.md、CONTEST_DECLARATION.md，以及 `M-China/mcd-mcp-server` 的工具清单，明确参赛必备文件与格式要求。
2. **创意确认**：在官方示例方向（套餐推荐、省钱助手、活动推荐）之外，结合 MCP 独有的主题活动预约能力（query-party-city / query-party-store / query-partystore-date / query-partystore-session / party-order-create），确定差异化的「派对聚餐助手」方向，定名「麦麦派对策划师」。
3. **实测校准**：在 WorkBuddy 中直接调用已连接的 mcd-mcp——`mall-points-products`（按类目筛选派对商品，取到 26 个在售主题）、`query-party-city`（42 个城市）、`campaign-calendar`——核对真实入参/返回结构后写入 Skill 参考文档，避免凭文档臆测。
4. **Skill 构建**：使用 WorkBuddy 内置 skill-creator 规范初始化 `maimai-party-planner` 技能目录，编写 SKILL.md（三大工作流程 + 硬性约束）、references（实测校准的工具速查表、四类场景策划剧本）、scripts（AA 分摊脚本）、assets（派对 Checklist 模板）。
5. **参赛材料**：同会话内生成 README.md、MCP_INTEGRATION.md、mcp-config.example.json（环境变量占位符）、原样引用官方 CONTEST_DECLARATION.md 及本文件。

## 声明

- 本项目由 WorkBuddy 参与开发的全过程真实发生，本文件为对话上下文的忠实摘要，完整对话记录可由 WorkBuddy 导出佐证。
- 文中不包含任何真实 Token、密钥或个人敏感信息。
