# 1. verinin hazırlanması
# 2. bg -ndb modeli ile expedted number of transaction
# 3. gamma gamma modeli ile expected av. profit
# 4. bg-nbd ve gamma gamma modeli ile cltv'nin hazırlanması
# 5. cltv'ye göre segmentlerin oluşturulması
# 6. çalışmanın fonksiyonlaştırılması

# 1. Verinin hazırlanması

#bir  e-ticaret şirketi. müşlerilerinin segmenlete ayırıp bu segmenlere göre
# pazarlama stratejileri belirlemek istioyr.

# Değişkenler.

#InvoiceNo: Fatura Numarası - C ile başlayanlar iptal
#StockCode : Ürün kodu
#Description
#Quantity
#InvoiceDate
#UnitPrice
#CustomerID
#Country


# kütüphaneler

# pip install lifetimes
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x:'%.4f' % x)

from sklearn.preprocessing import  MinMaxScaler

## ilk önce aykırı değerlerini tespit edilir ve baskılanır.

def outlier_thresholds(dataframe , variable):
    quartile1 = dataframe[variable].quantile(0.01) # normalde %25
    quartile3 = dataframe[variable].quantile(0.99) # normalde %75
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 -1.5 * interquantile_range
    return  low_limit, up_limit

## outlier_thresholds eşik değer belirler

def replace_with_thresholds(dataframe , variable):
    low_limit, up_limit = outlier_thresholds(dataframe,variable)
    dataframe.loc[(dataframe[variable]) < low_limit, variable] = low_limit
    dataframe.loc[(dataframe[variable]) > up_limit, variable] = up_limit

## replace_with_thresholds alt veya üst limiti geçen değerler yerine eşikleri yerleştir.

df_ = pd.read_excel("C:/Users/Omer/CRM_RFM/CRM_RFM/2_musteri_yasam_boyu_degeri/online_retail_II.xlsx", sheet_name="Year 2010-2011")

df = df_.copy()
df.describe().T
df.head()
df.isnull().sum()
##########

#Veri Ön İşleme

#########

df.dropna(inplace=True)
df = df[~df["Invoice"].str.contains("C", na=False)]
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]

replace_with_thresholds(df, "Quantity")
replace_with_thresholds(df, "Price")

df["TotalPrice"] = df["Quantity"] * df["Price"]

today_date = pd.Timestamp(2011,12,11)




# Lifetime Veri  Yapısının Hazırlanması


#receny : son satın alma üzerinden geçen zaman - Haftalık
#T : müşterinin yaşı . Haftalık  - ilk satın alım
# frequency : tekrar eden toplam satın alma sayısı  (frequency>1)
# monetary: satın alma başına ortalma kazanç


cltv_df = (df.groupby("Customer ID")
           .agg({"InvoiceDate": [lambda date: (date.max() - date.min()).days,
                                 lambda date : (today_date - date.min()).days],
                  "Invoice": lambda num: num.nunique(),
                  "TotalPrice": lambda TotalPrice : TotalPrice.sum()
               }))



cltv_df.columns = cltv_df.columns.droplevel(0)

cltv_df.columns = ['recency',"T","frequency","monetary"]

cltv_df.describe().T

cltv_df = cltv_df[(cltv_df["frequency"] > 1 )] # birden büyük olanlar devamlı müşteri

cltv_df["receny"] = cltv_df["recency"]/7 #haftalık veriye çevirdik
cltv_df["T"] = cltv_df["T"]/7 #haftalık veriye çevirdik


# BD-NBD Modelinin kurulması

bgf = BetaGeoFitter(penalizer_coef=0.001) #ceza katsayısı



bgf.fit(cltv_df["frequency"],
        cltv_df["recency"],
        cltv_df["T"])

#1 hafta içinde en çok satın alma beklediğimiz 10 müşteri kimdir?

bgf.conditional_expected_number_of_purchases_up_to_time(1, #haftalık değer
                                                        cltv_df["frequency"],
                                                        cltv_df["recency"],
                                                        cltv_df["T"]).sort_values(ascending=False).head(10)

bgf.predict(1, #haftalık değer
                                                        cltv_df["frequency"],
                                                        cltv_df["recency"],
                                                        cltv_df["T"]).sort_values(ascending=False).head(10)


# bgf için predict kullanabilir ama gama gama için kullanılmaz


cltv_df["expected_purc_1_week"] = bgf.predict(1, #haftalık değer
                                                        cltv_df["frequency"],
                                                        cltv_df["recency"],
                                                        cltv_df["T"])


# 1 ay içinde en çok satış yapılacak olan 10 müşteri

cltv_df["expected_purc_1_month"] = bgf.predict(4, #haftalık değer
                                                        cltv_df["frequency"],
                                                        cltv_df["recency"],
                                                        cltv_df["T"])


# Tahmin sonuçlarının değerlendirilmesi

plot_period_transactions(bgf)
plt.show()

#Gamma Gamma Modelinin kurulması

ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv_df["frequency"], cltv_df["monetary"])

