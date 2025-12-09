"""
База данных интернет-магазина
"""

import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

DATABASE_PATH = "shop.db"


@asynccontextmanager
async def get_db():
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


async def init_database():
    """Инициализация БД и добавление тестовых данных"""
    async with get_db() as db:
        # Пользователи
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Категории
        await db.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                icon TEXT DEFAULT '📦',
                parent_id INTEGER,
                FOREIGN KEY (parent_id) REFERENCES categories(id)
            )
        """)

        # Товары
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                old_price REAL,
                category_id INTEGER,
                image TEXT,
                stock INTEGER DEFAULT 0,
                rating REAL DEFAULT 0,
                reviews_count INTEGER DEFAULT 0,
                is_featured INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)

        # Корзина
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                UNIQUE(user_id, product_id)
            )
        """)

        # Избранное
        await db.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                UNIQUE(user_id, product_id)
            )
        """)

        # Заказы
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                total REAL NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Товары в заказе
        await db.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # Отзывы
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)

        await db.commit()

        # Добавляем тестовые данные если БД пустая
        cursor = await db.execute("SELECT COUNT(*) FROM categories")
        count = (await cursor.fetchone())[0]

        if count == 0:
            await add_sample_data(db)

        print("✅ База данных инициализирована")


async def add_sample_data(db):
    """Добавление тестовых данных"""

    # Категории
    categories = [
        ("Электроника", "electronics", "📱"),
        ("Одежда", "clothing", "👕"),
        ("Дом и сад", "home", "🏠"),
        ("Спорт", "sports", "⚽"),
        ("Книги", "books", "📚"),
        ("Красота", "beauty", "💄"),
    ]

    for name, slug, icon in categories:
        await db.execute(
            "INSERT INTO categories (name, slug, icon) VALUES (?, ?, ?)",
            (name, slug, icon)
        )

    # Товары
    products = [
        # Электроника
        ("iPhone 15 Pro", "iphone-15-pro", "Флагманский смартфон Apple с чипом A17 Pro", 129990, 139990, 1, "📱", 50, 4.9, 128, 1),
        ("MacBook Air M3", "macbook-air-m3", "Тонкий и легкий ноутбук с процессором M3", 149990, None, 1, "💻", 30, 4.8, 85, 1),
        ("AirPods Pro 2", "airpods-pro-2", "Беспроводные наушники с активным шумоподавлением", 24990, 27990, 1, "🎧", 100, 4.7, 256, 1),
        ("Apple Watch Ultra 2", "apple-watch-ultra-2", "Премиальные смарт-часы для спорта", 89990, None, 1, "⌚", 25, 4.9, 64, 1),
        ("iPad Pro 12.9", "ipad-pro-12", "Профессиональный планшет с M2", 109990, 119990, 1, "📱", 40, 4.8, 92, 0),
        ("Samsung Galaxy S24 Ultra", "samsung-s24-ultra", "Флагман Samsung с AI функциями", 119990, None, 1, "📱", 45, 4.7, 156, 1),
        ("Sony WH-1000XM5", "sony-wh1000xm5", "Лучшие беспроводные наушники", 34990, 39990, 1, "🎧", 60, 4.8, 312, 0),
        ("Nintendo Switch OLED", "nintendo-switch-oled", "Игровая консоль с OLED экраном", 29990, None, 1, "🎮", 35, 4.6, 178, 0),

        # Одежда
        ("Худи Nike Premium", "nike-hoodie-premium", "Комфортное худи из органического хлопка", 7990, 9990, 2, "👕", 200, 4.5, 89, 1),
        ("Кроссовки Adidas Ultraboost", "adidas-ultraboost", "Беговые кроссовки с технологией Boost", 15990, 18990, 2, "👟", 80, 4.7, 234, 1),
        ("Джинсы Levi's 501", "levis-501", "Классические джинсы прямого кроя", 8990, None, 2, "👖", 150, 4.6, 167, 0),
        ("Пуховик North Face", "north-face-puffer", "Теплый зимний пуховик", 24990, 29990, 2, "🧥", 40, 4.8, 78, 1),

        # Дом и сад
        ("Кофемашина DeLonghi", "delonghi-coffee", "Автоматическая кофемашина для дома", 49990, 59990, 3, "☕", 25, 4.9, 156, 1),
        ("Робот-пылесос Xiaomi", "xiaomi-vacuum", "Умный пылесос с лидаром", 29990, 34990, 3, "🤖", 50, 4.6, 289, 1),
        ("Набор постельного белья", "bed-linen-set", "Постельное белье из египетского хлопка", 5990, 7990, 3, "🛏️", 100, 4.4, 67, 0),
        ("LED гирлянда", "led-garland", "Праздничная гирлянда 10 метров", 1290, 1590, 3, "💡", 300, 4.3, 45, 0),

        # Спорт
        ("Беговая дорожка", "treadmill-pro", "Профессиональная беговая дорожка", 79990, 89990, 4, "🏃", 10, 4.7, 34, 1),
        ("Гантели разборные 20кг", "dumbbells-20kg", "Набор разборных гантелей", 6990, None, 4, "💪", 80, 4.5, 123, 0),
        ("Йога-мат Premium", "yoga-mat", "Коврик для йоги 6мм", 2490, 2990, 4, "🧘", 200, 4.6, 89, 0),
        ("Велосипед горный", "mountain-bike", "21-скоростной горный велосипед", 34990, 39990, 4, "🚴", 15, 4.8, 56, 1),

        # Книги
        ("Атомные привычки", "atomic-habits", "Джеймс Клир — книга о формировании привычек", 890, 990, 5, "📖", 500, 4.9, 1256, 1),
        ("Думай медленно, решай быстро", "thinking-fast-slow", "Даниэль Канеман о принятии решений", 790, None, 5, "📖", 300, 4.8, 892, 0),
        ("Python для начинающих", "python-beginners", "Полное руководство по Python", 1290, 1490, 5, "📖", 200, 4.7, 234, 1),

        # Красота
        ("Набор уходовой косметики", "skincare-set", "Комплексный набор для ухода за кожей", 4990, 6990, 6, "✨", 100, 4.6, 178, 1),
        ("Парфюм Chanel", "chanel-perfume", "Культовый аромат Chanel N°5", 12990, None, 6, "💐", 30, 4.9, 89, 1),
        ("Фен Dyson Supersonic", "dyson-supersonic", "Профессиональный фен для волос", 44990, 49990, 6, "💨", 20, 4.8, 167, 0),
    ]

    for p in products:
        await db.execute("""
            INSERT INTO products (name, slug, description, price, old_price, category_id, image, stock, rating, reviews_count, is_featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, p)

    # Админ пользователь
    await db.execute("""
        INSERT INTO users (email, password, name, is_admin)
        VALUES ('admin@shop.com', 'admin123', 'Администратор', 1)
    """)

    # Тестовый пользователь
    await db.execute("""
        INSERT INTO users (email, password, name, phone, address)
        VALUES ('user@test.com', '123456', 'Иван Петров', '+7 999 123-45-67', 'г. Москва, ул. Примерная, д. 1')
    """)

    await db.commit()
    print("✅ Тестовые данные добавлены")


