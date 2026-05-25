Q:Engineering (PE) 到底是"工程"还是"玄学"？为什么差不多一段话，换一种写法，模型的回答质量能差很多？

A: PE是工程，但是带一点“经验调参成分”的工程。

它不像玄学的地方在于：有稳定可复现的结构(  system / user / context)， 有明确的优化目标(准确性、格式、风格、可控性), 有可测量方法(A/B test、 成功率、 token成本)；

它看起来像玄学是因为模型不是规则系统而是概率系统。

Prompt =  在高维概率空间里“引导模型走哪条路径”，Prompt改变注意力方向，输出空间约束，角色分布。



Q:   除了换写法，还有哪些技巧能让模型更听话？



Q: few-shot 示例、chain-of-thought、角色设定、结构化输出分别解决什么问题？你能自己整理出一套可复用的 PE 原则吗？试着让 AI 陪你把它写成一份 checklist。



Q:Web 界面有哪些框架可以用？最轻的是一个 HTML 文件加 fetch，中间有 Gradio、Streamlit，重的有 Next.js、 Vue、 React。这些分别适合什么场景？



Q:这些 Web 框架和 AI 开发的关系是什么？为什么做 AI 应用的人也要懂一点前端？



Q:用户在浏览器里输入一句话，这句话怎么从浏览器一路送到 OpenAI 服务器，再把回复带回来？中间经过几跳？



MVP: 最小可运行的Web Chat APP

浏览器网页

&nbsp;   ↓

前端 UI (HTML/CSS/JS)

&nbsp;   ↓ HTTP

FastAPI 后端

&nbsp;   ↓

ChatEngine

&nbsp;   ↓

OpenAI API

V1、Web基础+最小 FastAPI

环境配置： 安装Web后端框架，最轻量的FastAPI: pip install fastapi uvicorn（FastAPI定义Web API ，例如@app.get("/")

(Uvicorn负责启动HTTP Server)



1.创建最小Web项目：

web\_chatbot/

│

├── main.py

└── requirements.txt

尝试一个简单的访问页面，返回hello world

2.引入BaseModel(自动解析JSON语言)：

打开自动文档http://127.0.0.1:9000/docs，FastAPI自动生成了API文档网页，有GET/POST功能

实现了：浏览器

&nbsp;		↓ HTTP POST

&nbsp;	   FastAPI

&nbsp;		↓

&nbsp;	Python函数

&nbsp;		↓

&nbsp;	JSON Response

3.HTML + JavaScript：实现前端调用后端

·导入新的库fastapi.response的FileResponse.

原本return{"message":"hello"}只是返回JSON，现在return 

FileResponse("static/index.html")浏览器收到HTML后会渲染网页（网页=HTML文件）

·在web\_chatbot下创建static/index html：

HTML网页结构 包括<input> <button> <div>   输入框/按键/一个区域…

<input id="messageInput" type="text">

<button onclick="sendMessage()">

核心：异步函数async function send Message()：有input拿到输入框对象，input.value获取用户输入文字

(※)fetch，向FastAPI发送HTTP请求

实现请后端通信，一个完整的Web App小闭环：

网页UI

↓

JavaScript

↓

HTTP POST

↓

FastAPI

↓

Python函数

↓

JSON

↓

更新网页

4.将chatbot接入Web：理解工程分层的重要性

可以将之前完成的app直接复制到web\_chatbot下(逻辑层)

修改main.py接入chatengine，可以在网页进行与AI的交流对话。



V2：实现Streaming Web Chat

1.修改FastAPI:在main.py中导入StreamingResponse,然后在app.post中修改返回方式，变为流式输出

2.修改前端JavaScript: fetch().json()不行了，替换sendMessages():

await response.json() -> response.body.getReader()

从等待整个相应结束变成可读取的数据流+创建流读取器

创建了读取器reader：await reader.read() 读取下一个chunk

！！！出现messages污染，既要Streaming，又要结构正确：

Session+ StreamingResponse

！！！每次AI回复共用一个id： 修改前端，每次创建独立DOM

！！！DOM 被 innerHTML 重建 + Stream 写入目标丢失：

Streaming UI构建能力，避免React没有引入时DOM非响应式重建问题。\*不用innerHTML 拼DOM:document.createElement()

appendChild()     保证DOM不再重建，节点稳定

\*AI输出节点的固定引用const aiSpan = document.createElement("span") 保证stream写入目标稳定而且不会绑定丢失

\*使用textContent 追加stream



V3：Chatgpt式升级

问题一:Web 版本每次请求都重新创建ChatEngine(),导致无法保持上下文对话，用户的多轮对话被当作请求独立处理+历史记录管理混乱：CLI版本会保存历史到文件/Web版本每次都加载历史但是不保存->两个版本都共享同一个历史文件会导致冲突

1.会话管理(Session ID + 简单的内存存储)：

main.py:

两个库:from pydantic import BaseModel

&nbsp;       from typing import Optional (避免None出现问题)

&nbsp;       import uuid(python中用来生成全局唯一ID)

定义聊天系统的数据结构：初始化session，前端请求格式(ChatRequestt)

&nbsp;     session定义为字典(对应关系)

&nbsp;     class ChatRequest(BaseModel): 前端发送给后的数据模板：定义了message(字符)，session\_id可以为空

&nbsp;     class SessionResponse(BaseModel):

&nbsp;                 ssession\_id: str 后端返回给前端的数据格式，后端给进入网站的用户生成一个唯一的id:session\_id = str(uuid.uuid4()) ，返回一个字典并保存他，传给前端保证有对话记忆。

@app的操作： get("/")访问该路径时候，return html返回某个网页

