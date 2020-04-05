from pathlib import Path
from typing import Callable, List, Tuple, Union
from urllib.parse import quote

from ..model.markdown import Comment, Header, Indent, Link, SpecialFile
from . import common, filesystem

# TODO: \n \n arasında olması gerekebilir


def generate_stringindexes_by_commentstring(
    index_string: str
) -> Tuple[str]:
    """Verilen indeks için başlangıç ve bitiş index metni oluşturur

    Arguments:
        index_string {str} -- İndeks metni

    Returns:
        Tuple -- (başlangıç, bitiş) indeks metinleri

    Examples:
        >>> generate_stringindexes_by_commentstring('Index')
        ('\\n<!--Index-->\\n\\n', '\\n\\n<!--Index-->\\n')
    """
    start_string = "\n" + Comment(index_string) + "\n\n"
    end_string = "\n\n" + Comment(index_string) + "\n"
    return start_string, end_string


def generate_indexsection_for_markdown(string: str) -> str:
    """Markdown metni için indeks alanı oluşturur

    Arguments:
        string {str} -- indeks metni

    Returns:
        str -- Oluşturulan indeks alanı

    Examples:
        >>> generate_indexsection_for_markdown('Index')
        '\\n<!--Index-->\\n\\n\\n\\n<!--Index-->\\n'
    """
    s1, s2 = generate_stringindexes_by_commentstring(string)
    return s1 + s2


def update_markdownfile_by_commentstring(
    string: str,
    filepath: Path,
    commentstring: str,
    must_inserted=False
) -> bool:
    """Verilen metni markdown dosyasına indeks metinlerini yorum satırlarına alarak ekler

    Arguments:
        string {str} -- Yerleştirilecek metin
        filepath {Path} -- Dosya yolu objesi
        commentstring {str} -- Yorum satırı metni

    Keyword Arguments:
        must_inserted {bool} -- Verilen indeksler bulunamazsa dosyanın sonuna indeksler ile ekler

    Returns:
        bool -- Dosyada değişiklik olduysa True
    """

    start_string, end_string = generate_stringindexes_by_commentstring(
        commentstring
    )
    return filesystem.update_file_by_stringindexes(
        string,
        filepath,
        start_string,
        end_string,
        must_inserted=must_inserted
    )


def create_markdownfile(filepath: Path, header: str = None) -> bool:
    """Markdown dosyası oluşturur

    Arguments:
        filepath {Path} -- Dosya yolu objesi

    Keyword Arguments:
        header {str} -- Dosyanın başlık metni (default: {None})

    Returns:
        bool -- Oluşturma başarılı ise True
    """

    if not header:
        header = filepath.name

    content = generate_headersection(1, header)
    return filesystem.write_to_file(filepath, content)


def find_substrings_by_commentstring(content: str, commentstring: str):
    """Markdown metni içerisideki indekslerin arasındaki metinleri alma

    Arguments:
        content {str} -- Metin
        commentstring {str} -- Yorum satırı metni

    Returns:
        List[str] -- Bulunan metinlerin listesi

    Examles:
        >>> find_substrings_by_commentstring(                               \
            'A\\n<!--Index-->\\n\\n YEmreAk \\n\\n<!--Index-->\\nB',    \
            'Index'                                                         \
            )
        [' YEmreAk ']
    """
    start_string, end_string = generate_stringindexes_by_commentstring(
        commentstring
    )
    return common.find_substrings_by_strings(
        content,
        start_string,
        end_string
    )


def find_all_headers(content) -> List[Header]:
    """İçerik içerisindeki tüm başlıkları bulur

    Arguments:
        content {str} -- İçerik metni

    Keyword Arguments:
        level {int} -- Bulunacak header seviyesi (default: {1})

    Returns:
        List[Header] -- Header listesi

    Examples:
        >>> find_all_headers('# Hey\\n# Hello')
        [Header(level=1, name='Hey'), Header(level=1, name='Hello')]
    """

    return Header.find_all(content)


def find_all_headers_from_file(filepath, level=1) -> List[Header]:
    if not filepath.exists():
        return []

    content = filesystem.read_file(filepath)
    headers = find_all_headers(content, level=level)
    return headers