# ═══════════════════════════════════════════════════════════════
# ПОЛЬЗОВАТЕЛИ
# ═══════════════════════════════════════════════════════════════

async def get_user_by_email(email: str) -> Optional[Dict]:
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_user_by_id(user_id: int) -> Optional[Dict]:
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def create_user(email: str, password: str, name: str) -> int:
    async with get_db() as db:
        cursor = await db.execute(
            "INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
            (email, password, name)
        )
        await db.commit()
        return cursor.lastrowid


async def update_user(user_id: int, **kwargs):
    async with get_db() as db:
        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        await db.execute(f"UPDATE users SET {fields} WHERE id = ?", values)
        await db.commit()


async def get_all_users() -> List[Dict]:
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM users ORDER BY created_at DESC")
        return [dict(row) for row in await cursor.fetchall()]


# ═══════════════════════════════════════════════════════════════
# КАТЕГОРИИ
# ═══════════════════════════════════════════════════════════════

async def get_categories() -> List[Dict]:
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT c.*, COUNT(p.id) as products_count
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id AND p.is_active = 1
            GROUP BY c.id
            ORDER BY c.name
        """)
        return [dict(row) for row in await cursor.fetchall()]


async def get_category_by_slug(slug: str) -> Optional[Dict]:
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM categories WHERE slug = ?", (slug,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_category_by_id(category_id: int) -> Optional[Dict]:
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


# ═══════════════════════════════════════════════════════════════
# ТОВАРЫ
# ═══════════════════════════════════════════════════════════════

async def get_products(
    category_id: int = None,
    search: str = None,
    min_price: float = None,
    max_price: float = None,
    sort: str = "popular",
    limit: int = 50,
    offset: int = 0
) -> List[Dict]:
    async with get_db() as db:
        sql = """
            SELECT p.*, c.name as category_name, c.slug as category_slug
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1
        """
        params = []

        if category_id:
            sql += " AND p.category_id = ?"
            params.append(category_id)

        if search:
            sql += " AND (p.name LIKE ? OR p.description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        if min_price is not None:
            sql += " AND p.price >= ?"
            params.append(min_price)

        if max_price is not None:
            sql += " AND p.price <= ?"
            params.append(max_price)

        # Сортировка
        sort_options = {
            "popular": "p.reviews_count DESC",
            "rating": "p.rating DESC",
            "price_asc": "p.price ASC",
            "price_desc": "p.price DESC",
            "new": "p.created_at DESC"
        }
        sql += f" ORDER BY {sort_options.get(sort, 'p.reviews_count DESC')}"

        sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await db.execute(sql, params)
        return [dict(row) for row in await cursor.fetchall()]


async def get_all_products_admin() -> List[Dict]:
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.created_at DESC
        """)
        return [dict(row) for row in await cursor.fetchall()]


