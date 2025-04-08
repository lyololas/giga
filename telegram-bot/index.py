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

        user_data = {
            'name': pseudonymized_name,
            'email': pseudonymized_email,
            'password': context.user_data['password'],
            'telegram_chat_id': update.effective_user.id,
            'role': context.user_data.get('role', 'user'),
            'original_name': context.user_data['name'],  
            'original_email': context.user_data['email'] 
        }

        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM users WHERE email = %s OR telegram_chat_id = %s",
                    (user_data['email'], user_data['telegram_chat_id'])
                )
                if cursor.fetchone():
                    await update.message.reply_text(
                        "⚠️ Пользователь с таким email или Telegram ID уже существует.",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    return ConversationHandler.END

                cursor.execute(
                    """INSERT INTO users 
                    (name, email, password, telegram_chat_id, role, original_name, original_email, created_at)
                    VALUES (%s, %s, %s, %s, %s, 
                    pgp_sym_encrypt(%s::text, 'encryption_key'), 
                    pgp_sym_encrypt(%s::text, 'encryption_key'), 
                    NOW()) RETURNING id""",
                    (user_data['name'], user_data['email'], user_data['password'],
                    user_data['telegram_chat_id'], user_data['role'],
                    user_data['original_name'], user_data['original_email'])
                )
                user_id = cursor.fetchone()[0]
                conn.commit()


                cursor.execute(
                "INSERT INTO access_logs (user_id, action, timestamp) VALUES (%s, %s, NOW())",
                (user_id, "registration")
                )
                conn.commit()

                await update.message.reply_text(
                    f"🎉 Регистрация успешна!\n\n"
                    f"Ваш ID пользователя: {user_id}",
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
            await update.message.reply_text("⚠️ Ошибка при сохранении данных. Пожалуйста, попробуйте позже.",
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
    """Handle user's request for help with 152-FZ compliant location sharing."""
    conn = None 
    try:
       
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT role FROM users WHERE telegram_chat_id = %s",
                (update.effective_user.id,)
            )
            result = cursor.fetchone()
            if not result or result[0] != 'user':
                await update.message.reply_text("Эта команда доступна только зарегистрированным пользователям.")
                return

        await update.message.reply_text(
            "Пожалуйста, поделитесь вашим местоположением для поиска ближайшего волонтера:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📍 Поделиться местоположением", request_location=True)]],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
    except Exception as e:
        logger.error(f"Error in request_help: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.")
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
    """Handle volunteer accepting/declining requests"""
    query = update.callback_query
    await query.answer()
    
    conn = None
    try:
        action, req_id = query.data.split('_')
        req_id = int(req_id)
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT hr.user_id, u.telegram_chat_id as user_chat_id,
                       v.telegram_chat_id as volunteer_chat_id
                FROM help_requests hr
                JOIN users u ON hr.user_id = u.id
                JOIN users v ON v.telegram_chat_id = %s
                WHERE hr.id = %s AND hr.status = 'pending'
            """, (query.from_user.id, req_id))
            
            request = cursor.fetchone()
            if not request:
                await query.edit_message_text("Этот запрос уже был обработан.")
                return

            user_id, user_chat_id, volunteer_id = request

            if action == 'accept':
                cursor.execute("""
                    UPDATE help_requests
                    SET status = 'accepted',
                        volunteer_id = %s,
                        accepted_at = NOW()
                    WHERE id = %s
                    RETURNING id
                """, (volunteer_id, req_id))
                conn.commit()

                chat_token = hashlib.sha256(f"{user_id}{volunteer_id}{datetime.now()}".encode()).hexdigest()[:8]
                cursor.execute("""
                    INSERT INTO chats (user_id, volunteer_id, token, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, (user_id, volunteer_id, chat_token))
                conn.commit()

      
                await context.bot.send_message(
                    chat_id=user_chat_id,
                    text=f"🎉 Ваш запрос принят! Волонтер скоро свяжется с вами.\n\n"
                         f"Для общения используйте команду /chat_{chat_token}"
                )

                await query.edit_message_text(
                    text=f"✅ Вы приняли запрос. Для общения используйте /chat_{chat_token}",
                    reply_markup=None
                )

            elif action == 'decline':
                await query.edit_message_text("Вы отклонили этот запрос.")

    except Exception as e:
        logger.error(f"Error handling request action: {e}")
        await query.edit_message_text("⚠️ Произошла ошибка при обработке запроса.")
    finally:
        if conn:
            conn.close()

async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_token = context.user_data.get('active_chat')
    if not chat_token:
        await update.message.reply_text("Нет активного чата для завершения.")
        return ConversationHandler.END
    
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

            keyboard = []
            for req_id, name, req_time, lon, lat in requests:
                req_time = req_time.strftime("%H:%M")
                map_url = f"https://www.google.com/maps?q={lat},{lon}"
                keyboard.append([
                    InlineKeyboardButton(
                        f"Request from {name} at {req_time}",
                        callback_data=f"view_{req_id}"
                    ),
                    InlineKeyboardButton(
                        "📍 View Location",
                        url=map_url
                    )
                ])

            await update.message.reply_text(
                "Available help requests:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
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
    """Handle incoming chat messages."""
    conn = None
    try:
        chat_token = context.user_data.get('active_chat')
        if not chat_token:
            await update.message.reply_text("Активный чат не найден. Используйте /chat чтобы начать.")
            return ConversationHandler.END

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Get chat participants
            cursor.execute("""
                SELECT u.id, u.telegram_chat_id, u.role 
                FROM chats c
                JOIN users u ON u.id IN (c.user_id, c.volunteer_id)
                WHERE c.token = %s AND c.ended_at IS NULL
            """, (chat_token,))
            participants = cursor.fetchall()
            
            if len(participants) != 2:
                await update.message.reply_text("Чат завершен или не существует.")
                context.user_data.pop('active_chat', None)
                return ConversationHandler.END

            # Find the other participant
            current_user_id = update.effective_user.id
            for participant in participants:
                if participant[1] != current_user_id:
                    recipient_id = participant[1]
                    recipient_role = participant[2]
                    break
            else:
                await update.message.reply_text("Не удалось найти участника чата.")
                return CHAT_MESSAGING

            # Forward the message
            sender_role = "volunteer" if recipient_role == "user" else "user"
            await context.bot.send_message(
                chat_id=recipient_id,
                text=f"{'Волонтер' if sender_role == 'volunteer' else 'Пользователь'}: {update.message.text}"
            )
            
            # Log the message in database
            cursor.execute("""
                INSERT INTO chat_messages 
                (chat_token, sender_id, message, sent_at)
                VALUES (
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
    """Process volunteer's response to help request."""
    query = update.callback_query
    await query.answer()
    
    conn = None
    try:
        action, user_id = query.data.split('_')
        if action == 'accept':
            await context.bot.send_message(
                chat_id=user_id,
                text="Волонтер принял ваш запрос и уже в пути!"
            )
            
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE help_requests
                    SET accepted_at = NOW(), status = 'accepted'
                    WHERE user_id = %s AND status = 'pending'
                    RETURNING id
                """, (user_id,))
                
                if cursor.fetchone():
                    conn.commit()
                    await query.edit_message_text("Вы успешно приняли запрос о помощи!")
                else:
                    await query.edit_message_text("Этот запрос уже был обработан.")
    except Exception as e:
        logger.error(f"Error handling volunteer response: {e}")
        await query.edit_message_text("⚠️ Произошла ошибка при обработке вашего ответа.")
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
    application.add_handler(CommandHandler("help", request_help))
    application.add_handler(CommandHandler("available", toggle_availability))
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