# -*- coding: utf-8 -*-
import requests
import json
import datetime
import os
import sys
import yaml
import uvicorn

class Config(object):
    def __init__(self,file):
        try:
            f = open(file,'r',encoding='utf-8')
            self.config= yaml.load(f,yaml.FullLoader)
            # print(self.config)
            f.close()
        except Exception as e:
            print("Config not found",e)
            sys.exit(0)
    def get(self,key):
        try:
            return self.config[key]
        except:
            return None
        

class AF(object):
    def __init__(self,host,api_user, passwd):
        self.host=host
        self.token=None
        body = {"name": api_user, "password": passwd}
        rel=self.forward(act="login",data=json.dumps(body))
        self.token =rel['data']['loginResult']["token"]
        # print(self.token)

    def logout(self):
        rel=self.forward(act="logout")
        print(rel)
   
    #接口转发
    def forward(self,act="logout",data=[],method="POST"):
        url = 'https://{}/api/v1/namespaces/@namespace/{}'.format(self.host,act)
        print("URL:",url,"METHOD:",method,"DATA:",data)
        headers = {'content-type': "application/json; charset=UTF-8",'Cookie': 'token={}'.format(self.token)}
        if method=="GET" or method=="DELETE":
            response = requests.request(method=method, url=url,  headers=headers,params=json.loads(data), verify=False)
        else:
            response = requests.request(method=method, url=url,  headers=headers,data=data, verify=False)

        rel=json.loads(response.content.decode())
        # print(rel)
        return rel





from fastapi import FastAPI, Path, Query, Body,Form,Header
app = FastAPI()
cfg=Config("config.yaml")
host=cfg.get("AF")["host"]
port=cfg.get("AF")["port"]
username=cfg.get("AF")["username"]
password=cfg.get("AF")["password"]
# 验证TOKEN
api_token=cfg.get("API")["token"]
listen_port=cfg.get("API")["port"]

print('Host:{} Port:{} User:{} Pass:{}'.format(host,port,username,password))
host=host+":"+str(port)
@app.post("/api/{action}")
async def do_api(
    action: str = Path(..., title="请查询API文档提供相应接口名称"),
    data = Body(None, title="参数"),
    token=Header(None),
    method=Header(None)
    ):
    if token != str(api_token):
        return {"code":10000,"msg":"error token","token":token}
    if method ==None:
        method="POST"
    else:
        method="GET"
    # return {"action": action, "data": data,"token":token}
    a=AF(host,username,password)
    try:
        data=json.dumps(data)
        return a.forward(action,data=data,method=method)
    except:
        return {"action": action, "data": data}
    

if __name__ == "__main__" :
    uvicorn.run( "app:app" ,reload=True ,port= listen_port)