async def get_product_by_slug(slug: str) -> Optional[Dict]:
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT p.*, c.name as category_name, c.slug as category_slug
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.slug = ?
        """, (slug,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_product_by_id(product_id: int) -> Optional[Dict]:
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_featured_products(limit: int = 8) -> List[Dict]:
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_featured = 1 AND p.is_active = 1
            ORDER BY p.rating DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in await cursor.fetchall()]


async def search_products(query: str, limit: int = 20) -> List[Dict]:
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1 AND (p.name LIKE ? OR p.description LIKE ?)
            ORDER BY p.rating DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        return [dict(row) for row in await cursor.fetchall()]


# ═══════════════════════════════════════════════════════════════
# КОРЗИНА
# ═══════════════════════════════════════════════════════════════

async def get_cart(user_id: int) -> List[Dict]:
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT ci.*, p.name, p.price, p.old_price, p.image, p.slug, p.stock
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = ?
            ORDER BY ci.created_at DESC
        """, (user_id,))
        return [dict(row) for row in await cursor.fetchall()]


async def get_cart_count(user_id: int) -> int:
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT COALESCE(SUM(quantity), 0) FROM cart_items WHERE user_id = ?",
            (user_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0


async def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    async with get_db() as db:
        # Проверяем, есть ли уже в корзине
        cursor = await db.execute(
            "SELECT id, quantity FROM cart_items WHERE user_id = ? AND product_id = ?",
            (user_id, product_id)
        )
        existing = await cursor.fetchone()

        if existing:
            new_qty = existing[1] + quantity
            await db.execute(
                "UPDATE cart_items SET quantity = ? WHERE id = ?",
                (new_qty, existing[0])
            )
        else:
            await db.execute(
                "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
                (user_id, product_id, quantity)
            )

        await db.commit()


async def update_cart_item(user_id: int, product_id: int, quantity: int):
    async with get_db() as db:
        if quantity <= 0:
            await db.execute(
                "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
                (user_id, product_id)
            )
        else:
            await db.execute(
                "UPDATE cart_items SET quantity = ? WHERE user_id = ? AND product_id = ?",
                (quantity, user_id, product_id)
            )
        await db.commit()


async def remove_from_cart(user_id: int, product_id: int):
    async with get_db() as db:
        await db.execute(
            "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
            (user_id, product_id)
        )
        await db.commit()


async def clear_cart(user_id: int):
    async with get_db() as db:
        await db.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
        await db.commit()


# ═══════════════════════════════════════════════════════════════
# ИЗБРАННОЕ
# ═══════════════════════════════════════════════════════════════

async def get_favorites(user_id: int) -> List[Dict]:
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT f.*, p.name, p.price, p.old_price, p.image, p.slug, p.rating
            FROM favorites f
            JOIN products p ON f.product_id = p.id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
        """, (user_id,))
        return [dict(row) for row in await cursor.fetchall()]


async def get_favorites_count(user_id: int) -> int:
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM favorites WHERE user_id = ?",
            (user_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0


async def is_favorite(user_id: int, product_id: int) -> bool:
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT 1 FROM favorites WHERE user_id = ? AND product_id = ?",
            (user_id, product_id)
        )
        return await cursor.fetchone() is not None


async def toggle_favorite(user_id: int, product_id: int) -> bool:
    """Возвращает True если добавлено, False если удалено"""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id FROM favorites WHERE user_id = ? AND product_id = ?",
            (user_id, product_id)
        )
        existing = await cursor.fetchone()

        if existing:
            await db.execute("DELETE FROM favorites WHERE id = ?", (existing[0],))
            await db.commit()
            return False
        else:
            await db.execute(
                "INSERT INTO favorites (user_id, product_id) VALUES (?, ?)",
                (user_id, product_id)
            )
            await db.commit()
            return True


# ═══════════════════════════════════════════════════════════════
# ЗАКАЗЫ
# ═══════════════════════════════════════════════════════════════

async def create_order(user_id: int, name: str, email: str, phone: str, address: str, comment: str = None) -> int:
    async with get_db() as db:
        # Получаем корзину
        cart = await get_cart(user_id)
        if not cart:
            return None

        # Считаем сумму
        total = sum(item['price'] * item['quantity'] for item in cart)

        # Создаем заказ
        cursor = await db.execute("""
            INSERT INTO orders (user_id, total, name, email, phone, address, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, total, name, email, phone, address, comment))
        order_id = cursor.lastrowid

        # Добавляем товары
        for item in cart:
            await db.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, item['product_id'], item['quantity'], item['price']))

            # Уменьшаем остаток
            await db.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (item['quantity'], item['product_id'])
            )

        # Очищаем корзину
        await db.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))

        await db.commit()
        return order_id


