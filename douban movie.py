import requests
from lxml import etree
import pandas as pd
import time
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36'
}

def get_first_text(lst):
    try:
        return lst[0].strip()
    except:
        return ''

all_data = []
urls = ['https://movie.douban.com/top250?start={}&filter='.format(str(i*25)) for i in range(10)]

print("开始爬取数据...")
for url in urls:
    res = requests.get(url=url, headers=headers)
    html = etree.HTML(res.text)
    lis = html.xpath('//*[@id="content"]/div/div[1]/ol/li')
    
    for li in lis:
        title = get_first_text(li.xpath('./div/div[2]/div[1]/a/span[1]/text()'))
        src = get_first_text(li.xpath('./div/div[2]/div[1]/a/@href'))
        
        # 抓取完整文本
        director_info_raw = li.xpath('./div/div[2]/div[2]/p[1]//text()')
        director_info = ''.join(director_info_raw).replace('\xa0', ' ').strip()
        
        score = get_first_text(li.xpath('./div/div[2]/div[2]/div/span[2]/text()'))
        comment_num = get_first_text(li.xpath('./div/div[2]/div[2]/div/span[4]/text()'))
        summary = get_first_text(li.xpath('./div/div[2]/div[2]/p[2]/span/text()'))
        
        all_data.append([title, src, director_info, score, comment_num, summary])
    time.sleep(1)

print("爬取完成，开始彻底拆分与清洗...")

df = pd.DataFrame(all_data, columns=['标题', '链接', '原始信息', '评分', '评价人数', '短评'])

# 1. 基础清洗
df['短评'] = df['短评'].fillna('暂无短评')
df['评价人数'] = df['评价人数'].str.replace('人评价', '').astype(int)
df['评分'] = df['评分'].astype(float)

# 2. 核心：全部拆分（用正则暴力提取）
def split_all_info(text):
    # 提取导演
    director_match = re.search(r'导演[:：]\s*(.*?)\s*(?:主演[:：]|$)', text)
    director = director_match.group(1).strip() if director_match else ''
    
    # 提取主演
    actor_match = re.search(r'主演[:：]\s*(.*?)\s*\d{4}', text)
    actor = actor_match.group(1).strip() if actor_match else ''
    
    # 提取年份
    year_match = re.search(r'(19\d{2}|20\d{2})', text)
    year = year_match.group(1) if year_match else ''
    
    # 按斜杠切分，提取国家和类型
    country, genre = '', ''
    parts = [p.strip() for p in text.split('/')]
    for i, p in enumerate(parts):
        if re.search(r'(19\d{2}|20\d{2})', p):
            if i + 1 < len(parts): 
                country = parts[i+1].split()[0] if parts[i+1].split() else '' # 只取第一个国家
            if i + 2 < len(parts): 
                genre = parts[i+2].strip()
            break
            
    return pd.Series([director, actor, year, country, genre])

# 将拆分结果直接应用并生成 5 个新列
df[['导演', '主演', '年份', '国家', '类型']] = df['原始信息'].apply(split_all_info)

# 3. 删除没用的原始信息列，并重新排序
df = df.drop(columns=['原始信息'])
df.insert(0, '排名', range(1, len(df) + 1))
df = df[['排名', '标题', '导演', '主演', '年份', '国家', '类型', '评分', '评价人数', '短评', '链接']]

# 4. 简单明了的文件名
file_name = 'douban_movies.csv'
df.to_csv(file_name, index=False, encoding='utf-8-sig')

print(f"清洗完成！共 {len(df)} 条，已保存为 {file_name}")
