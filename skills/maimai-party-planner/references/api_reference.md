# 麦当劳 MCP 工具速查（派对链路，实测校准于 2026-10-21）

Server: `https://mcp.mcd.cn`（Streamable HTTP，`Authorization: Bearer <MCD_MCP_TOKEN>`）
限流：每 Token 600 次/分钟，超限返回 429。

## 派对主题链路（顺序依赖）

```
mall-points-products ──► mall-product-detail
        │ spuId                │ skuId / partyType / shopId
        ▼                      ▼
  query-party-city ──► query-party-store ──► query-party-store-date ──► query-party-store-session
        code/lat/lng         storeCode                dateStr                     id/timeStart/timeEnd/leftNum
        └──────────────────────────────► party-order-create ◄────────────────────────────┘
```

### mall-points-products 查询可兑换商品列表
- 入参：`catRuleIds`（string，非必填，逗号分隔多选）
- 派对相关类目：`1>6>20` 生日类派对、`1>6>21` 主题类派对、`1>6>22` 麦麦体验营、`1>6>25` 品鉴会、`1>6>34` 读书会、`1>6>40` 积分兑换活动；其他：`1>4` 商品券、`2` 实物商品、`2>8` 周边产品、`2>9` 实物礼品卡
- 返回 `data[]`：`spuName、spuId、point、price、selling、upTime、downTime、spuImage、shopId、catName、status`（1 仓库中/2 上架/3 售罄/4 下架/5 预热）
- 易错点：只推荐 status=2 且未过 downTime 的；派对商品均为 shopId=5。

### mall-product-detail 商品详情
- 入参：`spuId`（integer，必填）
- 返回全部 SKU 规格；`skuId` 与 `partyType` 从这里取。`partyType` 含义：1 包场、2 拼团、-1 需询问用户。

### query-party-city 派对城市列表
- 入参：`spuId`（number，必填）
- 返回 `data[]`：`code`（integer，如 110100）、`latitude`、`longitude`、`name`、`initial`、`sortNo`
- 易错点：code 在本工具返回的是 number，但传入 `query-party-store` 时作为 string。

### query-party-store 城市下可办派对门店
- 入参：`code`（string，必填）、`latitude/longitude`（number，取自 query-party-city）、`spuId`（number）
- 返回 `data[]`：`code`（餐厅编码，string，**即后续工具的 storeCode**）、`name/shortName、address、cityCode、cityName、latitude/longitude、distance/distanceText、businessStatus、onlineBusinessStatus`

### query-party-store-date 可预约日期
- 入参：`spuId`、`storeCode`（均必填）
- 返回 `data[]`：`date`（yyyy-MM-dd，即后续工具的 dateStr 参数值）、`storeCode`、`spuId`
- 易错点：返回字段名叫 `date`，但传给下一工具时参数名叫 `dateStr`。

### query-party-store-session 场次列表
- 入参：`spuId`、`storeCode`、`dateStr`（均必填）
- 返回场次：`id、timeStart、timeEnd、leftNum、price、partyMin、partyMax`
- 易错点：**`price` 单位为分**（5900 = ¥59.00），展示给用户前需换算为元。

### party-order-create 创建派对订单
- 必填：`partyType`、`spuId、skuId、code、storeCode、dateStr、id、timeStart、timeEnd、leftNum、count`
- 可选 `partyTimeInfo`（object，含 id/leftNum/partyMax/partyMin/price/timeStart/timeEnd）
- 硬约束：仅 shopId=5；count 须在 [partyMin, partyMax] 内；partyType=-1 时先询问用户；每步等待用户确认，禁止跳步下单。

## 聚餐点餐链路（流程 B 常用）

| 工具 | 用途 | 关键参数/易错点 |
|---|---|---|
| query-nearby-stores | 到店/得来速门店 | `beType` 1 自取 / 5 得来速（必填）；`searchType` 2 按位置（需 city+keyword）/ 1 收藏；得来速门店返回 beCode，后续必传 |
| delivery-query-stores | 外送可配门店 | 需用户地址；返回 storeCode、beCode |
| delivery-query-addresses / delivery-create-address | 读/建地址 | 无地址时先建 |
| query-meals | 在售菜单 | 分类、餐品编码、标签 |
| query-meal-detail | 套餐组成与替换项 | 按餐品编码 |
| query-store-coupons / query-my-coupons | 门店券 / 账户券 | 算价前查 |
| auto-bind-coupons | 一键领券 | 不需要 couponId，领完重查 my-coupons |
| query-meal-assistance | 团餐助餐服务 | 仅 beType=6；`orderType=2` + `beCode`（外送/团餐）；到店自取 orderType=1 不传 beCode；得来速 orderType=1 传 beCode；预约场景传 `reservationDate`（yyyy-MM-dd HH:mm） |
| calculate-price | 算价 | 商品列表 + 券；返回原价/优惠/配送费/应付 |
| create-order | 下单 | 返回支付链接，不代付 |
| query-order / order-list / cancel-order | 订单管理 | 取消须用户明确表达 |

## 灵感与账户（流程 C）

| 工具 | 用途 | 备注 |
|---|---|---|
| campaign-calendar | 当月活动日历 | 可传 `specifiedDate`（yyyy-MM-dd）锚定前后三天 |
| mall-points-products（不传类目） | 积分商城全览 | 周边、礼品卡等 |
| query-my-account | 积分账户 | 可用/累计/冻结/将过期 |
| draw-lottery / query-lottery-info / query-my-prizes | 积分抽奖 | 消耗积分或次数，先查活动信息 |

## 错误码

- 401：Token 无效/过期/未配置 → 检查 `Authorization` 与环境变量 `MCD_MCP_TOKEN`。
- 429：触发限流 → 降低频率，稍候重试。
