from os.path import split, splitext

from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from mkdocs.config.defaults import MkDocsConfig

def on_page_markdown(markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str | None:
	dirpath, filename = split(page.file.src_uri)
	meta_title = page.meta.get('title', None)

	if meta_title is None:
		if filename == 'index.md':
			_, page_title = split(dirpath)
		else:
			page_title, _ = splitext(filename)

		page.meta['title'] = page_title
