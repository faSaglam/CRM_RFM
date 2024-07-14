#master_id : müşteri idsi
#order_channel: işletim sistemş
#last_order_channel : offline da olabilir
#first_order_date: ilk sipariş tarihi
#last_order_date_online :
#last_order_date_ofline

from datetime import date
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x:'%.4f' % x)
################   Quest 1     ################
# 1
df_ = pd.read_csv("/Case_Study_1_2/flo_data_20k.csv")
df = df_.copy()
# 2
df.head(10) #a
df.shape
df.isnull().sum() # d
df.describe().T # c
df.info()  #b -e
df.nunique()

#3
df["order_num_total_omni"]= df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]

#4
df["first_order_date"]=pd.to_datetime(df["first_order_date"])
df["last_order_date"]=pd.to_datetime(df["last_order_date"])
df["last_order_date_online"]=pd.to_datetime(df["last_order_date_online"])
df["last_order_date_offline"]=pd.to_datetime(df["last_order_date_offline"])

#5
df["customer_value_total"] = df["customer_value_total_ever_offline"]+df["customer_value_total_ever_online"]
df.groupby("order_channel").agg({"master_id":"count",
                                 "order_num_total_omni":"sum",
                                 "customer_value_total":"sum"
                                 })

#6
df.sort_values("customer_value_total",ascending=False)[:10]

#7
df.sort_values("order_num_total_omni",ascending=False)[:10]

#8
def data_ready(dataframe):
    dataframe["order_num_total_omni"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["first_order_date"] = pd.to_datetime(dataframe["first_order_date"])
    dataframe["last_order_date"] = pd.to_datetime(dataframe["last_order_date"])
    dataframe["last_order_date_online"] = pd.to_datetime(dataframe["last_order_date_online"])
    dataframe["last_order_date_offline"] = pd.to_datetime(dataframe["last_order_date_offline"])
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    dataframe.groupby("order_channel").agg({"master_id": "count",
                                     "order_num_total_omni": "sum",
                                     "customer_value_total": "sum"
                                     })
    dataframe.sort_values("customer_value_total", ascending=False)[:10]
    dataframe.sort_values("order_num_total_omni", ascending=False)[:10]



################   Quest 2      ################

df["last_order_date"].max() #2021-05-30 00:00:00
analysis_date = pd.Timestamp(year=2021,month=6,day=1)
#1 - 2 -3
rfm = pd.DataFrame()
rfm["customer_id"] = df["master_id"]


rfm["recency"] = (analysis_date - df["last_order_date"]).dt.days
rfm["frequency"] = df["order_num_total_omni"]
rfm["monetary"] = df["customer_value_total"]

rfm.head()

################   Quest 3       ################

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5]);

rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) +
                    rfm["frequency_score"].astype(str))

################   Quest 4       ################

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_risk',
    r'[1-2][5]': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions',
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

################   Quest 5       ################

rfm[["segment","recency","frequency","monetary"]].groupby("segment").agg(["mean","count"])

#a
target_segments_customer_ids = rfm[rfm["segment"].isin(["champions","loyal_customers"])]["customer_id"]
cust_ids = df[(df["master_id"]).isin(target_segments_customer_ids) &
              (df["interested_in_categories_12"].str.contains("KADIN"))]["master_id"]

cust_ids.to_csv("yeni-marka-hedef-müsteri-id.csv",index=False)
cust_ids.shape

#b
target_segments_customer_ids = rfm[rfm["segment"].isin(["cant_loose","atrisk","hibernating","new_customers"])]["customer_id"]
cust_ids = df[(df["master_id"]).isin(target_segments_customer_ids) &
              ((df["interested_in_categories_12"].str.contains("ERKEK")) |
              df["interested_in_categories_12"].str.contains("COCUK"))]["master_id"]

cust_ids.to_csv("indirim-hedef-müsteri-id.csv",index=False)
cust_ids.shape





