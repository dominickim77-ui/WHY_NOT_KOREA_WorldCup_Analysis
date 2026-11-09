# ============================================================
# 데이터 분석 수업 공통 라이브러리 파일
# ------------------------------------------------------------
# 이 파일은 각 Colab/Jupyter 노트북에서 `%run start.py`로 실행한다.
# 즉, 수업에서 반복해서 사용하는 라이브러리를 한 번에 준비하는 역할이다.
#
# [핵심 개념]
# pandas      : 표(DataFrame) 데이터 처리
# numpy       : 숫자/배열 계산
# seaborn     : 통계 그래프
# matplotlib  : 그래프 출력
# scipy       : 통계 계산
# sklearn     : 머신러닝 전처리/회귀/군집
# statsmodels : 회귀 결과를 통계적으로 자세히 확인
# ============================================================

# 경고 메시지 무시 (출력 화면을 깔끔하게 하기 위해)
import warnings
warnings.filterwarnings(action='ignore') 


# 데이터 분석/처리를 위한 라이브러리
import pandas as pd    # 데이터프레임(표) 처리
import numpy as np       # 수치 연산 라이브러리   
import seaborn as sns    # 통계 시각화 라이브러리
import matplotlib.pyplot as plt  # 그래프 시각화 라이브러리
import scipy as sp     # 과학/통계 계산 라이브러리

# 데이터 전처리용
from sklearn.preprocessing import StandardScaler   # 표준화(평균 0, 표준편차 1로 변환)

# 회귀 분석
from sklearn.linear_model import LinearRegression   # 선형 회귀 분석
import statsmodels.formula.api as smf               # 통계 모델링(formula 방식)

# 데이터 분할(학습/테스트)
from sklearn.model_selection import train_test_split   # 데이터셋 나누기

# 날짜 계산
from dateutil.relativedelta import relativedelta  # 날짜 간 간격 계산

# 군집 분석
from sklearn.cluster import KMeans      # K-Means 군집화
from yellowbrick.cluster import KElbowVisualizer      # Elbow 방법 시각화 도구

# 날짜/시간 처리
import datetime


# 한글 폰트 및 그래프 설정
plt.rc('font',family='Malgun Gothic')  # 한글 폰트 설정 (맑은 고딕)
plt.rcParams['axes.unicode_minus']=False  # '- 표시 마이너스 기호 깨짐 방지

