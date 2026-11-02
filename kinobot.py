import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Bot tokeni
TOKEN = "8568542464:AAGQqj2ybxRpMKrdOprDsWOcK_AfQMZBUXA"

# Telegram kanal username'i
CHANNEL_USERNAME = "@umid_kino"

# Siz yuborgan 2 ta Instagram sahifa havolalari
INSTAGRAM_URL_1 = "https://www.instagram.com/bakhr1dd1nov_21?srtk=eDBzYTRvaXJ2d21i&utm_source=qr"
INSTAGRAM_URL_2 = "https://www.instagram.com/fcgalaba_01?rpxt=eXhoaG5zd2g0d2w3&utm_source=qr"

# Adminlar ID raqamlari
ADMIN_IDS = [6971500711, 1774499608] 

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Bazani saqlash uchun fayl nomi
DB_FILE = "movies_db.json"

# Kinolarni fayldan o'qib olish
def load_movies():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

# Kinolarni faylga saqlash
def save_movies(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# Admin kino qo'shishi uchun holatlar (FSM)
class AdminStates(StatesGroup):
    waiting_for_code = State()

# Kanalga obuna bo'lganligini tekshiruvchi funksiya
async def check_user_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["creator", "administrator", "member"]:
            return True
        return False
    except Exception:
        return False

# /start komandasi
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer(
            "Assalomu alaykum, Admin! 🎬\n"
            "Yangi kino qo'shish uchun Menga shunchaki **kino (video) yuboring**."
        )
        return
    
    await message.answer(
        "Assalomu alaykum! Kinoni ko'rish uchun Instagram yoki TikTok'dan olgan kodni shu yerga yuboring.\n"
        "Masalan: <code>101</code>",
        parse_mode="HTML"
    )

# Admin video yuborganda uni ushlab qolish
@dp.message(F.video)
async def handle_admin_video(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    video_file_id = message.video.file_id
    await state.update_data(video_file_id=video_file_id)
    
    await message.answer("📥 Kino qabul qilindi. Endi bu kino uchun **kod** yuboring (masalan: <code>102</code>):", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_for_code)

# Admin kod kiritganda bazaga saqlash
@dp.message(AdminStates.waiting_for_code, F.text)
async def save_movie_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()
    video_file_id = data.get("video_file_id")
    
    movies = load_movies()
    movies[code] = video_file_id
    save_movies(movies)
    
    await state.clear()
    await message.answer(f"✅ Kino muvaffaqiyatli saqlandi!\n🔑 **Kodi:** <code>{code}</code>", parse_mode="HTML")

# Oddiy foydalanuvchilar kod yuborganda
@dp.message(F.text)
async def check_movie_code(message: types.Message):
    user_id = message.from_user.id
    code = message.text.strip()

    if user_id in ADMIN_IDS:
        await message.answer("⚠️ Kino qo'shish uchun avval botga **video yuboring**.")
        return

    is_subscribed = await check_user_subscription(user_id)

    if not is_subscribed:
        builder = InlineKeyboardBuilder()
        builder.button(text="📢 Telegram kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
        builder.button(text="📸 1-Instagram sahifaga obuna", url=INSTAGRAM_URL_1)
        builder.button(text="📸 2-Instagram sahifaga obuna", url=INSTAGRAM_URL_2)
        builder.button(text="✅ Tekshirish", callback_data=f"check_sub_{code}")
        builder.adjust(1)

        await message.answer(
            "⚠️ Kinoni olish uchun quyidagi shartlarni bajaring:\n\n"
            "1️⃣ Telegram kanalimizga obuna bo‘ling\n"
            "2️⃣ 1-Instagram sahifamizga obuna bo‘ling\n"
            "3️⃣ 2-Instagram sahifamizga obuna bo‘ling\n\n"
            "So'ngra <b>'Tekshirish'</b> tugmasini bosing:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        return

    movies = load_movies()
    if code in movies:
        await message.answer_video(
            video=movies[code],
            caption="🎬 Marhamat, kinoning to'liq versiyasi!"
        )
    else:
        await message.answer("❌ Bunday kod topilmadi. Iltimos, kodni to'g'ri kiritganingizni tekshiring.")

# "Tekshirish" tugmasi bosilganda
@dp.callback_query(F.data.startswith("check_sub_"))
async def process_check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    code = callback.data.split("_")[2]

    is_subscribed = await check_user_subscription(user_id)

    if is_subscribed:
        await callback.message.delete()
        movies = load_movies()
        if code in movies:
            await callback.message.answer_video(
                video=movies[code],
                caption="✅ Obuna tasdiqlandi! Marhamat, kino:"
            )
        else:
            await callback.message.answer("❌ Kino kodi topilmadi.")
    else:
        await callback.answer("⚠️ Siz hali Telegram kanalga obuna bo'lmadingiz!", show_alert=True)

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())