def find_first_header(content) -> Union[Header, None]:
    """İçerik içerisindeki ilk başlığı bulma

    Arguments:
        content {str} -- İçerik

    Keyword Arguments:
        level {int} -- Header seviyesi (default: {1})

    Returns:
        Union[Header, None] -- Bulunan Header objesi

    Examples:
        >>> find_first_header('# Hey\\n#Hello')
        Header(level=1, name='Hey')
    """

    return Header.find_first(content)


def find_first_header_from_file(filepath) -> Union[Header, None]:
    """Markdown dosyasının ilk başlığını okuma

    Arguments:
        filepath {Path} -- Markdown dosyasının yolu

    Keywords Arguments:
        level {int} -- Başlık seviyesi

    Returns:
        str -- Başlığı varsa başlığı, yoksa dosya ismini döndürür

    Examples:
        >>> find_first_header_from_file(Path('docs/README.md'))
        Header(level=1, name='📦 YPackage')
    """
    if not filepath.exists():
        return None

    content = filesystem.read_file(filepath)
    header = find_first_header(content)
    return header


def update_title_of_markdown(title: str, content: str) -> str:
    """Markdown metninin başlığını değiştirir

    Arguments:
        title {str} -- Yeni başlık metni
        content {str} -- Markdown metni

    Returns:
        str -- Değiştirilen markdown metni

    Examles:
        >>> update_title_of_markdown(                       \
            'YEmreAk',                                      \
            '# Selam\\n## Yeni işler\\n## Yeni Kodlar\\n'   \
            )
        '# YEmreAk\\n## Yeni işler\\n## Yeni Kodlar\\n'
    """
    title = Header(1, title).to_str()
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


def update_title_of_markdownfile(title: str, filepath: Path) -> bool:
    content = filesystem.read_file(filepath)
    content = update_title_of_markdown(title, content)
    return filesystem.write_file(filepath, content)


def generate_headersection(level: str, name: str) -> str:
    """Markdown dosyaları için standartlara uygun header alanı metni oluşturur

    Arguments:
        name {str} -- Başlık ismi
        level {str} -- Başlık seviyesi

    Returns:
        str -- Oluşturulan başlık alanı metni

    Examples:
        >>> generate_headersection(1, "YPackage")
        '# YPackage\\n\\n'
    """
    return Header(level, name).to_str(is_section=True)


def generate_name_for_markdownfile(filepath: Path) -> str:
    """Markdown dosyası için isim belirler

    Arguments:
        filepath {Path} -- Markdown dosyasının yolu

    Returns:
        str -- Başlığı varsa başlığı, yoksa dosya ismini döndürür

    Examples:
        >>> generate_name_for_markdownfile(Path('docs/README.md'))
        '📦 YPackage'
        >>> generate_name_for_markdownfile(Path('LICENSE'))
        'LICENSE'
    """

    header = None
    if is_markdownfile(filepath):
        header = find_first_header_from_file(filepath)

    name = header.name if header else filepath.name
    return name


def find_all_links(string) -> List[Link]:
    """Metin içerisindeki ilk bağlantıyı bulur

    Arguments:
        content {str} -- Metin

    Returns:
        Link -- Bulunan bağlantı objesi

    Examles:
        >>> find_all_links('[name1](path1) [name2](path2)')
        [Link(name='name1', path='path1'), Link(name='name2', path='path2')]
    """
    return Link.find_all(string)


def find_first_link(content: str) -> Link:
    """Metin içerisindeki ilk bağlantıyı bulur

    Arguments:
        content {str} -- Metin

    Returns:
        Link -- Bulunan bağlantı objesi

    Examles:
        >>> find_first_link('[name1](path1) [name2](path2)')
        Link(name='name1', path='path1')
    """
    return Link.find_first(content)


