# QiniuManager

七牛云本地调用

### 安装

```bash
$ sudo pip install qiniumanager --upgrade
```

> Mac OS 如果出现权限问题，则可用以下方法安装，可执行脚本路径在
> `/Users/<username>/Library/Python/2.7/bin/`

```bash
$ pip install qiniumanager --upgrade --user
```

### 七牛云存储 Qiniu Manager

```
七牛云存储 Qiniu Manager

Usage:
  qiniu <your file> [space]     选择文件位置上传，指定空间名或使用默认空间名
  qiniu [option] <file name> [space]    对云空间中文件进行操作
  qiniu [--key|-k] <access key> <secret key>    设置密钥

  --drename,-dr     调试重命名
  --private,-p      返回私有文件下载链接
  --remove,-r       删除云文件
  --export,-x       导出默认或指定空间文件下载链接
  --download,-d     下载文件
  --ddebug,-dd      调试下载
  --list-a,-la      显示本地已知所有空间文件列表
  --check,-c        查看文件状态
  --space,-s        修改或查看当前空间名
  --rename,-n       重命名
  --list-ex,-le     显示请求空间文件列表http报文
  --key,-k      修改或查看access key，secret key
  --link,-i     返回开放云空间文件下载链接
  --check-e,-ce     显示请求文件状态的http报文
  --list,-l     文件列表
  --r-space,-rs     删除本地保存的空间名
  --version,-v      当前版本号
  --help,-h     显示当前帮助页面

首次使用请设置密钥对 qiniu [--key|-k] <access key> <secret key>
必要情况下请设置默认空间名

更多帮助信息
https://github.com/hellflame/qiniu_manager/blob/v1.3.3/README.md
```

### 具体操作

#### 显示帮助信息方式

```bash
$ qiniu
$ qiniu -v # QiniuManager 版本
```

#### 基本设置

##### i.密钥设置

```bash
$ qiniu -k <access key> <secret key>  
$ qiniu -k # 显示密钥对
```

