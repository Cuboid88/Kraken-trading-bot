import fng_data
import pandas as pd
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed

def align_datasets(btc_prices, fng_data_list, n_days=1000):
    btc_prices['Date'] = pd.to_datetime(btc_prices['Date']).dt.normalize()
    fng_df = pd.DataFrame(fng_data_list)
    fng_df['Date'] = pd.to_datetime(fng_df['timestamp'], unit='s').dt.normalize()
    common_start = max(btc_prices['Date'].min(), fng_df['Date'].min())
    btc_filtered = btc_prices[btc_prices['Date'] >= common_start].copy()
    fng_filtered = fng_df[fng_df['Date'] >= common_start].copy()
    merged = pd.merge(btc_filtered, fng_filtered, on='Date', how='inner').sort_values(by='Date').head(n_days)
    aligned_btc = merged[['Date', 'Close_BTC']].reset_index(drop=True)
    aligned_fng = merged[['Date', 'value', 'value_classification']].reset_index(drop=True)
    return aligned_btc, aligned_fng

def backtrace(btc_prices, fng_data, buy_threshold, sell_threshold):
    btc_holdings, open_investment = 0.0, 0.0
    completed_invested, completed_realised = 0.0, 0.0
    buy_signals, sell_signals = [], []

    for i in range(len(btc_prices)):
        price = btc_prices.iloc[i]['Close_BTC']
        current_date = btc_prices.iloc[i]['Date']
        fng_value = float(fng_data.iloc[i]['value'])

        if fng_value < buy_threshold:
            btc_bought = 5 / price
            btc_holdings += btc_bought
            open_investment += 5
            buy_signals.append((current_date, price))
        elif fng_value > sell_threshold and btc_holdings > 0:
            proceeds = btc_holdings * price
            completed_invested += open_investment
            completed_realised += proceeds
            sell_signals.append((current_date, price))
            btc_holdings, open_investment = 0.0, 0.0

    remaining_value = btc_holdings * btc_prices.iloc[-1]['Close_BTC'] if btc_holdings > 0 else 0.0
    profit_loss = completed_realised - completed_invested
    return profit_loss, buy_signals, sell_signals, completed_invested, completed_realised, remaining_value

def visualise(btc_prices, buy_signals, sell_signals):
    plt.figure(figsize=(14, 7))
    plt.plot(btc_prices['Date'], btc_prices['Close_BTC'], label='BTC Price', color='blue')
    if buy_signals:
        buy_dates, buy_prices = zip(*buy_signals)
        plt.scatter(buy_dates, buy_prices, marker='o', color='green', s=100, label='Buy')
    if sell_signals:
        sell_dates, sell_prices = zip(*sell_signals)
        plt.scatter(sell_dates, sell_prices, marker='o', color='red', s=100, label='Sell')
    plt.xlabel('Date')
    plt.ylabel('BTC Close Price (USD)')
    plt.title('BTC Price with Buy/Sell Signals from FNG Strategy')
    plt.legend()
    plt.show()

def evaluate_strategy(args):
    buy, sell, aligned_btc, aligned_fng = args
    return backtrace(aligned_btc, aligned_fng, buy, sell), buy, sell

if __name__ == "__main__":
    fng_data_list = fng_data.fetch_fng_data()
    btc_df = pd.read_csv('extracted_closing_prices.csv', parse_dates=['Date'], dayfirst=True)
    aligned_btc, aligned_fng = align_datasets(btc_df, fng_data_list, n_days=2500)

    thresholds = [(buy, sell, aligned_btc, aligned_fng) for buy in range(10, 30) for sell in range(75, 90)]

    results = []
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(evaluate_strategy, args): args for args in thresholds}
        for i, future in enumerate(as_completed(futures), 1):
            results.append(future.result())
            if i % 10 == 0:
                print(f"Processed {i}/{len(thresholds)} strategies...")

    best_result, buy_threshold, sell_threshold = max(results, key=lambda x: x[0][0])
    profit_loss, buy_signals, sell_signals, completed_invested, completed_realised, remaining_value = best_result

    print("Profit/Loss for Completed Trades: ${:.2f}".format(profit_loss))
    print("Total Invested (completed trades only): ${:.2f}".format(completed_invested))
    print("Total Realised (completed trades only): ${:.2f}".format(completed_realised))
    print("Remaining Value (unsold holdings, not factored in P/L): ${:.2f}".format(remaining_value))
    print("Buy Threshold: {}".format(buy_threshold))
    print("Sell Threshold: {}".format(sell_threshold))

    visualise(aligned_btc, buy_signals, sell_signals)
