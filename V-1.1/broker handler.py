from ib.opt import Connection,message
from ib.ext.Contract import  Contract
from ib.ext.Order import   Order

import numpy as np
import pandas as pd
symbol_list=["TSLA","AMZN"]

def  generate_contract(symbol,sec_type,exchange,prime_exchange,currency):
    Contract.m_symbol=symbol
    Contract.m_secType=sec_type
    Contract.m_exchange=exchange
    Contract.m_primaryExch=prime_exchange
    Contract.m_currency=currency
    return Contract
def generate_order(action, quantity,price=None):
    if price is None:# If price is not specified, generate an limit order
        order=Order()
        Order.m_orderType="LMT"
        Order.m_totalQuantity=quantity
        Order.m_action=action
        Order.m_lmtPrice=price
    else:
        order = Order()
        Order.m_orderType = "MKT"
        Order.m_totalQuantity = quantity
        Order.m_action=action
    return order

def main():
    connection=Connection.create(port=7497, clientId=707)
    connection.connect()
    order_id=1
    contract=generate_contract(symbol_list[0],"STK","SMART","SMART","USD")
    offer=generate_order("BUY",222,200)
    connection.placeOrder(order_id,contract,offer)
    connection.disconnect()

main()



