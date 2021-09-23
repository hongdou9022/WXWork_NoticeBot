# 定时通知机器人配置说明
configs目录下添加配置文件, 可以添加多个配置文件, 程序会读取所有配置文件, 同时管理多个机器人的多个任务.  
修改配置后需要依次按停止按钮和开始按钮, 重新载入任务信息.  

Config.json
```json
{
  "Bot": "机器人key",
  "#JobList": "任务列表",
  "JobList": [
    {
      "desc": "描述",
      "active": "bool(true|false), 控制任务是否激活",
      "msgtype": "text/markdown/image/file",
      "url": "请求url获得数据",
      "analysis": "text|json",
      "content": "用于text/markdown发送的正文, image/file无用",
      "#mentioned_list": "用于text, @列表, 所用人用@all, 单人用企业邮箱",
      "mentioned_list": [],
      "file_path": "用于image/file指定文件路径, text/markdown无用",
      "#triggers": "触发器",
      "triggers": {
        "year": "int|str 4位数字",
        "month": "int|str (1-12)",
        "day": "int|str (1-31)",
        "week": "int|str (1-53)",
        "day_of_week": "int|str (0-6 or mon,tue,wed,thu,fri,sat,sun)",
        "hour": "int|str (0-23)",
        "minute": "int|str (0-59)",
        "second": "int|str (0-59)",
        "start_date": "datetime|str 最早可触发的日期/时间（包括）",
        "end_date": "datetime|str 最晚可触发的日期/时间（包括）",
        "timezone": "datetime.tzinfo|str 用于日期/时间计算的时区（默认为调度程序时区）",
        "jitter": "int|str 振动参数，给每次触发添加一个随机浮动秒数"
      }
    }
  ]
}
```

请求url获得数据示例:  
注意: url和analysis必须同时出现, 且content要用{}留出数据插入的位置, 数量和位置需要一一对应
```json
{
 "url": "http://www.weather.com.cn/data/cityinfo/101010100.html",
 "analysis": "json||weatherinfo.city|weatherinfo.temp1|weatherinfo.temp2|weatherinfo.weather",
 "content": "当前{}天气:\n>温度: {}\n>体感温度: {}\n>天气: {}\n>"
}
```
请求url得到的数据为:
"#test"是为展示加的值
```json
{
  "#test1":"200",
  "weatherinfo":{
    "city":"北京",
    "cityid":"101010100",
    "temp1":"18℃",
    "temp2":"31℃",
    "weather":"多云转阴",
    "img1":"n1.gif",
    "img2":"d2.gif",
    "ptime":"18:00",
    "#test2": [
      [1,2,3,4],
      ["a","b","c","d"]
    ]
  }
}
```
analysis: 用|分个开解析元素, 第一个元素json或者text, text不需要后续元素, json需要填后续元素, 第二个元素是校验值, 
    比如填test1=200, 则返回数据中会比对test1是否是200, 是则继续解析, 不是则解析失败, 用于有校验值的api, 不用可不
    填, 第三个之后的元素即为需要解析的数据, weatherinfo.city会取到北京, weatherinfo.#test2[0][1]会取到2, 
    weatherinfo.#test2[1][0]会取到a  

表达式类型  

| 表达式 | 参数类型 | 描述 |
| :---: | :-----: | :---: |
| * | 所有 | 通配符 例：minutes=*即每分钟触发 |
| */a | 所有 | 可被a整除的通配符 |
| a-b |	所有 | 范围a-b触发 |
| a-b/c | 所有 | 范围a-b，且可被c整除时触发 |
| xth y | 日 | 第几个星期几触发。x为第几个，y为星期几 |
| last x | 日 |	一个月中，最后个星期几触发 |
| last | 日 | 一个月最后一天触发 |
| x,y,z | 所有 | 组合表达式，可以组合确定值或上方的表达式 |