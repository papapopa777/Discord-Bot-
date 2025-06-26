import discord
from discord.ext import commands
from discord import app_commands
import random, asyncio

# ------------------ Bot Setup ------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def is_guild_owner():
    return app_commands.check(lambda i: i.user.id == i.guild.owner_id)

# ------------------ فان ------------------
jokes = [
    "یه پایتونیست رفت کافی‌شاپ، گفت: یه قهوه بدون باگ لطفاً!",
    "تو جهنم، برنامه‌نویسا حلقه بی‌نهایت می‌زنن 😂",
    "ربات چرا افسرده بود؟ چون دیگه باهاش صحبت نمی‌کردن!",
]

memes = [
    "https://i.imgflip.com/30b1gx.jpg",
    "https://i.redd.it/a9j3l.jpg",
]

@bot.tree.command(name="joke", description="یه جوک بامزه")
async def joke_cmd(i: discord.Interaction):
    await i.response.send_message(random.choice(jokes))

@bot.tree.command(name="meme", description="میم تصادفی")
async def meme_cmd(i: discord.Interaction):
    await i.response.send_message(random.choice(memes))

@bot.tree.command(name="coin", description="شیر یا خط")
async def coin_cmd(i: discord.Interaction):
    await i.response.send_message(random.choice(["🪙 شیر", "🪙 خط"]))

@bot.tree.command(name="dice", description="تاس بریز")
async def dice_cmd(i: discord.Interaction):
    await i.response.send_message(str(random.randint(1, 6)))

# ------------------ پیام‌دهی مخفی ------------------
@bot.tree.command(name="say", description="فرستادن پیام در همین چنل توسط بات")
@is_guild_owner()
async def say(i: discord.Interaction, message: str):
    await i.response.defer()
    await i.channel.send(message)

@bot.tree.command(name="dm", description="فرستادن پیام شخصی به کاربر توسط بات")
@is_guild_owner()
async def dm(i: discord.Interaction, user: discord.User, message: str):
    await i.response.defer()
    try:
        await user.send(message)
    except:
        pass

@bot.tree.command(name="announce", description="ارسال پیام فقط در همین چنل")
@is_guild_owner()
async def announce(i: discord.Interaction, message: str):
    await i.response.defer()
    await i.channel.send(f"📢 {message}")

# ------------------ تیکت ------------------
@bot.tree.command(name="ticket", description="ساخت پنل تیکت با رول پشتیبانی")
@is_guild_owner()
async def ticket_cmd(i: discord.Interaction, پشتیبانی: discord.Role):
    embed = discord.Embed(
        title="🎫 سیستم تیکت",
        description="برای ایجاد تیکت روی دکمه زیر کلیک کنید.",
        color=0x00ffcc
    )
    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="📩 ساخت تیکت",
            style=discord.ButtonStyle.primary,
            custom_id=f"create_ticket:{پشتیبانی.id}"
        )
    )
    await i.response.defer()
    await i.channel.send(embed=embed, view=view)

# ------------------ گیوای با دکمه ------------------
@bot.tree.command(name="giveaway", description="ساخت گیوای فارسی با دکمه 🎁")
@is_guild_owner()
async def giveaway_cmd(i: discord.Interaction, دقیقه: int, جایزه: str):
    embed = discord.Embed(
        title="🎁 گیوای!",
        description=f"🏆 جایزه: **{جایزه}**\n⏳ زمان: {دقیقه} دقیقه\nبرای شرکت روی دکمه کلیک کن!",
        color=0xff66ff
    )
    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="🎉 شرکت در گیوای",
            style=discord.ButtonStyle.success,
            custom_id="join_giveaway"
        )
    )
    await i.response.defer()
    msg = await i.channel.send(embed=embed, view=view)
    bot.giveaway_participants = []

    async def wait_and_pick():
        await asyncio.sleep(دقیقه * 60)
        if bot.giveaway_participants:
            winner = random.choice(bot.giveaway_participants)
            await msg.channel.send(f"🏆 برنده‌ی گیوای: {winner.mention} — تبریک! 🎉")
        else:
            await msg.channel.send("❌ کسی شرکت نکرد!")

    asyncio.create_task(wait_and_pick())

