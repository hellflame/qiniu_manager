# qiniu
七牛云本地调用

### 安装
```bash
    $ sudo pip install qiniumanager
```

### 调用方式
```bash
    $ qiniu
    $ qiniu --help
    
    # 使用基本配置
    $ qiniu --access "your access key"
    $ qiniu --secret "your secret key"
    $ qiniu --space "your space name"
    
    # 上传文件
    $ qiniu linux.file
    $ qiniu --upload linux.file
    
    # 文件下载
    $ qiniu --download linux.file
    
    # 私有文件下载
    # 私有文件下载前需要设置该空间默认域名(只需设置一次)
    $ qiniu --subdom 7xiyz1.com1.z0.glb.clouddn.com
    
    $ qiniu --private linux.file
    ...
```

### 说明

    配置文件每个用户保存在家目录一个隐藏文件中
    `$HOME/.qiniuManager/qiniu.conf`
    私有空间请设置`sub domain`

```bash
    $ qiniu --subdom
    $ qiniu --subdom 7xiyz1.com1.z0.glb.clouddn.com
```
    
    私有链接有效时间默认为生成后 `1` 小时
    
    私有文件的处理也提供了未开发的另一个模块，爬虫方法

### 历史版本

+   v0.9.12 修复无法上传中文文件名文件的错误
+   v0.9.13 下载输出优化
+   v0.9.14 私有空间文件下载
+   v0.9.15 下载前预判以及输出微调