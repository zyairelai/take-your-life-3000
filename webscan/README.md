# c.webscan.cc

## Requirements
```
python3 -m pip install -r requirements.txt

fake_headers==1.0.2
hurry==1.1
hurry.filesize==0.9
requests==2.31.0
```

## One shot install
```
wget https://raw.githubusercontent.com/zyairelai/take-your-life-3000/main/webscan/ihoneyBakFileScan_Modify.py
wget https://raw.githubusercontent.com/zyairelai/take-your-life-3000/main/webscan/webscan.py
wget https://raw.githubusercontent.com/zyairelai/take-your-life-3000/main/webscan/webscan_admin.py
sleep(1)
chmod a+x ihoneyBakFileScan_Modify.py && sudo mv ihoneyBakFileScan_Modify.py /usr/bin/ihoneyBakFileScan
chmod a+x webscan.py && sudo mv webscan.py /usr/bin/webscan
chmod a+x webscan_admin.py && sudo mv webscan_admin.py /usr/bin/webscan_admin
```

## ihoneyBakFileScan Usage
```
ihoneyBakFileScan -f <domain-list.txt> -o <output-result.txt>
```
```
参数：
    -h --help           查看工具使用帮助
    -f --url-file       批量时指定存放url的文件,每行url需要指定http://或者https://，否则默认使用http://
    -t --thread         指定线程数，建议100
    -u --url            单个url扫描时指定url
    -d --dict-file      自定义扫描字典
    -o --output-file    结果写入的文件名
    -p --proxy          代理服务，例：socks5://127.0.0.1:1080
使用:
    批量url扫描    python3 ihoneyBakFileScan_Modify.py -t 100 -f url.txt -o result.txt
    单个url扫描    python3 ihoneyBakFileScan_Modify.py -u https://www.baidu.com/ -o result.txt
                  python3 ihoneyBakFileScan_Modify.py -u www.baidu.com -o result.txt
                  python3 ihoneyBakFileScan_Modify.py -u www.baidu.com -d dict.txt -o result.txt
```
