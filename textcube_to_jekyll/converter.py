
import logging
import shutil
import base64
from pathlib import Path
from typing import Optional, List

from lxml import etree
from lxml import html
from tqdm import tqdm
from pydantic import BaseModel, ConfigDict
from textcube_to_jekyll.archive_org import parse_archive_org_html
from textcube_to_jekyll.template import get_template
from textcube_to_jekyll.models import Blog, Post, TTMLAttachmentTag
from textcube_to_jekyll.util import slugify


logger = logging.getLogger(__name__)


class TextcubeToJekyllConverter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backup_xml: Optional[Path] = None
    jekyll_root: Optional[Path] = None
    post_id: Optional[List[int]] = None
    enable_archive_org_link: bool = True
    archive_org_timestamp: str = '20211231'
    site_url: str = 'http://pig-min.com/tt'
    sample: int = 0
    archive_org_backup_path: Optional[Path] = None

    def model_post_init(self, __context):
        self._blog = Blog(site_url=self.site_url)
        self._post_template = get_template('post.html')

    def run(self):
        if self.backup_xml:
            self.run_backup_converter()
        if self.archive_org_backup_path:
            self.run_archives_org_converter()

    def run_backup_converter(self):
        logger.info("Converting backup.xml...")
        assert self.backup_xml.is_file(), f"{self.backup_xml} is not a file"

        posts_folder = self.jekyll_root.joinpath('tt/_posts/')
        attachments_folder = self.jekyll_root.joinpath('tt/attach/')

        logger.info(f"Cleaning up {posts_folder}")
        shutil.rmtree(posts_folder, ignore_errors=True)
        posts_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"Cleaning up {attachments_folder}")
        shutil.rmtree(attachments_folder, ignore_errors=True)
        attachments_folder.mkdir(parents=True, exist_ok=True)

        with self.backup_xml.open('rb') as f:
            backup_doc = etree.fromstring(f.read())

        post_elements = []

        if self.post_id:
            for _id in self.post_id:
                post_elements.append(backup_doc.xpath(f"//post/id[text() = '{_id}']/..")[0])
        else:
            post_elements += backup_doc.xpath("//post")

        if self.sample > 0:
            post_elements = post_elements[:self.sample]


        for post_element in tqdm(post_elements):
            post = Post.from_etree(post_element, include_private_comments=True)

            try:
                # 비공개 포스트 건너뜀
                if post.visibility == 'private':
                    continue

                self.write_post(
                    post=post,
                    posts_folder=posts_folder,
                    attachments_folder=attachments_folder,
                )


            except Exception as e:
                logger.error(f"Error processing post {post.id}")
                logger.exception(e)
                return


    def run_archives_org_converter(self):
        logger.info("Coverting archive.org html files...")

        assert self.archive_org_backup_path.is_dir(), f"{self.archive_org_backup_path} is not a directory"

        posts_folder = self.jekyll_root.joinpath('archive_org/_posts/')
        attachments_folder = self.jekyll_root.joinpath('archive_org/attach/')

        shutil.rmtree(posts_folder, ignore_errors=True)
        shutil.rmtree(attachments_folder, ignore_errors=True)

        for filename in tqdm(self.archive_org_backup_path.glob("*.html")):
            with filename.open('rb') as f:
                content = f.read()

            doc = html.fromstring(content)

            post = parse_archive_org_html(doc)

            self.write_post(
                post=post,
                posts_folder=posts_folder,
                attachments_folder=attachments_folder,
            )


    def write_post(self, post: Post, posts_folder: Path, attachments_folder: Path):
        raw_content = '\n'.join([content.text for content in post.contents])

        filename = "{date}-{id}-{slug}.html".format(
            date=post.published.format('YYYY-MM-DD'),
            id=post.id,
            slug=slugify(post.slogan, allow_unicode=True),
        )

        content = self._post_template.render(
            post=post,
            blog=self._blog,
            enable_archive_org_link=self.enable_archive_org_link,
            archive_org_timestamp=self.archive_org_timestamp,
        )

        out_path = posts_folder.joinpath(f'{filename}')
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with out_path.open('w', encoding='utf-8') as f:
            f.write(content)

        filename_seq_table = {}

        for tag in TTMLAttachmentTag.parse_from_content(raw_content):
            filename_seq_table[tag.filename] = tag.seq

        for attachment in post.attachments:
            attachment_path = attachments_folder.joinpath(f"{filename_seq_table.get(attachment.name, 0)}/{attachment.name}")
            attachment_path.parent.mkdir(parents=True, exist_ok=True)

            with attachment_path.open('wb') as f:
                f.write(base64.b64decode(attachment.content))