from pathlib import Path
from typing import List, Tuple, Union
from urllib.parse import quote

from deprecated import deprecated

from .. import common, filesystem
from .entity import Comment, Header, Indent, Link, SpecialFile

# TODO: \n \n arasında olması gerekebilir


def generate_insert_position_strings(index_string: str) -> Tuple[str]:
    """Verilen indeks için başlangıç ve bitiş index metni oluşturur

    Arguments:
        index_string {str} -- İndeks metni

    Returns:
        Tuple -- (başlangıç, bitiş) indeks metinleri

    Examples:
        >>> generate_insert_position_strings('Index')
        ('\\n<!-- Index -->\\n\\n', '\\n\\n<!-- Index -->\\n')
    """
    start_string = "\n" + Comment(index_string) + "\n\n"
    end_string = "\n\n" + Comment(index_string) + "\n"
    return start_string, end_string


def make_index_string(string: str) -> str:
    s1, s2 = generate_insert_position_strings(string)
    return s1 + s2


def insert_to_file(
    string: str,
    filepath: Path,
    index_string: str,
    must_inserted=False
) -> bool:
    """Verilen metni markdown dosyasına indeks metinlerini yorum satırlarına alarak ekler

    Arguments:
        string {str} -- Yerleştirilecek metin
        filepath {Path} -- Dosya yolu objesi
        index_string {str} -- Başlangıç metni

    Keyword Arguments:
        must_inserted {bool} -- Verilen indeksler bulunamazsa dosyanın sonuna indeksler ile ekler

    Returns:
        bool -- Dosyada değişiklik olduysa True
    """

    start_string, end_string = generate_insert_position_strings(index_string)
    return filesystem.insert_to_file(
        string,
        filepath,
        start_string,
        end_string,
        must_inserted=must_inserted
    )


def create_markdown_file(filepath: Path, header: str = None):
    if not header:
        header = filepath.name

    content = generate_header_section(header, 1)
    filesystem.write_to_file(filepath, content)


def generate_substrings(content, index):
    index = str(Comment(index))
    return common.generate_substrings(content, index)


def find_all_headers(string, level=1) -> List[Header]:
    headers = Header.find_all(string, level=level)
    return headers


def find_all_headers_from_file(filepath, level=1) -> List[Header]:
    if not filepath.exists():
        return []

    content = filesystem.read_file(filepath)
    headers = find_all_headers(content, level=level)
    return headers


def find_first_header(string, level=1) -> Union[Header, None]:
    """İçerik içerisindeki ilk header'ı bulma

    Arguments:
        string {str} -- İçerik

    Keyword Arguments:
        level {int} -- Header seviyesi (default: {1})

    Returns:
        Union[Any, None] -- Bulunan Header objesi

    Examples:
        >>> header = Header.find_first('# HEHO\\n#HOHO')
        >>> header.name
        'HEHO'
        >>> header.level
        1
    """

    header = Header.find_first(string, level=level)
    return header


def find_first_header_from_file(filepath, level=1) -> Union[Header, None]:
    """Markdown dosyasının ilk başlığını okuma

    Arguments:
        filepath {Path} -- Markdown dosyasının yolu

    Keywords Arguments:
        level {int} -- Başlık seviyesi

    Returns:
        str -- Başlığı varsa başlığı, yoksa dosya ismini döndürür

    Examples:
        >>> find_first_header_from_file(Path('docs/README.md'))
        Header('📦 YPackage', 1)
    """
    if not filepath.exists():
        return None

    content = filesystem.read_file(filepath)
    header = find_first_header(content, level=level)
    return header


def change_title_of_string(title: str, content: str) -> str:
    title_changed = False

    lines = common.parse_to_lines(content)
    for i, line in enumerate(lines):
        header = find_first_header(line)
        if header:
            if header.level == 1:
                lines[i] = title
                title_changed = True
                break
            elif header.level >= 1:
                lines[0] = title
                title_changed = True
                break

    if not title_changed:
        lines[0] = title
        title_changed = True

    return common.merge_lines(lines)


def change_title_of_file(title: str, filepath: Path):
    content = filesystem.read_file(filepath)
    content = change_title_of_string(title, content)
    filesystem.write_file(filepath, content)


