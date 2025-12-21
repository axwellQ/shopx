

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional
import uvicorn
from database import *

app = FastAPI(title="🛒 ShopMax - Маркетплейс")
app.add_middleware(SessionMiddleware, secret_key="supersecretkey123shopmax")


# ═══════════════════════════════════════════════════════════════
# ИНИЦИАЛИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    await init_database()


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def get_user_id(request: Request) -> Optional[int]:
    return request.session.get("user_id")


async def get_current_user(request: Request) -> Optional[dict]:
    user_id = get_user_id(request)
    if user_id:
        return await get_user_by_id(user_id)
    return None


def format_price(price: float) -> str:
    return f"{price:,.0f}".replace(",", " ") + " ₽"


# ═══════════════════════════════════════════════════════════════
# HTML ШАБЛОН
# ═══════════════════════════════════════════════════════════════

def base_template(content: str, title: str, request: Request, user: dict = None,
                  cart_count: int = 0, favorites_count: int = 0) -> str:
    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | ShopMax</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --success: #10b981;
            --danger: #ef4444;
            --dark: #1e293b;
            --gray: #64748b;
            --light: #f1f5f9;
            --white: #ffffff;
            --shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
            --radius: 12px;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background: var(--light);
            color: var(--dark);
            line-height: 1.6;
        }}

        .header {{
            background: var(--white);
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 1000;
        }}

        .header-top {{
            background: var(--dark);
            color: var(--white);
            padding: 8px 0;
            font-size: 13px;
        }}

        .header-main {{ padding: 16px 0; }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        .header-content {{
            display: flex;
            align-items: center;
            gap: 30px;
            flex-wrap: wrap;
        }}

        .logo {{
            font-size: 28px;
            font-weight: 800;
            color: var(--primary);
            text-decoration: none;
        }}

        .search-box {{
            flex: 1;
            max-width: 600px;
            position: relative;
        }}

        .search-box input {{
            width: 100%;
            padding: 14px 50px 14px 20px;
            border: 2px solid var(--light);
            border-radius: 50px;
            font-size: 15px;
        }}

        .search-box input:focus {{
            outline: none;
            border-color: var(--primary);
        }}

        .search-box button {{
            position: absolute;
            right: 6px;
            top: 6px;
            bottom: 6px;
            padding: 0 20px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 50px;
            cursor: pointer;
        }}

        .header-actions {{
            display: flex;
            gap: 8px;
        }}

        .header-btn {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px 16px;
            text-decoration: none;
            color: var(--dark);
            border-radius: var(--radius);
            transition: all 0.3s;
            position: relative;
            font-size: 13px;
        }}

        .header-btn:hover {{
            background: var(--light);
            color: var(--primary);
        }}

        .header-btn .icon {{ font-size: 24px; }}

        .badge {{
            position: absolute;
            top: 4px;
            right: 8px;
            background: var(--danger);
            color: white;
            font-size: 11px;
            padding: 2px 6px;
            border-radius: 50px;
        }}

        main {{
            padding: 30px 0;
            min-height: calc(100vh - 200px);
        }}

        .card {{
            background: var(--white);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            overflow: hidden;
        }}

        .card-header {{
            padding: 20px 24px;
            border-bottom: 1px solid var(--light);
            font-weight: 600;
            font-size: 18px;
        }}

        .card-body {{ padding: 24px; }}

        .products-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 24px;
        }}

        .product-card {{
            background: var(--white);
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow);
            transition: all 0.3s;
        }}

        .product-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-lg);
        }}

        .product-image {{
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            font-size: 72px;
            position: relative;
        }}

        .product-badge {{
            position: absolute;
            top: 12px;
            left: 12px;
            background: var(--danger);
            color: white;
            padding: 4px 12px;
            border-radius: 50px;
            font-size: 12px;
            font-weight: 600;
        }}

        .product-favorite {{
            position: absolute;
            top: 12px;
            right: 12px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: white;
            border: none;
            cursor: pointer;
            font-size: 20px;
            box-shadow: var(--shadow);
        }}

        .product-favorite.active {{
            background: var(--danger);
            color: white;
        }}

        .product-info {{ padding: 16px; }}

        .product-category {{
            font-size: 12px;
            color: var(--primary);
            font-weight: 500;
            text-transform: uppercase;
        }}

        .product-title {{
            font-size: 15px;
            font-weight: 600;
            margin: 8px 0;
        }}

        .product-title a {{
            color: inherit;
            text-decoration: none;
        }}

        .product-title a:hover {{ color: var(--primary); }}

        .product-rating {{
            display: flex;
            gap: 4px;
            font-size: 13px;
            color: var(--gray);
            margin-bottom: 12px;
        }}

        .product-rating .stars {{ color: #fbbf24; }}

        .product-price {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }}

        .price-current {{
            font-size: 20px;
            font-weight: 700;
        }}

        .price-old {{
            font-size: 14px;
            color: var(--gray);
            text-decoration: line-through;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 24px;
            border-radius: var(--radius);
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            border: none;
            text-decoration: none;
            transition: all 0.3s;
        }}

        .btn-primary {{
            background: var(--primary);
            color: white;
        }}

        .btn-primary:hover {{
            background: var(--primary-dark);
        }}

        .btn-secondary {{
            background: var(--light);
            color: var(--dark);
        }}

        .btn-success {{
            background: var(--success);
            color: white;
        }}

        .btn-danger {{
            background: var(--danger);
            color: white;
        }}

        .btn-outline {{
            background: transparent;
            border: 2px solid var(--primary);
            color: var(--primary);
        }}

        .btn-block {{ width: 100%; }}
        .btn-lg {{ padding: 16px 32px; font-size: 16px; }}
        .btn-sm {{ padding: 8px 16px; font-size: 13px; }}

        .form-group {{ margin-bottom: 20px; }}

        .form-label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }}

        .form-control {{
            width: 100%;
            padding: 14px 16px;
            border: 2px solid var(--light);
            border-radius: var(--radius);
            font-size: 15px;
        }}

        .form-control:focus {{
            outline: none;
            border-color: var(--primary);
        }}

        textarea.form-control {{
            resize: vertical;
            min-height: 100px;
        }}

        .alert {{
            padding: 16px 20px;
            border-radius: var(--radius);
            margin-bottom: 20px;
        }}

        .alert-success {{ background: #d1fae5; color: #065f46; }}
        .alert-error {{ background: #fee2e2; color: #991b1b; }}

        .page-header {{ margin-bottom: 30px; }}

        .page-title {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .page-subtitle {{
            color: var(--gray);
            font-size: 16px;
        }}

        .hero {{
            background: linear-gradient(135deg, var(--primary) 0%, #8b5cf6 100%);
            color: white;
            padding: 60px 40px;
            border-radius: 20px;
            margin-bottom: 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .hero-content h1 {{
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 16px;
        }}

        .hero-content p {{
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 24px;
        }}

        .hero-image {{ font-size: 150px; }}

        .section {{ margin-bottom: 50px; }}

        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }}

        .section-title {{
            font-size: 24px;
            font-weight: 700;
        }}

        .categories-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 16px;
        }}

        .category-card {{
            background: var(--white);
            padding: 24px;
            border-radius: var(--radius);
            text-align: center;
            text-decoration: none;
            color: var(--dark);
            box-shadow: var(--shadow);
            transition: all 0.3s;
        }}

        .category-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-lg);
        }}

        .category-card .icon {{
            font-size: 48px;
            margin-bottom: 12px;
        }}

        .category-card .name {{ font-weight: 600; }}
        .category-card .count {{ font-size: 13px; color: var(--gray); }}

        .sidebar-layout {{
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 30px;
        }}

        .filters {{
            background: var(--white);
            border-radius: var(--radius);
            padding: 24px;
            box-shadow: var(--shadow);
            position: sticky;
            top: 100px;
        }}

        .filter-section {{
            margin-bottom: 24px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--light);
        }}

        .filter-section:last-child {{ border-bottom: none; }}

        .filter-title {{
            font-weight: 600;
            margin-bottom: 16px;
        }}

        .cart-item {{
            display: flex;
            gap: 20px;
            padding: 20px 0;
            border-bottom: 1px solid var(--light);
        }}

        .cart-item:last-child {{ border-bottom: none; }}

        .cart-item-image {{
            width: 100px;
            height: 100px;
            background: var(--light);
            border-radius: var(--radius);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
        }}

        .cart-item-info {{ flex: 1; }}

        .cart-item-title {{
            font-weight: 600;
            margin-bottom: 8px;
        }}

        .cart-item-title a {{
            color: var(--dark);
            text-decoration: none;
        }}

        .cart-item-title a:hover {{ color: var(--primary); }}

        .cart-item-price {{
            font-size: 18px;
            font-weight: 700;
            color: var(--primary);
        }}

        .quantity-control {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 12px;
        }}

        .quantity-btn {{
            width: 36px;
            height: 36px;
            border: 2px solid var(--light);
            border-radius: 8px;
            background: white;
            cursor: pointer;
            font-size: 18px;
        }}

        .quantity-btn:hover {{
            border-color: var(--primary);
            color: var(--primary);
        }}

        .quantity-value {{
            font-weight: 600;
            min-width: 40px;
            text-align: center;
        }}

        .cart-summary {{
            background: var(--white);
            border-radius: var(--radius);
            padding: 24px;
            box-shadow: var(--shadow);
            position: sticky;
            top: 100px;
        }}

        .summary-row {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid var(--light);
        }}

        .summary-row:last-of-type {{ border-bottom: none; }}

        .summary-total {{
            font-size: 24px;
            font-weight: 700;
            color: var(--primary);
            padding-top: 16px;
            border-top: 2px solid var(--primary);
        }}

        .checkout-layout {{
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 30px;
        }}

        .order-card {{
            background: var(--white);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            margin-bottom: 20px;
        }}

        .order-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 24px;
            background: var(--light);
        }}

        .order-number {{ font-weight: 700; font-size: 18px; }}

        .order-status {{
            padding: 6px 16px;
            border-radius: 50px;
            font-size: 13px;
            font-weight: 600;
        }}

        .status-pending {{ background: #fef3c7; color: #92400e; }}
        .status-processing {{ background: #dbeafe; color: #1e40af; }}
        .status-shipped {{ background: #e0e7ff; color: #4338ca; }}
        .status-delivered {{ background: #d1fae5; color: #065f46; }}
        .status-cancelled {{ background: #fee2e2; color: #991b1b; }}

        .order-body {{ padding: 20px 24px; }}

        .order-items {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 16px;
        }}

        .order-item-mini {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: var(--light);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 13px;
        }}

        .order-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 16px;
            border-top: 1px solid var(--light);
        }}

        .product-detail {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 50px;
            background: var(--white);
            border-radius: var(--radius);
            padding: 40px;
            box-shadow: var(--shadow);
        }}

        .product-gallery {{
            background: var(--light);
            border-radius: var(--radius);
            height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 150px;
        }}

        .product-detail-info h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 16px;
        }}

        .product-detail-price {{
            font-size: 36px;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 8px;
        }}

        .product-detail-old-price {{
            font-size: 20px;
            color: var(--gray);
            text-decoration: line-through;
            margin-bottom: 20px;
        }}

        .product-stock {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 50px;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 24px;
        }}

        .stock-in {{ background: #d1fae5; color: #065f46; }}
        .stock-low {{ background: #fef3c7; color: #92400e; }}
        .stock-out {{ background: #fee2e2; color: #991b1b; }}

        .product-actions-detail {{
            display: flex;
            gap: 12px;
            margin-top: 30px;
        }}

        .auth-container {{
            max-width: 450px;
            margin: 50px auto;
        }}

        .auth-card {{
            background: var(--white);
            border-radius: var(--radius);
            padding: 40px;
            box-shadow: var(--shadow-lg);
        }}

        .auth-title {{
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 8px;
        }}

        .auth-subtitle {{
            color: var(--gray);
            text-align: center;
            margin-bottom: 32px;
        }}

        .auth-footer {{
            text-align: center;
            margin-top: 24px;
            padding-top: 24px;
            border-top: 1px solid var(--light);
            color: var(--gray);
        }}

        .auth-footer a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }}

        .empty-state {{
            text-align: center;
            padding: 60px 20px;
        }}

        .empty-state .icon {{
            font-size: 80px;
            margin-bottom: 20px;
        }}

        .empty-state h3 {{
            font-size: 24px;
            margin-bottom: 12px;
        }}

        .empty-state p {{
            color: var(--gray);
            margin-bottom: 24px;
        }}

        .grid {{ display: grid; gap: 24px; }}
        .grid-2 {{ grid-template-columns: repeat(2, 1fr); }}

        .admin-nav {{
            display: flex;
            gap: 8px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}

        .admin-nav a {{
            padding: 12px 24px;
            background: var(--white);
            border-radius: var(--radius);
            text-decoration: none;
            color: var(--dark);
            font-weight: 500;
            box-shadow: var(--shadow);
        }}

        .admin-nav a:hover, .admin-nav a.active {{
            background: var(--primary);
            color: white;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: var(--white);
            padding: 24px;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
        }}

        .stat-card .icon {{ font-size: 40px; margin-bottom: 12px; }}
        .stat-card .value {{ font-size: 32px; font-weight: 800; }}
        .stat-card .label {{ color: var(--gray); font-size: 14px; }}

        .table-container {{ overflow-x: auto; }}

        .table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .table th, .table td {{
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid var(--light);
        }}

        .table th {{
            font-weight: 600;
            color: var(--gray);
            font-size: 13px;
            text-transform: uppercase;
        }}

        .table tr:hover {{ background: var(--light); }}

        .footer {{
            background: var(--dark);
            color: white;
            padding: 40px 0 20px;
            margin-top: 60px;
        }}

        .footer-content {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 30px;
        }}

        .footer-brand {{ font-size: 24px; font-weight: 800; }}
        .footer-text {{ color: #94a3b8; font-size: 14px; margin-top: 10px; }}

        .footer-bottom {{
            border-top: 1px solid #334155;
            padding-top: 20px;
            margin-top: 30px;
            text-align: center;
            color: #64748b;
            font-size: 14px;
        }}

        .toast {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--dark);
            color: white;
            padding: 16px 24px;
            border-radius: var(--radius);
            box-shadow: var(--shadow-lg);
            z-index: 9999;
            animation: slideIn 0.3s ease;
        }}

        .toast.success {{ background: var(--success); }}
        .toast.error {{ background: var(--danger); }}

        @keyframes slideIn {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}

        .breadcrumb {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: var(--gray);
            margin-bottom: 16px;
        }}

        .breadcrumb a {{
            color: var(--primary);
            text-decoration: none;
        }}

        @media (max-width: 1024px) {{
            .sidebar-layout, .product-detail, .checkout-layout {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 768px) {{
            .header-content {{ flex-wrap: wrap; }}
            .search-box {{ order: 3; flex: 1 1 100%; max-width: 100%; margin-top: 16px; }}
            .hero {{ flex-direction: column; text-align: center; padding: 40px 20px; }}
            .hero-content h1 {{ font-size: 28px; }}
            .hero-image {{ font-size: 100px; }}
            .grid-2 {{ grid-template-columns: 1fr; }}
            .cart-item {{ flex-direction: column; }}
            .cart-item-image {{ width: 100%; height: 150px; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-top">
            <div class="container" style="display: flex; justify-content: space-between;">
                <span>📞 8-800-555-35-35</span>
                <span>🚚 Бесплатная доставка от 5000 ₽</span>
            </div>
        </div>
        <div class="header-main">
            <div class="container">
                <div class="header-content">
                    <a href="/" class="logo">🛒 ShopMax</a>

                    <form class="search-box" action="/catalog" method="get">
                        <input type="text" name="q" placeholder="Поиск товаров...">
                        <button type="submit">🔍</button>
                    </form>

                    <div class="header-actions">
                        <a href="/favorites" class="header-btn">
                            <span class="icon">❤️</span>
                            <span>Избранное</span>
                            {"<span class='badge'>" + str(favorites_count) + "</span>" if favorites_count else ""}
                        </a>
                        <a href="/cart" class="header-btn">
                            <span class="icon">🛒</span>
                            <span>Корзина</span>
                            {"<span class='badge'>" + str(cart_count) + "</span>" if cart_count else ""}
                        </a>
                        {f'''
                        <a href="/profile" class="header-btn">
                            <span class="icon">👤</span>
                            <span>{user["name"]}</span>
                        </a>
                        ''' if user else '''
                        <a href="/login" class="header-btn">
                            <span class="icon">👤</span>
                            <span>Войти</span>
                        </a>
                        '''}
                    </div>
                </div>
            </div>
        </div>
    </header>

    <main>
        <div class="container">
            {content}
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div>
                    <div class="footer-brand">🛒 ShopMax</div>
                    <p class="footer-text">Ваш надежный интернет-магазин</p>
                </div>
                <div>
                    <p class="footer-text">📞 8-800-555-35-35</p>
                    <p class="footer-text">✉️ info@shopmax.ru</p>
                </div>
            </div>
            <div class="footer-bottom">
                © 2024 ShopMax. Все права защищены.
            </div>
        </div>
    </footer>

    <script>
        function showToast(message, type = 'success') {{
            const toast = document.createElement('div');
            toast.className = 'toast ' + type;
            toast.innerHTML = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }}

        async function addToCart(productId) {{
            const response = await fetch('/api/cart/add', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ product_id: productId, quantity: 1 }})
            }});
            const data = await response.json();
            if (data.success) {{
                showToast('✅ Товар добавлен в корзину');
                location.reload();
            }} else if (data.redirect) {{
                window.location.href = data.redirect;
            }}
        }}

        async function toggleFavorite(productId, btn) {{
            const response = await fetch('/api/favorites/toggle', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ product_id: productId }})
            }});
            const data = await response.json();
            if (data.success) {{
                if (data.added) {{
                    btn.classList.add('active');
                    btn.innerHTML = '❤️';
                    showToast('💖 Добавлено в избранное');
                }} else {{
                    btn.classList.remove('active');
                    btn.innerHTML = '🤍';
                }}
                location.reload();
            }} else if (data.redirect) {{
                window.location.href = data.redirect;
            }}
        }}

        async function updateQuantity(productId, delta) {{
            const valueEl = document.getElementById('qty-' + productId);
            let newQty = parseInt(valueEl.textContent) + delta;
            if (newQty < 1) newQty = 1;

            await fetch('/api/cart/update', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ product_id: productId, quantity: newQty }})
            }});
            location.reload();
        }}

        async function removeFromCart(productId) {{
            if (!confirm('Удалить товар из корзины?')) return;
            await fetch('/api/cart/remove', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ product_id: productId }})
            }});
            location.reload();
        }}
    </script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════
