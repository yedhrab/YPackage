import configparser
import urllib.request


def readFileWithURL(rawUrl):
    return urllib.request.urlopen(rawUrl).read()


def getContent(path) -> str:
    print(url)
    username, repo = path.split("/")[-2:]
    rawPath = f"https://raw.githubusercontent.com/{username}/{repo}/master/SUMMARY.md"
    content = readFileWithURL(rawPath)
    return content


SUBMODULE_FILE = ".ygitbookintegration"

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(SUBMODULE_FILE)

for section in config.sections():
    if section.split()[0] == "integration":
        args = config[section]["args"]