def generate_header_section(name: str, level: str) -> str:
    """Markdown dosyaları için standartlara uygun header alanı metni oluşturur

    Arguments:
        name {str} -- Başlık ismi
        level {str} -- Başlık seviyesi

    Returns:
        str -- Oluşturulan başlık alanı metni

    Examples:
        >>> generate_header_section("YPackage", 1)
        '# YPackage\\n\\n'
    """
    return Header(name, level).to_str(is_section=True)


def generate_name_for_file(filepath: Path) -> str:
    """Markdown dosyası için isim belirleme

    Arguments:
        filepath {Path} -- Markdown dosyasının yolu

    Returns:
        str -- Başlığı varsa başlığı, yoksa dosya ismini döndürür

    Examples:
        >>> generate_name_for_file(Path('docs/README.md'))
        '📦 YPackage'
        >>> generate_name_for_file(Path('LICENSE'))
        'LICENSE'
    """

    header = None
    if is_markdown(filepath):
        header = find_first_header_from_file(filepath)

    name = header.name if header else filepath.name
    return name


def find_all_links(string) -> List[Link]:
    return Link.find_all(string)


def find_first_link(string) -> Link:
    return Link.find_first(string)


def generate_link_string(
    name: str,
    path: str,
    indent_level=0,
    is_list: bool = False,
    single_line: bool = False
) -> str:
    """Özel link metni oluşturma

    Arguments:
        name {str} -- Link'in ismi
        path {str} -- Link'in adresi

    Keyword Arguments:
        indent_level {int} -- Varsa girinti seviyesi (default: {0})
        is_list {bool} -- Liste elamanı olarak tanımlama '- ' ekler (default: {False})
        single_line {bool} -- Tek satırda yer alan link '\\n' ekler (default: {False})


    Returns:
        {str} -- Oluşturulan link metni

    Examples:
        >>> generate_link_string(           \
            'YPackage',                     \
            'https://ypackage.yemreak.com', \
            indent_level = 2,               \
            is_list      = True,            \
            single_line  = True             \
        )
        '    - [YPackage](https://ypackage.yemreak.com)\\n'

    """
    return Link(name, path).to_str(
        indent=Indent(indent_level),
        is_list=is_list,
        single_line=single_line
    )


def generate_filelink_string(
    filepath: Path,
    name: str = None,
    root: Path = None,
    indent_level=0,
    is_list: bool = False,
    single_line: bool = False
) -> str:
    """Özel dosya linki metni oluşturma

    Arguments:
        filepath {Path} -- Dosya yolu objesi

    Keyword Arguments:
        name {str} -- Link'in ismi
        indent_level {int} -- Varsa girinti seviyesi (default: {0})
        is_list {bool} -- Liste elamanı olarak tanımlama '- ' ekler (default: {False})
        single_line {bool} -- Tek satırda yer alan link '\\n' ekler (default: {False})

    Returns:
        {str} -- Oluşturulan link metni

    Examples:
        >>> generate_filelink_string(               \
            Path('./src/ypackage/markdown.py'),     \
            name         = 'YPackage',              \
            root         = Path('src/ypackage/'),   \
            indent_level = 2,                       \
            is_list      = True,                    \
            single_line  = True                     \
        )
        '    - [YPackage](markdown.py)\\n'
    """
    if not name:
        name = generate_name_for_file(filepath)

    if root:
        root = root.absolute()
        filepath = filepath.absolute()
        filepath = filepath.relative_to(root)

    filepath_string = encode_filepath(filepath)

    return generate_link_string(
        name,
        filepath_string,
        indent_level=indent_level,
        is_list=is_list,
        single_line=single_line
    )


def encode_filepath(filepath: Path) -> str:
    """Verilen dosya yolunu markdown url yapısına göre düzenler

    Arguments:
        filepath {Path} -- Dosya yolu objesi

    Returns:
        str -- Düzenlenmiş dosya yolu metni

    Examples:
        >>> encode_filepath(Path('Büt 2017 DM'))
        'B%C3%BCt%202017%20DM'
        >>> encode_filepath(Path('Vize 2020'))
        'Vize%202020'
    """

    filepath_string = filepath.as_posix()
    filepath_string = quote(filepath_string)
    return filepath_string


