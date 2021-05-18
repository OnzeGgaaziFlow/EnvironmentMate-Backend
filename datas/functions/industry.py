#%%

import pandas as pd
import numpy as np
import requests  # http 요청 모듈
from bs4 import BeautifulSoup  # 웹 크롤링 모듈
from urllib.request import urlopen  # 웹 크롤링 모듈
from urllib.parse import quote_plus, urlencode
from pandas import DataFrame, Series  # 시리즈, 데이터프레임 모듈
from pandas import ExcelFile, ExcelWriter  # 엑셀 읽기, 쓰기 모듈
import pickle
import seaborn as sns
import matplotlib.pyplot as plt

#%%

pd.set_option("display.max_columns", 15)  # 컬럼 숫자 설정, 15
api_key = "O9x%2Fz4aw9J5CVY2AIqiXhR%2Bc1ct0L18%2BTxTNTcUWk3bPYvVi3ArLzL1Qlx7pPbRwDZGISzuSLiV51X2m2vUdew%3D%3D"  # 공공데이터 포털에서 받은 서비스키 입력
plt.rc("font", family="AppleGothic")
#%%


# 조건을 결합한 url 페이지 완성하는 함수
def url_page(page_n, file_type, year, cate, eg_type):
    api_url = "http://apis.data.go.kr/B553530/GHG_ANALYSIS_01/GHG_ANALYSIS_01_LIST"
    query_params = (
        "?"
        + urlencode(
            {
                quote_plus("pageNo"): page_n,  # 페이지 번호
                quote_plus("numOfRows"): "10",  # 페이지당 읽는 행 숫자
                quote_plus("apiType"): file_type,  # xml/json 중 선택
                quote_plus("q1"): year,  # 연도
                quote_plus("q2"): cate,  # 업종별/지역별/용도별/설비별/공정별/종사자규모별
                quote_plus("q3"): eg_type,  # TOE/CO2/GHG 중 선택
                # quote_plus('q4'): '22291',
                quote_plus("serviceKey"): "",
            }
        )
        + api_key
    )
    return api_url + query_params


#%%


def report_table(file_type, tyear, cate, eg_type):

    url = url_page("1", file_type, tyear, cate, eg_type)
    res = requests.get(url)  # get 방식으로 페이지 요청
    html = BeautifulSoup(res.text, "lxml")  # 위에 설정한 페이지 읽기
    # print(html)
    total_count = html.find("totalcount").text  # 전체 행수
    total_page = int(int(total_count) / int(html.find("numofrows").text)) + 1  # 전체 페이지수
    # print(total_count, total_page)

    rows = []  # 빈 리스트 설정
    for pgn in range(1, total_page + 1):
        url = url_page(pgn, file_type, tyear, cate, eg_type)
        res = requests.get(url)  # get 방식으로 페이지 요청
        html = BeautifulSoup(res.text, "lxml")  # 위에 설정한 페이지 읽기
        data = html.find_all("item")  # XML에서 시간별 데이터 읽기

        for idx in range(len(data)):
            year = data[idx].trgt_year.text  # 연도
            dvsn_nm = data[idx].agrt_dvsn_nm.text  # 업종별/지역별/용도별/설비별/공정별/종사자규모별
            dvsn_cd = data[idx].data_dvsn_cd.text  # TOE/CO2/GHG
            cate_nm = data[idx].agrt_cate_nm.text  # 세부 구분(업종명, 지역명 등)
            e_dvsn_nm = data[idx].engsrc_dvsn_nm.text  # 에너지원
            qnty = data[idx].usems_qnty.text  # 사용(배출)량

            rows.append(
                {
                    "연도": year,
                    "구분": dvsn_nm,
                    "단위": dvsn_cd,
                    "세부구분명": cate_nm,
                    "에너지원": e_dvsn_nm,
                    "사용(배출)량": qnty,
                }
            )

    cols = ["연도", "구분", "단위", "세부구분명", "에너지원", "사용(배출)량"]
    out_df = pd.DataFrame(rows)  # 리스트를 데이터프레임으로 변환
    out_df.columns = cols  # 데이터프레임의 컬럼명을 변경
    out_df["사용(배출)량"] = out_df["사용(배출)량"].astype("float64")  # string을 float로 변경
    # print(out_df)
    pv_df = pd.pivot_table(
        out_df, index="세부구분명", columns="에너지원", values="사용(배출)량", aggfunc="mean"
    )
    pv_df = pv_df.fillna(0)  # Nan을 0으로 대체

    # print(pv_df)

    return pv_df


