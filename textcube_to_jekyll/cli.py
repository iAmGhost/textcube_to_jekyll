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


app = typer.Typer()

logger = logging.getLogger('textcube_to_jekyll')


def main(
    backup_xml: Annotated[Optional[Path], typer.Option()] = None,
    jekyll_root: Annotated[Optional[Path], typer.Option()] = None,
    post_id: Annotated[List[int], typer.Option()] = None,
    enable_archive_org_link: Annotated[bool, typer.Option()] = True,
    archive_org_timestamp: Annotated[str, typer.Option()] = '20211231',
    site_url: Annotated[str, typer.Option()] = 'http://pig-min.com/tt',
    archive_org_backup_path: Annotated[Optional[Path], typer.Option()] = None,
    sample: Annotated[int, typer.Option()] = 0,
):
    logging.basicConfig()
    logger.setLevel(level=logging.INFO)

    if jekyll_root is None:
        jekyll_root = Path("blog/")

    converter = TextcubeToJekyllConverter(
        backup_xml=backup_xml,
        jekyll_root=jekyll_root,
        post_id=post_id,
        enable_archive_org_link=enable_archive_org_link,
        archive_org_timestamp=archive_org_timestamp,
        archive_org_backup_path=archive_org_backup_path,
        site_url=site_url,
        sample=sample,
    )

    converter.run()


if __name__ == "__main__":
    typer.run(main)
