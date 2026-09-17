import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter


# =====================================================
# 기본 설정
# =====================================================

st.set_page_config(
    page_title='박준형 첫번째 데이터 분석 프로젝트',
    layout='wide'
)

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# 그래프 색상
deep_green = '#0B5D3B'
green = '#28734F'
light_green = '#5D9271'
soft_green = '#91B59E'


# =====================================================
# 데이터 불러오기
# =====================================================

# main.py가 있는 폴더 기준으로 경로 설정
BASE_DIR = Path(__file__).resolve().parent

csv_path = (
    BASE_DIR
    / 'data'
    / 'raw'
    / 'national_ghg_inventory.csv'
)

df = pd.read_csv(
    csv_path,
    encoding='utf-8-sig',
    keep_default_na=False
)


# =====================================================
# Wide → Long 변환
# =====================================================

long_df = df.melt(
    id_vars='분야 및 연도',
    var_name='연도',
    value_name='배출량_원본'
)


# NO, NA, IE, NE, C 등 숫자가 아닌 값은 NaN 처리
long_df['배출량'] = pd.to_numeric(
    long_df['배출량_원본'],
    errors='coerce'
)


# =====================================================
# 값 가져오기
# =====================================================

def get_value(category, year):

    result = long_df[
        (long_df['분야 및 연도'] == category) &
        (long_df['연도'] == str(year))
    ]['배출량']

    if result.empty:
        return None

    return result.iloc[0]


# =====================================================
# 국가 총배출량
# =====================================================

total_trend = long_df[
    long_df['분야 및 연도']
    == '총배출량(kt CO2-eq)'
].copy()


total_trend['연도_num'] = pd.to_numeric(
    total_trend['연도']
)


total_trend = total_trend.sort_values(
    '연도_num'
)


# 최고 배출량 연도
peak_index = total_trend['배출량'].idxmax()

peak_year = int(
    total_trend.loc[
        peak_index,
        '연도_num'
    ]
)

peak_value = total_trend.loc[
    peak_index,
    '배출량'
]


# 2023년 총배출량
national_2023 = get_value(
    '총배출량(kt CO2-eq)',
    2023
)


# =====================================================
# 분석 분야
# =====================================================

category_map = {
    '에너지':
        '에너지',

    '에너지산업':
        'A 연료연소_1 에너지산업',

    '제조업 및 건설업':
        'A 연료연소_2 제조업 및 건설업_2 제조업 및 건설업',

    '수송':
        'A 연료연소_3 수송'
}


# =====================================================
# 제목
# =====================================================

st.title('박준형 첫번째 데이터 분석 프로젝트')

st.subheader('국가 온실가스 배출구조 분석')

st.caption('1990~2023 국가 온실가스 인벤토리')


# =====================================================
# 사이드바
# =====================================================

with st.sidebar:

    st.header('메뉴')

    menu = st.radio(
        '분석 항목',
        [
            '개요',
            '분야별 분석',
            '데이터 확인'
        ]
    )

    if menu == '분야별 분석':

        selected_label = st.selectbox(
            '분야',
            list(category_map.keys())
        )


# =====================================================
# 개요
# =====================================================