def report_table_origin(file_type, tyear, cate, eg_type):
    plt.switch_backend("Agg")
    url = url_page("1", file_type, tyear, cate, eg_type)
    res = requests.get(url)  # get 방식으로 페이지 요청
    html = BeautifulSoup(res.text, "lxml")  # 위에 설정한 페이지 읽기
    # print(html)
    total_count = html.find("totalcount").text  # 전체 행수
    total_page = int(int(total_count) / int(html.find("numofrows").text)) + 1  # 전체 페이지수
    # print(total_count, total_page)

    rows = []  # 빈 리스트 설정
    for pgn in range(1, total_page + 1):
        url = url_page(pgn, file_type, tyear, cate, eg_type)
        res = requests.get(url)  # get 방식으로 페이지 요청
        html = BeautifulSoup(res.text, "lxml")  # 위에 설정한 페이지 읽기
        data = html.find_all("item")  # XML에서 시간별 데이터 읽기

        for idx in range(len(data)):
            year = data[idx].trgt_year.text  # 연도
            dvsn_nm = data[idx].agrt_dvsn_nm.text  # 업종별/지역별/용도별/설비별/공정별/종사자규모별
            dvsn_cd = data[idx].data_dvsn_cd.text  # TOE/CO2/GHG
            cate_nm = data[idx].agrt_cate_nm.text  # 세부 구분(업종명, 지역명 등)
            e_dvsn_nm = data[idx].engsrc_dvsn_nm.text  # 에너지원
            qnty = data[idx].usems_qnty.text  # 사용(배출)량

            rows.append(
                {
                    "연도": year,
                    "구분": dvsn_nm,
                    "단위": dvsn_cd,
                    "세부구분명": cate_nm,
                    "에너지원": e_dvsn_nm,
                    "사용(배출)량": qnty,
                }
            )

    cols = ["연도", "구분", "단위", "세부구분명", "에너지원", "사용(배출)량"]
    out_df = pd.DataFrame(rows)  # 리스트를 데이터프레임으로 변환
    out_df.columns = cols  # 데이터프레임의 컬럼명을 변경
    out_df["사용(배출)량"] = out_df["사용(배출)량"].astype("float64")  # string을 float로 변경
    return out_df


