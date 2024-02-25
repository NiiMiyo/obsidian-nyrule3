import regex
from os.path import splitext, split, relpath

from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files, File
from mkdocs.config.defaults import MkDocsConfig

WIKILINK_PATTERN = regex.compile(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]")

available_files: Files = None # type: ignore - will be initialized later

def on_files(files: Files, config: MkDocsConfig) -> Files | None:
	global available_files

	available_files = files

def on_page_markdown(markdown: str, *, page: Page, **_):
	global WIKILINK_PATTERN

	wikilink_matches = WIKILINK_PATTERN.finditer(markdown)

	while True:
		match = next(wikilink_matches, None)
		if match is None: break

		start, end = match.start(0), match.end(0)
		filename, text = match.group(1), match.group(2)

		replacement = get_wikilink_replacement(page.file, filename, text)
		markdown = markdown[:start] + replacement + markdown[end:]
		wikilink_matches = WIKILINK_PATTERN.finditer(markdown)

	return markdown


def get_wikilink_replacement(origin: File, destination_uri: str, text: str | None) -> str:
	destination_file, anchor = get_file_from_filepath(destination_uri, origin)

	if destination_file is not None:
		destination_uri = destination_file.src_uri

	if anchor != "" and not anchor.startswith("#"):
		anchor = "#" + anchor

	if not text and destination_file and destination_file.is_documentation_page():
		page = destination_file.page
		if page is not None:
			text = page.meta.get('title', None) or destination_file.name

		if text and text.lower() == "index":
			dirpath, _ = split(destination_file.src_uri)
			_, text = split(dirpath)

	href = relpath(destination_uri, origin.src_uri + '/..').replace('\\', '/') + anchor
	return f"[{text or ""}]({href})"


def get_file_from_filepath(filepath: str, origin: File) -> tuple[File | None, str]:
	global available_files

	id_index = filepath.find("#")
	element_id = ""

	if id_index != -1:
		element_id = filepath[id_index:]
		no_id_filepath = filepath[:id_index]
		if no_id_filepath == "":
			filepath = origin.src_uri
		else:
			filepath = no_id_filepath

	note_name, ext = splitext(filepath)
	if ext == "":
		ext = ".md"

	filepath = (note_name + ext).upper()
	_, filename = split(filepath)
	for f in available_files:
		f_filename = split(f.src_uri)[1].upper()

		if f_filename == filename and f.src_uri.upper().endswith(filepath):
			return f, element_id

	return None, ""
