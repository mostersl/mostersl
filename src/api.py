import base64
import hashlib
import json
import time
from datetime import datetime
from uuid import uuid4

import requests

from src import rsa_pk1


def ZT_Token(passwd, uid):
    url = 'https://sso.zto.com/oauth2/authorize?appid=ztDNprSNTtWdaQeoAcHgtKNQ&response_type=token&scope=userinfo%2Cusercert%2Cusercontact%2Cuser_id%2Cnode_id'
    h = {
        'Authorization': f'Secret {rsa_pk1.rsa_encrypt(passwd).decode()}',
        'X-Webrtc-Addrs': '192.168.0.1',
        'X-Sms-Otp': '',
        'Content-Type': 'application/json',
        'X-App-Bundle-Id': 'com.geenk.zto.sys',
        'X-App-Bundle-Name': '%E6%8E%8C%E4%B8%AD%E9%80%9A',
        'X-Extra-Mac': '02:00:00:00:00:00',
        'X-Is-Emulator': '0',
        'X-Device-Id': uid,
        'X-Platform-Name': 'Android',
        'X-Platform-Version': '12',
        'X-App-Version': '6.1.1',
        'Host': 'sso.zto.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.9.0',
    }
    result = requests.get(url=url, headers=h)
    return json.loads(result.text)


def ZT_UserInfo(token, openid, device):
    tim = str(int(time.time() * 1000))
    url = 'https://zztgateway2.zto.com/appInterface'
    h = {
        'X-Token': token,
        'X-OpenId': openid,
        'X-Timestamp': tim,
        'X-Device-Id': device,
        'X-Device-Name': 'Redmi+K30+5G',
        'X-Platform-Name': 'Android',
        'X-Device-Version': '12',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'zztgateway2.zto.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.9.0',
    }
    data = f'msg_type=INFO_USER&data=%7B%22accesstoken%22%3A%22{token}%22%2C%22openid%22%3A%22{openid}%22%7D&open_id={openid}&company_id=APP_ANDROID&data_digest=Useless&version=6.29.1&timestamp={tim}'
    result = requests.post(url=url, headers=h, data=data)
    return json.loads(result.text)


def ZT_TASK_LIST_V4(token, openid, device, b_date, e_date):
    tim = str(int(time.time() * 1000))
    url = 'https://zztgateway2.zto.com/DELIVERY_TASK_LIST_V4'
    h = {
        'X-Timestamp': tim,
        'X-Device-Id': device,
        'X-Device-Name': 'Redmi+K30+5G',
        'X-Platform-Name': 'Android',
        'X-Device-Version': '12',
        'X-Token': token,
        'X-OpenId': openid,
        'Content-Type': 'application/json; charset=utf-8',
        'Host': 'zztgateway2.zto.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.9.0',
    }
    data = {"carrierRequest": {
        "data": {"beginDate": b_date, "flag": "0", "endDate": e_date, "beginRow": 1,
                 "endRow": 400, "status": "0"}, "companyId": "APP_ANDROID", "timestamp": tim,
        "openId": openid, "open_id": openid, "version": "6.29.1",
        "data_digest": "Useless", "dataDigest": "Useless"}, "company_id": "APP_ANDROID", "data_digest": "Useless",
        "version": "6.29.1", "open_id": openid, "timestamp": tim}
    result = requests.post(url=url, headers=h, json=data)
    return json.loads(result.text)


def JT_Login(account, password, devices):
    tim = str(int(time.time() * 1000))
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    str_md5 = md5.hexdigest()
    url = 'https://bc.jtexpress.com.cn/bc/out/loginSecurity'
    h = {
        'Host': 'bc.jtexpress.com.cn',
        'device-name': 'Redmi Redmi K30 5G',
        'authtoken': '',
        'device-id': 'WA-0be9e30b20f7332',
        'userid': '0',
        'app-channel': 'Internal Deliver',
        'device-version': 'Android-31',
        'appid': '202100001',
        'devicefrom': 'android',
        'app-platform': 'Android_com.yunlu.salesman',
        'device': 'WA-0be9e30b20f7332',
        'user-agent': 'Android-Redmi Redmi K30 5G/app_out',
        'timestamp': tim,
        'content-type': 'application/json; charset=utf-8',
        'accept-encoding': 'gzip',
    }
    data = {"password": str_md5, "appDeviceId": "WCA-0be9e30b20f7332", "code": "",
            "account": account, "macAddr": devices}
    result = requests.post(url=url, headers=h, json=data)
    return json.loads(result.text)


