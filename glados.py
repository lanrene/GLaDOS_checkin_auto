import requests,json,os
# -------------------------------------------------------------------------------------------
# github workflows
# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # pushplus秘钥 申请地址 http://www.pushplus.plus
    sckey = os.environ.get("PUSHPLUS_TOKEN", "")
    # 推送内容
    sendContent = ""
    sendTitle = "✅ GLaDOS 签到成功"
    
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
    
    for cookie in cookies:
        headers = {
            "cookie": cookie,
            "origin": origin,
            "user-agent": "Mozilla/5.0 (Linux; Android 16; 23127PN0CC Build/BP2A.250605.031.A3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 Mobile Safari/537.36"
        }    
    
        state = requests.get(statusUrl, headers=headers)
        state_json = state.json()
        if state_json.get("code") != 0:
            print(f"[state] {state_json}")
            sendTitle = "❌ GLaDOS 签到失败"
            sendContent += f"{state_json.get('message', '未知错误')}\n\n"
            continue
        state_data = state_json.get("data", {})
        left_days = int(float(state_data.get("leftDays", "0")))
        email = state_data.get("email", "")
        
        checkin = requests.post(checkinUrl, headers=headers, data=json.dumps({"token": domain}))
        checkin_json = checkin.json()
        if "message" in checkin.text:
            mess = checkin_json.get("message")
            print(f"{email}----结果----{mess}")
            
            points = requests.get(pointsUrl, headers=headers)
            point = int(float(points.json().get("points", "0")))
            
            exchangeMessage = ""
            if point >= 500:
                print(f"积分已达{point}，开始兑换天数")
                exchange = requests.post(exchangeUrl, headers=headers, data=json.dumps({"planType": "plan500"}))
                exchange_json = exchange.json()
                if exchange_json.get("code") == 0:
                    print("成功兑换 100 天")
                    point -= 500
                    left_days += 100
                    exchangeMessage = "----✅ 自动兑换成功"
                else:
                    print(f"自动兑换失败，{exchange_json}")
                    exchangeMessage = "----❌ 自动兑换失败"
                     
            sendContent += f"{email}---{mess}{exchangeMessage}----积分({point})----剩余({left_days})天\n\n"
        else:
            sendTitle = "❌ GLaDOS 签到失败"
            sendContent += "cookie已失效\n\n"
            print(f"[checkin] {checkin_json}")
    
    #--------------------------------------------------------------------------------------------------------#   
    if sckey != "":
         requests.get("http://www.pushplus.plus/send", params={"token": sckey, "title": sendTitle, "content": sendContent})