![这里的AK及SK](https://static.hellflame.net/resource/5ccf929aae10fc0fb5a26a63c28e6d45)

##### ii.空间设置(bucket)

```bash
$ qiniu -s share # 可以省略测试域名
$ qiniu -s share 7xqh1q.dl1.z0.glb.clouddn.com
$ qiniu -s # 显示空间信息(bucket)
```

![space & alias](https://static.hellflame.net/resource/e506e9787b0a693da3a4d5be381b28ad)

好吧，一直用的测试域名，对于对外开放的空间访问的话，并不需要设置这个`alias`，只需要`qiniu -s share`即可（换成自己的空间名），对于私有空间，对于我而言，这个测试域名的使用是必要的

在每次设置过空间名之后，当前默认空间名都会指向该空间(bucket),可以通过`qiniu -s`最后一行信息验证默认空间(bucket)

如果不设置空间名的话，对于开放空间可能没有什么影响，但是对于如我一般的免费用户的话，没有开启自定义域名，只能使用测试域名，这样的话，只在下载的时候指定空间名将会导致生成一个无效的链接，主要是无效域名

##### iii.删除本地保存的空间信息

```bash
$ qiniu -rs <space name> # 尝试删除空间名为<space name>的空间信息
```

该操作仅仅针对本地数据库，并不会影响实际空间的存在；如果删除一个并没有保存进本地数据库的空间名并不会报错，因为在执行SQL语句之前并没有判断该空间名是否存在于数据库(~/.qiniu.sql)中，如果被删除的空间是默认空间的话，需要再一次手动指定默认空间，否则默认空间为空

#### 基本操作

##### i.上传

```bash
$ qiniu <file to upload> # 上传文件到默认空间(bucket)
$ qiniu <file to upload> <space name> # 上传文件到空间<space name>
```

这里如果没有设置默认空间名的话，上传结束之后会报错显示不存在这个bucket(空间)，因为如果获取不到默认空间名的话，空间名就是`''`(空字符串)，如果上传指定的空间不存在的话，也会报同样的错误

进度条显示偶尔出现满载情况的原因是，，忘了禁用单次上传后获取数据的进度显示，如果某一次网速变慢的话，就会偶尔出现进度条突然挤到100%的情况，因为上传是按照4M大小分块上传，并且需要收集服务器的回馈信息，用于最终创建文件，并且http报文的处理默认是启用进度条的，所以在每次上传分块结束之后有概率看到不连续的数值显示(来自分块上传数据)，更新之后已经禁用局部进度条显示

这里由于参数获取机制的问题，如果`<file to uplaod>`部分接了一个不存在的操作，会被当作上传文件到默认空间处理，`qiniu -d`等，一般情况下会报错`-d 这个文件不存在`类似的错误，不过要是真的存在着么一个`-d`文件的话，真的会尝试上传上去的

七牛云对于上传接口的处理，感觉还有很大一部分出于对安全的考虑，客户端与服务器进行通信时，内容都存在安全校验，`upload token`以及`Qbox token`什么的，所以文件分块上传的内容在最终创建文件之前都是没有意义的，需要客户端最终告诉服务器自己上传了哪些块，这些块都是属于哪一个文件的，这样服务器才会让这个文件上传结束，如果我在短时间内上传很多的文件分块，却不上传最终创建文件的`block info`的话，服务器的临时或者永久存储空间会不会被耗尽捏？或者是不是每一个用户有着最大的缓存大小限制呢？也许这就是对于客户端不信任的结果讷？在文件上传处理上，其实个人的静态文件服务器刚好和七牛云相反，我在一开始便上传了一个文件的基本信息，然后接下来上传的每一个分块都会带有与这个文件ID相匹配的标示，这样的话在第一次上传文件信息的时候文件就已经存在了，剩下的工作就是上传这个文件的每一个分块，如果上传同一个分块，那么服务器在检查header的时候就会直接放弃本脆上传的实体内容，返回成功标识，如果某一个分块上传失败，服务器并不会记录这个块的信息，如果在块不完整的情况下请求一个文件，服务器会返回409错误标识数据不完整。虽然不能说两种处理策略哪一个更好，但是就服务器资盘占用上来说，个人的静态文件处理会好一点

##### ii.文件列表

默认按照上传时间先后逆排序

```bash
$ qiniu -l # 显示当前空间(bucket)文件列表
$ qiniu -l backup # 显示`backup`中的文件列表
```

可以显示已经保存下来的所有空间的文件列表总表，这里的已知空间可以通过`qiniu -s`查看空间列表信息

```bash
$ qiniu -la # 显示已知所有空间的文件列表
```

在显示的时候其实有一个问题，就是非英文字符在终端打印时所占的宽度与英文字符宽度不同(应该是等宽字体并不包含其他语言文字的缘故)，导致排版略错乱

![list issue - terminal font type](https://static.hellflame.net/resource/9cd1d0ab79aa311a65dda6923c5ef1b0)

中文字符很显然打印出来的宽度并不与英文字符打印出来的宽度一致，并且这里的文件名称也转换为utf8字符计算长度(一个中文字符有三个字节的长度)，这个问题也会出现在上传或者下载进度条的时候，导致整个进度条看上去长度并不一致

> 这里存在一个可调式的模式调用

这个模式存在的意义在于让这个请求到响应过程都清晰明了

```bash 
# 显示列表操作的HTTP发起请求到获取的整个HTTP响应

$ qiniu -le 
$ qiniu -le <bucket name> # 空间名称
```

调试结果的可能返回界面

![响应结果](https://static.hellflame.net/resource/c25077a48f5690f3e161b220a078776f)

##### iii.文件详情

对于文件名中存在空格或者其他特殊符号的情况，用引号将目标文件名包裹起来就好了，在以下其他地方也适用

```bash
$ qiniu -c <filename> # 显示当前空间(bucket)中<filename>的信息(讲真这个信息炒鸡简略)
$ qiniu -c <filename> <space name> # 显示<space name>这个空间(bucket)中<filename>的信息
```

![qiniu -c](https://static.hellflame.net/resource/ffcf828ae54effbb8bb3e669b43db2ec)

好吧，总觉得这些信息甚至都没有这个文件被下载或者引用的次数什么的，意义看上去不是太大的样子。顺便一说，这里服务器返回的文件上传时间被'精确'了10000000倍，好吧，这里应该说至少精确了1000倍(到达毫秒级)，剩下的应该是随机值吧(自己做的静态文件服务器也有类似的处理)，因为实际上我只觉得秒级别对于普通用户而言已经很精确了

> v1.3.3 添加在所有空间中查找的功能

![遍历查询](https://static.hellflame.net/resource/65b1e9d28fe2a602ee30bee2f84de5e9)

程序会从默认空间开始查询给定文件，直到查找到，或者遍历完所有空间。遍历空间的范围通过 `qiniu -s` 可以查看。可以给定开始查找的空间，通过 `qiniu -c xxxx space` ，就可以先从space这个空间开始查找指定文件，找不到的话再从其他空间查找。

由于查看文件详情这样的功能一般都会是人手动查看，所以仅有这个功能添加了自动遍历查找的功能，输出的结果也在这一版本之后发生些许变化(然而再怎么变，官方给的输出都是那么一点点)

![文件详情](https://static.hellflame.net/resource/55795fc256e92140997aa91d606b0253)

如果不指定查找的空间的话，就可能出现自动遍历的情况。另外，在输出当中，给出了查找到该文件的空间名称和具体的文件大小(精确到B)，以及时间戳(精确到毫秒)。

> 这里存在一个可调式的模式调用

```bash
$ qiniu -ce <filename>
$ qiniu -ce <filename> <space name>
```

调试结果的可能返回界面

![响应结果](https://static.hellflame.net/resource/c29bde23662503d278ba215ca8f63fc8)

> v1.3.3 之后调试输出的结果可能会更多一点，毕竟会遍历很多空间

##### iv.获取下载链接

```bash
# 获取开放空间的有效链接
$ qiniu -i <filename> # 获取当前空间(bucket)中<filename>的下载链接
$ qiniu -i <filename> <space name> # 获取<space name>中<filename>的下载链接
# 获取私有空间的有效链接(expire 3600)
$ qiniu -p <filename> # 获取当前空间(bucket)中<filename>的私有下载链接,开放空间返回的链接可下载，但不会被expire限制可下载时间
$ qiniu -p <filename> <space name># 获取<space name>中<filename>的私有下载链接，开放空间返回的链接可下载，但不会被expire限制可下载时间
```

如果不知道该空间是否为私有空间，直接用`qiniu -p <target>`获取的链接将保证对于开放空间以及私有空间都有效，前提是能够正确设置空间的测试域名(对于作者这样的免费用户而言)。对于一个只有测试域名的空间来说，这个测试域名也是唯一有效的域名，必须将这个域名通过`-s`参数绑定给这个空间，否则下载链接将不可用

当然，还是知道空间的开放和私有属性比较好，事先check一下文件的状态也可以，或者直接用`-d`下载的时候会判断文件链接是否有效

![private and public](https://static.hellflame.net/resource/b74f36b5f05569fa005952e5a90561da)

##### v.下载

```bash
$ qiniu -d <filename> # 下载当前空间(bucket)中的<filename>
$ qiniu -d <filename> <space name> # 下载<space name>空间(bucket)中的<filename>
```

下载的文件存储在当前目录，与空间中文件名相同，如果当前目录存在同名文件，将用后缀的形式区分新下载的文件和旧文件，当判断文档不存在时，并不会下载空间的默认处理方式，而是报告404错误

正常的话，应该会显示下载进度条

![progress](https://static.hellflame.net/resource/7dc3b5f8d42a49d2233d152c6779b829)

![finished](https://static.hellflame.net/resource/a51952d5e39ab3c3308fced9ed79db1a)

如果崩溃的话，还是老老实实`wget url -O <filename>`或者`wget --content-disposition url`好了

这部分在调整了下载缓存大小并且优化了保存时候的状态判断之后，基本上能够独立使用了，不过这部分的http报文处理部分舍弃了对于chucked编码的支持

关于这部分，主要想吐槽一下chuncked编码。其实http报文本身即便不使用chucked编码，也是炒鸡难受的，甚至通过TCP来传递数据也是挺难受的，因为客户端在一开始并不知道要接收多长的数据。。。在一开始，客户端并不知道将要接收多少数据，作为header部分，如果运气不好的话，也许header部分还没有接收完，第一次recv就结束了，然后header就被截断了，也许第一次recv接收太长了，header接收完之后继续接收了报文实体部分，甚至整个报文都接收完了，如果是chucked编码的话，更不巧的是把每一个chucked编码块的那个十六进制长度字符串给截断了，那么接下来到底有多少是真正的实体内容呢？即便第一次获取报文长度运气还好，但是对于chucked编码，每次获取的时候都要对接收到的内容判断一下这次接收的内容里面有多少个chuncked块，以及下一次读取应该需要多少长度等等麻烦的问题，说到底，chuncked编码不过是服务器生成比较方便而已，并没有考虑过客户端的感受。如果某一天客户端也支持在POST数据的时候使用类似chuncked的编码的话，服务器是不是也要稍微烦恼一下捏

不过，上述问题应该还是只会出现在该项目中包含的http报文处理中，因为想要实现流水式的获取报文，而不是把报文所有内容都接收完之后再处理(看到过类似的处理)，这样在面对大文件传输的时候可能对内存会有较大的压力(当然，可以用缓存来解决这个问题)，并且能够真实的记录下载报文的进度

由于七牛的服务器并没有使用chucked编码，所以这里就取消了chucked编码支持

关于chuncked编码的处理，也许在另一个项目中会继续处理，这里的话，就暂时跳过好了

对于chucked编码，总有一种这是某个人心血来潮想出来的方案，服务器倒是很方便了，每次想要生产多少数据就生产多少数据，为什么就不能在上一次生产数据之后把下一次将要生产的数据的大小的字符串的长度也一起记录进去呢？这样至少我知道下一次需要接收多少字节作为下一个块，甚至知道更下一个块的长度信息，这么做起来真的很难么

- `v1.2.6`中添加指定下载目录的支持

```bash
$ qiniu -d <target file> -t <dir> # 在当前默认空间(bucket)中下载<dir>/<target file>
$ qiniu -d <target file> <space name> -t <dir> # 下载<space name>中的文件到<dir>/<target file>
```

新的支持基本上就是在原来的下载指令后面接上指定目录的操作；在执行操作之前，程序会预先判断指定的目录`<dir>`是否存在，如果不存在的话，将放弃进一步操作。同样，如果下载的文件名中包含`/`等特殊字符的，文件最终会保存为实际文件名

- `v1.3.0`中添加了调试命令的支持

```bash
$ qiniu -dd <filename>
$ qiniu -dd <filename> <space name>
```

可能的响应结果如下

![](https://static.hellflame.net/resource/803653eb10bb1a8d08f5d3c4094babe5)

##### vi.删除

```bash
$ qiniu -r <filename> # 删除当前空间(bucket)中的<filename>
$ qiniu -r <filename> <space name> # 删除<space name>空间(bucket)中的<filename>
```

想要吐槽的是，无论是七牛SDK的返回值规范性还是七牛服务器的返回值的规范性都不是很一致（与自己所认为的规范性不是很一致）

![confuse](https://static.hellflame.net/resource/8db93d0655185b086dde5ec2a4b8b9b6)

其实个人的做法更倾向于在成功时也返回一个json字符串，给出一个status表示操作成功，然而这里并没有。在查看服务器的返回值时，这个就更清楚了，服务器的response中，body部分的确是空的，`Content-Length: 0`，这也让我需要对这部分请求作特别的处理，比如禁用下载进度条(这是自己写的HTTP报文发送以及接受的方法中需要的)

以及SDK中使用了POST和GET方法，于是在生成Token的时候需要对两种方法传递的参数生成凭证，为什么就不能统一使用一种方法呢？

![](https://static.hellflame.net/resource/053660e4f3d6751c827c2bfe62aaa38c)

于是重新添加了一个和验证POST Token差不多的Token的方式(因为token的生成是与传递的数据实体有关的)

这里也出现了`Content-Type: application/x-www-form-urlencoded`这个一般只在网页上的form表单才出现的content-type。虽然我还不是很清楚这个content-type在这里出现的意义，但是应该是在某个地方处理到了模仿form表单上传数据吧，也说明这部分也许是直接调用了网页端的接口，也许这也是接口规范不一致的表现之一吧(自从有了ajax，我就一直很排斥form表单上传这样的存在了，即便是用js模拟from表单上传这样的行为。好吧，貌似也是因为并不是所有浏览器都支持File，FileReader或者类似的功能的样子，万恶的Old Browsers)

##### vii.重命名

```bash
$ qiniu -n <target file> <to file> # 将当前空间中的<target file>重命名为<to file>
$ qiniu -n <target file> <to file> <space name> # 将<space name>空间中的<target file>重命名为<space name>空间中的<to file>
```

![sdk move](https://static.hellflame.net/resource/45dfd760b9d4dcf54ecd6ea81f32b8a1)

实际上重命名接口在SDK中和移动资源方法是同一个，并且支持在不同的空间之间进行移动，但是个人认为在命令行中输入这么多参数已经很烦了，也并没有需求在不同空间之间进行资源操作，于是`QiniuManager`限制了重命名只能在当前空间

![](https://static.hellflame.net/resource/aef205f6251e8e50e42f034193fe8b26)

如果需要支持在不同空间之间进行资源移动的话，在上述代码中将第二个`space`换成目标space就好了，还有能够看到的是，里面中文翻译都是叫的空间，但是英文名却叫"bucket",表示并不清楚这个翻译的来源

![](https://static.hellflame.net/resource/54fbc0df69cbb8df1296f5712ee23c09)

我是不是应该也把这个叫做不规范讷

- `v1.3.0` 新增调试支持

```bash
$ qiniu -dr <filename> <another name>
$ qiniu -dr <filename> <another name> <space name>
```

调试结果的可能返回界面

![响应结果](https://static.hellflame.net/resource/19b48a9635f5ea0502938f6b9bd4cacb)

##### viii.批量导出下载链接及相关操作

```bash
$ qiniu -x # 导出当前空间(bucket)中的所有文件链接
$ qiniu -x <space name> # 导出<space name>空间中的所有文件链接
```

若空间中不存在任何文件的话，导出内容将为空，并且没有提示信息；若空间不存在，则会报错提示不存在该空间

导出链接默认为添加了`1h`时长安全凭证的链接，过期后不影响开放空间的正常访问，私有空间将受影响。输出以文本方式输出到终端，若想要导出到某一文件，请用重定向

```bash
$ qiniu -x > target.txt
$ qiniu -x <space name> > target.txt
```

批量链接将存放在`target.txt`中

若想要批量下载的话，依然可以使用管道方式

`wget`

```bash
# default list
qiniu -x | xargs -n1 wget --content-disposition
    
# target list
qiniu -x <space name> | xargs -n1 wget --content-disposition
```

or `curl`

```bash
# default list
$ qiniu -x | xargs -n1 curl -J -O
    
# target list
$ qiniu -x <space name> | xargs -n1 curl -J -O
    
```

### Issue

#### nodename nor servname provided, or not known

如果测试域名配置如下

![hostname unknown](https://static.hellflame.net/resource/e086339b219f691db1a1052f349deadb)

可能就会报如下错误，因为这个域名无效('7ktpup.com1.z0.glb.clouddn.com')

![hostname not valid](https://static.hellflame.net/resource/748ee73149aa605434221204397b39df)

可能的原因是七牛云没有解析所有的测试域名，处理方法就是在配置域名时，需要将测试域名配置为那个可用的域名,如`qiniu -s whatever whatever.qiniudn.com`(或者在一开始并不用设置测试域名，或者在本机的hosts文件中指定ip)，但是实际上并不知道七牛云的域名如何管理的，所以要知道哪个域名是可用的话，在`内容管理`界面查看外链，就知道至少哪一个域名是可用的了

关注了一段时间，发现这个域名只是偶尔无效(最近无效大概发生在凌晨，这次大概在5点左右？)，难道是服务器夜间维护？还是遭到攻击？还是日志统计需要？好吧，无论如何，这是一个问题，我也只能选择合适的时机使用

#### database is locked

![database lock](https://static.hellflame.net/resource/9869b5ac1d20097cb2e8a78cba81cc5f)

qiniuManager现在同时只能运行一个实例，因为manager从用户家目录下的一个SQLite数据库文件获取密钥，并且在程序开始运行时获取这个数据库，在程序结束时释放，如果某一个时刻正在下载一个大文件，一直占用数据库的话，再运行程序便会报这个错误。不过貌似并没有出现致命错误(对于SQLite我还不是很了解)。要修复这个问题的话，只要及时释放SQLite就好了，不过我并没有这么做，因为和整个程序一开始设计时候的构思并不一样(其实是因为懒)

#### 注入漏洞

项目使用`SQLite3`作为数据库支持，数据库文件位于`~/.qiniu.sql`，并将密钥对明文存储在数据库中，将空间名称存于数据库，这两个数据由于都是用户自己输入其中的，所以除非自己想的话，自己可以给自己的数据库注入，如果使用了特别的语句想要注入的话，应该还是比较简单的，当然我自己是不会自己尝试的

![](https://static.hellflame.net/resource/be76316468bca0bd2cd753cca17c82fe)

### 历史版本

- v0.9.12 

  修复无法上传中文文件名文件的错误

- v0.9.13 

  下载输出优化

- v0.9.14 

  私有空间文件下载

- v0.9.15 

  下载前预判以及输出微调

- v0.9.16 

  消除参数获取失败后的报错方式

- v0.9.17 

  未安装curl下载失败

- v1.1.0  

  基本从底层重写了一遍，尽量直接调用了API链接

- v1.1.1  

  urllib.quote

- v1.1.2  

  取消本地判断mimetype(因为会莫名卡在这里，并且上传这个mimetype的时候会告诉我这是未知的mimetype，所以实际上并没有用),取消上传缓存

- v1.1.3  

  文件列表统计总量

- v1.1.4  

  文件列表排序支持，默认按照上传时间逆序排序，修复单位转换中的小数丢失

- v1.2.0  

  底层http报文处理，适当调整响应缓存大小，提高下载速度等，'chucked'编码暂时不可用

- v1.2.1  

  删除本地保存的空间名支持，显示所有已知空间文件列表并统计大小支持，http报文处理去除chucked编码支持(chucked编码真是恶心)，下载文件预判，防止本地文件被覆盖，判断文件是否存在后再下载；部分显示格式调整

- v1.2.2  

  修复无效空间名时的无响应处理

- v1.2.3  

  进度条显示优化，并且应付七牛云接口不规范的锅出现的问题(。。。。。。这才过了多久，接口就变了，这还是一个对外接口应该有的作为么，，在我看来这并不是一个小事故。我开始猜测七牛云内部是不是还有手动拼接SQL语句这样的行为了，维护这些个接口的人真是不幸)

- v1.2.4

  取消qiniu SDK依赖，从文件导入所需方法(这并不是卸磨杀驴，在引用代码中已经包含原项目LICENSE声明)，本来这部分独立出来是为了兼容py3(调用SDK之后`requests`内部会报错，为了省去麻烦，反正自己也只使用了SDK中生成安全凭证的部分)，但是后来发现py3中对于字符串的处理挺繁琐的，各种bytes, str不通用，底层socket的send参数也变成了`bytes`，越修改越觉得烦，本以为py3能够对于编码以及字符串问题友好一些，但是最终发现各种类型之间转换起来真是心累，于是最终也就没有做py3兼容了。总之，`只要七牛云服务器端的接口不发生变动，整个程序就能正常运行起来`；优化下载时文件名判断，防止由于文件名中包含特殊符号，下载到其他位置去了，如类似`_log/whatever/2016-11-29/whatever.qiniudn.com_part-00000.gz`这样的文件名，下载时将以有效文件名`whatever.qiniudn.com_part-00000.gz`(顺便吐槽一下貌似这个日志文件内容就是Nginx日志的样子......)存储在当前目录，暂不支持下载目录选择(没有合适的地方来选择这个参数)；总列表按照时间分别逆序排序；

  对于我这样懒得在print后面加括号的人来说，py3已经很烦了，如果在我加完括号之后依然各种编码问题的话，我还是直接放弃py3好了，毕竟py3里并没有太多让我期待的新特性，py2最大的编码问题也有解决方案

- v1.2.5

  增加导出默认空间或指定空间内所有文件链接的支持；帮助菜单中引入本`README`文件所在链接；获取文件列表方法支持无进度条配置(暂无终端支持)；progress bar获取终端宽度时的异常重定向

- v1.2.6

  允许下载时指定下载目录，不过会跟很长的指令就是了，虽然一开始并不想添加这个支持的，但是想了想如果放进`cron`里定时执行的话，除非导出下载链接，然后用其他命令下载文件外，直接download的话，系统的默认目录一定不会是操作者想要的，这样的需求作者在某些时候也是需要的，并且这样也会方便一些；帮助菜单显示调整；修复上传文件时七牛的不规范的锅导致的返回报文实体为空的异常

- v1.2.7

  API切换为https接口

  本来以为只是把http换成https辣么简单的事情，后来发现七牛服务器的https证书貌似只有一份，也就是只对应了`qbox.me`，对于文件列表以及操作来说，接口链接直接换成https就好了，但是对于上传接口`up.qiniu.com`，直接换成https会报一个莫名其妙的错误(这是我在一开始写https测试的时候会遇到的错误)

  ![ssl.CertificateError](https://static.hellflame.net/resource/cd85b0deda8a4a4ef6f7a16b7533aa5e)

  然后如果在https连接初始化在server_check的时候将hostname换成`qbox.me`，便也能够正常使用
  很明显`up.qiniu.com`和`up.qbox.me`对应着同一个后台

  后来发现，貌似这个上传接口链接是有另一个接口来获取的，通过这个接口获取到了如下内容

  ```
  {
    "ttl":86400,
    "http":{
        "io":["http://iovip.qbox.me"],
        "up":["http://up.qiniu.com","http://upload.qiniu.com","-H up.qiniu.com http://183.136.139.16"]},
    "https":{
        "io":["https://iovip.qbox.me"],
        "up":["https://up.qbox.me"]
        }
  }
  ```

  所以原来https和http的接口的确有一点不一样的样子

  ![](https://static.hellflame.net/resource/4c5aa93ea010e6a721322e01339b1ba4)

  SDK中将这个json文件默认存在了临时目录，不知道有没有人报了类似的错误，但是直接这样存储的话，可能存在两个文件权限互不开放导致无法读取或者写入的情况，就比如，如果是root用户先创建了`/tmp/.qiniu_pythonsdk_hostscache.json`，普通用户就不能覆盖这个文件了捏，要是root用户不允许其他用户read，那么基本上整个程序又会从这里崩溃了吧，曾经在做终端字符打印的图片缓存的时候就遇到这样的问题(我是怎么想的要用root用户打印字符玩，，，，)。这里更妥善一点的做法是在这个文件名上面跟上用户名或者用户id，这些都是能在py里面获取的吧

  不过在这个项目中我并没有类似的烦恼，因为接口什么的，应该很少变动的，更何况这是接口的域名诶，要是这个都变了，那一定是发生了什么大事了，嗯，一定是酱紫的

- v1.2.8

  提供部分接口的调试信息选项，包括list和check两个方法

  提供这个方法的主要原因还是API接口响应的不够明确，或者是qiniumanager在开发时偷的懒，没有去一一对应http返回码的错误(我也的确没有找到类似的文档信息)

  如果七牛的API接口能在返回的数据中包含错误原因什么的话，我也应该不需要这个显示整个http请求到响应的报文方法，因为很多报错的返回仅仅是http返回码的不同，我也并没有找到相关的说明，于是为了方便跟官方反馈，我把整个http请求到响应都给你看看，总没有话说是我代码写错了吧

  最近发现的问题便是海外请求https的list接口时，会报502错误(bad gateway)，这样的错误的话，一般是nginx后端代理的服务器无法正常响应的结果

  ![bad gateway](https://static.hellflame.net/resource/011d81b67aa49bb7afb139ed41965205)

  同样的接口，如果换成http请求的话，就不会有问题了，这个问题虽然已经跟官方提交过反馈了，但是目前为止，这个问题依然还是存在的样子，虽然并不影响上传功能的样子，不过，都给我报502错误了，怎么能保证不出现其他更严重的问题额

  > 上述问题官方已经修复，只是在发布新版本之前自己的代码都没有做过调试，顾没有更新这个信息

  传统意义上来看的话，500以上的错误都算是严重错误了，虽然七牛的api中还有600+的错误，，好吧，，毕竟不是我的API接口，开发者开心就好

- v1.3.0

  修复了下载失败的HTTP请求，新增下载、重命名调试支持

  好吧，虽然下载问题存在了很久，但是由于自己基本上都只是备份文件，并且保存成功，于是并没有太在意这么大的问题=。=，最终发现就是在发送HTTP报文的结尾被注视掉了一行用来添加`\r\n`的语句。。。。导致服务器一直认为没有接收完报文，于是下载毫无响应，然而在其他方法调用时的报文在处理headers的时候添加了`\r\n`，于是就导致只有下载这个功能出问题了(因为不需要处理任何报文)。

  新增的调试支持其实功能一直都存在，只是一直没有添加进可选的参数中，在这个版本中新增了参数，现在的帮助菜单更长了。

- v1.3.1

  尝试修复python2.7.9以下导致的`AttributeError: 'module' object has no attribute 'SSLContext'` , [错误提示](https://github.com/hellflame/qiniu_manager/issues/1) , 方案来自于 [ssl 'module' object has no attribute 'SSLContext'](https://stackoverflow.com/questions/28228214/ssl-module-object-has-no-attribute-sslcontext)，由于个人没有该版本python，所以就试试看了。

- v1.3.2

  在**等宽字体**环境中，将中文、日文和韩文字符以及全角英文、数字等字符的宽度假定为ASCII字符宽度的两倍(大多数情况下应该都是没问题的)

  ![等宽字体终端中的uft8和ascii](https://static.hellflame.net/resource/6ccfa25ccfd39fb136dab5954e161eae)

- v1.3.3

  旧式类替换为新式类，以免谁多继承出什么问题(谁竟然还在多继承!)

  增加显示宽度，文件详情添加自动查找功能，等宽字体检查，将2倍宽度字体编码左边界增大，右边界不是很清楚=。=

  print from \_\_future\_\_ 

  文件详情更详细了一点点

  