# -*- coding: utf-8 -*-

import datetime
import time
import os, json
import random
from coincheck.coincheck import CoinCheck
import logging

CC_API_KEY = 'API_KEY'
CC_API_SECRET = 'API_SECRET'

DATA_NAME = "ShioriCcIdouBTCJPYData.txt"
LOGALL_NAME = "ShioriCcIdouBTCJPYAll.log"
LOGTRADE_NAME = "ShioriCcIdouBTCJPYTrade.log"

MAX_RATE = 8
MAX_MEANDIFF4 = 2
MAX_MEANDIFF8 = 2

def GetRateA(repeat=1) :

   # Coincheck
   rateNow = 0.0
   rateBuy = 0.0
   rateSell = 0.0
   for i in range(repeat) :
       # Rate
       res = Cc.ticker.all() 
       rate = json.loads(res)
       rateNow += (float(rate["bid"]) + float(rate["ask"])) / 2.0
       rateBuy += float(rate["ask"])
       rateSell += float(rate["bid"])
   rateNow /= repeat
   rateBuy /= repeat
   rateSell /= repeat
   return rateNow,rateBuy,rateSell

def GetBalanceA() :

   # Coincheck
   # Balance
   res = Cc.account.balance()
   balance = json.loads(res)
   if (balance["success"] == False) :
       raise Exception(balance["error"])
   else :
       return balance["jpy"],balance["btc"]

def BuyA(rate,amount) :

   # Coincheck
   params = {
      'rate': "{0:.8f}".format(rate),
      'amount': amount,
      'order_type': 'buy',
      'pair': 'btc_jpy'
   }
   res = Cc.order.create(params)
   order = json.loads(res)
   if (order["success"] == False) :
       raise Exception(order["error"])

def SellA(rate,amount) :

   # Coincheck
   params = {
      'rate': "{0:.8f}".format(rate),
      'amount': amount,
      'order_type': 'sell',
      'pair': 'btc_jpy'
   }
   res = Cc.order.create(params)
   order = json.loads(res)
   if (order["success"] == False) :
       raise Exception(order["error"])

def OpensA() :

   # Coincheck
   params = {
   }
   res = Cc.order.opens(params);
   orders = json.loads(res)
   if (orders["success"] == False) :
       raise Exception(orders["error"])
   if (orders['orders'] != []) :
       return orders['orders'][0]["id"]
   else :
       return 0

def CancelA(orderid) :

   # Coincheck
   params = {
      'id': orderid
   }
   res = Cc.order.cancel(params)
   cancel = json.loads(res)
   if (cancel["success"] == False) :
       raise Exception(cancel["error"])

def GetFile() :

   global Count,CcRateNow,MeanDiff4,MeanDiff8,BalanceBought

   # タイムスタンプ
   now = datetime.datetime.today();
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   
   if (os.path.isfile(DATA_NAME) == False) :
       # 【重要】プログラム初回起動時前にデータファイルを削除しておくこと。
       Count = 0
       msg = "データファイルが存在しません。"
       toLog(d, msg, "TA")
       print (d+" "+msg)
       return True;
   else :
       # データファイル読み込み
       try :
           h = open(DATA_NAME,"r")
           x = json.load(h)
           h.close()
       except Exception as e :    
           msg = "データファイルの読み込みに失敗しました。("+str(e.args)+")\n"
           toLog(d, msg, "A")
           print (d+" "+msg)
           return False
       
   # 代入 
   Count = x["Count"]
   BalanceBought = x["BalanceBought"]
   Rate = x["Rate"]
   MeanDiff4 = x["MeanDiff4"]
   MeanDiff8 = x["MeanDiff8"]
   # シフト
   for i in range(MAX_RATE-1) :
       Rate[i] = Rate[i+1] 
   Rate[MAX_RATE-1] = CcRateNow
   for i in range(MAX_MEANDIFF4-1) :
       MeanDiff4[i] = MeanDiff4[i+1]
   for i in range(MAX_MEANDIFF8-1) :
       MeanDiff8[i] = MeanDiff8[i+1]
   # カウント
   Count += 1
   # ログ
   y = json.dumps(x)
   msg = "File Read:" #+y
   toLog(d, msg, "A")
   print (d+" "+msg)
   return True

