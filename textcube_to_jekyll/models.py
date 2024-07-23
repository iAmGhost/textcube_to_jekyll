import re
from datetime import datetime

from more_itertools import grouper

from lxml.etree import Element
from pydantic import BaseModel, Field, model_validator
import pendulum
import purl

from textcube_to_jekyll.const import TTML_ATTACHMENT_REGEX


class TTMLAttachmentTag(BaseModel):
    seq: int
    filename: str
    attributes: str

    @classmethod
    def parse_from_content(cls, text: str) -> list['TTMLAttachmentTag']:
        result = []

        for match in re.finditer(TTML_ATTACHMENT_REGEX, text):
            seq = int(match.group('seq'))
            content = match.group('content')

            for _, filename, attribute, in grouper(content.split('|')[:-1], 3, incomplete='strict'):
                result.append(cls(seq=seq, filename=filename, attributes=attribute))

        return result


class Attachment(BaseModel):
    name: str
    label: str
    enclosure: bool
    attached: datetime
    downloads: int
    content: str
    mime: str
    size: int
    width: int
    height: int

    @classmethod
    def from_etree(cls, element: Element):
        instance = cls(
            name=element.xpath("string(./name/text())"),
            label=element.xpath("string(./label/text())"),
            enclosure=bool(element.xpath("boolean(./enclosure/text())")),
            attached=pendulum.from_timestamp(element.xpath("number(./attached/text())"), tz='Asia/Seoul'),
            downloads=int(element.xpath("number(./downloads/text())")),
            content=element.xpath("string(./content/text())"),
            mime=element.xpath("string(./@mime)"),
            size=int(element.xpath("number(./@size)")),
            width=int(element.xpath("number(./@width)")),
            height=int(element.xpath("number(./@height)")),
        )

        return instance


class Content(BaseModel):
    formatter: str = ""
    editor: str = ""
    text: str

    @classmethod
    def from_etree(cls, element: Element):
        instance = cls(
            formatter=element.xpath("string(./@formatter)"),
            editor=element.xpath("string(./@editor)"),
            text=element.xpath("string(./text())"),
        )

        return instance


class Trackback(BaseModel):
    url: str
    site: str
    title: str
    excerpt: str
    ip: str = ""
    received: datetime
    isFiltered: bool = False

    @classmethod
    def from_etree(cls, element: Element):
        instance = cls(
            url=element.xpath("string(./url/text())"),
            site=element.xpath("string(./site/text())"),
            title=element.xpath("string(./title/text())"),
            excerpt=element.xpath("string(./excerpt/text())"),
            ip=element.xpath("string(./ip/text())"),
            received=pendulum.from_timestamp(element.xpath("number(./received/text())"), tz='Asia/Seoul'),
            isFiltered=bool(element.xpath("boolean(./isFiltered/text())")),
        )

        instance.ip = "%s.%s.*.*" % tuple(instance.ip.split('.')[:2])

        return instance


class Commenter(BaseModel):
    name: str
    homepage: str = ""
    ip: str = ""
    openid: str = ""
    id: str = ""

    @classmethod
    def from_etree(cls, element: Element):
        instance = cls(
            name=element.xpath("string(./name/text())"),
            homepage=element.xpath("string(./homepage/text())"),
            ip=element.xpath("string(./ip/text())"),
            openid=element.xpath("string(./openid/text())"),
            id=element.xpath("string(./@id)"),
        )

        instance.ip = "%s.%s.*.*" % tuple(instance.ip.split('.')[:2])

        return instance


class Comment(BaseModel):
    id: int
    commenter: Commenter
    content: str
    password: str = ""
    secret: bool = False
    longitude: str = ""
    latitude: str = ""
    written: datetime
    isFiltered: bool = False

    @classmethod
    def from_etree(cls, element: Element):
        instance = cls(
            id=int(element.xpath("number(./id/text())")),
            commenter=Commenter.from_etree(element.find("./commenter")),
            content=element.xpath("string(./content/text())"),
            password=element.xpath("string(./password/text())"),
            secret=int(element.xpath("boolean(./secret/text())")),
            longitude=element.xpath("string(./longitude/text())"),
            latitude=element.xpath("string(./latitude/text())"),
            written=pendulum.from_timestamp(element.xpath("number(./written/text())"), tz='Asia/Seoul'),
            isFiltered=bool(element.xpath("boolean(./isFiltered/text())")),
        )

        return instance


class Post(BaseModel):
    id: int
    appointed: bool = False
    visibility: str = 'syndicated'
    starred: int = False
    title: str

    location: str = ""
    password: str = ""
    acceptComment: bool = True
    acceptTrackback: bool = True
    published: datetime
    created: datetime
    modified: datetime
    longitude: str = ""
    latitude: str = ""
    category: str
    tag: list[str] = Field(default_factory=list)
    comments: list[Comment] = Field(default_factory=list)
    trackbacks: list[Trackback] = Field(default_factory=list)
    contents: list[Content]
    attachments: list[Attachment] = Field(default_factory=list)
    slogan: str
    format: str = ""

    @classmethod
    def from_etree(cls, element: Element, include_private_comments = False):
        comments = []

        for comment in map(Comment.from_etree, element.xpath("./comment")):
            if not include_private_comments and comment.secret:
                continue

            comments.append(comment)

        instance = cls(
            id=int(element.xpath("number(./id/text())")),
            appointed=element.xpath("boolean(./appointed/text())"),
            visibility=element.xpath("string(./visibility/text())"),
            starred=int(element.xpath("number(./starred/text())")),
            title=element.xpath("string(./title/text())"),
            location=element.xpath("string(./location/text())"),
            password=element.xpath("string(./password/text())"),
            acceptComment=int(element.xpath("boolean(./acceptComment/text())")),
            acceptTrackback=int(element.xpath("boolean(./acceptTrackback/text())")),
            published=pendulum.from_timestamp(element.xpath("number(./published/text())"), tz='Asia/Seoul'),
            created=pendulum.from_timestamp(element.xpath("number(./created/text())"), tz='Asia/Seoul'),
            modified=pendulum.from_timestamp(element.xpath("number(./modified/text())"), tz='Asia/Seoul'),
            longitude=element.xpath("string(./longitude/text())"),
            latitude=element.xpath("string(./latitude/text())"),
            category=element.xpath("string(./category/text())"),
            tag=element.xpath("./tag/text()"),
            comments=comments,
            trackbacks=list(map(Trackback.from_etree, element.xpath("./trackback"))),
            contents=list(map(Content.from_etree, element.xpath("./content"))),
            slogan=element.xpath("string(./@slogan)"),
            format=element.xpath("string(./@format)"),
            attachments=list(map(Attachment.from_etree, element.xpath("./attachment")))
        )

        return instance



class Blog(BaseModel):
    site_url: str

    @classmethod
    @model_validator(mode='after')
    def validate(cls, data: 'Blog'):
        if data.site_url.endswith('/'):
            data.site_url = data.site_url[:-1]

    def get_alt_site_url(self):
        """www 붙은 URL 반환"""
        url = purl.URL(self.site_url)
        return f"{url.scheme()}://www.{url.host}"