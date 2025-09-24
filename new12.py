import yfinance as yf
import pandas as pd
from ta_strategies_TVLibrary import *
from indicators import *
from metrics import *
from display import *
from comparisons import *
from portfolios import *
from inputs import *
# =============================================================================




from comparision_types import ComparisonType



"""THIS CLASS BASICALLY CREATE INDICATOR FUNCTIONS AND STORE THEM IN A DICTIONARY
FOR EXAMPLE IF YOU TYPE self.indicators["SMA"] YOU WILL GET THE SMA FUNCTION 
BECAUSE IT IS STORED IN THE DICTIONARY AS self.indicators["SMA"] = sma"""



"""TO CALCULATE ANY INDICATOR VALUE USE THIS FUNCTION, JUST PASS THE NAME
AND THE PARAMETERS"""


# =============================================================================
# GENERIC COMPARISON SYSTEM
# =============================================================================


"""THIS FUNCTION FIRST CHECK IF ITS INDICATOR OR CONSTANT, IF ITS INDICATOR IT CALCULATES THE VALUE
AND STORES IT IN A NEW COLUMN, IF ITS CONSTANT IT STORES THE VALUE IN A NEW COLUMN"""

def create_comparison_column(data, comp_type, comp_name, comp_params, candles_ago=0):
    """Create a column for comparison - handles any type with candles ago logic"""
    
    if comp_type == ComparisonType.INDICATOR:
        # Calculate indicator
        # Handle both list and dict formats for comp_params
        if isinstance(comp_params, dict):
            period = comp_params.get('period', 20)  # Default to 20 if not specified
        else:
            period = comp_params[0]
        indicator_values = calculate_indicator(data, comp_name, comp_params)
        
        if candles_ago == 0:
            # Current candle
            data[f'{comp_name}_{period}'] = indicator_values
            return data, f'{comp_name}_{period}'
        else:
            # Previous candle(s)
            data[f'{comp_name}_{period}_{candles_ago}_ago'] = indicator_values.shift(candles_ago)
            return data, f'{comp_name}_{period}_{candles_ago}_ago'
    
    elif comp_type == ComparisonType.CONSTANT:
        # Create constant value column
        # Handle both list and dict formats for comp_params
        if isinstance(comp_params, dict):
            constant_value = comp_params.get('value', comp_params.get('period', 50))  # Default to 50
        elif len(comp_params) > 0:
            constant_value = comp_params[0]
        else:
            constant_value = 50  # Default constant value if no params provided
        if candles_ago == 0:
            data[f'Constant_{constant_value}'] = constant_value
            return data, f'Constant_{constant_value}'
        else:
            data[f'Constant_{constant_value}_{candles_ago}_ago'] = constant_value
            return data, f'Constant_{constant_value}_{candles_ago}_ago'
    
    elif comp_type == ComparisonType.PRICE:
        # Use price column directly
        if isinstance(comp_params, dict):
            price_column = comp_params.get('column', 'Close')  # Default to Close if not specified
        elif len(comp_params) > 0:
            price_column = comp_params[0]  # e.g., 'Close', 'Open', 'High', 'Low'
        else:
            price_column = 'Close'  # Default to Close if no params provided
        
        if price_column not in data.columns:
            raise ValueError(f"Price column '{price_column}' not found in data. Available: {list(data.columns)}")
        
        if candles_ago == 0:
            # Current candle
            data[f'Price_{price_column}'] = data[price_column]
            return data, f'Price_{price_column}'
        else:
            # Previous candle(s)
            data[f'Price_{price_column}_{candles_ago}_ago'] = data[price_column].shift(candles_ago)
            return data, f'Price_{price_column}_{candles_ago}_ago'
    
    else:
        raise ValueError(f"Unknown comparison type: {comp_type}")

# =============================================================================
# SIGNAL DETECTION
# =============================================================================

"""THIS FUNCTION CHECKS IF THE FIRST COLUMN IS GREATER THAN THE SECOND COLUMN
FOR EXAMPLE IF YOU TYPE crossed_up(data, "SMA_10", "SMA_20") IT WILL CHECK IF THE SMA_10
IS GREATER THAN THE SMA_20"""

# Comparison functions moved to comparisons.py

# =============================================================================
# GENERIC SIGNAL DETECTION
# =============================================================================

"""THIS CLASS BASICALLY CREATE SIGNAL DETECTION FUNCTIONS AND STORE THEM IN A DICTIONARY
FOR EXAMPLE IF YOU TYPE self.strategies["CROSSED UP"] YOU WILL GET THE CROSSED UP FUNCTION
BECAUSE IT IS STORED IN THE DICTIONARY AS self.strategies["CROSSED UP"] = crossed_up"""

