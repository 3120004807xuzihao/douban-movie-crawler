# 导入模块
import requests  # 网络请求模块
from lxml import etree # 数据解析模块
import csv
import time

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

# 用来存储所有数据
all_data=[]

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
        all_data.append([count,title,src,director,score,comment,summary])
        count+=1

    # 每爬一页休息 1 秒，防止请求太快被豆瓣封
    time.sleep(1)

# 把数据写入 CSV 文件，Excel 可以直接打开
with open(r'C:\Users\admin\Desktop\douban-movie-crawler\douban.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['排名', '标题', '链接', '导演/主演/年份/国家/类型', '评分', '评价人数', '简介'])
    writer.writerows(all_data)

print('保存完成，共', len(all_data), '条，文件：douban.csv')
