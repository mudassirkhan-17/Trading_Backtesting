from indicators import *
from metrics import *
from display import *
from comparisons import *
from inputs import *
# Removed circular import - functions will be passed as parameters


""" This files contains three classes:
1. Portfolio --> Single Ticker Portfolio
2. MultiTickerPortfolio
3. MultiTickerMultiStrategyPortfolio
"""
"""the portfolio class is the main class that is used to manage the portfolio and the trades"""
"""the MultiTickerPortfolio class is used to manage the portfolio and the trades for multiple tickers"""
"""the MultiTickerMultiStrategyPortfolio class is used to manage the portfolio and the trades for multiple tickers with different strategies"""


"""buy and enter long are same thing"""
"""sell and exit long are same thing"""

"""just calculating basic things, long --> buy stocks so number of stocks, 
short --> sell stocks so number of cash then matrices, positions, risk management orders,
 trailing stop, etc."""

class Portfolio:

    
    """set_stop_loss, set_take_profit, clear_orders, set_trailing_stop, update_trailing_stop,
     clear_trailing_stop, check_risk_orders, buy, sell, enter_long, enter_short, 
     get_portfolio_value, get_performance, set_trade_size_percentage"""

    
    def __init__(self, initial_cash=100, trade_size_percentage=100, trade_size_dollars=None, trade_type="percentage"):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.shares = 0
        self.entry_price = 0
        self.entry_date = None
        self.trades = []
        self.portfolio_value = []
        self.trade_size_percentage = trade_size_percentage  # Percentage of cash to use per trade
        self.trade_size_dollars = trade_size_dollars  # Dollar amount to use per trade
        self.trade_type = trade_type  # "percentage" or "dollars"
        self.available_cash = initial_cash  # Cash available for new trades
        
        # Risk management orders
        self.stop_loss_percentage = None  # Stop loss as percentage (e.g., 5.0 for 5%)
        self.take_profit_percentage = None  # Take profit as percentage (e.g., 10.0 for 10%)
        self.stop_loss_dollars = None  # Stop loss as dollar amount
        self.take_profit_dollars = None  # Take profit as dollar amount
        self.position_value = 0  # Current value of position
        self.orders_active = False  # Whether stop/take-profit orders are active
        
        # Trailing stop loss attributes
        self.trailing_stop_percentage = None  # Trailing stop as percentage
        self.trailing_stop_dollars = None  # Trailing stop as dollar amount
        self.highest_price = 0  # Track highest price since entry
        self.trailing_stop_price = 0  # Current trailing stop level
        self.trailing_stop_active = False  # Whether trailing stop is active
        
        # Long/Short position tracking
        self.long_shares = 0      # Positive: shares owned (long position)
        self.short_shares = 0     # Negative: shares shorted (short position)
        self.position = "OUT"     # "OUT", "LONG", "SHORT"
        self.margin_used = 0      # Cash used as margin for shorting

    """set_stop_loss doesnt do anything it just sets the stop_loss_percentage or stop_loss_dollars
    method is just a placeholder for the risk management orders""" 

    def set_stop_loss(self, percentage=None, dollars=None):
        """Set stop-loss order (percentage or dollar amount)"""
        if percentage is not None:
            self.stop_loss_percentage = abs(percentage)  # Always positive
            self.stop_loss_dollars = None
        elif dollars is not None:
            self.stop_loss_dollars = abs(dollars)  # Always positive
            self.stop_loss_percentage = None
        else:
            raise ValueError("Must specify either percentage or dollars")
    
    """set_take_profit doesnt do anything it just sets the take_profit_percentage or take_profit_dollars
    method is just a placeholder for the risk management orders""" 

    def set_take_profit(self, percentage=None, dollars=None):
        """Set take-profit order (percentage or dollar amount)"""
        if percentage is not None:
            self.take_profit_percentage = abs(percentage)  # Always positive
            self.take_profit_dollars = None
        elif dollars is not None:
            self.take_profit_dollars = abs(dollars)  # Always positive
            self.take_profit_percentage = None
        else:
            raise ValueError("Must specify either percentage or dollars")
    
    """clear_orders doesnt do anything it just clears the stop_loss_percentage, take_profit_percentage,
    stop_loss_dollars, take_profit_dollars, and orders_active""" 
    def clear_orders(self):
        """Clear all stop-loss and take-profit orders"""
        self.stop_loss_percentage = None
        self.take_profit_percentage = None
        self.stop_loss_dollars = None
        self.take_profit_dollars = None
        self.orders_active = False
    
    """set_trailing_stop doesnt do anything it just sets the trailing_stop_percentage or trailing_stop_dollars
    method is just a placeholder for the risk management orders""" 

    def set_trailing_stop(self, percentage=None, dollars=None):
        """Set trailing stop-loss order (percentage or dollar amount)"""
        if percentage is not None:
            self.trailing_stop_percentage = abs(percentage)  # Always positive
            self.trailing_stop_dollars = None
        elif dollars is not None:
            self.trailing_stop_dollars = abs(dollars)  # Always positive
            self.trailing_stop_percentage = None
        else:
            raise ValueError("Must specify either percentage or dollars")
        
        self.trailing_stop_active = True
        print(f"✅ Trailing stop set: {percentage}%" if percentage else f"✅ Trailing stop set: ${dollars}")
    
    """update_trailing_stop doesnt do anything it just updates the trailing_stop_price based on the current_price
    method is just a placeholder for the risk management orders""" 

    def update_trailing_stop(self, current_price):
        """Update trailing stop and check if triggered"""
        # Check if we have a position to manage
        has_position = False
        if self.position == "LONG" and self.long_shares > 0:
            has_position = True
        elif self.position == "SHORT" and self.short_shares < 0:
            has_position = True
        elif self.shares > 0:  # Legacy support
            has_position = True
        
        if not self.trailing_stop_active or not has_position:
            return None
        
        if self.position == "LONG":
            # For long positions: track highest price, stop below
            if current_price > self.highest_price:
                self.highest_price = current_price
                
                # Calculate new trailing stop level
                if self.trailing_stop_percentage:
                    self.trailing_stop_price = self.highest_price * (1 - self.trailing_stop_percentage/100)
                else:  # dollars
                    self.trailing_stop_price = self.highest_price - self.trailing_stop_dollars
                
                print(f"📈 Trailing stop updated: Highest=${self.highest_price:.2f}, Stop=${self.trailing_stop_price:.2f}")
            
            # Check if current price triggered trailing stop
            if current_price <= self.trailing_stop_price:
                return "trailing_stop_triggered"
                
        elif self.position == "SHORT":
            # For short positions: track lowest price, stop above
            if current_price < self.highest_price:  # Using highest_price to track lowest for short
                self.highest_price = current_price
                
                # Calculate new trailing stop level (above current price for short)
                if self.trailing_stop_percentage:
                    self.trailing_stop_price = self.highest_price * (1 + self.trailing_stop_percentage/100)
                else:  # dollars
                    self.trailing_stop_price = self.highest_price + self.trailing_stop_dollars
                
                print(f"📉 Trailing stop updated: Lowest=${self.highest_price:.2f}, Stop=${self.trailing_stop_price:.2f}")
            
            # Check if current price triggered trailing stop
            if current_price >= self.trailing_stop_price:
                return "trailing_stop_triggered"
        
        return None
    
    """clear_trailing_stop doesnt do anything it just clears the trailing_stop_percentage, trailing_stop_dollars,
    highest_price, trailing_stop_price, and trailing_stop_active""" 

    def clear_trailing_stop(self):
        """Clear trailing stop order"""
        self.trailing_stop_percentage = None
        self.trailing_stop_dollars = None
        self.highest_price = 0
        self.trailing_stop_price = 0
        self.trailing_stop_active = False
    
    """check_risk_orders doesnt do anything it just checks if the stop_loss_percentage or stop_loss_dollars
    or take_profit_percentage or take_profit_dollars is triggered based on the current_price and current_date""" 
    def check_risk_orders(self, current_price, current_date):
        """Check if stop-loss or take-profit orders should be triggered"""
        if not self.orders_active or self.entry_price == 0:
            return None, None  # No active position or orders
        
        # Check if we have a position to manage
        has_position = False
        if self.position == "LONG" and self.long_shares > 0:
            has_position = True
        elif self.position == "SHORT" and self.short_shares < 0:
            has_position = True
        elif self.shares > 0:  # Legacy support
            has_position = True
        
        if not has_position:
            return None, None
        
        # Calculate current P&L based on position type
        if self.position == "LONG":
            pnl_dollars = (current_price - self.entry_price) * self.long_shares
            pnl_percentage = (current_price - self.entry_price) / self.entry_price * 100
        elif self.position == "SHORT":
            # For short: profit when price goes down
            pnl_dollars = (self.entry_price - current_price) * abs(self.short_shares)
            pnl_percentage = (self.entry_price - current_price) / self.entry_price * 100
        else:  # Legacy long position
            pnl_dollars = (current_price - self.entry_price) * self.shares
            pnl_percentage = (current_price - self.entry_price) / self.entry_price * 100
        
        # Check stop-loss
        stop_loss_triggered = False
        stop_loss_reason = ""
        
        if self.stop_loss_percentage is not None and pnl_percentage <= -self.stop_loss_percentage:
            stop_loss_triggered = True
            stop_loss_reason = f"Stop-loss triggered: {pnl_percentage:.2f}% <= -{self.stop_loss_percentage}%"
        elif self.stop_loss_dollars is not None and pnl_dollars <= -self.stop_loss_dollars:
            stop_loss_triggered = True
            stop_loss_reason = f"Stop-loss triggered: ${pnl_dollars:.2f} <= -${self.stop_loss_dollars}"
        
        # Check take-profit
        take_profit_triggered = False
        take_profit_reason = ""
        
        if self.take_profit_percentage is not None and pnl_percentage >= self.take_profit_percentage:
            take_profit_triggered = True
            take_profit_reason = f"Take-profit triggered: {pnl_percentage:.2f}% >= {self.take_profit_percentage}%"
        elif self.take_profit_dollars is not None and pnl_dollars >= self.take_profit_dollars:
            take_profit_triggered = True
            take_profit_reason = f"Take-profit triggered: ${pnl_dollars:.2f} >= ${self.take_profit_dollars}"
        
        # Return the first triggered order (stop-loss has priority)
        if stop_loss_triggered:
            return "EXIT", stop_loss_reason
        elif take_profit_triggered:
            return "EXIT", take_profit_reason
        else:
            return None, None
        
    """Calculate the trade amount and then just buys the shares and hold it"""  
    def buy(self, price, date, shares_to_buy=None):
        """Execute buy order with position sizing"""
        if shares_to_buy is None:
            # Calculate position size based on trade type
            if self.trade_type == "dollars" and self.trade_size_dollars is not None:
                # Dollar-based trading
                trade_amount = min(self.trade_size_dollars, self.available_cash)
            else:
                # Percentage-based trading (default)
                trade_amount = self.available_cash * (self.trade_size_percentage / 100)
            
            shares_to_buy = trade_amount / price
        
        cost = shares_to_buy * price
        if cost <= self.available_cash:
            self.shares += shares_to_buy
            self.long_shares = shares_to_buy  # Set long shares for long/short system
            self.short_shares = 0  # Clear any short shares
            self.position = "LONG"  # Set position to LONG
            self.cash -= cost
            self.available_cash -= cost  # Reduce available cash for future trades
            self.entry_price = price
            self.entry_date = date
            self.orders_active = True  # Activate risk management orders
            
            # Initialize trailing stop tracking
            if self.trailing_stop_active:
                self.highest_price = price
                if self.trailing_stop_percentage:
                    self.trailing_stop_price = price * (1 - self.trailing_stop_percentage/100)
                else:
                    self.trailing_stop_price = price - self.trailing_stop_dollars
                print(f"🎯 Trailing stop initialized: Entry=${price:.2f}, Stop=${self.trailing_stop_price:.2f}")
            self.trades.append({
                'date': date,
                'action': 'BUY',
                'price': price,
                'shares': shares_to_buy,
                'cost': cost,
                'cash_remaining': self.cash,
                'available_cash': self.available_cash
            })
            return True
        return False
    
    """It sell the bought shares and add cash into real portfolio""" 
    def sell(self, price, date, reason="Strategy"):
        
        """Execute sell order"""
        if self.shares > 0:
            proceeds = self.shares * price
            self.cash += proceeds
            self.available_cash += proceeds  # Add proceeds back to available cash
            self.trades.append({
                'date': date,
                'action': 'SELL',
                'price': price,
                'shares': self.shares,
                'proceeds': proceeds,
                'cash_remaining': self.cash,
                'available_cash': self.available_cash,
                'reason': reason  # Add reason for the sell
            })
            self.shares = 0
            self.long_shares = 0  # Clear long shares for long/short system
            self.short_shares = 0  # Clear short shares for long/short system
            self.position = "OUT"  # Set position to OUT
            self.entry_price = 0
            self.entry_date = None
            self.orders_active = False  # Deactivate risk management orders
            
            # Clear trailing stop tracking
            self.clear_trailing_stop()
            return True
        return False
    
    """Calculate the trade amount and then just buys the shares and hold it""" 
    def enter_long(self, price, date, shares_to_buy=None):
        """Enter long position (buy shares)"""
        if self.position != "OUT":
            return False  # Can only enter long if currently OUT
        
        if shares_to_buy is None:
            # Calculate position size based on trade type
            if self.trade_type == "dollars" and self.trade_size_dollars is not None:
                trade_amount = min(self.trade_size_dollars, self.available_cash)
            else:
                # Use available cash for 100% trades (this IS the total portfolio value)
                trade_amount = self.available_cash * (self.trade_size_percentage / 100)
            shares_to_buy = trade_amount / price
        
        cost = shares_to_buy * price
        if cost <= self.available_cash:
            self.long_shares = shares_to_buy
            self.short_shares = 0
            self.cash -= cost
            self.available_cash -= cost
            self.position = "LONG"
            self.entry_price = price
            self.entry_date = date
            self.orders_active = True
            self.margin_used = 0
            
            # Initialize trailing stop tracking
            if self.trailing_stop_active:
                self.highest_price = price
                if self.trailing_stop_percentage:
                    self.trailing_stop_price = price * (1 - self.trailing_stop_percentage/100)
                else:
                    self.trailing_stop_price = price - self.trailing_stop_dollars
            
            self.trades.append({
                'date': date,
                'action': 'LONG',
                'price': price,
                'shares': shares_to_buy,
                'cost': cost,
                'cash_remaining': self.cash,
                'available_cash': self.available_cash,
                'position': 'LONG'
            })
            return True
        return False
    
    """It sell the bought shares and add cash into real portfolio""" 
    def enter_short(self, price, date, shares_to_short=None):
        """Enter short position (short shares)"""
        if self.position != "OUT":
            return False  # Can only enter short if currently OUT
        
        if shares_to_short is None:
            # Calculate position size based on trade type
            if self.trade_type == "dollars" and self.trade_size_dollars is not None:
                trade_amount = min(self.trade_size_dollars, self.available_cash)
            else:
                # Use available cash for 100% trades (this IS the total portfolio value)
                trade_amount = self.available_cash * (self.trade_size_percentage / 100)
            shares_to_short = trade_amount / price
        
        # Check if we have enough cash for margin
        margin_required = shares_to_short * price
        if margin_required <= self.available_cash:
            self.short_shares = -shares_to_short  # Negative for short position
            self.long_shares = 0
            # For short selling: use existing cash as margin (no extra cash created)
            # DO NOT add extra cash: self.cash += margin_required  # WRONG!
            self.available_cash -= margin_required  # Reserve as margin
            self.position = "SHORT"
            self.entry_price = price
            self.entry_date = date
            self.orders_active = True
            self.margin_used = margin_required
            
            # Initialize trailing stop tracking for short (track lowest price)
            if self.trailing_stop_active:
                self.highest_price = price  # For short, this tracks entry price
                if self.trailing_stop_percentage:
                    self.trailing_stop_price = price * (1 + self.trailing_stop_percentage/100)
                else:
                    self.trailing_stop_price = price + self.trailing_stop_dollars
            
            self.trades.append({
                'date': date,
                'action': 'SHORT',
                'price': price,
                'shares': -shares_to_short,
                'cost': margin_required,
                'cash_remaining': self.cash,
                'available_cash': self.available_cash,
                'position': 'SHORT'
            })
            return True
        return False
    
    """it just exits the position and add cash into real portfolio"""

    def exit_position(self, price, date, reason="Strategy"):
        """Exit current position (long or short)"""
        if self.position == "LONG" and self.long_shares > 0:
            # Exit long position
            proceeds = self.long_shares * price
            self.cash += proceeds
            self.available_cash += proceeds
            self.trades.append({
                'date': date,
                'action': 'EXIT_LONG',
                'price': price,
                'shares': self.long_shares,
                'proceeds': proceeds,
                'cash_remaining': self.cash,
                'available_cash': self.available_cash,
                'reason': reason,
                'position': 'OUT'
            })
            self.long_shares = 0
            self.position = "OUT"
            self.entry_price = 0
            self.entry_date = None
            self.orders_active = False
            self.margin_used = 0
            self.clear_trailing_stop()
            return True
            
        elif self.position == "SHORT" and self.short_shares < 0:
            # Exit short position (buy back shares)
            shares_to_buy = abs(self.short_shares)
            cost = shares_to_buy * price
            if cost <= self.cash:
                self.cash -= cost
                # After exit, available cash = current cash (no margin to return)
                self.available_cash = self.cash
                self.trades.append({
                    'date': date,
                    'action': 'EXIT_SHORT',
                    'price': price,
                    'shares': shares_to_buy,
                    'cost': cost,
                    'cash_remaining': self.cash,
                    'available_cash': self.available_cash,
                    'reason': reason,
                    'position': 'OUT'
                })
                self.short_shares = 0
                self.position = "OUT"
                self.entry_price = 0
                self.entry_date = None
                self.orders_active = False
                self.margin_used = 0
                self.clear_trailing_stop()
                return True
        return False
    
    """it just calculates the portfolio value based on the current_price"""
    
    """for old system compatibility"""
    def get_portfolio_value(self, current_price):
        """Calculate total portfolio value"""
        # Legacy support for old shares attribute
        legacy_value = self.cash + (self.shares * current_price)
        
        # New long/short calculation
        if self.position == "LONG":
            return self.cash + (self.long_shares * current_price)
        elif self.position == "SHORT":
            # For short: cash + (margin_used + short_profit)
            # short_profit = margin_used + (short_shares * current_price)
            # short_shares is negative, so this gives us the profit/loss
            short_profit = self.margin_used + (self.short_shares * current_price)
            return self.cash + short_profit
        else:  # OUT position
            return self.cash
    
    """it just calculates the performance metrics based on the current_price and data"""

    """Calculate performance metrics including advanced analytics
        
        initial_cash, current_value, total_return, return_pct, cash, shares,
         available_cash, total_trades, trade_size_percentage, advanced_metrics"""

    def get_performance(self, current_price, data=None):

         
        current_value = self.get_portfolio_value(current_price)
        total_return = current_value - self.initial_cash
        return_pct = (total_return / self.initial_cash) * 100
        
        # Basic performance metrics
        basic_metrics = {
            'initial_cash': self.initial_cash,
            'current_value': current_value,
            'total_return': total_return,
            'return_pct': return_pct,
            'cash': self.cash,
            'shares': self.shares,
            'available_cash': self.available_cash,
            'total_trades': len(self.trades),
            'trade_size_percentage': self.trade_size_percentage
        }
        
        # Add advanced metrics if data is provided
        if data is not None:
            advanced_metrics = calculate_advanced_metrics(self, data, self.trades)
            basic_metrics.update(advanced_metrics)
        
        return basic_metrics
    
    """it just sets the trade_size_percentage"""
    
    def set_trade_size_percentage(self, percentage):
        """Set the percentage of available cash to use per trade"""
        if 0 < percentage <= 100:
            self.trade_size_percentage = percentage
        else:
            raise ValueError("Trade size percentage must be between 0 and 100")
    
    # ===== LIQUIDATION METHODS =====
    
    def check_liquidation(self, current_price):
        """Check if portfolio should be liquidated due to losses (100% threshold)"""
        if self.position == "SHORT":
            # Calculate unrealized loss for short position
            # For short: profit when price goes down, loss when price goes up
            # Loss = (current_price - entry_price) * shares (positive when price goes up)
            unrealized_loss = (current_price - self.entry_price) * abs(self.short_shares)
            
            # Check if loss exceeds 100% of margin used
            # 100% liquidation means loss equals 100% of the margin we put up
            if unrealized_loss >= self.margin_used * 1.0:
                return True  # LIQUIDATION TRIGGERED!
        return False
    
    def liquidate_position(self, price, date):
        """Force close position due to liquidation"""
        if self.position == "SHORT":
            # Calculate cost to cover short
            shares_to_buy = abs(self.short_shares)
            cost = shares_to_buy * price
            
            # Check if we have enough cash
            if cost <= self.cash:
                # Force buy back shares
                self.cash -= cost
                # DO NOT return margin - it's gone after liquidation!
                
                # Record liquidation trade
                self.trades.append({
                    'date': date,
                    'action': 'LIQUIDATION',
                    'price': price,
                    'shares': shares_to_buy,
                    'cost': cost,
                    'cash_remaining': self.cash,
                    'available_cash': self.cash,  # Available cash = remaining cash
                    'reason': 'Liquidation - Loss exceeded 100% of available cash',
                    'position': 'OUT'
                })
                
                # Reset position
                self.short_shares = 0
                self.position = "OUT"
                self.entry_price = 0
                self.entry_date = None
                self.orders_active = False
                self.margin_used = 0
                self.clear_trailing_stop()
                
                return True
        return False