class SignalDetector:
    """Generic signal detector - easily extensible"""
    
    def __init__(self):
        self.strategies = {
            "CROSSED UP": crossed_up,
            "CROSSED DOWN": crossed_down,
            "CROSSED": crossed,
            "EQUAL": equal_comparison,
            "GREATER THAN": greater_than,
            "GREATER OR EQUAL": greater_or_equal,
            "LESS THAN": less_than,
            "LESS OR EQUAL": less_or_equal,
            "WITHIN RANGE": within_range,
            "INCREASED": increased,
            "DECREASED": decreased
        }

    """THIS CLASS BASICALLY CREATE SIGNAL DETECTION FUNCTIONS AND STORE THEM IN A DICTIONARY
    FOR EXAMPLE IF YOU TYPE self.strategies["CROSSED UP"] YOU WILL GET THE CROSSED UP FUNCTION
    BECAUSE IT IS STORED IN THE DICTIONARY AS self.strategies["CROSSED UP"] = crossed_up"""

    def register_strategy(self, name, function):
        """Register a new strategy"""
        self.strategies[name] = function
    
    """REMEBER COMPARISION FUNCTION WHICH COMPARE THE FIRST COLUMN WITH THE SECOND COLUMN I.E INDICATOR OR CONSTANT
    IN THIS FUCNTION THE INDICATOR PRICE IS CALCULATED AND STORED IN A NEW COLUMN
    WE ARE USING THE CREATE_COMPARISON_COLUMN FUNCTION TO CREATE THE NEW COLUMN"""

    def detect_signals(self, data, comp1_type, comp1_name, comp1_params, 
                      comp2_type, comp2_name, comp2_params, strategy,
                      comp1_candles_ago=0, comp2_candles_ago=0):
        """Detect signals based on any comparison with candles ago logic"""
        
        
        # Create both comparison columns with candles ago support
        """THIS WAS RETURNING TWO THINGS DATA AND THE INDICATOR OR CONTANT COL"""
        data, col1 = create_comparison_column(data, comp1_type, comp1_name, comp1_params, comp1_candles_ago)
        data, col2 = create_comparison_column(data, comp2_type, comp2_name, comp2_params, comp2_candles_ago)
        
        # Get strategy function
        """THIS GETS THE STRATEGY FUNCTION FROM THE DICTIONARY"""
        strategy_func = self.strategies.get(strategy)
        if strategy_func is None:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Apply strategy
        if strategy == "WITHIN RANGE":
            data['Signal'] = strategy_func(data, col1, col2, tolerance=0.01)
        else:
            data['Signal'] = strategy_func(data, col1, col2)
        
        return data, col1, col2

# Global signal detector instance
signal_detector = SignalDetector()


"""TILL NOW WORKFLOW
Step 1: User Input Collection
# User selects:
# - Indicator: RSI
# - Parameters: (14, 70, 30) 
# - Comparison Type: INDICATOR vs CONSTANT
# - Strategy: "GREATER THAN"

Step 2: Indicator Calculation

# System calls: create_comparison_column(data, "INDICATOR", "RSI", (14, 70, 30))
# This calculates RSI and stores it in a column like "RSI_14_70_30"

Step 3: Comparison Target Creation

# System calls: create_comparison_column(data, "CONSTANT", "70", ())
# This creates a constant column with value 70 like "Constant_70"

Step 4: Signal Generation

# System gets the strategy function: self.strategies["GREATER THAN"] = greater_than
# Then applies: data['Signal'] = greater_than(data, "RSI_14_70_30", "Constant_70")
"""

# =============================================================================
# STRATEGY EXECUTION
# =============================================================================

"""THIS FUNCTION DETECTS SIGNALS BASED ON ANY COMPARISON, FOR EXAMPLE IF YOU TYPE self.strategies["CROSSED UP"] YOU WILL GET THE CROSSED UP FUNCTION
BECAUSE IT IS STORED IN THE DICTIONARY AS self.strategies["CROSSED UP"] = crossed_up"""

def detect_strategy_signals(data, entry_comp1_type, entry_comp1_name, entry_comp1_params,
                           entry_comp2_type, entry_comp2_name, entry_comp2_params,
                           exit_comp1_type, exit_comp1_name, exit_comp1_params,
                           exit_comp2_type, exit_comp2_name, exit_comp2_params,
                           entry_strategy, exit_strategy, entry_comp1_candles_ago=0, 
                           entry_comp2_candles_ago=0, exit_comp1_candles_ago=0, exit_comp2_candles_ago=0):
    """Detect entry and exit signals using generic comparison system with candles ago logic"""
    
    # Entry signals
    data, entry_col1, entry_col2 = signal_detector.detect_signals(
        data, entry_comp1_type, entry_comp1_name, entry_comp1_params,
        entry_comp2_type, entry_comp2_name, entry_comp2_params, entry_strategy,
        comp1_candles_ago=entry_comp1_candles_ago, comp2_candles_ago=entry_comp2_candles_ago
    )
    data['Entry_Signal'] = data['Signal']
    
    # Rename entry columns to avoid conflicts
    entry_col1_renamed = f"Entry_{entry_col1}"
    entry_col2_renamed = f"Entry_{entry_col2}"
    data[entry_col1_renamed] = data[entry_col1]
    data[entry_col2_renamed] = data[entry_col2]
    
    # Exit signals
    data, exit_col1, exit_col2 = signal_detector.detect_signals(
        data, exit_comp1_type, exit_comp1_name, exit_comp1_params,
        exit_comp2_type, exit_comp2_name, exit_comp2_params, exit_strategy,
        comp1_candles_ago=exit_comp1_candles_ago, comp2_candles_ago=exit_comp2_candles_ago
    )
    data['Exit_Signal'] = data['Signal']
    
    # Rename exit columns to avoid conflicts
    exit_col1_renamed = f"Exit_{exit_col1}"
    exit_col2_renamed = f"Exit_{exit_col2}"
    data[exit_col1_renamed] = data[exit_col1]
    data[exit_col2_renamed] = data[exit_col2]
    
    return data, entry_col1_renamed, entry_col2_renamed, exit_col1_renamed, exit_col2_renamed