&nbsp;             post("/session")“给每个用户生成独立的id，根据每个id创立新的对话：session\[session\_id] = ChatEngine()

&nbsp;             post("/chat")聊天接口，聊天时候调用的接口：

&nbsp; req是FastAPI自动把JSON转换为ChatRequest形式

检查session(无session\_id重新创建session\_id)->流式输出generate->返回得到的流式输出



前端index.html:

&nbsp;       ① 首先let sessionId = null

&nbsp;       ②userMsg.innerHTML = `<b>你:</b> ${message}` 将字符串当作了HTML管理，（前端XSS漏洞）

改为textContent c纯文本，不会解析HTML 然后使用userMsg.appendChild将user\_label, user\_message插入界面

显示用户信息-> 创建AI容器 -> 请求stream->streaming写入

&nbsp;       ③stream中body主体请求内容

&nbsp;           body: JSON.stringify({

&nbsp;                      message: message,

&nbsp;                   session\_id: sessioId

&nbsp;               }) （携带id信息）



**Claude Code:后端 (main.py)**

**添加了会话存储：使用字典 sessions 存储每个用户的 ChatEngine 实例**

**添加了 session\_id 参数：ChatRequest 现在接受可选的 session\_id**

**自动创建会话：如果没有提供 session\_id 或 session 不存在，会自动创建新的**

**保持对话上下文：同一个 session\_id 会使用同一个 ChatEngine 实例**

**前端 (index.html)**

**添加了 sessionId 变量：在页面级别保持会话 ID**

**发送 session\_id：每次请求都会带上当前的 session\_id**

**修复了 XSS 漏洞：用户消息现在也使用 textContent 而不是 innerHTML**

**工作原理**

**用户第一次发送消息时，sessionId 为 null，后端会创建新的会话**

**后续的所有消息都会使用同一个 ChatEngine 实例，保持对话上下文**

**刷新页面会丢失 sessionId，相当于开始新对话**



debug:1.后端创建新会话时候，没有把session\_id 返回给前端，在generate中加yield f"SESSION\_ID:{session\_id}\\n"，后端对应的要在streaming写入中接收Session\_id

2\. 500错误:   测试导入是否成功-> 检查static目录存在index.html文件；  FileResponse路径问题： index.html是否存在； ChatEngine初始化问题； 测试FastAPI根路径，测试能否正常返回200； 检查配置问题.env, config.py 

3\. session\_id 定义了str=None， Pydantic v2不允许这种语法，改为session\_id : Optiional\[str] = None

4\.网页中发送的body不合法你: 你好，我是小明



AI: {"detail":\[{"type":"string\_type","loc":\["body","session\_id"],"msg":"Input should be a valid string","input":null}]}：



前端发送sessionID： null的时候， JSON把它序列化成了null 这与后端期望的是字符串冲突了。

修改Index.html: 

&nbsp;      const requestBody = { message: message }

&nbsp;           if (sessionId) {

&nbsp;               requestBody.session\_id = sessionId

&nbsp;           }   动态请求构建body， 如果有id再传递session\_id

&nbsp; JSON处的body：body: JSON.stringify(requestBody)



2\.历史记录管理：

问题：CLI 版本会保存历史到文件，Web 版本每次都加载历史但不保存，两个版本共享同一个历史文件会导致冲突。

(1). chat.py: 其中ChatEngine每次初始化都会读取历史文件load\_history() , CLI一个用户时候没有问题，Web版多个用户时问题很大，首先应该load\_history\_file=False, 后续可扩展性加条件语句if load\_history\_file.   在app/main中每次新建ChatEngine的时候加载(load\_history\_file = True)

CLI版本的文件的历史管理

(2).Web版本：默认不加载历史，加一个会话清理机制避免内存无限增长。(防止总是每来一个用户，记录一个)

记录当前的时间和每个用户最后活跃的时间，cleanup\_old\_sessions中判断时间差是否超过了MAX\_SESSION\_AGE, 如果超过了就清理掉。

将这个清理机制加到@app.post("/chat")聊天系统中

CLAUDE CODE总结：

改进内容

1\. 分离 CLI 和 Web 的历史记录 (chat.py:22)

ChatEngine 现在接受 load\_history\_file 参数

CLI 版本：ChatEngine(load\_history\_file=True) - 加载并保存历史到文件

Web 版本：ChatEngine() - 每个会话独立，不使用文件

2\. 添加会话自动清理机制 (main.py:14-24)

追踪每个会话的最后活跃时间

超过 1 小时不活跃的会话会被自动清理

避免内存无限增长

3\. 会话活跃时间更新 (main.py:38)

每次用户发送消息时更新会话的活跃时间

现在的工作方式

CLI 版本：



启动时加载 data/chat\_history.json

每次对话后保存历史

下次启动时继续之前的对话

Web 版本：



每个浏览器会话独立

刷新页面 = 新会话

不会污染 CLI 的历史文件

1 小时不活跃自动清理

V4 改进升级：
第一阶段：安全与稳定性
添加.gitignore, Web错误处理，移除Web中的CLI loading动画，添加输入验证
操作：①.gitignore保护环境变量和敏感信息.env , .env.loacl
②为Web添加错误处理:
后端main.py: chat/中调用DEEPSEEK API是否成功加一个try
前端index.html: 请求steam中,如果没有回复，则HTTP请求错误；streaming写入时，如果有错误信息，将错误信息标红(标注后端中返回的错误)， 最后catch显示错误。
③移除了chat.py中show_loading的加载界面：只有运行CLI时候才显示，在Web运行时不显示
④添加输入验证：
后端main.py:(字段验证器)， 自动检查是否合法
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
新导入HTTPException和field_validator这两个库
在定义信息请求格式的时候class ChatRequest加上验证























