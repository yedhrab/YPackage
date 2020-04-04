import logging
import re
from configparser import ConfigParser
from pathlib import Path
from typing import AnyStr, List, Pattern, Tuple, Any

logger = logging.getLogger(__name__)


def repr_class_variables(anyclass: Any):
    return ', '.join([f"{key}={repr(value)}" for key, value in vars(anyclass).items()])


class Base:

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return type(self).__name__ + "(" \
            + ', '.join([f"{key}={repr(value)}" for key, value in vars(self).items()]) \
            + ")"

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        items = vars(self)
        for key, value in vars(other).items():
            if not items[key] == value:
                return False

        return True


class Options(Base):

    LOG_LOAD_TEMPLATE = "{} ile komut çalıştırılıyor"
    LOG_LOAD_SYSTEM_ARGS = "Parametreler"

    def load_system_args(self, workdir: Path):
        raise NotImplementedError

    def log_load(self, load_type: str):
        message = self.LOG_LOAD_TEMPLATE.format(load_type)
        message += "\n"
        message += repr(self)

        logger.debug(message)

    @classmethod
    def from_system_args(cls, workdir: Path):
        raise NotImplementedError


def initialize_logging(level=logging.INFO):
    import coloredlogs

    if level == logging.DEBUG:
        log_format = r"%(name)s[%(process)d] %(levelname)s %(message)s"
    else:
        log_format = r"%(levelname)s %(message)s"

    coloredlogs.install(fmt=log_format, level=level)
    logger.debug("Renkli raporlayıcı aktif edildi")


def exit_if_not(condition, message=None):
    if not condition:
        exit(message)


def list_difference(list1: list, list2: list, safe: bool = True) -> list:
    """İki listenin farkını alır

    Arguments:
            list1 {list} -- Ana liste
            list2 {list} -- Çıkarılacak liste

    Keyword Arguments:
            safe {bool} -- Çıkarma işlemi sırasında verilerin sırasını korur ve tekrarları \
                                kaldırmaz (default: {True})

    Returns:
            list -- Sonuç listesi
    """
    if safe:
        list2 = set(list2)
        return [x for x in list1 if x not in list2]
    else:
        return list(set(list1) - set(list2))


def prod(numbers: list) -> int:
    """Verilen listedeki tüm elemanları çarpar

    Arguments:
            numbers {list} -- Sayı listesi

    Returns:
            int -- Çarpımın sonucu
    """
    result = 1
    for number in numbers:
        result *= number
    return result


def read_config(configpath: Path) -> dict:
    """Read configuration file

    Arguments:
        cpath {Path} -- Configuration file path

    Returns:
        dict -- Dictionary that contains config keys
    """
    try:
        config = ConfigParser(inline_comment_prefixes="#")
        config.read(configpath, encoding="utf-8")
    except Exception as e:
        logger.error(f"Cannot read config file {e}")
        return {}

    return config


def sort(string: str) -> str:
    lines = string.split("\n")
    lines.sort()
    result = "\n".join(lines)
    return result


def parse_to_lines(content: str) -> List[str]:
    return content.split("\n")


def merge_lines(lines: List[str]) -> str:
    return "\n".join(lines)


def rename_string(regex: Pattern[AnyStr], to: str, string: str) -> str:
    """Metni yeniden adlandırma

    Arguments:
        regex {Pattern[AnyStr]} -- Aranan regex
        to {str} -- Yeni isim
        path {str} -- Yol

    Returns:
        bool -- Adlandırma yapıldıysa true
    """
    result = regex.search(string)
    if result:
        if result.lastindex:
            for i in range(result.lastindex + 1):
                to = to.replace(f"${i}", result[i])

        string = regex.sub(to, string)

    return string


def update_string_by_indexes(string: str, content: str, start_pos: int, end_pos: int) -> str:
    """String içerisideki verilen konumdaki metni değiştirme

    Arguments:
        string {str} -- Eklenecek string
        content {str} -- Asıl içerik
        start_pos {int} -- Başlangıç indeksi
        end_pos {int} -- Bitiş indeksi

    Returns:
        str -- Eklenme yapılmış string

    Examples:
        >>> update_string_by_indexes('Selam', 'Merhaba YEmreAk', 0, 7)
        'Selam YEmreAk'
    """
    new_content = content[:start_pos] + string + content[end_pos:]
    return new_content