async def get_user_orders(user_id: int) -> List[Dict]:
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC
        """, (user_id,))

        orders = []
        for row in await cursor.fetchall():
            order = dict(row)

            # Получаем товары заказа
            items_cursor = await db.execute("""
                SELECT oi.*, p.name, p.image, p.slug
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?
            """, (order['id'],))
            order['items'] = [dict(item) for item in await items_cursor.fetchall()]

            orders.append(order)

        return orders


async def get_order_by_id(order_id: int) -> Optional[Dict]:
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = await cursor.fetchone()

        if not row:
            return None

        order = dict(row)

        # Получаем товары
        items_cursor = await db.execute("""
            SELECT oi.*, p.name, p.image, p.slug
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """, (order_id,))
        order['items'] = [dict(item) for item in await items_cursor.fetchall()]

        return order


async def get_all_orders(status: str = None, limit: int = 50) -> List[Dict]:
    """Для админ-панели"""
    async with get_db() as db:
        sql = """
            SELECT o.*, u.name as user_name, u.email as user_email
            FROM orders o
            JOIN users u ON o.user_id = u.id
        """
        params = []

        if status:
            sql += " WHERE o.status = ?"
            params.append(status)

        sql += " ORDER BY o.created_at DESC LIMIT ?"
        params.append(limit)

        cursor = await db.execute(sql, params)
        orders = []
        for row in await cursor.fetchall():
            order = dict(row)
            # Получаем товары заказа
            items_cursor = await db.execute("""
                SELECT oi.*, p.name, p.image
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?
            """, (order['id'],))
            order['items'] = [dict(item) for item in await items_cursor.fetchall()]
            orders.append(order)
        return orders


async def update_order_status(order_id: int, status: str):
    async with get_db() as db:
        await db.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id)
        )
        await db.commit()


# ═══════════════════════════════════════════════════════════════
# АДМИН - ТОВАРЫ
# ═══════════════════════════════════════════════════════════════

async def create_product(data: Dict) -> int:
    async with get_db() as db:
        cursor = await db.execute("""
            INSERT INTO products (name, slug, description, price, old_price, category_id, image, stock, is_featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['name'], data['slug'], data.get('description'),
            data['price'], data.get('old_price'), data.get('category_id'),
            data.get('image', '📦'), data.get('stock', 0), data.get('is_featured', 0)
        ))
        await db.commit()
        return cursor.lastrowid


async def update_product(product_id: int, data: Dict):
    async with get_db() as db:
        fields = ', '.join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [product_id]
        await db.execute(f"UPDATE products SET {fields} WHERE id = ?", values)
        await db.commit()


async def delete_product(product_id: int):
    async with get_db() as db:
        await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        await db.commit()


# ═══════════════════════════════════════════════════════════════
# СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

async def get_stats() -> Dict:
    """Статистика для админ-панели"""
    async with get_db() as db:
        stats = {}

        # Общее количество заказов и сумма
        cursor = await db.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM orders")
        row = await cursor.fetchone()
        stats['total_orders'] = row[0]
        stats['total_revenue'] = row[1]

        # Заказы по статусам
        cursor = await db.execute("""
            SELECT status, COUNT(*) as cnt FROM orders GROUP BY status
        """)
        stats['orders_by_status'] = {row[0]: row[1] for row in await cursor.fetchall()}

        # Пользователи
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
        stats['total_users'] = (await cursor.fetchone())[0]

        # Товары
        cursor = await db.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
        stats['total_products'] = (await cursor.fetchone())[0]

        # Товары с низким остатком
        cursor = await db.execute("SELECT COUNT(*) FROM products WHERE stock < 10 AND is_active = 1")
        stats['low_stock'] = (await cursor.fetchone())[0]

        return stats