## 특정 연도의 전국 업종 중 해당 업종가 속한 지역의 에너지 사용량 (총합량)에 대한 분석 결과
def total_usems_qnty(year, industry, unit):
    plt.switch_backend("Agg")
    data = report_table("xml", str(year), "업종별", unit)
    labels = data.index.to_list()
    # print(labels)
    colors = sns.color_palette("hls", len(labels))
    frequency = data["합계"].values
    industry_frequency = frequency[labels.index(industry)]
    fig = plt.figure(figsize=(8, 8))
    fig.set_facecolor("white")
    ax = fig.add_subplot()
    explode = np.zeros(len(labels))
    explode[labels.index(industry)] = 0.1
    # print(explode)
    pie = ax.pie(
        frequency,
        explode=explode,
        # labels=labels,
        startangle=90,
        counterclock=False,
        colors=colors,
    )

    total = np.sum(frequency)
    threshold = 5
    sum_pct = 0
    bbox_props = dict(boxstyle="square", fc="w", ec="w", alpha=0)
    config = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, va="center")

    for i, l in enumerate(labels):
        ang1, ang2 = ax.patches[i].theta1, ax.patches[i].theta2
        center, r = ax.patches[i].center, ax.patches[i].r

        if i < len(labels) - 1:
            sum_pct += float(f"{frequency[i]/total*100:.2f}")
            text = f"{frequency[i]/total*100:.2f}%"
        else:
            text = f"{100-sum_pct:.2f}%"

        if frequency[i] / total * 100 < threshold:
            ang = (ang1 + ang2) / 2
            x = np.cos(np.deg2rad(ang))
            y = np.sin(np.deg2rad(ang))

            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
            config["arrowprops"].update({"connectionstyle": connectionstyle})
            ax.annotate(
                text,
                xy=(x, y),
                xytext=(1.5 * x, 1.2 * y),
                horizontalalignment=horizontalalignment,
                **config,
            )
        else:
            x = (r / 2) * np.cos(np.pi / 180 * ((ang1 + ang2) / 2)) + center[0]
            y = (r / 2) * np.sin(np.pi / 180 * ((ang1 + ang2) / 2)) + center[1]
            ax.text(x, y, text, ha="center", va="center", fontsize=12)
    result = f"{year}년도 국내 업종 총 온실가스({round(total):,.0f} [{unit}]) 대비 현재 {industry} 업종은 {industry_frequency/total*100:.2f}%의 온실가스({round(industry_frequency):,.0f}[{unit}])를 배출하고 있습니다."
    plt.legend(pie[0], labels)  ## 범례
    plt.savefig(f"industry_total_usems_qnty_{year}_{industry}.png")
    return result


## 해당 업체가 속한 업종의 에너지 대비 사용량에 대한 분석 결과
def industry_usems_qnty_statistics(year, industry, usage, unit):
    plt.switch_backend("Agg")
    data = report_table("xml", str(year), "업종별", unit)  # 파일형식, 연도, 구분, 에너지/온실가스
    ## 데이터 준비
    labels = ["동종 업체", "해당 업체"]
    colors = sns.color_palette("hls", len(labels))  ## 색상
    frequency = [(data.at[industry, "합계"] - usage), usage]
    my_frequency = frequency[1]
    fig = plt.figure(figsize=(8, 8))
    fig.set_facecolor("white")
    ax = fig.add_subplot()
    explode = np.zeros(len(labels))
    explode[1] = 0.1
    # print(explode)
    pie = ax.pie(
        frequency,
        explode=explode,
        startangle=90,
        counterclock=False,
        colors=colors,
    )

    total = np.sum(frequency)  ## 빈도수 합
    threshold = 5  ## 상한선 비율
    sum_pct = 0  ## 퍼센티지
    bbox_props = dict(boxstyle="square", fc="w", ec="w", alpha=0)  ## annotation 박스 스타일
    ## annotation 설정
    config = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, va="center")

    for i, l in enumerate(labels):
        ang1, ang2 = ax.patches[i].theta1, ax.patches[i].theta2  ## 파이의 시작 각도와 끝 각도
        center, r = ax.patches[i].center, ax.patches[i].r  ## 원의 중심 좌표와 반지름길이

        if i < len(labels) - 1:
            sum_pct += float(f"{frequency[i]/total*100:.2f}")
            text = f"{frequency[i]/total*100:.2f}%"
        else:  ## 마지막 파이 조각은 퍼센티지의 합이 100이 되도록 비율을 조절
            text = f"{100-sum_pct:.2f}%"

        ## 비율 상한선보다 작은 것들은 Annotation으로 만든다.
        if frequency[i] / total * 100 < threshold:
            ang = (ang1 + ang2) / 2  ## 중심각
            x = np.cos(np.deg2rad(ang))  ## Annotation의 끝점에 해당하는 x좌표
            y = np.sin(np.deg2rad(ang))  ## Annotation의 끝점에 해당하는 y좌표

            ## x좌표가 양수이면 즉 y축을 중심으로 오른쪽에 있으면 왼쪽 정렬
            ## x좌표가 음수이면 즉 y축을 중심으로 왼쪽에 있으면 오른쪽 정렬
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)  ## 시작점과 끝점 연결 스타일
            config["arrowprops"].update({"connectionstyle": connectionstyle})  ##
            ax.annotate(
                text,
                xy=(x, y),
                xytext=(1.5 * x, 1.2 * y),
                horizontalalignment=horizontalalignment,
                **config,
            )
        else:
            x = (r / 2) * np.cos(np.pi / 180 * ((ang1 + ang2) / 2)) + center[
                0
            ]  ## 텍스트 x좌표
            y = (r / 2) * np.sin(np.pi / 180 * ((ang1 + ang2) / 2)) + center[
                1
            ]  ## 텍스트 y좌표
            ax.text(x, y, text, ha="center", va="center", fontsize=12)
    result = f"{industry} 업종 총 ({round(total):,.0f}[{unit}]) 온실가스 중 해당 업체는 온실가스({round(my_frequency):,.0f}[{unit}]) 배출하고 있습니다."
    plt.legend(pie[0], labels, loc="upper right")  ## 범례
    plt.savefig(f"my_industry_usems_qnty_{year}_{industry}.png")
    return result


