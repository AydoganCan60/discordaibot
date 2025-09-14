import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types

# .env dosyasını yükle
load_dotenv()

# API anahtarlarını çevre değişkenlerinden al
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY çevre değişkeni ayarlanmamış!")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN çevre değişkeni ayarlanmamış!")

# Gemini istemcisini ayarla
client = genai.Client(api_key=GEMINI_API_KEY)

# Konuşma geçmişi saklama (sunucu + kanal + kullanıcı bazında)
conversation_memory = {}
MAX_MEMORY_MESSAGES = 10  # Son 10 mesajı hatırla

def get_memory_key(guild_id: int, channel_id: int, user_id: int) -> str:
    """Güvenli hafıza anahtarı oluştur (sunucu/kanal/kullanıcı bazlı)"""
    return f"{guild_id}_{channel_id}_{user_id}"

# Discord Bot ayarları
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix="!", 
    intents=intents,
    allowed_mentions=discord.AllowedMentions.none()  # Güvenlik: @everyone/@here engelle
)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} olarak giriş yaptı!")
    print(f"Bot {len(bot.guilds)} sunucuda aktif.")

def get_conversation_context(memory_key: str) -> str:
    """Kullanıcının konuşma geçmişini formatla"""
    if memory_key not in conversation_memory or not conversation_memory[memory_key]:
        return ""
    
    context = "\n\nÖnceki konuşma geçmişi:\n"
    for msg in conversation_memory[memory_key]:
        context += f"Kullanıcı: {msg['user']}\nAI: {msg['ai']}\n\n"
    
    return context

def add_to_memory(memory_key: str, user_message: str, ai_response: str):
    """Konuşmayı hafızaya ekle"""
    if memory_key not in conversation_memory:
        conversation_memory[memory_key] = []
    
    # Kullanıcı mesajını da kısalt (güvenlik için)
    conversation_memory[memory_key].append({
        'user': user_message[:500],  # Kullanıcı mesajını kısalt
        'ai': ai_response[:500]  # AI cevabını kısalt
    })
    
    # Fazla eski mesajları sil
    if len(conversation_memory[memory_key]) > MAX_MEMORY_MESSAGES:
        conversation_memory[memory_key] = conversation_memory[memory_key][-MAX_MEMORY_MESSAGES:]