# =============================================================================
# DATA PROCESSING
# =============================================================================


def execute_trading_strategy(data, portfolio):
    """Execute the trading strategy with position tracking"""
    # Initialize tracking columns
    data['Position'] = 'OUT'
    data['Action'] = ''
    data['Portfolio_Value'] = 0.0
    data['Cash'] = 0.0
    data['Shares'] = 0.0
    data['Long_Shares'] = 0.0
    data['Short_Shares'] = 0.0
    data['Position_Type'] = 'OUT'
    data['Reason'] = ''  # Added for trade reasons

    current_position = 'OUT'

    for i in range(len(data)):
        current_price = data['Close'].iloc[i]
        current_date = data.index[i]
        
        # First, check trailing stop if we're IN position (highest priority)
        if current_position == 'IN':
            trailing_result = portfolio.update_trailing_stop(current_price)
            if trailing_result == "trailing_stop_triggered":
                if portfolio.sell(current_price, current_date, reason="Trailing stop triggered"):
                    current_position = 'OUT'
                    data.loc[i, 'Action'] = 'SELL'
                    data.loc[i, 'Reason'] = 'Trailing stop triggered'
                    data.loc[i, 'Position'] = 'OUT'
                    data.loc[i, 'Portfolio_Value'] = portfolio.get_portfolio_value(current_price)
                    data.loc[i, 'Cash'] = portfolio.cash
                    data.loc[i, 'Shares'] = portfolio.shares
                    continue
        
        # Second, check regular risk management orders (stop-loss/take-profit) if we're IN position
        if current_position in ['IN', 'LONG', 'SHORT']:
            risk_action, risk_reason = portfolio.check_risk_orders(current_price, current_date)
            if risk_action == "EXIT":
                if portfolio.exit_position(current_price, current_date, reason=risk_reason):
                    data.loc[i, 'Position'] = 'OUT'
                    data.loc[i, 'Action'] = 'EXIT'
                    data.loc[i, 'Reason'] = risk_reason
                    current_position = 'OUT'
                    continue  # Skip normal strategy signals if risk order triggered
            elif risk_action == "SELL":  # Legacy support
                if portfolio.sell(current_price, current_date, reason=risk_reason):
                    data.loc[i, 'Position'] = 'OUT'
                    data.loc[i, 'Action'] = 'SELL'
                    data.loc[i, 'Reason'] = risk_reason
                    current_position = 'OUT'
                    continue  # Skip normal strategy signals if risk order triggered
        
        # LONG/SHORT REVERSAL LOGIC
        # Entry Signal (SMA Crossover) - Enter LONG or flip from SHORT to LONG
        if data['Entry_Signal'].iloc[i]:
            if current_position == 'OUT' or current_position == 'SHORT':
                # Exit SHORT if currently short
                if current_position == 'SHORT':
                    if portfolio.exit_position(current_price, current_date, reason="Short to Long Flip"):
                        data.loc[i, 'Action'] = 'EXIT_SHORT'
                        data.loc[i, 'Reason'] = 'Short to Long Flip'
                
                # Enter LONG
                if portfolio.enter_long(current_price, current_date):
                    data.loc[i, 'Position'] = 'LONG'
                    data.loc[i, 'Action'] = 'LONG'
                    data.loc[i, 'Reason'] = 'Long Strategy Entry' if current_position == 'OUT' else 'Short to Long Flip'
                    current_position = 'LONG'
        
        # Exit Signal (SMA Crossdown) - Enter SHORT or flip from LONG to SHORT  
        elif data['Exit_Signal'].iloc[i]:
            if current_position == 'OUT' or current_position == 'LONG':
                # Exit LONG if currently long
                if current_position == 'LONG':
                    if portfolio.exit_position(current_price, current_date, reason="Long to Short Flip"):
                        data.loc[i, 'Action'] = 'EXIT_LONG'
                        data.loc[i, 'Reason'] = 'Long to Short Flip'
                
                # Enter SHORT
                if portfolio.enter_short(current_price, current_date):
                    data.loc[i, 'Position'] = 'SHORT'
                    data.loc[i, 'Action'] = 'SHORT'
                    data.loc[i, 'Reason'] = 'Short Strategy Entry' if current_position == 'OUT' else 'Long to Short Flip'
                    current_position = 'SHORT'
        
        # No action - maintain current position
        else:
            data.loc[i, 'Position'] = current_position
            data.loc[i, 'Action'] = ''
            data.loc[i, 'Reason'] = 'Hold'
        
        # Update portfolio tracking
        data.loc[i, 'Portfolio_Value'] = portfolio.get_portfolio_value(current_price)
        data.loc[i, 'Cash'] = portfolio.cash
        data.loc[i, 'Shares'] = portfolio.shares  # Legacy support
        data.loc[i, 'Long_Shares'] = portfolio.long_shares
        data.loc[i, 'Short_Shares'] = portfolio.short_shares
        data.loc[i, 'Position_Type'] = portfolio.position
    
    return data

