#master_id : müşteri idsi
#order_channel: işletim sistemş
#last_order_channel : offline da olabilir
#first_order_date: ilk sipariş tarihi
#last_order_date_online :
#last_order_date_ofline

from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x:'%.4f' % x)
################   Quest 1     ################
# 1



df_ = pd.read_csv("C:/Users/Omer/CRM_RFM/CRM_RFM/Case_Study_1_2/flo_data_20k.csv")
df = df_.copy()
df.describe().T
df.head()
df.isnull().sum()

df["last_order_date"].max() #2021-05-30
df["customer_value_total_ever_offline"].max() # min max arandı
df["customer_value_total_ever_online"].max() # min max arandı


def outlier_thresholds(dataframe , variable):
    quartile1 = dataframe[variable].quantile(0.01) # normalde %25
    quartile3 = dataframe[variable].quantile(0.99) # normalde %75
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range

    low_limit = quartile1 -1.5 * interquantile_range

    return  low_limit, up_limit

def replace_with_thresholds(dataframe , variable):
    low_limit, up_limit = outlier_thresholds(dataframe,variable)
    dataframe.loc[(dataframe[variable]) < low_limit, variable] =round(low_limit,0)
    dataframe.loc[(dataframe[variable]) > up_limit, variable] = round(up_limit,0)

replace_with_thresholds(df, "order_num_total_ever_online")
replace_with_thresholds(df, "order_num_total_ever_offline")
replace_with_thresholds(df, "customer_value_total_ever_offline")
replace_with_thresholds(df, "customer_value_total_ever_online")

df["Omnichannel_order"]=df["order_num_total_ever_offline"]+ df["order_num_total_ever_online"]
df["Omnichannel_value"]=df["customer_value_total_ever_online"]+df["customer_value_total_ever_offline"]

df.head()

date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns]=df[date_columns].apply(pd.to_datetime)
df.info()

analysis_date = pd.Timestamp(year=2021,month=6,day=2)
cltv_df = pd.DataFrame()
cltv_df["customer_id"]=df["master_id"]
cltv_df["recency_cltv_weekly"]= ((df["last_order_date"]-df["first_order_date"]).dt.days)/7
cltv_df["T_weekly"] = ((analysis_date - df["first_order_date"]).dt.days) / 7
cltv_df["frequency"] = df["Omnichannel_order"]
cltv_df["monetary_cltv_avg"] = df["Omnichannel_value"]/df["Omnichannel_order"]

cltv_df.head()

bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(cltv_df["frequency"],
        cltv_df["recency_cltv_weekly"],
        cltv_df["T_weekly"])


cltv_df["exp_sales_3_month"] = bgf.predict(4*3,
                                           cltv_df["frequency"],
                                           cltv_df["recency_cltv_weekly"],
                                           cltv_df["T_weekly"])

cltv_df["exp_sales_6_month"] = bgf.predict(4*6,
                                           cltv_df["frequency"],
                                           cltv_df["recency_cltv_weekly"],
                                           cltv_df["T_weekly"])


cltv_df[["exp_sales_3_month","exp_sales_6_month"]]

cltv_df.sort_values("exp_sales_3_month",ascending=False)[:10]
cltv_df.sort_values("exp_sales_6_month",ascending=False)[:10]


ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv_df["frequency"],cltv_df["monetary_cltv_avg"])
cltv_df["exp_avarage_value"]=ggf.conditional_expected_average_profit(cltv_df["frequency"],
                                                                     cltv_df["monetary_cltv_avg"])

cltv_df.head()


cltv = ggf.customer_lifetime_value(bgf,
                                   cltv_df["frequency"],
                                   cltv_df["recency_cltv_weekly"],
                                   cltv_df["T_weekly"],

                                   cltv_df["monetary_cltv_avg"],
                                   time=6,
                                   freq="W",
                                   discount_rate=0.01
                                   )
cltv_df["cltv"] = cltv

cltv_df.sort_values("cltv",ascending=False)[:20]

cltv_df["cltv_segment"] = pd.qcut(cltv_df["cltv"],4,labels=["D","C","B","A"])
cltv_df.head()