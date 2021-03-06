### QiniuManager历史版本

- v1.4.11

  空间修改问题fix

- v1.4.10

  http库支持chunked编码数据量监控

  进度条刷新间隔至少0.1s

  删除功能支持通配符选择

- v1.4.9
  
  文件状态输出修复

- v1.4.8

  修复http库中post方法在http实体中多添加 `\r\n` 导致的 `Malformed HTTP message`

  修复可能的chunked下载出错问题

  调试信息加入请求发出和获得响应的时间戳

- v1.4.7

  进一步完善测试脚本，继续添加了部分测试用例，后续的开发应该更稳妥了才对

  修复在python3测试中出现的 `unclosed ssl` 警告

  迁移README中的历史版本到这里

- v1.4.6

  bug fix、输出具体上传失败原因

- v1.4.5

  修复下载不存在文件时的报错

  结构优化

  ​更新底层http库，支持chunked编码，添加testcase，测试通过：

  ```bash
  *   Python 3.6.2 (default, Sep  4 2017, 19:45:38)
      [GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)] on darwin
  *   Python 3.5.3 (a37ecfe5f142bc971a86d17305cc5d1d70abec64, Jun 10 2017, 18:23:14)
      [PyPy 5.8.0-beta0 with GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)] on darwin
  *   Python 2.7.14 (default, Sep 25 2017, 20:46:21)
      [GCC 4.2.1 Compatible Apple LLVM 9.0.0 (clang-900.0.37)] on darwin
  ```

  虽然在这个小程序中貌似没有用到过chunked编码，但是作为预防，还是顺便加上了chunked编码支持，因为另一个小项目中考虑从自己的服务器上下载东西，然而自己的静态文件服务器大多数时候都使用分块编码传输数据，所以其实是在另一个项目中开始着手支持的。

  同时，在这次更新中，发现了曾经在py3中出现的下载到99%就一动不动的情况是来源于bytes与str之间的相互转换问题。由于二进制内容并不能编码后转换为字符串，曾经将bytes转换为utf8，忽略了错误，于是放进stringIO之后内容久丢失了，长度也因此变短了，所以进度条就无法到达100%了。曾经用StringIO还是为了偷懒，让StringIO来处理一行一行的数据，现在直接用bytes来记录数据，手动查找换行标志 `\r\n` ，发现也不是很难，就效果而言，反而更简单了。

  剩下的问题就是chunked编码时候的进度条乱跳问题了=。=

  发现七牛的接口又发生了变化，原本不存在的文件会什么都不返回，或者说一个空的http实体，现在返回了一个错误信息，`No such file or directory` 。。。导致需要修改一下check方法，这又是另一个故事了。

- v1.4.4

  进一步降低调用于功能之间的耦合(极大的解耦)

  显示所有空间文件列表的功能换成一次性输出，而非以往的获取一个空间的列表信息就开始输出到终端

  添加搜索功能，使用unix文件匹配模式(通配符)，使用方法如：

  ```bash
  $ qiniu -f *.txt
  $ qiniu -f wha?.tar
  ...
  ```

  关于文件匹配，这里有一个问题:

  ```bash
  $ qiniu -f *
  ```

  正常情况下应该返回所有文件，然而实际情况却是报了一个错误：

  ```bash
  qiniu: error: unrecognized arguments: xxx build dist qiniuManager qiniuManager.egg-info setup.py
  ```

  也就是把当前目录的文件列表给传进去了，应该是终端的默认行为，所以如果出现这样的问题的话，可以用下面的方法：

  ```bash
  $ qiniu -f "*"
  ```

  放进引号里面就好了=.=

  添加文件大小过滤功能，字节为单位，单边范围，未支持范围内过滤

  由于命令行换用argparse，虽然原本的功能都还在，但是总会有一点变化，所以感觉整个使用文档又要重写一遍了=。=虽然argparse用起来方便，但是果然还是没有自己写的命令解析灵活，虽然也可能是很少用argparse的缘故，py2和py3在参数上还有一点区别，真的是，，，

- v1.4.3

  本地存储Key加密支持 (当然，这需要重新添加一次key，原有的key会被删除，数据库中只会保留一份key)，当然，这也只是最简单的加密方式，如果知道使用用户的用户名的话，Key很容易解码出来。__兼容以往版本SQLite数据库__

  更详细的版本输出

  > 部分时候发现一些奇怪的问题，就是下载的时候下载到99%，就卡住了，再也收不到来自服务器的数据，检查了很多次http模块，怀疑了很多次是我在得到recv之后取字符串长度的时候的问题，毕竟py3中bytes和str不一样(但是为什么就偏偏在下载的时候出问题捏，难道跟下载的媒体类型有关？)，嗯，py2貌似倒是没什么问题的样子=。= 后来莫名其妙又没问题了

