新三板公告抓取
==============

描述
-----
    主要解决从巨潮接入新三板公告余老三板公告数据慢的问题， 实行抓取；抓取的文件形成数据存入mongo， 公告文件上传S3
    
程序运行
--------
    根据计划准备放在122.144.134.3:/opt/scrapyer/announcement_otc下运行
    使用screen命令， 是程序在后台工作， 运行：python run_otc.py
    
备注
------
    目前程序并未部署和运行
