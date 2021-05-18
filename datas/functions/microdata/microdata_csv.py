import numpy as np
import pandas as pd

# import tensorflow as tf
# from tensorflow import feature_column
# from tensorflow.keras import layers
# from sklearn.model_selection import train_test_split
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import quote_plus, urlencode
from pandas import DataFrame, Series
from pandas import ExcelFile, ExcelWriter

pd.set_option("display.max_columns", 15)

api_key = "O9x%2Fz4aw9J5CVY2AIqiXhR%2Bc1ct0L18%2BTxTNTcUWk3bPYvVi3ArLzL1Qlx7pPbRwDZGISzuSLiV51X2m2vUdew%3D%3D"


def url_page(page_n, file_type, year, area, eg_type):
    if eg_type == "TOE":
        api_url = "http://apis.data.go.kr/B553530/GHG_LIST_04/GHG_LIST_04_02_VIEW"
    if eg_type == "GHG":
        api_url = "http://apis.data.go.kr/B553530/GHG_LIST_04/GHG_LIST_04_03_VIEW"
    query_params = (
        "?"
        + urlencode(
            {
                quote_plus("pageNo"): page_n,  # 페이지 번호
                quote_plus("numOfRows"): "10",  # 페이지당 읽는 행 숫자
                quote_plus("apiType"): file_type,  # xml/json 중 선택
                quote_plus("q1"): year,  # 연도
                quote_plus("q2"): area,  # 지역
                # quote_plus('q3'): man, # 종사자규모
                # quote_plus('q4'): ksic, # 표준산업분류 코드
                # quote_plus('q5'): e_type, # 에너지원
                quote_plus("serviceKey"): "",
            }
        )
        + api_key
    )
    # print(api_url + query_params)
    return api_url + query_params


def micro_data(file_type, tyear, area, eg_type):

    url = url_page("1", file_type, tyear, area, eg_type)
    res = requests.get(url)  # get 방식으로 페이지 요청
    html = BeautifulSoup(res.text, "lxml")  # 위에 설정한 페이지 읽기
    # print(html)

    total_count = html.find("totalcount").text  # 전체 행수
    total_page = int(int(total_count) / int(html.find("numofrows").text)) + 1  # 전체 페이지수
    print("전체 행수, 전체 페이지수 : ", total_count, total_page)

    rows = []  # 빈 리스트 설정
    for pgn in range(1, total_page + 1):
        url = url_page(pgn, file_type, tyear, area, eg_type)
        res = requests.get(url)  # get 방식으로 페이지 요청
        html = BeautifulSoup(res.text, "lxml")  # 위에 설정한 페이지 읽기
        data = html.find_all("item")  # XML에서 시간별 데이터 읽기

        for idx in range(len(data)):
            fanm = data[idx].wrkplc_fanm.text  # 사업장가명
            year = data[idx].trgt_year.text  # 연도
            locl = data[idx].widm_locl_nm.text  # 광역지역
            wrkr = data[idx].wrkplc_wrkr_vol_nm.text  # 종사자규모
            ennm = data[idx].engsrc_nm.text  # 에너지원
            endv = data[idx].engsrc_dvsn_nm.text  # 에너지 구분
            kscd = data[idx].ksic_cd.text  # 표준산업분류코드
            ksnm = data[idx].ksic_nm.text  # 표준산업분류명
            if eg_type == "TOE":
                use = data[idx].engy_cnsm_qnty_nidval.text  # 소비(배출)량
            if eg_type == "GHG":
                use = data[idx].ghg_emsn_qnty_nidval.text  # 소비(배출)량

            rows.append(
                {
                    "사업장": fanm,
                    "연도": year,
                    "광역지역": locl,
                    "종사자규모": wrkr,
                    "에너지원": ennm,
                    "에너지구분": endv,
                    "표준산업코드": kscd,
                    "표준산업코드명": ksnm,
                    "소비(배출)량": use,
                }
            )

    cols = [
        "사업장",
        "연도",
        "광역지역",
        "종사자규모",
        "에너지원",
        "에너지구분",
        "표준산업코드",
        "표준산업코드명",
        "소비(배출)량",
    ]
    out_df = pd.DataFrame(rows)  # 리스트를 데이터프레임으로 변환
    out_df.columns = cols  # 데이터프레임의 컬럼명을 변경
    # print(out_df)

    return out_df


