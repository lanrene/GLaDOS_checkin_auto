import requests,json,os
# -------------------------------------------------------------------------------------------
# github workflows
# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # pushplus秘钥 申请地址 http://www.pushplus.plus
    sckey = os.environ.get("PUSHPLUS_TOKEN", "")
    # 推送内容
    sendContent = ""
    sendTitle = "GLaDOS 签到完成"
    
    # glados账号cookie 直接使用数组 如果使用环境变量需要字符串分割一下
    cookies = os.environ.get("GLADOS_COOKIE", []).split("&")
    if cookies[0] == "":
        print("未获取到COOKIE变量") 
        cookies = []
        exit(0)
    
    domain = "glados.rocks"
    origin = f"https://{domain}"
    checkinUrl = origin + "/api/user/checkin"
    statusUrl = origin + "/api/user/status"
    pointsUrl = origin + "/api/user/points"
    exchangeUrl = origin + "/api/user/exchange"
    
    useragent = "Mozilla/5.0 (Linux; Android 16; 23127PN0CC Build/BP2A.250605.031.A3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 Mobile Safari/537.36"
    
    for cookie in cookies:
        state = requests.get(statusUrl,headers={"cookie": cookie ,"origin": origin, "user-agent": useragent})
        print(f"[state] {state.json()}")
        if state.json()["code"] == -2:
            sendTitle = "GLaDOS Cookie 已失效"
            sendContent += "cookie已失效\n\n"
            continue
        time = state.json()["data"]["leftDays"]
        time_str = str(time)
        time = int(time_str.split(".")[0])
        email = state.json()["data"]["email"]
        
        checkin = requests.post(checkinUrl,headers={"cookie": cookie ,"origin": origin, "user-agent": useragent, "content-type": "application/json;charset=UTF-8"}, data=json.dumps({"token": domain}))       
        if "message" in checkin.text:
            mess = checkin.json()["message"]
            print(email + "----结果--" + mess)
            
            points = requests.get(pointsUrl,headers={"cookie": cookie ,"origin": origin, "user-agent": useragent})
            point = int(points.json()["points"].split(".")[0])
            
            exchangeMessage = ""
            if point >= 500:
                print(f"积分已达{point}，开始兑换天数")
                exchange = requests.post(exchangeUrl,headers={"cookie": cookie ,"origin": origin, "user-agent": useragent, "content-type": "application/json;charset=UTF-8"}, data=json.dumps({"planType": "plan500"}))
                if exchange.json()["code"] == 0:
                    print("成功兑换 100 天")
                    point -= 500
                    time += 100
                    exchangeMessage = "----✅ 自动兑换成功"
                else:
                    print(f"自动兑换失败，{exchange.json()}")
                    exchangeMessage = "----❌ 自动兑换失败"
                     
            sendContent += email + "---" + mess + exchangeMessage + f"----积分({point})----剩余({time})天\n\n"
        else:
            requests.get("http://www.pushplus.plus/send?token=" + sckey + "&title=【签到失败】&content="+email+"cookie已失效")
            print("cookie已失效")
    
    #--------------------------------------------------------------------------------------------------------#   
    if sckey != "":
         requests.get("http://www.pushplus.plus/send?token=" + sckey + "&title="+sendTitle+"&content="+sendContent)