@bot.command(name='sor')
@commands.cooldown(1, 3, commands.BucketType.user)  # 3 saniyede 1 komut
async def sor(ctx, *, mesaj: str = ""):
    """AI ile sohbet et - !sor [mesajın]"""
    
    if not mesaj:
        await ctx.send("Lütfen bir mesaj yazın! Örnek: `!sor Python hakkında bilgi ver`")
        return
    
    # DM kontrolü
    if ctx.guild is None:
        await ctx.send("Bu komut sadece sunucu kanallarında çalışır. Hafıza özelliği için bir sunucuda deneyin!")
        return
    
    # Güvenli hafıza anahtarı oluştur
    memory_key = get_memory_key(ctx.guild.id, ctx.channel.id, ctx.author.id)
    
    # Güvenlik için mesaj uzunluğunu sınırla
    mesaj = mesaj[:1000]  # Token kullanımını kontrol et
    
    try:
        # Discord'da yazıyor göstergesi
        async with ctx.typing():
            # Konuşma geçmişini al
            context = get_conversation_context(memory_key)
            
            # Tam prompt'u oluştur
            full_prompt = f"{context}\n\nKullanıcının yeni sorusu: {mesaj}\n\nLütfen önceki konuşma geçmişini dikkate alarak doğal bir şekilde cevap ver. Eğer önceki konuşmalarla ilgili bir soru soruyorsa, o bilgileri kullan."
            
            # Gemini API çağrısını async yap (performans için) - 20 saniye timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=full_prompt if context else mesaj
                    )
                ),
                timeout=20.0
            )
            
            cevap = response.text if response.text else "Üzgünüm, cevap üretemadım."
            
            # Konuşmayı hafızaya ekle
            add_to_memory(memory_key, mesaj, cevap)
            
            # Discord mesaj sınırı 2000 karakter - güvenli çözme
            if len(cevap) > 1900:  # Güvenlik marjı
                # İlk mesaj için prefix hesapla
                first_prefix = "**Cevap:**\n"
                first_max = 2000 - len(first_prefix)
                
                # Sonraki mesajlar için prefix hesapla  
                next_prefix = "**Devamı:**\n"
                next_max = 2000 - len(next_prefix)
                
                # İlk chunk
                first_chunk = cevap[:first_max]
                await ctx.send(f"{first_prefix}{first_chunk}")
                
                # Kalan kısımları böl
                remaining = cevap[first_max:]
                chunks = [remaining[i:i+next_max] for i in range(0, len(remaining), next_max)]
                
                for chunk in chunks:
                    await ctx.send(f"{next_prefix}{chunk}")
            else:
                await ctx.send(cevap)

    except asyncio.TimeoutError:
        await ctx.send("AI yanıt verme süresi aşıldı. Lütfen tekrar deneyin.")
        print(f"Timeout: Kullanıcı {ctx.author} için Gemini API zaman aşımı")
    except Exception as e:
        await ctx.send("Bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
        print(f"Hata detayı - Kullanıcı: {ctx.author}, Hata: {e}")

@bot.command(name='hafızaunut')
@commands.cooldown(1, 5, commands.BucketType.user)  # 5 saniyede 1
async def unutkafami(ctx):
    """Konuşma geçmişini temizle"""
    if ctx.guild is None:
        await ctx.send("Bu komut sadece sunucu kanallarında çalışır!")
        return
        
    memory_key = get_memory_key(ctx.guild.id, ctx.channel.id, ctx.author.id)
    
    if memory_key in conversation_memory and conversation_memory[memory_key]:
        conversation_memory[memory_key] = []
        await ctx.send("✅ Bu kanaldaki konuşma geçmişin temizlendi! Yeni bir sohbet başlayabiliriz.")
    else:
        await ctx.send("Zaten bu kanalda hafızamda bir şey yok! 😄")

@bot.command(name='hafızam')
async def hafizam(ctx):
    """Mevcut konuşma geçmişini göster (özel mesaj olarak)"""
    if ctx.guild is None:
        await ctx.send("Bu komut sadece sunucu kanallarında çalışır!")
        return
        
    memory_key = get_memory_key(ctx.guild.id, ctx.channel.id, ctx.author.id)
    
    if memory_key not in conversation_memory or not conversation_memory[memory_key]:
        await ctx.send("Henüz bu kanalda hiçbir konuşma yapmadık! `!sor` ile başlayalım.")
        return
    
    embed = discord.Embed(
        title=f"🧠 {ctx.channel.name} Kanalındaki Hafızam",
        color=0x3498db
    )
    
    for i, msg in enumerate(conversation_memory[memory_key][-5:], 1):  # Son 5'ini göster
        embed.add_field(
            name=f"Konuşma {i}",
            value=f"**Sen:** {msg['user'][:100]}...\n**Ben:** {msg['ai'][:100]}...",
            inline=False
        )
    
    embed.set_footer(text=f"Toplam {len(conversation_memory[memory_key])} konuşma bu kanalda hafızamda")
    
    # Gizlilik için özel mesaj gönder
    try:
        await ctx.author.send(embed=embed)
        await ctx.send("📩 Hafızamı özel mesaj olarak gönderdim!")
    except discord.Forbidden:
        await ctx.send("❌ Özel mesaj gönderemiyorum. DM'lerini aç!")

@bot.command(name='yardım')
async def yardim(ctx):
    """Bot komutları hakkında bilgi"""
    embed = discord.Embed(
        title="🤖 AI Bot Komutları",
        description="Bu bot Google Gemini AI kullanarak sorularınızı yanıtlar ve konuşma geçmişinizi hatırlar!",
        color=0x00ff00
    )
    embed.add_field(
        name="!sor [mesaj]",
        value="AI ile sohbet et. Geçmiş konuşmaları hatırlar! Örnek: `!sor Python nasıl öğrenilir?`",
        inline=False
    )
    embed.add_field(
        name="!hafızam",
        value="Son konuşma geçmişini özel mesaj olarak gösterir",
        inline=False
    )
    embed.add_field(
        name="!hafızaunut",
        value="Bu kanaldaki konuşma geçmişini temizler",
        inline=False
    )
    embed.add_field(
        name="!yardım",
        value="Bu yardım mesajını gösterir",
        inline=False
    )
    embed.set_footer(text="Google Gemini AI ile güçlendirilmiştir - Artık hafızalı! 🧠")
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Hata yönetimi"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Bilinmeyen komut! `!yardım` yazarak mevcut komutları görebilirsin.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Eksik parametre! Komut kullanımı için `!yardım` yazın.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Çok hızlı! {error.retry_after:.1f} saniye sonra tekrar deneyin.")
    else:
        await ctx.send("Bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
        print(f"Komut hatası - Kullanıcı: {ctx.author}, Hata: {error}")

if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Bot başlatılamadı: {e}")
