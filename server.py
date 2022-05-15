import asyncio
import websockets
import websockets_routes
import json
import pickle
# import ssl
import time
# 初始化一个router对象
import pathlib
from datetime import datetime
import random
import _thread
from utils import query_sim,check_sim_service,roles,get_real_ans
router = websockets_routes.Router()
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# ssl_context.load_cert_chain("dev-metaversel.fun.pem")

# 所有共享的参数
audience_list=[]
vote_count= {
    "Biden": 10,
    "Trump": 5,
    "Obama": 15
  }
status="idle"
chat_history=[]
message_synced={}
roles_names = {"Biden": {"random_range": range(7, 15), "now_sep": 6, "last_state": datetime.now()},
               "Obama": {"random_range": range(5, 10), "now_sep": 3, "last_state": datetime.now()},
               "Trump": {"random_range": range(5, 10), "now_sep": 6, "last_state": datetime.now()},
               "User": {"random_range": range(30, 40), "now_sep": -1, "last_state": datetime.now()}}



def load_param():
    global audience_list
    global  vote_count
    global status
    global chat_history
    global message_synced
    global roles_names
    with open("params.pickle","rb") as f:
        data=pickle.load(f)
    audience_list=data.get("audience_list")
    vote_count=data.get("vote_count")
    status=data.get("status")
    chat_history=data.get("chat_history")
    message_synced=data.get("message_synced")
    roles_names=data.get("roles_names")
def save_param():
    global audience_list
    global  vote_count
    global status
    global chat_history
    global message_synced
    global roles_names
    data={"audience_list":audience_list,"vote_count":vote_count,"status":status,"chat_history":chat_history,"message_synced":message_synced,"roles_names":roles_names}
    with open("params.pickle","wb") as f:
        pickle.dump(data,f)
def form_message():
    data=json.dumps({
          "status": status,
          "vote_count":vote_count ,
          "audience_list": audience_list,
          "message_list":chat_history
    })
    return  data

@router.route("/{user_id}/message") #添加router的route装饰器，它会路由uri。
async def message(websocket, path):
    # async for message in websocket:
    while True:
        await asyncio.sleep(0.5)
        user_id=path.params['user_id']
        global message_synced
        if user_id not in message_synced:
            message_synced[user_id]=False
        if message_synced[user_id]:
            continue
        message_now=form_message()
        await  websocket.send(message_now)
        message_synced[user_id]=True

def deal_enter(message):
        now_user_id=message["content"]["user_id"]
        global audience_list
        global message_synced
        audience_list.append(now_user_id)
        # if now_user_id not in message_synced:
        message_synced[now_user_id]=False
        for items in message_synced.keys():
            message_synced[items]=False

def deal_vote(message):
    vote_name=message["content"]["name"]
    global vote_count
    vote_count[vote_name]+=1
    global message_synced
    for items in message_synced.keys():
        message_synced[items]=False

@router.route("/send")
async def send(websocket, path):
    async for message in websocket:
        print("got a message:{}".format(message))
        message=json.loads(message)
        if message["action"]=="audience_enter":
            deal_enter(message)
        elif message["action"]=="vote":
            deal_vote(message)
        elif message["action"]=="send_message":
            deal_send(message)
        elif message["action"]=="refresh":
            deal_refresh()
        elif message["action"]=="reset":
            deal_reset()

def deal_send(message):
        global chat_history
        global status
        global message_synced
        global roles_names
        if status=="speaking":
            return
        text=message["content"]["message"]
        user_id=message["content"]["user_id"]
        timestamp=message["content"]["timestamp"]

        chat_history.append({"from":user_id,"timestamp":timestamp,"message":text})
        status="speaking"
        roles_names["User"]["last_state"] = datetime.now()
        roles_names["User"]["now_sep"] = random.choice(roles_names["User"]["random_range"])
        for items in message_synced.keys():
            message_synced[items]=False
def deal_refresh():
    global message_synced
    for items in message_synced.keys():
        message_synced[items] = False

def deal_reset():
    global status
    status="idle"



def act_by_cd_user(if_add_default=False):
    global status
    global chat_history
    global roles_names
    chat_history = [{"from":"Obama", "message":"Hi,everyone!How are you today?","timestamp":round(time.time()*1000)}]
    
    # print()
    all_names = list(roles_names.keys())
    count=0
    while True:
        # if if_random:
        #     random.shuffle(roles_names)
        for person in roles_names:
            sorted_names = [[person,roles_names[person]["now_sep"]] for person in roles_names]
            sorted_names=sorted(sorted_names,key=lambda x:x[1],reverse=False)
            print(sorted_names)
            if sorted_names[0][1]<0:
                person=sorted_names[0][0]
            # print(status)
            # print(person)
            now=datetime.now()
            if person=="User":
                print(roles_names)
                print(status)
                print((now-roles_names[person]["last_state"]).total_seconds())
            
            if (now-roles_names[person]["last_state"]).total_seconds() < roles_names[person]["now_sep"]:
                continue
            print(person,"pass")
            if status=="idle":
                print(status)
                continue
            if person=="User":
                # other_topic=list(set(all_topics)-set(now_topic))
                # if if_transfer_by_topics and other_topic:
                #     ans=random.choice(topic_corpus.get(random.choice(other_topic)))
                # else:
                #     ans=input(f"{str(now)}    User:  ")
                status="idle"
                deal_refresh()
                continue
            else:  
                prompt=roles[person]["prompt"]
                if if_add_default:
                    prompt+=roles[person]["default_chat"]
                if len(chat_history)>2:
                    now_use_chat_history=chat_history[-3:]
                else:
                    now_use_chat_history=chat_history
                # print(now_use_chat_history)
                for content in now_use_chat_history:
                    if content["from"] not in all_names:
                        prompt+=content["from"]+":"+content["message"]+"\n"
                prompt+=person+":"
                raw_data={"prompt":prompt,"strategy":"append"}
                try:
                    ans=get_real_ans(raw_data)
                except Exception as e:
                    print(e)
                    ans=get_real_ans(raw_data)
                print("请求生成模型")
                #去掉重复的发言
                all_history=[i["message"] for i in chat_history]
                if len(ans) >4 and check_sim_service(ans,all_history):
                    continue
            if person in all_names:
                chat_history.append({"from":person,"message":ans,"timestamp":round(time.time()*1000)})
            roles_names[person]["last_state"]=datetime.now()
            print(vote_count)
            
            roles_names[person]["now_sep"]=random.choice(roles_names[person]["random_range"])*(sum(vote_count.values())+1)/(vote_count[person]+1)/2
            for toward_somebody in all_names:
                 if toward_somebody in ans:
                     roles_names[toward_somebody]["now_sep"]=-1
                     print(f"Next Speaker is {toward_somebody}")
            # print_history(chat_history,append_time=True)
            global message_synced
            for items in message_synced.keys():
                message_synced[items] = False
            # print(chat_history)
            count+=1
        time.sleep(0.5)


async def main():
    # rooter是一个装饰器，它的__call__函数有三个参数，第一个参数是self。
    # 所以这里我们需要使用lambda进行一个转换操作，因为serv的wshander函数只能接收2个参数
    async with websockets.serve(lambda x, y: router(x, y), "0.0.0.0", 8099):
        print("======")

        await  asyncio.Future()  # run forever

        


if __name__ == "__main__":
    load_param()
    try:
        _thread.start_new_thread(act_by_cd_user,(True,))
    except Exception as e:
        print("Error: 无法启动线程",e)
    try:
        asyncio.run(main())
    except Exception as e:
        print("Counter", e)
    finally:
        save_param()