if menu == '개요':

    st.divider()

    # -------------------------------------------------
    # 2023년 배출 현황
    # -------------------------------------------------

    st.subheader('2023년 배출 현황')


    energy_2023 = get_value(
        '에너지',
        2023
    )


    energy_share = (
        energy_2023
        / national_2023
    ) * 100


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            '총배출량',
            f'{national_2023:,.0f}'
        )


    with col2:

        st.metric(
            '에너지 배출량',
            f'{energy_2023:,.0f}'
        )


    with col3:

        st.metric(
            '에너지 비중',
            f'{energy_share:.1f}%'
        )


    st.caption('단위: kt CO₂-eq')


    st.divider()


    # -------------------------------------------------
    # 국가 총배출량 변화
    # -------------------------------------------------

    st.subheader('국가 총배출량 변화')


    fig, ax = plt.subplots(
        figsize=(11, 5)
    )


    ax.plot(
        total_trend['연도_num'],
        total_trend['배출량'],
        color=deep_green,
        linewidth=2.5,
        marker='o',
        markersize=4
    )


    # 최고점
    ax.scatter(
        peak_year,
        peak_value,
        color=green,
        s=90,
        zorder=5
    )


    ax.annotate(
        f'{peak_year}년\n{peak_value:,.0f}',
        xy=(
            peak_year,
            peak_value
        ),
        xytext=(
            peak_year - 7,
            peak_value + 35000
        ),
        arrowprops={
            'arrowstyle': '->',
            'color': deep_green
        }
    )


    # 2023년
    ax.scatter(
        2023,
        national_2023,
        color=light_green,
        s=90,
        zorder=5
    )


    ax.annotate(
        f'2023년\n{national_2023:,.0f}',
        xy=(
            2023,
            national_2023
        ),
        xytext=(
            2016,
            national_2023 - 70000
        ),
        arrowprops={
            'arrowstyle': '->',
            'color': deep_green
        }
    )


    ax.set_xlabel('연도')

    ax.set_ylabel(
        '배출량 (kt CO₂-eq)'
    )


    ax.set_xticks(
        range(1990, 2024, 5)
    )


    ax.yaxis.set_major_formatter(
        StrMethodFormatter(
            '{x:,.0f}'
        )
    )


    ax.grid(
        True,
        alpha=0.2
    )


    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


    # -------------------------------------------------
    # 최고점 이후 변화
    # -------------------------------------------------

    decrease_amount = (
        peak_value
        - national_2023
    )


    decrease_rate = (
        decrease_amount
        / peak_value
    ) * 100


    st.subheader(
        f'{peak_year}년 이후 변화'
    )


    change1, change2, change3 = st.columns(3)


    with change1:

        st.metric(
            f'{peak_year}년 배출량',
            f'{peak_value:,.0f}'
        )


    with change2:

        st.metric(
            '감소량',
            f'{decrease_amount:,.0f}'
        )


    with change3:

        st.metric(
            '감소율',
            f'{decrease_rate:.1f}%'
        )


    st.caption('단위: kt CO₂-eq')


    with st.expander('감소율 계산'):

        st.write(
            '감소율 = '
            '(최고점 배출량 - 2023년 배출량) '
            '÷ 최고점 배출량 × 100'
        )

        st.write(
            f'({peak_value:,.2f} - '
            f'{national_2023:,.2f}) '
            f'÷ {peak_value:,.2f} × 100 '
            f'= {decrease_rate:.1f}%'
        )


    st.divider()


    # -------------------------------------------------
    # 감소 기여도
    # -------------------------------------------------

    st.subheader('감소 기여도')


    # 에너지
    energy_peak = get_value(
        '에너지',
        peak_year
    )


    energy_decrease = (
        energy_peak
        - energy_2023
    )


    energy_contribution = (
        energy_decrease
        / decrease_amount
    ) * 100


    # 에너지산업
    energy_industry_peak = get_value(
        'A 연료연소_1 에너지산업',
        peak_year
    )


    energy_industry_2023 = get_value(
        'A 연료연소_1 에너지산업',
        2023
    )


    energy_industry_decrease = (
        energy_industry_peak
        - energy_industry_2023
    )


    energy_industry_contribution = (
        energy_industry_decrease
        / energy_decrease
    ) * 100


    # 공공 전기 및 열 생산
    power_peak = get_value(
        'A 연료연소_a 공공 전기 및 열 생산',
        peak_year
    )


    power_2023 = get_value(
        'A 연료연소_a 공공 전기 및 열 생산',
        2023
    )


    power_decrease = (
        power_peak
        - power_2023
    )


    power_contribution = (
        power_decrease
        / energy_industry_decrease
    ) * 100


    con1, con2, con3 = st.columns(3)


    with con1:

        st.metric(
            '에너지',
            f'{energy_contribution:.1f}%'
        )


    with con2:

        st.metric(
            '에너지산업',
            f'{energy_industry_contribution:.1f}%'
        )


    with con3:

        st.metric(
            '공공 전기·열 생산',
            f'{power_contribution:.1f}%'
        )


    # -------------------------------------------------
    # 감소 기여도 표
    # -------------------------------------------------

    summary_df = pd.DataFrame({

        '구분': [
            '국가 전체 → 에너지',
            '에너지 → 에너지산업',
            '에너지산업 → 공공 전기 및 열 생산'
        ],

        '상위 감소량': [
            decrease_amount,
            energy_decrease,
            energy_industry_decrease
        ],

        '해당 분야 감소량': [
            energy_decrease,
            energy_industry_decrease,
            power_decrease
        ],

        '기여도(%)': [
            energy_contribution,
            energy_industry_contribution,
            power_contribution
        ]
    })


    st.dataframe(
        summary_df,
        hide_index=True,
        use_container_width=True,

        column_config={

            '상위 감소량':
                st.column_config.NumberColumn(
                    '상위 감소량',
                    format='%.2f'
                ),

            '해당 분야 감소량':
                st.column_config.NumberColumn(
                    '해당 분야 감소량',
                    format='%.2f'
                ),

            '기여도(%)':
                st.column_config.NumberColumn(
                    '기여도 (%)',
                    format='%.2f'
                )
        }
    )


    with st.expander('기여도 계산'):

        st.write(
            '에너지'
        )

        st.write(
            f'{energy_decrease:,.2f} '
            f'÷ {decrease_amount:,.2f} '
            f'× 100 '
            f'= {energy_contribution:.2f}%'
        )


        st.write(
            '에너지산업'
        )

        st.write(
            f'{energy_industry_decrease:,.2f} '
            f'÷ {energy_decrease:,.2f} '
            f'× 100 '
            f'= {energy_industry_contribution:.2f}%'
        )


        st.write(
            '공공 전기 및 열 생산'
        )

        st.write(
            f'{power_decrease:,.2f} '
            f'÷ {energy_industry_decrease:,.2f} '
            f'× 100 '
            f'= {power_contribution:.2f}%'
        )


    if power_contribution > 100:

        st.caption(
            '※ 다른 세부 부문의 증가분으로 인해 '
            '기여도가 100%를 넘을 수 있음'
        )


    st.divider()


    # -------------------------------------------------
    # 2023년 주요 분야 배출량
    # -------------------------------------------------

    st.subheader(
        '2023년 주요 분야 배출량'
    )


    comparison_data = []


    for label, category in category_map.items():

        value = get_value(
            category,
            2023
        )

        comparison_data.append({
            '분야': label,
            '배출량': value
        })


    comparison_df = pd.DataFrame(
        comparison_data
    )


    comparison_df = comparison_df.sort_values(
        by='배출량',
        ascending=False
    )


    fig, ax = plt.subplots(
        figsize=(10, 5)
    )


    bars = ax.bar(
        comparison_df['분야'],
        comparison_df['배출량'],
        color=[
            deep_green,
            green,
            light_green,
            soft_green
        ]
    )


    ax.bar_label(
        bars,
        labels=[
            f'{value:,.0f}'
            for value
            in comparison_df['배출량']
        ],
        padding=4,
        fontsize=10
    )


    ax.set_ylabel(
        '배출량 (kt CO₂-eq)'
    )


    ax.yaxis.set_major_formatter(
        StrMethodFormatter(
            '{x:,.0f}'
        )
    )


    ax.grid(
        axis='y',
        alpha=0.2
    )


    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


    st.caption('단위: kt CO₂-eq')


