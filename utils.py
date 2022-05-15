import requests
import random
from datetime import datetime
import re
import os
import json
import time
import pandas as pd
from split_text import SplitSentence
import requests

def query_sim(text1,text2):
    headers = {
        'User-Agent': 'Apipost client Runtime/+https://www.apipost.cn/',
        'Content-Type': 'application/json',
    }
    data = json.dumps({"text":[text1,text2],"require_numbers":True})

    response = requests.post('http://39.99.249.45:8087/z', headers=headers, data=data)
    # print(response.json())
    return eval(response.json()["result"])


def check_sim_service(ans,all_history):
    all_history= all_history if len(all_history)<10 else all_history[-9:]
    for text2 in all_history:
        if query_sim(ans,text2)>0.9:
            return True
    return False
def query_theme(text):
    headers = {
        'User-Agent': 'Apipost client Runtime/+https://www.apipost.cn/',
        'Authorization': 'Bearer sk-IxKsLwAVCwgCh8m0tSvE4niDYDtbTOypHy6uPoPQBGcdiv9C',
        'Content-Type': 'application/json',
    }

    data = json.dumps({ "text":text, "labels":all_topics, "lang":"all" })

    response = requests.post('http://39.99.249.45:8066/v1/models/kfserving-custom-model:predict', headers=headers, data=data)
    return response.json()["result"]["labels"][0]


split_sentence = SplitSentence()
puncs_fine = ['……', '\r\n', '，', '。', ';', '；', '…', '！',
                           '!', '?', '？', '\r', '\n', '“', '”', '‘', '’',
                           '：',":",".","\"","$","&"]
count=0
now=datetime.now().strftime("%Y-%m-%d")
data_corpus=pd.read_csv("topic_transfer_label.csv")
topic_corpus={}

# for index,corpus in enumerate(data_corpus["txt"]):
#     tags=data_corpus["tag"][index]
#     if tags not  in topic_corpus:
#         topic_corpus[tags]=[]
#     else:
#         topic_corpus[tags].append(corpus.replace("\xa0"," "))
# all_topics=list(topic_corpus.keys())
# print(topic_corpus)
# print(all_topics)
def query_deal_gpt_3(json_data):
    global now
    global count
    # print(json_data)
    if datetime.now().strftime("%Y-%m-%d")!=now:
        now=datetime.now().strftime("%Y-%m-%d")
        count=0
    record_data=json.load(open("record.json","r"))
    record_data.update({now:count})
    with open("record.json","w") as f:
        json.dump(record_data,f)
    inpu=json_data.get("prompt","hello")
    stop_words=json_data.get("user","user")+":"
    frequency_penalty=json_data.get("frequency_penalty",3)
    max_tokens=json_data.get("max_tokens",50)
    temperature=json_data.get("temperature",0.9)
    top_p=json_data.get("top_p",0.9)
    headers = {
        'User-Agent': 'Apipost client Runtime/+https://www.apipost.cn/',
        'Content-Type': 'application/json',
    }
    data = json.dumps({"prompt": inpu, "max_tokens": max_tokens,"temperature": temperature, "top_p":top_p, "frequency_penalty": frequency_penalty,"presence_penalty":1,"stop":stop_words})
    # print(data)
    if count>20000:
        response = requests.post('http://39.103.143.138:8080/z', headers=headers,data=data)
        # print(response.json())
        response=response.json()["result"]["sentence"]
    else:
        count+=1
        response = requests.post('http://52.53.227.127:8000/v1/engines/text-davinci-001/completions', headers=headers,
                             data=data)
        # print(response.json())
        response=response.json()["choices"][0]["text"]
    response=response.split("\n")
    res=[i for i in response if i]
    # print(res)
    if res:
        return res[0]
    else:
        return ""

def get_real_ans(raw_data):
    ans=query_deal_gpt_3(raw_data)
    res = split_sentence(ans, criterion='fine')
    if res[-1][-1] not in puncs_fine:
        strategy=raw_data.get('strategy',"append")
        if strategy=="append":
            raw_data["max_tokens"]=15
            raw_data["prompt"]+= ans
            ans_ = query_deal_gpt_3(raw_data)
            ans+= split_sentence(ans_, criterion='fine')[0]
        elif strategy=="delete":
            ans="".join(res[:-1])
        else:
            ans=ans
    if ans and ans[-1]==",":
        ans=ans[:-1]+"."
    ans=ans.split("Trump:")[0].split("Biden:")[0].split("Obama:")[0]
    return ans


with open('roles.txt', 'r') as f:
    roles = json.load(f)
    for key,val in roles.items():
        print(key)
        print(val)


def print_history(chat_history,append_time=False):
    with open("out_chat.txt","w") as f:
        f.write("*"*20+"\n")
        for content in chat_history:
            if append_time:
                f.write(content[2]+"      ")
            f.write(content[0] + ":   " + content[1]+"\n")
    print("\n"+"*"*20)
    for content in chat_history:
        if append_time:
            print(content[2]+"    "+content[0]+":   "+content[1])
        else:
            print(content[0]+":   "+content[1])
if __name__=="__main__":
    # act_by_order(True,True)
    act_by_cd_user(True,False)