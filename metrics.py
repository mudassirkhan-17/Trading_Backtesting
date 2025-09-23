import pandas as pd
import numpy as np

def calculate_drawdown(returns):
    """Calculate drawdown from returns series"""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown

def calculate_volatility(returns):
    """Calculate annualized volatility"""
    if len(returns) == 0:
        return 0
    return returns.std() * np.sqrt(252)

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate Sharpe ratio"""
    if len(returns) == 0:
        return 0
    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
    if excess_returns.std() == 0:
        return 0
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

def calculate_max_drawdown(returns):
    """Calculate maximum drawdown"""
    if len(returns) == 0:
        return 0
    drawdown = calculate_drawdown(returns)
    return drawdown.min()

def calculate_calmar_ratio(returns):
    """Calculate Calmar ratio (annual return / max drawdown)"""
    if len(returns) == 0:
        return 0
    annual_return = returns.mean() * 252
    max_dd = abs(calculate_max_drawdown(returns))
    return annual_return / max_dd if max_dd != 0 else 0

def calculate_win_rate(trades):
    """Calculate win rate from trades"""
    if not trades:
        return 0
    profitable_trades = sum(1 for trade in trades if trade.get('profit', 0) > 0)
    return profitable_trades / len(trades)

def calculate_profit_factor(trades):
    """Calculate profit factor"""
    if len(trades) == 0:
        return 0
    
    gross_profit = sum(trade.get('profit', 0) for trade in trades if trade.get('profit', 0) > 0)
    gross_loss = abs(sum(trade.get('profit', 0) for trade in trades if trade.get('profit', 0) < 0))
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0
    
    return gross_profit / gross_loss

def calculate_annual_return(initial_value, final_value, years):
    """Calculate annualized return"""
    if initial_value == 0 or years == 0:
        return 0
    return (final_value / initial_value) ** (1/years) - 1

def calculate_cumulative_return(initial_value, final_value):
    """Calculate cumulative return"""
    if initial_value == 0:
        return 0
    return (final_value - initial_value) / initial_value

def calculate_advanced_metrics(portfolio, data, trades):
    """Calculate comprehensive trading metrics"""
    if len(data) == 0:
        return {}
    
    # Calculate returns
    portfolio_values = data['Portfolio_Value'].dropna()
    if len(portfolio_values) < 2:
        return {}
    
    returns = portfolio_values.pct_change().dropna()
    
    # Basic metrics
    total_return = calculate_cumulative_return(portfolio_values.iloc[0], portfolio_values.iloc[-1])
    
    # Calculate actual years from data
    if len(data) > 1:
        # Estimate years from the data length (assuming daily data)
        years = len(portfolio_values) / 252  # 252 trading days per year
    else:
        years = 1
    
    annual_return = calculate_annual_return(portfolio_values.iloc[0], portfolio_values.iloc[-1], years)
    volatility = calculate_volatility(returns)
    sharpe_ratio = calculate_sharpe_ratio(returns)
    max_drawdown = calculate_max_drawdown(portfolio_values)
    
    # Trade-based metrics
    win_rate = calculate_win_rate(trades)
    profit_factor = calculate_profit_factor(trades)
    
    return {
        'total_return': total_return,
        'cumulative_return': total_return * 100,  # Convert to percentage
        'annual_return': annual_return * 100,  # Convert to percentage
        'volatility': volatility * 100,  # Convert to percentage
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown * 100,  # Convert to percentage
        'win_rate': win_rate * 100,  # Convert to percentage
        'profit_factor': profit_factor,
        'total_trades': len(trades),
        'years_traded': years,
        'trading_days': len(portfolio_values)
    }
