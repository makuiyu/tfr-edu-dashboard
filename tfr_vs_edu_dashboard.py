import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr, linregress

# 设置中文和负号支持
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False  

# 加载数据
@st.cache_data
def load_data():
    edu_df = pd.read_csv('中等教育女性毛入学率.csv')
    fert_df = pd.read_csv('总和生育率.csv')
    
    edu_long = edu_df.melt(id_vars=['Country Name', 'Country Code'], var_name='Year', value_name='Female Enrollment Rate')
    fert_long = fert_df.melt(id_vars=['Country Name', 'Country Code'], var_name='Year', value_name='TFR')
    
    edu_long['Year'] = edu_long['Year'].astype(int)
    fert_long['Year'] = fert_long['Year'].astype(int)
    
    merged = pd.merge(edu_long, fert_long, on=['Country Code', 'Year'], suffixes=('_edu', '_fert')) 
    
    return merged

data = load_data()

st.title("🌍 中等教育女性毛入学率与总和生育率关系图")

# 构建国家名与代码映射
country_map = data[['Country Name_fert', 'Country Code']].drop_duplicates()
country_name_to_code = dict(zip(country_map['Country Name_fert'], country_map['Country Code']))
country_code_to_name = dict(zip(country_map['Country Code'], country_map['Country Name_fert']))

# 下拉选国家（显示名称，后台用代码）
all_country_names = sorted(country_name_to_code.keys())
selected_country_names = st.multiselect("选择国家/地区（留空=全部）", all_country_names)

if selected_country_names:
    selected_country_codes = [country_name_to_code[name] for name in selected_country_names]
else:
    selected_country_codes = []

# 年份和地区下拉
all_years = sorted(data['Year'].unique())
years = st.multiselect("选择年份（留空=全部）", all_years)

# 数据筛选
filtered = data.copy()
if selected_country_codes:
    filtered = filtered[filtered['Country Code'].isin(selected_country_codes)]
if years:
    filtered = filtered[filtered['Year'].isin(years)]

filtered = filtered.dropna(subset=['Female Enrollment Rate', 'TFR'])

if filtered.empty:
    st.warning("当前筛选条件无数据，请更换条件。")
else:
    # 相关系数
    pearson_corr, pearson_p = pearsonr(filtered['Female Enrollment Rate'], filtered['TFR'])
    spearman_corr, spearman_p = spearmanr(filtered['Female Enrollment Rate'], filtered['TFR'])
    st.write(f"**皮尔森相关系数**: {pearson_corr:.3f} (p={pearson_p:.3e})")
    st.write(f"**斯皮尔曼相关系数**: {spearman_corr:.3f} (p={spearman_p:.3e})")

    # 回归拟合
    slope, intercept, r_value, p_value, std_err = linregress(filtered['Female Enrollment Rate'], filtered['TFR'])
    st.write(f"**回归拟合方程**: TFR = {slope:.3f} × 入学率 + {intercept:.3f} (R² = {r_value**2:.3f})")

    # 图表选择
    chart_type = st.selectbox("选择图形类型", ['散点图', '散点图 + 拟合线', '箱线图', '热力图', '双轴时间序列'])

    if chart_type == '散点图':
        plt.figure(figsize=(8, 6))
        sns.scatterplot(data=filtered, x='Female Enrollment Rate', y='TFR', hue='Year', palette='viridis', alpha=0.7)
        plt.title("散点图")
        st.pyplot(plt.gcf())

    elif chart_type == '散点图 + 拟合线':
        sns.lmplot(data=filtered, x='Female Enrollment Rate', y='TFR', hue='Year', height=6, aspect=1.2, scatter_kws={'alpha':0.7})
        plt.title("散点图 + 拟合线")
        st.pyplot(plt.gcf())

    elif chart_type == '箱线图':
        plt.figure(figsize=(8, 6))
        sns.boxplot(data=filtered, x='Year', y='TFR')
        plt.title("各年份 TFR 箱线图")
        st.pyplot(plt.gcf())

    elif chart_type == '热力图':
        pivot = filtered.pivot_table(index='Country Name_edu', columns='Year', values='TFR', aggfunc='mean')
        plt.figure(figsize=(10, 6))
        sns.heatmap(pivot, cmap='YlGnBu', annot=True, fmt=".1f")
        plt.title("TFR 热力图")
        st.pyplot(plt.gcf())

    elif chart_type == '双轴时间序列':
        if selected_country_codes:
            plt.figure(figsize=(10, 6))
            for code in filtered['Country Code'].unique():
                subset = filtered[filtered['Country Code'] == code]
                ax = subset.plot(x='Year', y='TFR', label=f"{country_code_to_name[code]} TFR", legend=True)
                subset.plot(x='Year', y='Female Enrollment Rate', secondary_y=True, label=f"{country_code_to_name[code]} 入学率", ax=ax, legend=True)
            plt.title("双轴时间序列")
            st.pyplot(plt.gcf())
        else:
            st.info("请至少选择一个国家/地区以显示双轴时间序列")

    # 下载数据
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("下载当前数据 CSV", csv, "统计结果.csv", "text/csv")