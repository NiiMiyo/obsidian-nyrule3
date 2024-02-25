from mkdocs.structure.files import Files
from mkdocs.structure.nav import Navigation
from mkdocs.config.defaults import MkDocsConfig
from os.path import split, splitext

def on_nav(nav: Navigation, config: MkDocsConfig, files: Files) -> Navigation | None:
	for f in files:
		dirpath, filename = split(f.src_uri)
		_, dirname = split(dirpath)

		filename, ext = splitext(filename)

		if dirname == filename and ext == '.md':
			f.name = 'index'

			f.url = split(split(f.url)[0])[0]
			f.dest_uri = split(split(f.dest_uri)[0])[0] + '/index.html'
			f.abs_dest_path = split(split(f.abs_dest_path)[0])[0] + '/index.html'
