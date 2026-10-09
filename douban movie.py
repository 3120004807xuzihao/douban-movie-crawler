# 导入模块
import requests  # 网络请求模块
from lxml import etree # 数据解析模块

# 请求头信息
headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0'
}

# 功能函数，获取列表的第一个元素
def get_first_text(list):
    try:
        return list[0].strip()
    except:
        return ''

# 使用列表生成式获取10个页面的地址
urls=['https://movie.douban.com/top250?start={}&filter='.format(str(i*25)) for i in range(10)]
count=1 # 用来计数
for url in urls:
    res=requests.get(url=url,headers=headers)
    html=etree.HTML(res.text)
    lis=html.xpath('//*[@id="content"]/div/div[1]/ol/li')
    # 解析数据
    for li in lis:
        title=get_first_text(li.xpath('./div/div[2]/div[1]/a/span[1]/text()'))
        src=get_first_text(li.xpath('./div/div[2]/div[1]/a/@href'))
        director=get_first_text(li.xpath('./div/div[2]/div[2]/p[1]/text()'))
        score=get_first_text(li.xpath('./div/div[2]/div[2]/div/span[2]/text()'))
        comment=get_first_text(li.xpath('./div/div[2]/div[2]/div/span[4]/text()'))
        summary=get_first_text(li.xpath('./div/div[2]/div[2]/p[2]/span/text()'))
        print(count,title,src,director,score,comment,summary)
        count+=1