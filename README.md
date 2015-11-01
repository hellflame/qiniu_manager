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
    $ qiniu --access "your access key"
    $ qiniu --secret "your secret key"
    $ qiniu --space "your space name"
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

### 历史版本

+    v0.9.12 修复无法上传中文文件名文件的错误
+    v0.9.13 下载输出优化
+    v0.9.14 私有空间文件下载