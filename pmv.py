#!/usr/bin/env python
# coding: utf-8

# # PMV計算、および快適温度算出ツール
# 最終更新：2021/12/16

# In[1]:


import math
import numpy as np


# ## PMVの算出

# In[2]:


#飽和蒸気圧[kPa]の計算
def FNPS(T):
    fnps = math.exp(16.6536-4030.183/(T+235))
    return fnps
    


#PMV,PPD計算用関数の定義

"""
input
    CLO=着衣量[clo]
    MET=代謝率[met]
    WME=外部仕事量[met]
    TA=大気温[℃]
    TR=平均放射温度[℃]
    VEL=相対風速[m/s]
    RH=相対湿度[%]=水蒸気量/飽和水蒸気量

output
    PMV
    PPD[%]
"""


def calc_pmv(CLO,MET,WME,TA,TR,VEL,RH):
    # 相対湿度から水蒸気圧PA[Pa]の算出
    PA=RH*10*FNPS(TA)

    #ICL=衣服の基本熱抵抗[m^2 K/W]の算出
    ICL = 0.155 * CLO
    M = MET * 58.15 
    W = WME * 58.15
    MW = M - W

    #衣類表面係数の計算
    if ICL < 0.078:
        FCL = 1 + 1.29 * ICL
    else:
        FCL = 1.05+0.645*ICL

    #強制対流熱伝達
    HCF = 12.1 * math.sqrt(VEL)

    #大気温をセルシウス温度から絶対温度に変換
    TAA = TA + 273

    #平均放射温度をセルシウス温度から絶対温度に変換
    TRA = TR + 273

    #　反復による表面温度の計算
    TCLA = TAA + (35.5-TA) / (3.5*(6.45*ICL+0.1))
    P1 = ICL * FCL
    P2 = P1 * 3.96
    P3 = P1 * 100
    P4 = P1 * TAA
    P5 = 308.7 - 0.028 * MW +P2 * (TRA/100) ** 4
    XN = TCLA / 100
    XF = XN
    N=0 #反復数 Number of iterations
    EPS = 0.00015

    XF = (XF+XN) / 2
    HCN=2.38*abs(100*XF-TAA)**0.25
    if HCF>HCN:
        HC=HCF
    else:
        HC=HCN
    XN=(P5+P4*HC-P2*XF**4) / (100+P3*HC)
    N=N+1

    while abs(XN-XF)>EPS:
        XF = (XF+XN) / 2
        HCN=2.38*abs(100*XF-TAA)**0.25
        if HCF>HCN:
            HC=HCF
        else:
            HC=HCN
        XN=(P5+P4*HC-P2*XF**4) / (100+P3*HC)
        N=N+1
        if N>150:
            print(N)
            break

    TCL=100*XN-273

    # 熱損失コンポーネント

    HL1 = 3.05*0.001*(5733-6.99*MW-PA)
    if MW > 58.15:
        HL2 = 0.42 * (MW-58.15)
    else:
        HL2 = 0

    HL3 = 1.7 * 0.00001 * M * (5867-PA)
    HL4 = 0.0014 * M * (34-TA)
    HL5 = 3.96*FCL*(XN**4-(TRA/100)**4)
    HL6 = FCL * HC * (TCL-TA)

    # PMV算出
    TS = 0.303 * math.exp(-0.036*M) + 0.028
    PMV = TS * (MW-HL1-HL2-HL3-HL4-HL5-HL6)
    PPD=100-95*math.exp(-0.03353*PMV**4-0.2179*PMV**2)

    return PMV,PPD


# ## 快適温度算出関数(個人差考慮なし)

# In[3]:


#快適温度算出関数(個人差考慮なし)
"""
input
    PPD_lim:不満足度率の上限[%] Eg. 5
    CLO:着衣量[clo] Eg. 1clo
    MET:代謝率[met] Eg. 1.2
    WME:外部仕事量[met] Eg. 0
    VEL:相対風速[m/s] Eg. 0.1
    RH:相対湿度[%]=水蒸気量/飽和水蒸気量 Eg. 入力

output
    快適温度[℃]
    快適温度下限[℃]
    快適温度上限[℃]
"""

