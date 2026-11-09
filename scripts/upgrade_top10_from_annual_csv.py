"""Top 10 nations by 2002-2022 total wins, plus Korea, when the original six CSVs exist.
Usage: python scripts/upgrade_top10_from_annual_csv.py
Does not fabricate countries. Fails if any CSV missing or six-year Korea stats mismatch.
Overwrites charts 02, 05, 06 and produces data/top10_comparison.csv.
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'data'/'source'
YEARS=(2002,2006,2010,2014,2018,2022)
RENAMES={'Korea Republic':'South Korea','Republic of Korea':'South Korea','Korea, South':'South Korea','Korea Rep.':'South Korea','IR Iran':'Iran','USA':'United States','England':'England','Germany FR':'Germany'}
KO={'South Korea':'대한민국','Argentina':'아르헨티나','Brazil':'브라질','Germany':'독일','France':'프랑스','Spain':'스페인','Italy':'이탈리아','England':'잉글랜드','Netherlands':'네덜란드','Croatia':'크로아티아','Portugal':'포르투갈','Belgium':'벨기에','Uruguay':'우루과이','Japan':'일본','Switzerland':'스위스','United States':'미국','Mexico':'멕시코','Morocco':'모로코','Senegal':'세네갈','Sweden':'스웨덴','Denmark':'덴마크'}
plt.rcParams.update({'font.family':'NanumGothic','axes.unicode_minus':False,'font.size':10,'axes.spines.top':False,'axes.spines.right':False})

def find_csv(year):
    candidates=[p for p in DIR.glob('*.csv') if re.search(rf'(?<!\d){year}(?!\d)',p.stem)]
    if len(candidates)!=1: raise FileNotFoundError(f'{year}년 CSV 1개 필요: {DIR} (발견 {len(candidates)}개)')
    return candidates[0]

def gather():
    parts=[]
    required=['Position','Team','Games Played','Win','Draw','Loss','Goals For','Goals Against']
    for year in YEARS:
        path=find_csv(year);d=pd.read_csv(path);d.columns=d.columns.str.strip()
        if set(required)-set(d.columns):raise ValueError(f'{path.name}: 누락 열 {set(required)-set(d.columns)}')
        d=d[required].copy();d['Team']=d['Team'].astype(str).str.strip().replace(RENAMES);d['Year']=year
        for c in required[2:]:d[c]=pd.to_numeric(d[c],errors='raise')
        d['Position']=pd.to_numeric(d['Position'],errors='raise')
        if len(d)!=32 or d.Team.duplicated().any():raise ValueError(f'{path.name}: 32개 국가·중복 기준 불일치')
        if not (d['Games Played']==d.Win+d.Draw+d.Loss).all():raise ValueError(f'{path.name}: 경기·승무패 합계 불일치')
        parts.append(d)
    return pd.concat(parts,ignore_index=True)

def main():
    d=gather(); s=d.groupby('Team',as_index=True).agg(경기=('Games Played','sum'),승=('Win','sum'),득점=('Goals For','sum'),실점=('Goals Against','sum'))
    kr=s.loc['South Korea']; actual=[int(kr['경기']),int(kr['승']),int(kr['득점']),int(kr['실점'])]
    if actual!=[24,7,28,35]:raise ValueError(f'한국 기존 노트북과 데이터 불일치: {actual} != [24,7,28,35]. 원본 데이터 정의 재검토 필요')
    # Check all four countries from original notebook before mixing historical baselines.
    expected={'Argentina':[31,20,52,32],'Brazil':[34,23,64,30],'Germany':[34,23,70,27],'South Korea':[24,7,28,35]}
    for name,vals in expected.items():
        if name not in s.index or s.loc[name,['경기','승','득점','실점']].astype(int).tolist()!=vals:
            raise ValueError(f'{name} 집계 불일치: 기존 분석과 다른 출처/집계일 수 있음')
    top=s.drop(index='South Korea').sort_values(['승','득점','경기'],ascending=[False,False,False]).head(10)
    # Top10 competitors + Korea = 11 rows, even if Korea would rank inside overall top10.
    chosen=pd.concat([top,s.loc[['South Korea']]]);chosen['승률(%)']=chosen['승']/chosen['경기']*100
    chosen['득점/경기']=chosen['득점']/chosen['경기'];chosen['실점/경기']=chosen['실점']/chosen['경기'];chosen['표기명']=[KO.get(k,k) for k in chosen.index]
    chosen.to_csv(ROOT/'data'/'top10_comparison.csv',encoding='utf-8-sig')
    (ROOT/'charts').mkdir(exist_ok=True)
    # 02: horizontal scored/conceded bars
    view=chosen.sort_values('득점/경기');y=np.arange(len(view));fig,ax=plt.subplots(figsize=(11,8));a=ax.barh(y-.18,view['득점/경기'],height=.34,color=['#E3484E' if k=='South Korea' else '#397BAD' for k in view.index],label='경기당 득점');b=ax.barh(y+.18,view['실점/경기'],height=.34,color=['#EBA5A6' if k=='South Korea' else '#AAB4C3' for k in view.index],label='경기당 실점');ax.set_yticks(y,view['표기명']);ax.set_xlabel('골 / 경기');ax.set_title('2002~2022년 승리 수 상위 10개국 + 한국: 경기당 득실',fontsize=15,pad=14);ax.bar_label(a,fmt='%.2f',padding=2,fontsize=8);ax.bar_label(b,fmt='%.2f',padding=2,fontsize=8);ax.legend(ncol=2);ax.set_xlim(0,max(view['득점/경기'].max(),view['실점/경기'].max())+0.5);fig.tight_layout();fig.savefig(ROOT/'charts'/'02_country_goals_comparison.png',dpi=190,bbox_inches='tight');plt.close(fig)
    # 05 win rate
    view=chosen.sort_values('승률(%)');fig,ax=plt.subplots(figsize=(10,7.5));b=ax.barh(view['표기명'],view['승률(%)'],color=['#E3484E' if k=='South Korea' else '#397BAD' for k in view.index]);ax.bar_label(b,labels=[f'{v:.1f}%' for v in view['승률(%)']],padding=3);ax.set_xlim(0,100);ax.set_xlabel('승률 (%)');ax.set_title('2002~2022년 승리 수 상위 10개국 + 한국: 승률',fontsize=15);fig.tight_layout();fig.savefig(ROOT/'charts'/'05_country_win_rate.png',dpi=190,bbox_inches='tight');plt.close(fig)
    # 06 scatter
    fig,ax=plt.subplots(figsize=(10,7));
    for name,row in chosen.iterrows():
        ax.scatter(row['득점/경기'],row['실점/경기'],c='#E3484E' if name=='South Korea' else '#397BAD',s=125 if name=='South Korea' else 54,zorder=3)
        ax.annotate(KO.get(name,name),(row['득점/경기'],row['실점/경기']),xytext=(6,6),textcoords='offset points',fontsize=9)
    ax.set_xlabel('경기당 득점 (골)');ax.set_ylabel('경기당 실점 (골)');ax.set_title('2002~2022년 승리 수 상위 10개국 + 한국: 공격·수비 위치',fontsize=14);ax.grid(alpha=.18);fig.tight_layout();fig.savefig(ROOT/'charts'/'06_country_scatter.png',dpi=190,bbox_inches='tight');plt.close(fig)
    print('Top 10 + Korea charts rendered. Selected nations:',list(chosen.index))

if __name__=='__main__':main()