# Coincheck から情報を取得する
# 戻り値：　TRUE　成功
#         FALSE 失敗 
def GetCoincheck() :
   
   global CcRateNow,CcRateBuy,CcRateSell,BalanceJPY,BalanceBTC
   global F_Buy,F_Sell,F_Non
   global BalanceBought

   # タイムスタンプ
   now = datetime.datetime.today();
   d = now.strftime("%Y/%m/%d %H:%M:%S")

   try :
       # Rate
       CcRateNow,CcRateBuy,CcRateSell = GetRateA(1)
   except Exception as e :
       msg = "CcRate の取得に失敗しました。("+str(e.args)+")\n"
       toLog(d, msg, "TA")
       print (d+" "+msg)
       return False

   try :    
       # Balance
       BalanceJPY,BalanceBTC = GetBalanceA()
   except Exception as e :
       msg = "Balance の取得に失敗しました。("+str(e.args)+")\n"
       toLog(d, msg, "TA")
       print (d+" "+msg)
       return False
   # ログ
   if (F_Buy == True) :
       msg = "RateBuy:"+"{0:.8f}".format(CcRateBuy)+"(JPY) BalanceJPY:" \
              +str(BalanceJPY)+"(JPY) BalanceBTC:"+str(BalanceBTC)+"(BTC) BalanceAll:" \
              +"{0:.8f}".format(float(BalanceJPY) + float(BalanceBTC) * float(CcRateBuy))+"(JPY)"
   elif (F_Sell == True) :
       msg = "RateSell:"+"{0:.8f}".format(CcRateSell)+"(JPY) BalanceJPY:" \
              +str(BalanceJPY)+"(JPY) BalanceBTC:"+str(BalanceBTC)+"(BTC) BalanceAll:" \
              +"{0:.8f}".format(float(BalanceJPY) + float(BalanceBTC) * float(CcRateSell))+"(JPY)"
        # profits は厳密に計算しない。参考程度に。。
       profits = (float(BalanceJPY) + float(BalanceBTC) * float(CcRateNow)) - float(BalanceBought)
       msg2 = "Profits:"+"{0:.8f}".format(profits)+"(JPY)"
       toLog(d, msg2, "TA")
       print (d+" "+msg2)
   else :
       msg = "RateMean:"+"{0:.8f}".format(CcRateNow)+"(JPY) BalanceJPY:" \
              +str(BalanceJPY)+"(JPY) BalanceBTC:"+str(BalanceBTC)+"(BTC) BalanceAll:" \
              +"{0:.8f}".format(float(BalanceJPY) + float(BalanceBTC) * float(CcRateBuy))+"(JPY)"
   toLog(d, msg, "TA")
   print (d+" "+msg)
   return True

def Calcurate() :

   global Count,MeanDiff4,MeanDiff8,Amount,Rate
   global CcRateBuy,CcRateSell,CcRateNow
   global BalanceJPY,BalanceBTC

   if (Count < MAX_RATE) :
       # タイムスタンプ
       now = datetime.datetime.today()
       d = now.strftime("%Y/%m/%d %H:%M:%S")
       msg = "Calcurate はキャンセルされました。"
       toLog(d, msg, "A")
       print (d+" "+msg)
       return

   # 移動平均を計算している （必要に応じて修正）
   # 移動平均１回
   Mean1= Rate[MAX_RATE-1]
   # 移動平均４回
   sum = 0.0
   for i in range(4) :
       sum += Rate[i]
   Mean4 = sum / 4.0
   MeanDiff4[MAX_MEANDIFF4-1] = Mean1 - Mean4
   # 移動平均８回
   sum = 0.0
   for i in range(8) :
       sum += Rate[i]
   Mean8 = sum / 8.0
   MeanDiff8[MAX_MEANDIFF8-1] = Mean4 - Mean8

   # タイムスタンプ
   now = datetime.datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   Amount = 0.0
   # 買い条件を決めているところ（要修正）     
   # 買い注文
   if ((Amount == 0.0)\
                and (MeanDiff4[MAX_MEANDIFF4-1] >= 0 and MeanDiff4[MAX_MEANDIFF4-2] < 0)) :
       Amount = 0.005 #round(float(BalanceJPY) * 0.999999 / float(CcRateBuy) - 0.0005,4)
       if (Amount < 0.005) : # Coincheck の最小売買単位
           Amount = 0.0
       msg = "Calcurate Amount(Buy):"+str(Amount)
       toLog(d, msg, "A");
       print (d+" "+msg)

   # 売り条件を決めているところ（要修正）     
   # 売り注文
   if ((Amount == 0.0) \
                and (Rate[MAX_RATE-1] < Rate[MAX_RATE-2])) :
       Amount = -0.005 #float(BalanceBTC)
       if (-Amount < 0.005) : # Coincheck の最小売買単位
           Amount = 0.0
       msg = "Calcurate Amount(Sell):"+str(Amount)
       toLog(d, msg, "A");
       print (d+" "+msg)

   # 何もしない
   if (Amount == 0.0) :
       msg = "Calcurate Amount(Non):0.0";
       toLog(d, msg, "A");
       print (d+" "+msg)

