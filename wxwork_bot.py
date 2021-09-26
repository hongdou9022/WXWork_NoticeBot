import requests
import base64
import hashlib


def send_text(bot_key, text, mentioned_list=None):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_key}"
    headers = {"Content-Type": "text/plain"}
    data = {
        "msgtype": "text",
        "text": {
            "content": text,
        }
    }
    if mentioned_list is not None:
        data['text']['mentioned_list'] = mentioned_list
    r = requests.post(url, headers=headers, json=data)
    print(r.text)
    return r.text


def send_markdown(bot_key, text):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_key}"
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": text
        }
    }
    r = requests.post(url, json=data)
    print(r.text)
    return r.text


def send_file(bot_key, file_path):
    file_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={bot_key}&type=file"
    file = {'file': open(file_path, 'rb')}
    result = requests.post(file_url, files=file)
    media_id = eval(result.text)['media_id']
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_key}"
    data = {
        "msgtype": "file",
        "file": {
            "media_id": media_id
        }
    }
    r = requests.post(url, json=data)
    print(r.text)
    return r.text

def send_image(bot_key, file_path):
    with open(file_path, "rb") as f:
        base64_data = base64.b64encode(f.read())
    file = open(file_path, "rb")
    md = hashlib.md5()
    md.update(file.read())
    md5 = md.hexdigest()
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_key}"
    headers = {"Content-Type": "text/plain"}
    data = {
        "msgtype": "image",
        "image": {
            "base64": base64_data.decode('utf-8'),
            "md5": md5
        }
    }
    r = requests.post(url, headers=headers, json=data)
    print(r.text)
    return r.text