def execute_trading_strategy_original(data, portfolio, strategy_direction):
    """Execute trading strategy for Long Only or Short Only"""
    # Initialize tracking columns
    data['Position'] = 'OUT'
    data['Action'] = ''
    data['Portfolio_Value'] = 0.0
    data['Cash'] = 0.0
    data['Shares'] = 0.0
    data['Long_Shares'] = 0.0
    data['Short_Shares'] = 0.0
    data['Position_Type'] = 'OUT'
    data['Reason'] = ''

    current_position = 'OUT'

    for i in range(len(data)):
        current_price = data['Close'].iloc[i]
        current_date = data.index[i]
        
        # Risk management checks (same as before)
        if current_position == 'IN':
            trailing_result = portfolio.update_trailing_stop(current_price)
            if trailing_result == "trailing_stop_triggered":
                if portfolio.sell(current_price, current_date, reason="Trailing stop triggered"):
                    current_position = 'OUT'
                    data.loc[i, 'Action'] = 'SELL'
                    data.loc[i, 'Reason'] = 'Trailing stop triggered'
                    data.loc[i, 'Position'] = 'OUT'
                    data.loc[i, 'Portfolio_Value'] = portfolio.get_portfolio_value(current_price)
                    data.loc[i, 'Cash'] = portfolio.cash
                    data.loc[i, 'Shares'] = portfolio.shares
                    continue
        
        if current_position == 'IN':
            risk_action, risk_reason = portfolio.check_risk_orders(current_price, current_date)
            if risk_action == "EXIT":
                if portfolio.sell(current_price, current_date, reason=risk_reason):
                    data.loc[i, 'Position'] = 'OUT'
                    data.loc[i, 'Action'] = 'SELL'
                    data.loc[i, 'Reason'] = risk_reason
                    current_position = 'OUT'
                    continue
            elif risk_action == "SELL":
                if portfolio.sell(current_price, current_date, reason=risk_reason):
                    data.loc[i, 'Position'] = 'OUT'
                    data.loc[i, 'Action'] = 'SELL'
                    data.loc[i, 'Reason'] = risk_reason
                    current_position = 'OUT'
                    continue
        
        # Strategy-specific logic
        if strategy_direction == "Long Only":
            # Long Only: Buy on entry signal, sell on exit signal
            if current_position == 'OUT' and data['Entry_Signal'].iloc[i]:
                if portfolio.buy(current_price, current_date):
                    data.loc[i, 'Position'] = 'IN'
                    data.loc[i, 'Action'] = 'BUY'
                    data.loc[i, 'Reason'] = 'Strategy Entry'
                    current_position = 'IN'
            elif current_position == 'IN' and data['Exit_Signal'].iloc[i]:
                if portfolio.sell(current_price, current_date, reason="Strategy Exit"):
                    data.loc[i, 'Position'] = 'OUT'
                    data.loc[i, 'Action'] = 'SELL'
                    data.loc[i, 'Reason'] = 'Strategy Exit'
                    current_position = 'OUT'
                    
        elif strategy_direction == "Short Only":
            # Short Only: Short on exit signal, cover on entry signal
            if current_position == 'OUT' and data['Exit_Signal'].iloc[i]:
                if portfolio.enter_short(current_price, current_date):
                    data.loc[i, 'Position'] = 'SHORT'
                    data.loc[i, 'Action'] = 'SHORT'
                    data.loc[i, 'Reason'] = 'Short Strategy Entry'
                    current_position = 'SHORT'
            elif current_position == 'SHORT' and data['Entry_Signal'].iloc[i]:
                if portfolio.exit_position(current_price, current_date, reason="Short Strategy Exit"):
                    data.loc[i, 'Position'] = 'OUT'
                    data.loc[i, 'Action'] = 'EXIT_SHORT'
                    data.loc[i, 'Reason'] = 'Short Strategy Exit'
                    current_position = 'OUT'
        
        # No action - maintain current position
        else:
            data.loc[i, 'Position'] = current_position
            data.loc[i, 'Action'] = ''
            data.loc[i, 'Reason'] = 'Hold'
        
        # Update portfolio tracking
        data.loc[i, 'Portfolio_Value'] = portfolio.get_portfolio_value(current_price)
        data.loc[i, 'Cash'] = portfolio.cash
        data.loc[i, 'Shares'] = portfolio.shares
        data.loc[i, 'Long_Shares'] = portfolio.long_shares
        data.loc[i, 'Short_Shares'] = portfolio.short_shares
        data.loc[i, 'Position_Type'] = portfolio.position
    
    return data