"""MultiTickerPortfolio class is used to manage the portfolio and the trades for multiple tickers"""
"""it just sets the trade_size_percentage"""
"""it just sets the trade_size_dollars"""
"""it just sets the trade_type"""
"""it just sets the total_capital"""
"""it just sets the allocations"""
"""it just sets the ticker_capital"""

"""it just adds the ticker to the portfolio
elf.portfolios[ticker] = portfolio  # ← Ticker is the KEY!
self.portfolios = {
    "AAPL": Portfolio(initial_cash=6000, ...),  # ← AAPL portfolio
    "MSFT": Portfolio(initial_cash=4000, ...),  # ← MSFT portfolio
    "GOOGL": Portfolio(initial_cash=2000, ...)  # ← GOOGL portfolio
}
"""

class MultiTickerPortfolio:
    """Portfolio class for managing multiple tickers with allocation percentages and position sizing"""
    
    def __init__(self, total_capital, allocations, trade_size_percentages=None, trade_size_dollars=None, trade_type="percentage"):
        self.total_capital = total_capital
        self.allocations = allocations  # {ticker: percentage}
        self.trade_size_percentages = trade_size_percentages or {}  # {ticker: percentage}
        self.trade_size_dollars = trade_size_dollars or {}  # {ticker: dollar_amount}
        self.trade_type = trade_type  # "percentage" or "dollars"
        self.ticker_capital = {}  # {ticker: allocated_capital}
        self.portfolios = {}  # {ticker: Portfolio}
        self.ticker_data = {}  # {ticker: data}
        self.ticker_performance = {}  # {ticker: performance}
        
        # Calculate allocated capital for each ticker
        for ticker, percentage in self.allocations.items():
            self.ticker_capital[ticker] = (total_capital * percentage) / 100
        
        # Risk management settings for each ticker
        self.ticker_stop_loss = {}  # {ticker: stop_loss_percentage}
        self.ticker_take_profit = {}  # {ticker: take_profit_percentage}
    
    def add_ticker(self, ticker, data, interval):
        """Add a ticker to the portfolio with its data"""
        if ticker not in self.allocations:
            raise ValueError(f"Ticker {ticker} not found in allocations")
        
        # Create portfolio for this ticker
        capital = self.ticker_capital[ticker]
        trade_size_pct = self.trade_size_percentages.get(ticker, 100)
        trade_size_dollars = self.trade_size_dollars.get(ticker)
        
        portfolio = Portfolio(
            initial_cash=capital,
            trade_size_percentage=trade_size_pct,
            trade_size_dollars=trade_size_dollars,
            trade_type=self.trade_type
        )
        
        self.portfolios[ticker] = portfolio
        self.ticker_data[ticker] = data
    
    def set_ticker_risk_management(self, ticker, stop_loss_percentage=None, take_profit_percentage=None, 
                                 stop_loss_dollars=None, take_profit_dollars=None,
                                 trailing_stop_percentage=None, trailing_stop_dollars=None):
        """Set risk management for a specific ticker"""
        if ticker not in self.portfolios:
            raise ValueError(f"Ticker {ticker} not found in portfolio")
        
        if stop_loss_percentage is not None:
            self.ticker_stop_loss[ticker] = stop_loss_percentage
            self.portfolios[ticker].set_stop_loss(percentage=stop_loss_percentage)
        elif stop_loss_dollars is not None:
            self.ticker_stop_loss[ticker] = stop_loss_dollars
            self.portfolios[ticker].set_stop_loss(dollars=stop_loss_dollars)
        
        if take_profit_percentage is not None:
            self.ticker_take_profit[ticker] = take_profit_percentage
            self.portfolios[ticker].set_take_profit(percentage=take_profit_percentage)
        elif take_profit_dollars is not None:
            self.ticker_take_profit[ticker] = take_profit_dollars
            self.portfolios[ticker].set_take_profit(dollars=take_profit_dollars)
        
        if trailing_stop_percentage is not None:
            self.portfolios[ticker].set_trailing_stop(percentage=trailing_stop_percentage)
        elif trailing_stop_dollars is not None:
            self.portfolios[ticker].set_trailing_stop(dollars=trailing_stop_dollars)
    
    def set_all_tickers_risk_management(self, stop_loss_percentage=None, take_profit_percentage=None):
        """Set risk management for all tickers"""
        for ticker in self.portfolios:
            self.set_ticker_risk_management(ticker, stop_loss_percentage, take_profit_percentage)
    
    def get_ticker_data(self, ticker, period, interval):
        """Download data for a specific ticker"""
        data = download_and_prepare_data(ticker, period, interval)
        if data is not None:
            self.ticker_data[ticker] = data
        return data
    
    def run_strategy_on_ticker(self, ticker, period, interval, strategy_config, detect_strategy_signals, execute_trading_strategy, execute_trading_strategy_original):
        """Run strategy on a specific ticker"""
        data = self.get_ticker_data(ticker, period, interval)
        if data is None:
            return None
        
        # Create portfolio for this ticker
        allocated_capital = self.ticker_capital[ticker]
        trade_size = self.trade_size_percentages.get(ticker, 100)
        
        portfolio = Portfolio(
            initial_cash=allocated_capital,
            trade_size_percentage=trade_size,
            trade_type=self.trade_type
        )
        
        # Run the trading strategy
        data, entry_col1, entry_col2, exit_col1, exit_col2 = detect_strategy_signals(
            data,
            strategy_config['entry_comp1_type'], strategy_config['entry_comp1_name'], strategy_config['entry_comp1_params'],  # entry_comp1
            strategy_config['entry_comp2_type'], strategy_config['entry_comp2_name'], strategy_config['entry_comp2_params'],  # entry_comp2
            strategy_config['exit_comp1_type'], strategy_config['exit_comp1_name'], strategy_config['exit_comp1_params'],  # exit_comp1
            strategy_config['exit_comp2_type'], strategy_config['exit_comp2_name'], strategy_config['exit_comp2_params'],  # exit_comp2
            strategy_config['entry_strategy'], strategy_config['exit_strategy'],  # strategies
            strategy_config['entry_comp1_candles_ago'], strategy_config['entry_comp2_candles_ago'], 
            strategy_config['exit_comp1_candles_ago'], strategy_config['exit_comp2_candles_ago']  # candles_ago
        )
        
        # Execute trading strategy based on direction
        strategy_direction = strategy_config.get('strategy_direction', 'Long Only')
        if strategy_direction == "Long/Short Reversal":
            data = execute_trading_strategy(data, portfolio)
        else:
            # For Long Only and Short Only, use the original logic
            data = execute_trading_strategy_original(data, portfolio, strategy_direction)
        
        # Store portfolio and performance
        self.portfolios[ticker] = portfolio
        current_price = data['Close'].iloc[-1] if not data.empty else 0
        self.ticker_performance[ticker] = portfolio.get_performance(current_price)
        
        return data
    
    def get_combined_performance(self):
        """Calculate combined portfolio performance"""
        total_initial = self.total_capital
        total_current = 0
        total_trades = 0
        
        for ticker, portfolio in self.portfolios.items():
            if ticker in self.ticker_performance:   
                performance = self.ticker_performance[ticker]
                total_current += performance['current_value']
                total_trades += performance['total_trades']
            else:
                # If no performance data, use current portfolio value
                if ticker in self.ticker_data and len(self.ticker_data[ticker]) > 0:
                    final_price = self.ticker_data[ticker]['Close'].iloc[-1]
                    portfolio_value = portfolio.get_portfolio_value(final_price)
                    total_current += portfolio_value
                    total_trades += len(portfolio.trades)
        
        total_return = total_current - total_initial
        return_pct = (total_return / total_initial) * 100 if total_initial > 0 else 0
        
        return {
            'total_initial': total_initial,
            'total_current': total_current,
            'total_return': total_return,
            'return_pct': return_pct,
            'total_trades': total_trades
        }
    
    def display_combined_results(self, config):
        """Display combined and individual results for multi-ticker portfolio"""
        combined = self.get_combined_performance()
        
        print("\n" + "="*60)
        print("MULTI-TICKER PORTFOLIO PERFORMANCE REPORT")
        print("="*60)
        
        print("\n📊 PORTFOLIO ALLOCATION:")
        for ticker, percentage in self.allocations.items():
            capital = self.ticker_capital[ticker]
            trade_size = self.trade_size_percentages.get(ticker, 100)
            print(f"  {ticker}: {percentage}% (${capital:,.2f}) - Trade Size: {trade_size}%")
        
        print(f"\n📈 COMBINED PERFORMANCE:")
        print(f"  Initial Capital: ${combined['total_initial']:,.2f}")
        print(f"  Current Value: ${combined['total_current']:,.2f}")
        print(f"  Total Return: ${combined['total_return']:,.2f} ({combined['return_pct']:.2f}%)")
        print(f"  Total Trades: {combined['total_trades']}")
        
        print(f"\n📊 INDIVIDUAL TICKER PERFORMANCE:")
        for ticker, performance in self.ticker_performance.items():
            print(f"  {ticker}: ${performance['current_value']:,.2f} ({performance['return_pct']:.2f}%) - {performance['total_trades']} trades")
        
        print("="*60)

