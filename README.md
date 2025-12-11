# README.md

```markdown
# 🛒 ShopMax - Маркетплейс

Полнофункциональный интернет-магазин на FastAPI с современным UI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📸 Скриншоты

```
┌─────────────────────────────────────────────────────────────┐
│  🛒 ShopMax          [Поиск...]           ❤️ 🛒 👤          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   🎁 Летняя распродажа!                                     │
│   Скидки до 50% на электронику                              │
│                                                             │
│   📦 Категории                                              │
│   ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐          │
│   │ 📱  │ │ 👕  │ │ 🏠  │ │ ⚽  │ │ 📚  │ │ 💄  │          │
│   └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘          │
│                                                             │
│   🔥 Хиты продаж                                            │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│   │   📱    │ │   💻    │ │   🎧    │ │   ⌚    │          │
│   │ iPhone  │ │ MacBook │ │ AirPods │ │ Watch   │          │
│   │ 129 990₽│ │ 149 990₽│ │ 24 990₽ │ │ 89 990₽ │          │
│   │[В корз.]│ │[В корз.]│ │[В корз.]│ │[В корз.]│          │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Возможности

### 👤 Для покупателей
- 🔍 Поиск и фильтрация товаров
- 📦 Каталог с категориями
- 🛒 Корзина с изменением количества
- ❤️ Избранное
- 📝 Оформление заказов
- 📋 История заказов
- 👤 Личный кабинет

### 👑 Для администратора
- 📊 Дашборд со статистикой
- 📦 Управление заказами
- 🏷️ Управление товарами
- 👥 Просмотр пользователей

### 🛠 Технические
- ⚡ Асинхронный FastAPI
- 🗄️ SQLite база данных
- 🎨 Современный адаптивный UI
- 🔐 Сессионная авторизация
- 📱 Мобильная версия

## 🚀 Быстрый старт

### Требования
- Python 3.8+
- pip

### Установка

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/your-username/shopmax.git
cd shopmax

# 2. Создайте виртуальное окружение (рекомендуется)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Запустите приложение
python main.py
```

### Открыть в браузере

```
http://localhost:8000
```

## 🔑 Тестовые аккаунты

| Роль | Email | Пароль |
|------|-------|--------|
| 👤 Пользователь | `user@test.com` | `123456` |
| 👑 Администратор | `admin@shop.com` | `admin123` |

## 📁 Структура проекта

```
shopmax/
├── main.py           # Основное приложение FastAPI
├── database.py       # Работа с базой данных
├── requirements.txt  # Зависимости Python
├── shop.db          # SQLite база данных (создаётся автоматически)
└── README.md        # Документация
```

## 📦 Зависимости

```txt
fastapi==0.109.0
uvicorn==0.27.0
aiosqlite==0.19.0
python-multipart==0.0.6
```

## 🗺️ Маршруты

### Публичные страницы
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | Главная страница |
| GET | `/catalog` | Каталог товаров |
| GET | `/catalog?category=1` | Фильтр по категории |
| GET | `/catalog?q=iphone` | Поиск товаров |
| GET | `/product/{id}` | Страница товара |
| GET | `/login` | Вход |
| GET | `/register` | Регистрация |

### Личный кабинет (требуется авторизация)
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/cart` | Корзина |
| GET | `/favorites` | Избранное |
| GET | `/checkout` | Оформление заказа |
| GET | `/orders` | Мои заказы |
| GET | `/profile` | Профиль |
| GET | `/logout` | Выход |

### Админ-панель (только для админов)
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/admin` | Дашборд |
| GET | `/admin/orders` | Управление заказами |
| GET | `/admin/products` | Управление товарами |
| GET | `/admin/users` | Пользователи |

### API
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/cart/add` | Добавить в корзину |
| POST | `/api/cart/update` | Обновить количество |
| POST | `/api/cart/remove` | Удалить из корзины |
| POST | `/api/favorites/toggle` | Добавить/удалить из избранного |
| POST | `/api/admin/orders/{id}/status` | Изменить статус заказа |

## 🗄️ База данных

### Схема таблиц

```sql
-- Пользователи
users (id, email, password, name, phone, address, is_admin, created_at)

-- Категории
categories (id, name, slug, icon, parent_id)

-- Товары
products (id, name, slug, description, price, old_price, category_id, 
          image, stock, rating, reviews_count, is_featured, is_active, created_at)

-- Корзина
cart_items (id, user_id, product_id, quantity, created_at)

-- Избранное
favorites (id, user_id, product_id, created_at)

-- Заказы
orders (id, user_id, status, total, name, email, phone, address, comment, created_at)

-- Товары в заказе
order_items (id, order_id, product_id, quantity, price)

-- Отзывы
reviews (id, user_id, product_id, rating, text, created_at)
```

### Статусы заказов

| Статус | Описание |
|--------|----------|
| `pending` | ⏳ Ожидает оплаты |
| `processing` | 🔄 В обработке |
| `shipped` | 🚚 Отправлен |
| `delivered` | ✅ Доставлен |
| `cancelled` | ❌ Отменён |

## ⚙️ Конфигурация

### Изменить порт

```python
# main.py (в конце файла)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)
```

### Изменить путь к БД

```python
# database.py
DATABASE_PATH = "data/shop.db"  # или другой путь
```

### Изменить секретный ключ сессий

```python
# main.py
app.add_middleware(SessionMiddleware, secret_key="ваш-секретный-ключ")
```

## 🔧 Разработка

### Запуск в режиме разработки

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Сброс базы данных

```bash
# Удалите файл shop.db и перезапустите приложение
rm shop.db
python main.py
```

### Добавление нового товара (через код)

```python
from database import create_product

await create_product({
    "name": "Новый товар",
    "slug": "new-product",
    "description": "Описание товара",
    "price": 9990,
    "old_price": 12990,  # опционально
    "category_id": 1,
    "image": "🎁",
    "stock": 100,
    "is_featured": 1
})
```

## 🐛 Решение проблем

### Страница недоступна
```bash
# Используйте localhost вместо 0.0.0.0
http://localhost:8000
# или
http://127.0.0.1:8000
```

### Ошибка "Address already in use"
```bash
# Порт занят, используйте другой
python -m uvicorn main:app --reload --port 8080
```

### Ошибка с базой данных
```bash
# Удалите старую БД
rm shop.db
# Перезапустите приложение
python main.py
```

### DeprecationWarning при запуске
Это предупреждение можно игнорировать — код работает. Или обновите код согласно документации FastAPI.

## 📝 TODO / Идеи для развития

- [ ] Загрузка изображений товаров
- [ ] Система промокодов
- [ ] Отзывы и рейтинги
- [ ] Email уведомления
- [ ] Интеграция с платёжными системами
- [ ] REST API для мобильного приложения
- [ ] Система рекомендаций
- [ ] Чат поддержки
- [ ] Сравнение товаров
- [ ] Wishlist / списки желаний

## 📄 Лицензия

MIT License — используйте свободно для любых целей.

## 👨‍💻 Автор

Создано с ❤️ и ☕

---

⭐ Если проект полезен — поставьте звёздочку!
```

---

Этот README содержит:
- ✅ Описание проекта
- ✅ Инструкции по установке
- ✅ Тестовые аккаунты
- ✅ Структуру проекта
- ✅ Документацию API
- ✅ Схему БД
- ✅ Решение проблем
- ✅ Идеи для развития