class MultiConditionDetector:
    """Detects signals based on multiple conditions with AND or OR logic"""
    
    def __init__(self):
        self.conditions = []
        self.logic_type = 'AND'  # 'AND' or 'OR'
    
    def add_condition(self, comp1_type, comp1_name, comp1_params, 
                     comp2_type, comp2_name, comp2_params, strategy,
                     comp1_candles_ago=0, comp2_candles_ago=0):
        """Add a single condition to the list with candles ago support"""
        self.conditions.append({
            'comp1_type': comp1_type, 'comp1_name': comp1_name, 'comp1_params': comp1_params,
            'comp2_type': comp2_type, 'comp2_name': comp2_name, 'comp2_params': comp2_params,
            'strategy': strategy, 'comp1_candles_ago': comp1_candles_ago, 'comp2_candles_ago': comp2_candles_ago
        })
    
    def set_logic_type(self, logic_type):
        """Set logic type: 'AND' or 'OR'"""
        if logic_type not in ['AND', 'OR']:
            raise ValueError("Logic type must be 'AND' or 'OR'")
        self.logic_type = logic_type
    
    def detect_all_conditions(self, data):
        """Check conditions with AND or OR logic"""
        if not self.conditions:
            return data, []
        
        all_signals = []
        condition_columns = []
        
        for i, condition in enumerate(self.conditions):
            try:
                # Use existing detect_signals function with candles ago support
                data, col1, col2 = signal_detector.detect_signals(
                    data, 
                    condition['comp1_type'], condition['comp1_name'], condition['comp1_params'],
                    condition['comp2_type'], condition['comp2_name'], condition['comp2_params'], 
                    condition['strategy'],
                    condition.get('comp1_candles_ago', 0), condition.get('comp2_candles_ago', 0)
                )
                
                # Check if Signal column exists
                if 'Signal' not in data.columns:
                    raise ValueError(f"Signal column not created for condition {i+1}")
                
                # Rename columns to avoid conflicts
                condition_col1 = f"Condition_{i+1}_{col1}"
                condition_col2 = f"Condition_{i+1}_{col2}"
                data[condition_col1] = data[col1]
                data[condition_col2] = data[col2]
                
                all_signals.append(data['Signal'])
                condition_columns.append((condition_col1, condition_col2))
                
            except Exception as e:
                raise ValueError(f"Error processing condition {i+1}: {str(e)}")
        
        # Apply logic (AND or OR)
        if len(all_signals) == 1:
            data['Combined_Signal'] = all_signals[0]
        else:
            if self.logic_type == 'AND':
                # All conditions must be true
                combined_signal = all_signals[0]
                for signal in all_signals[1:]:
                    combined_signal = combined_signal & signal
            else:  # OR logic
                # Any condition can be true
                combined_signal = all_signals[0]
                for signal in all_signals[1:]:
                    combined_signal = combined_signal | signal
            
            data['Combined_Signal'] = combined_signal
        
        return data, condition_columns
    
    def clear_conditions(self):
        """Clear all conditions"""
        self.conditions = []

# Global multi-condition detectors
entry_multi_detector = MultiConditionDetector()
exit_multi_detector = MultiConditionDetector()


def run_multi_condition_strategy(ticker, period, interval, entry_conditions, exit_conditions, entry_logic='AND', exit_logic='AND', strategy_direction="Long Only"):
    """Run a multi-condition trading strategy"""
    # Download and prepare data
    data = download_and_prepare_data(ticker, period, interval)
    
    # Detect signals using multi-condition system
    data, entry_condition_columns, exit_condition_columns = detect_multi_strategy_signals(
        data, entry_conditions, exit_conditions, entry_logic, exit_logic
    )
    
    # Initialize portfolio
    portfolio = Portfolio(10000)  # Start with $10,000
    
    # Ask user about trailing stop
    print("\n--- TRAILING STOP LOSS ---")
    print("Trailing stop follows price up to protect profits")
    print("Example: If you buy at $100 and set 5% trailing stop:")
    print("  - At $105: Stop moves to $99.75")
    print("  - At $110: Stop moves to $104.50")
    print("  - If price drops to $104: You sell at $104 (profit!)")
    
    enable_trailing = input("\nEnable trailing stop loss? (y/n) [default: n]: ").lower().strip()
    
    # Default to 'n' if empty input
    if not enable_trailing:
        enable_trailing = 'n'
    
    if enable_trailing == 'y':
        print("\n1. Percentage (e.g., 5% trailing distance)")
        print("2. Dollar amount (e.g., $5 trailing distance)")
        trailing_choice = input("Enter choice (1-2): ").strip()
        
        if trailing_choice == '1':
            trailing_value = float(input("Enter trailing distance percentage (e.g., 5.0): "))
            portfolio.set_trailing_stop(percentage=trailing_value)
        else:
            trailing_value = float(input("Enter trailing distance in dollars (e.g., 5.0): "))
            portfolio.set_trailing_stop(dollars=trailing_value)
    else:
        print("Trailing stop disabled - using regular risk management only")
    
    # Execute trading strategy based on direction
    if strategy_direction == "Long/Short Reversal":
        data = execute_trading_strategy(data, portfolio)
    else:
        # For Long Only and Short Only, use the original logic
        data = execute_trading_strategy_original(data, portfolio, strategy_direction)
    
    # Display results
    display_multi_condition_results(ticker, data, portfolio, entry_conditions, exit_conditions, entry_logic, exit_logic)

