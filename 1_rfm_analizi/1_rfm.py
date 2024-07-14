import datetime
#1. İş Problemi

#Bir e -ticaret sitesinin RFM Analizi

#Veri seti


# Değişkenler.

#InvoiceNo: Fatura Numarası - C ile başlayanlar iptal
#StockCode : Ürün kodu
#Description
#Quantity
#InvoiceDate
#UnitPrice
#CustomerID
#Country

from datetime import date
import pandas as pd
pd.set_option('display.max_columns',None)
pd.set_option('display.float_format',lambda x:'%.3f' % x)

df_ = pd.read_excel("C:/Users/Omer/CRM_RFM/CRM_RFM/online_retail_II.xlsx", sheet_name="Year 2009-2010")
df = df_.copy()
df.head()
df.shape
df.isnull().sum()

df["Description"].nunique()

df["Description"].value_counts().head()

df.groupby("Description").agg({"Quantity":"sum"}).head()

df.groupby("Description").agg({"Quantity":"sum"}).sort_values("Quantity", ascending=False).head()


df["TotalPrice"] = df["Quantity"]*df["Price"]

df.groupby("Invoice").agg({"TotalPrice": "sum"}).head()


# Veri hazırlama

df.dropna(inplace=True) #boş olan verileri sildik

df.describe().T

df = df[~df["Invoice"].str.contains("C", na=False)] # iade olanlar hariç tutuldu


# RFM Metriklerinin Hesaplanması

# Recency , Frequency , Monetary

df.head()
df["InvoiceDate"].max()


today_date = pd.Timestamp(2010,12,11)
print(today_date)

'''
rfm = df.groupby('Customer ID').agg({ 'InvoiceDate':lambda date : (today_date - date.max()).days,
                                      'Invoice':lambda num: num.nunique(),
                                      'TotalPrice': lambda TotalPrice : TotalPrice.sum()})
'''
rfm = df.groupby('Customer ID').agg({
    'InvoiceDate': lambda date: (today_date - date.max()).days,
    'Invoice' : lambda  Invoice : Invoice.nunique(),
    'TotalPrice': lambda TotalPrice : TotalPrice.sum()
                                     })

rfm.head()

rfm.columns = ['recency','frequency','monetary']

rfm.describe().T

##monetary değeri 0 olamaz

rfm = rfm[rfm["monetary"]>0]

rfm.describe().T

rfm.shape

# RFM Skorlarının Hesaplanması

## Recency ters oranlı skordur

## qcut verilen değeri min - max aralığını istenilen parçaya böler
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels = [5,4,3,2,1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first") ,5 , labels=[1,2,3,4,5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"],5,labels =[1,2,3,4,5])

rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) +
                    rfm["frequency_score"].astype(str))

rfm[rfm["RFM_SCORE"] == "55"]

# RFM Segmentlerinin oluşturulması ve analizi


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

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map,regex =True)

rfm[["segment","recency","frequency","monetary"]].groupby("segment").agg(["mean","count"])

rfm[rfm["segment"] == "need_attention"].head()
rfm[rfm["segment"] == "need_attention"].index

new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index
new_df["new_customer_id"] = new_df["new_customer_id"].astype(int)
new_df.to_csv("new_customers.csv")



rfm.to_csv("rfm.csv")

#tüm süreci fonksiyonlaştırma

def create_rfm(dataframe , csv = False):

    #VERIYI HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C",na=False)]

    #RFM METRIKLERININ HAZIRLANMASI
    today_date = pd.Timestamp(2011,12,11)
    rfm = dataframe.groupby("Customer ID").agg({
            'InvoiceDate': lambda date: (today_date - date.max()).days,
            'Invoice' : lambda  Invoice : Invoice.nunique(),
            'TotalPrice': lambda TotalPrice : TotalPrice.sum()
    })

    rfm.columns = ['recency', 'frequency', 'monetary']
    rfm = rfm[rfm["monetary"] > 0]

    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

    rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) +
                        rfm["frequency_score"].astype(str))

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
    rfm = rfm[["segment","recency","frequency","monetary"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")
    return rfm

df = df_.copy()

rfm_new = create_rfm(df)

rfm_new_csv = create_rfm(df,csv=True)