# ------------------ مدیریت چنل و پرمیشن ------------------
@bot.tree.command(name="reset_channel", description="پاکسازی کامل چنل و ساخت مجدد")
@is_guild_owner()
async def reset_ch(i: discord.Interaction):
    old_channel = i.channel
    name = old_channel.name
    category = old_channel.category
    position = old_channel.position
    await i.response.send_message("♻️ در حال ریست کامل کانال...", ephemeral=True)
    await old_channel.delete()
    new_channel = await i.guild.create_text_channel(name=name, category=category, position=position)
    await new_channel.send("✅ این کانال به‌طور کامل ریست شد.")

@bot.tree.command(name="permission", description="تغییر پرمیشن برای همه چنل‌ها")
@is_guild_owner()
async def set_perm(i: discord.Interaction, perm: str, value: str):
    v = True if value == "true" else False if value == "false" else None
    if v is None:
        return await i.response.send_message("⚠ مقدار باید 'true' یا 'false' باشه", ephemeral=True)
    for ch in i.guild.channels:
        await ch.set_permissions(i.guild.default_role, overwrite=discord.PermissionOverwrite(**{perm: v}))
    await i.response.send_message(f"✅ پرمیشن `{perm}` برای همه چنل‌ها شد `{value}`", ephemeral=True)

@bot.tree.command(name="category", description="تنظیم پرمیشن روی یک کتگوری")
@is_guild_owner()
async def category_perm(i: discord.Interaction, category: discord.CategoryChannel, perm: str, value: str):
    v = True if value == "true" else False if value == "false" else None
    if v is None:
        return await i.response.send_message("⚠ مقدار باید 'true' یا 'false' باشه", ephemeral=True)
    for ch in category.channels:
        await ch.set_permissions(i.guild.default_role, overwrite=discord.PermissionOverwrite(**{perm: v}))
    await i.response.send_message(f"📁 پرمیشن `{perm}` برای کتگوری `{category.name}` تنظیم شد.", ephemeral=True)

# ------------------ هندل دکمه‌ها ------------------
@bot.event
async def on_interaction(i: discord.Interaction):
    if i.type != discord.InteractionType.component:
        return

    cid = i.data.get("custom_id")

    # 🎫 تیکت
    if cid and cid.startswith("create_ticket:"):
        role_id = int(cid.split(":")[1])
        staff_role = i.guild.get_role(role_id)
        overwrites = {
            i.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            i.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        ch = await i.guild.create_text_channel(f"ticket-{i.user.name}", overwrites=overwrites)
        embed = discord.Embed(description="✅ تیکت ساخته شد. لطفاً منتظر پاسخ باشید.", color=0x00ffcc)
        close_btn = discord.ui.Button(label="❌ بستن تیکت", style=discord.ButtonStyle.danger, custom_id="close_ticket")
        view = discord.ui.View()
        view.add_item(close_btn)
        await ch.send(content=f"{i.user.mention}", embed=embed, view=view)
        await i.response.send_message("✅ تیکت ساخته شد", ephemeral=True)

    elif cid == "close_ticket":
        await i.response.send_message("⏳ در حال بستن تیکت...")
        await asyncio.sleep(2)
        await i.channel.delete()

    # 🎉 گیوای
    elif cid == "join_giveaway":
        if not hasattr(bot, "giveaway_participants"):
            bot.giveaway_participants = []
        if i.user not in bot.giveaway_participants:
            bot.giveaway_participants.append(i.user)
            await i.response.send_message("✅ شما در گیوای شرکت کردید!", ephemeral=True)
        else:
            await i.response.send_message("⚠️ شما قبلاً شرکت کرده‌اید!", ephemeral=True)

# ------------------ اجرا ------------------
@bot.event
async def on_ready():
    print(f"✅ Bot is ready as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔧 Synced {len(synced)} commands.")
    except Exception as e:
        print("❌ Sync error:", e)

# 🟢 اجرای بات با توکن مستقیم
bot.run(os.getenv("TOKEN"))
