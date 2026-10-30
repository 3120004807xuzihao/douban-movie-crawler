import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from collections import Counter

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 读取干净的数据
df = pd.read_csv('douban_movies.csv')

# ================= 数据预处理 =================
# 处理年代字段 (转为 int 备用)
df['年份_int'] = pd.to_numeric(df['年份'], errors='coerce')

# 【解决拥挤】把 1990 年以前的年代合并，或者只保留 Top 年代
df['年代'] = df['年份_int'].apply(lambda x: f"{int(x//10*10)}s" if pd.notna(x) else '未知')
decade_counts = df['年代'].value_counts()
# 把数量小于 10 的合并为“早期经典(90年代前)”
small_decades = decade_counts[decade_counts < 10].index
df['年代合并'] = df['年代'].apply(lambda x: '早期经典' if x in small_decades else x)
decade_pie_counts = df['年代合并'].value_counts()

# 国家数量 Top5 + 其他
country_counts = df['国家'].value_counts()
country_pie = country_counts.head(5).copy()
country_pie['其他'] = country_counts.iloc[5:].sum()

# 导演上榜数量
director_counter = Counter()
for dirs in df['导演'].dropna():
    for d in str(dirs).split('/'):
        if d.strip(): director_counter[d.strip()] += 1
top_directors = director_counter.most_common(10)

# 类型统计 (拆分)
genre_counter = Counter()
for genres in df['类型'].dropna():
    for g in str(genres).split(' '):
        if g.strip(): genre_counter[g.strip()] += 1
top_genres = genre_counter.most_common(10)


# ================= 开始绘制 6 大实战图表 =================
plt.figure(figsize=(18, 11))

# 图1：国家分布饼图
plt.subplot(2, 3, 1)
plt.pie(country_pie.values, labels=country_pie.index, autopct='%1.1f%%', 
        startangle=90, colors=plt.cm.Pastel1.colors, pctdistance=0.75)
plt.title('上榜电影主国家分布', fontsize=14)

# 图2：年代分布饼图（解决了数字拥挤）
plt.subplot(2, 3, 2)
plt.pie(decade_pie_counts.values, labels=decade_pie_counts.index, autopct='%1.1f%%', 
        startangle=90, colors=plt.cm.Set3.colors, pctdistance=0.75)
plt.title('上榜电影年代分布', fontsize=14)

# 图3：导演重复度 Top10
plt.subplot(2, 3, 3)
dir_names = [d[0] for d in top_directors][::-1]
dir_counts = [d[1] for d in top_directors][::-1]
plt.barh(dir_names, dir_counts, color='steelblue')
plt.title('导演上榜作品数量 Top10', fontsize=14)
plt.xlabel('作品数')

# 图4：各年代平均评分对比（替换无意义散点图）
plt.subplot(2, 3, 4)
# 只取数量大于5的年代，避免极个别电影拉偏均值
decade_score = df.groupby('年代')['评分'].agg(['mean', 'count'])
decade_score = decade_score[decade_score['count'] >= 5] 
plt.plot(decade_score.index, decade_score['mean'], marker='o', color='purple', linewidth=2)
plt.title('不同年代的平均评分对比', fontsize=14)
plt.ylabel('平均评分')
plt.xticks(rotation=45)
# 标出具体数值
for i, v in enumerate(decade_score['mean']):
    plt.text(i, v + 0.02, f'{v:.2f}', ha='center', fontsize=10)

# 图5：不同国家平均评分对比（Top 6 国家）
plt.subplot(2, 3, 5)
country_score = df.groupby('国家')['评分'].agg(['mean', 'count'])
country_score = country_score[country_score['count'] >= 10].sort_values('mean', ascending=False).head(6)
plt.bar(country_score.index, country_score['mean'], color='lightcoral', edgecolor='black')
plt.title('上榜数量≥10的国家平均评分', fontsize=14)
plt.ylabel('平均评分')
plt.ylim(8.4, 9.4) # 调整Y轴范围凸显差异
for i, v in enumerate(country_score['mean']):
    plt.text(i, v + 0.02, f'{v:.2f}', ha='center', fontsize=10)

# 图6：不同类型平均评分对比（Top 6 类型）
plt.subplot(2, 3, 6)
# 把包含某个类型的行展开，算每种类型的平均分
type_score_list = []
for idx, row in df.iterrows():
    if pd.notna(row['类型']):
        for g in str(row['类型']).split(' '):
            type_score_list.append({'类型': g, '评分': row['评分']})
df_type = pd.DataFrame(type_score_list)
type_score = df_type.groupby('类型')['评分'].agg(['mean', 'count'])
type_score = type_score[type_score['count'] >= 15].sort_values('mean', ascending=False).head(6)
plt.bar(type_score.index, type_score['mean'], color='mediumseagreen', edgecolor='black')
plt.title('上榜数量≥15的电影类型平均评分', fontsize=14)
plt.ylabel('平均评分')
plt.ylim(8.4, 9.4)
for i, v in enumerate(type_score['mean']):
    plt.text(i, v + 0.02, f'{v:.2f}', ha='center', fontsize=10)

plt.tight_layout()
plt.savefig('douban_analysis_result.png', dpi=300)
print("图表已更新，带有具体数值，请查看 douban_analysis_result.png")
plt.show()