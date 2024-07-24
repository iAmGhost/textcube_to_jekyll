# textcube_to_jekyll

Textcube 백업 및 Archive.org 포스트를 Jekyll 포스트로 변환하는 툴입니다.

https://blog.pig-min.com 만드는데 사용했습니다.

```bash
poetry install
# help를 참조하여 백업 파일/출력 경로 지정 후 실행
poetry run textcube_to_jekyll --help
```

백업본의 more/less, 각주 표시를 지원합니다. 표시를 위해 Jekyll 테마에 아래 내용을 추가해주세요.

```html
<link rel="stylesheet" href="{{ "/assets/ttml.css" | relative_url }}">
<script src="{{ "/assets/ttml.js" | relative_url }}"></script>
```