class MultiTickerMultiStrategyPortfolio:
    """Portfolio class for managing multiple tickers with individual strategies"""
    
    def __init__(self, total_capital, allocations, trade_size_percentages=None, ticker_strategies=None, trade_type="percentage", trade_size_dollars=None):
        self.total_capital = total_capital
        self.allocations = allocations  # {ticker: percentage}
        self.trade_size_percentages = trade_size_percentages or {}  # {ticker: percentage}
        self.trade_size_dollars = trade_size_dollars or {}  # {ticker: dollar_amount}
        self.trade_type = trade_type  # "percentage" or "dollars"
        self.ticker_strategies = ticker_strategies or {}  # {ticker: strategy_config}
        self.ticker_capital = {}  # {ticker: allocated_capital}
        self.portfolios = {}  # {ticker: Portfolio}
        self.ticker_data = {}  # {ticker: data}
        self.ticker_performance = {}  # {ticker: performance}
        
        # Risk management settings for each ticker
        self.ticker_stop_loss = {}  # {ticker: stop_loss_percentage}
        self.ticker_take_profit = {}  # {ticker: take_profit_percentage}
        
        # Initialize capital allocation
        for ticker, percentage in self.allocations.items():
            allocated_capital = self.total_capital * (percentage / 100)
            self.ticker_capital[ticker] = allocated_capital
    
    def add_ticker(self, ticker, data, interval):
        """Add a ticker to the portfolio with its data"""
        if ticker not in self.allocations:
            raise ValueError(f"Ticker {ticker} not found in allocations")
        
        # Create portfolio for this ticker
        capital = self.ticker_capital[ticker]
        trade_size_pct = self.trade_size_percentages.get(ticker, 100)
        trade_size_dollars = self.trade_size_dollars.get(ticker)
        
        portfolio = Portfolio(
            initial_cash=capital,
            trade_size_percentage=trade_size_pct,
            trade_size_dollars=trade_size_dollars,
            trade_type=self.trade_type
        )
        
        self.portfolios[ticker] = portfolio
        self.ticker_data[ticker] = data
    
    def set_trade_size_percentage(self, ticker, percentage):
        """Set trade size percentage for a specific ticker"""
        if ticker in self.portfolios:
            self.portfolios[ticker].set_trade_size_percentage(percentage)
            self.trade_size_percentages[ticker] = percentage
        else:
            raise ValueError(f"Ticker {ticker} not found in portfolio")
    
    def set_ticker_strategy(self, ticker, strategy_config):
        """Set strategy configuration for a specific ticker"""
        self.ticker_strategies[ticker] = strategy_config
    
    def set_ticker_risk_management(self, ticker, stop_loss_percentage=None, take_profit_percentage=None, stop_loss_dollars=None, take_profit_dollars=None,
                                 trailing_stop_percentage=None, trailing_stop_dollars=None):
        """Set risk management for a specific ticker"""
        if ticker not in self.portfolios:
            raise ValueError(f"Ticker {ticker} not found in portfolio")
        
        if stop_loss_percentage is not None:
            self.ticker_stop_loss[ticker] = stop_loss_percentage
            self.portfolios[ticker].set_stop_loss(percentage=stop_loss_percentage)
        
        if take_profit_percentage is not None:
            self.ticker_take_profit[ticker] = take_profit_percentage
            self.portfolios[ticker].set_take_profit(percentage=take_profit_percentage)
        
        if stop_loss_dollars is not None:
            self.portfolios[ticker].set_stop_loss(dollars=stop_loss_dollars)
        
        if take_profit_dollars is not None:
            self.portfolios[ticker].set_take_profit(dollars=take_profit_dollars)
        
        if trailing_stop_percentage is not None:
            self.portfolios[ticker].set_trailing_stop(percentage=trailing_stop_percentage)
        
        if trailing_stop_dollars is not None:
            self.portfolios[ticker].set_trailing_stop(dollars=trailing_stop_dollars)
    
    def get_ticker_data(self, ticker, period, interval):
        """Download data for a specific ticker"""
        data = download_and_prepare_data(ticker, period, interval)
        if data is not None:
            self.ticker_data[ticker] = data
        return data
    
    def run_strategy_on_ticker(self, ticker, period, interval, detect_strategy_signals, execute_trading_strategy, execute_trading_strategy_original):
        """Run individual strategy on a specific ticker"""
        if ticker not in self.ticker_strategies:
            print(f"❌ No strategy configured for {ticker}")
            return None
        
        # Download data if not already available
        if ticker not in self.ticker_data:
            data = self.get_ticker_data(ticker, period, interval)
            if data is None:
                return None
        else:
            data = self.ticker_data[ticker]
        
        # Create portfolio for this ticker if it doesn't exist
        if ticker not in self.portfolios:
            allocated_capital = self.ticker_capital[ticker]
            trade_size = self.trade_size_percentages.get(ticker, 100)
            
            self.portfolios[ticker] = Portfolio(
                initial_cash=allocated_capital,
                trade_size_percentage=trade_size,
                trade_type=self.trade_type
            )
        
        portfolio = self.portfolios[ticker]
        strategy_config = self.ticker_strategies[ticker]
        
        if strategy_config['type'] == 'single':
            # Single condition strategy
            data, entry_col1, entry_col2, exit_col1, exit_col2 = detect_strategy_signals(
                data,
                strategy_config['entry_comp1_type'], strategy_config['entry_comp1_name'], strategy_config['entry_comp1_params'],
                strategy_config['entry_comp2_type'], strategy_config['entry_comp2_name'], strategy_config['entry_comp2_params'],
                strategy_config['exit_comp1_type'], strategy_config['exit_comp1_name'], strategy_config['exit_comp1_params'],
                strategy_config['exit_comp2_type'], strategy_config['exit_comp2_name'], strategy_config['exit_comp2_params'],
                strategy_config['entry_strategy'], strategy_config['exit_strategy'],
                strategy_config['entry_comp1_candles_ago'], strategy_config['entry_comp2_candles_ago'],
                strategy_config['exit_comp1_candles_ago'], strategy_config['exit_comp2_candles_ago']
            )
        else:
            # Multi-condition strategy
            data, entry_condition_columns, exit_condition_columns = detect_multi_strategy_signals(
                data, strategy_config['entry_conditions'], strategy_config['exit_conditions'],
                strategy_config['entry_logic'], strategy_config['exit_logic']
            )
        
        # Execute trading strategy based on direction
        strategy_direction = self.ticker_strategies[ticker].get('strategy_direction', 'Long Only')
        if strategy_direction == "Long/Short Reversal":
            data = execute_trading_strategy(data, portfolio)
        else:
            # For Long Only and Short Only, use the original logic
            data = execute_trading_strategy_original(data, portfolio, strategy_direction)
        
        # Store performance
        final_price = data['Close'].iloc[-1]
        performance = portfolio.get_performance(final_price, data)
        self.ticker_performance[ticker] = performance
        
        return data
    
    def get_combined_performance(self):
        """Calculate combined portfolio performance"""
        total_initial = self.total_capital
        total_current = 0
        total_trades = 0
        
        for ticker, performance in self.ticker_performance.items():
            total_current += performance['current_value']
            total_trades += performance['total_trades']
        
        total_return = total_current - total_initial
        return_pct = (total_return / total_initial) * 100
        
        return {
            'total_initial': total_initial,
            'total_current': total_current,
            'total_return': total_return,
            'return_pct': return_pct,
            'total_trades': total_trades,
            'ticker_performance': self.ticker_performance
        }
    
    def display_combined_results(self, period, interval):
        """Display combined and individual results"""
        combined = self.get_combined_performance()
        
        print(f"\n{'='*80}")
        print(f"MULTI-TICKER MULTI-STRATEGY PORTFOLIO PERFORMANCE REPORT")
        print(f"{'='*80}")
        
        # Display allocation breakdown
        print(f"\n📊 PORTFOLIO ALLOCATION:")
        for ticker, percentage in self.allocations.items():
            capital = self.ticker_capital[ticker]
            trade_size = self.trade_size_percentages.get(ticker, 100)
            print(f"  {ticker}: {percentage}% (${capital:,.2f}) - Trade Size: {trade_size}%")
        
        # Display individual strategies
        print(f"\n📈 INDIVIDUAL STRATEGIES:")
        for ticker, strategy_config in self.ticker_strategies.items():
            print(f"\n  {ticker} Strategy:")
            if strategy_config['type'] == 'single':
                print(f"    Entry: {strategy_config['entry_comp1_name']} {strategy_config['entry_strategy']} {strategy_config['entry_comp2_name']}")
                print(f"    Exit: {strategy_config['exit_comp1_name']} {strategy_config['exit_strategy']} {strategy_config['exit_comp2_name']}")
            else:
                print(f"    Entry Logic: {strategy_config['entry_logic']} ({len(strategy_config['entry_conditions'])} conditions)")
                print(f"    Exit Logic: {strategy_config['exit_logic']} ({len(strategy_config['exit_conditions'])} conditions)")
        
        # Display combined performance
        print(f"\n💰 COMBINED PORTFOLIO PERFORMANCE:")
        print(f"  Initial Capital: ${combined['total_initial']:,.2f}")
        print(f"  Current Value: ${combined['total_current']:,.2f}")
        print(f"  Total Return: ${combined['total_return']:,.2f}")
        print(f"  Return Percentage: {combined['return_pct']:.2f}%")
        print(f"  Total Trades: {combined['total_trades']}")
        
        # Display advanced metrics
        display_advanced_metrics_summary(self.ticker_performance)
        
        # Display individual ticker performance
        print(f"\n📋 INDIVIDUAL TICKER PERFORMANCE:")
        print(f"{'Ticker':<8} {'Allocation':<12} {'Trade Size':<12} {'Initial':<12} {'Current':<12} {'Return':<12} {'Return%':<10} {'Trades':<8}")
        print("-" * 90)
        
        for ticker, performance in self.ticker_performance.items():
            allocation = self.allocations[ticker]
            trade_size = self.trade_size_percentages.get(ticker, 100)
            print(f"{ticker:<8} {allocation:>8}% {trade_size:>10}% ${performance['initial_cash']:>10,.0f} ${performance['current_value']:>10,.0f} "
                  f"${performance['total_return']:>10,.0f} {performance['return_pct']:>8.1f}% {performance['total_trades']:>6}")
        
        # Display trade history for each ticker
        print(f"\n📈 TRADE HISTORY BY TICKER:")
        for ticker, portfolio in self.portfolios.items():
            if portfolio.trades:
                print(f"\n{ticker} Trades (Trade Size: {self.trade_size_percentages.get(ticker, 100)}%):")
                print(f"{'Date':<12} {'Action':<6} {'Price':<8} {'Shares':<10} {'Value':<10} {'Cash':<10} {'Available':<10}")
                print("-" * 80)
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
                    print(f"{trade['date']:<12} {trade['action']:<6} ${trade['price']:<7.2f} {trade['shares']:<10.4f} "
                          f"${value:<9.2f} ${trade['cash_remaining']:<9.2f} ${trade['available_cash']:<9.2f}")
        
        print(f"\n{'='*80}")
        if combined['return_pct'] > 0:
            print(f"🎉 COMBINED PROFIT! You made ${combined['total_return']:,.2f} ({combined['return_pct']:.2f}%)")
        else:
            print(f"📉 COMBINED LOSS! You lost ${abs(combined['total_return']):.2f} ({abs(combined['return_pct']):.2f}%)")
        print(f"{'='*80}")
    
    def get_ticker_data(self, ticker, period, interval):
        """Download data for a specific ticker"""
        data = download_and_prepare_data(ticker, period, interval)
        if data is not None:
            self.ticker_data[ticker] = data
        return data
    
    
    def get_combined_performance(self):
        """Calculate combined portfolio performance"""
        total_initial = self.total_capital
        total_current = 0
        total_trades = 0
        
        for ticker, performance in self.ticker_performance.items():
            total_current += performance['current_value']
            total_trades += performance['total_trades']
        
        total_return = total_current - total_initial
        return_pct = (total_return / total_initial) * 100
        
        return {
            'total_initial': total_initial,
            'total_current': total_current,
            'total_return': total_return,
            'return_pct': return_pct,
            'total_trades': total_trades,
            'ticker_performance': self.ticker_performance
        }
    
    def display_combined_results(self, strategy_config):
        """Display combined and individual results"""
        combined = self.get_combined_performance()
        
        print(f"\n{'='*80}")
        print(f"MULTI-TICKER PORTFOLIO PERFORMANCE REPORT")
        print(f"{'='*80}")
        
        # Display allocation breakdown
        print(f"\n📊 PORTFOLIO ALLOCATION:")
        for ticker, percentage in self.allocations.items():
            capital = self.ticker_capital[ticker]
            trade_size = self.trade_size_percentages.get(ticker, 100)
            print(f"  {ticker}: {percentage}% (${capital:,.2f}) - Trade Size: {trade_size}%")
        
        # Display strategies for each ticker
        print(f"\n📈 INDIVIDUAL TICKER STRATEGIES:")
        for ticker, ticker_strategy in self.ticker_strategies.items():
            if ticker_strategy['type'] == 'single':
                print(f"  {ticker}: {ticker_strategy['entry_comp1_name']} {ticker_strategy['entry_strategy']} {ticker_strategy['entry_comp2_name']} | {ticker_strategy['exit_comp1_name']} {ticker_strategy['exit_strategy']} {ticker_strategy['exit_comp2_name']}")
            else:
                print(f"  {ticker}: Multi-condition strategy")
        
        # Display combined performance
        print(f"\n💰 COMBINED PORTFOLIO PERFORMANCE:")
        print(f"  Initial Capital: ${combined['total_initial']:,.2f}")
        print(f"  Current Value: ${combined['total_current']:,.2f}")
        print(f"  Total Return: ${combined['total_return']:,.2f}")
        print(f"  Return Percentage: {combined['return_pct']:.2f}%")
        print(f"  Total Trades: {combined['total_trades']}")
        
        # Display advanced metrics
        display_advanced_metrics_summary(self.ticker_performance)
        
        # Display individual ticker performance
        print(f"\n📋 INDIVIDUAL TICKER PERFORMANCE:")
        print(f"{'Ticker':<8} {'Allocation':<12} {'Trade Size':<12} {'Initial':<12} {'Current':<12} {'Return':<12} {'Return%':<10} {'Trades':<8}")
        print("-" * 90)
        
        for ticker, performance in self.ticker_performance.items():
            allocation = self.allocations[ticker]
            trade_size = self.trade_size_percentages.get(ticker, 100)
            print(f"{ticker:<8} {allocation:>8}% {trade_size:>10}% ${performance['initial_cash']:>10,.0f} ${performance['current_value']:>10,.0f} "
                  f"${performance['total_return']:>10,.0f} {performance['return_pct']:>8.1f}% {performance['total_trades']:>6}")
        
        # Display trade history for each ticker
        print(f"\n📈 TRADE HISTORY BY TICKER:")
        for ticker, portfolio in self.portfolios.items():
            if portfolio.trades:
                print(f"\n{ticker} Trades (Trade Size: {self.trade_size_percentages.get(ticker, 100)}%):")
                print(f"{'Date':<12} {'Action':<6} {'Price':<8} {'Shares':<10} {'Value':<10} {'Cash':<10} {'Available':<10}")
                print("-" * 80)
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
                    print(f"{trade['date']:<12} {trade['action']:<6} ${trade['price']:<7.2f} {trade['shares']:<10.4f} "
                          f"${value:<9.2f} ${trade['cash_remaining']:<9.2f} ${trade['available_cash']:<9.2f}")
        
        print(f"\n{'='*80}")
        if combined['return_pct'] > 0:
            print(f"🎉 COMBINED PROFIT! You made ${combined['total_return']:,.2f} ({combined['return_pct']:.2f}%)")
        else:
            print(f"📉 COMBINED LOSS! You lost ${abs(combined['total_return']):,.2f} ({abs(combined['return_pct']):.2f}%)")
        print(f"{'='*80}")
