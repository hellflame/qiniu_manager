# qiniu
七牛云本地调用

### 安装
```bash
    $ sudo pip install qiniumanager --upgrade
```

### 七牛云存储 Qiniu Manager

```
Usage:
  qiniu <your file> [space]		选择文件位置上传，指定空间名或使用默认空间名
  qiniu [option] <file name> [space]	对云空间中文件进行操作
  qiniu [--key|-k] <access key> <secret key>	设置密钥

  --version,-v	当前版本号
  --space,-s	修改或查看当前空间名
  --remove,-r	删除云文件
  --private,-p	返回私有文件下载链接
  --download,-d	下载文件
  --check,-c	查看文件状态
  --rename,-n	重命名
  --key,-k	修改或查看access key，secret key
  --link,-i	返回开放云空间文件下载链接
  --list,-l	文件列表
  --help,-h	帮助
  --clean,-e	清除缓存

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

#### 基本操作
i.文件列表
```bash
	qiniu -l # 显示当前空间(bucket)文件列表
	qiniu -l backup # 显示`backup`中的文件列表
```
ii.文件详情
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
> 当然，还是知道空间的开放和私有属性比较好
![private and public](https://static.hellflame.net/resource/b74f36b5f05569fa005952e5a90561da)

v.下载
```bash
	qiniu -d <filename> # 下载当前空间(bucket)中的<filename>
	qiniu -d <filename> <space name> # 下载<space name>空间(bucket)中的<filename>
```

> 下载的文件存储在当前目录，与空间中文件名相同
> 正常的话，应该会显示下载进度条

![progress](https://static.hellflame.net/resource/7dc3b5f8d42a49d2233d152c6779b829)
![finished](https://static.hellflame.net/resource/a51952d5e39ab3c3308fced9ed79db1a)

>不正常的话，进度条可能会不能正常显示，不过如果还好的话，最终文件还是会正常下载完毕
>如果崩溃的话，还是老老实实`wget url -O <filename>`好了


### 历史版本

+   v0.9.12 修复无法上传中文文件名文件的错误
+   v0.9.13 下载输出优化
+   v0.9.14 私有空间文件下载
+   v0.9.15 下载前预判以及输出微调
+   v0.9.16 消除参数获取失败后的报错方式
+   v0.9.17 未安装curl下载失败
+   v1.1.0  基本从底层重写了一遍，尽量直接调用了API链接