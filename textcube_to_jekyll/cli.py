import logging
from pathlib import Path
from typing import Optional, List

from typing_extensions import Annotated
import typer

import logging
from pathlib import Path
from typing import Optional, List

from typing_extensions import Annotated

from textcube_to_jekyll.converter import TextcubeToJekyllConverter


app = typer.Typer(no_args_is_help=True)

logger = logging.getLogger('textcube_to_jekyll')



@app.command()
def run_converter(
    jekyll_root: Annotated[Optional[Path], typer.Option(help="Jekyll 루트 경로 지정(미지정시 blog/ 사용)", default_factory=lambda: Path("blog/"))],
    backup_xml: Annotated[Optional[Path], typer.Option(help="텍스트큐브 백업 XML 파일 경로")] = None,
    archive_org_link: Annotated[bool, typer.Option(help="포스트에 archive.org 링크 추가")] = True,
    archive_org_link_timestamp: Annotated[str, typer.Option(help="archive.org 링크에 사용할 타임스탬프")] = '20211231',
    site_url: Annotated[str, typer.Option(help="텍스트큐브 블로그 주소(예: http://pig-min.com/tt)")] = 'http://pig-min.com/tt',
    archive_org_backup_path: Annotated[Optional[Path], typer.Option(help="archive.org 백업 HTML 폴더 주소(Pig-Min 복구용, 스킨에 따라 작동하지 않을 수 있습니다.)")] = None,
    post_id: Annotated[List[int], typer.Option(help="(테스트용) 특정 ID의 포스트만 추출 ")] = None,
    sample: Annotated[int, typer.Option(help="(테스트용) N개의 포스트만 추출")] = 0,
    slug_max_length:  Annotated[int, typer.Option(help="파일명의 제목(Slug) 최대 길이")] = 30,
):
    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S')
    logger.setLevel(level=logging.INFO)

    assert any([backup_xml, archive_org_backup_path]), "backup-xml 또는 archive-org-backup-path를 지정해야 합니다."

    converter = TextcubeToJekyllConverter(
        backup_xml=backup_xml,
        jekyll_root=jekyll_root,
        post_id=post_id,
        archive_org_link=archive_org_link,
        archive_org_link_timestamp=archive_org_link_timestamp,
        archive_org_backup_path=archive_org_backup_path,
        site_url=site_url,
        sample=sample,
        slug_max_length=slug_max_length,
    )

    converter.run()

if __name__ == "__main__":
    app()
