# 수정 기사 팩트체크

2002~2022 FIFA 남자 월드컵 본선 6개 대회 · 384경기 · 팀·대회 기록 192건

| 대상 | PASS | FAIL | HOLD | REVIEW | 합계 |
|---|---:|---:|---:|---:|---:|
| 원문 전체 | 32 | 4 | 4 | 1 | 41 |
| 수정본 전체 | 37 | 0 | 0 | 0 | 37 |
| article.revised.md | 14 | 0 | 0 | 0 | 14 |
| WHY_NOT_KOREA_Final_Article.revised.md | 23 | 0 | 0 | 0 | 23 |

수정본 집계는 본문에 남은 검증 대상 문장을 센다. 원문의 HOLD는 아래에 별도로 추적했다.
동일한 통계 문장은 기존 팩트체크를 현재 CSV로 재실행했다. 바뀐 문장의 수치와 집단 명칭은 수정본을 읽어 새 검사에 연결했다.

## 수정과 보류 내역

- 아르헨티나 18승, 31경기, 승률 58.1%. 승부차기 승리 3건을 더하면 21승으로 기존 20승은 재현되지 않는다. 근거 M-ARG-2002–2022 및 S-ARG-legacy.
- 16강 48건과 8강 24건은 해당 단계에서 탈락한 팀·대회 기록이다. 동일 집단으로 평균을 재계산했다. 근거 M-stages 및 FS-최종 성적별 비교.
- 원문 1행 (REVIEW) — 관찰 가능한 국가 간 비교를 제목으로 삼았다.
- 원문 25행 (HOLD) — 대회별 1~4위만 있는 순위 CSV로는 192개 기록의 상관계수를 재계산할 수 없다.
- 원문 25행 (HOLD) — 상관계수 방향을 확인하는 데도 전체 순위가 필요하다.
- 원문 29행 (HOLD) — 기존 Kaggle 원본 URL과 버전은 확인 불가다. 수정본 재검증에 사용한 출처를 표기했다.
- 원문 32행 (HOLD) — FIFA 공식 자료와 직접 대조했는지는 확인 불가다.

## 출처 대조

- 로컬 경기 자료 2종의 날짜·팀·스코어 384건이 모두 일치했다. 근거 M-all 및 I-384.
- 공개 원본과 로컬 경기·순위·대회 CSV는 줄바꿈 정규화 후 대조했다. 보조 자료는 원본의 기간·대회·열을 동일하게 추려 대조했다.