## 해당 업체가 속한 업종의 각 에너지 종류 별 사용량에 대한 분석 결과
def items_usems_qnty_statistics(
    year, industry, gas, other, oil, coal, thermal, electric, unit
):
    plt.switch_backend("Agg")
    data = report_table_origin("xml", str(year), "업종별", unit)  # 파일형식, 연도, 구분, 에너지/온실가스
    data = data.groupby(["세부구분명", "에너지원"]).mean()
    labels = data.index.to_list()
    # print(labels)
    # print(data.index)
    plt.figure(figsize=(15, 7))
    same_industry = data.loc[industry][:6].values  # 에너지 종류별 사용량
    my_industry = [gas, other, oil, coal, thermal, electric]
    index_list = ["가스", "기타", "석유류", "석탄류", "열에너지", "전력"]
    plt.plot(index_list, same_industry, marker="s", color="r")
    plt.plot(index_list, my_industry, marker="o", color="g")
    plt.ylabel(f"사용량[{unit}]", fontsize=14)
    plt.xlabel("에너지 종류", fontsize=14)
    # for i, v in enumerate(index_list):
    #     plt.text(v, *same_industry[i], *same_industry[i],
    #              fontsize=9,
    #              color='r',
    #              horizontalalignment='center',
    #              verticalalignment='bottom')
    # for i, v in enumerate(index_list):
    #     plt.text(v, my_industry[i], my_industry[i],
    #              fontsize=9,
    #              color='b',
    #              horizontalalignment='center',
    #              verticalalignment='bottom')
    plt.legend(["동종업체 평균", "해당 기업"], loc="upper right")
    plt.savefig(f"items_usems_qnty_statistics_{year}_{industry}.png")
    title_list = []
    mission_list = []
    for i in range(6):
        if same_industry[i] < my_industry[i]:
            value = int(my_industry[i] - same_industry[i])
            title_list.append(
                f"동종업체에 비해 {index_list[i]} 사용량이 {value:,.0f}GHG 이상 많이 배출되고 있습니다."
            )
            mission_list.append(
                f"{index_list[i]} 사용량 {int(my_industry[i]) / 50:,.0f}GHG 감축 미션"
            )
    return title_list, mission_list


#%%
#############
#   TEST    #
#############

"""
ex) ['광업', '그외기타제조업', '비금속광물제품', '섬유제품업', '음식료업', '자동차제조업', '전자장비제조업', '정유', '제1차금속산업', '제조업소계', '펄프종이', '화학']
"""
if __name__ == "__main__":
    print(total_usems_qnty(2018, "광업", "GHG"))
    print(industry_usems_qnty_statistics(2018, "광업", 130002, "GHG"))
    print(
        items_usems_qnty_statistics(
            2018, "광업", 5000, 150, 70000, 200000, 550, 200000, "GHG"
        )
    )
