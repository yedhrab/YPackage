# 📦 YPackage

Kişisel python modüllerim

- 📦 [PYPI](https://pypi.org/project/ypackage/)
- 🐙 [Github](https://github.com/yedhrab/YPackage)

> ✨ Yenilikler için [CHANAGELOG](https://github.com/yedhrab/YPackage/blob/master/CHANGELOG.md) alanına bakın.

## 💫 Entegrasyon Scripti

- Github - GitBook entegrasyonu için `ygitbookintegration` komutu kullanılır
- Kullanım detayları için `ygitbookintegration -h` yazın

> Komut olarak sadece yol verilirse, dizindeki yapılandırma dosyasına (`.ygitbookintegration`) göre çalışır

### 👨‍🔧 Entegrasyon Yapılandırması

Entegrasyon yapılandırması `.ygitbookintegration` dosyası içerisindeki yapı ile sağlanır

| Modül                         | Açıklama                                                  |
| ----------------------------- | --------------------------------------------------------- |
| `[integration "Kişisel not"]` | Entegrasyonu verilen argümanlara göre çalıştırır          |
| `[submodule "kişisel not"]`   | Verilen GitBook sitesinin içeriklerine bağlantı oluşturur |

### 📑 Yapılandırma Dosyası Örneği

```ini
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

## 👨‍💻 Geliştirici Notları

Temel kullanım `import ypackage` şeklindedir ve modüllere `ypackage.<modül>` şeklinde erişilir.

| Modül        | Açıklama                                 |
| ------------ | ---------------------------------------- |
| `common`     | 🌟 Sık kullandığum metotlar              |
| `filesystem` | 📂 Dosya işlemleri                       |
| `gitbook`    | 📖 GitBook için scriptlerim              |
| `github`     | 🐙 GitHub işlemleri                      |
| `integrate`  | 💫 Entegrasyon işlemleri                 |
| `markdown`   | 📑 Markdown scriptlerim                  |
| `markdown`   | 💎 Regex scriptlerim (yapılm aşamasında) |

## 💖 Destek ve İletişim

**The [MIT License](https://choosealicense.com/licenses/mit/) &copy; Yunus Emre Ak**

[![Github](https://drive.google.com/uc?id=1PzkuWOoBNMg0uOMmqwHtVoYt0WCqi-O5)][github]
[![LinkedIn](https://drive.google.com/uc?id=1hvdil0ZHVEzekQ4AYELdnPOqzunKpnzJ)][linkedin]
[![Website](https://drive.google.com/uc?id=1wR8Ph0FBs36ZJl0Ud-HkS0LZ9b66JBqJ)][website]
[![Mail](https://drive.google.com/uc?id=142rP0hbrnY8T9kj_84_r7WxPG1hzWEcN)][mail]
[![Destek](https://drive.google.com/uc?id=1zyU7JWlw4sJTOx46gJlHOfYBwGIkvMQs)][bağış anlık]

[![Patreon](https://drive.google.com/uc?id=11YmCRmySX7v7QDFS62ST2JZuE70RFjDG)][bağış aylık]

<!-- İletişim -->

[mail]: mailto::yedhrab@gmail.com?subject=YPackage%20%7C%20Github
[github]: https://github.com/yedhrab
[website]: https://yemreak.com
[linkedin]: https://www.linkedin.com/in/yemreak/
[bağış anlık]: https://gogetfunding.com/yemreak/
[bağış aylık]: https://www.patreon.com/yemreak/

<!-- İletişim Sonu -->

[geliştiriciler için api yayınlayan yerli girişim ve şirket listesi]: https://webrazzi.com/2017/07/17/uygulama-programlama-arayuzu-api/
