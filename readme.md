# 洛仙都机器人

## 命令
**注意** 所有的命令都可以使用后面加注的中文别称来访问。

### 模块 getRocstarStatus.py
- getRockstarStatus `('服务器状态', 'R星服务器状态', '游戏服务器状态', '服务状态')`
  
  用于查询Rockstar服务器状态，无参数。
  
  返回示例：
  ```
   根据Rockstar官方通报，目前GTA Online各平台服务器状态如下：
   PC 平台：服务正常
   PS4 平台：服务正常
   Xbox One 平台：服务正常
   PS3 平台：服务正常
   Xbox 360 平台：服务正常
   Rockstar Social Club 服务状态：服务正常
   ```


### 模块 Gamepass.py
- getGamePass `('购买账号', '账号购买', '购买黑号', '黑号购买')`
  
  用于购买账号，无参数。
  
  购买账号时，会提示确认购买：
  ```
   @您 要购买价值xx.xx元的游戏账号，是否确定购买？
  ```
  此时，回复`是`、`确认`、`确定`或`购买`，即可触发账号购买操作。
  
  如果账户余额充足，成功扣款，则会向用户私聊发送黑号使用说明，以及黑号账号信息。账号信息的格式如下：
  ```
  您购买的账号信息如下：
  邮箱：xxxxx@yyyyy.com
  邮箱密码：password
  Steam账号：steam
  Steam密码：password
  序列号：SE-RI-AL-NU-MB-ER
  ```
  
- addGamePass `('添加账号', '账号上货')`
  
  用于账号的上货，上货格式：
  ```
  addGamePass
  邮箱1----邮箱1的密码----steam账号1----steam账号1的密码----游戏序列号1
  邮箱2----邮箱2的密码----steam账号2----steam账号2的密码----游戏序列号2
  邮箱3----邮箱3的密码----steam账号3----steam账号3的密码----游戏序列号3
  ...
  ```
  上货完成后，会有回复：
  ```
  上货完成！共有数据n行，成功上货n个，未识别行数为n-m
  ```
- checkGamePass `('查询账号余量', '查询黑号余量')`

  用来查询目前的账号库存。返回示例：
  ```
  当前账号余量：n个
  ```
- setGamePassPrice `('设置黑号价格', '设置账号价格')`
  
  用于设置账号价格，参数格式：
  ```
  setGamePassPrice xx.xx
  ```
- getGamePassPrice `('查询黑号价格', '查询账号价格')`

  无参数，返回示例：
  ```
  当前账号价格：n元
  ```


### 模块 ForthPartyPay.py
- generalDeposit `('充值', '快速充值', 'cz', 'CZ')`
  
  用于监听充值，和020支付进行对接。用户充值格式：
  ```
  generalDeposit 支付宝/微信 金额
  ```
  如果020支付的接口正常，就会回复给用户一个二维码，用户进行扫码支付。
  
  如果020支付的接口出现问题，会给用户回复：
  ```
  获取支付宝/微信二维码错误，请重试或联系群主。
  ```
  并且自动通知到管理群接口错误的详细信息。
- generalManualDeposit `('手动充值', 'sdcz', 'SDCZ')`
  
  用于管理员为客户手动充值，格式如下：
  ```
  generalManualDeposit QQ号 金额
  ```
  充值完成之后会有回复：
  ```
  成功为xxx充值xx.xx元！
  ```
  这个接口 **不会** 自动记账，如果有实际的账目收入，请务必发送记账指令。
- generalManualCost `('手动扣款', 'sdkk', 'SDKK')`
  
  用于管理员售卖服务，如刷钱和解封等无法自动发卡的服务。命令格式：
  ```
  generalManualCost QQ号 扣款项目 金额
  ```
  如果被扣款用户的余额充足，扣款会直接进行，并且在扣款后向被扣款用户发送通知：
  ```
  您已成功购买xxx！付款xx.xx元
  ```
  并且回复管理员：
  ```
  成功对xxx扣款xx.xx元！
  ```
- changeSuccessString `('切换手续费耍赖状态', 'qhsxfsl', 'QHSXFSL')`
- getSuccessString `('查询手续费耍赖状态', 'cxsxfsl', 'CXSXFSL')`


### 模块 account.py


### 模块 faq.py


### 模块 bankstatement.py


