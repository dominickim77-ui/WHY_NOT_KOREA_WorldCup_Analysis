from pathlib import Path
import difflib
import json
import os
import re
import streamlit as st

ROOT = Path(os.environ.get('WORLDCUP_PROJECT', Path(__file__).resolve().parent))
REV = ROOT / 'reports/article_revision_2026-11-11'
st.set_page_config(page_title='WHY NOT KOREA | 기사 검토', page_icon='📰', layout='wide')
st.markdown('''<style>
.stApp {background:#faf9f6;color:#202731}
.block-container {max-width:1380px;padding-top:2.5rem}
h1,h2,h3 {font-family:Georgia,'Malgun Gothic',serif;letter-spacing:-.035em}
h1 {border-top:5px solid #183d50;padding-top:22px!important}
[data-testid="stSidebar"] {background:#eeede7}
[data-testid="stMarkdownContainer"] p {line-height:1.9}
[data-testid="stMetric"] {background:#fff;border-top:3px solid #a96039;padding:16px}
</style>''', unsafe_allow_html=True)

def read(path):
    try:
        return path.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError) as exc:
        st.error(f'자료를 읽지 못했습니다: {path.name} · {exc}')
        return ''

def render(path):
    content = read(path)
    # Local images are served by Streamlit; local document links open in the source viewer.
    def link(match):
        label, dest = match.groups()
        if re.match(r'^(https?://|mailto:|#)', dest):
            return match.group(0)
        target = (path.parent / dest).resolve()
        try:
            rel = target.relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            return label
        from urllib.parse import quote
        return f'[{label}](?doc={quote(rel)})'
    for part in re.split(r'(!\[[^\]]*\]\([^)]+\))', content):
        img = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', part)
        if img:
            target = (path.parent / img[2]).resolve()
            if target.is_relative_to(ROOT.resolve()) and target.is_file():
                st.image(str(target), caption=img[1], width='stretch')
            else:
                st.caption(f'이미지 확인 필요: {img[2]}')
        else:
            st.markdown(re.sub(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)', link, part))

st.caption('DATA JOURNALISM / EDITORIAL REVIEW / 2026.11.11')
st.title('WHY NOT KOREA')
st.markdown('**월드컵 기록으로 읽는 한국 축구** · 기사와 근거를 함께 검토하는 편집 데스크')
st.sidebar.title('기사 검토 데스크')
article = st.sidebar.radio('기사 선택', ['기사 1 · 대한민국의 월드컵 기록', '기사 2 · 국가별 득점과 실점 비교'])
filename = 'article.md' if article.startswith('기사 1') else 'WHY_NOT_KOREA_Final_Article.md'
original = ROOT / filename
revised = REV / filename.replace('.md', '.revised.md')
st.sidebar.caption('원본 자료를 읽기만 합니다. 화면에서 기사를 수정하거나 검증을 재실행하지 않습니다.')
st.sidebar.caption(str(ROOT))
raw = read(REV / 'verification.json')
try:
    verification = json.loads(raw) if raw else {}
except ValueError:
    st.error('검증 JSON 형식을 확인해 주세요.')
    verification = {}
st.caption(verification.get('scope', '2002–2022 FIFA 남자 월드컵'))
tabs = st.tabs(['기사 읽기', '수정 전후 비교', '분석 그래프 8개', '팩트체크', '보고서 · 출처'])
with tabs[0]:
    version = st.radio('읽을 버전', ['수정본', '기존 기사'], horizontal=True)
    chosen = revised if version == '수정본' else original
    st.caption(f'{version} · {chosen.relative_to(ROOT).as_posix()}')
    render(chosen)
    st.download_button('Markdown 다운로드', read(chosen), file_name=chosen.name, mime='text/markdown')
with tabs[1]:
    left, right = st.columns(2, gap='large')
    with left:
        st.subheader('기존 기사')
        render(original)
    with right:
        st.subheader('수정본')
        render(revised)
    with st.expander('추가·삭제된 문장 보기', expanded=True):
        diff = '\n'.join(difflib.unified_diff(read(original).splitlines(), read(revised).splitlines(), fromfile='기존 기사', tofile='수정본', lineterm=''))
        st.code(diff or '변경 사항이 없습니다.', language='diff')
    st.subheader('수정 이유와 근거')
    for change in verification.get('changes', []):
        if change.get('original_article') == filename:
            with st.expander(f"원문 {change.get('original_line')}행 · {change.get('reason', '')}"):
                st.write('이전:', change.get('before') or '없음')
                st.write('이후:', change.get('after') or '본문에서 제외')
                st.caption('근거: ' + ', '.join(change.get('evidence_ids', [])))
with tabs[2]:
    st.subheader('기록을 읽는 여덟 가지 시선')
    st.caption('README에 지정된 분석 그래프 8개입니다. 기존 이미지와 해석을 그대로 표시합니다.')
    sections = re.split(r'(?m)^### ', read(ROOT / 'README.md'))
    chart_sections = [s for s in sections if re.search(r'!\[[^\]]*\]\(charts/', s)]
    cols = st.columns(2, gap='large')
    for i, section in enumerate(chart_sections[:8]):
        match = re.search(r'!\[([^\]]*)\]\((charts/[^)]+)\)', section)
        with cols[i % 2]:
            st.subheader(section.splitlines()[0])
            chart = ROOT / match[2]
            if chart.exists():
                st.image(str(chart), caption=match[1], width='stretch')
            else:
                st.error(f'그래프 없음: {match[2]}')
            notes = '\n'.join(line for line in section.splitlines() if line.startswith('- **'))
            st.markdown(notes)
    if len(chart_sections) != 8:
        st.warning(f'README에서 확인한 그래프 수: {len(chart_sections)}')
with tabs[3]:
    st.subheader('수정 전후 검증 결과')
    st.caption('두 기사 전체 집계 · 저장된 verification.json 기준이며 새 검증 결과가 아닙니다.')
    for col, status, label in zip(st.columns(4), ['PASS','FAIL','HOLD','REVIEW'], ['통과','불일치','보류','검토 필요']):
        before = verification.get('original_counts', {}).get(status, '—')
        after = verification.get('revised_counts', {}).get(status, '—')
        col.metric(f'{label} ({status})', f'{after}건', delta=None)
        col.caption(f'기존 {before}건 → 수정본 {after}건')
    st.info('원문 검증 대상 41건과 수정본 37건은 서로 다른 집계입니다. 본문에서 제외된 주장도 있어, 보류 0건이 모든 의문이 해결됐다는 뜻은 아닙니다.')
    for key, label in [('unresolved_original_claims','여전히 확인되지 않은 원문 주장'), ('excluded','수정본에서 제외한 내용')]:
        with st.expander(label, expanded=True):
            st.json(verification.get(key, []), expanded=1)
    report = st.radio('상세 판정 보고서', ['수정 후', '수정 전'], horizontal=True)
    render(REV / 'factcheck_report.md' if report == '수정 후' else ROOT / 'reports/article_factcheck.md')
with tabs[4]:
    documents = [REV/'factcheck_report.md', REV/'sentence_comparison.md', ROOT/'docs/DATA_AND_FACTCHECK.md', ROOT/'data/README.md', ROOT/'README.md', ROOT/'data/provenance.json', REV/'verification.json', ROOT/'reports/article_factcheck.json']
    selected = st.selectbox('보고서 또는 출처 자료', documents, format_func=lambda p: p.relative_to(ROOT).as_posix())
    requested = st.query_params.get('doc')
    if requested:
        candidate = (ROOT / requested).resolve()
        if candidate.is_relative_to(ROOT.resolve()) and candidate.is_file() and candidate.suffix in ('.md','.json','.csv'):
            selected = candidate
            st.caption(f'기사에서 연결된 자료: {requested}')
            if st.button('연결 자료 닫기'):
                st.query_params.clear()
                st.rerun()
    if selected.suffix == '.md':
        render(selected)
    elif selected.suffix == '.json':
        try:
            st.json(json.loads(read(selected)), expanded=1)
        except ValueError:
            st.error('JSON 형식을 읽을 수 없습니다.')
    else:
        st.code(read(selected))
st.divider()
st.caption('WHY NOT KOREA · 로컬 기사 검토용 / 원본·CSV·그래프·검증 자료 읽기 전용')