ggf.conditional_expected_average_profit(cltv_df["frequency"],
                                        cltv_df["monetary"]).sort_values(ascending=False).head(10)

cltv_df["expected_avarage_profit"] = ggf.conditional_expected_average_profit(cltv_df["frequency"],
                                                                             cltv_df["monetary"])

cltv_df.sort_values("expected_avarage_profit",ascending=False).head(10)

# BG- NBD ve  GG modeli ile CLTV 'nin hesaplanması

cltv = ggf.customer_lifetime_value(bgf,
                                   cltv_df["frequency"],
                                   cltv_df["recency"],
                                   cltv_df["T"],
                                   cltv_df["monetary"],
                                   time=1, # 1 aylık
                                   freq="W" , #Tnin frekans bilgisi W = week
                                    discount_rate=0.01)

cltv.head()

cltv = cltv.reset_index()

cltv_final = cltv_df.merge(cltv, on="Customer ID", how="left")
cltv_final.sort_values(by="clv", ascending=False).head(10)


# CLTV'ye göre Segmentlerin Oluşturulması


cltv_final["segment"] = pd.qcut(cltv_final["clv"],4,labels =["D", "C", "B", "A"])

cltv_final.sort_values(by="clv", ascending=False).head(50)

cltv_final.groupby("segment").agg(
    {"count","mean","sum"}
)

#Fonksiyonlaştırma

def create_cltv_p(dataframe,month=3):
    #1. veri ön işleme
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C",na=False)]
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe = dataframe[dataframe["Price"] > 0]
    replace_with_thresholds(dataframe, "Quantity")
    replace_with_thresholds(dataframe, "Price")
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    today_date = pd.Timestamp(2011,12,11)

    cltv_df = dataframe.groupby("Customer ID").agg(
        {"InvoiceDate":[lambda  InvoiceDate:(InvoiceDate.max() - InvoiceDate.min()).days,
                        lambda  InvoiceDate : (today_date - InvoiceDate.min()).days],
         "Invoice" : lambda  Invoice : Invoice.nunique(),
         "TotalPrice": lambda  TotalPrice : TotalPrice.sum()}

    )
    cltv_df.columns = cltv_df.columns.droplevel(0)

    cltv_df.columns = ['recency', "T", "frequency", "monetary"]

    cltv_df = cltv_df[(cltv_df["frequency"] > 1)]  # birden büyük olanlar devamlı müşteri

    cltv_df["receny"] = cltv_df["recency"] / 7  # haftalık veriye çevirdik
    cltv_df["T"] = cltv_df["T"] / 7  # haftalık veriye çevirdik

    # BD-NBD Modelinin kurulması

    bgf = BetaGeoFitter(penalizer_coef=0.001)  # ceza katsayısı

    bgf.fit(cltv_df["frequency"],
            cltv_df["recency"],
            cltv_df["T"])

    bgf.conditional_expected_number_of_purchases_up_to_time(1,  # haftalık değer
                                                            cltv_df["frequency"],
                                                            cltv_df["recency"],
                                                            cltv_df["T"]).sort_values(ascending=False).head(10)

    bgf.predict(1,  # haftalık değer
                cltv_df["frequency"],
                cltv_df["recency"],
                cltv_df["T"]).sort_values(ascending=False).head(10)

    # bgf için predict kullanabilir ama gama gama için kullanılmaz

    cltv_df["expected_purc_1_week"] = bgf.predict(1,  # haftalık değer
                                                  cltv_df["frequency"],
                                                  cltv_df["recency"],
                                                  cltv_df["T"])


    # Gamma Gamma Modelinin kurulması

    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(cltv_df["frequency"], cltv_df["monetary"])

    ggf.conditional_expected_average_profit(cltv_df["frequency"],
                                            cltv_df["monetary"]).sort_values(ascending=False).head(10)

    cltv_df["expected_avarage_profit"] = ggf.conditional_expected_average_profit(cltv_df["frequency"],
                                                                                 cltv_df["monetary"])

    cltv_df.sort_values("expected_avarage_profit", ascending=False).head(10)

    # BG- NBD ve  GG modeli ile CLTV 'nin hesaplanması

    cltv = ggf.customer_lifetime_value(bgf,
                                       cltv_df["frequency"],
                                       cltv_df["recency"],
                                       cltv_df["T"],
                                       cltv_df["monetary"],
                                       time=1,  # 1 aylık
                                       freq="W",  # Tnin frekans bilgisi W = week
                                       discount_rate=0.01)

    cltv = cltv.reset_index()

    cltv_final = cltv_df.merge(cltv, on="Customer ID", how="left")
    cltv_final.sort_values(by="clv", ascending=False)

    # CLTV'ye göre Segmentlerin Oluşturulması

    cltv_final["segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])

    cltv_final.sort_values(by="clv", ascending=False).head(50)

    cltv_final.groupby("segment").agg(
        {"count", "mean", "sum"}
    )











