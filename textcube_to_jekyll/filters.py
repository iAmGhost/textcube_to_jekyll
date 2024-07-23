import json
import re

from datetime import datetime
import pendulum

from textcube_to_jekyll.models import Blog, Post, TTMLAttachmentTag
from textcube_to_jekyll.const import TTML_ATTACHMENT_REGEX


def encode_json(value: str):
    return json.dumps(value, ensure_ascii=False)


def date_format(value: datetime, format: str):
    return pendulum.instance(value).format(format)


def convert_ttml(content: str, blog: Blog, post: Post):
    from textcube_to_jekyll.template import get_template

    # 중괄호
    content = content.replace("{{", "&#123;&#123;")
    content = content.replace("}}", "&#125;&#125;")

    # 사이트 URL 하드링크 수정
    site_urls = [blog.site_url, blog.get_alt_site_url()]

    for site_url in site_urls:
        content = re.sub(fr"{site_url}/", r"/tt/", content)

    # More/Less 태그
    moreless_template = get_template('ttml/moreless.html')

    def moreless_sub(match: re.Match):
        return moreless_template.render(
            open_text=match.group('open_text'),
            close_text=match.group('close_text'),
            content=match.group('content'),
        )

    content = re.sub(r'\[#M_(?P<open_text>.+?)\|(?P<close_text>.+?)\|(?P<content>.+?)_M#\]', moreless_sub, content, flags=re.DOTALL)

    # 첨부파일
    attachment_template = get_template('ttml/attachment.html')

    def attachment_sub(match: re.Match):
        return attachment_template.render(
            attachments=TTMLAttachmentTag.parse_from_content(match.group(0))
        )

    content = re.sub(TTML_ATTACHMENT_REGEX, attachment_sub, content, flags=re.DOTALL)

    # 마법진
    def magicalcircle_sub(match: re.Match):
        content = match.group(1)
        return content.replace("[", "<").replace("]", ">")

    content = re.sub(r'\[magicalcircle\](.+?)\[\/magicalcircle\]', magicalcircle_sub, content, flags=re.DOTALL)

    # footnote
    footnote_template = get_template('ttml/footnote.html')

    def footnote_sub(match: re.Match):
        return footnote_template.render(
            content=match.group('content'),
        )

    content = re.sub(r'\[footnote\](?P<content>.+?)\[\/footnote\]', footnote_sub, content, flags=re.DOTALL)
    return content
