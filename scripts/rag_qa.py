"""Structured retrieval with extractive answers; no LLM or network required."""
import csv
import hashlib
import json
import re
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# RAG 지침 파일 위치
INSTRUCTIONS_PATH = ROOT / "config" / "RAG_INSTRUCTIONS.md"

def load_instructions():
    if not INSTRUCTIONS_PATH.is_file():
        raise FileNotFoundError(
            f"RAG 지침 파일을 찾을 수 없습니다: {INSTRUCTIONS_PATH}"
        )

    return INSTRUCTIONS_PATH.read_text(encoding="utf-8")

METRICS = {'games': ('경기 수', ['경기 수','경기수','몇 경기','games']), 'wins': ('승리', ['승리','승수','몇 승','wins']), 'gf': ('득점', ['득점','goals for']), 'ga': ('실점', ['실점','goals against']), 'win_rate': ('승률', ['승률','win rate']), 'position': ('최종 순위', ['순위','몇 위','position'])}
def retrieve(question):
    q = question.lower()
    if not any(x in q for x in ['대한민국','한국','korea']):
        return [], '현재 지원 대상은 대한민국입니다.'
    if any(x in q for x in ['왜','원인','전술','선수','예측','우승 가능','why','tactic','cause']):
        return [], '전술·원인·예측을 뒷받침할 근거가 없습니다.'
    years = [int(y) for y in re.findall(r'(?<![0-9])[12][0-9]{3}(?![0-9])', q)]
    allowed = [2002,2006,2010,2014,2018,2022]
    if any(y not in allowed for y in years):
        return [], '자료 범위는 2002·2006·2010·2014·2018·2022년입니다.'
    if len(years)>1 and not (years == [2002,2022] and re.search(r'2002\s*[-–~부터]+\s*2022',q)):
        return [], '복수 연도 비교는 지원하지 않습니다. 한 대회씩 질문하세요.'
    metrics = [k for k,(_,terms) in METRICS.items() if any(t in q for t in terms)]
    if not metrics:
        return [], '지원 항목: 경기 수, 승리, 득점, 실점, 승률, 대회별 순위.'
    yearly = len(years)==1
    if 'position' in metrics and not yearly:
        return [], '최종 순위에는 하나의 대회 연도가 필요합니다.'
    path = ROOT/'data'/('korea_summary.csv' if yearly else 'country_summary.csv')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(encoding='utf-8-sig',newline='') as f:
        rows = list(csv.DictReader(f))
    found = [(i,r) for i,r in enumerate(rows,2) if r['code']=='KOR' and (not yearly or int(r['year'])==years[0])]
    if len(found)!=1:
        return [], '유일한 근거 행을 확인할 수 없습니다.'
    line,row = found[0]
    period = str(years[0]) if yearly else '2002–2022'
    facts = []
    for key in metrics:
        value = float(row[key])
        if key=='win_rate':
            if abs(value - int(row['wins'])/int(row['games'])*100)>1e-8:
                return [], '승률 계산과 원본 값이 일치하지 않습니다.'
        facts.append({'id':f'F-KOR-{period}-{key}', 'metric':METRICS[key][0], 'value':value, 'unit':'%' if key=='win_rate' else '위' if key=='position' else '경기' if key=='games' else '승' if key=='wins' else '골', 'period':period, 'source':str(path.relative_to(ROOT)).replace(chr(92),'/'), 'line':line,'column':key,'sha256':digest})
    return facts, ''
def answer(question):
    instructions = load_instructions()
    facts, reason = retrieve(question)
    if not facts:
        return {'question':question,'status':'확인 불가','answer':'확인 불가: '+reason,'evidence':[]}
    sentences = [f"대한민국 {f['period']} {f['metric']}: {f['value']:.1f}{f['unit']} [{f['id']}]" for f in facts]
    return {'question':question,'status':'근거 확인','answer':'\n'.join(sentences),'evidence':facts}
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('question')
    print(json.dumps(answer(parser.parse_args().question),ensure_ascii=False,indent=2))
