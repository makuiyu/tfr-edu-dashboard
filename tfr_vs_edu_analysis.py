
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文和负号支持
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False   

# 读取数据文件
edu_df = pd.read_csv('中等教育女性毛入学率.csv')
fert_df = pd.read_csv('总和生育率.csv')

# 转成长格式
edu_long = edu_df.melt(id_vars=['Country Name', 'Country Code'], var_name='Year', value_name='Female Enrollment Rate')
fert_long = fert_df.melt(id_vars=['Country Name', 'Country Code'], var_name='Year', value_name='TFR')

# 转换年份
edu_long['Year'] = edu_long['Year'].astype(int)
fert_long['Year'] = fert_long['Year'].astype(int)

# 合并数据
merged_df = pd.merge(edu_long, fert_long, on=['Country Code', 'Year'], suffixes=('_edu', '_fert'))

# 绘图函数
def plot_tfr_vs_edu(data, countries=None, years=None):
    df = data.copy()
    if countries:
        df = df[df['Country Code'].isin(countries)]
    if years:
        df = df[df['Year'].isin(years)]
    df = df.dropna(subset=['Female Enrollment Rate', 'TFR'])
    
    if df.empty:
        print("筛选条件下无有效数据。")
        return
    
    corr = df['Female Enrollment Rate'].corr(df['TFR'])
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Female Enrollment Rate', y='TFR', hue='Year', palette='viridis', alpha=0.7)
    plt.title(f'中等教育女性毛入学率与总和生育率关系 (相关系数: {corr:.2f})')
    plt.xlabel('中等教育女性毛入学率 (%)')
    plt.ylabel('总和生育率 (TFR)')
    plt.legend(title='年份', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
    print(f"相关系数: {corr:.3f}")

# 示例调用：全部数据
# plot_tfr_vs_edu(merged_df)

# 你也可以按需调用，比如：
plot_tfr_vs_edu(merged_df, years=[ x for x in range(2015, 2024) ])
# plot_tfr_vs_edu(merged_df, countries=['CHN'])
