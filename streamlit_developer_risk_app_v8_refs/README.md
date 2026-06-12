# AI 전후 개발자 직종별 고용 생존성 대시보드

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 포함 데이터
- Stack Overflow Developer Survey 2021/2025 정리 엑셀: 메인 계산 데이터
- O*NET Software Skills 요약: 직업별 요구 기술 참고자료
- Kaggle LinkedIn Jobs & Skills 2024 요약: 채용공고 기술스택 참고자료
- 국내 직종별 SW 전문인력 요약: 국내 고용시장 참고자료

## 주의
LinkedIn 보조자료는 `job_link`와 `job_skills`만 사용했기 때문에 직무명은 URL 키워드로 추정했다. 핵심 계산에는 반영하지 않고 참고자료로만 사용한다.
