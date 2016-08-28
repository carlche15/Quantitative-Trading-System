This “Quantitative Analysis platform” will hopefully do three major things:  
1) Stock chart analysis  
2) Quantitative trading simulation  
3) A machine-learning approach to profit/loss simulation of a hedge fund  
    Each part of the function is composed by various modules:  
    0) 
    1) Stock chart analysis:  
     1.1 Fetching & updating data from public Python API(Yahoo Finance).  
     1.2 Local database management(Sqlite3).  
     1.3 OOB structure of stock data, analysis methodology and data visualization tools.    
        1.3.1 Stock data class(Stock_Info)  
        1.3.2 Stock analysis method class(Stock_Method)  
        1.3.3 Data visualization tools class(Chart_Factory)  
    2) Quantitative trading simulation:  
     2.1 Portfolio object design(Portfolio).  
     2.2 Portfolio visualization tool class(Chart_Factory_Portfolio)
