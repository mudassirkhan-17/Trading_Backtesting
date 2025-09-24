"""
Display Functions Module
Handles all output formatting and result display for trading strategies
"""

def display_financial_summary(performance):
    """Display financial summary with advanced metrics"""
    print(f"\n💰 FINANCIAL SUMMARY:")
    print(f"Initial Investment: ${performance['initial_cash']:.2f}")
    print(f"Final Portfolio Value: ${performance['current_value']:.2f}")
    print(f"Total Return: ${performance['total_return']:.2f}")
    print(f"Return Percentage: {performance['return_pct']:.2f}%")
    print(f"Total Trades: {performance['total_trades']}")
    
    # Display advanced metrics if available
    if 'annual_return' in performance:
        print(f"\n📊 ADVANCED PERFORMANCE METRICS:")
        print(f"Annual Return: {performance.get('annual_return', 0):.2f}%")
        print(f"Cumulative Return: {performance.get('cumulative_return', performance.get('total_return', 0) * 100):.2f}%")
        print(f"Sharpe Ratio: {performance.get('sharpe_ratio', 0):.3f}")
        print(f"Volatility: {performance.get('volatility', 0):.2f}%")
        print(f"Max Drawdown: {performance.get('max_drawdown', 0):.2f}%")
        print(f"Win Rate: {performance.get('win_rate', 0):.1f}%")
        print(f"Profit Factor: {performance.get('profit_factor', 0):.2f}")
        if 'years_traded' in performance and 'trading_days' in performance:
            print(f"Trading Period: {performance['years_traded']:.2f} years ({performance['trading_days']} days)")

def display_advanced_metrics_summary(ticker_performance):
    """Display advanced metrics summary for multi-ticker portfolios"""
    if not ticker_performance:
        return
    
    # Calculate combined advanced metrics
    all_volatilities = [p.get('volatility', 0) for p in ticker_performance.values() if 'volatility' in p]
    all_sharpe_ratios = [p.get('sharpe_ratio', 0) for p in ticker_performance.values() if 'sharpe_ratio' in p]
    all_max_drawdowns = [p.get('max_drawdown', 0) for p in ticker_performance.values() if 'max_drawdown' in p]
    
    if all_volatilities:
        avg_volatility = sum(all_volatilities) / len(all_volatilities)
        avg_sharpe = sum(all_sharpe_ratios) / len(all_sharpe_ratios) if all_sharpe_ratios else 0
        max_drawdown = max(all_max_drawdowns) if all_max_drawdowns else 0
        
        print(f"\n📊 COMBINED ADVANCED METRICS:")
        print(f"  Average Volatility: {avg_volatility:.2f}%")
        print(f"  Average Sharpe Ratio: {avg_sharpe:.3f}")
        print(f"  Maximum Drawdown: {max_drawdown:.2f}%")

def display_current_position(performance, final_price):
    """Display current position"""
    print(f"\n📊 CURRENT POSITION:")
    print(f"Cash: ${performance['cash']:.2f}")
    print(f"Shares: {performance['shares']:.4f}")
    print(f"Current Price: ${final_price:.2f}")

def display_trade_history(portfolio):
    """Display trade history"""
    if portfolio.trades:
        print(f"\n📈 TRADE HISTORY:")
        print(f"{'Date':<12} {'Action':<6} {'Price':<8} {'Shares':<10} {'Value':<10} {'Cash':<10}")
        print("-" * 70)
        for trade in portfolio.trades:
            # Handle different trade types
            if trade['action'] in ['BUY', 'LONG', 'SHORT']:
                value = trade['cost']
            elif trade['action'] in ['SELL', 'EXIT_LONG']:
                value = trade.get('proceeds', trade.get('cost', 0))
            elif trade['action'] == 'EXIT_SHORT':
                value = trade['cost']
            else:
                value = trade.get('proceeds', trade.get('cost', 0))
            print(f"{trade['date']:<12} {trade['action']:<6} ${trade['price']:<7.2f} {trade['shares']:<10.4f} ${value:<9.2f} ${trade['cash_remaining']:<9.2f}")

def display_strategy_performance(data, entry_col1, entry_col2, exit_col1, exit_col2):
    """Display strategy performance"""
    print(f"\n📋 STRATEGY PERFORMANCE:")
    columns = ['Date', 'Close', entry_col1, entry_col2, exit_col1, exit_col2,
              'Position', 'Action', 'Portfolio_Value']
    print(data[columns].tail(10).to_string(index=False))

def display_results(ticker, data, portfolio, entry_comp1_name, entry_comp2_name, 
                   exit_comp1_name, exit_comp2_name, entry_strategy, exit_strategy,
                   entry_col1, entry_col2, exit_col1, exit_col2):
    """Display comprehensive results and performance report"""
    final_price = data['Close'].iloc[-1]
    performance = portfolio.get_performance(final_price, data)

    # Display results
    print(f"\n{'='*60}")
    print(f"PORTFOLIO PERFORMANCE REPORT - {ticker}")
    print(f"{'='*60}")
    print(f"Entry Strategy: {entry_comp1_name} vs {entry_comp2_name} - {entry_strategy}")
    print(f"Exit Strategy: {exit_comp1_name} vs {exit_comp2_name} - {exit_strategy}")
    print(f"{'='*60}")

    display_financial_summary(performance)
    display_current_position(performance, final_price)
    display_trade_history(portfolio)
    display_strategy_performance(data, entry_col1, entry_col2, exit_col1, exit_col2)

    print(f"\n{'='*60}")
    if performance['return_pct'] > 0:
        print(f"🎉 PROFIT! You made ${performance['total_return']:.2f} ({performance['return_pct']:.2f}%)")
    else:
        print(f"📉 LOSS! You lost ${abs(performance['total_return']):.2f} ({abs(performance['return_pct']):.2f}%)")
    print(f"{'='*60}")