| CSV | 공개 원본 대조 |
|---|---|
| matches.csv | 일치 · [공개 원본](https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/matches.csv) |
| tournament_standings.csv | 일치 · [공개 원본](https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/tournament_standings.csv) |
| tournaments.csv | 일치 · [공개 원본](https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/tournaments.csv) |
| independent_scores.csv | 일치 · [공개 원본](https://raw.githubusercontent.com/martj42/international_results/master/results.csv) |

## RAG 재실행

한국의 기간 합계와 2002년 기록은 RAG 결과를 경기·순위 CSV 재계산 값에 대조했다. RAG가 지원하지 않는 아르헨티나와 성적 단계는 CSV 팩트체크로 검증했다.

- 2002~2022 대한민국 경기 수, 승리, 득점, 실점, 승률은? — 근거 확인 · F-KOR-2002–2022-games, F-KOR-2002–2022-wins, F-KOR-2002–2022-gf, F-KOR-2002–2022-ga, F-KOR-2002–2022-win_rate
- 2002 대한민국 경기 수, 승리, 득점, 실점, 최종 순위는? — 근거 확인 · F-KOR-2002-games, F-KOR-2002-wins, F-KOR-2002-gf, F-KOR-2002-ga, F-KOR-2002-position
- 2002~2022 아르헨티나 승률과 승수는? — 확인 불가 · 확인 불가: 현재 지원 대상은 대한민국입니다.
- 16강·8강 탈락 팀의 경기당 득점과 실점은? — 확인 불가 · 확인 불가: 현재 지원 대상은 대한민국입니다.
- 대한민국 월드컵 전체 순위와 득점·실점의 상관관계는? — 확인 불가 · 확인 불가: 최종 순위에는 하나의 대회 연도가 필요합니다.
- 한국은 왜 월드컵에서 우승하지 못했나? — 확인 불가 · 확인 불가: 전술·원인·예측을 뒷받침할 근거가 없습니다.
- 기존 Kaggle 원본 URL과 버전 및 FIFA 공식 자료 대조 여부는? — 확인 불가 · 확인 불가: 현재 지원 대상은 대한민국입니다.

## 수정본 문장별 판정

| 파일·줄 | 판정 | 문장 | 근거 ID |
|---|---|---|---|
| article.revised.md:1 | PASS | # 대한민국의 월드컵 24경기, 7승과 35실점 | F-KOR-2002–2022-ga, F-KOR-2002–2022-games, F-KOR-2002–2022-wins, FS-국가별 비교, M-KOR-2002–2022, S-country_summary-KOR-None-ga, S-country_summary-KOR-None-games, S-country_summary-KOR-None-wins, T-period |
| article.revised.md:3 | PASS | 2002년부터 2022년까지 남자 월드컵 본선 6개 대회에서 대한민국은 24경기 중 7경기를 이겼다. | F-KOR-2002–2022-games, F-KOR-2002–2022-wins, FS-국가별 비교, M-KOR-2002–2022, S-country_summary-KOR-None-games, S-country_summary-KOR-None-wins, T-period |
| article.revised.md:3 | PASS | 28골을 넣고 35골을 내줬다. | F-KOR-2002–2022-ga, F-KOR-2002–2022-gf, FS-국가별 비교, M-KOR-2002–2022, S-country_summary-KOR-None-ga, S-country_summary-KOR-None-gf |
| article.revised.md:3 | PASS | 승률은 29.2%였다. | F-KOR-2002–2022-win_rate, FS-국가별 비교, M-KOR-2002–2022, S-country_summary-KOR-None-win_rate |
| article.revised.md:3 | PASS | 연장 종료 때 동점인 경기는 무승부로 집계했다. | M-all |
| article.revised.md:5 | PASS | 6개 대회의 누적 승수 상위 10개국과 비교하면 대한민국은 경기당 득점(1.17골)이 가장 적고 실점(1.46골)이 가장 많았다. | FS-국가별 비교, M-KOR-2002–2022, M-all, S-country_summary-KOR-None-conceded, S-country_summary-KOR-None-scored, S-top10, T-period |
| article.revised.md:5 | PASS | 독일과 브라질은 각각 23승을 거뒀다. | FS-국가별 비교, M-BRA-2002–2022, M-DEU-2002–2022, S-country_summary-BRA-None-wins, S-country_summary-DEU-None-wins |
| article.revised.md:5 | PASS | 16승을 거둔 네덜란드는 23경기를 치러, 비교 대상 중 승률이 가장 높았다(69.6%). | M-NLD-2002–2022, M-all, S-country_summary-NLD-None-games, S-country_summary-NLD-None-win_rate, S-country_summary-NLD-None-wins, S-top10, T-period |
| article.revised.md:7 | PASS | 대한민국의 최고 성적은 2002년 4위였다. | FS-대한민국 대회별 성적, R-KOR, R-KOR-annual |
| article.revised.md:7 | PASS | 당시 경기당 0.86골을 내줬다. | FS-대한민국 대회별 성적, M-KOR-2002, S-korea_summary-KOR-2002-conceded |
| article.revised.md:7 | PASS | 대한민국의 6개 대회 합산 평균(1.46골)보다 낮았고, 같은 기간 6개 우승팀 평균(0.62골)보다는 높았다. | FS-국가별 비교, M-KOR-2002, M-KOR-2002–2022, M-champions, R-champions, S-country_summary-KOR-None-conceded |
| article.revised.md:7 | PASS | 2002년 대한민국은 경기당 1.14골을 넣었고, 우승팀 평균은 2.02골이었다. | FS-대한민국 대회별 성적, M-KOR-2002, M-champions, R-champions, S-korea_summary-KOR-2002-scored |
| article.revised.md:9 | PASS | 6개 대회의 기록으로 우승 가능성이나 특정 전략의 효과를 추정하기는 어렵다. | T-period |
| article.revised.md:11 | PASS | 자료는 Fjelstul World Cup Database의 본선 경기 기록이며 집계 방식과 교차 검증 내역은 [README](../../README.md)에 있다. | M-all |
| WHY_NOT_KOREA_Final_Article.revised.md:3 | PASS | ## 2002~2022년 24경기에서 7승…비교 대상 국가보다 경기당 득점은 적고 실점은 많았다 | F-KOR-2002–2022-games, F-KOR-2002–2022-wins, FS-국가별 비교, M-KOR-2002–2022, M-all, S-country_summary-KOR-None-games, S-country_summary-KOR-None-wins, T-period |
| WHY_NOT_KOREA_Final_Article.revised.md:7 | PASS | ### 비교 대상 국가보다 낮은 승률 | M-all, T-period |
| WHY_NOT_KOREA_Final_Article.revised.md:9 | PASS | 2002~2022년 월드컵에서 한국은 24경기 중 7승을 거뒀다. | F-KOR-2002–2022-games, F-KOR-2002–2022-wins, FS-국가별 비교, M-KOR-2002–2022, S-country_summary-KOR-None-games, S-country_summary-KOR-None-wins, T-period |
| WHY_NOT_KOREA_Final_Article.revised.md:9 | PASS | 28골을 넣고 35골을 내줬으며, 경기당 득점은 1.17골, 실점은 1.46골이다. | F-KOR-2002–2022-ga, F-KOR-2002–2022-gf, FS-국가별 비교, M-KOR-2002–2022, S-country_summary-KOR-None-conceded, S-country_summary-KOR-None-ga, S-country_summary-KOR-None-gf, S-country_summary-KOR-None-scored |
| WHY_NOT_KOREA_Final_Article.revised.md:11 | PASS | 비교 대상 국가의 경기당 득점은 아르헨티나 1.68골, 브라질 1.88골, 독일 2.06골이다. | FS-국가별 비교, M-ARG-2002–2022, M-BRA-2002–2022, M-DEU-2002–2022, S-country_summary-ARG-None-scored, S-country_summary-BRA-None-scored, S-country_summary-DEU-None-scored |
| WHY_NOT_KOREA_Final_Article.revised.md:11 | PASS | 경기당 실점은 아르헨티나 1.03골, 브라질 0.88골, 독일 0.79골이었다. | FS-국가별 비교, M-ARG-2002–2022, M-BRA-2002–2022, M-DEU-2002–2022, S-country_summary-ARG-None-conceded, S-country_summary-BRA-None-conceded, S-country_summary-DEU-None-conceded |
| WHY_NOT_KOREA_Final_Article.revised.md:11 | PASS | 승률은 브라질과 독일이 각각 67.6%, 아르헨티나가 58.1%였고, 한국은 29.2%였다. | F-KOR-2002–2022-win_rate, FS-국가별 비교, M-ARG-2002–2022, M-BRA-2002–2022, M-DEU-2002–2022, M-KOR-2002–2022, S-ARG-legacy, S-country_summary-ARG-None-win_rate, S-country_summary-BRA-None-win_rate, S-country_summary-DEU-None-win_rate, S-country_summary-KOR-None-win_rate |
| WHY_NOT_KOREA_Final_Article.revised.md:11 | PASS | 브라질과 독일은 각각 34경기에서 23승, 아르헨티나는 31경기에서 18승을 기록했다. | FS-국가별 비교, M-ARG-2002–2022, M-BRA-2002–2022, M-DEU-2002–2022, S-ARG-legacy, S-country_summary-ARG-None-games, S-country_summary-ARG-None-wins, S-country_summary-BRA-None-games, S-country_summary-BRA-None-wins, S-country_summary-DEU-None-games, S-country_summary-DEU-None-wins |
| WHY_NOT_KOREA_Final_Article.revised.md:13 | PASS | 국가별 경기 수가 다르므로 총득점이나 총승수만 비교하기보다 경기당 기록과 승률을 함께 볼 필요가 있다. | M-all |
| WHY_NOT_KOREA_Final_Article.revised.md:13 | PASS | 이 수치에서는 한국이 비교 대상 국가들보다 경기당 득점은 적고 실점은 많았다. | M-all, T-period |
| WHY_NOT_KOREA_Final_Article.revised.md:13 | PASS | 승수는 승부차기 결과를 별도 승리로 계산하지 않은 데이터셋 기준이다. | M-all |
| WHY_NOT_KOREA_Final_Article.revised.md:15 | PASS | ### 2002년은 한국의 최고 성적 | FS-대한민국 대회별 성적, R-KOR, R-KOR-annual |
| WHY_NOT_KOREA_Final_Article.revised.md:17 | PASS | 한국의 분석 기간 중 최고 성적은 2002년 4위다. | FS-대한민국 대회별 성적, R-KOR, R-KOR-annual |
| WHY_NOT_KOREA_Final_Article.revised.md:17 | PASS | 당시 7경기에서 3승 2무 2패를 기록했고, 8득점 6실점을 했다. | F-KOR-2002-ga, F-KOR-2002-games, F-KOR-2002-gf, F-KOR-2002-wins, FS-대한민국 대회별 성적, M-KOR-2002, S-korea_summary-KOR-2002-draws, S-korea_summary-KOR-2002-ga, S-korea_summary-KOR-2002-games, S-korea_summary-KOR-2002-gf, S-korea_summary-KOR-2002-losses, S-korea_summary-KOR-2002-wins |
| WHY_NOT_KOREA_Final_Article.revised.md:17 | PASS | 경기당 득점은 1.14골, 실점은 0.86골이었다. | FS-대한민국 대회별 성적, M-KOR-2002, S-korea_summary-KOR-2002-conceded, S-korea_summary-KOR-2002-scored |
| WHY_NOT_KOREA_Final_Article.revised.md:19 | PASS | 2002년 한국의 경기당 득점은 2002~2022년 한국 전체 평균인 1.17골보다 낮았다. | FS-국가별 비교, M-KOR-2002, M-KOR-2002–2022, S-country_summary-KOR-None-scored |
| WHY_NOT_KOREA_Final_Article.revised.md:19 | PASS | 경기당 실점 0.86골도 같은 기간 한국 전체 평균인 1.46골과 비교하면 낮은 수치다. | FS-국가별 비교, FS-대한민국 대회별 성적, M-KOR-2002, M-KOR-2002–2022, S-country_summary-KOR-None-conceded, S-korea_summary-KOR-2002-conceded |
| WHY_NOT_KOREA_Final_Article.revised.md:19 | PASS | 한 차례의 4강 진출 기록만으로 이후 대회의 성적이나 우승 가능성을 설명할 수는 없다. | R-KOR-annual |
| WHY_NOT_KOREA_Final_Article.revised.md:23 | PASS | 최종 성적별 팀·대회 기록은 조별리그 탈락 96건, 16강 탈락 48건, 8강 탈락 24건, 4강 진출 24건이다. | FS-최종 성적별 비교, M-stages |
| WHY_NOT_KOREA_Final_Article.revised.md:23 | PASS | 조별리그 탈락 팀은 경기당 0.826득점·1.694실점, 8강 탈락 팀은 1.642득점·0.808실점, 16강 탈락 팀은 1.240득점·1.255실점, 4강 진출 팀은 1.738득점·0.827실점이었다. | FS-최종 성적별 비교, M-stages |
| WHY_NOT_KOREA_Final_Article.revised.md:27 | PASS | **재검증 자료** — Fjelstul World Cup Database의 본선 경기·순위 CSV | M-all, P-matches, R-podium |
| WHY_NOT_KOREA_Final_Article.revised.md:28 | PASS | **분석 기간:** 2002~2022년 | T-period |
| WHY_NOT_KOREA_Final_Article.revised.md:30 | PASS | 경기별 스코어를 팀·대회별로 집계했으며, 상대팀 수준과 전술은 분석에 반영하지 않았다. | I-384, M-stages |

[문장 비교표](sentence_comparison.md) · [계산식·CSV 행과 열·근거 SHA-256](verification.json) · [자동 테스트 로그](test_results.txt)
