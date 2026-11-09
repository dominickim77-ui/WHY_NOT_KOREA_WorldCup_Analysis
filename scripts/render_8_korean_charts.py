"""Regenerate eight Korean charts from existing notebook saved numeric tables.
The 2002-2022 Top 10 expansion is separate and requires original annual CSVs.
"""
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
OUT=Path(__file__).resolve().parents[1]
nb=json.loads((OUT/"WHY_NOT_KOREA_WorldCup_Analysis.ipynb").read_text(encoding="utf-8"))
def tab(i):
 return next("".join(o["data"]["text/plain"]) for o in nb["cells"][i]["outputs"] if "text/plain" in o.get("data",{}))
(OUT/"charts").mkdir(exist_ok=True)
(OUT/"data").mkdir(exist_ok=True)
rows=[]
for line in tab(5).splitlines()[1:]:
 t=line.split(); rows.append([int(x) for x in t[1:]])
ko=pd.DataFrame(rows, columns=['연도','최종순위','경기','승','무','패','득점','실점'])
ko['경기당 득점']=ko['득점']/ko['경기'];ko['경기당 실점']=ko['실점']/ko['경기'];ko['승률(%)']=ko['승']/ko['경기']*100
ko_recent=ko[ko['연도'].between(2002,2022)].copy()
records=[]
for line in tab(8).split('Conceded Per Game')[0].rstrip().splitlines()[2:]:
 country,games,wins,gf,ga,_,_=line.rsplit(maxsplit=6)
 records.append((country.strip(),int(games),int(wins),int(gf),int(ga)))
