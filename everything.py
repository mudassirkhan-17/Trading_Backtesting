import yfinance as yf
import pandas as pd
import numpy as np

def sma_crossover(symbol='AAPL', short_period=20, long_period=25, period='1y', interval='1h'):
    """
    Simple SMA Crossover Strategy
    
    Entry: When short SMA crosses above long SMA
    Exit: When short SMA crosses below long SMA
    """
    
    # Fetch data
    print(f"Fetching {symbol} data...")
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period, interval=interval)
    
    if data.empty:
        print("No data found!")
        return None
    
    print(f"Data fetched: {len(data)} records")
    
    # Calculate SMAs
    data[f'SMA_{short_period}'] = data['Close'].rolling(window=short_period).mean()
    data[f'SMA_{long_period}'] = data['Close'].rolling(window=long_period).mean()
    
    # Generate signals
    data['Signal'] = 0
    
    for i in range(1, len(data)):
        # Bullish crossover (BUY)
        if (data[f'SMA_{short_period}'].iloc[i] > data[f'SMA_{long_period}'].iloc[i] and
            data[f'SMA_{short_period}'].iloc[i-1] <= data[f'SMA_{long_period}'].iloc[i-1]):
            data['Signal'].iloc[i] = 1
            
        # Bearish crossover (SELL)
        elif (data[f'SMA_{short_period}'].iloc[i] < data[f'SMA_{long_period}'].iloc[i] and
              data[f'SMA_{short_period}'].iloc[i-1] >= data[f'SMA_{long_period}'].iloc[i-1]):
            data['Signal'].iloc[i] = -1
    
    # Calculate returns
    initial_capital = 10000
    capital = initial_capital
    position = 0
    trades = []
    
    for i, (date, row) in enumerate(data.iterrows()):
        if row['Signal'] == 1 and position == 0:  # Buy
            position = 1
            shares = capital / row['Close']
            capital = 0
            print(f"BUY: {date.strftime('%Y-%m-%d %H:%M')} at ${row['Close']:.2f}")
            
        elif row['Signal'] == -1 and position == 1:  # Sell
            position = 0
            capital = shares * row['Close']
            pnl = capital - initial_capital
            pnl_pct = (pnl / initial_capital) * 100
            
            trades.append({
                'entry_date': data.index[i-1] if i > 0 else date,
                'exit_date': date,
                'entry_price': data['Close'].iloc[i-1] if i > 0 else row['Close'],
                'exit_price': row['Close'],
                'pnl': pnl,
                'pnl_pct': pnl_pct
            })
            
            print(f"SELL: {date.strftime('%Y-%m-%d %H:%M')} at ${row['Close']:.2f} | P&L: ${pnl:.2f} ({pnl_pct:.2f}%)")
    
    # Final position
    if position == 1:
        final_price = data['Close'].iloc[-1]
        capital = shares * final_price
        print(f"FINAL: Still holding at ${final_price:.2f}")
    
    # Calculate cumulative returns and metrics
    data['Cumulative_Return'] = (data['Close'] / data['Close'].iloc[0] - 1) * 100
    
    # Strategy cumulative return
    data['Strategy_Return'] = 0.0
    data['Strategy_Value'] = initial_capital
    current_value = initial_capital
    current_shares = 0
    
    for i, (date, row) in enumerate(data.iterrows()):
        if row['Signal'] == 1 and current_shares == 0:  # Buy
            current_shares = current_value / row['Close']
            current_value = 0
        elif row['Signal'] == -1 and current_shares > 0:  # Sell
            current_value = current_shares * row['Close']
            current_shares = 0
        
        # Update strategy value
        if current_shares > 0:
            data['Strategy_Value'].iloc[i] = current_shares * row['Close']
        else:
            data['Strategy_Value'].iloc[i] = current_value
            
        data['Strategy_Return'].iloc[i] = (data['Strategy_Value'].iloc[i] / initial_capital - 1) * 100
    
    # Final results
    total_return = (capital - initial_capital) / initial_capital * 100
    buy_hold_return = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0] * 100
    max_return = data['Strategy_Return'].max()
    min_return = data['Strategy_Return'].min()
    
    # Calculate additional metrics
    if len(trades) > 0:
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] < 0]
        
        win_rate = len(winning_trades) / len(trades) * 100
        avg_win = np.mean([t['pnl_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl_pct'] for t in losing_trades]) if losing_trades else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Calculate drawdown
        peak = data['Strategy_Value'].expanding().max()
        drawdown = (data['Strategy_Value'] - peak) / peak * 100
        max_drawdown = drawdown.min()
        
        # Calculate Sharpe ratio (simplified)
        returns = data['Strategy_Return'].diff().dropna()
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else 0
    else:
        win_rate = 0
        avg_win = 0
        avg_loss = 0
        profit_factor = 0
        max_drawdown = 0
        sharpe_ratio = 0
    
    print(f"\n" + "="*60)
    print("COMPREHENSIVE PERFORMANCE METRICS")
    print("="*60)
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Value: ${capital:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Buy & Hold Return: {buy_hold_return:.2f}%")
    print(f"Outperformance: {total_return - buy_hold_return:.2f}%")
    print(f"Max Return: {max_return:.2f}%")
    print(f"Min Return: {min_return:.2f}%")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"\nTRADE METRICS:")
    print(f"Total Trades: {len(trades)}")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Average Win: {avg_win:.2f}%")
    print(f"Average Loss: {avg_loss:.2f}%")
    print(f"Profit Factor: {profit_factor:.2f}")
    
    return data, trades

# Run the strategy
if __name__ == "__main__":
    data, trades = sma_crossover('AAPL', 25, 20, '1y', '1h')
