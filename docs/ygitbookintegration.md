---
description: "\U0001F91D GitHub projerini GitBook üzerinden sunmak için gerekli dönüşümleri yapar"
---

# 💫 YGitBookIntegration

## 🎌 Kullanım Notları

* 🔄 Github - GitBook entegrasyonu için `ygitbookintegration` komutu kullanılır
* 🆘 Kullanım detayları için `ygitbookintegration -h` yazın

> Komut olarak sadece yol verilirse, dizindeki yapılandırma dosyasına \(`.ygitbookintegration`\) göre çalışır

## 👨‍🔧 Entegrasyon Yapılandırması

Entegrasyon yapılandırması `.ygitbookintegration` dosyası içerisindeki yapı ile sağlanır

| Modül | Açıklama |
| :--- | :--- |
| `[integration "Kişisel not"]` | Entegrasyonu verilen argümanlara göre çalıştırır |
| `[submodule "kişisel not"]` | Verilen GitBook sitesinin içeriklerine bağlantı oluşturur |

## 📑 Yapılandırma Dosyası Örneği

```yaml
# ygitbookintegration'ı verilern argümanlara göre çalıştırır
# Detaylar: ygitbookintegration . -u olarak komutu çalıştırır
[integration "pre"]
    args = "-u"

# Verilen bilgiler doğrultusunda sitenin içeriklerini bağlantı oluşturur
# Detaylar: GitHub üzerinden url'deki SUMMARY'i içeriğini root'a göre düzenleyip, path'e yazar
[submodule "code/python.md"]
    description = 🐍 Python notlarım
    path = code/python.md
    url = https://github.com/YEmreAk/YPython
    root = https://python.yemreak.com
```

## 💖 Destek ve İletişim

​[​![Github](.gitbook/assets/github_32px%20%281%29.png)​](https://github.com/yedhrab) [​![LinkedIn](.gitbook/assets/linkedin_32px%20%283%29.png)​](https://www.linkedin.com/in/yemreak/) [​![Website](.gitbook/assets/geography_32px.png)​](https://yemreak.com/) [​![Mail](.gitbook/assets/gmail_32px%20%283%29.png)​](mailto:yemreak.com@gmail.com?subject=YGitBookIntegration%20%7C%20GitHub)​

​[​![Patreon](.gitbook/assets/become_a_patron_32px%20%281%29.png)](https://www.patreon.com/yemreak/)

## 🔏 Lisans

**The** [**Apache 2.0 License**](https://choosealicense.com/licenses/apache-2.0/) **©️ Yunus Emre Ak**

![YEmreAk](.gitbook/assets/ysigniture-trans%20%281%29.png)

