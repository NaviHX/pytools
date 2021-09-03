# bilibili弹幕姬-python

一个简易的python弹幕姬，使用curses绘制界面，asiowebsocket进行ws通信。

# 配置

弹幕姬配置文件为`config.json`，各条目含义如下

|配置|含义|
|-|-|
|enable|开启对应信息的输出，True：输出礼物信息、直播开始结束、人气值信息|
|roomid|需要捕获弹幕的房间号|
|format|输出信息的格式|
|size|gui的样式|
|csrf / csrf_token / cookie|`(optional)`发送弹幕的设置|

## format配置

弹幕姬会将捕获到的弹幕信息按照`format`中的格式输出

|配置|含义|支持的变量|
|-|-|-|
|danmu|普通的弹幕信息|uname：发送者ID message：弹幕|
|gift|礼物信息|uname：发送者ID action：发送礼物的动作 num：礼物数量 gift：礼物名称|
|live|直播开始提示| - |
|preparing|直播结束/准备中提示| - |
|other|不能识别的信息|cmd：接收的指令|
|hot|直播间人气值|hot：人气值|

## UI配置

UI的配置在`size`项中

界面分为了在上方的接收框与在下方的发送框，两个框的宽度相同

|配置|含义|
|-|-|
|output_lines|输出框的高度|
|input_lines|输入框的高度|
|width|宽度|

## 发送弹幕配置

弹幕姬支持发送弹幕。使用发送功能需要进行配置cookie与csrf相关的变量。csrf的值一般不发生变化，cookie值需要每次进入直播间时重新获取。

获取方法为打开直播间，打开浏览器`F12`的控制台，选择`network`标签，在直播间发送一条弹幕，在`filter`栏中搜索send，点击搜索结果，在request header中可以找到。
