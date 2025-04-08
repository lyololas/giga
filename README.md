# 🌟 *СВОИ* | who-too-ton 🌐  


---

## 👥 Команда  
| Роль           | Имя               | Контакты                          |
|----------------|-------------------|-----------------------------------|
| 🎯 Менеджер    | Копырина Милена   | [Telegram](https://t.me/...)      |
| 🎨 Дизайнер    | Мордовской Аман   | [Telegram](https://t.me/...)      |
| 💻 Разработчик | Петров Леонид     | [Telegram](https://t.me/...)      |

---

## 📌 О проекте  
**СВОИ** — платформа для психологической поддержки военных, разработанная в рамках всероссийского этапа МПИТ.  

---

## 🚀 Функционал  
✅ **Создание и редактирование тем**  
✅ **Создание и редактирование истории**
✅ **Админ-панель** (управление пользователями/темами)  
✅ **Основная функция тг бота** 
🔜 **Дополнительные функции** (в разработке)  
🔜 **Дополнительные функции тг бота** (в разработке)  

---

## 🛠️ Технологии

### **Backend**  
<div align="left">  
  <img src="https://skillicons.dev/icons?i=laravel" alt="Laravel">  
  <img src="https://skillicons.dev/icons?i=php" alt="PHP" title="PHP 8.3">  
  <img src="https://skillicons.dev/icons?i=mysql" alt="MySQL" title="MySQL">  
</div>  

### **Frontend**  
<div align="left">  
  <img src="https://skillicons.dev/icons?i=vue" alt="Vue.js" title="Vue 3">  
  <img src="https://skillicons.dev/icons?i=tailwind" alt="Tailwind CSS" title="Tailwind CSS">  
  <img src="https://skillicons.dev/icons?i=vite" alt="Vite" title="Vite">  
  <img src="https://skillicons.dev/icons?i=inertia" alt="Inertia.js" title="Inertia.js">  
</div>  

### **Tools**  
<div align="left">  
  <img src="https://skillicons.dev/icons?i=git" alt="Git" title="Git">  
  <img src="https://skillicons.dev/icons?i=github" alt="GitHub" title="GitHub">  
  <img src="https://skillicons.dev/icons?i=postman" alt="Postman" title="Postman">  
</div>  

---

## ⚡ Быстрый старт (Docker)

### 1️⃣ Установка Docker
- Убедитесь, что у вас установлены:
  - [Docker](https://docs.docker.com/get-docker/)
  - [Docker Compose](https://docs.docker.com/compose/install/)

### 2️⃣ Запуск проекта
```bash
# Клонируйте репозиторий
git clone https://github.com/your-repo.git
cd your-repo

# Скопируйте и настройте .env
cp .env.example .env
# Отредактируйте .env при необходимости (см. раздел конфигурации ниже)

# Запустите сервисы
docker-compose up -d

# Установите зависимости
docker-compose exec app composer install
docker-compose exec app npm install

# Генерация ключа и миграции
docker-compose exec app php artisan key:generate
docker-compose exec app php artisan migrate --seed

# Сборка фронтенда (для production)
docker-compose exec app npm run build

# Или для разработки (в другом терминале)
docker-compose exec app npm run dev
