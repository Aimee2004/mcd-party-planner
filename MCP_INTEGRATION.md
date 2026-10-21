# 麦当劳 MCP 集成说明 (MCP_INTEGRATION.md)

## 1. 使用的 MCP Server

| 项目 | 内容 |
|---|---|
| Server 名称 | 麦当劳 MCP Server（mcd-mcp） |
| 接入地址 | `https://mcp.mcd.cn` |
| 传输协议 | Streamable HTTP |
| 认证方式 | 请求头 `Authorization: Bearer <MCP Token>`（Token 经[麦当劳 MCP 开放平台](https://open.mcd.cn/mcp)申请，配置中以环境变量占位符 `${MCD_MCP_TOKEN}` 引用） |
| 限流 | 每 Token 600 次/分钟 |

## 2. 实际使用的 Tools

本项目共使用麦当劳 MCP 的 21 个工具，按业务链路分为四组（全部经过实测校准）：

### 2.1 主题派对预约链路（核心）

| Tool | 作用 | 输入要点 | 输出关键信息 |
|---|---|---|---|
| `mall-points-products` | 查询积分商城可兑换商品，定位派对主题（spuId） | `catRuleIds` 类目筛选：`1>6>20` 生日派对 / `1>6>21` 主题派对 / `1>6>22` 体验营 / `1>6>25` 品鉴会 / `1>6>34` 读书会 / `1>6>40` 积分兑换活动 | spuId、名称、价格、卖点、上下架时间、状态 |
| `mall-product-detail` | 商品详情，取得 skuId 与 partyType | `spuId` | SKU 列表、partyType（1 包场/2 拼团/-1 需询问）、shopId |
| `query-party-city` | 该主题可预约城市 | `spuId` | 城市 code、经纬度、城市名 |
| `query-party-store` | 城市下可办派对的门店 | `code`（string）、`latitude/longitude`、`spuId` | 门店列表（storeCode） |
| `query-party-store-date` | 门店可预约日期 | `spuId`、`storeCode` | dateStr 列表 |
| `query-party-store-session` | 日期下可预约场次 | `spuId`、`storeCode`、`dateStr` | 场次 id、起止时间、余位、价格、成团人数上下限 |
| `party-order-create` | 创建派对订单 | `partyType、spuId、skuId、code、storeCode、dateStr、id、timeStart、timeEnd、leftNum、count` | 订单结果；仅支持 shopId=5，人数须满足 partyMin/partyMax |

### 2.2 聚餐点餐链路

| Tool | 作用 |
|---|---|
| `query-nearby-stores` | 到店自取（beType=1）/得来速（beType=5）门店查询 |
| `delivery-query-stores` / `delivery-query-addresses` / `delivery-create-address` | 外送场景门店与地址管理 |
| `query-meals` | 当前门店在售菜单（分类、编码、标签） |
| `query-meal-detail` | 餐品详情与套餐组成/替换项 |
| `calculate-price` | 商品金额、配送费、优惠、应付总价计算 |
| `create-order` | 创建订单并返回支付链接（支付引导回官方渠道，不代付） |
| `query-order` / `order-list` / `cancel-order` | 订单查询、历史订单、取消订单（须用户明确表达） |

### 2.3 优惠与团餐

| Tool | 作用 |
|---|---|
| `query-store-coupons` / `query-my-coupons` | 门店可用券 / 账户券查询，算价前调用 |
| `auto-bind-coupons` | 麦麦省一键领券（无需指定券 id） |
| `query-meal-assistance` | 企业团餐（beType=6）助餐服务查询，算价前必调；orderType=2 且必传 beCode |
| `query-my-account` | 积分账户（可用/冻结/将过期），用于积分兑换建议 |

### 2.4 活动情报

| Tool | 作用 |
|---|---|
| `campaign-calendar` | 当月营销活动日历，用于聚餐灵感与蹭活动 |
| `mall-points-products`（全类目） | 积分商城周边/礼品卡浏览 |
| `query-lottery-info` / `draw-lottery` / `query-my-prizes` | 积分抽奖活动信息、抽奖、奖品记录（收尾互动） |

## 3. 调用流程

### 3.1 主题派对预约（逐步确认，禁止跳步）

```
mall-points-products ──► mall-product-detail
        │ spuId                │ skuId / partyType / shopId
        ▼                      ▼
  query-party-city ──► query-party-store ──► query-party-store-date ──► query-party-store-session
        code/lat/lng         storeCode                dateStr                     场次 id/时间/余位
        └──────────────────────────────► party-order-create ◄────────────────────────────┘
```

每一步的结果都呈现给用户并等待明确选择后再进入下一步；下单前复述完整订单信息做二次确认；`partyType=-1` 时先询问用户要包场还是拼团。

### 3.2 普通聚餐点餐

```
query-nearby-stores / delivery-query-stores
        │ storeCode（及 beCode）
        ▼
query-meals ──► query-meal-detail ──► [query-store-coupons / query-my-coupons]
        │                                        │
        ▼                                        ▼
   组合建议（人均预算 × 人数） ──────────► calculate-price ──► create-order
```

企业团餐场景在 `calculate-price` 前插入 `query-meal-assistance`（beType=6）。

### 3.3 实测记录（2026-10-21）

- `mall-points-products`（catRuleIds=1>6>20,1>6>21,1>6>22,1>6>25）：返回 26 个在售派对/品鉴商品，含「程序员节派对」等，结构与文档一致。
- `query-party-city`（spuId=18229）：返回 42 个可预约城市（含 code/经纬度）。
- `campaign-calendar`：返回当月活动日历，含进行中与未来活动。

## 4. 业务价值

- **对用户**：把"组织一次聚餐/派对"从数小时的信息搜集（查门店、对场次、比价格、凑优惠）压缩为一轮对话；麦当劳的主题派对资源（生日会、体验营、品鉴会）此前分散在 App 各入口，本 Skill 将其串联成端到端预约体验。
- **对麦当劳**：提升主题派对与积分商城等长尾资源的曝光与转化，通过"聚会场景"带动多人客单与会员积分活跃。
- **差异化**：市面上的麦当劳 Skill 多聚焦单人点餐或省钱，本 Skill 聚焦"多人聚会"这一高客单、高决策成本场景，形成互补。
