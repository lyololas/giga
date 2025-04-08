import logging
import psycopg2
import bcrypt
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)
from telegram.error import Conflict, NetworkError
from datetime import datetime, timedelta
import hashlib
import time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONSENT, ROLE, NAME, EMAIL, PASSWORD, CONFIRM = range(6)
CHAT_MESSAGING = range(1)

DB_CONFIG = {
    'dbname': 'laravel',    
    'user': 'sail',
    'password': 'password',
    'host': 'pgsql',
    'port': '5432',
    'connect_timeout': 5
}
print('dinaxy')
BOT_TOKEN = "7886668986:AAEcwC6QJWykSK7-KWPak5LXVtp11cfd5QM"

class DataProtection:
    @staticmethod
    def pseudonymize(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def approximate_location(lat: float, lon: float) -> tuple:

        return (round(lat, 3), round(lon, 3))

def get_db_connection(max_retries=3):
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            with conn.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
                conn.commit()
            logger.info("Successfully connected to database with PostGIS support")
            return conn
        except psycopg2.OperationalError as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("Max connection retries reached")
                raise
            time.sleep(2)

def hash_password(password: str) -> str:
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10))
        return hashed.decode('utf-8').replace('$2b$', '$2y$')
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data.clear()
        
        privacy_text = (
            "🔒 <b>Согласие на обработку персональных данных</b>\n\n"
            "В соответствии с Федеральным законом №152-ФЗ:\n"
            "1. Оператор: Who-Too-Ton\n"
            "2. Цели обработки: организация волонтерской помощи\n"
            "3. Перечень данных: ФИО, контакты, геолокация\n"
            "4. Срок хранения: 1 год после последнего взаимодействия\n\n"
            "Нажимая «Принимаю», вы даете согласие на обработку данных."
        )
        
        reply_keyboard = [["✅ Принимаю", "❌ Отказываюсь"]]
        await update.message.reply_text(
            privacy_text,
            parse_mode='HTML',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return CONSENT
    except Exception as e:
        logger.error(f"Error in start: {e}")
        return ConversationHandler.END

async def handle_consent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process user consent according to 152-FZ."""
    try:
        choice = update.message.text
        if choice == "❌ Отказываюсь":
            await update.message.reply_text(
                "Для использования бота необходимо дать согласие на обработку данных.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO consent_records 
                    (user_id, consent_given_at, version) 
                    VALUES (%s, NOW(), '1.0')""",
                    (update.effective_user.id,)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log consent: {e}")

        reply_keyboard = [["🙋‍♂️ Я волонтер", "🧑‍💻 Мне нужна помощь"]]
        await update.message.reply_text(
            "Вы волонтер или вам нужна помощь?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return ROLE
    except Exception as e:
        logger.error(f"Error in handle_consent: {e}")
        return ConversationHandler.END

async def handle_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store user role and proceed with registration."""
    try:
        choice = update.message.text
        if "волонтер" in choice:
            context.user_data['role'] = 'volunteer'
            context.user_data['pseudonym'] = f"Volunteer_{update.effective_user.id}"
        else:
            context.user_data['role'] = 'user'
            context.user_data['pseudonym'] = f"User _{update.effective_user.id}"
        
        await update.message.reply_text(
            "Пожалуйста, введите ваше полное имя:",
            reply_markup=ReplyKeyboardRemove()
        )
        return NAME
    except Exception as e:
        logger.error(f"Error in handle_role: {e}")
        return ConversationHandler.END

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the name and ask for email."""
    try:
        context.user_data['name'] = update.message.text.strip()
        if not context.user_data['name']:
            await update.message.reply_text("⚠️ Имя не может быть пустым. Пожалуйста, введите ваше имя:")
            return NAME
            
        await update.message.reply_text(
            "📧 Отлично! Теперь введите ваш адрес электронной почты:",
            reply_markup=ReplyKeyboardRemove()
        )
        return EMAIL
    except Exception as e:
        logger.error(f"Error in name: {e}")
        return ConversationHandler.END

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the email and ask for password."""
    try:
        email = update.message.text.strip().lower()
        if not ("@" in email and "." in email and len(email) > 5):
            await update.message.reply_text("⚠️ Пожалуйста, введите действительный адрес электронной почты:")
            return EMAIL
        
        context.user_data['email'] = email
        await update.message.reply_text(
            "🔒 Теперь создайте пароль (мин. 8 символов):",
            reply_markup=ReplyKeyboardRemove()
        )
        return PASSWORD
    except Exception as e:
        logger.error(f"Error in email: {e}")
        return ConversationHandler.END

async def password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the password and ask for confirmation."""
    try:
        password = update.message.text.strip()
        if len(password) < 8:
            await update.message.reply_text("⚠️ Пароль должен содержать не менее 8 символов. Пожалуйста, попробуйте снова:")
            return PASSWORD
        
        context.user_data[' plain_password'] = password
        context.user_data['password'] = hash_password(password)

        reply_keyboard = [["✅ Да", "❌ Нет"]]
        await update.message.reply_text(
            f"Пожалуйста, подтвердите ваши данные:\n\n"
            f"Роль: {context.user_data.get('role', 'user')}\n"
            f"Имя: {context.user_data['name']}\n"
            f"Электронная почта: {context.user_data['email']}\n\n"
            f"Это правильно?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return CONFIRM
    except Exception as e:
        logger.error(f"Error in password: {e}")
        return ConversationHandler.END

# In the confirm function, modify the database insertion part:
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm registration and save to database."""
    try:
        user_choice = update.message.text
        
        if user_choice == "❌ Нет":
            await update.message.reply_text(
                "🔄 Давайте начнем заново. Пожалуйста, введите ваше полное имя:",
                reply_markup=ReplyKeyboardRemove()
            )
            return NAME
        
        pseudonymized_name = DataProtection.pseudonymize(context.user_data['name'])
        pseudonymized_email = DataProtection.pseudonymize(context.user_data['email'])

        # Ensure we're using the correct Telegram chat ID
        telegram_chat_id = update.effective_chat.id  # Changed from effective_user.id
        
        user_data = {
            'name': pseudonymized_name,
            'email': pseudonymized_email,
            'password': context.user_data['password'],
            'telegram_chat_id': telegram_chat_id,
            'role': context.user_data.get('role', 'user'),
            'original_name': context.user_data['name'],  
            'original_email': context.user_data['email'] 
        }

        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Check for existing user with this chat ID
                cursor.execute(
                    "SELECT id FROM users WHERE telegram_chat_id = %s",
                    (user_data['telegram_chat_id'],)
                )
                if cursor.fetchone():
                    await update.message.reply_text(
                        "⚠️ Пользователь с таким Telegram ID уже существует.",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    return ConversationHandler.END

                # Check for existing email
                cursor.execute(
                    "SELECT id FROM users WHERE email = %s",
                    (user_data['email'],)
                )
                if cursor.fetchone():
                    await update.message.reply_text(
                        "⚠️ Пользователь с таким email уже существует.",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    return ConversationHandler.END

                # Insert new user with BIGINT type for telegram_chat_id
                cursor.execute(
                    """INSERT INTO users 
                    (name, email, password, telegram_chat_id, role, original_name, original_email, created_at)
                    VALUES (%s, %s, %s, %s::BIGINT, %s, 
                    pgp_sym_encrypt(%s::text, 'encryption_key'), 
                    pgp_sym_encrypt(%s::text, 'encryption_key'), 
                    NOW()) RETURNING id""",
                    (user_data['name'], user_data['email'], user_data['password'],
                    str(user_data['telegram_chat_id']), user_data['role'],  # Explicitly convert to string
                    user_data['original_name'], user_data['original_email'])
                )
                user_id = cursor.fetchone()[0]
                conn.commit()

                # Log the registration
                cursor.execute(
                    "INSERT INTO access_logs (user_id, action, timestamp) VALUES (%s, %s, NOW())",
                    (user_id, "registration")
                )
                conn.commit()

                await update.message.reply_text(
                    f"🎉 Регистрация успешна!\n\n"
                    f"Ваш ID пользователя: {user_id}\n"
                    f"Ваш Telegram Chat ID: {telegram_chat_id}",  # Show the chat ID for debugging
                    reply_markup=ReplyKeyboardRemove()
                )

                if user_data['role'] == 'volunteer':
                    await update.message.reply_text(
                        "Как волонтер, вы можете:\n"
                        "1. Установить статус доступности: /available\n"
                        "2. Просмотреть активные запросы: /requests"
                    )
                else:
                    await update.message.reply_text(
                        "Чтобы запросить помощь, используйте команду /help"
                    )

        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            await update.message.reply_text(
                "⚠️ Ошибка при сохранении данных. Пожалуйста, попробуйте позже.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        finally:
            if conn:
                conn.close()
        
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error in confirm: {e}")
        return ConversationHandler.END
        
async def request_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user's help request and notify available volunteers."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Verify user is registered
            cursor.execute(
                "SELECT id, role, original_name FROM users WHERE telegram_chat_id = %s",
                (update.effective_user.id,)
            )
            user = cursor.fetchone()
            
            if not user or user[1] != 'user':
                await update.message.reply_text("Эта команда доступна только зарегистрированным пользователям.")
                return

            user_id, _, user_name = user

            # Check for existing active requests
            cursor.execute(
                "SELECT id FROM help_requests WHERE user_id = %s AND status = 'pending'",
                (user_id,)
            )
            if cursor.fetchone():
                await update.message.reply_text("У вас уже есть активный запрос. Дождитесь ответа волонтера.")
                return

            # Ask for additional info if not provided
            if not context.args:
                await update.message.reply_text(
                    "Пожалуйста, опишите вашу проблему после команды /help\n"
                    "Например: /help Нужна помощь с доставкой продуктов"
                )
                return

            additional_info = ' '.join(context.args)

            # Ask for location if not provided
            if not update.message.location:
                await update.message.reply_text(
                    "Пожалуйста, поделитесь вашим местоположением:",
                    reply_markup=ReplyKeyboardMarkup(
                        [[KeyboardButton("📍 Поделиться местоположением", request_location=True)]],
                        one_time_keyboard=True,
                        resize_keyboard=True
                    )
                )
                # Store additional info temporarily
                context.user_data['help_request_info'] = additional_info
                return

            # Process location
            location = update.message.location
            approx_lat, approx_lon = DataProtection.approximate_location(
                location.latitude, 
                location.longitude
            )

            # Create help request
            cursor.execute("""
                INSERT INTO help_requests 
                (user_id, location, requested_at, status, additional_info)
                VALUES (
                    %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    NOW(),
                    'pending',
                    %s
                )
                RETURNING id
            """, (user_id, approx_lon, approx_lat, additional_info))
            request_id = cursor.fetchone()[0]
            conn.commit()

            # Notify available volunteers with improved message
            cursor.execute("""
                SELECT telegram_chat_id FROM users 
                WHERE role = 'volunteer' AND available = true
            """)
            volunteers = cursor.fetchall()

            if volunteers:
                map_url = f"https://www.google.com/maps?q={approx_lat},{approx_lon}"
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Принять запрос", callback_data=f"accept_{request_id}"),
                        InlineKeyboardButton("❌ Отклонить", callback_data=f"decline_{request_id}")
                    ],
                    [InlineKeyboardButton("📍 Посмотреть на карте", url=map_url)]
                ])

                notification_text = (
                    f"🆘 <b>Новый запрос о помощи!</b>\n\n"
                    f"<b>От:</b> {user_name}\n"
                    f"<b>Описание:</b> {additional_info}\n"
                    f"<b>Когда:</b> {datetime.now().strftime('%H:%M %d.%m.%Y')}\n\n"
                    f"📍 <a href='{map_url}'>Местоположение на карте</a>"
                )

                for volunteer in volunteers:
                    try:
                        await context.bot.send_message(
                            chat_id=volunteer[0],
                            text=notification_text,
                            parse_mode='HTML',
                            reply_markup=keyboard
                        )
                    except Exception as e:
                        logger.error(f"Error notifying volunteer {volunteer[0]}: {e}")

                await update.message.reply_text(
                    "✅ Ваш запрос отправлен волонтерам. Ожидайте ответа..."
                )
            else:
                await update.message.reply_text(
                    "😔 В данный момент нет доступных волонтеров. Попробуйте позже."
                )

    except Exception as e:
        logger.error(f"Error in request_help: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при обработке запроса.")
    finally:
        if conn:
            conn.close()

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process user location for help request."""
    conn = None
    try:
        # Check if this is part of a help request flow
        if 'help_request_info' not in context.user_data:
            return

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, original_name FROM users WHERE telegram_chat_id = %s",
                (update.effective_user.id,)
            )
            user = cursor.fetchone()
            if not user:
                await update.message.reply_text("Please complete registration first")
                return

            user_id, user_name = user
            additional_info = context.user_data['help_request_info']
            
            location = update.message.location
            if not location:
                await update.message.reply_text("Please share your location")
                return
            
            approx_lat, approx_lon = DataProtection.approximate_location(
                location.latitude, 
                location.longitude
            )

            # Create help request
            cursor.execute("""
                INSERT INTO help_requests 
                (user_id, location, requested_at, status, additional_info)
                VALUES (
                    %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    NOW(),
                    'pending',
                    %s
                )
                RETURNING id
            """, (user_id, approx_lon, approx_lat, additional_info))
            request_id = cursor.fetchone()[0]
            conn.commit()

            # Notify volunteers
            cursor.execute("""
                SELECT telegram_chat_id FROM users 
                WHERE role = 'volunteer' AND available = true
            """)
            volunteers = cursor.fetchall()

            if volunteers:
                map_url = f"https://www.google.com/maps?q={approx_lat},{approx_lon}"
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Принять запрос", callback_data=f"accept_{request_id}"),
                        InlineKeyboardButton("❌ Отклонить", callback_data=f"decline_{request_id}")
                    ],
                    [InlineKeyboardButton("📍 Посмотреть на карте", url=map_url)]
                ])
                notification_text = (
                    f"🆘 <b>Новый запрос о помощи!</b>\n\n"
                    f"<b>От:</b> {user_name}\n"
                    f"<b>Описание:</b> {additional_info}\n"
                    f"<b>Когда:</b> {datetime.now().strftime('%H:%M %d.%m.%Y')}\n\n"
                    f"📍 <a href='{map_url}'>Местоположение на карте</a>"
                )

                for volunteer in volunteers:
                    try:
                        await context.bot.send_message(
                            chat_id=volunteer[0],
                            text=notification_text,
                            parse_mode='HTML',
                            reply_markup=keyboard
                        )
                    except Exception as e:
                        logger.error(f"Error notifying volunteer {volunteer[0]}: {e}")

                await update.message.reply_text(
                    "✅ Ваш запрос отправлен волонтерам. Ожидайте ответа..."
                )
            else:
                await update.message.reply_text(
                    "😔 В данный момент нет доступных волонтеров. Попробуйте позже."
                )

    except Exception as e:
        logger.error(f"Error in handle_location: {e}")
        await update.message.reply_text("Error processing your request")
    finally:
        if conn:
            conn.close()
        # Clear temporary data
        if 'help_request_info' in context.user_data:
            context.user_data.pop('help_request_info')
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check volunteer status and active requests."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT available FROM users 
                WHERE telegram_chat_id = %s AND role = 'volunteer'
            """, (update.effective_user.id,))
            
            volunteer = cursor.fetchone()
            if not volunteer:
                await update.message.reply_text("Вы не зарегистрированы как волонтер.")
                return

            available = volunteer[0]
            status = "доступен" if available else "недоступен"
            
            cursor.execute("""
                SELECT COUNT(*) FROM help_requests 
                WHERE status = 'pending'
            """)
            pending_requests = cursor.fetchone()[0]
            
            await update.message.reply_text(
                f"Ваш статус: {status}\n"
                f"Активных запросов: {pending_requests}\n\n"
                "Используйте /available чтобы изменить статус"
            )

    except Exception as e:
        logger.error(f"Error checking status: {e}")
        await update.message.reply_text("⚠️ Ошибка при проверке статуса.")
    finally:
        if conn:
            conn.close()
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process user location and find available volunteers"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE telegram_chat_id = %s",
                (update.effective_user.id,)
            )
            user = cursor.fetchone()
            if not user:
                await update.message.reply_text("Please complete registration first")
                return
            user_id = user[0]

        location = update.message.location
        if not location:
            await update.message.reply_text("Please share your location")
            return
        
        approx_lat, approx_lon = DataProtection.approximate_location(location.latitude, location.longitude)
        
        expires_at = datetime.now() + timedelta(days=365)
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_locations 
                (user_id, geom, expires_at)
                VALUES (
                    %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    %s
                )
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    geom = EXCLUDED.geom,
                    expires_at = EXCLUDED.expires_at,
                    updated_at = NOW()
            """, (user_id, approx_lon, approx_lat, expires_at))
            conn.commit()

            cursor.execute("""
                INSERT INTO help_requests 
                (user_id, location, requested_at, status)
                VALUES (
                    %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    NOW(),
                    'pending'
                )
                RETURNING id
            """, (user_id, approx_lon, approx_lat))
            request_id = cursor.fetchone()[0]
            conn.commit()

            await update.message.reply_text(
                "Ваш запрос о помощи зарегистрирован. Волонтеры будут уведомлены."
            )

    except Exception as e:
        logger.error(f"Error in handle_location: {e}")
        await update.message.reply_text("Error processing your location")
    finally:
        if conn:
            conn.close()
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  
    logger.error(f"Update {update} caused error {context.error}")
    if update:
        await update.message.reply_text("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ Конверсация отменена. Если вы хотите начать заново, используйте команду /start.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END
async def handle_request_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    _, req_id = query.data.split('_')
    req_id = int(req_id)
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.original_name, hr.requested_at,
                       ST_X(hr.location::geometry) as lon,
                       ST_Y(hr.location::geometry) as lat,
                       u.telegram_chat_id
                FROM help_requests hr
                JOIN users u ON hr.user_id = u.id
                WHERE hr.id = %s AND hr.status = 'pending'
            """, (req_id,))
            
            request = cursor.fetchone()
            if not request:
                await query.edit_message_text("Request no longer available")
                return

            name, req_time, lon, lat, user_chat_id = request
            req_time = req_time.strftime("%H:%M")
            map_url = f"https://www.google.com/maps?q={lat},{lon}"

            await query.edit_message_text(
                text=f"Help request from {name} at {req_time}",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Accept", callback_data=f"accept_{req_id}"),
                        InlineKeyboardButton("Decline", callback_data=f"decline_{req_id}")
                    ],
                    [
                        InlineKeyboardButton("View Location", url=map_url)
                    ]
                ])
            )
            
    except Exception as e:
        logger.error(f"Error viewing request: {e}")
        await query.edit_message_text("Error loading request details")
    finally:
        if conn:
            conn.close()
async def handle_request_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle volunteer accepting/declining requests with proper chat initiation"""
    query = update.callback_query
    await query.answer()
    
    conn = None
    try:
        action, req_id = query.data.split('_')
        req_id = int(req_id)
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Get full request details with FOR UPDATE lock
            cursor.execute("""
                SELECT hr.user_id, u.telegram_chat_id, u.original_name,
                       ST_X(hr.location::geometry) as lon,
                       ST_Y(hr.location::geometry) as lat,
                       hr.additional_info
                FROM help_requests hr
                JOIN users u ON hr.user_id = u.id
                WHERE hr.id = %s AND hr.status = 'pending'
                FOR UPDATE
            """, (req_id,))
            
            request = cursor.fetchone()
            if not request:
                await query.edit_message_text("This request has already been processed or doesn't exist.")
                return

            user_id, user_chat_id, user_name, lon, lat, additional_info = request
            volunteer_chat_id = query.from_user.id

            if action == 'accept':
                try:
                    # Update request status
                    cursor.execute("""
                        UPDATE help_requests
                        SET status = 'accepted',
                            volunteer_id = (SELECT id FROM users WHERE telegram_chat_id = %s),
                            accepted_at = NOW()
                        WHERE id = %s
                        RETURNING id
                    """, (volunteer_chat_id, req_id))
                    
                    if not cursor.fetchone():
                        await query.edit_message_text("Error updating request status")
                        return
                    
                    # Create chat session
                    chat_token = hashlib.sha256(f"{user_id}{volunteer_chat_id}{datetime.now()}".encode()).hexdigest()[:8]
                    cursor.execute("""
                        INSERT INTO chats (user_id, volunteer_id, token, created_at)
                        VALUES (%s, (SELECT id FROM users WHERE telegram_chat_id = %s), %s, NOW())
                        RETURNING id
                    """, (user_id, volunteer_chat_id, chat_token))
                    
                    if not cursor.fetchone():
                        conn.rollback()
                        await query.edit_message_text("Error creating chat session")
                        return
                        
                    conn.commit()

                    # Store chat token in context for both parties
                    context.user_data['active_chat'] = chat_token
                    
                    # Get volunteer context to store chat token
                    volunteer_context = context.application.user_data.get(volunteer_chat_id, {})
                    volunteer_context['active_chat'] = chat_token
                    context.application.user_data[volunteer_chat_id] = volunteer_context
                    
                    # Get user context to store chat token
                    user_context = context.application.user_data.get(user_chat_id, {})
                    user_context['active_chat'] = chat_token
                    context.application.user_data[user_chat_id] = user_context

                    # Prepare location info
                    map_url = f"https://maps.google.com/?q={lat},{lon}"

                    # Notify user
                    try:
                        await context.bot.send_message(
                            chat_id=user_chat_id,
                            text=f"🟢 <b>Ваш запрос о помощи принят!</b>\n\n"
                                 f"💬 <b>Чат с волонтером начат. Просто отправляйте сообщения в этот чат.</b>\n"
                                 f"Ваш запрос: {additional_info}",
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        logger.error(f"Error notifying user: {e}")

                    # Notify volunteer
                    try:
                        await query.edit_message_text(
                            text=f"✅ <b>Вы приняли запрос от {user_name}</b>\n\n"
                                 f"💬 <b>Чат с пользователем начат. Просто отправляйте сообщения в этот чат.</b>\n"
                                 f"Запрос: {additional_info}",
                            parse_mode='HTML'
                        )

                        # Send initial message to volunteer
                        await context.bot.send_message(
                            chat_id=volunteer_chat_id,
                            text=f"💬 <b>Чат с {user_name} начат</b>\n"
                                 "Отправьте любое сообщение здесь для общения.\n"
                                 f"Запрос: {additional_info}\n"
                                 "Используйте /endchat для завершения.",
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        logger.error(f"Error notifying volunteer: {e}")

                except Exception as e:
                    conn.rollback()
                    logger.error(f"Database error during acceptance: {e}")
                    await query.edit_message_text("⚠️ Ошибка при обработке запроса. Попробуйте снова.")
                    raise

            elif action == 'decline':
                await query.edit_message_text("Вы отклонили этот запрос.")

    except psycopg2.Error as e:
        logger.error(f"Database error in handle_request_action: {e}")
        await query.edit_message_text("⚠️ Ошибка базы данных. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Error in handle_request_action: {e}")
        await query.edit_message_text("⚠️ Произошла ошибка при обработке запроса.")
    finally:
        if conn:
            conn.close()
async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_token = context.user_data.get('active_chat')
    if not chat_token:
        await update.message.reply_text("Нет активного чата для завершения.")
        return ConversationHandler.END
    
async def call_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiate a call to user"""
    try:
        user_id = context.args[0]
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT original_name, phone FROM users WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()
            
            if user:
                name, phone = user
                await update.message.reply_text(
                    f"📞 Call {name} at: {phone or 'No phone number provided'}\n\n"
                    "After calling, please:\n"
                    "1. Confirm arrival with /arrived_{user_id}\n"
                    "2. Mark complete with /complete_{request_id}"
                )
            else:
                await update.message.reply_text("User not found")
    except Exception as e:
        logger.error(f"Call user error: {e}")
        await update.message.reply_text("Error fetching user info")

async def mark_complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark request as completed"""
    try:
        req_id = context.args[0]
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE help_requests 
                SET status = 'completed', completed_at = NOW() 
                WHERE id = %s
                RETURNING user_id
            """, (req_id,))
            
            if cursor.fetchone():
                conn.commit()
                await update.message.reply_text("✅ Request marked as completed")
            else:
                await update.message.reply_text("Request not found")
    except Exception as e:
        logger.error(f"Complete error: {e}")
        await update.message.reply_text("Error updating request")


    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE chats SET ended_at = NOW() 
                WHERE token = %s AND ended_at IS NULL
                RETURNING user_id, volunteer_id
            """, (chat_token,))
            chat = cursor.fetchone()
            conn.commit()
            
            if chat:
                user_id, volunteer_id = chat
                current_user_id = update.effective_user.id
                other_party_id = volunteer_id if current_user_id == user_id else user_id
                
                cursor.execute("""
                    SELECT telegram_chat_id FROM users WHERE id = %s
                """, (other_party_id,))
                other_chat_id = cursor.fetchone()
                
                if other_chat_id:
                    await context.bot.send_message(
                        chat_id=other_chat_id[0],
                        text="❌ Чат был завершен другой стороной."
                    )
            
            await update.message.reply_text(
                "Чат успешно завершен.",
                reply_markup=ReplyKeyboardRemove()
            )
            
    except Exception as e:
        logger.error(f"Error ending chat: {e}")
        await update.message.reply_text("⚠️ Ошибка при завершении чата.")
    finally:
        if conn:
            conn.close()
    
    context.user_data.pop('active_chat', None)
    return ConversationHandler.END

async def show_help_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available help requests to volunteers"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM users 
                WHERE telegram_chat_id = %s 
                AND role = 'volunteer' 
                AND available = true
            """, (update.effective_user.id,))
            
            if not cursor.fetchone():
                await update.message.reply_text("You need to be an available volunteer to view requests")
                return

            cursor.execute("""
                SELECT hr.id, u.original_name, hr.requested_at,
                       ST_X(hr.location::geometry) as lon,
                       ST_Y(hr.location::geometry) as lat
                FROM help_requests hr
                JOIN users u ON hr.user_id = u.id
                WHERE hr.status = 'pending'
                ORDER BY hr.requested_at
            """)
            requests = cursor.fetchall()

            if not requests:
                await update.message.reply_text("No help requests available")
                return

            for req_id, name, req_time, lon, lat in requests:
                req_time = req_time.strftime("%H:%M")
                map_url = f"https://www.google.com/maps?q={lat},{lon}"
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Accept", callback_data=f"accept_{req_id}"),
                        InlineKeyboardButton("❌ Decline", callback_data=f"decline_{req_id}")
                    ],
                    [InlineKeyboardButton("📍 View Location", url=map_url)]
                ])
                await update.message.reply_text(
                    f"Request from {name} at {req_time}\n"
                    f"Location: {map_url}",
                    reply_markup=keyboard
                )

    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        await update.message.reply_text("Error loading requests")
    except Exception as e:
        logger.error(f"Error showing requests: {e}")
        await update.message.reply_text("Error loading requests")
    finally:
        if conn:
            conn.close()
async def start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start a chat conversation by token or show active chat."""
    try:
        if 'active_chat' in context.user_data:
            await update.message.reply_text(
                "Вы уже в активном чате. Используйте /endchat чтобы завершить текущий чат."
            )
            return CHAT_MESSAGING

        if len(context.args) > 0:
            chat_token = context.args[0]
            return await join_chat(update, context, chat_token)
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT c.token, u.original_name     
                FROM chats c
                JOIN users u ON c.user_id = u.id
                WHERE c.volunteer_id = (
                    SELECT id FROM users WHERE telegram_chat_id = %s
                ) AND c.ended_at IS NULL
            """, (update.effective_user.id,))
            
            active_chats = cursor.fetchall()
            
            if active_chats:
                keyboard = [
                    [InlineKeyboardButton(
                        f"Чат с {chat[1]}", 
                        callback_data=f"joinchat_{chat[0]}"
                    )] 
                    for chat in active_chats
                ]
                
                await update.message.reply_text(
                    "Ваши активные чаты:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
                
        await update.message.reply_text(
            "Используйте команду /chat_[токен] для входа в чат или дождитесь приглашения."
        )
        
    except Exception as e:
        logger.error(f"Error starting chat: {e}")
        await update.message.reply_text("⚠️ Ошибка при запуске чата.")
    finally:
        if conn:
            conn.close()
    return ConversationHandler.END
async def join_chat(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_token: str) -> int:
    """Join an existing chat session."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, volunteer_id FROM chats 
                WHERE token = %s AND ended_at IS NULL
            """, (chat_token,))
            chat = cursor.fetchone()
            
            if not chat:
                await update.message.reply_text("Чат не найден или уже завершен.")
                return ConversationHandler.END

            user_id, volunteer_id = chat
            current_user_id = update.effective_user.id

            cursor.execute("""
                SELECT telegram_chat_id FROM users 
                WHERE id IN (%s, %s) AND telegram_chat_id = %s
            """, (user_id, volunteer_id, current_user_id))
            
            if not cursor.fetchone():
                await update.message.reply_text("У вас нет доступа к этому чату.")
                return

            context.user_data['active_chat'] = chat_token
            await update.message.reply_text(
                "💬 Вы в чате поддержки. Все ваши сообщения будут пересылаться вашему партнеру.\n\n"
                "Используйте /endchat чтобы завершить общение."
            )
            return CHAT_MESSAGING

    except Exception as e:
        logger.error(f"Error joining chat: {e}")
        await update.message.reply_text("⚠️ Ошибка при подключении к чату.")
    finally:
        if conn:
            conn.close()
    return ConversationHandler.END


async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle incoming chat messages between user and volunteer."""
    conn = None
    try:
        chat_token = context.user_data.get('active_chat')
        if not chat_token:
            await update.message.reply_text("Нет активного чата. Используйте /chat для начала.")
            return ConversationHandler.END

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Get chat participants
            cursor.execute("""
                SELECT 
                    u.telegram_chat_id as user_chat_id,
                    v.telegram_chat_id as volunteer_chat_id,
                    u.original_name as user_name,
                    v.original_name as volunteer_name
                FROM chats c
                JOIN users u ON c.user_id = u.id
                JOIN users v ON c.volunteer_id = v.id
                WHERE c.token = %s AND c.ended_at IS NULL
            """, (chat_token,))
            
            chat = cursor.fetchone()
            if not chat:
                await update.message.reply_text("Чат завершен или не существует.")
                context.user_data.pop('active_chat', None)
                return ConversationHandler.END

            user_chat_id, volunteer_chat_id, user_name, volunteer_name = chat
            current_user_id = update.effective_user.id

            # Determine recipient and sender info
            if current_user_id == user_chat_id:
                recipient_id = volunteer_chat_id
                sender_name = user_name
                sender_role = "Пользователь"
            else:
                recipient_id = user_chat_id
                sender_name = volunteer_name
                sender_role = "Волонтер"

            # Forward message with sender info
            try:
                await context.bot.send_message(
                    chat_id=recipient_id,
                    text=f"{sender_role} {sender_name}:\n{update.message.text}"
                )
            except Exception as e:
                logger.error(f"Error forwarding message: {e}")
                await update.message.reply_text("Не удалось отправить сообщение. Возможно, пользователь заблокировал бота.")
                return CHAT_MESSAGING

            # Log message in database
            cursor.execute("""
                INSERT INTO chat_messages (
                    chat_token, 
                    sender_id,
                    message,
                    sent_at
                ) VALUES (
                    %s,
                    (SELECT id FROM users WHERE telegram_chat_id = %s),
                    %s,
                    NOW()
                )
            """, (chat_token, current_user_id, update.message.text))
            conn.commit()

    except Exception as e:
        logger.error(f"Error handling chat message: {e}")
        await update.message.reply_text("⚠️ Ошибка при отправке сообщения.")
    finally:
        if conn:
            conn.close()
    return CHAT_MESSAGING
    
async def handle_volunteer_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process volunteer's response to help request with improved error handling."""
    query = update.callback_query
    await query.answer()
    
    conn = None
    try:
        action, req_id = query.data.split('_')
        req_id = int(req_id)
        
        if action not in ['accept', 'decline']:
            await query.edit_message_text("⚠️ Неизвестное действие.")
            return

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Get request details with user chat ID
            cursor.execute("""
                SELECT hr.id, u.telegram_chat_id, hr.status
                FROM help_requests hr
                JOIN users u ON hr.user_id = u.id
                WHERE hr.id = %s
                FOR UPDATE
            """, (req_id,))
            
            request = cursor.fetchone()
            if not request:
                await query.edit_message_text("Запрос не найден или уже обработан.")
                return

            _, user_chat_id, current_status = request
            
            if current_status != 'pending':
                await query.edit_message_text("Этот запрос уже был обработан.")
                return

            if action == 'accept':
                try:
                    # Update request status
                    cursor.execute("""
                        UPDATE help_requests
                        SET status = 'accepted',
                            volunteer_id = (SELECT id FROM users WHERE telegram_chat_id = %s),
                            accepted_at = NOW()
                        WHERE id = %s
                        RETURNING id
                    """, (query.from_user.id, req_id))
                    
                    if not cursor.fetchone():
                        await query.edit_message_text("Ошибка при обновлении статуса запроса")
                        return
                    
                    conn.commit()
                    try:
                        await context.bot.send_message(
                            chat_id=user_chat_id,
                            text="🟢 Волонтер принял ваш запрос о помощи и уже в пути!"
                        )
                        await query.edit_message_text(" ")
                    except Exception as e:
                        logger.error(f"Error notifying user {user_chat_id}: {e}")
                        await query.edit_message_text(
                            "✅ Вы приняли запрос, но не удалось уведомить пользователя. "
                            "Попробуйте связаться с ним другим способом."
                        )

                except Exception as e:
                    conn.rollback()
                    logger.error(f"Database error during acceptance: {e}")
                    await query.edit_message_text("⚠️ Ошибка при обработке запроса. Попробуйте снова.")
                    raise

            elif action == 'decline':
                try:
                   
                    cursor.execute("""
                        UPDATE help_requests
                        SET status = 'declined',
                            declined_at = NOW()
                        WHERE id = %s
                    """, (req_id,))
                    conn.commit()
                    await query.edit_message_text("Вы отклонили этот запрос.")
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error declining request: {e}")
                    await query.edit_message_text("⚠️ Ошибка при отклонении запроса.")

    except ValueError:
        await query.edit_message_text("⚠️ Неверный формат запроса.")
    except psycopg2.Error as e:
        logger.error(f"Database error in handle_volunteer_response: {e}")
        await query.edit_message_text("⚠️ Ошибка базы данных. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Error in handle_volunteer_response: {e}")
        await query.edit_message_text("⚠️ Произошла ошибка при обработке запроса.")
    finally:
        if conn:
            conn.close()

async def toggle_availability(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allow volunteers to toggle their availability status."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, available FROM users 
                WHERE telegram_chat_id = %s AND role = 'volunteer'
            """, (update.effective_user.id,))
            
            user = cursor.fetchone()
            if not user:
                await update.message.reply_text("Эта команда доступна только волонтерам.")
                return

            user_id, current_status = user
            new_status = not current_status

            cursor.execute("""
                UPDATE users SET available = %s 
                WHERE id = %s
            """, (new_status, user_id))
            conn.commit()

            status_text = "доступен" if new_status else "недоступен"
            await update.message.reply_text(
                f"Ваш статус изменен: теперь вы {status_text} для помощи."
            )

    except Exception as e:
        logger.error(f"Error toggling availability: {e}")
        await update.message.reply_text("⚠️ Не удалось изменить статус.")
    finally:
        if conn:
            conn.close()
def main() -> None:
    """Run the bot with all handlers."""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Registration conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONSENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_consent)],
            ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_role)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password)],
            CONFIRM: [MessageHandler(filters.Regex("^(✅ Да|❌ Нет)$"), confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Chat conversation handler (only add this once!)
    chat_handler = ConversationHandler(
    entry_points=[CommandHandler("chat", start_chat)],
    states={
        CHAT_MESSAGING: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat_message),
            MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_chat_message)
        ]
    },
    fallbacks=[CommandHandler("endchat", end_chat)],
)
    
    application.add_handler(conv_handler)
    application.add_handler(chat_handler)  
    application.add_handler(CommandHandler("status", check_status))
    application.add_handler(CommandHandler("help", request_help))
    application.add_handler(CommandHandler("available", toggle_availability))
    application.add_handler(CommandHandler("call_user", call_user))
    application.add_handler(CommandHandler("complete", mark_complete))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(CallbackQueryHandler(handle_volunteer_response))
    application.add_handler(CallbackQueryHandler(handle_request_action, pattern="^(accept|decline)_"))
    application.add_handler(CommandHandler("requests", show_help_requests))
    application.add_error_handler(error_handler)

    try:
        application.run_polling(
            poll_interval=1.0,
            timeout=10,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    except Conflict:
        logger.error("Another instance is already running. Exiting...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")   
    finally:
        logger.info("Bot stopped")

if __name__ == "__main__":
    main()