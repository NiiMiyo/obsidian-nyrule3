import unicodedata
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


def get_wikilink_replacement(origin: File, file_input: str, text: str | None) -> str:
	global available_files

	destination_uri, anchor = remove_anchor(file_input)
	destination_file = get_file_from_filepath(destination_uri, origin, available_files)

	if destination_file is not None:
		destination_uri = destination_file.src_uri
		href = relpath(destination_uri, origin.src_uri + '/..').replace('\\', '/') + parse_anchor(anchor)

	else:
		href = destination_uri

	if not text:
		if anchor is not None:
			text = anchor[1:]

		elif destination_file is None or destination_file.is_documentation_page():
			text = file_input

	return f"[{text or ""}]({href})"

def remove_anchor(filepath: str) -> tuple[str, str | None]:
	anchor_start = filepath.find("#")
	if anchor_start == -1:
		return filepath, None

	return filepath[:anchor_start], filepath[anchor_start:]

def get_file_from_filepath(filepath: str, origin: File, files: Files) -> File | None:
	filepath, _ = remove_anchor(filepath.strip())

	if filepath == "":
		filepath = origin.src_uri

	filepath_no_ext, ext = splitext(filepath)
	if ext == "":
		ext = ".md"

	filepath_upper = (filepath_no_ext + ext).upper()
	_, filename_upper = split(filepath_upper)

	for f in files:
		f_filename_upper = split(f.src_uri)[1].upper()

		if f_filename_upper == filename_upper and f.src_uri.upper().endswith(filepath_upper):
			return f

	return None

def parse_anchor(anchor: str | None) -> str:
	if anchor is None or anchor == "":
		return ""

	parsed = unicodedata.normalize('NFD', anchor) \
		.encode('ascii', 'ignore') \
		.decode('utf-8') \
		.lower() \
		.replace(' - ', '-') \
		.replace(' ', '-')

	if not parsed.startswith("#"):
		parsed = "#" + parsed

	return parsed
