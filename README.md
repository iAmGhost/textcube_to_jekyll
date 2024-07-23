# textcube_to_jekyll

Textcube 백업 및 Archive.org 포스트를 jekyll 포스트로 변환하는 툴 입니다.

https://blog.pig-min.com 만드는데 사용했습니다.

```bash
poetry install
poetry run textcube_to_jekyll --help
```

more/less, 각주 태그 지원을 위해 테마에 아래 내용을 추가해주세요.

```html
<link rel="stylesheet" href="{{ "/assets/ttml.css" | relative_url }}">
<script src="{{ "/assets/ttml.js" | relative_url }}"></script>
```