# QiniuManager

七牛云本地调用

### 安装

```bash
    $ sudo pip install qiniumanager --upgrade
```

### 七牛云存储 Qiniu Manager

```
七牛云存储 Qiniu Manager

Usage:
  qiniu <your file> [space]		选择文件位置上传，指定空间名或使用默认空间名
  qiniu [option] <file name> [space]	对云空间中文件进行操作
  qiniu [--key|-k] <access key> <secret key>	设置密钥

  --version,-v	当前版本号
  --space,-s	修改或查看当前空间名
  --remove,-r	删除云文件
  --private,-p	返回私有文件下载链接
  --download,-d	下载文件
  --list-a,-la	显示本地已知所有空间文件列表
  --check,-c	查看文件状态
  --rename,-n	重命名
  --key,-k	修改或查看access key，secret key
  --link,-i	返回开放云空间文件下载链接
  --list,-l	文件列表
  --r-space,-rs	删除本地保存的空间名
  --help,-h	帮助

首次使用请设置密钥对 qiniu [--key|-k] <access key> <secret key>
必要情况下请设置默认空间名
```

### 具体操作

####显示帮助信息方式

```bash
	qiniu
	qiniu -v # QiniuManager 版本以及SDK版本
```

####基本设置

i.密钥设置
```bash
	qiniu -k <access key> <secret key>	
	qiniu -k # 显示密钥对
```

