import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# 1. BOT TOKEN
TOKEN = "8973350137:AAHcG20ks7hnXZmMfRMRDqd8QBAf-D74TCM"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# O'qituvchi (Sizning) Telegram ID raqamingiz
TEACHER_ID = 6971500711

# 2. O'QUVCHILAR BAZASI
students_db = {
    "201": {"name": "Murodov O‘tabek", "parent_id": None, "paid": False, "score": 0},
    "202": {"name": "Alisherov Shohmalik", "parent_id": None, "paid": False, "score": 0},
    "203": {"name": "Shonazarov Asror", "parent_id": None, "paid": False, "score": 0},
    "204": {"name": "Murtozayeva Shahnoz", "parent_id": None, "paid": False, "score": 0},
    "205": {"name": "Normurodov Bunyod", "parent_id": None, "paid": False, "score": 0},
    "206": {"name": "Alisherov Humoyun", "parent_id": None, "paid": False, "score": 0},
    "207": {"name": "Yo‘ldoshev Asilbek", "parent_id": None, "paid": False, "score": 0},
    "208": {"name": "Haqnazarov Hayotbek", "parent_id": None, "paid": False, "score": 0},
    "209": {"name": "Ro‘ziyev Zafar", "parent_id": None, "paid": False, "score": 0},
    "210": {"name": "Ro‘zimurodova Nozima", "parent_id": None, "paid": False, "score": 0},
    "211": {"name": "Shavkatova Gulina", "parent_id": None, "paid": False, "score": 0},
    "212": {"name": "Nurmamatov Shoxjahon", "parent_id": None, "paid": False, "score": 0},
    "213": {"name": "Murodova Farzona", "parent_id": None, "paid": False, "score": 0},
    "214": {"name": "Anvarov Adiz", "parent_id": None, "paid": False, "score": 0},
    "215": {"name": "Ravshanova Diana", "parent_id": None, "paid": False, "score": 0},
    "216": {"name": "Erdonayev Sardor", "parent_id": None, "paid": False, "score": 0},
}

# O'qituvchi uchun pastki menyu tugmalari
teacher_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Yo'qlama / Natija yuborish"), KeyboardButton(text="📋 O'quvchilar ro'yxati")],
        [KeyboardButton(text="💳 To'lovni belgilash"), KeyboardButton(text="🏆 Reyting")]
    ],
    resize_keyboard=True
)

# Bot holatlarini boshqarish
class ParentAuth(StatesGroup):
    waiting_for_code = State()

class TeacherActions(StatesGroup):
    waiting_for_attendance_code = State()
    waiting_for_score = State()
    waiting_for_note = State()

class PaymentActions(StatesGroup):
    waiting_for_payment_code = State()