def generate_dirlink_string(
    dirpath: Path,
    root: Path = Path.cwd(),
    indent_level=0,
    is_list: bool = False,
    single_line: bool = False
) -> str:
    """Özel dosya linki metni oluşturma

    Arguments:
        filepath {Path} -- Dosya yolu objesi

    Keyword Arguments:
        name {str} -- Link'in ismi
        intent {Indent} -- Varsa girinti objesi (default: {None})
        is_list {bool} -- Liste elamanı olarak tanımlama '- ' ekler (default: {False})
        single_line {bool} -- Tek satırda yer alan link '\\n' ekler (default: {False})

    Returns:
        {str} -- Oluşturulan link metni

    Examples:
        >>> generate_dirlink_string(                \
            Path('src/ypackage/markdown.py'),       \
            Path('src'),                            \
            indent_level=2,                         \
            is_list     = True,                     \
            single_line = True                      \
        )
        '    [README.md](ypackage/markdown.py/README.md)\\n'
    """

    readme_path = readme_path_for_dir(dirpath)

    return generate_filelink_string(
        readme_path if readme_path else dirpath,
        root=root,
        indent_level=indent_level,
        single_line=single_line
    )


@deprecated
def is_url(link: str) -> bool:
    return "https://" in link or "http://" in link


@deprecated
def check_links(fpath):
    with open(fpath, "r", encoding="utf-8") as f:
        for line in f:
            links = find_all_links(line)
            for link in links:
                if not link.filepath:
                    print(link.path)


def map_links(content: str, func: Link.map_function) -> str:
    """Dosyadaki tüm linkler için verilen fonksiyonu uygular

    Arguments:
        content {str} -- Metin içeriği
        func {Link.map_function} -- Link alan ve Link döndüren fonksiyon

    Returns:
        str -- Değişen metin içeriği
    """
    lines = common.parse_to_lines(content)
    for i, line in enumerate(lines):
        oldlinks = Link.find_all(line)
        for oldlink in oldlinks:
            newlink = func(oldlink)
            lines[i] = lines[i].replace(str(oldlink), str(newlink))

    return common.merge_lines(lines)


def replace_in_links(content: str, old: str, new: str) -> str:

    def replace_link(link: Link):
        link.path = link.path.replace(old, new)
        return link

    map_links(content, replace_link)


def list_nonmarkdown_files(dirpath: Path) -> List[Path]:
    """Markdown olmayan dosyaların listesini sıralı olarak döndürür

    Arguments:
        dirpath {Path} -- Dizin yolu objesi

    Returns:
        List[Path] -- Sıralı markdown olmayan dosya listesi

    Examles:
        >>> list_nonmarkdown_files(Path('docs'))
        []
        >>> nonmarkdowns = list_nonmarkdown_files(Path('.'))
        >>> Path('LICENSE') in nonmarkdowns
        True
    """

    nonmarkdown_filepaths = []

    for path in sorted(dirpath.iterdir()):
        if path.is_file() and ".md" not in path.name:
            nonmarkdown_filepaths.append(path)
    return nonmarkdown_filepaths


def list_markdown_files(dirpath: Path) -> List[Path]:
    """Markdown olmayan dosyaların listesini sıralı olarak döndürür

    Arguments:
        dirpath {Path} -- Dizin yolu objesi

    Returns:
        List[Path] -- Sıralı markdown olmayan dosya listesi
    Examles:
        >>> list_markdown_files(Path('.'))
        []
        >>> markdowns = list_markdown_files(Path('docs'))
        >>> Path('docs/README.md') in markdowns
        True
    """

    markdown_filepaths = []

    for path in sorted(dirpath.iterdir()):
        if path.is_file() and is_markdown(path):
            markdown_filepaths.append(path)
    return markdown_filepaths


def readme_path_for_dir(dirpath: Path) -> Path:
    """Dizin için README dosya yolu objesi oluşturur

    Arguments:
        dirpath {Path} -- Dizin

    Returns:
        Path -- README dosya yolu objesi

    Examples:
        >>> readme_path_for_dir(Path('.')).as_posix()
        'README.md'
    """
    return SpecialFile.README.get_filepath(dirpath)


def changelog_path_for_dir(dirpath: Path) -> Path:
    """Dizin için CHANGELOG dosya yolu objesi oluşturur

    Arguments:
        dirpath {Path} -- Dizin

    Returns:
        Path -- README dosya yolu objesi

    Examples:
        >>> changelog_path_for_dir(Path('.')).as_posix()
        'CHANGELOG.md'
    """
    return SpecialFile.CHANGELOG.get_filepath(dirpath)


