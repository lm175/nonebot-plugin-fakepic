<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-fakepic

_✨ NoneBot伪造聊天截图插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/lm175/nonebot-plugin-fakepic.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-fakepic">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-fakepic.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>


</details>

## 📖 介绍

nonebot2插件，使用pillow库进行图片绘制

使用示例: 3889009218【2.5条悟】说你好像误会了什么 你才是挑战者+1980765716说龙鳞，反反，成双之流星+3889009218说抱歉没能让宿傩大人尽兴

## 💿 安装

<details open>
<summary>（推荐）使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-fakepic

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

    pip install nonebot-plugin-fakepic


打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_fakepic"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| fakepic_user_split | 否 | "+" | 分隔不同用户的符号 |
| fakepic_message_split | 否 | " " | 分隔同一用户的几条消息 |
| fakepic_nick_start | 否 | "【" | 获取昵称的起始符号 |
| fakepic_nick_end | 否 | "】" | 获取昵称的终止符号 |
| fakepic_add_level_icon | 否 | True | 是否为用户添加等级图标 |
| fakepic_add_bot_icon | 否 | True | 是否为官方机器人添加bot图标 |
| fakepic_del_cqface | 否 | True | 是否删除QQ表情的CQ码 |
| fakepic_nick_font | 否 | "" | 昵称首选字体 |
| fakepic_chat_font | 否 | "" | 聊天首选字体 |
| fakepic_fallback_nickfonts | 否 | [] | 昵称备选字体 |
| fakepic_fallback_chatfont | 否 | [] | 聊天备选字体 |

若添加字体配置后文字位置发生较大偏移，可添加以下配置进行修正

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| fakepic_correct_nick | 否 | [0, 0] | 昵称位置 |
| fakepic_correct_chat | 否 | [0, 0] | 聊天文字位置 |

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| <QQ号>说<消息内容> | 无 | 否 | 私聊/群聊 | 分隔符号可在配置中修改 |
| <QQ号>【用户昵称】说<消息内容> | 无 | 否 | 私聊/群聊 | 指定用户昵称 |


### 效果图
<img src="https://github.com/lm175/nonebot-plugin-fakepic/blob/master/preview/command.jpg" width="606" height="826" />
<img src="https://github.com/lm175/nonebot-plugin-fakepic/blob/master/preview/result.png" width="450" height="640" />

## 更新日志
### [0.2.0] - 2024-11-16
- 可在指令中通过【】符号指定用户的昵称
- 增加备选字体的配置项