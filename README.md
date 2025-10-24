# kkutuhelper
[끄투코리아](kkutu.co.kr)에서만 사용 가능
[Korean Notion Docs](https://www.notion.so/Project-Report-KKUTU-HELPER-2216a3ed2d7980dbbdd2fbc6264c9e7f?source=copy_link)

# 사용법
## Chrome
[chrome://extensions/](chrome://extensions) 에서 개발자모드 활성화 -> 압축 해제된 확장프로그램 로드 클릭
chrome/manifest.json 더블클릭
kkutuhelper/overlay 폴더를 터미널에서 연 후

```python overlay.py```

[kkutu.co.kr](kkutu.co.kr)에 접속 후 회원가입/로그인 후 아무 방에나 들어가서 작동하는지 보기
## Firefox
[Firefox Developer Edition](https://www.firefox.com/ko/channel/desktop/developer/) 다운로드
Firefox Developer Edition에서 [about:config](about:config) 접속 -> network.websocket.allowInsecureFromHTTPS를 True로 바꾸기
[about:addons](about:addons)에서 설정 버튼 클릭 -> 파일에서 부가 기능 설치 -> kkutuhelper/firefox/firefox.zip 열기
kkutuhelper/overlay 폴더를 터미널에서 연 후

```python overlay.py```

[kkutu.co.kr](kkutu.co.kr)에 접속 후 회원가입/로그인 후 아무 방에나 들어가서 작동하는지 보기

# 단어장
kkutuhelper/overlay/words.txt에 기본적으로 장문이 저장되어있으며, 아래에 줄바꿈 기준으로 추가하실 수 있습니다.
~~kkutuhelper/overlay/kkutudeadlocked.txt에 막힌 글자가 자동으로 저장됩니다.~~ 개선 예정