def display_multi_condition_results(ticker, data, portfolio, entry_conditions, exit_conditions, entry_logic='AND', exit_logic='AND'):
    """Display comprehensive results for multi-condition strategy"""
    final_price = data['Close'].iloc[-1]
    performance = portfolio.get_performance(final_price, data)

    # Display results
    print(f"\n{'='*60}")
    print(f"MULTI-CONDITION PORTFOLIO PERFORMANCE REPORT - {ticker}")
    print(f"{'='*60}")
    
    # Display entry conditions
    print(f"\n📈 ENTRY CONDITIONS ({len(entry_conditions)}) - Logic: {entry_logic}:")
    for i, condition in enumerate(entry_conditions, 1):
        if condition['comp1_type'] == ComparisonType.INDICATOR:
            comp1_desc = f"{condition['comp1_name']}{condition['comp1_params']}"
        elif condition['comp1_type'] == ComparisonType.CONSTANT:
            comp1_desc = f"Constant({condition['comp1_params'][0] if len(condition['comp1_params']) > 0 else 50})"
        else:  # PRICE
            comp1_desc = f"Price({condition['comp1_params'][0] if len(condition['comp1_params']) > 0 else 'Close'})"
            
        if condition['comp2_type'] == ComparisonType.INDICATOR:
            comp2_desc = f"{condition['comp2_name']}{condition['comp2_params']}"
        elif condition['comp2_type'] == ComparisonType.CONSTANT:
            comp2_desc = f"Constant({condition['comp2_params'][0] if len(condition['comp2_params']) > 0 else 50})"
        else:  # PRICE
            comp2_desc = f"Price({condition['comp2_params'][0] if len(condition['comp2_params']) > 0 else 'Close'})"
            
        print(f"  {i}. {comp1_desc} {condition['strategy']} {comp2_desc}")
    
    # Display exit conditions
    print(f"\n📉 EXIT CONDITIONS ({len(exit_conditions)}) - Logic: {exit_logic}:")
    for i, condition in enumerate(exit_conditions, 1):
        if condition['comp1_type'] == ComparisonType.INDICATOR:
            comp1_desc = f"{condition['comp1_name']}{condition['comp1_params']}"
        elif condition['comp1_type'] == ComparisonType.CONSTANT:
            comp1_desc = f"Constant({condition['comp1_params'][0] if len(condition['comp1_params']) > 0 else 50})"
        else:  # PRICE
            comp1_desc = f"Price({condition['comp1_params'][0] if len(condition['comp1_params']) > 0 else 'Close'})"
            
        if condition['comp2_type'] == ComparisonType.INDICATOR:
            comp2_desc = f"{condition['comp2_name']}{condition['comp2_params']}"
        elif condition['comp2_type'] == ComparisonType.CONSTANT:
            comp2_desc = f"Constant({condition['comp2_params'][0] if len(condition['comp2_params']) > 0 else 50})"
        else:  # PRICE
            comp2_desc = f"Price({condition['comp2_params'][0] if len(condition['comp2_params']) > 0 else 'Close'})"
            
        print(f"  {i}. {comp1_desc} {condition['strategy']} {comp2_desc}")
    
    print(f"{'='*60}")

    display_financial_summary(performance)
    display_current_position(performance, final_price)
    display_trade_history(portfolio)
    
    # Display strategy performance
    print(f"\n📋 STRATEGY PERFORMANCE:")
    columns = ['Date', 'Close', 'Entry_Signal', 'Exit_Signal', 'Position', 'Action', 'Portfolio_Value']
    print(data[columns].tail(10).to_string(index=False))

    print(f"\n{'='*60}")
    if performance['return_pct'] > 0:
        print(f"🎉 PROFIT! You made ${performance['total_return']:.2f} ({performance['return_pct']:.2f}%)")
    else:
        print(f"📉 LOSS! You lost ${abs(performance['total_return']):.2f} ({abs(performance['return_pct']):.2f}%)")
    print(f"{'='*60}")

# =============================================================================
# MAIN CONTROLLER
# =============================================================================

def run_trading_strategy(ticker, period, interval, entry_comp1_type, entry_comp1_name, entry_comp1_params,
                        entry_comp2_type, entry_comp2_name, entry_comp2_params,
                        exit_comp1_type, exit_comp1_name, exit_comp1_params,
                        exit_comp2_type, exit_comp2_name, exit_comp2_params,
                        entry_strategy, exit_strategy, entry_comp1_candles_ago=0, 
                        entry_comp2_candles_ago=0, exit_comp1_candles_ago=0, exit_comp2_candles_ago=0, strategy_direction="Long Only"):
    """Run a complete trading strategy with candles ago logic"""
    # Download and prepare data
    data = download_and_prepare_data(ticker, period, interval)
    
    # Detect signals using generic comparison system
    data, entry_col1, entry_col2, exit_col1, exit_col2 = detect_strategy_signals(
        data, entry_comp1_type, entry_comp1_name, entry_comp1_params,
        entry_comp2_type, entry_comp2_name, entry_comp2_params,
        exit_comp1_type, exit_comp1_name, exit_comp1_params,
        exit_comp2_type, exit_comp2_name, exit_comp2_params,
        entry_strategy, exit_strategy, entry_comp1_candles_ago, entry_comp2_candles_ago,
        exit_comp1_candles_ago, exit_comp2_candles_ago
    )
    
    # Initialize portfolio
    portfolio = Portfolio(10000)  # Start with $10,000
    
    # Execute trading strategy based on direction
    if strategy_direction == "Long/Short Reversal":
        data = execute_trading_strategy(data, portfolio)
    else:
        # For Long Only and Short Only, use the original logic
        data = execute_trading_strategy_original(data, portfolio, strategy_direction)
    
    # Display results
    display_results(ticker, data, portfolio, entry_comp1_name, entry_comp2_name,
                   exit_comp1_name, exit_comp2_name, entry_strategy, exit_strategy,
                   entry_col1, entry_col2, exit_col1, exit_col2)