def JT_Task_all(account, token, b_date, e_date):
    tim = str(int(time.time() * 1000))
    u = 'https://bc.jtexpress.com.cn/bc/task/awaitDelivery/all'
    h = {
        'Host': 'bc.jtexpress.com.cn',
        'device-name': 'Redmi Redmi K30 5G',
        'staffno': account,
        'authtoken': token,
        'device-id': 'WA-0be9e30b20f7332',
        'app-channel': 'Internal Deliver',
        'device-version': 'Android-31',
        'appid': '202100001',
        'devicefrom': 'android',
        'app-platform': 'Android_com.yunlu.salesman',
        'device': 'WA-0be9e30b20f7332',
        'user-agent': 'Android-Redmi Redmi K30 5G/app_out',
        'timestamp': tim,
        'content-type': 'application/json; charset=UTF-8',
        'accept-encoding': 'gzip',
    }
    d = {"address": "", "customerName": "", "endTime": e_date, "groupFlag": "10", "orderFlag": "10", "orderId": "",
         "orderType": 0, "pageNum": 1, "phone": "", "staffLngLat": "", "startTime": b_date, "taskStatus": "3",
         "waybillId": ""}
    result = requests.post(url=u, headers=h, json=d)
    return json.loads(result.text)


def Md5ToBase64(text):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return base64.b64encode(md5.digest()).decode('utf-8')


def YT_SMS(account, phone, token):
    tim = str(int(time.time() * 1000))
    d1 = f'orgCodetime{tim}c0^@*jsd&82026da003873*r63^*67(w%8(57'
    url = 'http://pdanew.yto56.com.cn:9193/opXZApp/jsc/smsVerify'
    data = {"empCode": account, "phone": phone, "preToken": token,
            "type": "loginVerify"}
    h = {
        'time': tim,
        'requestID': Md5ToBase64(d1),
        'pdaDeviceNo': 'BU+MD3GLC5L/PUJQ',
        'pdaVersionNo': '8.1.4.5',
        'pdaVersionCode': '20230465',
        'pdaDeviceType': 'XZ-AND',
        'deviceModel': 'Redmi K30 5G',
        'token': '',
        'orgCode': '',
        'loginUserCode': '',
        'signKey': 'XZ20210106',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'pdanew.yto56.com.cn:9193',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.11.0',
    }
    result = requests.post(url=url, headers=h, json=data)
    return json.loads(result.text)


def YT_Login(account, passwd):
    tim = str(int(time.time() * 1000))
    date = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    d1 = f'orgCodetime{tim}c0^@*jsd&82026da003873*r63^*67(w%8(57'
    url = 'http://pdanew.yto56.com.cn:9091/pdaUpload/courier/newLogin'
    data = {"loginLat": 0, "loginLng": 0, "loginTime": date,
            "userCode": account, "userPassword": Md5ToBase64(passwd).replace('=', '\u003d')}
    d2 = f'jiuzhouToken=&loginTime={date}&pdaDeviceNo=BU+MD3GLC5L/PUJQ&preToken=&smsValCode=&userCode={account}&userPassword={Md5ToBase64(passwd)}a8a33bdaef839830082bf385c1f41aa8'
    h = {
        'time': tim,
        'requestID': Md5ToBase64(d1),
        'pdaDeviceNo': 'BU+MD3GLC5L/PUJQ',
        'pdaVersionNo': '8.1.4.5',
        'pdaVersionCode': '20230465',
        'pdaDeviceType': 'XZ-AND',
        'deviceModel': 'Redmi K30 5G',
        'token': '',
        'orgCode': '',
        'loginUserCode': '',
        'courierSignature': Md5ToBase64(d2),
        'signKey': 'XZ20210106',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'pdanew.yto56.com.cn:9091',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.11.0',
    }
    result = requests.post(url=url, headers=h, json=data)
    return json.loads(result.text)