def PutCoincheck() :

   global Count,Amount,CcRateBuy,CcRateSell,CcRateNow
   global BalanceJPY,BalanaceBTC,BalanceBought
   global F_Buy,F_Sell,F_Non,F_Cancel,RateNow

   if (Count < MAX_RATE+3) :
       # タイムスタンプ
       now = datetime.datetime.today()
       d = now.strftime("%Y/%m/%d %H:%M:%S")
       msg = "PutCoincheck はキャンセルされました。";
       toLog(d, msg, "A")
       print (d+" "+msg)
       return

   F_Buy = False
   F_Sell = False
   F_Cancel = False
   # タイムスタンプ
   now = datetime.datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   if (Amount > 0.0) :
       try :             
           # 買い注文
           balancebuy = float(BalanceJPY) + float(BalanceBTC) * float(CcRateNow)
           BuyA(CcRateBuy,Amount)
           msg = "注文（買い）を出しました。"
           toLog(d, msg, "TA")
           print (d+" "+msg)
       except Exception as e :
           msg = "注文（買い）に失敗しました。"+str(e.args)
           toLog(d, msg, "TA")
           print (d+" "+msg)
           return False
        # 約定待ち （必要に応じて修正、単位は秒）
       time.sleep(20)
        # タイムスタンプ
       now = datetime.datetime.today()
       d = now.strftime("%Y/%m/%d %H:%M:%S")
       try :
           orderid = OpensA()
       except Exception as e :
           msg = "未約定注文一覧の取得に失敗しました。"+str(e.args)
           toLog(d, msg, "TA");
           print (d+" "+msg)
           return False
       if (orderid != 0) :
           try :
               CancelA(orderid)
               msg = "注文をキャンセルしました。" 
               toLog(d, msg, "TA");
               print (d+" "+msg)
               F_Cancel = True
               return True
           except Exception as e :
               msg = "キャンセルに失敗しました。"+str(e.args)
               toLog(d, msg, "TA")
               print (d+" "+msg)
               BalanceBought = balancebuy
               F_Buy = True
               return False

       BalanceBought = balancebuy
       msg = "Buy "+str(Amount)+"(BTC)"
       toLog(d,msg,"TA")
       print (d+" "+msg)
       F_Buy = True
       return True

   elif (Amount < 0.0) :
       try : 
           # 売り注文
           SellA(CcRateSell,-Amount)
           msg = "注文（売り）を出しました。"
           toLog(d, msg, "TA")
           print (d+" "+msg)
       except Exception as e :
           msg = "注文（売り）に失敗しました。"+str(e.args)
           toLog(d, msg, "TA")
           print (d+" "+msg)
           return False
        # 約定待ち （必要に応じて修正、単位は秒）
       time.sleep(20)
        # タイムスタンプ
       now = datetime.datetime.today()
       d = now.strftime("%Y/%m/%d %H:%M:%S")
       try :
           orderid = OpensA()
       except Exception as e :
           msg = "未約定注文一覧の取得に失敗しました。"+str(e.args)
           toLog(d, msg, "TA");
           print (d+" "+msg)
           return False
       if (orderid != 0) :
           try :
               CancelA(orderid)
               msg = "注文をキャンセルしました。" 
               toLog(d, msg, "TA");
               print (d+" "+msg)
               F_Cancel = True
               return True
           except Exception as e :
               msg = "キャンセルに失敗しました。"+str(e.args)
               toLog(d, msg, "TA")
               print (d+" "+msg)
               Pos = 0.0
               F_Sell = True
               return False

       msg = "Sell "+str(Amount)+"(BTC)"
       toLog(d,msg,"TA")
       print (d+" "+msg)
       F_Sell = True
       return True

   else :
       # 何もしない
       msg = "non:0.0(BTC)";
       toLog(d, msg, "A");
       print (d+" "+msg)
       F_Non = True
       return True

def PutFile() :

   global Count,Pos,Rate,MeanDiff4,MeanDiff8,BalanceBought

   # タイムスタンプ
   now = datetime.datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   # Json
   x = {"Date":d,"Count":Count,"BalanceBought":BalanceBought,"Rate":Rate, \
        "MeanDiff4":MeanDiff4,"MeanDiff8":MeanDiff8}
   y = json.dumps(x)
   try :
       h = open(DATA_NAME,"w")
       h.write(y)
       h.flush()
       h.close()
   except Exception as e :    
       msg = "データファイルの書き込みに失敗しました。("+str(e.args)+")\n"
       toLog(d, msg, "A")
       print (d+" "+msg)
       return
   msg = "File Write:" #+y
   toLog(d, msg, "A")
   print (d+" "+msg)