# ГЛАВНАЯ СТРАНИЦА
# ═══════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = await get_current_user(request)
    user_id = get_user_id(request)

    cart_count = await get_cart_count(user_id) if user_id else 0
    favorites_count = await get_favorites_count(user_id) if user_id else 0

    categories = await get_categories()
    featured = await get_featured_products(8)

    user_favorites = []
    if user_id:
        favs = await get_favorites(user_id)
        user_favorites = [f['product_id'] for f in favs]

    categories_html = "".join(f"""
        <a href="/catalog?category={c['id']}" class="category-card">
            <div class="icon">{c['icon']}</div>
            <div class="name">{c['name']}</div>
            <div class="count">{c['products_count']} товаров</div>
        </a>
    """ for c in categories)

    def product_card(p):
        discount = ""
        if p.get('old_price') and p['old_price'] > p['price']:
            percent = int((1 - p['price'] / p['old_price']) * 100)
            discount = f'<span class="product-badge">-{percent}%</span>'

        is_fav = p['id'] in user_favorites
        fav_class = 'active' if is_fav else ''
        fav_icon = '❤️' if is_fav else '🤍'
        stars = '⭐' * int(p.get('rating', 0))

        return f"""
        <div class="product-card">
            <div class="product-image">
                {discount}
                <button class="product-favorite {fav_class}" onclick="toggleFavorite({p['id']}, this)">
                    {fav_icon}
                </button>
                {p.get('image', '📦')}
            </div>
            <div class="product-info">
                <div class="product-category">{p.get('category_name', '')}</div>
                <h3 class="product-title">
                    <a href="/product/{p['id']}">{p['name']}</a>
                </h3>
                <div class="product-rating">
                    <span class="stars">{stars}</span>
                    <span>({p.get('reviews_count', 0)})</span>
                </div>
                <div class="product-price">
                    <span class="price-current">{format_price(p['price'])}</span>
                    {f'<span class="price-old">{format_price(p["old_price"])}</span>' if p.get('old_price') else ''}
                </div>
                <button class="btn btn-primary btn-block" onclick="addToCart({p['id']})">
                    🛒 В корзину
                </button>
            </div>
        </div>
        """

    products_html = "".join(product_card(p) for p in featured)

    content = f"""
    <div class="hero">
        <div class="hero-content">
            <h1>Летняя распродажа!</h1>
            <p>Скидки до 50% на электронику и товары для дома</p>
            <a href="/catalog" class="btn btn-lg" style="background: white; color: var(--primary);">
                Смотреть каталог →
            </a>
        </div>
        <div class="hero-image">🎁</div>
    </div>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">📦 Категории</h2>
            <a href="/catalog" class="btn btn-secondary">Все категории →</a>
        </div>
        <div class="categories-grid">
            {categories_html}
        </div>
    </section>

    <section class="section">
        <div class="section-header">
            <h2 class="section-title">🔥 Хиты продаж</h2>
            <a href="/catalog" class="btn btn-secondary">Все товары →</a>
        </div>
        <div class="products-grid">
            {products_html}
        </div>
    </section>
    """

    return HTMLResponse(base_template(content, "Главная", request, user, cart_count, favorites_count))


