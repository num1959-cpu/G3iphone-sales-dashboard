import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# กำหนดหน้าจอเป็นแบบ Wide และตั้งชื่อ Page
st.set_page_config(page_title="iPhone Sales Dashboard", layout="wide")

# สร้าง Apple Theme ด้วย CSS CSS สำหรับแต่งหน้าเว็บให้เรียบหรูสไตล์ Apple
apple_theme_css = """
<style>
    /* ใช้ฟอนต์ตระกูล Apple (San Francisco) */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        background-color: #FBFBFD !important; /* สีเทาอ่อนมากๆ แบบเว็บ Apple */
        color: #1D1D1F !important;
    }
    
    /* ปรับปุ่มให้ดูเรียบหรู */
    .stButton>button {
        background-color: #0071E3;
        color: white;
        border-radius: 980px;
        border: none;
        padding: 8px 16px;
        font-weight: 400;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #0077ED;
        transform: scale(1.02);
    }
    
    /* ปรับแต่งส่วนหัว (Headers) */
    h1, h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.015em;
    }
    
    /* ซ่อน Hamburger menu และ Footer ของ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* แปลงหน้าตาของ Tabs ให้กลายเป็นปุ่ม (Segmented Controls แบบ iOS) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #F2F2F7;
        padding: 6px;
        border-radius: 12px;
        border: none;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 8px;
        padding: 0px 20px;
        background-color: transparent;
        border: none;
        color: #8E8E93;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #E5E5EA;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.08) !important;
        color: #0071E3 !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
</style>
"""
st.markdown(apple_theme_css, unsafe_allow_html=True)


