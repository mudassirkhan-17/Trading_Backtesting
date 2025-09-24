Long Only --> Take the trade amount = available_cash * (trade_size_percentage / 100)
--> shares = trade_amount/price 
--> cost (share * price)  
We will sum up the shares and we will decrease the price. so whenever 
The system works by:
BUY: Converting cash to shares (reducing cash, increasing shares)
SELL: Converting shares back to cash (increasing cash, resetting shares)
Position tracking: Always knowing if you're IN (shares) or OUT (cash)
Cash management: Tracking available money for new trades
Share management: Tracking owned shares for selling