def find_substring(content: str, start_pos: int, end_pos: int) -> str:
    """Metin içerisinde metin arama

    Arguments:
        content {str} -- Metin
        start_pos {int} -- Başlangıç indeksi (dahil)
        end_pos {int} -- Bitiş indeksi (dahil değil)

    Returns:
        str -- Bulunan metin

    Examles:
        >>> find_substring('YEmreAk', 1, 5)
        'Emre'
    """
    new_content = content[start_pos:end_pos]
    return new_content


def update_string_by_stringindexes(
        string: str,
        content: str,
        start_string: str,
        end_string: str
) -> str:
    """Metnin içerisideki indekslerin arasındaki metni değiştirme

    Arguments:
        string {str} -- Yeni metin
        content {str} -- Asıl içerik
        start_string {str} -- Başlangıç metni
        end_string {str} -- Bitiş metni

    Returns:
        str -- Değiştirilmiş içerik

    Examples:
        >>> update_string_by_stringindexes( \
                'YPackage',                 \
                'Merhaba YEmreAk Merhaba',  \
                'Merhaba ',                 \
                ' Merhaba'                  \
            )
        'Merhaba YPackage Merhaba'
        >>> update_string_by_stringindexes( \
                'YPackage',                 \
                'Merhaba YEmreAk Merhaba',  \
                'Heey ',                    \
                ' Merhaba'                  \
            )
        'Merhaba YEmreAk Merhaba'
        >>> update_string_by_stringindexes( \
                'YPackage',                 \
                'Merhaba YEmreAk Merhaba',  \
                'Merhaba',                  \
                'Merhaba'                   \
            )
        'MerhabaYPackageMerhaba'
    """

    positions = position_index_from_string_index(content, start_string, end_string)
    for start_pos, end_pos in positions:
        content = update_string_by_indexes(string, content, start_pos, end_pos)

    return content


def find_substrings_by_strings(
    content: str,
    start_index: str,
    end_index: str
) -> List[str]:
    """Metnin içerisideki indekslerin arasındaki metinleri alma

    Arguments:
        content {str} -- Metin
        start_string {str} -- Başlangıç metni
        end_string {str} -- Bitiş metni

    Returns:
        List[str] -- Bulunan metinlerin listesi

    Examles:
        >>> find_substrings_by_strings('- Yeni - A - Yapıt -', '-', '-')
        [' Yeni ', ' A ', ' Yapıt ']
        >>> find_substrings_by_strings('Sıkıcı bir gün oldu', ' ', ' ')
        ['bir', 'gün']
        >>> find_substrings_by_strings('Sıkıcı _bir gün_ oldu', '_', '_')
        ['bir gün']
    """
    substrings = []

    positions = position_index_from_string_index(content, start_index, end_index)
    for start_pos, end_pos in positions:
        substring = find_substring(content, start_pos, end_pos)
        substrings.append(substring)

    return substrings


def position_index_from_string_index(
    content: str,
    start_string: str,
    end_string: str
) -> List[Tuple[int, int]]:
    spos = [m.start() + len(start_string) for m in re.finditer(start_string, content)]
    epos = [m.start() for m in re.finditer(end_string, content)]

    positions = match_start_and_end_positions(spos, epos)
    return positions


def match_start_and_end_positions(spos: list, epos: list) -> List[Tuple[int, int]]:
    """[summary]

    Arguments:
        spos {list} - - [description]
        epos {list} - - [description]

    Returns:
        List[Tuple[int, int]] - - [description]

    Examples:
        >> > match_start_and_end_positions(
            [1, 3, 5],
            [2, 4, 7]
            )
        [(1, 2), (3, 4), (5, 7)]
        >> > match_start_and_end_positions(
            [1, 3, 5],
            [1, 5, 9]
            )
        [(1, 5), (5, 9)]
        >> > match_start_and_end_positions(
            [131],
            [130, 275]
            )
        [(131, 275)]
    """
    positions = []

    istart, iend = 0, 0
    while istart < len(spos):
        if istart != 0 and spos[istart] < epos[iend - 1]:
            istart += 1
            continue

        while iend < len(epos) and not (spos[istart] < epos[iend]):
            iend += 1

        if not (iend < len(epos)):
            break

        positions.append((spos[istart], epos[iend]))
        istart += 1
        iend += 1

    return positions


def has_indexes(content: str, start_string: str, end_string: str) -> bool:
    positions = position_index_from_string_index(content, start_string, end_string)
    return bool(positions)
