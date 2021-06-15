import pandas as pd
import QuantLib as ql



def date2ql(date):

    date = pd.to_datetime(date)
    return ql.Date(date.day, date.month, date.year)

def business_day_between(date1, date2):
    date1 = date2ql(date1) if not isinstance(date1,ql.Date) else date1
    date2 = date2ql(date2) if not isinstance(date2,ql.Date) else date2
    cal = ql.UnitedStates(ql.UnitedStates.NYSE)
    return cal.businessDaysBetween(date1,date2)