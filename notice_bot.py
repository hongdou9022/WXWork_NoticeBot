import json
import os
import time
import requests

import wxwork_bot
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

CONFIGS_PATH = './configs'
CONFIG_ESSENTIAL_DICT = {'Bot': 'str', 'JobList': 'list'}
JOB_ESSENTIAL_DICT = {'desc': 'str', 'active': 'bool', 'msgtype': 'str', 'triggers': 'dict'}
TRIGGER_KEY_LIST = ['year', 'month', 'day', 'week', 'day_of_week',
                    'hour', 'minute', 'second',
                    'start_date', 'end_date',
                    'timezone', 'jitter']


def read_json_file(json_file):
    if not os.path.exists(json_file):
        return -1
    with open(json_file, 'r', encoding='utf-8') as f:
        s = f.read()
        try:
            return json.loads(s)
        except:
            return -2


def get_directory_allfiles(dir, file_list):
    files = os.listdir(dir)
    for f in files:
        pathname = os.path.join(dir, f)
        if os.path.isdir(pathname):
            get_directory_allfiles(pathname, file_list)
        else:
            file_list.append(pathname)


def isinstance_by_str(arg, type_str):
    if type_str == 'str':
        return isinstance(arg, str)
    if type_str == 'list':
        return isinstance(arg, list)
    if type_str == 'dict':
        return isinstance(arg, dict)
    if type_str == 'bool':
        return isinstance(arg, bool)
    return False


