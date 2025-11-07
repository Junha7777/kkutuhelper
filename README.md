__**정지 먹어도 내 책임 아님**__

개발 능력 향상을 위해 개발했습니다.

# kkutuhelper
[끄투코리아](kkutu.co.kr)에서만 사용 가능

[Korean Notion Docs](https://www.notion.so/Project-Report-KKUTU-HELPER-2216a3ed2d7980dbbdd2fbc6264c9e7f?source=copy_link)


# 사용법
## Chrome
[chrome://extensions/](chrome://extensions) 에서 개발자모드 활성화 -> 압축 해제된 확장프로그램 로드 클릭

chrome/manifest.json 더블클릭

kkutuhelper/overlay 폴더를 터미널에서 연 후

```python overlay.py```

[kkutu.co.kr](kkutu.co.kr)에 접속 후 아무 방에나 작동하는지 확인
## Firefox
[about:config](about:config) 접속 -> network.websocket.allowInsecureFromHTTPS를 True로 바꾸기

[about:debugging#/runtime/this-firefox](about:debugging#/runtime/this-firefox)에서 '임시 부가 기능 로드...' 클릭 -> kkutuhelper/firefox/firefox.zip 열기

kkutuhelper/overlay 폴더를 터미널에서 연 후

```python overlay.py```

[kkutu.co.kr](kkutu.co.kr)에 접속 후 아무 방에나 작동하는지 확인

# 단어장
kkutuhelper/overlay/words.txt에 기본적으로 한국어 끝말잇기 + 어인정용 장문이 저장되어있으며, 아래에 줄바꿈 기준으로 추가하실 수 있습니다.

kkutuhelper/overlay/kkutudeadlocked.txt에 막힌 글자가 자동으로 저장됩니다. // TODO: 개선 필요

# TODO
미션 기반 단어 추천
끄3, 핑끄 등 다른 프리서버 지원하기