#温度走査範囲
temp_min=14
temp_max=28
temp_step=0.1


def calc_comf_temp(PPD_lim,CLO,MET,WME,VEL,RH):
    comf_temp_min=16
    comf_temp_max=28
    comf_temp=23
    PPD_min=100
    for temp in np.arange(temp_min,temp_max,temp_step):
        PMV,PPD=calc_pmv(CLO,MET,WME,temp,temp,VEL,RH)
        if PPD<PPD_lim:
            comf_temp_min=temp
            break
    
    for temp in np.arange(temp_max,temp_min,-temp_step):
        PMV,PPD=calc_pmv(CLO,MET,WME,temp,temp,VEL,RH)
        if PPD<PPD_lim:
            comf_temp_max=temp
            break
    
    for temp in np.arange(comf_temp_min,comf_temp_max,temp_step):
        PMV,PPD=calc_pmv(CLO,MET,WME,temp,temp,VEL,RH)
        if PPD<PPD_min:
            PPD_min=PPD
            comf_temp=temp
        if PPD>PPD_min:
            break
    
    return comf_temp,comf_temp_min,comf_temp_max


# ## 快適温度算出関数(個人差考慮あり)

# In[4]:


"""
基礎代謝算出関数(改良版ハリス・ベネディクト方程式)
参考：https://keisan.casio.jp/exec/system/1161228736

input
    AGE:年齢[歳]
    SEX:性別("male"or"female")
    HEIGHT:身長[cm]
    WEIGHT:体重[kg]

output
    基礎代謝量[kcal]
"""

def calc_bmr(AGE,SEX,HEIGHT,WEIGHT):
    if SEX == "male":
        return 13.397*WEIGHT+4.799*HEIGHT-5.677*AGE+88.362
    elif SEX == "female":
        return 9.247*WEIGHT+3.098*HEIGHT-4.33*AGE+447.593
    else:
        print("Please enter \"male\" or \"female\" for the variable \"SEX\".")
        return -1







"""
体表面積算出関数(デフォルトはデュポア式)
参考：https://keisan.casio.jp/exec/system/1161228735

input
    HEIGHT:身長[cm]
    WEIGHT:体重[kg]
    method:"DuBois" or "Shintani" or "Fujimoto" or "Average"

output
    体表面積[m^2]
"""

def calc_bsa(HEIGHT,WEIGHT,method="DuBois"):
    if method=="DuBois":
        return (HEIGHT**0.725)*(WEIGHT**0.425)*0.007184
    elif method=="Shintani":
        return (HEIGHT**0.725)*(WEIGHT**0.425)*0.007358
    elif method=="Fujimoto":
        return (HEIGHT**0.663)*(WEIGHT**0.444)*0.008883
    elif method=="Average":
        return (((HEIGHT**0.725)*(WEIGHT**0.425)*0.007184)+((HEIGHT**0.725)*(WEIGHT**0.425)*0.007358)+((HEIGHT**0.663)*(WEIGHT**0.444)*0.008883))/3
    else:
        print("Please enter \"DuBois\" or \"Shintani\" or \"Fujimoto\" or \"Average\" for the variable \"method\".")
        return -1







"""
快適温度算出関数(個人差考慮)

input
    PPD_lim:不満足度率の上限[%]
    CLO:着衣量[clo]
    MET:代謝率[met]
    WME:外部仕事量[met]
    VEL:相対風速[m/s]
    RH:相対湿度[%]=水蒸気量/飽和水蒸気量
    AGE:年齢[歳]
    SEX:性別("male"or"female")
    HEIGHT:身長[cn]
    WEIGHT:体重[kg]

output
    快適温度[℃]
    快適温度下限[℃]
    快適温度上限[℃]
"""

