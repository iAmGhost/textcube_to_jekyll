import re
from lxml.etree import Element
from lxml import html
import pendulum

from textcube_to_jekyll.models import Comment, Commenter, Content, Post
from textcube_to_jekyll.util import slugify


def parse_archive_org_html(element: Element):
    """archive.org 백업본 html에서 포스트 생성"""
    post_id = int(re.sub(r".+?(\d+?)$", "\g<1>", element.xpath("string(//a[starts-with(@id, 'entry_')]/@id)")))

    assert element.xpath(f"string(//a[@id='trackbackCount{post_id}']/text())").strip() == 'No Trackback'

    comments = []

    for c in element.cssselect(f"div#entry{post_id}CommentList li"):
        name = '익명'
        homepage = ''

        if elems := c.cssselect("span.nickname"):
            name = elems[0].text or '익명'

        if elems := c.cssselect("a.nickname"):
            name = elems[0].text
            homepage = elems[0].get('href')

        commenter = Commenter(
            name=name,
            homepage=homepage,
            openid="",
            ip="",
            id="",
        )

        comment = Comment(
            id=re.sub(r'deleteComment\((\d.+?)\);.*', r'\g<1>', c.cssselect("a[title='수정/삭제하기']")[0].get('onclick')),
            commenter=commenter,
            secret=len(c.cssselect('span.hiddenCommentTag_name')) > 0,
            content=c.cssselect("p.content")[0].text,
            written=pendulum.from_format(c.cssselect("span.command")[0].text.strip(), 'YYYY/MM/DD HH:mm', tz='Asia/Seoul'),
        )

        comments.append(comment)

    dt = pendulum.from_format(element.xpath("string(//li[contains(@class, 'infoDate')]/text())")[4:], "YYYY/MM/DD HH:mm", tz='Asia/Seoul')

    title = element.cssselect("div#container a.entry-title")[0].text

    content_str = '\n'.join([
        html.tostring(child, encoding='utf-8').decode('utf-8')
        for child in element.cssselect("div.article")[0].iterchildren()
    ])

    content_str = re.sub(r'[https:]?\/\/web.archive.org\/web\/.+?\/', '', content_str)

    content_str = re.sub(
        r"""<p.+?class="moreless_fold">.+?onclick="toggleMoreLess\(this, '.+?','(?P<openText>.+?)','(?P<closeText>.+?)'\);.+?<div.+?class="moreless_content".+?>(?P<content>.+?)<\/div>""",
        r"[#M_\g<openText>|\g<closeText>|\g<content>_M#]",
        content_str,
        flags=re.DOTALL,
    )

    content = Content(text=content_str)

    post = Post(
        id=post_id,
        title=title,
        contents=[content],
        published=dt,
        created=dt,
        modified=dt,
        category=element.cssselect("ul.postInfo li.infoCategory a")[0].text,
        slogan=slugify(title, allow_unicode=True),
        comments=comments,
    )

    return post