# ═══════════════════════════════════════════════════════════════
# КАТАЛОГ
# ═══════════════════════════════════════════════════════════════

@app.get("/catalog", response_class=HTMLResponse)
async def catalog(
        request: Request,
        category: int = None,
        sort: str = "popular",
        min_price: float = None,
        max_price: float = None,
        q: str = None
):
    user = await get_current_user(request)
    user_id = get_user_id(request)

    cart_count = await get_cart_count(user_id) if user_id else 0
    favorites_count = await get_favorites_count(user_id) if user_id else 0

    categories = await get_categories()
    current_category = None
    if category:
        current_category = await get_category_by_id(category)

    products = await get_products(
        category_id=category,
        search=q,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )

    user_favorites = []
    if user_id:
        favs = await get_favorites(user_id)
        user_favorites = [f['product_id'] for f in favs]

    categories_html = "".join(f"""
        <a href="/catalog?category={c['id']}" style="display: flex; justify-content: space-between; padding: 10px 0; text-decoration: none; color: {'var(--primary); font-weight: 600' if category == c['id'] else 'var(--dark)'};">
            <span>{c['icon']} {c['name']}</span>
            <span style="color: var(--gray);">{c['products_count']}</span>
        </a>
    """ for c in categories)

    def product_card(p):
        discount = ""
        if p.get('old_price') and p['old_price'] > p['price']:
            percent = int((1 - p['price'] / p['old_price']) * 100)
            discount = f'<span class="product-badge">-{percent}%</span>'

        is_fav = p['id'] in user_favorites
        fav_class = 'active' if is_fav else ''
        fav_icon = '❤️' if is_fav else '🤍'
        stars = '⭐' * int(p.get('rating', 0))

        return f"""
        <div class="product-card">
            <div class="product-image">
                {discount}
                <button class="product-favorite {fav_class}" onclick="toggleFavorite({p['id']}, this)">
                    {fav_icon}
                </button>
                {p.get('image', '📦')}
            </div>
            <div class="product-info">
                <div class="product-category">{p.get('category_name', '')}</div>
                <h3 class="product-title">
                    <a href="/product/{p['id']}">{p['name']}</a>
                </h3>
                <div class="product-rating">
                    <span class="stars">{stars}</span>
                    <span>({p.get('reviews_count', 0)})</span>
                </div>
                <div class="product-price">
                    <span class="price-current">{format_price(p['price'])}</span>
                    {f'<span class="price-old">{format_price(p["old_price"])}</span>' if p.get('old_price') else ''}
                </div>
                <button class="btn btn-primary btn-block" onclick="addToCart({p['id']})">
                    🛒 В корзину
                </button>
            </div>
        </div>
        """

    products_html = "".join(product_card(p) for p in products) if products else """
        <div class="empty-state" style="grid-column: 1/-1;">
            <div class="icon">🔍</div>
            <h3>Товары не найдены</h3>
            <p>Попробуйте изменить фильтры</p>
        </div>
    """

    content = f"""
        <div class="breadcrumb">
            <a href="/">Главная</a> <span>/</span>
            <a href="/catalog">Каталог</a>
            {f'<span>/</span> <span>{current_category["name"]}</span>' if current_category else ''}
        </div>

        <div class="page-header">
            <h1 class="page-title">{current_category['icon'] + ' ' + current_category['name'] if current_category else '📦 Каталог товаров'}</h1>
            <p class="page-subtitle">Найдено {len(products)} товаров</p>
        </div>

        <div class="sidebar-layout">
            <aside>
                <div class="filters">
                    <div class="filter-section">
                        <h4 class="filter-title">Категории</h4>
                        <div style="display: flex; flex-direction: column;">
                            <a href="/catalog" style="display: flex; justify-content: space-between; padding: 10px 0; text-decoration: none; color: {'var(--primary); font-weight: 600' if not category else 'var(--dark)'};">
                                <span>📦 Все товары</span>
                            </a>
                            {categories_html}
                        </div>
                    </div>

                    <form class="filter-section" method="get" action="/catalog">
                        <h4 class="filter-title">Цена</h4>
                        <div style="display: flex; gap: 12px; align-items: center;">
                            <input type="number" name="min_price" placeholder="От" value="{min_price or ''}" 
                                   style="width: 100%; padding: 10px; border: 2px solid var(--light); border-radius: 8px;">
                            <span>—</span>
                            <input type="number" name="max_price" placeholder="До" value="{max_price or ''}"
                                   style="width: 100%; padding: 10px; border: 2px solid var(--light); border-radius: 8px;">
                        </div>
                        {f'<input type="hidden" name="category" value="{category}">' if category else ''}
                        <input type="hidden" name="sort" value="{sort}">
                        <button type="submit" class="btn btn-primary btn-block" style="margin-top: 16px;">
                            Применить
                        </button>
                    </form>

                    <div class="filter-section">
                        <h4 class="filter-title">Сортировка</h4>
                        <select class="form-control" onchange="window.location.href='/catalog?sort='+this.value{'&category=' + '{category}' if category else ''}">
                            <option value="popular" {'selected' if sort == 'popular' else ''}>По популярности</option>
                            <option value="rating" {'selected' if sort == 'rating' else ''}>По рейтингу</option>
                            <option value="price_asc" {'selected' if sort == 'price_asc' else ''}>Сначала дешевые</option>
                            <option value="price_desc" {'selected' if sort == 'price_desc' else ''}>Сначала дорогие</option>
                            <option value="new" {'selected' if sort == 'new' else ''}>Новинки</option>
                        </select>
                    </div>
                </div>
            </aside>

            <div>
                <div class="products-grid">
                    {products_html}
                </div>
            </div>
        </div>
        """

    return HTMLResponse(
        base_template(content, current_category['name'] if current_category else "Каталог", request, user, cart_count,
                      favorites_count))


