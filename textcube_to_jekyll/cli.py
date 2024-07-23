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


def run_converter(
    jekyll_root: Annotated[Optional[Path], typer.Option(help="Specify jekyll root", default_factory=lambda: Path("blog/"))],
    backup_xml: Annotated[Optional[Path], typer.Option(help="Path of Textcube backup XML file.")] = None,
    post_id: Annotated[List[int], typer.Option(help="Extract specific post only")] = None,
    enable_archive_org_link: Annotated[bool, typer.Option(help="Add archive.org link to post")] = True,
    archive_org_timestamp: Annotated[str, typer.Option(help="timestamp for archive.org link")] = '20211231',
    site_url: Annotated[str, typer.Option(help="Textcube blog url")] = 'http://pig-min.com/tt',
    archive_org_backup_path: Annotated[Optional[Path], typer.Option(help="Specify folder that contains archive.org backup posts.")] = None,
    sample: Annotated[int, typer.Option(help="Only convert N posts.")] = 0,
):
    logging.basicConfig()
    logger.setLevel(level=logging.INFO)

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


def main():
    typer.run(run_converter)


if __name__ == "__main__":
    main()