#
# ログファイルへ書き込み
#

def toLog(time, msg, opt) :
   x = time + " " + msg
   if (opt == "TA" or opt == "AT") :
       LogAll(x+"\n");
       LogTrade(x+"\n")
   elif (opt == "A") :
       LogAll(x+"\n");
   elif (opt == "T") :
       LogTrade(x+"\n")

def LogAll(str) :

   try :
       h = open(LOGALL_NAME,"a")
       h.write(str)
       h.flush()
       h.close()
   except Exception as e :    
       print ("ログファイル（All）の書き込みに失敗しました。("+str(e.args)+")")

def LogTrade(str) :

   try :
       h = open(LOGTRADE_NAME,"a")
       h.write(str)
       h.flush()
       h.close()
   except Exception as e :    
       print ("ログファイル（Trade）の書き込みに失敗しました。("+str(e.args)+")")

#
# main
#

def main() :

   global BalanceJPY,BalanceBTC
   global Count,MeanDiff4,MeanDiff8,Rate
   global BalanceBought,F_Buy,F_Sell,F_Non,F_Cancel
   global Cc

   while True :

       # タイムスタンプ
       now = datetime.datetime.today()
       d = now.strftime("%Y/%m/%d %H:%M:%S")
       msg = "Start:"+str(__file__)
       toLog(d, msg, "A")
       print (d + " " + msg)

       Rate = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0] # MAX_RATE
       MeanDiff4 = [0.0,0.0] # MAX_MEANDIFF4
       MeanDiff8 = [0.0,0.0] # MAX_MEANDIFF8
       BalanceBought = 0.0 
       F_Buy = False
       F_Sell = False
       F_Non = False

       Cc = CoinCheck(CC_API_KEY, CC_API_SECRET)

       # stop というファイルが存在すれば以降の処理をキャンセルする
       if os.path.exists('stop') :
           # タイムスタンプ
           now = datetime.datetime.today();
           d = now.strftime("%Y/%m/%d %H:%M:%S")
           msg = "stop ファイルが存在するため実行をキャンセルしました。"
           toLog(d, msg, "A")
           print (d + " " + msg+"\n")
           # タイムスタンプ
           now = datetime.datetime.today();
           d = now.strftime("%Y/%m/%d %H:%M:%S")
           msg = "End"
           toLog(d, msg+"\n", "A")
           print (d + " " + msg+"\n")
           continue

       # Coincheck から Rate や Balance を取得する
       if (GetCoincheck() == False) :
           # タイムスタンプ
           now = datetime.datetime.today();
           d = now.strftime("%Y/%m/%d %H:%M:%S")
           msg = "End"
           toLog(d, msg+"\n", "A")
           print (d + " " + msg+"\n")
           continue

        # ファイルに保存してあったデータをロードする
       if (GetFile() == False) :
           # タイムスタンプ
           now = datetime.datetime.today();
           d = now.strftime("%Y/%m/%d %H:%M:%S")
           msg = "End"
           toLog(d, msg+"\n", "A")
           print (d + " " + msg+"\n")
           continue

        # 売買条件が成立しているか判断する
       Calcurate()

       # stop-trade というファイルが存在すれば実際の売買は行わない
       if os.path.exists('stop-trade') :
           # タイムスタンプ
           now = datetime.datetime.today();
           d = now.strftime("%Y/%m/%d %H:%M:%S")
           msg = "stop-trade ファイルが存在するため PutCoincheck をキャンセルしました。"
           toLog(d, msg, "A")
           print (d + " " + msg+"\n")
       else :
             # 実際の売買
           for i in range(10) :
               F_Buy = False
               F_Sell = False
               F_Cancel = False
               PutCoincheck()
               if (F_Cancel == False) :
                   break
                 # キャンセルした場合は Rate,Balance を取得し直し売買条件が成立するか判断する
               GetCoincheck()
               Calcurate()
　　　　　　　　　time.sleep(4)

       Cc = CoinCheck(CC_API_KEY, CC_API_SECRET)
        # 売買後の Balance を取得する（表示用）
       GetCoincheck()
        # データをファイルに保存する
       PutFile()

        # タイムスタンプ
       now = datetime.datetime.today();
       d = now.strftime("%Y/%m/%d %H:%M:%S")
       msg = "End"
       toLog(d, msg+"\n", "A")
       print (d + " " + msg + "\n")

        # ２分３０秒のウエイト
       time.sleep(150)

if __name__ == "__main__":
   main()