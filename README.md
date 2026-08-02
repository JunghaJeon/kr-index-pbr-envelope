# 코스피 · 코스닥 PBR 엔벨로프

한국거래소(KRX) 지수 PBR 10년치를 받아, 20일 단순이동평균 ±20% 엔벨로프와 함께 그린다.

- 기간: 2016-08-02 ~ 2026-07-31 (각 2,451거래일)
- 출처: KRX 정보데이터시스템 `MDCSTAT00702` (지수 PER/PBR/배당수익률 추이)

## 파일

| 파일 | 역할 |
| --- | --- |
| `kospi_raw.csv`, `kosdaq_raw.csv` | 수집 원본. `날짜,종가,PBR,PER,배당수익률` (헤더 없음) |
| `build_chart.py` | CSV를 템플릿에 주입해 `pbr_chart.html` 생성. 이동평균·분위를 pandas로 교차검증 출력 |
| `pbr_chart_template.html` | `__DATA__` 플레이스홀더를 가진 차트 템플릿 |
| `pbr_chart.html` | 빌드 결과물 (단일 파일, 외부 의존 없음) |
| `serve.py` | 검증용 정적 서버. `SimpleHTTPRequestHandler`가 빠뜨리는 charset을 붙인다 |
| `recv.py` | 수집 시 브라우저가 보낸 데이터를 파일로 받는 임시 수신 서버 |

## 배포

- GitHub Pages: https://junghajeon.github.io/kr-index-pbr-envelope/ (`main` 브랜치 루트의 `index.html`)
- 임시 공개(로컬을 그대로 노출): `python serve.py 8732` 를 띄운 뒤

  ```bash
  cloudflared tunnel --url http://127.0.0.1:8732
  ```

  터널 주소는 실행할 때마다 바뀌고, `cloudflared` 를 끄면 사라진다. 원본은 `127.0.0.1` 로
  지정한다 — `localhost` 로 두면 IPv6(`::1`) 로 먼저 붙어 연결이 실패할 수 있다.

## 다시 빌드

```bash
python3 -m venv .venv && ./.venv/bin/pip install pandas
./.venv/bin/python build_chart.py
```

## 데이터를 다시 수집하려면

KRX 정보데이터시스템은 **로그인이 필수**다. 데이터 API(`getJsonData.cmd`)는 세션이 없으면
HTTP 400에 본문 `LOGOUT`을 돌려준다. 공개 API가 아닌 웹 내부 엔드포인트라 KRX가 화면을
바꾸면 깨질 수 있다.

수집 방식은 브라우저에 로그인한 뒤, 그 세션에서 API를 호출해 결과를 `recv.py`로 보내는 것이다.

```bash
./.venv/bin/python recv.py   # localhost:8891 에서 대기
```

브라우저(로그인 상태, `data.krx.co.kr` 오리진)에서:

```js
// bld=dbms/MDC/STAT/standard/MDCSTAT00702, searchType=P
// 코스피 indTpCd=1 / 코스닥 indTpCd=2, indTpCd2=001
// 조회 구간은 최대 2년 — 넘기면 INVALIDPERIOD2
fetch('http://localhost:8891/', { method: 'POST', headers: { 'x-name': 'kospi_raw.csv' }, body: csv });
```

`https` 페이지에서 `http://localhost`로 보내는 요청이라 Private Network Access 대상이다.
`recv.py`가 preflight에 `Access-Control-Allow-Private-Network: true`를 돌려주도록 돼 있다.

## 주의

KRX는 미산출 구간의 PER/PBR을 **0으로 채워** 내려준다. `build_chart.py`가 결측으로 되돌린다.
(이번 10년 구간에는 해당 값이 없었다. PBR 유효 시작은 KOSPI 2002-04-23, KOSDAQ 2005-10-04.)
