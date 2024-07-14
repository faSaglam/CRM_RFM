# customer lifetime value

## satın alma başına ortalama kazanç * satın alma sayısı

## CLTV = (Customer Value / Churn Rate) * Profit Margin

## Customer Value = Purchase Freq * Avarage Order Val.

## CLTV = Expected Number of Transaction * Expected Average Profit

## CLTV = BG/NBD Model * Gamma Gamma Submodel

## ÖZET : KİTLESEN DAVRANIŞI KİŞİYE İNDİRGENEREK İŞLEM YAPILACAKTIR.

###########################
# Beta Geometric / Negative Binomial Distribution ile Expected Number Of Transaction

# Rasssal değişken (random var.)

# BUY TILL YOU DIE (BG /NBD)

# Trancation Process (Buy) + Dropout Process (Till you die)

# Transaction Process (Buy)#
# Bir müşteri canlı olduğu sürece kendi transaction rate'i etrafında rastgele satın alım yapmaya devam edecektir.
# Transaction rate ile possion dağılır
# Transaction rateler her müşteriye göre değişir. ve tüm kitle için gama dağılır (r,a)
#
# Dropout Process (Till you die)
# her müşterinin p olasığılı ile dropout rate'i vardır (churn olma)
#  her bir müşteri için değişir tüm kitle için beta dağılır (a,b)

# gama dağılım + beta dağılım


###########################


# Gamma Gamma Submodel : müşterinin işlem başına ort. ne kadar kar getireceğini tahmnin etmek için kullanılır.

# avarage order val. olasılıksal değeri

# monetary'nin ortalaması

# zamanla kullanıcılar arasında değişir ama tek bir kullanıcı için değişmez

# tüm müşteriler arasında gama dağılır


############################