#温度走査範囲
temp_min=14
temp_max=28
temp_step=0.1


def calc_comf_temp_p(RH,AGE,SEX,HEIGHT,WEIGHT,PPD_lim=6,CLO=1,MET=1.2,WME=0,VEL=0.1):
    #個人差補正
    MET_p=MET*calc_bmr(AGE,SEX,HEIGHT,WEIGHT)/(calc_bsa(HEIGHT,WEIGHT)*859.1174476)

    comf_temp_min=16
    comf_temp_max=28
    comf_temp=23
    PPD_min=100
    for temp in np.arange(temp_min,temp_max,temp_step):
        PMV,PPD=calc_pmv(CLO,MET_p,WME,temp,temp,VEL,RH)
        if PPD<PPD_lim:
            comf_temp_min=temp
            break
    
    for temp in np.arange(temp_max,temp_min,-temp_step):
        PMV,PPD=calc_pmv(CLO,MET_p,WME,temp,temp,VEL,RH)
        if PPD<PPD_lim:
            comf_temp_max=temp
            break
    
    for temp in np.arange(comf_temp_min,comf_temp_max,temp_step):
        PMV,PPD=calc_pmv(CLO,MET_p,WME,temp,temp,VEL,RH)
        if PPD<PPD_min:
            PPD_min=PPD
            comf_temp=temp
        if PPD>PPD_min:
            break
    return comf_temp,comf_temp_min,comf_temp_max


# # 可視化コーナー

import matplotlib.pyplot as plt

fontsize=15


# In[6]:


#外気温と、PMV,PPDの関係


fig=plt.figure()
ax=fig.add_subplot(111)

#タイトル
ax.set_title("PMV,PPDと気温の関係",fontsize=fontsize)

#温度を16℃から28℃まで変更したときのPPDを描画
ax.plot(np.arange(16,28,0.1),[list(calc_pmv(1,1.2,0,t,t,0.1,50))[1]  for t in np.arange(16,28,0.1)],label="PPD",color="#82BFDA")
ax.set_xlabel("Temperature[℃]",fontsize=fontsize)
ax.set_ylabel("PPD(予測不満足率) [%]",fontsize=fontsize)


#温度を16℃から28℃まで変更したときのPMVを描画
ax1=ax.twinx()
ax1.plot(np.arange(16,28,0.1),[list(calc_pmv(1,1.2,0,t,t,0.1,50))[0]  for t in np.arange(16,28,0.1)],color="orange",label="PMV")
ax1.set_ylabel("PMV",fontsize=fontsize)
fig.legend(loc='upper left',bbox_to_anchor=(0,1), bbox_transform=ax.transAxes)

plt.show
#fig.savefig("PMV_PPD_vs_Temperature.png")


# In[7]:


#PMVとPPD



fig=plt.figure(figsize=(6,4))
ax=fig.add_subplot(111)
ax.plot([list(calc_pmv(1,1.2,0,t,t,0.1,50))[0]  for t in np.arange(10,34,0.1)],[list(calc_pmv(1,1.2,0,t,t,0.1,50))[1]  for t in np.arange(10,34,0.1)],color="black")

#タイトル
ax.set_title("PMVとPPD",fontsize=fontsize)


#x軸の設定
ax.set_xlabel("PMV",fontsize=fontsize)
ax.set_xlim(-2.5,2.5)
ax.set_xticks([i for i in np.arange(-2,2.5,0.5)])

#y軸の設定
ax.set_yticks([0,5,20,40,60,80,100])
ax.set_ylim(0,100)
ax.set_ylabel("PPD(予測不満足率) [%]",fontsize=fontsize)

#PPD 5%のところに水平線を引く
ax.hlines(5,-2.5,2.5,linestyles="dotted",color="black")