# --- START BUYRUG'I ---
@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id == TEACHER_ID:
        await message.answer(
            "👋 Xush kelibsiz, Ustoz!\n"
            "Quyidagi tugmalardan birini tanlang:",
            reply_markup=teacher_keyboard
        )
    else:
        await message.answer("Xush kelibsiz! Farzandingizga berilgan maxsus KODni kiriting:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(ParentAuth.waiting_for_code)

# --- OTA-ONA KODNI KIRITGANDA ---
@dp.message(ParentAuth.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    
    if code in students_db:
        students_db[code]["parent_id"] = message.from_user.id
        student_name = students_db[code]["name"]
        await message.answer(f"✅ Muvaffaqiyatli ulandingiz! Endi siz {student_name} ning natijalarini qabul qilasiz.")
        await state.clear()
    else:
        await message.answer("❌ Noto'g'ri kod! Iltimos, o'qituvchidan olingan kodni qayta kiriting.")

# --- TUGMALAR BILAN ISHLASH (O'QITUVCHI UCHUN) ---

@dp.message(F.text == "📋 O'quvchilar ro'yxati")
async def show_students_btn(message: types.Message):
    if message.from_user.id != TEACHER_ID:
        return
    
    text = "📋 **O'quvchilar ro'yxati va kodlari:**\n\n"
    for code, info in students_db.items():
        status = "🟢 Ulangan" if info["parent_id"] else "🔴 Ulanmagan"
        pay_status = "💳 To'lagan" if info["paid"] else "⏳ To'lamagan"
        text += f"Kod: `{code}` | {info['name']} | {status} | {pay_status} | 🏆 {info['score']} ball\n"
    
    await message.answer(text, parse_mode="Markdown", reply_markup=teacher_keyboard)

@dp.message(F.text == "🏆 Reyting")
async def show_rating_btn(message: types.Message):
    if message.from_user.id != TEACHER_ID:
        return
    
    sorted_students = sorted(students_db.items(), key=lambda x: x[1]["score"], reverse=True)
    
    text = "🏆 **O'quvchilar reytingi:**\n\n"
    for i, (code, info) in enumerate(sorted_students, 1):
        text += f"{i}. {info['name']} — {info['score']} ball\n"
        
    await message.answer(text, parse_mode="Markdown", reply_markup=teacher_keyboard)

# --- TO'LOVNI BOSHQARISH ---
@dp.message(F.text == "💳 To'lovni belgilash")
async def start_payment_btn(message: types.Message, state: FSMContext):
    if message.from_user.id != TEACHER_ID:
        return
    await message.answer("To'lov qilgan o'quvchining KODini kiriting (masalan: 201):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(PaymentActions.waiting_for_payment_code)

@dp.message(PaymentActions.waiting_for_payment_code)
async def process_payment(message: types.Message, state: FSMContext):
    code = message.text.strip()
    if code not in students_db:
        await message.answer("❌ Bunday kodli o'quvchi topilmadi. Qayta kiriting:")
        return
    
    students_db[code]["paid"] = True
    await message.answer(f"✅ {students_db[code]['name']} uchun to'lov qabul qilindi deb belgilandi!", reply_markup=teacher_keyboard)
    await state.clear()

# --- YO'QLAMA VA NATIJA YUBORISH ---
@dp.message(F.text == "📊 Yo'qlama / Natija yuborish")
async def start_report_btn(message: types.Message, state: FSMContext):
    if message.from_user.id != TEACHER_ID:
        return
    await message.answer("O'quvchining KODINI kiriting:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(TeacherActions.waiting_for_attendance_code)

@dp.message(TeacherActions.waiting_for_attendance_code)
async def process_student_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    if code not in students_db:
        await message.answer("❌ Bunday kodli o'quvchi topilmadi. Qayta kiriting:")
        return
    
    await state.update_data(selected_code=code)
    await message.answer("Test ballini raqamda kiriting (masalan: 85) yoki dars haqida izoh yozing:")
    await state.set_state(TeacherActions.waiting_for_score)

@dp.message(TeacherActions.waiting_for_score)
async def process_score(message: types.Message, state: FSMContext):
    score_text = message.text
    
    if score_text.isdigit():
        code = (await state.get_data())["selected_code"]
        students_db[code]["score"] += int(score_text)
        
    await state.update_data(score=score_text)
    await message.answer("Kamchiliklar yoki qo'shimcha izohlaringizni yozing (masalan: 'Uy vazifasini qilmagan'):")
    await state.set_state(TeacherActions.waiting_for_note)

@dp.message(TeacherActions.waiting_for_note)
async def send_to_parent(message: types.Message, state: FSMContext):
    note_text = message.text
    data = await state.get_data()
    
    code = data["selected_code"]
    score = data["score"]
    student = students_db[code]
    parent_id = student["parent_id"]
    
    if not parent_id:
        await message.answer(f"⚠️ {student['name']} ning ota-onasi hali botga ulanmagan.", reply_markup=teacher_keyboard)
        await state.clear()
        return

    report = (
        f"📩 **Farzandingiz haqida ma'lumot**\n\n"
        f"👤 **O'quvchi:** {student['name']}\n"
        f"📊 **Natija/Davomat:** {score}\n"
        f"📝 **O'qituvchi izohi:** {note_text}\n"
    )
    
    try:
        await bot.send_message(chat_id=parent_id, text=report, parse_mode="Markdown")
        await message.answer("✅ Xabar ota-onaga muvaffaqiyatli yuborildi!", reply_markup=teacher_keyboard)
    except Exception as e:
        await message.answer(f"❌ Xabarni yuborishda xatolik yuz berdi: {e}", reply_markup=teacher_keyboard)
        
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())