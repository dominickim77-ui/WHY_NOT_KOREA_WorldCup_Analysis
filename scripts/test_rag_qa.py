import unittest
from rag_qa import answer, ROOT, load_instructions
import csv, hashlib
class RagTests(unittest.TestCase):
    def test_instructions_loaded(self):
        instructions = load_instructions()

        self.assertIn("데이터 사용 원칙", instructions)
        self.assertIn("확인 불가", instructions)
        self.assertIn("2002~2022", instructions)
    
    def test_instruction_behavior(self):
        # 1. 근거가 있는 질문
        result = answer("대한민국 2002~2022 승률")

        self.assertEqual(result["status"], "근거 확인")
        self.assertTrue(result["evidence"])
        self.assertIn("F-KOR-", result["answer"])

        # 2. 데이터 범위 밖의 질문
        result = answer("한국 2026 경기 수")

        self.assertEqual(result["status"], "확인 불가")
        self.assertEqual(result["evidence"], [])

        # 3. 데이터로 입증할 수 없는 원인 질문
        result = answer("한국이 전술 때문에 우승하지 못한 원인은?")

        self.assertEqual(result["status"], "확인 불가")
        self.assertEqual(result["evidence"], [])

    def test_supported_and_citations(self):
        result=answer('대한민국 2002~2022 경기 수 승리 득점 실점 승률')
        self.assertEqual([f['value'] for f in result['evidence']],[24,7,28,35,7/24*100])
        for f in result['evidence']:
            path=ROOT/f['source']
            with path.open(encoding='utf-8-sig',newline='') as stream:
                rows=list(csv.DictReader(stream))
            self.assertEqual(float(rows[f['line']-2][f['column']]),f['value'])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),f['sha256'])
            self.assertIn('['+f['id']+']',result['answer'])
    def test_year(self):
        self.assertEqual(answer('한국 2018 순위')['evidence'][0]['value'],19)
    def test_abstentions(self):
        for q in ['한국 2026 경기 수','한국이 전술 때문에 진 원인은?','한국 2018 선수 득점','한국 2002 2006 승률','브라질 승률','한국 순위','한국 점유율']:
            with self.subTest(question=q):
                r=answer(q)
                self.assertEqual(r['status'],'확인 불가')
                self.assertEqual(r['evidence'],[])
if __name__=='__main__': unittest.main(verbosity=2)