def generate_linkstring(
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
        >>> generate_linkstring(            \
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


def generate_filelinkstring(
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
        >>> generate_filelinkstring(                \
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
        name = generate_name_for_markdownfile(filepath)

    if root:
        root = root.absolute()
        filepath = filepath.absolute()
        filepath = filepath.relative_to(root)

    filepath_string = encode_filepath(filepath)

    return generate_linkstring(
        name,
        filepath_string,
        indent_level=indent_level,
        is_list=is_list,
        single_line=single_line
    )


def generate_nonmarkdown_fileliststring(dirpath: Path) -> str:
    nonmarkdown_filepaths = list_nonmarkdownfiles(dirpath)

    if not nonmarkdown_filepaths:
        return ""

    filelink_strings = []
    for filepath in nonmarkdown_filepaths:
        filelink_strings.append(
            generate_filelinkstring(
                filepath,
                root=dirpath,
                is_list=True
            )
        )

    content = common.merge_lines(filelink_strings)
    return content


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


def generate_dirlinkstring(
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
        >>> generate_dirlinkstring(                 \
            Path('src/ypackage/markdown.py'),       \
            Path('src'),                            \
            indent_level=2,                         \
            is_list     = True,                     \
            single_line = True                      \
        )
        '    [README.md](ypackage/markdown.py/README.md)\\n'
    """

    readme_path = readmepath_for_dir(dirpath)

    return generate_filelinkstring(
        readme_path if readme_path else dirpath,
        root=root,
        indent_level=indent_level,
        single_line=single_line
    )


def check_links(fpath):
    with open(fpath, "r", encoding="utf-8") as f:
        for line in f:
            links = find_all_links(line)
            for link in links:
                if not link.filepath:
                    print(link.path)


def map_links_in_string(content: str, func: Callable[[Link], None]) -> str:
    """Metindeki tüm linkler için verilen fonksiyonu uygular

    Arguments:
        content {str} -- Metin içeriği
        func {Callable[[Link], None]} -- Link alan ve değiştiren fonksiyon

    Returns:
        str -- Değişen metin içeriği
    """

    return Link.map(content, func)


def map_links_in_string_in_markdownfile(
    filepath: Path,
    func: Callable[[Link], None]
) -> bool:
    """Dosyadaki tüm linkler için verilen fonksiyonu uygular

    Arguments:
        filepath {Path} -- Dosya yolu objesi
        func {Callable[[Link], None]} -- Link alan ve değiştiren fonksiyon

    Returns:
        bool -- Değişim olduysa True
    """
    content = filesystem.read_file(filepath)
    content = map_links_in_string(content, func)
    return filesystem.write_to_file(filepath)


def list_nonmarkdownfiles(dirpath: Path) -> List[Path]:
    """Markdown olmayan dosyaların listesini sıralı olarak döndürür

    Arguments:
        dirpath {Path} -- Dizin yolu objesi

    Returns:
        List[Path] -- Sıralı markdown olmayan dosya listesi

    Examles:
        >>> list_nonmarkdownfiles(Path('docs'))
        []
        >>> nonmarkdowns = list_nonmarkdownfiles(Path('.'))
        >>> Path('LICENSE') in nonmarkdowns
        True
    """

    nonmarkdown_filepaths = []

    for path in sorted(dirpath.iterdir()):
        if path.is_file() and ".md" not in path.name:
            nonmarkdown_filepaths.append(path)
    return nonmarkdown_filepaths


def list_markdownfiles(dirpath: Path) -> List[Path]:
    """Markdown olmayan dosyaların listesini sıralı olarak döndürür

    Arguments:
        dirpath {Path} -- Dizin yolu objesi

    Returns:
        List[Path] -- Sıralı markdown olmayan dosya listesi
    Examles:
        >>> list_markdownfiles(Path('.'))
        []
        >>> markdowns = list_markdownfiles(Path('docs'))
        >>> Path('docs/README.md') in markdowns
        True
    """

    markdown_filepaths = []

    for path in sorted(dirpath.iterdir()):
        if path.is_file() and is_markdownfile(path):
            markdown_filepaths.append(path)
    return markdown_filepaths


def readmepath_for_dir(dirpath: Path) -> Path:
    """Dizin için README dosya yolu objesi oluşturur

    Arguments:
        dirpath {Path} -- Dizin

    Returns:
        Path -- README dosya yolu objesi

    Examples:
        >>> readmepath_for_dir(Path('.')).as_posix()
        'README.md'
    """
    return SpecialFile.README.get_filepath(dirpath)


def changelogpath_for_dir(dirpath: Path) -> Path:
    """Dizin için CHANGELOG dosya yolu objesi oluşturur

    Arguments:
        dirpath {Path} -- Dizin

    Returns:
        Path -- README dosya yolu objesi

    Examples:
        >>> changelogpath_for_dir(Path('.')).as_posix()
        'CHANGELOG.md'
    """
    return SpecialFile.CHANGELOG.get_filepath(dirpath)


def licensepath_for_dir(dirpath: Path) -> Path:
    """Dizin için LICENSE dosya yolu objesi oluşturur

    Arguments:
        dirpath {Path} -- Dizin

    Returns:
        Path -- README dosya yolu objesi

    Examples:
        >>> licensepath_for_dir(Path('.')).as_posix()
        'LICENSE'
    """
    return SpecialFile.LICENSE.get_filepath(dirpath)


def codeofconductpath_for_dir(dirpath: Path) -> Path:
    """Dizin için CODE_OF_CONDUCT dosya yolu objesi oluşturur

    Arguments:
        dirpath {Path} -- Dizin

    Returns:
        Path -- README dosya yolu objesi

    Examples:
        >>> codeofconductpath_for_dir(Path('.')).as_posix()
        'CODE_OF_CONDUCT.md'
    """
    return SpecialFile.CODE_OF_CONDUCT.get_filepath(dirpath)


def contributingpath_for_dir(dirpath: Path) -> Path:
    """Dizin için CONTRIBUTING dosya yolu objesi oluşturur

    Arguments:
        dirpath {Path} -- Dizin

    Returns:
        Path -- README dosya yolu objesi

    Examples:
        >>> contributingpath_for_dir(Path('.')).as_posix()
        'CONTRIBUTING.md'
    """
    return SpecialFile.CONTRIBUTING.get_filepath(dirpath)


def has_readmefile(dirpath: Path) -> bool:
    """Verilen dizinde README dosyasını varlığını kontrol eder

    Arguments:
        dirpath {Path} -- Kontrol edilecek dizin

    Returns:
        bool -- Varsa True

    Examples:
        >>> has_readmefile(Path('docs'))
        True
    """
    filepath = readmepath_for_dir(dirpath)
    return filepath.exists()


def has_changelogfile(dirpath: Path) -> bool:
    """Verilen dizinde README dosyasını varlığını kontrol eder

    Arguments:
        dirpath {Path} -- Kontrol edilecek dizin

    Returns:
        bool -- Varsa True

    Examples:
        >>> has_changelogfile(Path('docs'))
        True
    """
    filepath = changelogpath_for_dir(dirpath)
    return filepath.exists()


def has_codeofconductfile(dirpath: Path) -> bool:
    """Verilen dizinde CODE_OF_CONDUCT dosyasını varlığını kontrol eder

    Arguments:
        dirpath {Path} -- Kontrol edilecek dizin

    Returns:
        bool -- Varsa True

    Examples:
        >>> has_codeofconductfile(Path('.'))
        False
    """
    filepath = codeofconductpath_for_dir(dirpath)
    return filepath.exists()


def has_contributingfile(dirpath: Path) -> bool:
    """Verilen dizinde CONTRIBUTING dosyasını varlığını kontrol eder

    Arguments:
        dirpath {Path} -- Kontrol edilecek dizin

    Returns:
        bool -- Varsa True

    Examples:
        >>> has_contributingfile(Path('docs'))
        True
    """
    filepath = contributingpath_for_dir(dirpath)
    return filepath.exists()


def has_licensefile(dirpath: Path) -> bool:
    """Verilen dizinde LICENSE dosyasını varlığını kontrol eder

    Arguments:
        dirpath {Path} -- Kontrol edilecek dizin

    Returns:
        bool -- Varsa True

    Examples:
        >>> has_licensefile(Path('.'))
        True
    """
    filepath = licensepath_for_dir(dirpath)
    return filepath.exists()


def is_markdownfile(filepath: Path) -> bool:
    """Verilen dosyanın markdown mı

    Arguments:
        filepath {Path} -- Dosya yolu objesi

    Returns:
        bool -- Markdown ise True

    Examples:
        >>> is_markdownfile(Path('docs/README.md'))
        True
        >>> is_markdownfile(Path('LICENSE'))
        False
    """
    return filepath.name[-3:] == ".md"


def is_readmefile(filepath: Path) -> bool:
    """Verilen dosyanın README olmasını kontrol eder

    Arguments:
        filepath {Path} -- Dosya yolu objesi

    Returns:
        bool -- Markdown ise True

    Examples:
        >>> is_readmefile(Path('docs/README.md'))
        True
        >>> is_readmefile(Path('LICENSE'))
        False
    """
    result = filepath.name == SpecialFile.README.value
    return result