def YT_Login2(account, passwd, token, smsCode):
    tim = str(int(time.time() * 1000))
    date = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    d1 = f'orgCodetime{tim}c0^@*jsd&82026da003873*r63^*67(w%8(57'
    url = 'http://pdanew.yto56.com.cn:9091/pdaUpload/courier/newLogin'
    data = {"loginLat": 0.0, "loginLng": 0.0, "loginTime": date,
            "preToken": token, "smsValCode": smsCode, "userCode": account,
            "userPassword": Md5ToBase64(passwd).replace('=', '\u003d')}
    d2 = f'jiuzhouToken=&loginTime={date}&pdaDeviceNo=BU+MD3GLC5L/PUJQ&preToken={token}&smsValCode={smsCode}&userCode={account}&userPassword={Md5ToBase64(passwd)}a8a33bdaef839830082bf385c1f41aa8'
    h = {
        'time': tim,
        'requestID': Md5ToBase64(d1),
        'pdaDeviceNo': 'BU+MD3GLC5L/PUJQ',
        'pdaVersionNo': '8.1.4.5',
        'pdaVersionCode': '20230465',
        'pdaDeviceType': 'XZ-AND',
        'deviceModel': 'Redmi K30 5G',
        'token': '',
        'orgCode': '',
        'loginUserCode': '',
        'courierSignature': Md5ToBase64(d2),
        'signKey': 'XZ20210106',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'pdanew.yto56.com.cn:9091',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.11.0',
    }
    result = requests.post(url=url, headers=h, json=data)
    return json.loads(result.text)