# ═══════════════════════════════════════════════════════════════
# СТРАНИЦА ТОВАРА
# ═══════════════════════════════════════════════════════════════

@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int):
    user = await get_current_user(request)
    user_id = get_user_id(request)

    cart_count = await get_cart_count(user_id) if user_id else 0
    favorites_count = await get_favorites_count(user_id) if user_id else 0

    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    is_fav = False
    if user_id:
        is_fav = await is_favorite(user_id, product['id'])

    # Статус остатка
    if product['stock'] > 10:
        stock_html = '<div class="product-stock stock-in">✅ В наличии</div>'
    elif product['stock'] > 0:
        stock_html = f'<div class="product-stock stock-low">⚠️ Осталось {product["stock"]} шт</div>'
    else:
        stock_html = '<div class="product-stock stock-out">❌ Нет в наличии</div>'

    stars = '⭐' * int(product.get('rating', 0))

    category = await get_category_by_id(product['category_id']) if product.get('category_id') else None

    content = f"""
        <div class="breadcrumb">
            <a href="/">Главная</a> <span>/</span>
            <a href="/catalog">Каталог</a> <span>/</span>
            {f'<a href="/catalog?category={category["id"]}">{category["name"]}</a> <span>/</span>' if category else ''}
            <span>{product['name']}</span>
        </div>

        <div class="product-detail">
            <div class="product-gallery">
                {product.get('image', '📦')}
            </div>

            <div class="product-detail-info">
                <h1>{product['name']}</h1>

                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px; font-size: 15px;">
                    <span style="color: #fbbf24;">{stars}</span>
                    <span><strong>{product.get('rating', 0)}</strong></span>
                    <span style="color: var(--gray);">• {product.get('reviews_count', 0)} отзывов</span>
                </div>

                <div class="product-detail-price">{format_price(product['price'])}</div>
                {f'<div class="product-detail-old-price">{format_price(product["old_price"])}</div>' if product.get('old_price') else ''}

                {stock_html}

                <p style="color: var(--gray); line-height: 1.8; margin-bottom: 30px;">
                    {product.get('description', 'Описание товара отсутствует.')}
                </p>

                <div class="product-actions-detail">
                    <button class="btn btn-primary btn-lg" onclick="addToCart({product['id']})" {'disabled' if product['stock'] <= 0 else ''}>
                        🛒 Добавить в корзину
                    </button>
                    <button class="btn {'btn-danger' if is_fav else 'btn-outline'} btn-lg" 
                            onclick="toggleFavorite({product['id']}, this)">
                        {'❤️ В избранном' if is_fav else '🤍 В избранное'}
                    </button>
                </div>

                <div style="margin-top: 30px; padding-top: 30px; border-top: 1px solid var(--light);">
                    <div style="display: flex; gap: 30px;">
                        <div>
                            <div style="font-size: 24px; margin-bottom: 8px;">🚚</div>
                            <div style="font-weight: 600;">Доставка</div>
                            <div style="font-size: 13px; color: var(--gray);">1-3 дня</div>
                        </div>
                        <div>
                            <div style="font-size: 24px; margin-bottom: 8px;">💳</div>
                            <div style="font-weight: 600;">Оплата</div>
                            <div style="font-size: 13px; color: var(--gray);">Картой / Наличными</div>
                        </div>
                        <div>
                            <div style="font-size: 24px; margin-bottom: 8px;">🔄</div>
                            <div style="font-weight: 600;">Возврат</div>
                            <div style="font-size: 13px; color: var(--gray);">14 дней</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

    return HTMLResponse(base_template(content, product['name'], request, user, cart_count, favorites_count))


# ═══════════════════════════════════════════════════════════════
# КОРЗИНА
# ═══════════════════════════════════════════════════════════════

@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    user = await get_current_user(request)
    user_id = get_user_id(request)

    if not user_id:
        return RedirectResponse("/login?next=/cart", status_code=302)

    cart = await get_cart(user_id)
    cart_count = sum(item['quantity'] for item in cart)
    favorites_count = await get_favorites_count(user_id)

    if not cart:
        content = """
            <div class="page-header">
                <h1 class="page-title">🛒 Корзина</h1>
            </div>
            <div class="card">
                <div class="empty-state">
                    <div class="icon">🛒</div>
                    <h3>Корзина пуста</h3>
                    <p>Добавьте товары, чтобы оформить заказ</p>
                    <a href="/catalog" class="btn btn-primary">Перейти в каталог</a>
                </div>
            </div>
            """
        return HTMLResponse(base_template(content, "Корзина", request, user, 0, favorites_count))

    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    delivery = 0 if subtotal >= 5000 else 299
    total = subtotal + delivery

    items_html = ""
    for item in cart:
        items_html += f"""
            <div class="cart-item">
                <div class="cart-item-image">{item.get('image', '📦')}</div>
                <div class="cart-item-info">
                    <h4 class="cart-item-title">
                        <a href="/product/{item['product_id']}">{item['name']}</a>
                    </h4>
                    <div class="cart-item-price">{format_price(item['price'])}</div>

                    <div class="quantity-control">
                        <button class="quantity-btn" onclick="updateQuantity({item['product_id']}, -1)">−</button>
                        <span class="quantity-value" id="qty-{item['product_id']}">{item['quantity']}</span>
                        <button class="quantity-btn" onclick="updateQuantity({item['product_id']}, 1)">+</button>
                        <button class="btn btn-sm btn-danger" style="margin-left: auto;" onclick="removeFromCart({item['product_id']})">
                            🗑️ Удалить
                        </button>
                    </div>
                </div>
                <div style="text-align: right; min-width: 120px;">
                    <div style="font-size: 20px; font-weight: 700;">
                        {format_price(item['price'] * item['quantity'])}
                    </div>
                </div>
            </div>
            """

    content = f"""
        <div class="page-header">
            <h1 class="page-title">🛒 Корзина</h1>
            <p class="page-subtitle">{cart_count} товаров</p>
        </div>

        <div class="checkout-layout">
            <div class="card">
                <div class="card-body">
                    {items_html}
                </div>
            </div>

            <div class="cart-summary">
                <h3 style="margin-bottom: 20px;">Ваш заказ</h3>

                <div class="summary-row">
                    <span>Товары ({cart_count})</span>
                    <span>{format_price(subtotal)}</span>
                </div>

                <div class="summary-row">
                    <span>Доставка</span>
                    <span>{'Бесплатно' if delivery == 0 else format_price(delivery)}</span>
                </div>

                {f'<div style="font-size: 13px; color: var(--gray); margin-bottom: 16px;">До бесплатной доставки: {format_price(5000 - subtotal)}</div>' if subtotal < 5000 else ''}

                <div class="summary-row summary-total">
                    <span>Итого</span>
                    <span>{format_price(total)}</span>
                </div>

                <a href="/checkout" class="btn btn-primary btn-lg btn-block" style="margin-top: 20px;">
                    Оформить заказ →
                </a>

                <a href="/catalog" class="btn btn-secondary btn-block" style="margin-top: 12px;">
                    Продолжить покупки
                </a>
            </div>
        </div>
        """

    return HTMLResponse(base_template(content, "Корзина", request, user, cart_count, favorites_count))


# ═══════════════════════════════════════════════════════════════
# ИЗБРАННОЕ
# ═══════════════════════════════════════════════════════════════

@app.get("/favorites", response_class=HTMLResponse)
async def favorites_page(request: Request):
    user = await get_current_user(request)
    user_id = get_user_id(request)

    if not user_id:
        return RedirectResponse("/login?next=/favorites", status_code=302)

    favorites = await get_favorites(user_id)
    cart_count = await get_cart_count(user_id)

    if not favorites:
        content = """
            <div class="page-header">
                <h1 class="page-title">❤️ Избранное</h1>
            </div>
            <div class="card">
                <div class="empty-state">
                    <div class="icon">💔</div>
                    <h3>Список избранного пуст</h3>
                    <p>Добавляйте понравившиеся товары</p>
                    <a href="/catalog" class="btn btn-primary">Перейти в каталог</a>
                </div>
            </div>
            """
        return HTMLResponse(base_template(content, "Избранное", request, user, cart_count, 0))

    products_html = ""
    for item in favorites:
        stars = '⭐' * int(item.get('rating', 0))
        products_html += f"""
            <div class="product-card">
                <div class="product-image">
                    <button class="product-favorite active" onclick="toggleFavorite({item['product_id']}, this)">
                        ❤️
                    </button>
                    {item.get('image', '📦')}
                </div>
                <div class="product-info">
                    <h3 class="product-title">
                        <a href="/product/{item['product_id']}">{item['name']}</a>
                    </h3>
                    <div class="product-rating">
                        <span class="stars">{stars}</span>
                    </div>
                    <div class="product-price">
                        <span class="price-current">{format_price(item['price'])}</span>
                        {f'<span class="price-old">{format_price(item["old_price"])}</span>' if item.get('old_price') else ''}
                    </div>
                    <button class="btn btn-primary btn-block" onclick="addToCart({item['product_id']})">
                        🛒 В корзину
                    </button>
                </div>
            </div>
            """

    content = f"""
        <div class="page-header">
            <h1 class="page-title">❤️ Избранное</h1>
            <p class="page-subtitle">{len(favorites)} товаров</p>
        </div>

        <div class="products-grid">
            {products_html}
        </div>
        """

    return HTMLResponse(base_template(content, "Избранное", request, user, cart_count, len(favorites)))


# ═══════════════════════════════════════════════════════════════
# ОФОРМЛЕНИЕ ЗАКАЗА
# ═══════════════════════════════════════════════════════════════

@app.get("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request):
    user = await get_current_user(request)
    user_id = get_user_id(request)

    if not user_id:
        return RedirectResponse("/login?next=/checkout", status_code=302)

    cart = await get_cart(user_id)
    if not cart:
        return RedirectResponse("/cart", status_code=302)

    cart_count = sum(item['quantity'] for item in cart)
    favorites_count = await get_favorites_count(user_id)

    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    delivery = 0 if subtotal >= 5000 else 299
    total = subtotal + delivery

    items_html = "".join(f"""
            <div style="display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--light);">
                <div style="width: 50px; height: 50px; background: var(--light); border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                    {item.get('image', '📦')}
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: 500;">{item['name']}</div>
                    <div style="color: var(--gray); font-size: 13px;">{item['quantity']} × {format_price(item['price'])}</div>
                </div>
                <div style="font-weight: 600;">{format_price(item['price'] * item['quantity'])}</div>
            </div>
        """ for item in cart)

    content = f"""
        <div class="page-header">
            <h1 class="page-title">📝 Оформление заказа</h1>
        </div>

        <div class="checkout-layout">
            <div>
                <form method="post" action="/checkout">
                    <div class="card" style="margin-bottom: 24px;">
                        <div class="card-header">📍 Контактные данные</div>
                        <div class="card-body">
                            <div class="grid grid-2">
                                <div class="form-group">
                                    <label class="form-label">Имя *</label>
                                    <input type="text" name="name" class="form-control" required 
                                           value="{user.get('name', '')}" placeholder="Иван Иванов">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">Email *</label>
                                    <input type="email" name="email" class="form-control" required 
                                           value="{user.get('email', '')}" placeholder="email@example.com">
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Телефон *</label>
                                <input type="tel" name="phone" class="form-control" required 
                                       value="{user.get('phone', '') or ''}" placeholder="+7 999 123-45-67">
                            </div>
                        </div>
                    </div>

                    <div class="card" style="margin-bottom: 24px;">
                        <div class="card-header">🚚 Доставка</div>
                        <div class="card-body">
                            <div class="form-group">
                                <label class="form-label">Адрес доставки *</label>
                                <textarea name="address" class="form-control" required 
                                          placeholder="Город, улица, дом, квартира">{user.get('address', '') or ''}</textarea>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Комментарий к заказу</label>
                                <textarea name="comment" class="form-control" 
                                          placeholder="Пожелания к заказу..."></textarea>
                            </div>
                        </div>
                    </div>

                    <div class="card" style="margin-bottom: 24px;">
                        <div class="card-header">💳 Способ оплаты</div>
                        <div class="card-body">
                            <label style="display: flex; padding: 16px; background: var(--light); border-radius: var(--radius); margin-bottom: 12px; cursor: pointer;">
                                <input type="radio" name="payment" value="card" checked style="margin-right: 12px;">
                                <div>
                                    <div style="font-weight: 600;">💳 Банковской картой онлайн</div>
                                    <div style="font-size: 13px; color: var(--gray);">Visa, Mastercard, МИР</div>
                                </div>
                            </label>
                            <label style="display: flex; padding: 16px; background: var(--light); border-radius: var(--radius); cursor: pointer;">
                                <input type="radio" name="payment" value="cash" style="margin-right: 12px;">
                                <div>
                                    <div style="font-weight: 600;">💵 Наличными при получении</div>
                                    <div style="font-size: 13px; color: var(--gray);">Оплата курьеру</div>
                                </div>
                            </label>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-success btn-lg btn-block">
                        ✅ Подтвердить заказ на {format_price(total)}
                    </button>
                </form>
            </div>

            <div>
                <div class="cart-summary">
                    <h3 style="margin-bottom: 20px;">🛒 Ваш заказ</h3>
                    <div style="max-height: 300px; overflow-y: auto; margin-bottom: 16px;">
                        {items_html}
                    </div>
                    <div class="summary-row">
                        <span>Товары ({cart_count} шт.)</span>
                        <span>{format_price(subtotal)}</span>
                    </div>
                    <div class="summary-row">
                        <span>Доставка</span>
                        <span>{'Бесплатно ✓' if delivery == 0 else format_price(delivery)}</span>
                    </div>
                    <div class="summary-row summary-total">
                        <span>Итого</span>
                        <span>{format_price(total)}</span>
                    </div>
                </div>
                <a href="/cart" class="btn btn-secondary btn-block" style="margin-top: 16px;">
                    ← Вернуться в корзину
                </a>
            </div>
        </div>
        """

    return HTMLResponse(base_template(content, "Оформление заказа", request, user, cart_count, favorites_count))


@app.post("/checkout", response_class=HTMLResponse)
async def checkout_submit(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        phone: str = Form(...),
        address: str = Form(...),
        comment: str = Form(""),
        payment: str = Form("card")
):
    user_id = get_user_id(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    user = await get_current_user(request)
    cart = await get_cart(user_id)

    if not cart:
        return RedirectResponse("/cart", status_code=302)

    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    delivery = 0 if subtotal >= 5000 else 299
    total = subtotal + delivery

    order_id = await create_order(user_id, name, email, phone, address, comment)

    if not order_id:
        return RedirectResponse("/cart", status_code=302)

    await update_user(user_id, phone=phone, address=address)

    content = f"""
        <div style="max-width: 600px; margin: 50px auto; text-align: center;">
            <div class="card">
                <div class="card-body" style="padding: 60px 40px;">
                    <div style="font-size: 80px; margin-bottom: 24px;">🎉</div>
                    <h1 style="font-size: 32px; margin-bottom: 16px; color: var(--success);">
                        Заказ успешно оформлен!
                    </h1>
                    <p style="font-size: 24px; margin-bottom: 8px;">
                        Номер заказа: <strong style="color: var(--primary);">#{order_id}</strong>
                    </p>
                    <p style="color: var(--gray); margin-bottom: 32px;">
                        Мы отправили подтверждение на <strong>{email}</strong>
                    </p>

                    <div style="background: var(--light); border-radius: var(--radius); padding: 24px; text-align: left; margin-bottom: 32px;">
                        <h3 style="margin-bottom: 16px;">📋 Детали заказа</h3>
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e2e8f0;">
                            <span style="color: var(--gray);">Сумма заказа</span>
                            <span style="font-weight: 600;">{format_price(total)}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e2e8f0;">
                            <span style="color: var(--gray);">Получатель</span>
                            <span>{name}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                            <span style="color: var(--gray);">Адрес</span>
                            <span style="text-align: right; max-width: 200px;">{address}</span>
                        </div>
                    </div>

                    <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
                        <a href="/orders" class="btn btn-primary btn-lg">
                            📦 Мои заказы
                        </a>
                        <a href="/catalog" class="btn btn-secondary btn-lg">
                            🛒 Продолжить покупки
                        </a>
                    </div>
                </div>
            </div>
        </div>
        """

    return HTMLResponse(base_template(content, "Заказ оформлен", request, user, 0, 0))


# ═══════════════════════════════════════════════════════════════
# ЗАКАЗЫ ПОЛЬЗОВАТЕЛЯ
# ═══════════════════════════════════════════════════════════════

@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login?next=/orders", status_code=302)

    user_id = get_user_id(request)
    cart_count = await get_cart_count(user_id)
    favorites_count = await get_favorites_count(user_id)
    orders = await get_user_orders(user_id)

    if not orders:
        content = """
            <div class="page-header">
                <h1 class="page-title">📦 Мои заказы</h1>
            </div>
            <div class="card">
                <div class="empty-state">
                    <div class="icon">📦</div>
                    <h3>У вас пока нет заказов</h3>
                    <p>Самое время сделать первый!</p>
                    <a href="/catalog" class="btn btn-primary">Перейти в каталог</a>
                </div>
            </div>
            """
        return HTMLResponse(base_template(content, "Мои заказы", request, user, cart_count, favorites_count))

    status_labels = {
        'pending': ('⏳ Ожидает оплаты', 'status-pending'),
        'processing': ('🔄 В обработке', 'status-processing'),
        'shipped': ('🚚 Отправлен', 'status-shipped'),
        'delivered': ('✅ Доставлен', 'status-delivered'),
        'cancelled': ('❌ Отменён', 'status-cancelled'),
    }

    orders_html = ""
    for order in orders:
        status_text, status_class = status_labels.get(order['status'], ('❓ Неизвестно', ''))

        items_preview = "".join(f"""
                <div class="order-item-mini">
                    {item.get('image', '📦')} {item['name'][:20]}{'...' if len(item['name']) > 20 else ''} × {item['quantity']}
                </div>
            """ for item in order['items'][:3])

        if len(order['items']) > 3:
            items_preview += f'<div class="order-item-mini">+{len(order["items"]) - 3} ещё</div>'

        orders_html += f"""
            <div class="order-card">
                <div class="order-header">
                    <div class="order-number">Заказ #{order['id']}</div>
                    <div class="order-status {status_class}">{status_text}</div>
                </div>
                <div class="order-body">
                    <div class="order-items">{items_preview}</div>
                    <div class="order-footer">
                        <span style="color: var(--gray);">
                            {order['created_at'][:10] if order['created_at'] else ''}
                        </span>
                        <span style="font-size: 20px; font-weight: 700;">
                            {format_price(order['total'])}
                        </span>
                    </div>
                </div>
            </div>
            """

    content = f"""
        <div class="page-header">
            <h1 class="page-title">📦 Мои заказы</h1>
            <p class="page-subtitle">{len(orders)} заказов</p>
        </div>

        {orders_html}
        """

    return HTMLResponse(base_template(content, "Мои заказы", request, user, cart_count, favorites_count))


# ═══════════════════════════════════════════════════════════════
# ПРОФИЛЬ
# ═══════════════════════════════════════════════════════════════

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login?next=/profile", status_code=302)

    user_id = get_user_id(request)
    cart_count = await get_cart_count(user_id)
    favorites_count = await get_favorites_count(user_id)
    orders = await get_user_orders(user_id)

    content = f"""
        <div class="page-header">
            <h1 class="page-title">👤 Мой профиль</h1>
        </div>

        <div class="grid grid-2">
            <div class="card">
                <div class="card-header">📋 Личные данные</div>
                <div class="card-body">
                    <p><strong>Имя:</strong> {user['name']}</p>
                    <p><strong>Email:</strong> {user['email']}</p>
                    <p><strong>Телефон:</strong> {user.get('phone') or 'Не указан'}</p>
                    <p><strong>Адрес:</strong> {user.get('address') or 'Не указан'}</p>

                    <div style="margin-top: 20px;">
                        <a href="/logout" class="btn btn-secondary">🚪 Выйти</a>
                        {f'<a href="/admin" class="btn btn-primary" style="margin-left: 8px;">⚙️ Админ-панель</a>' if user.get('is_admin') else ''}
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">📊 Статистика</div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                        <div style="text-align: center; padding: 20px; background: var(--light); border-radius: 8px;">
                            <div style="font-size: 32px; font-weight: 700; color: var(--primary);">{len(orders)}</div>
                            <div style="color: var(--gray);">Заказов</div>
                        </div>
                        <div style="text-align: center; padding: 20px; background: var(--light); border-radius: 8px;">
                            <div style="font-size: 32px; font-weight: 700; color: var(--primary);">{favorites_count}</div>
                            <div style="color: var(--gray);">В избранном</div>
                        </div>
                    </div>

                    <div style="margin-top: 20px;">
                        <a href="/orders" class="btn btn-primary">📦 Мои заказы</a>
                        <a href="/favorites" class="btn btn-secondary" style="margin-left: 8px;">❤️ Избранное</a>
                    </div>
                </div>
            </div>
        </div>
        """

    return HTMLResponse(base_template(content, "Профиль", request, user, cart_count, favorites_count))


# ═══════════════════════════════════════════════════════════════
# АВТОРИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/"):
    user = await get_current_user(request)
    if user:
        return RedirectResponse("/", status_code=302)

    content = f"""
        <div class="auth-container">
            <div class="auth-card">
                <h1 class="auth-title">👋 Вход</h1>
                <p class="auth-subtitle">Войдите в свой аккаунт</p>

                <form method="post" action="/login">
                    <input type="hidden" name="next" value="{next}">

                    <div class="form-group">
                        <label class="form-label">Email</label>
                        <input type="email" name="email" class="form-control" required 
                               placeholder="email@example.com">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Пароль</label>
                        <input type="password" name="password" class="form-control" required 
                               placeholder="Введите пароль">
                    </div>

                    <button type="submit" class="btn btn-primary btn-lg btn-block">
                        Войти
                    </button>
                </form>

                <div class="auth-footer">
                    Нет аккаунта? <a href="/register">Зарегистрироваться</a>
                </div>

                <div style="margin-top: 20px; padding: 16px; background: var(--light); border-radius: 8px; font-size: 13px;">
                    <strong>Тестовые аккаунты:</strong><br>
                    👤 user@test.com / 123456<br>
                    👑 admin@shop.com / admin123
                </div>
            </div>
        </div>
        """

    return HTMLResponse(base_template(content, "Вход", request, None, 0, 0))


@app.post("/login", response_class=HTMLResponse)
async def login_submit(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        next: str = Form("/")
):
    user = await get_user_by_email(email)

    if not user or user['password'] != password:
        content = """
            <div class="auth-container">
                <div class="auth-card">
                    <div class="alert alert-error">
                        ❌ Неверный email или пароль
                    </div>
                    <a href="/login" class="btn btn-primary btn-block">Попробовать снова</a>
                </div>
            </div>
            """
        return HTMLResponse(base_template(content, "Ошибка входа", request, None, 0, 0))

    request.session["user_id"] = user["id"]
    return RedirectResponse(next, status_code=302)


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse("/", status_code=302)

    content = """
        <div class="auth-container">
            <div class="auth-card">
                <h1 class="auth-title">🎉 Регистрация</h1>
                <p class="auth-subtitle">Создайте новый аккаунт</p>

                <form method="post" action="/register">
                    <div class="form-group">
                        <label class="form-label">Имя</label>
                        <input type="text" name="name" class="form-control" required 
                               placeholder="Иван Иванов">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Email</label>
                        <input type="email" name="email" class="form-control" required 
                               placeholder="email@example.com">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Пароль</label>
                        <input type="password" name="password" class="form-control" required 
                               placeholder="Минимум 6 символов" minlength="6">
                    </div>

                    <button type="submit" class="btn btn-primary btn-lg btn-block">
                        Зарегистрироваться
                    </button>
                </form>

                <div class="auth-footer">
                    Уже есть аккаунт? <a href="/login">Войти</a>
                </div>
            </div>
        </div>
        """

    return HTMLResponse(base_template(content, "Регистрация", request, None, 0, 0))


@app.post("/register", response_class=HTMLResponse)
async def register_submit(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...)
):
    existing = await get_user_by_email(email)
    if existing:
        content = """
            <div class="auth-container">
                <div class="auth-card">
                    <div class="alert alert-error">
                        ❌ Пользователь с таким email уже существует
                    </div>
                    <a href="/register" class="btn btn-primary btn-block">Попробовать снова</a>
                </div>
            </div>
            """
        return HTMLResponse(base_template(content, "Ошибка", request, None, 0, 0))

    user_id = await create_user(email, password, name)
    request.session["user_id"] = user_id

    return RedirectResponse("/", status_code=302)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)


# ═══════════════════════════════════════════════════════════════
# API ДЛЯ AJAX
# ═══════════════════════════════════════════════════════════════

@app.post("/api/cart/add")
async def api_add_to_cart(request: Request):
    user_id = get_user_id(request)
    if not user_id:
        return JSONResponse({"success": False, "redirect": "/login"})

    data = await request.json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    await add_to_cart(user_id, product_id, quantity)
    cart_count = await get_cart_count(user_id)

    return JSONResponse({"success": True, "cart_count": cart_count})


@app.post("/api/cart/update")
async def api_update_cart(request: Request):
    user_id = get_user_id(request)
    if not user_id:
        return JSONResponse({"success": False})

    data = await request.json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    await update_cart_item(user_id, product_id, quantity)

    return JSONResponse({"success": True})


@app.post("/api/cart/remove")
async def api_remove_from_cart(request: Request):
    user_id = get_user_id(request)
    if not user_id:
        return JSONResponse({"success": False})

    data = await request.json()
    product_id = data.get("product_id")

    await remove_from_cart(user_id, product_id)

    return JSONResponse({"success": True})


@app.post("/api/favorites/toggle")
async def api_toggle_favorite(request: Request):
    user_id = get_user_id(request)
    if not user_id:
        return JSONResponse({"success": False, "redirect": "/login"})

    data = await request.json()
    product_id = data.get("product_id")

    added = await toggle_favorite(user_id, product_id)
    favorites_count = await get_favorites_count(user_id)

    return JSONResponse({
        "success": True,
        "added": added,
        "favorites_count": favorites_count
    })


# ═══════════════════════════════════════════════════════════════
# АДМИН-ПАНЕЛЬ
# ═══════════════════════════════════════════════════════════════

async def require_admin(request: Request):
    user = await get_current_user(request)
    if not user or not user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return user


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user = await get_current_user(request)
    if not user or not user.get('is_admin'):
        return RedirectResponse("/login", status_code=302)

    stats = await get_stats()

    content = f"""
        <div class="page-header">
            <h1 class="page-title">⚙️ Админ-панель</h1>
        </div>

        <div class="admin-nav">
            <a href="/admin" class="active">📊 Дашборд</a>
            <a href="/admin/orders">📦 Заказы</a>
            <a href="/admin/products">🏷️ Товары</a>
            <a href="/admin/users">👥 Пользователи</a>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">💰</div>
                <div class="value">{format_price(stats['total_revenue'])}</div>
                <div class="label">Общая выручка</div>
            </div>
            <div class="stat-card">
                <div class="icon">📦</div>
                <div class="value">{stats['total_orders']}</div>
                <div class="label">Всего заказов</div>
            </div>
            <div class="stat-card">
                <div class="icon">👥</div>
                <div class="value">{stats['total_users']}</div>
                <div class="label">Пользователей</div>
            </div>
            <div class="stat-card">
                <div class="icon">🏷️</div>
                <div class="value">{stats['total_products']}</div>
                <div class="label">Товаров</div>
            </div>
        </div>

        <div class="grid grid-2">
            <div class="card">
                <div class="card-header">📊 Заказы по статусам</div>
                <div class="card-body">
                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span>⏳ Ожидают оплаты</span>
                            <strong>{stats['orders_by_status'].get('pending', 0)}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>🔄 В обработке</span>
                            <strong>{stats['orders_by_status'].get('processing', 0)}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>🚚 Отправлены</span>
                            <strong>{stats['orders_by_status'].get('shipped', 0)}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>✅ Доставлены</span>
                            <strong>{stats['orders_by_status'].get('delivered', 0)}</strong>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">⚠️ Требует внимания</div>
                <div class="card-body">
                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        <div style="display: flex; justify-content: space-between; color: var(--danger);">
                            <span>Мало на складе</span>
                            <strong>{stats['low_stock']} товаров</strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

    return HTMLResponse(base_template(content, "Админ-панель", request, user, 0, 0))


