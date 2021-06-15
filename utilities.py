
    
    
def fuck_pd_rolling(window,data, func, *args,**kwargs):
    window=3
    df_idx = data.index
    result_df = pd.DataFrame().reindex_like(data)

    for i in range(len(df_idx)):      
        sub_df = data.loc[df_idx[i-window+1]:df_idx[i]]
        result_df.loc[df_idx[i]]=func(sub_df,*args,**kwargs)
    return result_df
 