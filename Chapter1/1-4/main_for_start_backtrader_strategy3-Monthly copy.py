"""範例策略：每月 1 號定期定額買入 0050，單筆 10,000 元，回測區間 2020/1/1 ~ 2025/12/12."""

import datetime as dt
import backtrader as bt
import pandas as pd
import yfinance as yf


class MonthlyDCA(bt.Strategy):
    params = dict(
        investment_amount=10_000,  # 每月投入金額
        investment_day=1,  # 每月幾號下單
        start_date=dt.date(2020, 1, 1),
        end_date=dt.date(2025, 12, 12),
    )

    def __init__(self):
        # 計時器：每月指定日期觸發
        self.add_timer(
            when=bt.Timer.SESSION_START,
            monthdays=[self.params.investment_day],
        )
        self.total_contributed = 0.0
        self.total_cost = 0.0

    def log(self, msg):
        dt_str = self.data.datetime.date(0).isoformat()
        print(f"{dt_str} {msg}")

    def notify_order(self, order):
        if order.status == order.Completed:
            cost = order.executed.value + order.executed.comm
            self.total_cost += cost
            self.log(
                f"成交，買入 {order.executed.size} 股，均價 {order.executed.price:.2f}，成本 {cost:.2f}"
            )

    def notify_timer(self, timer, when, *args, **kwargs):
        today = self.data.datetime.date(0)
        if not (self.params.start_date <= today <= self.params.end_date):
            return

        # 每月投入現金，剩餘現金會自動累積
        self.broker.add_cash(self.params.investment_amount)
        self.total_contributed += self.params.investment_amount

        price = self.data.close[0]
        size = int(self.params.investment_amount // price)
        if size <= 0:
            self.log("當日股價過高，當月暫不買入（留存現金）")
            return

        self.buy(size=size)

    def stop(self):
        position = self.getposition(self.data)
        market_value = position.size * self.data.close[0]
        portfolio_value = self.broker.getvalue()
        self.log(
            f"總投入現金 {self.total_contributed:.0f}，實際買入成本 {self.total_cost:.2f}，"
            f"持有股數 {position.size:.0f}，市值 {market_value:.2f}，"
            f"帳戶總值 {portfolio_value:.2f}"
        )


def run():
    symbol = "0050.TW"
    start = "2020-01-01"
    end = "2025-12-12"

    # 下載 0050 價格，若已經有本地檔可自行替換掉下載部分
    df = yf.download(symbol, start=start, end=end)
    if df.empty:
        raise SystemExit("下載不到 0050 資料，請確認網路或資料源。")

    df = df.dropna()
    data_feed = bt.feeds.PandasData(dataname=df)

    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(MonthlyDCA)
    cerebro.broker.setcash(0)  # 從零開始，每月投入現金
    cerebro.broker.setcommission(commission=0.0015)

    cerebro.run()
    cerebro.plot(style="candlestick")


if __name__ == "__main__":
    run()
