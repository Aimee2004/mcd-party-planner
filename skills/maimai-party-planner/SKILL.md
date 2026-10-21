---
name: maimai-party-planner
description: 麦麦派对策划师——基于麦当劳 MCP 的聚餐派对一站式策划技能。当用户想组织生日会、儿童主题派对、公司团建、班级聚会、朋友聚餐、品鉴会、麦麦体验营，或询问麦当劳主题活动预约、聚餐点餐比价、团餐安排时使用此技能。本技能应驱动 mcd-mcp 连接器完成"找主题→选城市→选门店→选日期场次→预约下单/聚餐点餐→人均预算"的全流程策划。
agent_created: true
---

# 麦麦派对策划师 (MaiMai Party Planner)

## Overview

将用户一句"想组织个聚餐/派对"变成一份可直接执行的麦当劳派对策划案：推荐当下可预约的主题活动，逐级收窄城市、门店、日期、场次，并支持预约下单；非主题派对的普通聚餐则提供门店比选、点餐清单、优惠券叠加与人均预算。所有真实数据来自麦当劳 MCP Server（`https://mcp.mcd.cn`），禁止编造门店、场次、价格。

## 工作流程决策树

先判断用户属于哪类场景：

1. **主题活动/派对预约**（生日会、主题派对、麦麦体验营、品鉴会、读书会、积分兑换活动）→ 走【流程 A】
2. **普通聚餐点餐**（多人到店、外送拼单、得来速、企业团餐）→ 走【流程 B】
3. **只要灵感/情报**（"最近有什么活动""有什么好玩的"）→ 走【流程 C】
4. **混合需求**（派对 + 现场加餐）→ 先 A 后 B，合并出一份策划案

需求收集必备四要素（缺失时先问，一次问全，不要挤牙膏）：城市、日期/日期范围、人数、人均预算；儿童派对另问年龄段。

## 流程 A：主题活动预约（逐步确认，禁止跳步）

链路：找主题 → 查城市 → 查门店 → 查日期 → 查场次 → 创建订单。**每一步完成后必须把结果呈现给用户并等待明确选择，再进行下一步。**

1. **找主题（spuId）**：调用 `mall-points-products`，用 `catRuleIds` 按场景筛选：
   - 生日类派对 `1>6>20`；主题类派对 `1>6>21`；麦麦体验营 `1>6>22`；品鉴会 `1>6>25`；读书会 `1>6>34`；积分兑换活动 `1>6>40`
   - 可多选逗号分隔，如 `"1>6>20,1>6>21"`。向用户展示 商品名称/spuId/所需金额/卖点，让其选定一个 spu。
   - 仅展示 `status=2`（上架）且 `downTime` 未过期的商品；过期或售罄的直接过滤。
   - 如需了解主题详情（含 skuId、partyType、shopId），调用 `mall-product-detail`。
2. **查城市**：`query-party-city`（传 spuId），返回 `data[].code/latitude/longitude/name`。用户所在城市不在列表中时如实告知并推荐最近可选项。
3. **查门店**：`query-party-store`（传 `code`（string）、`latitude/longitude`（取自城市返回）、`spuId`），得到候选门店 storeCode。
4. **查日期**：`query-party-store-date`（传 `spuId`、`storeCode`），得到 `dateStr` 列表。
5. **查场次**：`query-party-store-session`（传 `spuId`、`storeCode`、`dateStr`），得到场次 `id、timeStart、timeEnd、leftNum、price、partyMin/partyMax`。展示时标注余位紧张（leftNum ≤ partyMin 的 20%）的场次。
6. **创建订单**：`party-order-create`。下单前必须复述完整订单信息（主题、门店、场次时间、人数、金额）并获得用户确认。参数要点：
   - `partyType`：商品 partyType=1 → 传 1（包场）；=2 → 传 2（拼团）；=-1 → 必须先询问用户要包场还是拼团。
   - 仅 `shopId=5` 的商品支持（ mall 返回的派对商品均为 shopId=5）。
   - 必填：`spuId、skuId、code、storeCode、dateStr、id、timeStart、timeEnd、leftNum、count`。
   - `count` 必须满足场次的 partyMin/partyMax，越界先提醒用户。

下单成功后主动补充：可顺手用 `query-my-coupons`/`auto-bind-coupons` 看有无可叠加优惠，用 `query-my-prizes`/`draw-lottery` 提示积分抽奖（如用户有兴趣）。

## 流程 B：普通聚餐点餐

1. **定位就餐方式**：到店自取（beType=1）、得来速（beType=5）用 `query-nearby-stores`；外送/团餐（beType=2/6）用 `delivery-query-stores`（需要用户地址；无地址可用 `delivery-query-addresses` 读取已有地址或 `delivery-create-address` 新增）。
2. **选菜**：`query-meals` 按门店查在售菜单 → `query-meal-detail` 查套餐组成与可替换项。多人聚餐按人数×人均预算生成 2-3 套组合建议（主食/小吃/饮品配比），标注每套总价。
3. **算优惠**：到店用 `query-store-coupons`，账户券用 `query-my-coupons`；也可 `auto-bind-coupons` 一键领券后重查。企业团餐（beType=6）在算价前必须先 `query-meal-assistance`（orderType=2，传 beCode）。
4. **算价**：`calculate-price`（商品列表 + 可用券），展示原价/优惠/应付。注意 beType 与 orderType 映射：到店自取 orderType=1 不传 beCode；得来速 orderType=1 传 beCode；麦乐送/团餐 orderType=2 传 beCode。
5. **下单**：`create-order` 前再次确认商品、就餐方式、金额；返回支付链接后明确告知"链接请在麦当劳官方渠道完成支付"。订单管理用 `query-order`/`order-list`/`cancel-order`。

## 流程 C：灵感与情报

- `campaign-calendar`（可选 `specifiedDate`）查当月活动日历，从中提炼适合聚餐蹭热度的活动（新品、联名、周边）。
- `mall-points-products` 浏览积分商城（含周边、礼品卡），给"预算有限"的团队积分兑换建议。
- `query-my-account` 查积分余额，结合兑换门槛给攒积分建议。

## 策划案输出格式

策划完成（无论走到哪一步中断）都产出结构化小结：

```
🎉 麦麦派对策划案
主题：xxx（¥xx/场，包场/拼团）
地点：xx市 xx门店（storeCode: xxxx）
时间：x月x日 xx:xx-xx:xx（余位 xx）
人数：xx 人 ｜ 人均：¥xx
餐品建议：…（如适用）
优惠建议：…（可用券/积分）
待确认：…（下一步需要用户拍板的事项）
```

多人分摊、AA 计算可调用 `scripts/budget_split.py`。

## 硬性约束

- 一切门店、场次、价格、余位以 MCP 实时返回为准，禁止编造或凭记忆报数。
- 预约与下单类操作必须二次确认；取消订单（`cancel-order`）必须用户明确说出取消意图后执行。
- 不代替用户支付；支付一律引导回官方渠道。
- 遇 429 限流（600 次/分钟）时稍后重试，避免连续高频调用。
- 参与人数、预算等个人信息仅用于本次策划，不写入任何文件。

## Resources

- `references/party-playbook.md`：四类典型场景的完整对话剧本与推荐话术（儿童生日会、公司团建、班级聚会、品鉴尝新）。
- `references/api_reference.md`：派对链路及相关 MCP 工具的参数、返回结构、易错点速查表（已实测校准）。
- `scripts/budget_split.py`：聚餐费用分摊/AA 计算脚本。
- `assets/party-checklist.md`：派对当日 Checklist 模板，策划案输出后附赠给用户。