@app.get("/admin/orders", response_class=HTMLResponse)
async def admin_orders(request: Request):
    user = await get_current_user(request)
    if not user or not user.get('is_admin'):
        return RedirectResponse("/login", status_code=302)

    orders = await get_all_orders()

    status_labels = {
        'pending': ('⏳ Ожидает', 'status-pending'),
        'processing': ('🔄 Обработка', 'status-processing'),
        'shipped': ('🚚 Отправлен', 'status-shipped'),
        'delivered': ('✅ Доставлен', 'status-delivered'),
        'cancelled': ('❌ Отменён', 'status-cancelled'),
    }

    rows_html = ""
    for order in orders:
        status_text, status_class = status_labels.get(order['status'], ('❓', ''))
        rows_html += f"""
            <tr>
                <td><strong>#{order['id']}</strong></td>
                <td>{order['user_name']}<br><small style="color: var(--gray);">{order['user_email']}</small></td>
                <td>{format_price(order['total'])}</td>
                <td><span class="order-status {status_class}">{status_text}</span></td>
                <td>{order['created_at'][:16] if order['created_at'] else ''}</td>
                <td>
                    <select class="form-control" style="padding: 8px;" onchange="updateOrderStatus({order['id']}, this.value)">
                        <option value="pending" {'selected' if order['status'] == 'pending' else ''}>⏳ Ожидает</option>
                        <option value="processing" {'selected' if order['status'] == 'processing' else ''}>🔄 Обработка</option>
                        <option value="shipped" {'selected' if order['status'] == 'shipped' else ''}>🚚 Отправлен</option>
                        <option value="delivered" {'selected' if order['status'] == 'delivered' else ''}>✅ Доставлен</option>
                        <option value="cancelled" {'selected' if order['status'] == 'cancelled' else ''}>❌ Отменён</option>
                    </select>
                </td>
            </tr>
            """

    content = f"""
        <div class="page-header">
            <h1 class="page-title">📦 Управление заказами</h1>
        </div>

        <div class="admin-nav">
            <a href="/admin">📊 Дашборд</a>
            <a href="/admin/orders" class="active">📦 Заказы</a>
            <a href="/admin/products">🏷️ Товары</a>
            <a href="/admin/users">👥 Пользователи</a>
        </div>

        <div class="card">
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Покупатель</th>
                            <th>Сумма</th>
                            <th>Статус</th>
                            <th>Дата</th>
                            <th>Действие</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html if rows_html else '<tr><td colspan="6" style="text-align: center; padding: 40px;">Заказов пока нет</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            async function updateOrderStatus(orderId, status) {{
                await fetch('/api/admin/orders/' + orderId + '/status', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ status: status }})
                }});
                showToast('✅ Статус обновлён');
            }}
        </script>
        """

    return HTMLResponse(base_template(content, "Заказы", request, user, 0, 0))


