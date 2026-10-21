#!/usr/bin/env python3
"""聚餐费用分摊计算器（麦麦派对策划师配套脚本）。

用途：聚餐结算时计算总额、人均，以及多人 AA 时每个人的应付金额
（支持不同人吃不同价、券抵扣均摊）。

用法：
    python3 budget_split.py --total 520 --people 8                 # 简单均摊
    python3 budget_split.py --items "张三:88,李四:52,王五:65"        # 各点各的
    python3 budget_split.py --items "张三:88,李四:52" --coupon 30    # 券抵扣均摊
"""

import argparse
import sys


def parse_items(raw: str) -> list[tuple[str, float]]:
    items = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise ValueError(f"条目格式错误: {part}（应为 姓名:金额）")
        name, amount = part.rsplit(":", 1)
        value = float(amount)
        if value < 0:
            raise ValueError(f"金额不能为负: {part}")
        items.append((name.strip(), value))
    if not items:
        raise ValueError("至少需要一个条目")
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description="聚餐费用分摊计算")
    parser.add_argument("--total", type=float, help="总金额（元）")
    parser.add_argument("--people", type=int, help="均摊人数")
    parser.add_argument("--items", type=str, help='按人明细，如 "张三:88,李四:52"')
    parser.add_argument("--coupon", type=float, default=0.0, help="优惠券抵扣金额（元），均摊到每人")
    args = parser.parse_args()

    try:
        if args.items:
            items = parse_items(args.items)
        elif args.total is not None and args.people:
            if args.people <= 0:
                raise ValueError("人数必须大于 0")
            per = round(args.total / args.people, 2)
            items = [(f"成员{i + 1}", per) for i in range(args.people)]
        else:
            parser.error("需要提供 --items 或同时提供 --total 与 --people")
            return 2

        gross = round(sum(a for _, a in items), 2)
        payable = round(max(gross - args.coupon, 0), 2)

        print(f"原价合计: ¥{gross:.2f}")
        if args.coupon:
            print(f"券抵扣:   -¥{args.coupon:.2f}")
        print(f"实付合计: ¥{payable:.2f}")
        print("-" * 32)
        for name, amount in items:
            share = round(amount - args.coupon * (amount / gross) if gross else amount, 2)
            print(f"{name}: 应付 ¥{share:.2f}")
        return 0
    except ValueError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
