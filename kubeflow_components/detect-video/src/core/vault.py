import json
from confluent_kafka import Consumer
import requests
import time

def CreateQueue(bootstrap_servers='', topic='', mechanism='', security='', username= '', password=''):
    return Kafka(bootstrap_servers=bootstrap_servers, topic=topic, mechanism=mechanism, security=security, username=username, password=password)

class Kafka:
    def __init__(self, bootstrap_servers='', topic='', mechanism='', security='', username= '', password=''):
        self.topic = topic
        kafkaC_settings = {
            'bootstrap.servers': bootstrap_servers,
            "group.id":             "mygroup",
            "session.timeout.ms":   10000,
            "queued.max.messages.kbytes": 10000, #10MB
        	"auto.offset.reset":    "earliest",
            "sasl.mechanisms":   mechanism,#"PLAIN",
            "security.protocol": security, #"SASL_PLAINTEXT",
            "sasl.username":     username,
            "sasl.password":     password,
        }
        self.kafka_consumer = Consumer(kafkaC_settings)
        self.kafka_consumer.subscribe([self.topic])

    def ReceiveMessages(self):
        msg = self.kafka_consumer.poll(timeout=1.0)
        if msg is None:
            return []
        return [json.loads(msg.value())]

    def Close(self):
        self.kafka_consumer.close()
        return True



def download_video(api_address, access_key, secret_access_key, message, video_folder='/input_videos'):
    '''
    Downloads video given a adress obtained from Kafka broker
    '''

    fileName = message['payload']['key']
    provider = message['source']

    
    response = requests.get(
        api_address,
        headers={
            'X-Kerberos-Storage-FileName': fileName,
            'X-Kerberos-Storage-Provider': provider,
            'X-Kerberos-Storage-AccessKey': access_key,
            'X-Kerberos-Storage-SecretAccessKey': secret_access_key,
    },
    )
    
    if response.status_code != 200:
        print(response.content)
        print("Something went wrong: " + response.content)

    fileContent = response.content
    with open(video_folder + '/video.mp4', 'wb') as file:
        file.write(fileContent)