# 🎉 麦麦派对策划师 (MaiMai Party Planner)

> 基于麦当劳 MCP 的聚餐派对一站式策划 Skill —— 一句话，从"想聚"到"约好"。

「下个月想给 5 岁女儿办个生日会」「周五团队 12 人聚餐，人均 60」「最近麦当劳有什么好玩的品鉴会？」——把需求丢给麦麦派对策划师，它会基于**麦当劳 MCP 实时数据**完成：推荐主题派对 → 锁定城市门店日期场次 → 预约下单，或为普通聚餐生成点餐组合、叠加优惠券、算好人均预算，最后输出一份完整的《麦麦派对策划案》。

## ✨ 核心功能

| 能力 | 说明 | 依赖的麦当劳 MCP 工具 |
|---|---|---|
| 🎂 主题派对预约 | 生日会/主题派对/麦麦体验营/品鉴会/读书会的"城市→门店→日期→场次→下单"全链路逐步引导 | `mall-points-products`、`mall-product-detail`、`query-party-city`、`query-party-store`、`query-party-store-date`、`query-party-store-session`、`party-order-create` |
| 🍔 聚餐点餐规划 | 按人数×人均预算生成 2-3 套点餐组合并比价 | `query-nearby-stores`、`delivery-query-stores`、`query-meals`、`query-meal-detail`、`calculate-price`、`create-order` |
| 💰 省钱叠加 | 门店券/账户券/一键领券，团餐助餐服务 | `query-store-coupons`、`query-my-coupons`、`auto-bind-coupons`、`query-meal-assistance` |
| 🎈 活动情报 | 当月营销日历、积分商城、积分抽奖 | `campaign-calendar`、`mall-points-products`、`query-my-account`、`draw-lottery` |
| 🧮 AA 分摊 | 聚餐费用分摊计算脚本 | 本地脚本 `scripts/budget_split.py` |

## 📦 安装

### 1. 配置麦当劳 MCP

先到[麦当劳 MCP 开放平台](https://open.mcd.cn/mcp)申请 MCP Token（详见[申请教程](https://github.com/M-China/mcd-mcp-server)），然后在 WorkBuddy 中配置本仓库提供的 `mcp-config.example.json`（把 `${MCD_MCP_TOKEN}` 替换为你的真实 Token）：

```json
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamablehttp",
      "url": "https://mcp.mcd.cn",
      "headers": {
        "Authorization": "Bearer ${MCD_MCP_TOKEN}"
      }
    }
  }
}
```

> ⚠️ 请勿把真实 Token 提交到任何仓库或贴到公开场合，配置中使用环境变量占位符。

### 2. 安装本 Skill

将 `skills/maimai-party-planner/` 目录复制到 `~/.workbuddy/skills/`（用户级）或项目的 `.workbuddy/skills/`（项目级），重启 WorkBuddy 即可。也可以直接下载本仓库 `dist/maimai-party-planner.zip` 解压安装。

## 🚀 使用示例

安装后，在 WorkBuddy 对话框里直接说：

- 「帮我策划一个下周六的儿童生日会，8 个小朋友，上海，预算 500 以内」
- 「周五晚上团队 12 人团建聚餐，人均 60，找个有意思的」
- 「最近麦当劳有什么新品品鉴会？带朋友去」
- 「社团 8 人聚餐，人均 30 以内，帮我算好怎么点最省」

Skill 会逐步与你确认（城市→门店→日期→场次→人数），并在关键操作（预约/下单/取消）前二次确认，最后输出结构化策划案。

**示例输出：**

```
🎉 麦麦派对策划案
主题：程序员节派对（¥59/人，品鉴会）
地点：上海市 xx 门店（storeCode: xxxxxx）
时间：10月24日（周六） 14:00-15:30（余位 6）
人数：8 人 ｜ 人均：¥59
优惠建议：可先 auto-bind-coupons 领券，现场加餐叠加使用
待确认：回复"创建订单"即可预约
```

## 🎯 目标用户

- **宝妈宝爸**：给孩子办生日会、主题派对，不想自己操心流程
- **职场团队**：部门团建、项目庆功、例会加餐，要有趣又要好报销
- **学生社群**：班级/社团聚会，预算敏感，追求性价比
- **吃货潮人**：追新品品鉴会、主题体验，喜欢凑热闹

## 🗂 项目结构

```
.
├── README.md                        # 本文件
├── CONTEST_DECLARATION.md           # 参赛声明（官方原文）
├── MCP_INTEGRATION.md               # 麦当劳 MCP 集成说明
├── mcp-config.example.json          # 脱敏 MCP 配置示例（环境变量占位符）
├── workbuddy.md                     # WorkBuddy 开发对话上下文说明
└── skills/
    └── maimai-party-planner/        # Skill 主体
        ├── SKILL.md                 # 技能定义与工作流程
        ├── references/
        │   ├── api_reference.md     # MCP 工具速查（实测校准）
        │   └── party-playbook.md    # 四类场景策划剧本
        ├── scripts/
        │   └── budget_split.py      # AA 分摊计算脚本
        └── assets/
            └── party-checklist.md   # 派对当日 Checklist 模板
```

## ⚠️ 说明

- 本项目为麦当劳程序员节创意开发大赛参赛作品，由参赛者独立开发，非麦当劳官方产品。
- 所有门店、场次、价格、余位数据来自麦当劳 MCP 实时接口，以麦当劳官方渠道为准。
- 支付环节一律引导回麦当劳官方渠道，本 Skill 不代为支付。