- v1.4.2

  重传支持、上传失败原因说明(曾经基本依赖超时和JSON异常)、部分颜色调整

  由于上传只是使用了串行方式，内存中只会驻留最多4M文件内容，重传处理也相对简单。之后可能考虑添加并行上传功能，可以预见会发生很多问题=。=

- v1.4.1

  上传修复

- v1.4.0

  添加了Py3支持：不知道是谁说py3的编码问题得到了改善，但是为什么我觉得更难受了呢，一会儿需要bytes一会儿需要str，还有str和bytes的长度不相等什么的，各种decode，encode，还没有在py2下面那样一次性解决的更好的办法，真的是。。。。

  更详细的调试信息输出

  优化了HTTP请求部分

  删除时需要手动确认(还没有添加强制删除选项)。因为有人反馈自己公司的资源被莫名删除了，员工也没有谁承认是自己删除了资源，通过我在http请求的UA信息找到我。如果七牛云一边什么问题都没有的话，或者没有人冒用了我的UA的话，那就应该是有人手残，测试命令删除，工具里也没有进一步提示信息，于是资源就被删除了，而且也没有办法恢复。

  暂时添加了加密模块，但尚未使用，主要原因就是py3里面str和bytes很烦=。=

- v1.3.3

  旧式类替换为新式类，以免谁多继承出什么问题(谁竟然还在多继承!)

  增加显示宽度，文件详情添加自动查找功能，等宽字体检查，将2倍宽度字体编码左边界增大，右边界不是很清楚=。=

  print from \_\_future\_\_

  文件详情更详细了一点点