# =====================================================
# 분야별 분석
# =====================================================

elif menu == '분야별 분석':

    st.divider()


    selected_category = category_map[
        selected_label
    ]


    selected_df = long_df[
        long_df['분야 및 연도']
        == selected_category
    ].copy()


    selected_df['연도_num'] = pd.to_numeric(
        selected_df['연도']
    )


    selected_df = selected_df.sort_values(
        '연도_num'
    )


    value_1990 = get_value(
        selected_category,
        1990
    )


    value_2023 = get_value(
        selected_category,
        2023
    )


    change_rate = (
        (
            value_2023
            - value_1990
        )
        / value_1990
    ) * 100


    st.subheader(
        selected_label
    )


    kpi1, kpi2, kpi3 = st.columns(3)


    with kpi1:

        st.metric(
            '1990년',
            f'{value_1990:,.0f}'
        )


    with kpi2:

        st.metric(
            '2023년',
            f'{value_2023:,.0f}'
        )


    with kpi3:

        st.metric(
            '증감률',
            f'{change_rate:.1f}%'
        )


    st.caption('단위: kt CO₂-eq')


    with st.expander('증감률 계산'):

        st.write(
            f'({value_2023:,.2f} - '
            f'{value_1990:,.2f}) '
            f'÷ {value_1990:,.2f} × 100 '
            f'= {change_rate:.1f}%'
        )


    st.subheader(
        f'{selected_label} 연도별 변화'
    )


    fig, ax = plt.subplots(
        figsize=(11, 5)
    )


    ax.plot(
        selected_df['연도_num'],
        selected_df['배출량'],
        color=deep_green,
        linewidth=2.5,
        marker='o',
        markersize=4
    )


    ax.set_xlabel('연도')

    ax.set_ylabel(
        '배출량 (kt CO₂-eq)'
    )


    ax.set_xticks(
        range(1990, 2024, 5)
    )


    ax.yaxis.set_major_formatter(
        StrMethodFormatter(
            '{x:,.0f}'
        )
    )


    ax.grid(
        True,
        alpha=0.2
    )


    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


# =====================================================
# 데이터 확인
# =====================================================

elif menu == '데이터 확인':

    st.divider()

    st.subheader('데이터 확인')


    data_col1, data_col2 = st.columns(2)


    with data_col1:

        st.metric(
            '행',
            df.shape[0]
        )


    with data_col2:

        st.metric(
            '열',
            df.shape[1]
        )


    st.subheader('원본 데이터')


    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True
    )


    st.subheader('Long Format')


    st.dataframe(
        long_df,
        hide_index=True,
        use_container_width=True
    )


    st.caption(
        f'{long_df.shape[0]:,}행 × '
        f'{long_df.shape[1]}열'
    )


# =====================================================
# 하단
# =====================================================

st.divider()

st.caption(
    'Python · Pandas · Matplotlib · Streamlit'
)

