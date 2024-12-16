import streamlit as st
import matplotlib.pyplot as plt
import gsp
import numpy as np
from datetime import datetime
from matplotlib.ticker import FuncFormatter
import japanize_matplotlib
import calendar

st.title('給料グラフ')

# パラメータの初期化
if 'spreadsheet_url' not in st.query_params:
    st.query_params.spreadsheet_url = ''
if 'sheet_name' not in st.query_params:
    st.query_params.sheet_name = ''
if 'work_times_range' not in st.query_params:
    st.query_params.work_times_range = ''
if 'salary_per_hour' not in st.query_params:
    st.query_params.salary_per_hour = 0
if 'target_salary' not in st.query_params:
    st.query_params.target_salary = 0

if 'settings_expanded' not in st.session_state:
    st.session_state.settings_expanded = True

with st.expander("パラメーター設定", expanded=st.session_state.settings_expanded):
    spreadsheet_url = st.text_input(label='Google Spreadsheet URL',
                                    placeholder='https: // docs.google.com/spreadsheets/d/xxxx',
                                    value=st.query_params.spreadsheet_url)
    sheet_name = st.text_input(label='Sheet名',
                               placeholder='Sheet1',
                               value=st.query_params.sheet_name)
    # 日ごとの勤務時間
    work_times_range = st.text_input(label='勤務時間の範囲',
                                     placeholder='A1:Alast_day',
                                     value=st.query_params.work_times_range)
    salary_per_hour = st.number_input(
        label='時給', value=int(st.query_params.salary_per_hour), step=100, placeholder=1000)
    target_salary = st.number_input(
        label='月の目標金額', value=int(st.query_params.target_salary), step=1000, placeholder=100000)

    def contract():
        st.session_state.settings_expanded = False
    save_settings_button = st.button(label='決定', on_click=contract)

if save_settings_button:
    # パラメータを保存
    st.query_params.spreadsheet_url = spreadsheet_url
    st.query_params.sheet_name = sheet_name
    st.query_params.work_times_range = work_times_range
    st.query_params.salary_per_hour = salary_per_hour
    st.query_params.target_salary = target_salary

    # 勤務時間を取得
    work_times = gsp.get_range(
        spreadsheet_url, sheet_name, work_times_range)

    if work_times == None:
        st.error('Failed to get current work time')
    else:
        def to_hour(time: str) -> float:
            if time.count(':') == 1:
                h, m = time.split(':')
                return float(h) + float(m) / 60
            if time.count(':') == 2:
                h, m, s = time.split(':')
                return float(h) + float(m) / 60 + float(s) / 3600
        work_times = [to_hour(w) for w in work_times]
        today = datetime.now().day
        cumulative_salary = np.cumsum(work_times[:today]) * salary_per_hour
        a, b = np.polyfit(range(today), cumulative_salary, 1)
        last_day = calendar.monthrange(
            datetime.now().year, datetime.now().month)[1]

        # グラフ描画
        fig, ax = plt.subplots()
        ax.axhline(y=target_salary, color='r', linestyle='--', label='給料目標')
        ax.plot(range(1, last_day+1), np.arange(1, last_day+1)*target_salary/last_day,
                color='r', linestyle=':', label='理論値')
        ax.plot(range(1, last_day+1), a * np.arange(1, last_day+1) + b,
                color='b', linestyle='--', label='給料予測')
        ax.plot(range(1, today+1), cumulative_salary,
                marker='o', color='g', linestyle='-', label='給料')

        # グラフの装飾
        ax.legend()
        ax.grid()
        ax.set_xlim(1, last_day)
        ax.set_xlabel('日数')
        ax.set_ylabel('給料', rotation=0)
        txt = cumulative_salary[-1]
        ax.annotate(f'{int(txt):,}円', (today, txt),
                    textcoords="offset points", xytext=(0, -20), ha='center')

        # 軸のフォーマッター関数を定義
        def yen_formatter(y, pos):
            return f'{int(y / 10000)}万'

        def day_formatter(x, pos):
            return f'{int(x)}日'

        # 軸のフォーマッターを設定
        yformatter = FuncFormatter(yen_formatter)
        xformatter = FuncFormatter(day_formatter)

        # フォーマッターを適用
        plt.gca().yaxis.set_major_formatter(yformatter)
        plt.gca().xaxis.set_major_formatter(xformatter)

        st.header('今週の給料')
        st.write(f'今日までの給料: {int(cumulative_salary[-1]):,}円')
        st.write(f'給料予測: {int(a*last_day+b):,}円')
        st.pyplot(plt)