def YT_queryList(token):
    url = 'https://courier-web.yto56.com.cn/opXZApp/h5/h5AggregationRecieversDeliveryList'
    data = {"pageNo": 1, "pageSize": 100, "searchKeywords": "", "incrementType": "", "receiverPreference": "",
            "otherType": "", "timeSort": "2", "distanceSort": "", "lng": "121.02411734699331",
            "lat": "28.180975328929865"}
    h = {
        'Host': 'courier-web.yto56.com.cn',
        'Connection': 'keep-alive',
        'pdaVersionNo': '12',
        'deviceType': 'Redmi K30 5G',
        'pdaDeviceNo': 'BU+MD3GLC5L/PUJQ',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Redmi K30 5G Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.104 Mobile Safari/537.36',
        'token': token,
        'pdaDeviceType': 'XZ-AND',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': '*/*',
        'Origin': 'https://courier-web.yto56.com.cn',
        'X-Requested-With': 'com.yto.receivesend',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://courier-web.yto56.com.cn/waitDispatch',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    result = requests.post(url=url, headers=h, json=data)
    return json.loads(result.text)


def ST_sendAuthCode(phone):
    tim = str(int(time.time() * 1000))
    url = 'https://appsys.sto.cn/app-service/user/sendAuthCode'
    random_uuid = str(uuid4())
    data = {"mobile": phone}
    nm = f'925989e5cc3245dc9afeff9d2ac00ee2{tim}{random_uuid}{json.dumps(data)}'
    md5 = hashlib.md5()
    md5.update(nm.encode('utf-8'))
    sign = str(md5.hexdigest())
    h = {
        'Host': 'appsys.sto.cn',
        'appversion': 'V1.3.1',
        'clienttype': 'android',
        'signature': sign,
        'fromapp': 'BGX',
        'jwt': '',
        'appid': 'app_android',
        'opterminal': 'ASXZ20000000000',
        'source': 'new_sxz',
        'nonce': random_uuid,
        'mac': '02:00:00:00:00:00',
        'timestamp': tim,
        'content-type': 'application/json; charset=UTF-8',
        'accept-encoding': 'gzip',
        'user-agent': 'okhttp/3.11.0',
    }
    result = requests.post(url=url, headers=h, json=data)
    return json.loads(result.text)


def ST_Login(phone, code):
    tim = str(int(time.time() * 1000))
    url = 'https://appsys.sto.cn/app-service/user/login'
    random_uuid = str(uuid4())
    data = {"mobile": phone, "captcha": code}
    nm = f'925989e5cc3245dc9afeff9d2ac00ee2{tim}{random_uuid}{json.dumps(data)}'
    md5 = hashlib.md5()
    md5.update(nm.encode('utf-8'))
    sign = str(md5.hexdigest())
    h = {
        'Host': 'appsys.sto.cn',
        'appversion': 'V1.3.1',
        'clienttype': 'android',
        'signature': sign,
        'fromapp': 'BGX',
        'jwt': '',
        'appid': 'app_android',
        'opterminal': 'ASXZ20000000000',
        'source': 'new_sxz',
        'nonce': random_uuid,
        'mac': '02:00:00:00:00:00',
        'timestamp': tim,
        'content-type': 'application/json; charset=UTF-8',
        'accept-encoding': 'gzip',
        'user-agent': 'okhttp/3.11.0',
    }
    result = requests.post(url=url, headers=h, json=data)
    return json.loads(result.text)


def ST_getUser(token):
    tim = str(int(time.time() * 1000))
    url = 'https://appsys.sto.cn/app-service/user/getUserAccountInfo'
    random_uuid = str(uuid4())
    data = {}
    nm = f'925989e5cc3245dc9afeff9d2ac00ee2{tim}{random_uuid}{json.dumps(data)}'
    md5 = hashlib.md5()
    md5.update(nm.encode('utf-8'))
    sign = str(md5.hexdigest())
    h = {
        'Host': 'appsys.sto.cn',
        'appversion': 'V1.3.1',
        'tokenid': token,
        'clienttype': 'android',
        'signature': sign,
        'fromapp': 'BGX',
        'jwt': '',
        'appid': 'app_android',
        'opterminal': 'ASXZ20000000000',
        'source': 'new_sxz',
        'nonce': random_uuid,
        'mac': '02:00:00:00:00:00',
        'timestamp': tim,
        'content-type': 'application/json; charset=UTF-8',
        'accept-encoding': 'gzip',
        'user-agent': 'okhttp/3.11.0',
    }
    result = requests.post(url=url, headers=h, json=data)
    return json.loads(result.text)


def ST_queryList(token):
    tim = str(int(time.time() * 1000))
    url = 'https://appsys.sto.cn/app-service/delivery/queryDeliveryGroupList'
    random_uuid = str(uuid4())
    data = {"sortType": "2", "isGroup": True, "statusDetail": "46", "issueTypeCode": "", "stationSource": "",
            "filterCode": None, "groupingByType": "CUSTOMER", "pageNum": 1, "issueCategoryCode": "",
            "belongDate": "2023-06-11", "pageSize": 200, "keyword": "", "partnerName": ""}
    nm = f'925989e5cc3245dc9afeff9d2ac00ee2{tim}{random_uuid}{json.dumps(data)}'
    md5 = hashlib.md5()
    md5.update(nm.encode('utf-8'))
    sign = str(md5.hexdigest())
    h = {
        'Host': 'appsys.sto.cn',
        'tokenid': token,
        'appversion': 'V1.3.1',
        'clienttype': 'android',
        'signature': sign,
        'fromapp': 'BGX',
        'jwt': '',
        'appid': 'app_android',
        'opterminal': 'ASXZ20000000000',
        'source': 'new_sxz',
        'nonce': random_uuid,
        'mac': '02:00:00:00:00:00',
        'timestamp': tim,
        'content-type': 'application/json; charset=UTF-8',
        'accept-encoding': 'gzip',
        'user-agent': 'okhttp/3.11.0',
    }
    result = requests.post(url=url, headers=h, json=data)
    return json.loads(result.text)