def run_multi_ticker_strategy(config):
    """Run multi-ticker portfolio strategy"""
    print(f"\n🚀 Running Multi-Ticker Portfolio Strategy...")
    print(f"Tickers: {', '.join(config['tickers'])}")
    print(f"Total Capital: ${config['total_capital']:,.2f}")
    print(f"Allocations: {config['allocations']}")
    print(f"Trade Sizes: {config['trade_sizes']}")
    print(f"Strategy Direction: {config['strategy_direction']}")
    
    # Initialize multi-ticker portfolio
    portfolio = MultiTickerPortfolio(config['total_capital'], config['allocations'], config['trade_sizes'])
    
    # Download data for all tickers
    print(f"\n📊 Downloading data for all tickers...")
    for ticker in config['tickers']:
        print(f"  Downloading {ticker}...")
        data = portfolio.get_ticker_data(ticker, config['period'], config['interval'])
        if data is None:
            print(f"  ❌ Failed to download {ticker}")
            return
    
    # Run strategy on each ticker
    print(f"\n📈 Running strategy on all tickers...")
    for ticker in config['tickers']:
        print(f"  Processing {ticker}...")
        data = portfolio.run_strategy_on_ticker(ticker, config['period'], config['interval'], config)
        if data is None:
            print(f"  ❌ Failed to process {ticker}")
            return
    
    # Display results
    portfolio.display_combined_results(config)

def run_multi_ticker_multi_strategy(config):
    """Run multi-ticker multi-strategy portfolio"""
    print(f"\n🚀 Running Multi-Ticker Multi-Strategy Portfolio...")
    print(f"Tickers: {', '.join(config['tickers'])}")
    print(f"Total Capital: ${config['total_capital']:,.2f}")
    print(f"Allocations: {config['allocations']}")
    print(f"Trade Sizes: {config['trade_sizes']}")
    print(f"Strategy Direction: {config['strategy_direction']}")
    
    # Add strategy direction to each ticker's strategy config
    for ticker in config['tickers']:
        if ticker in config['ticker_strategies']:
            config['ticker_strategies'][ticker]['strategy_direction'] = config['strategy_direction']
    
    # Initialize multi-strategy portfolio
    portfolio = MultiTickerMultiStrategyPortfolio(
        config['total_capital'], 
        config['allocations'], 
        config['trade_sizes'],
        config['ticker_strategies']
    )
    
    # Run strategy on each ticker with individual strategies
    print(f"\n📈 Running individual strategies on all tickers...")
    for ticker in config['tickers']:
        print(f"  Processing {ticker} with its unique strategy...")
        data = portfolio.run_strategy_on_ticker(ticker, config['period'], config['interval'])
        if data is None:
            print(f"  ❌ Failed to process {ticker}")
            return
    
    # Display results
    portfolio.display_combined_results(config)

