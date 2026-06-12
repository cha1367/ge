# AI 전후 개발자 직종별 고용 생존성 대시보드

## 개요
2021년과 2025년 Stack Overflow Developer Survey 정리표를 기반으로 개발자 직무별 기술 스택 변동성, 연봉, 정규직/고용 비율, 고용 생존성을 시각화하는 Streamlit 대시보드입니다.

## 실행 방법
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 배포 구조
GitHub 저장소에는 아래 파일을 같은 폴더에 둡니다.

```text
app.py
requirements.txt
README.md
stackoverflow_2021_2025_exactname_combined_tables_v2.xlsx
```

## 화면 구성
- 개요
- 간단 요약
- 표1 기술 Top10
- 표2 변동성 분석
- 표3 고용 지표
- 표4 4사분면
- 결론
- 원자료
