import os
from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import time
from openai import OpenAI
client = OpenAI()


TEXT_TEMPLATE = """
<xml>
    <ToUserName><![CDATA[{to_user}]]></ToUserName>
    <FromUserName><![CDATA[{from_user}]]></FromUserName>
    <CreateTime>{create_time}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{content}]]></Content>
</xml>
"""


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')

@app.route('/api/message', methods=['POST'])
def receive_message():
    """
    接收公众号消息推送
    """


    req = request.get_json()
    app.logger.info(req)
    res = {
        'to_user': req['FromUserName'],
        'from_user': req['ToUserName'],
        'create_time': int(time.time()),
        'content': '抱歉，系统当前不可用，请稍后再试',
    }
    if req.get('content', '') == 'openai':
        try:
            res['content'] = '这里应该填写响应数据'
            key = os.environ.get('OPENAI_API_KEY', '')[-10:]
            app.logger.info(f'openai_api_key: {key}')

            completion = client.chat.completions.create(
              model="gpt-3.5-turbo",
              messages=[
                # {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
                # {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
                {"role": "user", "content": "Result of 1 + 1"}
              ]
            )

            app.logger.info(completion.choices[0].message)
            res['content'] = str(completion.choices[0].message)

        except Exception as e:
            app.logger.exception(f'请求报错，error: {e}')

    return TEXT_TEMPLATE.format(**res)


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)