countries=pd.DataFrame(records,columns=['Country','Games','Wins','GF','GA']);countries['득점/경기']=countries.GF/countries.Games;countries['실점/경기']=countries.GA/countries.Games;countries['승률(%)']=100*countries.Wins/countries.Games;countries['득실차/경기']=(countries.GF-countries.GA)/countries.Games
names={'Argentina':'아르헨티나','Brazil':'브라질','Germany':'독일','South Korea':'대한민국'};countries['국가']=countries.Country.map(names)
stages=pd.DataFrame([['4강 진출',24,1.74,.83],['8강 진출',24,1.64,.81],['16강 진출',48,1.24,1.26],['조별리그 탈락',96,.83,1.69]],columns=['구간','팀·대회 기록','득점/경기','실점/경기']);stages['득실차/경기']=[0.91,0.83,-0.02,-0.87]  # exact saved notebook output (unrounded source difference)
champs=pd.DataFrame([[2002,'브라질',2.57,.57],[2006,'이탈리아',1.71,.29],[2010,'스페인',1.14,.29],[2014,'독일',2.57,.57],[2018,'프랑스',2,.86],[2022,'아르헨티나',2.14,1.14]],columns=['연도','우승국','득점/경기','실점/경기'])
# save extracted tables, precise notebook output provenance
for k,v in [('korea_history',ko),('four_countries',countries),('stage_aggregates',stages),('champions',champs)]:v.to_csv(OUT/'data'/f'{k}_from_notebook.csv',index=False,encoding='utf-8-sig')
assert len(ko_recent)==6 and int(ko_recent['경기'].sum())==24 and int(ko_recent['득점'].sum())==28 and int(ko_recent['실점'].sum())==35
assert countries.loc[countries.Country=='South Korea','Games'].iloc[0]==24
font=fm.FontProperties(family='NanumGothic')
plt.rcParams.update({'font.family':'NanumGothic','axes.unicode_minus':False,'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
GREY='#A8B0BF';RED='#E3484E';BLUE='#4179AE';ORANGE='#D99643';GREEN='#27826B'
def title(ax,txt,sub=None):
 ax.set_title(txt,loc='left',fontsize=15,fontweight='bold',y=1.10)
 if sub: ax.text(0,1.025,sub,transform=ax.transAxes,fontsize=9,color='#566277',va='bottom')
def footer(fig,txt):fig.text(.06,.018,txt,fontsize=8,color='#647084')
def save(fig,n):
 fig.savefig(OUT/'charts'/n,dpi=190,bbox_inches='tight');plt.close(fig)
# 1 rankings
fig,ax=plt.subplots(figsize=(11,5.5));ax.plot(ko['연도'],ko['최종순위'],marker='o',c=BLUE,lw=2.3)
for r in ko.itertuples(index=False):
 ax.annotate(f'{r.최종순위}위',(r.연도,r.최종순위),xytext=(0,-16 if r.연도 in [1998,2014] else 9),textcoords='offset points',ha='center',fontsize=8,color=RED if r.연도==2002 else '#344255')
ax.scatter([2002],[4],c=RED,s=120,zorder=5);ax.invert_yaxis();ax.set_xlabel('월드컵 개최 연도');ax.set_ylabel('한국 최종 순위 (작을수록 우수)');ax.set_xticks(ko['연도']);ax.tick_params(axis='x',rotation=35);ax.grid(axis='y',alpha=.18)
title(ax,'한국 월드컵 최종 순위의 변화','1954~2022년 참가 11개 대회 · 2002년 4위 강조');footer(fig,'근거: 기존 노트북 6번 셀의 저장 출력 · FIFA 공식 원자료 독립 대조 전');fig.tight_layout(rect=(0,.05,1,1));save(fig,'01_korea_worldcup_rank.png')
# 2 grouped compare 4 nations
fig,ax=plt.subplots(figsize=(10,5.8));x=np.arange(len(countries)); w=.34;bars1=ax.bar(x-w/2,countries['득점/경기'],w,color=[RED if n=='대한민국' else BLUE for n in countries['국가']],label='경기당 득점');bars2=ax.bar(x+w/2,countries['실점/경기'],w,color=[RED if n=='대한민국' else GREY for n in countries['국가']],alpha=.58,label='경기당 실점');ax.bar_label(bars1,fmt='%.2f',padding=3,fontsize=9);ax.bar_label(bars2,fmt='%.2f',padding=3,fontsize=9)
ax.set_xticks(x,countries['국가']);ax.set_ylim(0,2.45);ax.set_ylabel('골 / 경기');ax.legend(ncols=2,frameon=False);title(ax,'국가별 경기당 득점과 실점','2002~2022년 · 검증 가능한 4개 국가 · 한국 빨간색 강조');footer(fig,'전체 상위 10개국 원본 CSV 미포함: Top 10으로 해석하지 않음');fig.tight_layout(rect=(0,.06,1,1));save(fig,'02_country_goals_comparison.png')
# 3 Korea 2002 vs champions
v=np.array([[8/7,6/7],[champs['득점/경기'].mean(),champs['실점/경기'].mean()]])
fig,ax=plt.subplots(figsize=(9,5.5));x=np.arange(2);w=.34;aa=ax.bar(x-w/2,v[:,0],w,color=[RED,BLUE],label='경기당 득점');bb=ax.bar(x+w/2,v[:,1],w,color=[RED,GREY],alpha=.6,label='경기당 실점');ax.bar_label(aa,fmt='%.2f',padding=4);ax.bar_label(bb,fmt='%.2f',padding=4);ax.set_xticks(x,['한국 2002년','6개 우승팀 평균']);ax.set_ylabel('골 / 경기');ax.set_ylim(0,2.4);ax.legend(frameon=False);title(ax,'2002년 한국과 2002~2022년 우승팀 평균 비교','우승팀 각각의 대회별 경기당 값을 계산한 뒤 6개 대회를 동일 비중으로 평균');footer(fig,'출처: 노트북 11~12번 셀 저장 출력 · 서로 다른 집계 기준 비교');fig.tight_layout(rect=(0,.06,1,1));save(fig,'03_korea_2002_vs_champions.png')
# 4 stages
fig,ax=plt.subplots(figsize=(10,5.5));vals=stages['득실차/경기'].to_numpy();bars=ax.barh(stages['구간'],vals,color=[BLUE if x>0 else RED for x in vals]);ax.axvline(0,c='#243347',lw=1);ax.invert_yaxis();ax.set_xlim(-1.2,1.2);ax.set_xlabel('평균 경기당 득실차 (골)');
for b,v in zip(bars,vals):ax.text(v+(.05 if v>0 else -.05),b.get_y()+b.get_height()/2,f'{v:+.2f}',ha='left' if v>0 else 'right',va='center',fontsize=10)
title(ax,'최종 순위 구간별 경기당 득실차','각 팀·대회 기록의 경기당 득점·실점 평균 차이 · 구간은 최종 순위 기준');footer(fig,'근거: 노트북 13·16번 셀 저장 집계 · + 값은 득점 우세');fig.tight_layout(rect=(0,.06,1,1));save(fig,'04_stage_goal_difference.png')
# 5 independent win rate (avoid duplicate former chart)
fig,ax=plt.subplots(figsize=(9,5.5));cc=countries.sort_values('승률(%)',ascending=True);bars=ax.barh(cc['국가'],cc['승률(%)'],color=[RED if n=='대한민국' else BLUE for n in cc['국가']]);ax.bar_label(bars,labels=[f'{n:.1f}%' for n in cc['승률(%)']],padding=4);ax.set_xlim(0,85);ax.set_xlabel('경기 승률 (%) = 승리 수 ÷ 경기 수 × 100');title(ax,'4개 국가의 월드컵 승률 비교','2002~2022년 · 한국 29.17% · 승부차기 기록의 승·무·패 정의는 원본 확인 필요');footer(fig,'출처: 기존 노트북 9번 셀 저장 국가별 집계');fig.tight_layout(rect=(0,.06,1,1));save(fig,'05_country_win_rate.png')
# 6 scatter
fig,ax=plt.subplots(figsize=(9,6));
for r in countries.itertuples():
 c=RED if r.국가=='대한민국' else BLUE
 ax.scatter(r._asdict()['득점/경기'] if False else r.GF/r.Games,r.GA/r.Games,color=c,s=155 if r.국가=='대한민국' else 85,zorder=4)
 ax.annotate(r.국가,(r.GF/r.Games,r.GA/r.Games),xytext=(8,10 if r.국가!='브라질' else -15),textcoords='offset points',fontsize=10,fontweight='bold' if r.국가=='대한민국' else 'normal')
ax.set_xlim(.95,2.38);ax.set_ylim(.60,1.7);ax.set_xlabel('경기당 득점 (오른쪽으로 갈수록 공격 지표 우수)');ax.set_ylabel('경기당 실점 (아래일수록 수비 지표 우수)');ax.grid(alpha=.2);title(ax,'공격·수비 위치 비교 산점도','점 하나는 국가 하나 · 실제로 저장된 비교 국가 4개');footer(fig,'확장용 10개국 데이터의 근거가 확보되면 동일 축에 국가를 추가할 수 있음');fig.tight_layout(rect=(0,.06,1,1));save(fig,'06_country_scatter.png')
# 7 heatmap
corr=ko_recent[['최종순위','승률(%)','경기당 득점','경기당 실점']].corr();fig,ax=plt.subplots(figsize=(8.6,6.5));im=ax.imshow(corr,cmap='RdBu_r',vmin=-1,vmax=1);ax.set_xticks(np.arange(4),corr.columns,rotation=25,ha='right');ax.set_yticks(np.arange(4),corr.index)
for i in range(4):
 for j in range(4):ax.text(j,i,f'{corr.iat[i,j]:.2f}',ha='center',va='center',fontsize=10,color='white' if abs(corr.iat[i,j])>.65 else '#1D2A3B')
fig.colorbar(im,ax=ax,label='피어슨 상관계수 (-1 ~ +1)',shrink=.72);title(ax,'한국의 대회별 성적과 득실의 상관관계','2002~2022년 총 6개 대회, 표본이 작아 해석에 주의');footer(fig,'상관은 인과관계가 아님 · 나쁜 최종 순위일수록 숫자가 큼');fig.tight_layout(rect=(0,.06,1,1));save(fig,'07_korea_correlation_heatmap.png')
# 8 distribution
fig,ax=plt.subplots(figsize=(8.4,5.7));series=[ko_recent['경기당 득점'],ko_recent['경기당 실점']];bp=ax.boxplot(series,patch_artist=True,showfliers=True,medianprops={'color':RED,'linewidth':2},boxprops={'linewidth':1.2});
for patch,color in zip(bp['boxes'],['#C4E7F6','#FFE1B4']):patch.set_facecolor(color)
for x,ss in enumerate(series,1):
 ax.scatter([x+o for o in [-.06,-.036,-.012,.012,.036,.06]],ss,s=34,c=BLUE,zorder=3)
 ax.text(x+.16,float(ss.median()),f'중앙값 {ss.median():.2f}',fontsize=9,va='center',color=RED)
ax.set_xticks([1,2],['경기당 득점','경기당 실점']);ax.set_ylabel('골 / 경기');ax.grid(axis='y',alpha=.18);title(ax,'한국의 경기당 득점·실점 분포','2002~2022년 6개 대회 · 상자=사분위 범위 · 점=각 대회');footer(fig,'중앙값은 6개 대회의 값에서 계산, 전체 24경기 합계로부터 계산한 평균과 다름');fig.tight_layout(rect=(0,.07,1,1));save(fig,'08_korea_goals_boxplot.png')
# audit file
notes={'source':'existing notebook cached outputs only','comparison_countries':countries['Country'].tolist(),'korea_2002_2022_games':24,'no_top10':True}
(OUT/'data'/'PROVENANCE.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2),encoding='utf-8')
print('created png',[(p.name,p.stat().st_size) for p in (OUT/'charts').glob('*.png')]);print('corr',corr.round(2).to_string())