class NoticeBot(object):
    __job_list = []
    __config_dict = {}
    __logs = []
    __log_callback = None

    def __init__(self, isBlock=True):
        self.is_ready = False
        self.is_start = False

        if isBlock:
            self.__scheduler = BlockingScheduler()
        else:
            self.__scheduler = BackgroundScheduler()

    def set_log_callback(self, log_callback):
        self.__log_callback = log_callback

    def print_log(self, log):
        log = '{} {}'.format(time.strftime("%H:%M:%S", time.localtime()), log)
        self.__logs.append(f'{log}\n')
        if self.__log_callback is not None:
            self.__log_callback(log)
        print(log)

    def read_all_configs(self):
        self.is_ready = False
        self.__config_dict = {}
        allConfigFiles = []
        get_directory_allfiles(CONFIGS_PATH, allConfigFiles)
        for configFile in allConfigFiles:
            config = read_json_file(configFile)
            if config == -2:
                self.print_log(f'????????????{configFile}????????????json')
                return
            for key, typeStr in CONFIG_ESSENTIAL_DICT.items():
                if key not in config:
                    self.print_log(f'????????????{configFile}????????????????????????, ??????{key}')
                    return
                if not isinstance_by_str(config[key], typeStr):
                    self.print_log(f'????????????{configFile}????????????????????????, {key}????????????:{typeStr}')
                    return
            for index, jobInfo in enumerate(config['JobList']):
                for key, typeStr in JOB_ESSENTIAL_DICT.items():
                    if key not in jobInfo:
                        self.print_log(f'????????????{configFile}????????????????????????, JobList[{index}]?????????{key}')
                        return
                    if not isinstance_by_str(jobInfo[key], typeStr):
                        self.print_log(f'????????????{configFile}????????????????????????, JobList[{index}]{key}????????????:{typeStr}')
                        return
                msgtype = jobInfo['msgtype']
                if msgtype == 'text' or msgtype == 'markdown':
                    if 'content' not in jobInfo.keys():
                        self.print_log(
                            '????????????{}????????????????????????, JobList[{}]?????????[{}]?????????content'.format(configFile, index, jobInfo['desc']))
                        return
                    if 'url' in jobInfo.keys() and 'analysis' not in jobInfo.keys():
                        self.print_log(
                            '????????????{}????????????????????????, JobList[{}]?????????[{}]??????url?????????analysis'.format(configFile, index,
                                                                                        jobInfo['desc']))
                        return
                elif msgtype == 'image' or msgtype == 'file':
                    if 'file_path' not in jobInfo.keys():
                        self.print_log('????????????{}????????????????????????, JobList[{}]?????????[{}]?????????file_path!!!!'.format(configFile, index,
                                                                                                   jobInfo['desc']))
                        return
                    if not os.path.exists(jobInfo['file_path']):
                        self.print_log(
                            '????????????{}????????????????????????, JobList[{}]?????????[{}]???file_path????????????????????????!!!!'.format(configFile, index,
                                                                                              jobInfo['desc']))
                        return
            key = os.path.splitext(os.path.basename(configFile))[0]
            self.__config_dict[key] = config
        self.is_ready = True

    def create_jobs(self):
        self.read_all_configs()
        if not self.is_ready:
            self.print_log('???????????????????????????, ??????????????????, ?????????????????????!!!')
            return

        self.__job_list = []
        for key, config in self.__config_dict.items():
            bot = config['Bot']
            jobConfigList = config['JobList']
            for index, jobInfo in enumerate(jobConfigList):
                if jobInfo["active"]:
                    triggers = jobInfo["triggers"]
                    triggerDict = {}
                    for triggerName in TRIGGER_KEY_LIST:
                        if triggerName in triggers.keys():
                            triggerDict[triggerName] = triggers[triggerName]
                        else:
                            triggerDict[triggerName] = None

                    jobId = f'{key}_{index}'
                    trigger = CronTrigger(year=triggerDict['year'], month=triggerDict['month'], day=triggerDict['day'],
                                          week=triggerDict['week'], day_of_week=triggerDict['day_of_week'],
                                          hour=triggerDict['hour'], minute=triggerDict['minute'],
                                          second=triggerDict['second'], start_date=triggerDict['start_date'],
                                          end_date=triggerDict['end_date'], timezone=triggerDict['timezone'],
                                          jitter=triggerDict['jitter'])
                    job = self.__scheduler.add_job(self.job_handle, trigger=trigger, max_instances=10, id=jobId,
                                                   args=[jobId, bot, jobInfo])
                    self.__job_list.append(job)

    def start(self):
        if not self.is_ready:
            self.print_log('???????????????????????????, ??????????????????, ?????????????????????!!!')
            return
        if self.is_start:
            return
        self.is_start = True
        self.__scheduler.start()
        self.print_log('??????')

    def close(self):
        if not self.is_start:
            return
        self.is_start = False
        self.__scheduler.shutdown(wait=False)
        self.__scheduler.remove_all_jobs()
        self.print_log('??????')


    def get_url_content(self, content, jobInfo):
        """
        :param content:
        :param jobInfo:
        :return: error_msg, content
        """
        response = requests.get(jobInfo['url'])
        if response.status_code != 200:
            return 'URL????????????!!', None
        url_content = response.content
        elements = jobInfo['analysis'].split('|')
        try:
            if elements[0] == 'json':
                data = json.loads(url_content)
                if elements[1] != '':
                    code = elements[1].split('=')
                    if data[code[0]] != code[1]:
                        return 'URL??????????????????!!', None
                params = []
                for i in range(2, len(elements)):
                    param = data
                    items = elements[i].split('.')
                    for item in items:
                        if item.find('[') == -1:
                            param = param[item]
                        else:
                            index = item.split('[')
                            if index[0] != '0':
                                param = param[index[0]]
                            for j in range(1, len(index)):
                                param = param[int(index[j].replace(']', ''))]
                    params.append(param)
                return None, content.format(*params)
            elif elements[0] == 'text':
                return None, content.format(url_content)
        except Exception as e:
            return f'URL??????????????????????????????, ????????????: {e}!!', None

    def job_handle(self, job_id, bot, job_info):
        try:
            result = ''
            msgtype = job_info['msgtype']
            if msgtype == 'text' or msgtype == 'markdown':
                content = job_info['content']
                if 'url' in job_info.keys():
                    error_msg, content = self.get_url_content(content, job_info)
                    if error_msg is not None:
                        self.print_log('job[{}] {} ????????????! URL????????????: {}'.format(job_id, job_info['desc'], error_msg))
                        return

                if msgtype == 'text':
                    mentioned_list = []
                    if 'mentioned_list' in job_info.keys() and isinstance(job_info['mentioned_list'], list):
                        mentioned_list = job_info['mentioned_list']
                    result = wxwork_bot.send_text(bot, content, mentioned_list)
                else:
                    result = wxwork_bot.send_markdown(bot, content)
            elif msgtype == 'image':
                result = wxwork_bot.send_image(bot, job_info['file_path'])
            elif msgtype == 'file':
                result = wxwork_bot.send_file(bot, job_info['file_path'])

            result = json.loads(result)
            if result["errcode"] == 0:
                self.print_log('job[{}] {} ????????????!'.format(job_id, job_info['desc']))
            else:
                self.print_log('job[{}] {} ????????????! ?????????: {}, ????????????: {}.'.format(job_id, job_info['desc'], result["errcode"],
                                                                            result["errmsg"]))
        except Exception as e:
            self.print_log('job[{}] {} ????????????! ????????????: {}.'.format(job_id, job_info['desc'], e))

    def __del__(self):
        if not self.is_start:
            return
        self.__scheduler.shutdown(wait=False)