#ヒートマップ描画
heat=np.array([[i for i in np.arange(-2.5,2.5,0.1)] for j in np.arange(0,100,1)])
ax.imshow(heat,extent=[-2.5,2.5,0,100],aspect=0.03,cmap="RdBu_r")





#補助線を引く
ax.grid()

plt.show
#fig.savefig("PMV_vs_PPD.png")


# In[ ]:





# # 付録

# ## 着衣量算出ツール

# In[8]:


#着衣量の参考＝http://freehand-japan.com/value/

"""
input
    clothes:着用している衣服のリスト
    SEX:性別("male"or"female")
output
    着衣量[clo]
"""



def calc_clo(clothes,SEX):

    #女性用CLO値
    clo_dict_w={"ブラ":0.01,"女性用ショーツ":0.03,"タンクトップ・キャミソール":0.14,"スリップ":0.16,"Tシャツ":0.08,
"ノースリーブブラウス":0.12,"半袖ポロシャツ":0.17,"薄手半袖ブラウス":0.15,"厚手半袖ブラウス":0.20,"薄手長袖ブラウス":0.18,"厚手長袖ブラウス":0.25,"長袖スウェットシャツ":0.30,
"ショートパンツ":0.06,"七分丈パンツ":0.08,"薄手ズボン":0.15,"厚手ズボン":0.24,"スウェットパンツ":0.28,
"薄手スカート":0.14,"厚手スカート":0.23,
"ノースリーブワンピース":0.25,"半袖ワンピース":0.29,"薄手長袖ワンピース":0.40,"厚手長袖ワンピース":0.50,
"薄手ジャケット":0.34,"厚手ジャケット":0.54,"薄手ジャンパー":0.35,"厚手ジャンパー":0.55,"中綿入りジャンパー":0.65,
"薄手スーツ上下":0.50,"厚手スーツ上下":0.80,
"薄手セーター・カーディガン":0.20,"厚手セーター・カーディガン":0.39,"タートルネックセーター":0.22,
"薄手ベスト":0.13,"厚手ベスト":0.17,
"スプリングコート":0.46,"冬用コート":0.63,
"パンスト・ストッキング":0.02,"足首丈のスポーツソックス":0.02,"ふくらはぎ丈のソックス":0.03,"ハイソックス":0.06,
"サンダル":0.01,"スニーカー":0.02,"革靴":0.03,"ブーツ":0.10,"スリッパ":0.03}

    #男性用CLO値
    clo_dict_m={"半袖シャツ":0.08,"ランニングシャツ":0.05,"ブリーフ・トランクス":0.04,
"半袖ドレスシャツ":0.19,"長袖ドレスシャツ":0.25,"長袖スウェットシャツ":0.34,
"ショートパンツ":0.06,"七分丈パンツ":0.08,"薄手ズボン":0.15,"厚手ズボン":0.24,"スウェットパンツ":0.28,
"薄手ジャケット":0.34,"厚手ジャケット":0.54,"薄手ジャンパー":0.35,"厚手ジャンパー":0.55,"中綿入りジャンパー":0.65,
"夏物スーツ上下":0.60,"合ものスーツ上下":0.80,"冬物スーツ上下":1.00,
"薄手セーター・カーディガン":0.30,"厚手セーター・カーディガン":0.50,"タートルネックセーター":0.22,
"薄手ベスト":0.13,"厚手ベスト":0.17,
"スプリングコート":0.50,"冬用コート":0.71,
"足首丈のスポーツソックス":0.02,"ふくらはぎ丈のソックス":0.03,"ハイソックス":0.06,
"サンダル":0.01,"スニーカー":0.02,"革靴":0.03,"ブーツ":0.10,"スリッパ":0.03
}
    if SEX=="male":
        return sum([clo_dict_m[cloth] for cloth in clothes])
    elif SEX=="female":
        return sum([clo_dict_w[cloth] for cloth in clothes])
    else:
        print("Please enter \"male\" or \"female\" for the variable \"SEX\".")
        return -1
    