![这里的AK及SK](https://static.hellflame.net/resource/5ccf929aae10fc0fb5a26a63c28e6d45)

ii.空间设置(bucket)

```bash
	qiniu -s share # 可以省略测试域名
	qiniu -s share 7xqh1q.dl1.z0.glb.clouddn.com
	qiniu -s # 显示空间信息(bucket)
```

![space & alias](https://static.hellflame.net/resource/e506e9787b0a693da3a4d5be381b28ad)

>好吧，一直用的测试域名，对于对外开放的空间访问的话，并不需要设置这个`alias`，只需要`qiniu -s share`即可（换成自己的空间名），对于私有空间，对于我而言，这个测试域名的使用是必要的
>
>在每次设置过空间名之后，当前默认空间名都会指向该空间(bucket),可以通过`qiniu -s`最后一行信息验证默认空间(bucket)
>
>如果不设置空间名的话，对于开放空间可能没有什么影响，但是对于如我一般的免费用户的话，没有开启自定义域名，只能使用测试域名，这样的话，只在下载的时候指定空间名将会导致生成一个无效的链接

iii.删除本地保存的空间信息

```bash
	qiniu -rs <space name> # 尝试删除空间名为<space name>的空间信息
```

该操作仅仅针对本地数据库，并不会影响实际空间的存在；如果删除一个并没有保存进本地数据库的空间名并不会报错，因为在执行SQL语句之前并没有判断该空间名是否存在于数据库(~/.qiniu.sql)中，如果被删除的空间是默认空间的话，需要再一次手动指定默认空间，否则默认空间为空


#### 基本操作

i.文件列表

> 默认按照上传时间先后逆排序

```bash
	qiniu -l # 显示当前空间(bucket)文件列表
	qiniu -l backup # 显示`backup`中的文件列表
```

> 可以显示已经保存下来的所有空间的文件列表总表，这里的已知空间可以通过`qiniu -s`查看空间列表信息

```bash
	qiniu -la # 显示已知所有空间的文件列表
```

在显示的时候其实有一个问题，就是非英文字符在终端打印时所占的宽度与英文字符宽度不同(应该是等宽字体并不包含其他语言文字的缘故)，导致排版略错乱

![list issue - terminal font type](https://static.hellflame.net/resource/9cd1d0ab79aa311a65dda6923c5ef1b0)

中文字符很显然打印出来的宽度并不与英文字符打印出来的宽度一致，并且这里的文件名称也转换为utf8字符计算长度(一个中文字符有三个字节的长度)

ii.文件详情

> 对于文件名中存在空格或者其他特殊符号的情况，用引号将目标文件名包裹起来就好了，在以下其他地方也适用

```bash
	qiniu -c <filename> # 显示当前空间(bucket)中<filename>的信息(讲真这个信息炒鸡简略)
	qiniu -c <filename> <space name> # 显示<space name>这个空间(bucket)中<filename>的信息
```

iii.获取下载链接

```bash
	# 获取开放空间的有效链接
	qiniu -i <filename> # 获取当前空间(bucket)中<filename>的下载链接
	qiniu -i <filename> <space name> # 获取<space name>中<filename>的下载链接
	# 获取私有空间的有效链接(expire 3600)
	qiniu -p <filename> # 获取当前空间(bucket)中<filename>的私有下载链接,开放空间返回的链接可下载，但不会被expire限制可下载时间
	qiniu -p <filename> <space name># 获取<space name>中<filename>的私有下载链接，开放空间返回的链接可下载，但不会被expire限制可下载时间
```

> 如果不知道该空间是否为私有空间，直接用`qiniu -p `获取的链接将保证对于开放空间以及私有空间都有效，前提是能够正确设置空间的测试域名(对于作者这样的免费用户而言)
> 
> 当然，还是知道空间的开放和私有属性比较好

![private and public](https://static.hellflame.net/resource/b74f36b5f05569fa005952e5a90561da)

iv.下载

```bash
	qiniu -d <filename> # 下载当前空间(bucket)中的<filename>
	qiniu -d <filename> <space name> # 下载<space name>空间(bucket)中的<filename>
```

> 下载的文件存储在当前目录，与空间中文件名相同
> 
> 正常的话，应该会显示下载进度条

![progress](https://static.hellflame.net/resource/7dc3b5f8d42a49d2233d152c6779b829)
![finished](https://static.hellflame.net/resource/a51952d5e39ab3c3308fced9ed79db1a)

>不正常的话，进度条可能会不能正常显示，不过如果还好的话，最终文件还是会正常下载完毕
>
>如果崩溃的话，还是老老实实`wget url -O <filename>`好了
>
>这部分在调整了下载缓存大小并且优化了保存时候的状态判断之后，基本上能够独立使用了，不过这部分的http报文处理部分舍弃了对于chucked编码的支持

关于这部分，主要想吐槽一下chucked编码。其实http报文本身即便不使用chucked编码，也是炒鸡难受的，甚至通过TCP来传递数据也是挺难受的，因为客户端在一开始并不知道要接收多长的数据。。。在一开始，客户端并不知道将要接收多少数据，作为header部分，如果运气不好的话，也许header部分还没有接收完，第一次recv就结束了，然后header就被截断了，也许第一次recv接收太长了，header接收完之后继续接收了报文实体部分，甚至整个报文都接收完了，如果是chucked编码的话，更不巧的是把每一个chucked编码块的那个十六进制长度字符串给截断了，那么接下来到底有多少是真正的实体内容呢？即便第一次获取报文长度运气还好，但是对于chucked编码，每次获取的时候都要对接收到的内容判断一下这次接收的内容里面有多少个chucked块，以及下一次读取应该需要多少长度等等麻烦的问题

不过，上述问题应该还是只会出现在该项目中包含的http报文处理中，因为想要实现流水式的获取报文，而不是把报文所有内容都接收完之后再处理，这样在面对大文件传输的时候可能对内存会有较大的压力(当然，可以用缓存来解决这个问题)，并且能够真实的记录下载报文的进度

由于七牛的服务器并没有使用chucked编码，所以这里就取消了chucked编码支持

v.删除
```bash
	qiniu -r <filename> # 删除当前空间(bucket)中的<filename>
	qiniu -r <filename> <space name> # 删除<space name>空间(bucket)中的<filename>
```

> 想要吐槽的是，无论是七牛SDK的返回值规范性还是七牛服务器的返回值的规范性都不是很一致（与自己所认为的规范性不是很一致）

![confuse](https://static.hellflame.net/resource/8db93d0655185b086dde5ec2a4b8b9b6)

其实个人的做法更倾向于在成功时也返回一个json字符串，给出一个status表示操作成功，然而这里并没有。在查看服务器的返回值时，这个就更清楚了，服务器的response中，body部分的确是空的，`Content-Length: 0`，这也让我需要对这部分请求作特别的处理，比如禁用下载进度条(这是自己写的HTTP报文发送以及接受的方法中需要的)

以及SDK中在使用POST方法的大环境下，调用了少量GET方法接口，于是在生成Token的时候需要对GET的data也进行操作

![](https://static.hellflame.net/resource/053660e4f3d6751c827c2bfe62aaa38c)

于是重写添加了一个和验证POST Token差不多的Token的方式(因为token的生成是与传递的数据实体有关的)

这里也出现了`Content-Type: application/x-www-form-urlencoded`这个一般只在网页上的form表单才出现的content-type。虽然我还不是很清楚这个content-type在这里出现的意义，但是应该是在某个地方处理到了模仿form表单上传数据吧，也说明这部分也许是直接调用了网页端的接口，也许这也是接口规范不一致的表现之一吧

vi.查看单个文件

```bash
	qiniu -c <filename> # 查看当前空间(bucket)中<filename>的一般属性，实际上并没有太详细的信息的样子
	qiniu -c <filename> <space name> # 查看<space name>空间(bucket)中的<filename>的一般信息
```

![qiniu -c](https://static.hellflame.net/resource/ffcf828ae54effbb8bb3e669b43db2ec)

好吧，总觉得这些信息甚至都没有这个文件被下载或者引用的次数什么的，意义看上去不是太大的样子。顺便一说，这里服务器返回的文件上传时间被'精确'了10000000倍，好吧，这里应该说至少精确了1000倍(到达毫秒级)，剩下的应该是随机值吧(自己做的静态文件服务器也有类似的处理)

vii.重命名
```bash
	qiniu -n <target file> <to file> # 将当前空间中的<target file>重命名为<to file>
	qiniu -n <target file> <to file> <space name> # 将<space name>空间中的<target file>重命名为<space name>空间中的<to file>
```

![sdk move](https://static.hellflame.net/resource/45dfd760b9d4dcf54ecd6ea81f32b8a1)

实际上重命名接口在SDK中和移动资源方法是同一个，并且支持在不同的空间之间进行移动，但是作者认为在命令行中输入这么多参数已经很烦了，也并没有需求在不同空间之间进行资源操作，于是`QiniuManager`限制了重命名只能在当前空间

![](https://static.hellflame.net/resource/aef205f6251e8e50e42f034193fe8b26)

如果需要支持在不同空间之间进行资源移动的话，在上述代码中将第二个`space`换成目标space就好了，还有能够看到的是，里面中文翻译都是叫的空间，但是英文名却叫"bucket",表示并不清楚这个翻译的来源

![](https://static.hellflame.net/resource/54fbc0df69cbb8df1296f5712ee23c09)

我是不是应该也把这个叫做不规范讷

#### Issue
##### nodename nor servname provided, or not known

如果测试域名配置如下

![hostname unknown](https://static.hellflame.net/resource/e086339b219f691db1a1052f349deadb)

可能就会报如下错误，因为这个域名无效('7ktpup.com1.z0.glb.clouddn.com')

![hostname not valid](https://static.hellflame.net/resource/748ee73149aa605434221204397b39df)

可能的原因是七牛云没有解析所有的测试域名，处理方法就是在配置域名时，需要将测试域名配置为那个可用的域名,如`qiniu -s whatever whatever.qiniudn.com`(或者在一开始并不用设置测试域名，或者在本机的hosts文件中指定ip)，但是实际上并不知道七牛云的域名如何管理的，所以要知道哪个域名是可用的话，在`内容管理`界面查看外链，就知道至少哪一个域名是可用的了

关注了一段时间，发现这个域名只是偶尔无效(最近无效大概发生在凌晨，这次大概在5点左右？)，难道是服务器夜间维护？还是遭到攻击？还是日志统计需要？好吧，无论如何，这是一个问题，我也只能选择合适的时机使用

##### database is locked

![database lock](https://static.hellflame.net/resource/9869b5ac1d20097cb2e8a78cba81cc5f)

qiniuManager现在同时只能运行一个实例，因为manager从用户家目录下的一个SQLite数据库文件获取密钥，并且在程序开始运行时获取这个数据库，在程序结束时释放，如果某一个时刻正在下载一个大文件，一直占用数据库的话，再运行程序便会报这个错误。不过貌似并没有出现致命错误(对于SQLite我还不是很了解)。要修复这个问题的话，只要及时释放SQLite就好了，不过我并没有这么做，因为和整个程序一开始设计时候的构思并不一样(其实是因为懒)

##### 注入漏洞

项目使用`SQLite3`作为数据库支持，数据库文件位于`~/.qiniu.sql`，并将密钥对明文存储在数据库中，将空间名称存于数据库，这两个数据由于都是用户自己输入其中的，所以除非自己想的话，自己可以给自己的数据库注入，如果使用了特别的语句想要注入的话，应该还是比较简单的，当然我自己是不会自己尝试的

![](https://static.hellflame.net/resource/be76316468bca0bd2cd753cca17c82fe)

### 历史版本

+   v0.9.12 修复无法上传中文文件名文件的错误
+   v0.9.13 下载输出优化
+   v0.9.14 私有空间文件下载
+   v0.9.15 下载前预判以及输出微调
+   v0.9.16 消除参数获取失败后的报错方式
+   v0.9.17 未安装curl下载失败
+   v1.1.0  基本从底层重写了一遍，尽量直接调用了API链接
+   v1.1.1  urllib.quote
+   v1.1.2  取消本地判断mimetype(因为会莫名卡在这里，并且上传这个mimetype的时候会告诉我这是未知的mimetype，所以实际上并没有用),取消上传缓存
+   v1.1.3  文件列表统计总量
+   v1.1.4  文件列表排序支持，默认按照上传时间逆序排序，修复单位转换中的小数丢失
+   v1.2.0  底层http报文处理，适当调整响应缓存大小，提高下载速度等，'chucked'编码暂时不可用
+   v1.2.1  删除本地保存的空间名支持，显示所有已知空间文件列表并统计大小支持，http报文处理去除chucked编码支持(chucked编码真是恶心)，下载文件预判，防止本地文件被覆盖，判断文件是否存在后再下载；部分显示格式调整


