# 部署说明


## 部署代码

```bash
# 部署目录 = DEPLOYDIR

mkdir -p DEPLOYDIR
git clone https://github.com/observerss/ybk DEPLOYDIR
cd DEPLOYDIR
python3 setup.py develop

# 验证安装完毕
ybk --help

# 修改配置文件(也可以直接用命令行参数给)
cp config.yaml.default config.yaml
vim config.yaml
```


## 运行

### Server

直接执行

```bash
ybk serve --production --mongodb_url=mongodb://localhost/ybk --num_processes=4 --port=5100 --secret_key=ybk000
```

或者用supervisor来起这个服务

```bash
# /etc/supervisord.conf
...
```

```bash
sudo apt-get install supervisor
sudo supervisorctl start ybk000
```


Nginx转发

```bash
# /etc/nginx/sites-enabled/ybk000.com

```


### Cronjob


```bash
YBK = `which ybk`
crontab -e

# 每小时执行一次
0 * * * * YBK cron --mongodb_url=mongodb://localhost/ybk
```