#
# def micro_data(file_type, tyear, eg_type):
#
#     url = url_page('1', file_type, tyear, eg_type)
#     res = requests.get(url) # get 방식으로 페이지 요청
#     html = BeautifulSoup(res.text, 'lxml') # 위에 설정한 페이지 읽기
#     # print(html)
#
#     total_count = html.find('totalcount').text # 전체 행수
#     total_page = int(int(total_count)/int(html.find('numofrows').text))+1 # 전체 페이지수
#     print('전체 행수, 전체 페이지수 : ', total_count, total_page)
#
#     rows=[] # 빈 리스트 설정
#     for pgn in range(1, total_page + 1):
#         url = url_page(pgn, file_type, tyear, eg_type)
#         res = requests.get(url) # get 방식으로 페이지 요청
#         html = BeautifulSoup(res.text, 'lxml') # 위에 설정한 페이지 읽기
#         data = html.find_all('item') # XML에서 시간별 데이터 읽기
#
#         for idx in range(len(data)):
#             fanm = data[idx].wrkplc_fanm.text # 사업장가명
#             year = data[idx].trgt_year.text # 연도
#             locl = data[idx].widm_locl_nm.text # 광역지역
#             wrkr = data[idx].wrkplc_wrkr_vol_nm.text # 종사자규모
#             ennm = data[idx].engsrc_nm.text # 에너지원
#             endv = data[idx].engsrc_dvsn_nm.text # 에너지 구분
#             kscd = data[idx].ksic_cd.text # 표준산업분류코드
#             ksnm = data[idx].ksic_nm.text # 표준산업분류명
#             if eg_type == 'TOE':
#                 use = data[idx].engy_cnsm_qnty_nidval.text # 소비(배출)량
#             if eg_type == 'GHG':
#                 use = data[idx].ghg_emsn_qnty_nidval.text # 소비(배출)량
#
#             rows.append({'사업장':fanm, '연도':year, '광역지역':locl, '종사자규모':wrkr,
#                     '에너지원':ennm, '에너지구분':endv, '표준산업코드':kscd, '표준산업코드명':ksnm, '소비(배출)량':use})
#
#     cols = ['사업장', '연도', '광역지역', '종사자규모', '에너지원', '에너지구분', '표준산업코드', '표준산업코드명', '소비(배출)량']
#     out_df = pd.DataFrame(rows) # 리스트를 데이터프레임으로 변환
#     out_df.columns = cols # 데이터프레임의 컬럼명을 변경
#     #print(out_df)
#
#     return out_df


# 사업장 id, 연도, 지역, 온실가스배출 단위를 입력으로 받으면 과거 해당 사업장에 대한 에너지 소비량을 확인할 수 있음.
def micro_data_table(id, tyear, area, eg_type):
    data = micro_data("xml", tyear, area, eg_type)
    data = data[data["사업장"] == id]
    data.to_csv(f"micro_data_test_{id}_{tyear}.csv")
    return data


# 사업장 id, 지역, 온실가스 배출 단위를 입력으로 받으면 과거 에너지 소비량에 대한 시계열 데이터를 그래프로 확인할 수 있음. (2010~2018)
def micro_data_series_data(id, area, eg_type):
    data = micro_data("xml", str(2015), area, eg_type)
    for i in range(2016, 2019):
        try:
            next = micro_data("xml", str(i), area, eg_type)
            next = next[data["사업장"] == id]
            data = data.concat[data, next]
        except:
            continue
    data.to_csv(f"micro_series_data_{id}.csv")
    return data


#############
#   TEST    #
#############
if __name__ == "__main__":
    # micro_data_table
    result = micro_data_series_data(
        "51CCEC9C57F34E659F58C46CC90A90D37C526FA5", "제주", "GHG"
    )
    print(result)
    # micro_data_series_data('51CCEC9C57F34E659F58C46CC90A90D37C526FA5', '제주', 'GHG')
