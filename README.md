✨ Özellikler:
🧠 AI Entegrasyonu

    Google Gemini 2.5 Flash modeli entegrasyonu
    Bağlamsal ve akıllı cevaplar
    Türkçe dil desteği

💾 Hafıza Sistemi

    Kanal bazında konuşma geçmişi saklama
    Son 10 konuşmayı otomatik hatırlama
    Çapraz sunucu/kanal gizlilik koruması
    Otomatik hafıza yönetimi

🔒 Güvenlik

    Rate limiting (spam koruması)
    @everyone/@here mention engelleme
    Güvenli API anahtar yönetimi
    Hata logları gizlilik koruması
    DM tabanlı güvenli hafıza paylaşımı

⚡ Performans

    Asenkron API çağrıları
    20 saniye API timeout
    Discord 2000 karakter limit uyumu
    Non-blocking operasyonlar

🛠️ Teknolojiler:

    Python 3.11
    discord.py - Discord API wrapper
    google-genai - Google Gemini AI SDK
    python-dotenv - Environment yönetimi
    asyncio - Asenkron programlama

📋 Gereksinimler:

discord.py>=2.6.3
google-genai>=1.36.0
python-dotenv>=1.1.1

🚀 Kurulum:
1. Projeyi Klonlayın:

git clone [repo-url]
cd discord-ai-bot

2. Gerekli Paketleri Yükleyin:

pip install -r requirements.txt

3. Environment Değişkenlerini Ayarlayın:

.env dosyası oluşturun:

DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key

4. Botu Çalıştırın:

python main.py

🎮 Kullanım:
Temel Komutlar:

    !kodlaai [mesaj] - AI ile sohbet et
    !hafızam - Konuşma geçmişini görüntüle
    !unutkafamı - Hafızayı temizle
    !yardım - Komut listesi

Örnek Kullanım:

!kodlaai Python nasıl öğrenilir?
!kodlaai Az önce ne konuştuk?
!hafızam
!unutkafamı

🔧 Konfigürasyon:
Discord Bot Ayarları:

    Discord Developer Portal'dan bot oluşturun
    Bot token'ını alın
    Gerekli intent'leri aktif edin (Message Content Intent)

Gemini API Ayarları:

    Google AI Studio'dan API key alın
    Environment değişkenine ekleyin

📊 Sistem Mimarisi:
Hafıza Sistemi:

    Guild ID + Channel ID + User ID tabanlı scoping
    Maksimum 10 konuşma/kanal
    500 karakter mesaj limiti
    Otomatik cleanup

Güvenlik Mimarileri:

    Rate limiting: 3 saniye/komut
    Input validation ve sanitization
    Cross-channel data leak koruması
    Secure error handling

🚀 Deployment (Replit):

Bu proje Replit platformunda optimize edilmiştir:

    Otomatik environment yönetimi
    Integrated secrets management
    One-click deployment
    7/24 hosting

🤝 Katkıda Bulunma:

    Fork edin
    Feature branch oluşturun (git checkout -b feature/YeniOzellik)
    Commit edin (git commit -am 'Yeni özellik eklendi')
    Push edin (git push origin feature/YeniOzellik)
    Pull Request oluşturun

📄 Lisans:

MIT License
🆘 Destek:

    Discord sunucumuz: [link]
    Issues: GitHub Issues
    Email: [email]

🔄 Sürüm Geçmişi:

    v1.0.0: Temel AI entegrasyonu
    v1.1.0: Hafıza sistemi eklendi
    v1.2.0: Güvenlik iyileştirmeleri
