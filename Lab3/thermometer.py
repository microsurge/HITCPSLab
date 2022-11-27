import paho.mqtt.client as mqtt
import time
import hashlib
import hmac
import random
from threading import Thread

#CPS验证与评价实验三
#物联网平台实验 代码在实验指导书的基础上进行修改
#平台产品有三个属性 temperature humidity power 本文件于50行处随机生成他们的值
#该产品有三个设备 分别为device1 device2 device3
#运行本代码需要创建具有上述三个属性的产品，并且创建三个设备，将options中的前三项分别替换即可
options = {
    'productKey' : "hz9kaAdT7uR",
    'deviceName' : ["device1", "device2", "device3"],
    'deviceSecret' : ["d631c98292ddffd8d2e0204f27b34efa", "024dd1e01e41a33a47a63c04cb1b63a7", "96e2d577dd635a417f5cfc0ff97c06ac"],
    'regionId' : 'cn-shanghai'
}


HOST = options['productKey'] + '.iot-as-mqtt.' + options['regionId'] + '.aliyuncs.com'
PORT = 1883
KEEP_ALIVE = 300
def generatePubTopic(deviceIndex) :
    return "/sys/" + options['productKey'] + "/" + options['deviceName'][deviceIndex - 1] + "/thing/event/property/post"

def on_connect (client, userdata, flags, rc) :
    print("Connected with result code : " , str(rc))

def on_message (client, userdata, msg) :
    print(msg.topic + " " + str(msg.payload))

def hmacsha1(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha1).hexdigest()

def getAliyunIoTClient(deviceIndex):
    timestamp = str(int(time.time()))
    CLIENT_ID = "paho.py|securemode=3,signmethod=hmacsha1,timestamp=" + timestamp + "|"
    CONTENT_STR_FORMAT = "clientIdpaho.pydeviceName" + options['deviceName'][deviceIndex-1] + "productKey" + options['productKey'] + "timestamp" + timestamp
    #set username/password.
    USER_NAME = options['deviceName'][deviceIndex-1] + "&" + options['productKey']
    PWD = hmacsha1(options['deviceSecret'][deviceIndex - 1], CONTENT_STR_FORMAT)
    client = mqtt.Client (client_id = CLIENT_ID, clean_session = False)
    client.username_pw_set (USER_NAME,PWD)
    return client

def generatePayLoad() :
    #随机生成三个属性的数据
    ret = {
        'id': int(time.time()),
        'params':{
            'temperature': random.randint(-30, 50),
            'power': round(random.uniform(0, 30) , 2),
            'humidity': round(random.uniform(0, 100) , 2)
        },
        'method' : "thing.event.property.post"
    }
    return ret

def runClient(clientIndex) :
    client = getAliyunIoTClient(clientIndex)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HOST, PORT, KEEP_ALIVE)
    payload = generatePayLoad()
    print('send data to iot device' + str(clientIndex) + " : "  + str(payload))
    client.publish (generatePubTopic(clientIndex), payload = str(payload), qos=1)
    client.loop_forever()

if __name__ == '__main__' :
    #主函数里面开了三个线程 分别跑三个设备的数据上传
    try:
        thread1 = Thread(target = runClient, args = (1, ))
        thread2 = Thread(target = runClient, args = (2, ))
        thread3 = Thread(target = runClient, args = (3, ))
        thread1.start()
        thread2.start()
        thread3.start()
    except:
        print("Some errors occur!!")
    