@st.cache_data
def load_data():
    file_path = '/Users/somyotmekpha/Desktop/G3Sep/G3Sep.xlsx'
    
    sales = pd.read_excel(file_path, sheet_name='ยอดขาย')
    deposit = pd.read_excel(file_path, sheet_name='มัดจำ')
    zone = pd.read_excel(file_path, sheet_name='zone')
    
    sales['Branch (ID)'] = sales['Branch (ID)'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    deposit['Branch (ID)'] = deposit['Branch (ID)'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    zone['ID'] = zone['ID'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    
    df = pd.merge(sales, zone[['ID', 'RM', 'AM']], left_on='Branch (ID)', right_on='ID', how='left')
    dep_df = pd.merge(deposit, zone[['ID', 'RM', 'AM']], left_on='Branch (ID)', right_on='ID', how='left')
    
    for d in [df, dep_df]:
        d['RM'] = d['RM'].fillna('Unspecified').astype(str)
        d['AM'] = d['AM'].fillna('Unspecified').astype(str)
        d['Branch (Name)'] = d['Branch (Name)'].fillna('Unspecified').astype(str)
    
    def parse_date(d):
        try:
            parts = str(d).split(' ')
            if len(parts) >= 2:
                date_part = parts[1]
                d_m_y = date_part.split('/')
                if len(d_m_y) == 3:
                    return int(d_m_y[0]), int(d_m_y[2])
        except:
            pass
        return None, None

    for d in [df, dep_df]:
        parsed = d['Doc Date'].apply(parse_date)
        d['Day'] = parsed.apply(lambda x: x[0] if x else None)
        d['Year'] = parsed.apply(lambda x: x[1] if x else None)
    
    df = df[df['Year'].isin([2568, 2569])]
    dep_df = dep_df[dep_df['Year'].isin([2568, 2569])]
    
    df['Number'] = pd.to_numeric(df['Number'], errors='coerce').fillna(0)
    df['ราคาขายตามบิล'] = pd.to_numeric(df['ราคาขายตามบิล'], errors='coerce').fillna(0)
    
    dep_df['Number'] = pd.to_numeric(dep_df['Number'], errors='coerce').fillna(0)
    dep_df['ราคารวมทั้งสิ้น'] = pd.to_numeric(dep_df['ราคารวมทั้งสิ้น'], errors='coerce').fillna(0)
    
    return df, dep_df

with st.spinner("Loading data..."):
    df, dep_df = load_data()

st.title(" iPhone Sales Dashboard (Sep Last Year vs This Year)")

# Sidebar Filters
st.sidebar.header("Filters")

metric_choice = st.sidebar.radio("Select Metric", ["Sales Amount", "Quantity"])
if metric_choice == "Sales Amount":
    metric_col = "ราคาขายตามบิล"
    dep_metric_col = "ราคารวมทั้งสิ้น"
else:
    metric_col = "Number"
    dep_metric_col = "Number"

rm_list = sorted(df['RM'].unique().tolist())
rm_list.insert(0, "All")
selected_rm = st.sidebar.selectbox("Select RM (Regional Manager)", rm_list)

if selected_rm != "All":
    am_list = sorted(df[df['RM'] == selected_rm]['AM'].unique().tolist())
else:
    am_list = sorted(df['AM'].unique().tolist())
am_list.insert(0, "All")
selected_am = st.sidebar.selectbox("Select AM (Area Manager)", am_list)

branch_df = df.copy()
if selected_rm != "All":
    branch_df = branch_df[branch_df['RM'] == selected_rm]
if selected_am != "All":
    branch_df = branch_df[branch_df['AM'] == selected_am]
    
branch_list = sorted(branch_df['Branch (Name)'].unique().tolist())
branch_list.insert(0, "All")
selected_branch = st.sidebar.selectbox("Select Branch", branch_list)

filtered_df = df.copy()
filtered_dep_df = dep_df.copy()

if selected_rm != "All":
    filtered_df = filtered_df[filtered_df['RM'] == selected_rm]
    filtered_dep_df = filtered_dep_df[filtered_dep_df['RM'] == selected_rm]
if selected_am != "All":
    filtered_df = filtered_df[filtered_df['AM'] == selected_am]
    filtered_dep_df = filtered_dep_df[filtered_dep_df['AM'] == selected_am]
if selected_branch != "All":
    filtered_df = filtered_df[filtered_df['Branch (Name)'] == selected_branch]
    filtered_dep_df = filtered_dep_df[filtered_dep_df['Branch (Name)'] == selected_branch]

# Sales Aggregation
agg_df = filtered_df.groupby(['Year', 'Day'])[metric_col].sum().reset_index()
pivot_df = agg_df.pivot(index='Day', columns='Year', values=metric_col).fillna(0)

# Deposit Aggregation
agg_dep_df = filtered_dep_df.groupby(['Year', 'Day'])[dep_metric_col].sum().reset_index()
pivot_dep_df = agg_dep_df.pivot(index='Day', columns='Year', values=dep_metric_col).fillna(0)

all_days = pd.DataFrame(index=range(1, 32))
pivot_df = all_days.join(pivot_df, how='left').fillna(0)
pivot_df.index.name = 'Day'

pivot_dep_df = all_days.join(pivot_dep_df, how='left').fillna(0)
pivot_dep_df.index.name = 'Day'


col_last_year = 'Sep Last Year'
col_this_year = 'Sep This Year'

if 2568 in pivot_df.columns:
    pivot_df.rename(columns={2568: col_last_year}, inplace=True)
if 2569 in pivot_df.columns:
    pivot_df.rename(columns={2569: col_this_year}, inplace=True)

if 2568 in pivot_dep_df.columns:
    pivot_dep_df.rename(columns={2568: col_last_year}, inplace=True)
if 2569 in pivot_dep_df.columns:
    pivot_dep_df.rename(columns={2569: col_this_year}, inplace=True)


if metric_choice == "Quantity":
    format_str = "{:,.0f}"
    val_format = "{:,.0f}"
else:
    format_str = "{:,.0f}"
    val_format = "{:,.0f}"

latest_day = 0
if 2569 in agg_df['Year'].values:
    latest_day = int(agg_df[agg_df['Year'] == 2569]['Day'].max())
if pd.isna(latest_day) or latest_day == 0:
    latest_day = 30
    
total_this_year = pivot_df[col_this_year].sum() if col_this_year in pivot_df.columns else 0
mtd_last_year = pivot_df.loc[1:latest_day, col_last_year].sum() if col_last_year in pivot_df.columns else 0
total_last_year = pivot_df[col_last_year].sum() if col_last_year in pivot_df.columns else 0

diff_mtd = total_this_year - mtd_last_year
diff_pct_mtd = (diff_mtd / mtd_last_year * 100) if mtd_last_year > 0 else 0

forecast_this_year = (total_this_year / latest_day) * 30 if latest_day > 0 else 0
forecast_pct = ((forecast_this_year - total_last_year) / total_last_year * 100) if total_last_year > 0 else 0

def create_chart(df_pivot):
    texts_last = []
    texts_this = []

    for i in range(len(df_pivot)):
        v_this = df_pivot[col_this_year].iloc[i] if col_this_year in df_pivot.columns else 0
        t_this = val_format.format(v_this) if v_this != 0 else ''
        if t_this and i % 2 == 1:
            t_this = t_this + '<br><br>'
        texts_this.append(t_this)
        
        v_last = df_pivot[col_last_year].iloc[i] if col_last_year in df_pivot.columns else 0
        t_last = val_format.format(v_last) if v_last != 0 else ''
        if t_last and i % 2 == 1:
            t_last = '<br><br>' + t_last
        texts_last.append(t_last)

    fig = go.Figure()

    if col_last_year in df_pivot.columns:
        fig.add_trace(go.Scatter(
            x=df_pivot.index, 
            y=df_pivot[col_last_year], 
            mode='lines+text+markers',
            name=col_last_year,
            line=dict(color='#8E8E93', width=2),
            marker=dict(size=6, color='#8E8E93'),
            text=texts_last,
            textposition="bottom center",
            textfont=dict(size=10, color='#8E8E93')
        ))

    if col_this_year in df_pivot.columns:
        fig.add_trace(go.Scatter(
            x=df_pivot.index, 
            y=df_pivot[col_this_year], 
            mode='lines+text+markers',
            name=col_this_year,
            line=dict(color='#1D8348', width=3),
            marker=dict(size=8, color='#1D8348'),
            text=texts_this,
            textposition="top center", 
            textfont=dict(size=10, color='#1D8348', weight='bold')
        ))

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"),
        xaxis=dict(title='Day', tickmode='linear', tick0=1, dtick=1, showgrid=True, gridcolor='#F2F2F7', zeroline=False),
        yaxis=dict(title=metric_choice, showgrid=True, gridcolor='#F2F2F7', zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(255,255,255,0.8)'),
        margin=dict(l=20, r=20, t=20, b=20),
        hovermode='x unified'
    )
    return fig

# สร้าง Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Daily Overview", "Ranking", "Deposit Overview", "Deposit Ranking"])

with tab1:
    st.subheader(f"Daily {metric_choice} Comparison")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(f"This Year (MTD 1-{latest_day})", format_str.format(total_this_year))
    col2.metric(f"Last Year (MTD 1-{latest_day})", format_str.format(mtd_last_year))
    col3.metric("MTD Growth", format_str.format(diff_mtd), f"{diff_pct_mtd:.1f}%")
    col4.metric("Total Sep Last Year", format_str.format(total_last_year))
    col5.metric("Forecast Sep This Year", format_str.format(forecast_this_year), f"{forecast_pct:.1f}%")

    fig_sales = create_chart(pivot_df)
    st.plotly_chart(fig_sales, use_container_width=True)

    st.write("---")
    st.subheader("Daily Data Table")
    display_df = pivot_df.copy()

    for col in display_df.columns:
        display_df[col] = display_df[col].apply(lambda x: format_str.format(x))

    st.dataframe(display_df, use_container_width=True)

with tab2:
    st.subheader(f"MTD {metric_choice} Ranking (This Year)")
    
    # Filter data for MTD comparison
    df_mtd = filtered_df[filtered_df['Day'] <= latest_day]
    df_2569 = df_mtd[df_mtd['Year'] == 2569]
    df_2568 = df_mtd[df_mtd['Year'] == 2568]
    
    if df_2569.empty and df_2568.empty:
        st.info("No data available for the selected filters.")
    else:
        def get_rank_df(group_col):
            # Sum for this year
            d_this = df_2569.groupby(group_col)[metric_col].sum().reset_index().rename(columns={metric_col: 'This Year'})
            # Sum for last year
            d_last = df_2568.groupby(group_col)[metric_col].sum().reset_index().rename(columns={metric_col: 'Last Year'})
            
            # Merge both years
            d = pd.merge(d_this, d_last, on=group_col, how='outer').fillna(0)
            
            # ตัด 'Unspecified' ออก
            d = d[d[group_col] != 'Unspecified']
            
            # Sort by this year descending
            d = d.sort_values(by='This Year', ascending=False).reset_index(drop=True)
            d.index = d.index + 1 # Start rank from 1
            d = d.reset_index().rename(columns={'index': 'Rank'})
            
            # Calculate Growth
            d['% Growth'] = np.where(d['Last Year'] > 0, ((d['This Year'] - d['Last Year']) / d['Last Year'] * 100), 0.0)
            
            # Formatting
            d['This Year'] = d['This Year'].apply(lambda x: format_str.format(x))
            d['Last Year'] = d['Last Year'].apply(lambda x: format_str.format(x))
            d['% Growth'] = d['% Growth'].apply(lambda x: f"{x:+.1f}%")
            
            return d

        rank_rm = get_rank_df('RM')
        rank_am = get_rank_df('AM')
        rank_branch = get_rank_df('Branch (Name)')
        
        st.markdown("**RM Ranking**")
        st.dataframe(rank_rm, hide_index=True, use_container_width=True, height=(len(rank_rm) + 1) * 36)
        
        st.write("---")
        
        st.markdown("**AM Ranking (All)**")
        st.dataframe(rank_am, hide_index=True, use_container_width=True, height=(len(rank_am) + 1) * 36)
        
        st.write("---")
        
        st.markdown("**Branch Ranking (All)**")
        st.dataframe(rank_branch, hide_index=True, use_container_width=True, height=600)

with tab3:
    st.subheader(f"Daily Deposit ({metric_choice}) Comparison")
    
    dep_total_this_year = pivot_dep_df[col_this_year].sum() if col_this_year in pivot_dep_df.columns else 0
    dep_mtd_last_year = pivot_dep_df.loc[1:latest_day, col_last_year].sum() if col_last_year in pivot_dep_df.columns else 0
    dep_total_last_year = pivot_dep_df[col_last_year].sum() if col_last_year in pivot_dep_df.columns else 0

    dep_diff_mtd = dep_total_this_year - dep_mtd_last_year
    dep_diff_pct_mtd = (dep_diff_mtd / dep_mtd_last_year * 100) if dep_mtd_last_year > 0 else 0

    dep_forecast_this_year = (dep_total_this_year / latest_day) * 30 if latest_day > 0 else 0
    dep_forecast_pct = ((dep_forecast_this_year - dep_total_last_year) / dep_total_last_year * 100) if dep_total_last_year > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(f"This Year (MTD 1-{latest_day})", format_str.format(dep_total_this_year))
    c2.metric(f"Last Year (MTD 1-{latest_day})", format_str.format(dep_mtd_last_year))
    c3.metric("MTD Growth", format_str.format(dep_diff_mtd), f"{dep_diff_pct_mtd:.1f}%")
    c4.metric("Total Sep Last Year", format_str.format(dep_total_last_year))
    c5.metric("Forecast Sep This Year", format_str.format(dep_forecast_this_year), f"{dep_forecast_pct:.1f}%")

    fig_dep = create_chart(pivot_dep_df)
    st.plotly_chart(fig_dep, use_container_width=True)

    st.write("---")
    st.subheader("Daily Deposit Table")
    display_dep_df = pivot_dep_df.copy()

    for col in display_dep_df.columns:
        display_dep_df[col] = display_dep_df[col].apply(lambda x: format_str.format(x))

    st.dataframe(display_dep_df, use_container_width=True)

with tab4:
    st.subheader(f"MTD Deposit ({metric_choice}) Ranking")
    
    # Filter data for MTD comparison
    dep_df_mtd = filtered_dep_df[filtered_dep_df['Day'] <= latest_day]
    dep_df_2569 = dep_df_mtd[dep_df_mtd['Year'] == 2569]
    dep_df_2568 = dep_df_mtd[dep_df_mtd['Year'] == 2568]
    
    if dep_df_2569.empty and dep_df_2568.empty:
        st.info("No data available for the selected filters.")
    else:
        def get_dep_rank_df(group_col):
            # Sum for this year
            d_this = dep_df_2569.groupby(group_col)[dep_metric_col].sum().reset_index().rename(columns={dep_metric_col: 'This Year'})
            # Sum for last year
            d_last = dep_df_2568.groupby(group_col)[dep_metric_col].sum().reset_index().rename(columns={dep_metric_col: 'Last Year'})
            
            # Merge both years
            d = pd.merge(d_this, d_last, on=group_col, how='outer').fillna(0)
            
            # ตัด 'Unspecified' ออก
            d = d[d[group_col] != 'Unspecified']
            
            # Sort by this year descending
            d = d.sort_values(by='This Year', ascending=False).reset_index(drop=True)
            d.index = d.index + 1 # Start rank from 1
            d = d.reset_index().rename(columns={'index': 'Rank'})
            
            # Calculate Growth
            d['% Growth'] = np.where(d['Last Year'] > 0, ((d['This Year'] - d['Last Year']) / d['Last Year'] * 100), 0.0)
            
            # Formatting
            d['This Year'] = d['This Year'].apply(lambda x: format_str.format(x))
            d['Last Year'] = d['Last Year'].apply(lambda x: format_str.format(x))
            d['% Growth'] = d['% Growth'].apply(lambda x: f"{x:+.1f}%")
            
            return d

        rank_dep_rm = get_dep_rank_df('RM')
        rank_dep_am = get_dep_rank_df('AM')
        rank_dep_branch = get_dep_rank_df('Branch (Name)')
        
        st.markdown("**RM Ranking**")
        st.dataframe(rank_dep_rm, hide_index=True, use_container_width=True, height=(len(rank_dep_rm) + 1) * 36)
        
        st.write("---")
        
        st.markdown("**AM Ranking (All)**")
        st.dataframe(rank_dep_am, hide_index=True, use_container_width=True, height=(len(rank_dep_am) + 1) * 36)
        
        st.write("---")
        
        st.markdown("**Branch Ranking (All)**")
        st.dataframe(rank_dep_branch, hide_index=True, use_container_width=True, height=600)
