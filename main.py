import sqlite3
import random
import string
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

DB_PATH = "dong_bot.db"

def create_connection():
    return sqlite3.connect(DB_PATH)

def generate_code():
    return "DNG_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

# ---------- Database Helpers ----------
def save_user(user):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
              (user.id, user.username, user.first_name))
    conn.commit()
    conn.close()

def create_dong(code, title, owner_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO dongs (code, title, owner_id) VALUES (?, ?, ?)", (code, title, owner_id))
    c.execute("INSERT INTO dong_members (code, user_id, status) VALUES (?, ?, 'accepted')", (code, owner_id))
    conn.commit()
    conn.close()

def request_join(code, user_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO dong_members (code, user_id, status) VALUES (?, ?, 'pending')", (code, user_id))
    conn.commit()
    conn.close()

def get_dong_owner(code):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT owner_id FROM dongs WHERE code = ?", (code,))
    owner = c.fetchone()
    conn.close()
    return owner[0] if owner else None

def accept_user(code, user_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("UPDATE dong_members SET status = 'accepted' WHERE code = ? AND user_id = ?", (code, user_id))
    conn.commit()
    conn.close()

def get_dong_info(code):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT title FROM dongs WHERE code = ?", (code,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else "نامشخص"

def get_user_display_name(user_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT username, first_name FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0] or row[1] or f"کاربر{user_id}"
    return f"کاربر{user_id}"

def format_dong_header(code):
    title = get_dong_info(code)
    return f"🏠 {title} ({code})\n" + "─" * 30 + "\n"

def is_user_in_dong(code, user_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT status FROM dong_members WHERE code = ? AND user_id = ?", (code, user_id))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# ---------- Bot Commands ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user)
    user = update.effective_user
    welcome_text = f"""
🎉 سلام {user.first_name} عزیز!

به ربات dong خوش آمدید! 🤖

این ربات برای مدیریت هزینه‌های گروهی طراحی شده است.

📋 دستورات اصلی:
• /new_dong - ساخت گروه جدید
• /join_dong - پیوستن به گروه
• /add_expense - افزودن هزینه
• /show_status - مشاهده وضعیت
• /members - مشاهده اعضا
• /help - راهنما

برای شروع، یک گروه جدید بسازید یا به گروه موجودی بپیوندید!
"""
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 راهنمای ربات dong

🟢 دستورات اصلی:
• /start - شروع و دریافت راهنما
• /help - نمایش همین راهنما
• /new_dong - ساخت گروه جدید
• /join_dong - پیوستن به گروه
• /add_expense - افزودن هزینه
• /show_status - مشاهده وضعیت مالی
• /members - مشاهده اعضای گروه
• /cancel - لغو عملیات جاری

💡 نکات مهم:
• ابتدا باید عضو یک گروه باشید
• برای افزودن هزینه، عنوان و مبلغ را وارد کنید
• اعضای شرکت‌کننده را انتخاب کنید
• هزینه‌کننده را مشخص کنید

🔧 پشتیبانی: در صورت مشکل با سازنده تماس بگیرید
    @KMmatin_00
"""
    await update.message.reply_text(help_text)

async def new_dong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    
    await update.message.reply_text("📝 نام گروه جدید را وارد کنید:")
    context.user_data['new_dong_step'] = 'awaiting_title'

async def handle_new_dong_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('new_dong_step') == 'awaiting_title':
        title = update.message.text.strip()
        if len(title) < 2:
            await update.message.reply_text("❌ نام گروه باید حداقل 2 کاراکتر باشد.")
            return
            
        code = generate_code()
        create_dong(code, title, update.effective_user.id)
        
        # ذخیره dong فعال
        context.user_data['active_dong'] = code
        
        header = format_dong_header(code)
        success_text = f"{header}✅ گروه با موفقیت ساخته شد!\n\n📋 دستورات بعدی:\n• /add_expense - افزودن هزینه\n• /members - مشاهده اعضا\n• /show_status - وضعیت مالی\n• /help - راهنما"
        
        await update.message.reply_text(success_text)
        context.user_data['new_dong_step'] = None

async def join_dong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 کد گروه را وارد کنید:")
    context.user_data['join_step'] = 'awaiting_code'

async def handle_join_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('join_step') == 'awaiting_code':
        code = update.message.text.strip().upper()
        user = update.effective_user
        
        # بررسی وجود گروه
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT title FROM dongs WHERE code = ?", (code,))
        dong = c.fetchone()
        conn.close()
        
        if not dong:
            await update.message.reply_text("❌ گروهی با این کد یافت نشد!")
            context.user_data['join_step'] = None
            return
        
        # بررسی عضویت قبلی
        current_status = is_user_in_dong(code, user.id)
        if current_status == 'accepted':
            await update.message.reply_text("✅ شما قبلاً عضو این گروه هستید!")
            context.user_data['active_dong'] = code
            context.user_data['join_step'] = None
            return
        elif current_status == 'pending':
            await update.message.reply_text("⏳ درخواست عضویت شما در انتظار تایید است!")
            context.user_data['join_step'] = None
            return
        
        # ارسال درخواست عضویت
        request_join(code, user.id)
        owner_id = get_dong_owner(code)
        
        # اطلاع‌رسانی به صاحب گروه
        keyboard = [
            [InlineKeyboardButton("✅ تایید", callback_data=f"accept:{code}:{user.id}")],
            [InlineKeyboardButton("❌ رد", callback_data=f"reject:{code}:{user.id}")]
        ]
        
        owner_message = f"📥 درخواست عضویت جدید!\n\n👤 کاربر: {user.first_name}\n🏠 گروه: {dong[0]} ({code})"
        
        try:
            await context.bot.send_message(
                owner_id, 
                owner_message, 
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass  # اگر نتوانست پیام بفرستد
        
        await update.message.reply_text("✅ درخواست عضویت ارسال شد! صاحب گروه به زودی آن را بررسی خواهد کرد.")
        context.user_data['join_step'] = None

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_dong = context.user_data.get('active_dong')
    if not active_dong:
        await update.message.reply_text("❌ ابتدا باید عضو یک گروه باشید!\nاز /join_dong استفاده کنید.")
        return
    
    header = format_dong_header(active_dong)
    await update.message.reply_text(f"{header}📝 عنوان هزینه را وارد کنید:")
    context.user_data['expense_step'] = 'awaiting_title'

async def handle_expense_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    active_dong = context.user_data.get('active_dong')
    header = format_dong_header(active_dong)

    step = context.user_data.get('expense_step')

    if step == 'awaiting_title':
        if len(text) < 2:
            await update.message.reply_text(f"{header}❌ عنوان باید حداقل 2 کاراکتر باشد!")
            return
            
        context.user_data['exp_title'] = text
        context.user_data['expense_step'] = 'awaiting_amount'
        await update.message.reply_text(f"{header}💰 مبلغ هزینه را وارد کنید (تومان):")
    
    elif step == 'awaiting_amount':
        try:
            amount = float(text.replace(',', ''))
            if amount <= 0:
                await update.message.reply_text(f"{header}❌ مبلغ باید مثبت باشد!")
                return
                
            context.user_data['exp_amount'] = amount
            
            # دریافت اعضا
            conn = create_connection()
            c = conn.cursor()
            c.execute("""
                SELECT u.user_id, u.username, u.first_name 
                FROM dong_members dm 
                JOIN users u ON dm.user_id = u.user_id 
                WHERE dm.code = ? AND dm.status = 'accepted'
                ORDER BY u.first_name
            """, (active_dong,))
            members = c.fetchall()
            conn.close()

            if not members:
                await update.message.reply_text(f"{header}❌ هیچ عضوی در این گروه وجود ندارد!")
                context.user_data['expense_step'] = None
                return

            context.user_data['member_list'] = members
            context.user_data['expense_step'] = 'select_participants'
            context.user_data['selected_participants'] = []

            # نمایش لیست اعضا با شماره
            member_text = f"{header}👥 اعضای گروه:\n\n"
            for i, (uid, username, first_name) in enumerate(members, 1):
                display_name = username or first_name or f"کاربر{uid}"
                member_text += f"{i}. {display_name}\n"
            
            member_text += "\n📝 شماره اعضای شرکت‌کننده را وارد کنید (مثل: 1,2,3):"
            
            await update.message.reply_text(member_text)

        except ValueError:
            await update.message.reply_text(f"{header}❌ مبلغ نامعتبر است! لطفاً عدد وارد کنید.")

async def handle_participant_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    active_dong = context.user_data.get('active_dong')
    header = format_dong_header(active_dong)
    
    try:
        # پردازش شماره‌های وارد شده
        numbers = [int(x.strip()) for x in text.split(',')]
        member_list = context.user_data['member_list']
        selected_participants = []
        
        for num in numbers:
            if 1 <= num <= len(member_list):
                selected_participants.append(member_list[num-1][0])  # user_id
        
        if not selected_participants:
            await update.message.reply_text(f"{header}❌ حداقل یک شماره معتبر وارد کنید!")
            return
        
        context.user_data['selected_participants'] = selected_participants
        
        # نمایش انتخاب‌ها و دکمه تایید
        selected_names = []
        for uid in selected_participants:
            for member_uid, username, first_name in member_list:
                if uid == member_uid:
                    display_name = username or first_name or f"کاربر{uid}"
                    selected_names.append(display_name)
                    break
        
        keyboard = [[InlineKeyboardButton("✅ تایید و ادامه", callback_data="exp_done")]]
        
        selected_text = f"{header}✅ اعضای انتخاب شده:\n" + "\n".join(f"• {name}" for name in selected_names) + "\n\nبرای ادامه کلیک کنید:"
        
        await update.message.reply_text(
            selected_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except ValueError:
        await update.message.reply_text(f"{header}❌ فرمت نامعتبر! لطفاً شماره‌ها را با کاما جدا کنید (مثل: 1,2,3)")

async def handle_expense_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    active_dong = context.user_data.get('active_dong')
    header = format_dong_header(active_dong)

    if data == "exp_done":
        if not context.user_data['selected_participants']:
            await query.edit_message_text(f"{header}❌ حداقل یکنفر را انتخاب کنید!")
            return
        
        # انتخاب هزینه‌کننده
        context.user_data['expense_step'] = 'select_payer'
        
        member_list = context.user_data['member_list']
        buttons = []
        for i, (uid, username, first_name) in enumerate(member_list, 1):
            if uid in context.user_data['selected_participants']:
                display_name = username or first_name or f"کاربر{uid}"
                buttons.append([InlineKeyboardButton(f"{i}. {display_name}", callback_data=f"exp_payer:{uid}")])
        
        await query.edit_message_text(
            f"{header}👤 چه کسی هزینه را پرداخت کرده؟",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data.startswith("exp_payer:"):
        payer_id = int(data.split(":")[1])
        
        # ذخیره هزینه
        conn = create_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO expenses (code, title, amount, payer_id, participants)
            VALUES (?, ?, ?, ?, ?)
        """, (
            active_dong,
            context.user_data['exp_title'],
            context.user_data['exp_amount'],
            payer_id,
            ','.join(str(uid) for uid in context.user_data['selected_participants'])
        ))
        conn.commit()
        conn.close()
        
        payer_name = get_user_display_name(payer_id)
        success_text = f"{header}✅ هزینه ثبت شد!\n\n📝 عنوان: {context.user_data['exp_title']}\n💰 مبلغ: {context.user_data['exp_amount']:,} تومان\n👤 پرداخت‌کننده: {payer_name}"
        
        await query.edit_message_text(success_text)
        context.user_data['expense_step'] = None

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_dong = context.user_data.get('active_dong')
    if not active_dong:
        await update.message.reply_text("❌ ابتدا باید عضو یک گروه باشید!\nاز /join_dong استفاده کنید.")
        return
    
    await show_dong_status(update, context, active_dong)

async def show_dong_status(update: Update, context: ContextTypes.DEFAULT_TYPE, code):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM expenses WHERE code = ?", (code,))
    expenses = c.fetchall()
    balances = defaultdict(float)

    for exp in expenses:
        _, _, _, amount, payer_id, participants = exp
        shared_with = [int(uid) for uid in participants.split(',')]
        split = amount / len(shared_with)
        for uid in shared_with:
            if uid != payer_id:
                balances[uid] -= split
                balances[payer_id] += split

    header = format_dong_header(code)
    
    if not balances:
        await update.message.reply_text(f"{header}💰 وضعیت مالی:\n\n✅ همه چیز تسویه شده است!")
        conn.close()
        return

    # جداسازی بدهکاران و طلبکاران
    debtors = []  # کسانی که بدهی دارند
    creditors = []  # کسانی که طلب دارند
    
    for uid, balance in balances.items():
        if abs(balance) < 0.01:
            continue
        user_name = get_user_display_name(uid)
        if balance > 0:
            creditors.append((uid, user_name, balance))
        else:
            debtors.append((uid, user_name, abs(balance)))

    # مرتب‌سازی بر اساس مبلغ (بیشترین اول)
    debtors.sort(key=lambda x: x[2], reverse=True)
    creditors.sort(key=lambda x: x[2], reverse=True)

    # محاسبه پرداخت‌های بهینه
    payments = []
    debtor_idx = 0
    creditor_idx = 0
    
    while debtor_idx < len(debtors) and creditor_idx < len(creditors):
        debtor_id, debtor_name, debtor_amount = debtors[debtor_idx]
        creditor_id, creditor_name, creditor_amount = creditors[creditor_idx]
        
        payment_amount = min(debtor_amount, creditor_amount)
        
        if payment_amount > 0:
            payments.append({
                'from': debtor_name,
                'to': creditor_name,
                'amount': payment_amount
            })
        
        # کاهش مبالغ
        debtor_amount -= payment_amount
        creditor_amount -= payment_amount
        
        if debtor_amount < 0.01:
            debtor_idx += 1
        else:
            debtors[debtor_idx] = (debtor_id, debtor_name, debtor_amount)
            
        if creditor_amount < 0.01:
            creditor_idx += 1
        else:
            creditors[creditor_idx] = (creditor_id, creditor_name, creditor_amount)

    conn.close()
    
    # نمایش نتیجه
    status_text = f"{header}💰 وضعیت مالی:\n\n"
    
    if payments:
        status_text += "📋 لیست پرداخت‌های لازم:\n\n"
        for i, payment in enumerate(payments, 1):
            status_text += f"{i}. 💸 {payment['from']} → {payment['to']}\n"
            status_text += f"   💰 مبلغ: {payment['amount']:,.0f} تومان\n\n"
        
        # خلاصه وضعیت
        status_text += "📊 خلاصه وضعیت:\n"
        for uid, user_name, balance in debtors:
            if balance > 0.01:
                status_text += f"➖ {user_name}: {balance:,.0f} تومان بدهی\n"
        for uid, user_name, balance in creditors:
            if balance > 0.01:
                status_text += f"➕ {user_name}: {balance:,.0f} تومان طلب\n"
    else:
        status_text += "✅ همه چیز تسویه شده است!"

    await update.message.reply_text(status_text)

async def members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_dong = context.user_data.get('active_dong')
    if not active_dong:
        await update.message.reply_text("❌ ابتدا باید عضو یک گروه باشید!\nاز /join_dong استفاده کنید.")
        return
    
    await show_dong_members(update, context, active_dong)

async def show_dong_members(update: Update, context: ContextTypes.DEFAULT_TYPE, code):
    conn = create_connection()
    c = conn.cursor()
    c.execute("""
        SELECT u.user_id, u.username, u.first_name, dm.status
        FROM dong_members dm 
        JOIN users u ON dm.user_id = u.user_id 
        WHERE dm.code = ? 
        ORDER BY dm.status DESC, u.first_name
    """, (code,))
    members = c.fetchall()
    conn.close()
    
    header = format_dong_header(code)
    
    if not members:
        await update.message.reply_text(f"{header}❌ هیچ عضوی در این گروه وجود ندارد!")
        return
    
    member_text = f"{header}👥 اعضای گروه:\n\n"
    
    for uid, username, first_name, status in members:
        display_name = username or first_name or f"کاربر{uid}"
        status_icon = "✅" if status == 'accepted' else "⏳"
        status_text = "عضو" if status == 'accepted' else "در انتظار"
        member_text += f"{status_icon} {display_name} ({status_text})\n"
    
    await update.message.reply_text(member_text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # پاک کردن همه مراحل
    keys_to_remove = ['new_dong_step', 'join_step', 'expense_step', 'status_step', 'members_step']
    for key in keys_to_remove:
        context.user_data.pop(key, None)
    
    await update.message.reply_text("❌ عملیات لغو شد.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("accept:"):
        _, code, uid = data.split(":")
        uid = int(uid)
        accept_user(code, uid)
        
        # اطلاع به کاربر
        try:
            await context.bot.send_message(uid, f"🎉 درخواست عضویت شما در گروه {code} تایید شد!")
        except:
            pass
        
        await query.edit_message_text("✅ کاربر تایید شد!")
        
    elif data.startswith("reject:"):
        _, code, uid = data.split(":")
        uid = int(uid)
        
        # اطلاع به کاربر
        try:
            await context.bot.send_message(uid, f"❌ درخواست عضویت شما در گروه {code} رد شد.")
        except:
            pass
        
        await query.edit_message_text("❌ درخواست رد شد.")
    
    elif data == "exp_done" or data.startswith("exp_payer:"):
        await handle_expense_callbacks(update, context)

async def step_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # بررسی مراحل مختلف
    if context.user_data.get('new_dong_step'):
        await handle_new_dong_steps(update, context)
    elif context.user_data.get('join_step'):
        await handle_join_steps(update, context)
    elif context.user_data.get('expense_step') == 'select_participants':
        await handle_participant_selection(update, context)
    elif context.user_data.get('expense_step'):
        await handle_expense_steps(update, context)
    else:
        await update.message.reply_text("❌ دستور نامعتبر! از /help برای راهنما استفاده کنید.")

# ---------- Run Bot ----------
TOKEN = "YOUR_BOT_TOKEN_HERE"

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    # ثبت هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("new_dong", new_dong))
    app.add_handler(CommandHandler("join_dong", join_dong))
    app.add_handler(CommandHandler("add_expense", add_expense))
    app.add_handler(CommandHandler("show_status", show_status))
    app.add_handler(CommandHandler("members", members))
    app.add_handler(CommandHandler("cancel", cancel))
    
    # هندلرهای callback و پیام
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, step_router))

    print("🤖 ربات dong در حال اجرا است...")
    app.run_polling() 