def main():
    """Main function to run the trading strategy"""
    print("\n" + "="*60)
    print("ADVANCED TRADING STRATEGY SYSTEM")
    print("="*60)
    print("Choose strategy type:")
    print("1. Single Condition Strategy (Original)")
    print("2. Multi-Condition Strategy")
    print("3. Multi-Ticker Portfolio Strategy (Same strategy for all)")
    print("4. Multi-Ticker Multi-Strategy Portfolio (NEW! Different strategy per ticker)")
    print("="*60)
    
    choice = input("Enter choice (1-4) [default: 1]: ").strip()
    
    # If empty input, default to 1
    if not choice:
        choice = "1"
    
    if choice == "1":
        # Original single condition system
        # Ask for strategy direction first
        print("\n--- STRATEGY DIRECTION ---")
        print("1. Long Only (Buy on crossover, sell on crossdown)")
        print("2. Short Only (Sell on crossdown, buy on crossover)")
        print("3. Long/Short Reversal (Flip positions automatically)")
        
        while True:
            try:
                direction_choice = input("Enter choice (1-3) [default: 1]: ").strip()
                
                # If empty input, default to 1
                if not direction_choice:
                    direction_choice = "1"
                
                direction_map = {
                    "1": "Long Only",
                    "2": "Short Only", 
                    "3": "Long/Short Reversal"
                }
                
                if direction_choice in direction_map:
                    strategy_direction = direction_map[direction_choice]
                    break
                else:
                    print("❌ Invalid choice! Please enter 1, 2, or 3.")
                    continue
                    
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled!")
                return
            except Exception as e:
                print(f"❌ Error: {e}")
                return
        
        show_trading_examples()
        inputs = get_strategy_inputs()
        if inputs is None:
            return
        
        (ticker, period, interval, entry_comp1_type, entry_comp1_name, entry_comp1_params,
         entry_comp2_type, entry_comp2_name, entry_comp2_params,
         exit_comp1_type, exit_comp1_name, exit_comp1_params,
         exit_comp2_type, exit_comp2_name, exit_comp2_params,
         entry_strategy, exit_strategy, entry_comp1_candles_ago, entry_comp2_candles_ago,
         exit_comp1_candles_ago, exit_comp2_candles_ago) = inputs
        
        run_trading_strategy(ticker, period, interval, entry_comp1_type, entry_comp1_name, entry_comp1_params,
                            entry_comp2_type, entry_comp2_name, entry_comp2_params,
                            exit_comp1_type, exit_comp1_name, exit_comp1_params,
                            exit_comp2_type, exit_comp2_name, exit_comp2_params,
                            entry_strategy, exit_strategy, entry_comp1_candles_ago, entry_comp2_candles_ago,
                            exit_comp1_candles_ago, exit_comp2_candles_ago, strategy_direction)
    
    elif choice == "2":
        # Multi-condition system
        # Ask for strategy direction first
        print("\n--- STRATEGY DIRECTION ---")
        print("1. Long Only (Buy on crossover, sell on crossdown)")
        print("2. Short Only (Sell on crossdown, buy on crossover)")
        print("3. Long/Short Reversal (Flip positions automatically)")
        
        while True:
            try:
                direction_choice = input("Enter choice (1-3) [default: 1]: ").strip()
                
                # If empty input, default to 1
                if not direction_choice:
                    direction_choice = "1"
                
                direction_map = {
                    "1": "Long Only",
                    "2": "Short Only", 
                    "3": "Long/Short Reversal"
                }
                
                if direction_choice in direction_map:
                    strategy_direction = direction_map[direction_choice]
                    break
                else:
                    print("❌ Invalid choice! Please enter 1, 2, or 3.")
                    continue
                    
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled!")
                return
            except Exception as e:
                print(f"❌ Error: {e}")
                return
        
        inputs = get_multi_strategy_inputs()
        if inputs is None:
            return
        
        ticker, period, interval, entry_conditions, exit_conditions, entry_logic, exit_logic = inputs
        run_multi_condition_strategy(ticker, period, interval, entry_conditions, exit_conditions, entry_logic, exit_logic, strategy_direction)
    
    elif choice == "3":
        # Multi-ticker portfolio system
        # Ask for strategy direction first
        print("\n--- STRATEGY DIRECTION ---")
        print("1. Long Only (Buy on crossover, sell on crossdown)")
        print("2. Short Only (Sell on crossdown, buy on crossover)")
        print("3. Long/Short Reversal (Flip positions automatically)")
        
        while True:
            try:
                direction_choice = input("Enter choice (1-3) [default: 1]: ").strip()
                
                # If empty input, default to 1
                if not direction_choice:
                    direction_choice = "1"
                
                direction_map = {
                    "1": "Long Only",
                    "2": "Short Only", 
                    "3": "Long/Short Reversal"
                }
                
                if direction_choice in direction_map:
                    strategy_direction = direction_map[direction_choice]
                    break
                else:
                    print("❌ Invalid choice! Please enter 1, 2, or 3.")
                    continue
                    
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled!")
                return
            except Exception as e:
                print(f"❌ Error: {e}")
                return
        
        config = get_multi_ticker_inputs()
        if config is None:
            return
        
        # Add strategy direction to config
        config['strategy_direction'] = strategy_direction
        
        run_multi_ticker_strategy(config)
    
    elif choice == "4":
        # Multi-ticker multi-strategy system
        # Ask for strategy direction first
        print("\n--- STRATEGY DIRECTION ---")
        print("1. Long Only (Buy on crossover, sell on crossdown)")
        print("2. Short Only (Sell on crossdown, buy on crossover)")
        print("3. Long/Short Reversal (Flip positions automatically)")
        
        while True:
            try:
                direction_choice = input("Enter choice (1-3) [default: 1]: ").strip()
                
                # If empty input, default to 1
                if not direction_choice:
                    direction_choice = "1"
                
                direction_map = {
                    "1": "Long Only",
                    "2": "Short Only", 
                    "3": "Long/Short Reversal"
                }
                
                if direction_choice in direction_map:
                    strategy_direction = direction_map[direction_choice]
                    break
                else:
                    print("❌ Invalid choice! Please enter 1, 2, or 3.")
                    continue
                    
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled!")
                return
            except Exception as e:
                print(f"❌ Error: {e}")
                return
        
        config = get_multi_ticker_multi_strategy_inputs()
        if config is None:
            return
        
        # Add strategy direction to config
        config['strategy_direction'] = strategy_direction
        
        run_multi_ticker_multi_strategy(config)
    
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