def license_path_for_dir(dirpath: Path) -> Path:
    """Dizin için LICENSE dosya yolu objesi oluşturur

    Arguments:
        dirpath {Path} -- Dizin

    Returns:
        Path -- README dosya yolu objesi

    Examples:
        >>> license_path_for_dir(Path('.')).as_posix()
        'LICENSE'
    """
    return SpecialFile.LICENSE.get_filepath(dirpath)


def code_of_conduct_path_for_dir(dirpath: Path) -> Path:
    """Dizin için CODE_OF_CONDUCT dosya yolu objesi oluşturur

    Arguments:
        dirpath {Path} -- Dizin

    Returns:
        Path -- README dosya yolu objesi

    Examples:
        >>> code_of_conduct_path_for_dir(Path('.')).as_posix()
        'CODE_OF_CONDUCT.md'
    """
    return SpecialFile.CODE_OF_CONDUCT.get_filepath(dirpath)


def contributing_path_for_dir(dirpath: Path) -> Path:
    """Dizin için CONTRIBUTING dosya yolu objesi oluşturur

    Arguments:
        dirpath {Path} -- Dizin

    Returns:
        Path -- README dosya yolu objesi

    Examples:
        >>> contributing_path_for_dir(Path('.')).as_posix()
        'CONTRIBUTING.md'
    """
    return SpecialFile.CONTRIBUTING.get_filepath(dirpath)


def has_readme_file(dirpath: Path) -> bool:
    """Verilen dizinde README dosyasını varlığını kontrol eder

    Arguments:
        dirpath {Path} -- Kontrol edilecek dizin

    Returns:
        bool -- Varsa True

    Examples:
        >>> has_readme_file(Path('docs'))
        True
    """
    filepath = readme_path_for_dir(dirpath)
    return filepath.exists()


def has_changelog_file(dirpath: Path) -> bool:
    """Verilen dizinde README dosyasını varlığını kontrol eder

    Arguments:
        dirpath {Path} -- Kontrol edilecek dizin

    Returns:
        bool -- Varsa True

    Examples:
        >>> has_changelog_file(Path('docs'))
        True
    """
    filepath = changelog_path_for_dir(dirpath)
    return filepath.exists()


def has_code_of_conduct_file(dirpath: Path) -> bool:
    """Verilen dizinde CODE_OF_CONDUCT dosyasını varlığını kontrol eder

    Arguments:
        dirpath {Path} -- Kontrol edilecek dizin

    Returns:
        bool -- Varsa True

    Examples:
        >>> has_code_of_conduct_file(Path('.'))
        False
    """
    filepath = code_of_conduct_path_for_dir(dirpath)
    return filepath.exists()


def has_contributing_file(dirpath: Path) -> bool:
    """Verilen dizinde CONTRIBUTING dosyasını varlığını kontrol eder

    Arguments:
        dirpath {Path} -- Kontrol edilecek dizin

    Returns:
        bool -- Varsa True

    Examples:
        >>> has_contributing_file(Path('docs'))
        True
    """
    filepath = contributing_path_for_dir(dirpath)
    return filepath.exists()


def has_license_file(dirpath: Path) -> bool:
    """Verilen dizinde LICENSE dosyasını varlığını kontrol eder

    Arguments:
        dirpath {Path} -- Kontrol edilecek dizin

    Returns:
        bool -- Varsa True

    Examples:
        >>> has_license_file(Path('.'))
        True
    """
    filepath = license_path_for_dir(dirpath)
    return filepath.exists()


def is_markdown(filepath: Path) -> bool:
    """Verilen dosyanın markdown mı

    Arguments:
        filepath {Path} -- Dosya yolu objesi

    Returns:
        bool -- Markdown ise True

    Examples:
        >>> is_markdown(Path('docs/README.md'))
        True
        >>> is_markdown(Path('LICENSE'))
        False
    """
    return filepath.name[-3:] == ".md"


def is_readme(filepath: Path) -> bool:
    """Verilen dosyanın README olmasını kontrol eder

    Arguments:
        filepath {Path} -- Dosya yolu objesi

    Returns:
        bool -- Markdown ise True

    Examples:
        >>> is_readme(Path('docs/README.md'))
        True
        >>> is_readme(Path('LICENSE'))
        False
    """
    result = filepath.name == SpecialFile.README.value
    return result