- v1.3.2

  在**等宽字体**环境中，将中文、日文和韩文字符以及全角英文、数字等字符的宽度假定为ASCII字符宽度的两倍(大多数情况下应该都是没问题的)，测试字体 *Monaco*

  ![等宽字体终端中的uft8和ascii](https://static.hellflame.net/resource/6ccfa25ccfd39fb136dab5954e161eae)

- v1.3.1

  尝试修复python2.7.9以下导致的`AttributeError: 'module' object has no attribute 'SSLContext'` , [错误提示](https://github.com/hellflame/qiniu_manager/issues/1) , 方案来自于 [ssl 'module' object has no attribute 'SSLContext'](https://stackoverflow.com/questions/28228214/ssl-module-object-has-no-attribute-sslcontext)，由于个人没有该版本python，所以就试试看了。

- v1.3.0

  修复了下载失败的HTTP请求，新增下载、重命名调试支持

  好吧，虽然下载问题存在了很久，但是由于自己基本上都只是备份文件，并且保存成功，于是并没有太在意这么大的问题=。=，最终发现就是在发送HTTP报文的结尾被注视掉了一行用来添加`\r\n`的语句。。。。导致服务器一直认为没有接收完报文，于是下载毫无响应，然而在其他方法调用时的报文在处理headers的时候添加了`\r\n`，于是就导致只有下载这个功能出问题了(因为不需要处理任何报文)。

  新增的调试支持其实功能一直都存在，只是一直没有添加进可选的参数中，在这个版本中新增了参数，现在的帮助菜单更长了。

- v1.2.8

  提供部分接口的调试信息选项，包括list和check两个方法

  提供这个方法的主要原因还是API接口响应的不够明确，或者是qiniumanager在开发时偷的懒，没有去一一对应http返回码的错误(我也的确没有找到类似的文档信息)

  如果七牛的API接口能在返回的数据中包含错误原因什么的话，我也应该不需要这个显示整个http请求到响应的报文方法，因为很多报错的返回仅仅是http返回码的不同，我也并没有找到相关的说明，于是为了方便跟官方反馈，我把整个http请求到响应都给你看看，总没有话说是我代码写错了吧

  最近发现的问题便是海外请求https的list接口时，会报502错误(bad gateway)，这样的错误的话，一般是nginx后端代理的服务器无法正常响应的结果

  ![bad gateway](https://static.hellflame.net/resource/011d81b67aa49bb7afb139ed41965205)

  同样的接口，如果换成http请求的话，就不会有问题了，这个问题虽然已经跟官方提交过反馈了，但是目前为止，这个问题依然还是存在的样子，虽然并不影响上传功能的样子，不过，都给我报502错误了，怎么能保证不出现其他更严重的问题额

  > 上述问题官方已经修复，只是在发布新版本之前自己的代码都没有做过调试，顾没有更新这个信息

  传统意义上来看的话，500以上的错误都算是严重错误了，虽然七牛的api中还有600+的错误，，好吧，，毕竟不是我的API接口，开发者开心就好

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

- v1.2.6

  允许下载时指定下载目录，不过会跟很长的指令就是了，虽然一开始并不想添加这个支持的，但是想了想如果放进`cron`里定时执行的话，除非导出下载链接，然后用其他命令下载文件外，直接download的话，系统的默认目录一定不会是操作者想要的，这样的需求作者在某些时候也是需要的，并且这样也会方便一些；帮助菜单显示调整；修复上传文件时七牛的不规范的锅导致的返回报文实体为空的异常

- v1.2.5

  增加导出默认空间或指定空间内所有文件链接的支持；帮助菜单中引入本`README`文件所在链接；获取文件列表方法支持无进度条配置(暂无终端支持)；progress bar获取终端宽度时的异常重定向

- v1.2.4

  取消qiniu SDK依赖，从文件导入所需方法(这并不是卸磨杀驴，在引用代码中已经包含原项目LICENSE声明)，本来这部分独立出来是为了兼容py3(调用SDK之后`requests`内部会报错，为了省去麻烦，反正自己也只使用了SDK中生成安全凭证的部分)，但是后来发现py3中对于字符串的处理挺繁琐的，各种bytes, str不通用，底层socket的send参数也变成了`bytes`，越修改越觉得烦，本以为py3能够对于编码以及字符串问题友好一些，但是最终发现各种类型之间转换起来真是心累，于是最终也就没有做py3兼容了。总之，`只要七牛云服务器端的接口不发生变动，整个程序就能正常运行起来`；优化下载时文件名判断，防止由于文件名中包含特殊符号，下载到其他位置去了，如类似`_log/whatever/2016-11-29/whatever.qiniudn.com_part-00000.gz`这样的文件名，下载时将以有效文件名`whatever.qiniudn.com_part-00000.gz`(顺便吐槽一下貌似这个日志文件内容就是Nginx日志的样子......)存储在当前目录，暂不支持下载目录选择(没有合适的地方来选择这个参数)；总列表按照时间分别逆序排序；

  对于我这样懒得在print后面加括号的人来说，py3已经很烦了，如果在我加完括号之后依然各种编码问题的话，我还是直接放弃py3好了，毕竟py3里并没有太多让我期待的新特性，py2最大的编码问题也有解决方案

- v1.2.3

  进度条显示优化，并且应付七牛云接口不规范的锅出现的问题(。。。。。。这才过了多久，接口就变了，这还是一个对外接口应该有的作为么，，在我看来这并不是一个小事故。我开始猜测七牛云内部是不是还有手动拼接SQL语句这样的行为了，维护这些个接口的人真是不幸)

- v1.2.2

  修复无效空间名时的无响应处理

- v1.2.1

  删除本地保存的空间名支持，显示所有已知空间文件列表并统计大小支持，http报文处理去除chucked编码支持(chucked编码真是恶心)，下载文件预判，防止本地文件被覆盖，判断文件是否存在后再下载；部分显示格式调整


- v1.2.0

  底层http报文处理，适当调整响应缓存大小，提高下载速度等，'chucked'编码暂时不可用

- v1.1.4

  文件列表排序支持，默认按照上传时间逆序排序，修复单位转换中的小数丢失

- v1.1.3

  文件列表统计总量

- v1.1.2

  取消本地判断mimetype(因为会莫名卡在这里，并且上传这个mimetype的时候会告诉我这是未知的mimetype，所以实际上并没有用),取消上传缓存

- v1.1.1

  urllib.quote

- v1.1.0

  基本从底层重写了一遍，尽量直接调用了API链接

- v0.9.17

  未安装curl下载失败

- v0.9.16

  消除参数获取失败后的报错方式

- v0.9.15

  下载前预判以及输出微调

- v0.9.14

  私有空间文件下载

- v0.9.13

  下载输出优化

- v0.9.12

  修复无法上传中文文件名文件的错误