@app.post("/api/admin/orders/{order_id}/status")
async def api_update_order_status(request: Request, order_id: int):
    user = await get_current_user(request)
    if not user or not user.get('is_admin'):
        return JSONResponse({"success": False}, status_code=403)

    data = await request.json()
    status = data.get("status")

    await update_order_status(order_id, status)

    return JSONResponse({"success": True})


@app.get("/admin/products", response_class=HTMLResponse)
async def admin_products(request: Request):
    user = await get_current_user(request)
    if not user or not user.get('is_admin'):
        return RedirectResponse("/login", status_code=302)

    products = await get_all_products_admin()

    rows_html = ""
    for p in products:
        stock_color = "var(--success)" if p['stock'] > 10 else ("var(--danger)" if p['stock'] < 5 else "var(--warning)")
        rows_html += f"""
            <tr>
                <td>{p['id']}</td>
                <td>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 24px;">{p.get('image', '📦')}</span>
                        <div>
                            <strong>{p['name']}</strong>
                            <div style="font-size: 12px; color: var(--gray);">{p.get('category_name', '')}</div>
                        </div>
                    </div>
                </td>
                <td>{format_price(p['price'])}</td>
                <td style="color: {stock_color}; font-weight: 600;">{p['stock']}</td>
                <td>{'✅' if p['is_active'] else '❌'}</td>
                <td>{'⭐' if p['is_featured'] else ''}</td>
            </tr>
            """

    content = f"""
        <div class="page-header">
            <h1 class="page-title">🏷️ Управление товарами</h1>
        </div>

        <div class="admin-nav">
            <a href="/admin">📊 Дашборд</a>
            <a href="/admin/orders">📦 Заказы</a>
            <a href="/admin/products" class="active">🏷️ Товары</a>
            <a href="/admin/users">👥 Пользователи</a>
        </div>

        <div class="card">
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Товар</th>
                            <th>Цена</th>
                            <th>Остаток</th>
                            <th>Активен</th>
                            <th>Хит</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>
        """

    return HTMLResponse(base_template(content, "Товары", request, user, 0, 0))


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    user = await get_current_user(request)
    if not user or not user.get('is_admin'):
        return RedirectResponse("/login", status_code=302)

    users = await get_all_users()

    rows_html = ""
    for u in users:
        rows_html += f"""
            <tr>
                <td>{u['id']}</td>
                <td>
                    <strong>{u['name']}</strong>
                    {'<span style="background: var(--primary); color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px;">ADMIN</span>' if u['is_admin'] else ''}
                </td>
                <td>{u['email']}</td>
                <td>{u.get('phone') or '—'}</td>
                <td>{u['created_at'][:10] if u['created_at'] else ''}</td>
            </tr>
            """

    content = f"""
        <div class="page-header">
            <h1 class="page-title">👥 Пользователи</h1>
        </div>

        <div class="admin-nav">
            <a href="/admin">📊 Дашборд</a>
            <a href="/admin/orders">📦 Заказы</a>
            <a href="/admin/products">🏷️ Товары</a>
            <a href="/admin/users" class="active">👥 Пользователи</a>
        </div>

        <div class="card">
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Имя</th>
                            <th>Email</th>
                            <th>Телефон</th>
                            <th>Регистрация</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>
        """

    return HTMLResponse(base_template(content, "Пользователи", request, user, 0, 0))


# ═══════════════════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
