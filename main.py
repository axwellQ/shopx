# main.py
"""
🛒 Маркетплейс - Полноценный интернет-магазин
FastAPI + SQLite + Современный UI
"""

from fastapi import FastAPI, Request, Form, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional
import uvicorn
from database import *

app = FastAPI(title="🛒 ShopMax - Маркетплейс")
app.add_middleware(SessionMiddleware, secret_key="supersecretkey123shopmax")


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def get_user_id(request: Request) -> Optional[int]:
    return request.session.get("user_id")


def require_auth(request: Request) -> int:
    user_id = get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    return user_id


async def get_current_user(request: Request) -> Optional[dict]:
    user_id = get_user_id(request)
    if user_id:
        return await get_user_by_id(user_id)
    return None


def format_price(price: float) -> str:
    return f"{price:,.0f}".replace(",", " ") + " ₽"


# ═══════════════════════════════════════════════════════════════
# HTML ШАБЛОНЫ
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
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #f59e0b;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --dark: #1e293b;
            --gray: #64748b;
            --light: #f1f5f9;
            --white: #ffffff;
            --shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
            --radius: 12px;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--light);
            color: var(--dark);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        /* Header */
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
        
        .header-main {{
            padding: 16px 0;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .header-content {{
            display: flex;
            align-items: center;
            gap: 30px;
        }}
        
        .logo {{
            font-size: 28px;
            font-weight: 800;
            color: var(--primary);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
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
            transition: all 0.3s;
        }}
        
        .search-box input:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(99,102,241,0.1);
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
            font-size: 18px;
            transition: background 0.3s;
        }}
        
        .search-box button:hover {{
            background: var(--primary-dark);
        }}
        
        .header-actions {{
            display: flex;
            align-items: center;
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
        
        .header-btn .icon {{
            font-size: 24px;
            margin-bottom: 2px;
        }}
        
        .badge {{
            position: absolute;
            top: 4px;
            right: 8px;
            background: var(--danger);
            color: white;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 50px;
            min-width: 18px;
            text-align: center;
        }}
        
        /* Navigation */
        .nav {{
            background: var(--white);
            border-top: 1px solid var(--light);
        }}
        
        .nav-list {{
            display: flex;
            list-style: none;
            gap: 5px;
            padding: 12px 0;
            overflow-x: auto;
        }}
        
        .nav-list a {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 18px;
            text-decoration: none;
            color: var(--dark);
            font-weight: 500;
            border-radius: 50px;
            white-space: nowrap;
            transition: all 0.3s;
        }}
        
        .nav-list a:hover, .nav-list a.active {{
            background: var(--primary);
            color: white;
        }}
        
        /* Main content */
        main {{
            padding: 30px 0;
            min-height: calc(100vh - 300px);
        }}
        
        /* Cards */
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
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .card-body {{
            padding: 24px;
        }}
        
        /* Product Grid */
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
            position: relative;
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
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow);
            transition: all 0.3s;
        }}
        
        .product-favorite:hover {{
            transform: scale(1.1);
        }}
        
        .product-favorite.active {{
            background: var(--danger);
            color: white;
        }}
        
        .product-info {{
            padding: 16px;
        }}
        
        .product-category {{
            font-size: 12px;
            color: var(--primary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        .product-title {{
            font-size: 15px;
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.4;
        }}
        
        .product-title a {{
            color: inherit;
            text-decoration: none;
        }}
        
        .product-title a:hover {{
            color: var(--primary);
        }}
        
        .product-rating {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 13px;
            color: var(--gray);
            margin-bottom: 12px;
        }}
        
        .product-rating .stars {{
            color: #fbbf24;
        }}
        
        .product-price {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }}
        
        .price-current {{
            font-size: 20px;
            font-weight: 700;
            color: var(--dark);
        }}
        
        .price-old {{
            font-size: 14px;
            color: var(--gray);
            text-decoration: line-through;
        }}
        
        .price-discount {{
            background: #fef3c7;
            color: #92400e;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .product-actions {{
            display: flex;
            gap: 8px;
        }}
        
        /* Buttons */
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
            transition: all 0.3s;
            border: none;
            text-decoration: none;
        }}
        
        .btn-primary {{
            background: var(--primary);
            color: white;
        }}
        
        .btn-primary:hover {{
            background: var(--primary-dark);
            transform: translateY(-2px);
        }}
        
        .btn-secondary {{
            background: var(--light);
            color: var(--dark);
        }}
        
        .btn-secondary:hover {{
            background: #e2e8f0;
        }}
        
        .btn-success {{
            background: var(--success);
            color: white;
        }}
        
        .btn-success:hover {{
            background: #059669;
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
        
        .btn-outline:hover {{
            background: var(--primary);
            color: white;
        }}
        
        .btn-block {{
            width: 100%;
        }}
        
        .btn-sm {{
            padding: 8px 16px;
            font-size: 13px;
        }}
        
        .btn-lg {{
            padding: 16px 32px;
            font-size: 16px;
        }}
        
        .btn-icon {{
            width: 40px;
            height: 40px;
            padding: 0;
            border-radius: 50%;
        }}
        
        /* Forms */
        .form-group {{
            margin-bottom: 20px;
        }}
        
        .form-label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--dark);
        }}
        
        .form-control {{
            width: 100%;
            padding: 14px 16px;
            border: 2px solid var(--light);
            border-radius: var(--radius);
            font-size: 15px;
            transition: all 0.3s;
        }}
        
        .form-control:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(99,102,241,0.1);
        }}
        
        textarea.form-control {{
            resize: vertical;
            min-height: 100px;
        }}
        
        select.form-control {{
            cursor: pointer;
        }}
        
        /* Alerts */
        .alert {{
            padding: 16px 20px;
            border-radius: var(--radius);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .alert-success {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .alert-error {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .alert-warning {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        .alert-info {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        /* Grid layouts */
        .grid {{
            display: grid;
            gap: 24px;
        }}
        
        .grid-2 {{
            grid-template-columns: repeat(2, 1fr);
        }}
        
        .grid-3 {{
            grid-template-columns: repeat(3, 1fr);
        }}
        
        .grid-4 {{
            grid-template-columns: repeat(4, 1fr);
        }}
        
        .sidebar-layout {{
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 30px;
        }}
        
        /* Page title */
        .page-header {{
            margin-bottom: 30px;
        }}
        
        .page-title {{
            font-size: 32px;
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 8px;
        }}
        
        .page-subtitle {{
            color: var(--gray);
            font-size: 16px;
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
        
        /* Hero section */
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
            line-height: 1.2;
        }}
        
        .hero-content p {{
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 24px;
            max-width: 500px;
        }}
        
        .hero-image {{
            font-size: 150px;
        }}
        
        /* Section */
        .section {{
            margin-bottom: 50px;
        }}
        
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
        
        /* Category cards */
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
        
        .category-card .name {{
            font-weight: 600;
            margin-bottom: 4px;
        }}
        
        .category-card .count {{
            font-size: 13px;
            color: var(--gray);
        }}
        
        /* Filters sidebar */
        .filters {{
            background: var(--white);
            border-radius: var(--radius);
            padding: 24px;
            box-shadow: var(--shadow);
        }}
        
        .filter-section {{
            margin-bottom: 24px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--light);
        }}
        
        .filter-section:last-child {{
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
        }}
        
        .filter-title {{
            font-weight: 600;
            margin-bottom: 16px;
            font-size: 15px;
        }}
        
        .filter-options {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .filter-option {{
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
        }}
        
        .filter-option input {{
            width: 18px;
            height: 18px;
            cursor: pointer;
        }}
        
        .price-inputs {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}
        
        .price-inputs input {{
            width: 100%;
            padding: 10px 12px;
            border: 2px solid var(--light);
            border-radius: 8px;
        }}
        
        /* Cart */
        .cart-item {{
            display: flex;
            gap: 20px;
            padding: 20px 0;
            border-bottom: 1px solid var(--light);
        }}
        
        .cart-item:last-child {{
            border-bottom: none;
        }}
        
        .cart-item-image {{
            width: 100px;
            height: 100px;
            background: var(--light);
            border-radius: var(--radius);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            flex-shrink: 0;
        }}
        
        .cart-item-info {{
            flex: 1;
        }}
        
        .cart-item-title {{
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        .cart-item-title a {{
            color: var(--dark);
            text-decoration: none;
        }}
        
        .cart-item-title a:hover {{
            color: var(--primary);
        }}
        
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
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s;
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
            top: 120px;
        }}
        
        .summary-row {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid var(--light);
        }}
        
        .summary-row:last-of-type {{
            border-bottom: none;
        }}
        
        .summary-total {{
            font-size: 24px;
            font-weight: 700;
            color: var(--primary);
            padding-top: 16px;
            margin-top: 8px;
            border-top: 2px solid var(--primary);
        }}
        
        /* Orders */
        .order-card {{
            background: var(--white);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            margin-bottom: 20px;
            overflow: hidden;
        }}
        
        .order-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 24px;
            background: var(--light);
        }}
        
        .order-number {{
            font-weight: 700;
            font-size: 18px;
        }}
        
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
        
        .order-body {{
            padding: 20px 24px;
        }}
        
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
        
        /* Product detail */
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
        
        .product-detail-rating {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 24px;
            font-size: 15px;
        }}
        
        .product-detail-description {{
            color: var(--gray);
            line-height: 1.8;
            margin-bottom: 30px;
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
        
        /* Auth pages */
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
        
        /* Admin */
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
            transition: all 0.3s;
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
        
        .stat-card .icon {{
            font-size: 40px;
            margin-bottom: 12px;
        }}
        
        .stat-card .value {{
            font-size: 32px;
            font-weight: 800;
            color: var(--dark);
        }}
        
        .stat-card .label {{
            color: var(--gray);
            font-size: 14px;
        }}
        
        /* Table */
        .table-container {{
            overflow-x: auto;
        }}
        
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
            letter-spacing: 0.5px;
        }}
        
        .table tr:hover {{
            background: var(--light);
        }}
        
        /* Empty state */
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
        
        /* Toast notifications */
        .toast {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--dark);
            color: white;
            padding: 16px 24px;
            border-radius: var(--radius);
            box-shadow: var(--shadow-lg);
            display: flex;
            align-items: center;
            gap: 12px;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        }}
        
        @keyframes slideIn {{
            from {{
                transform: translateX(100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        
        .toast.success {{ background: var(--success); }}
        .toast.error {{ background: var(--danger); }}
        
        /* Checkout */
        .checkout-layout {{
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 30px;
        }}
        
        /* Footer */
        .footer {{
            background: var(--dark);
            color: white;
            padding: 60px 0 30px;
            margin-top: 60px;
        }}
        
        .footer-grid {{
            display: grid;
            grid-template-columns: 2fr repeat(3, 1fr);
            gap: 40px;
            margin-bottom: 40px;
        }}
        
        .footer-brand {{
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 16px;
        }}
        
        .footer-text {{
            color: #94a3b8;
            font-size: 14px;
            line-height: 1.8;
        }}
        
        .footer-title {{
            font-weight: 600;
            margin-bottom: 20px;
        }}
        
        .footer-links {{
            list-style: none;
        }}
        
        .footer-links li {{
            margin-bottom: 12px;
        }}
        
        .footer-links a {{
            color: #94a3b8;
            text-decoration: none;
            font-size: 14px;
            transition: color 0.3s;
        }}
        
        .footer-links a:hover {{
            color: white;
        }}
        
        .footer-bottom {{
            border-top: 1px solid #334155;
            padding-top: 30px;
            text-align: center;
            color: #64748b;
            font-size: 14px;
        }}
        
        /* Responsive */
        @media (max-width: 1024px) {{
            .sidebar-layout {{
                grid-template-columns: 1fr;
            }}
            
            .product-detail {{
                grid-template-columns: 1fr;
            }}
            
            .checkout-layout {{
                grid-template-columns: 1fr;
            }}
            
            .footer-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        @media (max-width: 768px) {{
            .header-content {{
                flex-wrap: wrap;
            }}
            
            .search-box {{
                order: 3;
                flex: 1 1 100%;
                max-width: 100%;
                margin-top: 16px;
            }}
            
            .hero {{
                flex-direction: column;
                text-align: center;
                padding: 40px 20px;
            }}
            
            .hero-content h1 {{
                font-size: 28px;
            }}
            
            .hero-image {{
                font-size: 100px;
            }}
            
            .grid-2, .grid-3, .grid-4 {{
                grid-template-columns: 1fr;
            }}
            
            .footer-grid {{
                grid-template-columns: 1fr;
            }}
            
            .cart-item {{
                flex-direction: column;
            }}
            
            .cart-item-image {{
                width: 100%;
                height: 150px;
            }}
        }}
        
        /* Loading animation */
        .loading {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        /* Animations */
        .fade-in {{
            animation: fadeIn 0.5s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-top">
            <div class="container" style="display: flex; justify-content: space-between;">
                <span>📞 8-800-555-35-35 (бесплатно)</span>
                <span>🚚 Бесплатная доставка от 5000 ₽</span>
            </div>
        </div>
        <div class="header-main">
            <div class="container">
                <div class="header-content">
                    <a href="/" class="logo">🛒 ShopMax</a>
                    
                    <form class="search-box" action="/search" method="get">
                        <input type="text" name="q" placeholder="Поиск товаров..." autocomplete="off">
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
            <div class="footer-grid">
                <div>
                    <div class="footer-brand">🛒 ShopMax</div>
                    <p class="footer-text">
                        Ваш надежный интернет-магазин с широким ассортиментом товаров
                        по лучшим ценам. Быстрая доставка по всей России!
                    </p>
                </div>
                <div>
                    <div class="footer-title">Покупателям</div>
                    <ul class="footer-links">
                        <li><a href="/catalog">Каталог</a></li>
                        <li><a href="#">Доставка</a></li>
                        <li><a href="#">Оплата</a></li>
                        <li><a href="#">Возврат</a></li>
                    </ul>
                </div>
                <div>
                    <div class="footer-title">Компания</div>
                    <ul class="footer-links">
                        <li><a href="#">О нас</a></li>
                        <li><a href="#">Контакты</a></li>
                        <li><a href="#">Вакансии</a></li>
                        <li><a href="#">Блог</a></li>
                    </ul>
                </div>
                <div>
                    <div class="footer-title">Контакты</div>
                    <ul class="footer-links">
                        <li>📞 8-800-555-35-35</li>
                        <li>✉️ info@shopmax.ru</li>
                        <li>📍 Москва, ул. Примерная, 1</li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                © 2024 ShopMax. Все права защищены.
            </div>
        </div>
    </footer>
    
    <script>
        // Toast notification
        function showToast(message, type = 'success') {{
            const toast = document.createElement('div');
            toast.className = 'toast ' + type;
            toast.innerHTML = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {{
                toast.style.animation = 'slideIn 0.3s ease reverse';
                setTimeout(() => toast.remove(), 300);
            }}, 3000);
        }}
        
        // Add to cart AJAX
        async function addToCart(productId) {{
            try {{
                const response = await fetch('/api/cart/add', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ product_id: productId, quantity: 1 }})
                }});
                const data = await response.json();
                
                if (data.success) {{
                    showToast('✅ Товар добавлен в корзину');
                    updateCartBadge(data.cart_count);
                }} else {{
                    if (data.redirect) {{
                        window.location.href = data.redirect;
                    }} else {{
                        showToast('❌ ' + data.error, 'error');
                    }}
                }}
            }} catch (e) {{
                showToast('❌ Ошибка', 'error');
            }}
        }}
        
        // Toggle favorite AJAX
        async function toggleFavorite(productId, btn) {{
            try {{
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
                        showToast('💔 Удалено из избранного');
                    }}
                    updateFavoritesBadge(data.favorites_count);
                }} else if (data.redirect) {{
                    window.location.href = data.redirect;
                }}
            }} catch (e) {{
                showToast('❌ Ошибка', 'error');
            }}
        }}
        
        function updateCartBadge(count) {{
            const badges = document.querySelectorAll('.header-btn .badge');
            badges.forEach((badge, i) => {{
                if (i === 1) {{ // Cart badge
                    if (count > 0) {{
                        badge.textContent = count;
                        badge.style.display = 'block';
                    }} else {{
                        badge.style.display = 'none';
                    }}
                }}
            }});
        }}
        
        function updateFavoritesBadge(count) {{
            const badges = document.querySelectorAll('.header-btn .badge');
            badges.forEach((badge, i) => {{
                if (i === 0) {{ // Favorites badge
                    if (count > 0) {{
                        badge.textContent = count;
                        badge.style.display = 'block';
                    }} else {{
                        badge.style.display = 'none';
                    }}
                }}
            }});
        }}
        
        // Update cart quantity
        async function updateQuantity(productId, delta) {{
            const valueEl = document.getElementById('qty-' + productId);
            let newQty = parseInt(valueEl.textContent) + delta;
            if (newQty < 1) newQty = 1;
            
            try {{
                const response = await fetch('/api/cart/update', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ product_id: productId, quantity: newQty }})
                }});
                const data = await response.json();
                
                if (data.success) {{
                    valueEl.textContent = newQty;
                    location.reload();
                }}
            }} catch (e) {{
                showToast('❌ Ошибка', 'error');
            }}
        }}
        
        // Remove from cart
        async function removeFromCart(productId) {{
            if (!confirm('Удалить товар из корзины?')) return;
            
            try {{
                const response = await fetch('/api/cart/remove', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ product_id: productId }})
                }});
                const data = await response.json();
                
                if (data.success) {{
                    location.reload();
                }}
            }} catch (e) {{
                showToast('❌ Ошибка', 'error');
            }}
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

    # Получаем избранные товары пользователя
    user_favorites = []
    if user_id:
        favs = await get_favorites(user_id)
        user_favorites = [f['product_id'] for f in favs]

    categories_html = "".join(f"""
        <a href="/catalog/{c['slug']}" class="category-card">
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
        <div class="product-card fade-in">
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
                    <a href="/product/{p['slug']}">{p['name']}</a>
                </h3>
                <div class="product-rating">
                    <span class="stars">{stars}</span>
                    <span>{p.get('rating', 0)}</span>
                    <span>({p.get('reviews_count', 0)} отзывов)</span>
                </div>
                <div class="product-price">
                    <span class="price-current">{format_price(p['price'])}</span>
                    {f'<span class="price-old">{format_price(p["old_price"])}</span>' if p.get('old_price') else ''}
                </div>
                <div class="product-actions">
                    <button class="btn btn-primary btn-block" onclick="addToCart({p['id']})">
                        🛒 В корзину
                    </button>
                </div>
            </div>
        </div>
        """

    products_html = "".join(product_card(p) for p in featured)

    content = f"""
    <div class="hero">
        <div class="hero-content">
            <h1>Летняя распродажа!</h1>
            <p>Скидки до 50% на электронику, одежду и товары для дома. Успейте купить по выгодным ценам!</p>
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
            <a href="/catalog?sort=popular" class="btn btn-secondary">Все товары →</a>
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
@app.get("/catalog/{category_slug}", response_class=HTMLResponse)
async def catalog(
        request: Request,
        category_slug: str = None,
        sort: str = "popular",
        min_price: float = None,
        max_price: float = None,
        q: str = None
):
    user = await get_current_user(request)
    user_id = get_user_id(request)

    cart_count = await get_cart_count(user_id) if user_id else 0
    favorites_count_header = await get_favorites_count(user_id) if user_id else 0

    categories = await get_categories()
    category = None
    category_id = None

    if category_slug:
        category = await get_category_by_slug(category_slug)
        if category:
            category_id = category['id']

    products = await get_products(
        category_id=category_id,
        search=q,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )

    user_favorites = []
    if user_id:
        favs = await get_favorites(user_id)
        user_favorites = [f['product_id'] for f in favs]

    # Sidebar с категориями
    categories_html = "".join(f"""
        <a href="/catalog/{c['slug']}" style="display: flex; justify-content: space-between; padding: 10px 0; text-decoration: none; color: {'var(--primary); font-weight: 600' if category and category['id'] == c['id'] else 'var(--dark)'};">
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
        <div class="product-card fade-in">
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
                    <a href="/product/{p['slug']}">{p['name']}</a>
                </h3>
                <div class="product-rating">
                    <span class="stars">{stars}</span>
                    <span>{p.get('rating', 0)}</span>
                    <span>({p.get('reviews_count', 0)})</span>
                </div>
                <div class="product-price">
                    <span class="price-current">{format_price(p['price'])}</span>
                    {f'<span class="price-old">{format_price(p["old_price"])}</span>' if p.get('old_price') else ''}
                </div>
                <div class="product-actions">
                    <button class="btn btn-primary btn-block" onclick="addToCart({p['id']})">
                        🛒 В корзину
                    </button>
                </div>
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

    current_url = f"/catalog/{category_slug}" if category_slug else "/catalog"

    content = f"""
    <div class="breadcrumb">
        <a href="/">Главная</a> <span>/</span>
        <a href="/catalog">Каталог</a>
        {f'<span>/</span> <span>{category["name"]}</span>' if category else ''}
    </div>
    
    <div class="page-header">
        <h1 class="page-title">{category['icon'] + ' ' + category['name'] if category else '📦 Каталог товаров'}</h1>
        <p class="page-subtitle">Найдено {len(products)} товаров</p>
    </div>
    
    <div class="sidebar-layout">
        <aside>
            <div class="filters">
                <div class="filter-section">
                    <h4 class="filter-title">Категории</h4>
                    <div style="display: flex; flex-direction: column;">
                        <a href="/catalog" style="display: flex; justify-content: space-between; padding: 10px 0; text-decoration: none; color: {f'var(--primary); font-weight: 600' if not category else 'var(--dark)'};">
                            <span>📦 Все товары</span>
                        </a>
                        {categories_html}
                    </div>
                </div>
                
                <form class="filter-section" method="get" action="{current_url}">
                    <h4 class="filter-title">Цена</h4>
                    <div class="price-inputs">
                        <input type="number" name="min_price" placeholder="От" value="{min_price or ''}">
                        <span>—</span>
                        <input type="number" name="max_price" placeholder="До" value="{max_price or ''}">
                    </div>
                    <input type="hidden" name="sort" value="{sort}">
                    <button type="submit" class="btn btn-primary btn-block" style="margin-top: 16px;">
                        Применить
                    </button>
                </form>
                
                <div class="filter-section">
                    <h4 class="filter-title">Сортировка</h4>
                    <select class="form-control" onchange="window.location.href='{current_url}?sort='+this.value">
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

    return HTMLResponse(base_template(content, category['name'] if category else "Каталог", request, user, cart_count,
                                       favorites_count_header))


# ═══════════════════════════════════════════════════════════════
# ПОИСК
# ═══════════════════════════════════════════════════════════════

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = ""):
    return RedirectResponse(f"/catalog?q={q}", status_code=302)


# ═══════════════════════════════════════════════════════════════
# СТРАНИЦА ТОВАРА
# ═══════════════════════════════════════════════════════════════

@app.get("/product/{slug}", response_class=HTMLResponse)
async def product_detail(request: Request, slug: str):
    user = await get_current_user(request)
    user_id = get_user_id(request)

    cart_count = await get_cart_count(user_id) if user_id else 0
    favorites_count = await get_favorites_count(user_id) if user_id else 0

    product = await get_product_by_slug(slug)
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

    content = f"""
    <div class="breadcrumb">
        <a href="/">Главная</a> <span>/</span>
        <a href="/catalog">Каталог</a> <span>/</span>
        <a href="/catalog/{product.get('category_slug', '')}">{product.get('category_name', 'Категория')}</a> <span>/</span>
        <span>{product['name']}</span>
    </div>
    
    <div class="product-detail">
        <div class="product-gallery">
            {product.get('image', '📦')}
        </div>
        
        <div class="product-detail-info">
            <h1>{product['name']}</h1>
            
            <div class="product-detail-rating">
                <span style="color: #fbbf24;">{stars}</span>
                <span><strong>{product.get('rating', 0)}</strong></span>
                <span style="color: var(--gray);">• {product.get('reviews_count', 0)} отзывов</span>
            </div>
            
            <div class="product-detail-price">{format_price(product['price'])}</div>
            {f'<div class="product-detail-old-price">{format_price(product["old_price"])}</div>' if product.get('old_price') else ''}
            
            {stock_html}
            
            <p class="product-detail-description">
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

    # Рассчитываем суммы
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    discount = sum((item.get('old_price', item['price']) - item['price']) * item['quantity'] for item in cart if
                   item.get('old_price'))
    delivery = 0 if subtotal >= 5000 else 299
    total = subtotal + delivery

    items_html = ""
    for item in cart:
        items_html += f"""
        <div class="cart-item">
            <div class="cart-item-image">{item.get('image', '📦')}</div>
            <div class="cart-item-info">
                <h4 class="cart-item-title">
                    <a href="/product/{item['slug']}">{item['name']}</a>
                </h4>
                <div class="cart-item-price">{format_price(item['price'])}</div>
                {f'<div style="color: var(--gray); text-decoration: line-through; font-size: 14px;">{format_price(item["old_price"])}</div>' if item.get('old_price') else ''}
                
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
            
            {f'<div class="summary-row" style="color: var(--success);"><span>Скидка</span><span>−{format_price(discount)}</span></div>' if discount > 0 else ''}
            
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
                <p>Добавляйте понравившиеся товары, чтобы не потерять их</p>
                <a href="/catalog" class="btn btn-primary">Перейти в каталог</a>
            </div>
        </div>
        """
        return HTMLResponse(base_template(content, "Избранное", request, user, cart_count, 0))

    products_html = ""
    for item in favorites:
        stars = '⭐' * int(item.get('rating', 0))
        products_html += f"""
        <div class="product-card fade-in">
            <div class="product-image">
                <button class="product-favorite active" onclick="toggleFavorite({item['product_id']}, this)">
                    ❤️
                </button>
                {item.get('image', '📦')}
            </div>
            <div class="product-info">
                <h3 class="product-title">
                    <a href="/product/{item['slug']}">{item['name']}</a>
                </h3>
                <div class="product-rating">
                    <span class="stars">{stars}</span>
                    <span>{item.get('rating', 0)}</span>
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
                                      placeholder="Пожелания к заказу, удобное время доставки..."></textarea>
                        </div>
                    </div>
                </div>

                <div class="card" style="margin-bottom: 24px;">
                    <div class="card-header">💳 Способ оплаты</div>
                    <div class="card-body">
                        <label class="filter-option" style="padding: 16px; background: var(--light); border-radius: var(--radius); margin-bottom: 12px; display: flex; cursor: pointer;">
                            <input type="radio" name="payment" value="card" checked style="margin-right: 12px;">
                            <div>
                                <div style="font-weight: 600;">💳 Банковской картой онлайн</div>
                                <div style="font-size: 13px; color: var(--gray);">Visa, Mastercard, МИР</div>
                            </div>
                        </label>
                        <label class="filter-option" style="padding: 16px; background: var(--light); border-radius: var(--radius); margin-bottom: 12px; display: flex; cursor: pointer;">
                            <input type="radio" name="payment" value="sbp" style="margin-right: 12px;">
                            <div>
                                <div style="font-weight: 600;">📱 СБП (Система быстрых платежей)</div>
                                <div style="font-size: 13px; color: var(--gray);">Оплата через приложение банка</div>
                            </div>
                        </label>
                        <label class="filter-option" style="padding: 16px; background: var(--light); border-radius: var(--radius); display: flex; cursor: pointer;">
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

                <p style="text-align: center; margin-top: 16px; font-size: 13px; color: var(--gray);">
                    Нажимая кнопку, вы соглашаетесь с условиями обработки персональных данных
                </p>
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
                    <span style="color: {'var(--success)' if delivery == 0 else 'inherit'};">
                        {'Бесплатно ✓' if delivery == 0 else format_price(delivery)}
                    </span>
                </div>

                {f'''
                <div style="background: #d1fae5; color: #065f46; padding: 12px; border-radius: 8px; margin: 16px 0; font-size: 13px;">
                    ✅ Вы экономите на доставке {format_price(299)}!
                </div>
                ''' if delivery == 0 else f'''
                <div style="background: #fef3c7; color: #92400e; padding: 12px; border-radius: 8px; margin: 16px 0; font-size: 13px;">
                    💡 До бесплатной доставки осталось {format_price(5000 - subtotal)}
                </div>
                '''}

                <div class="summary-row summary-total">
                    <span>Итого к оплате</span>
                    <span>{format_price(total)}</span>
                </div>

                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--light);">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <span style="font-size: 20px;">🔒</span>
                        <span style="font-size: 13px; color: var(--gray);">Безопасная оплата</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <span style="font-size: 20px;">🚚</span>
                        <span style="font-size: 13px; color: var(--gray);">Доставка 1-3 дня</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 20px;">↩️</span>
                        <span style="font-size: 13px; color: var(--gray);">Возврат 14 дней</span>
                    </div>
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

    # Считаем итоговую сумму
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    delivery = 0 if subtotal >= 5000 else 299
    total = subtotal + delivery

    # Создаем заказ
    order_id = await create_order(user_id, name, email, phone, address, comment)

    if not order_id:
        return RedirectResponse("/cart", status_code=302)

    # Обновляем данные пользователя
    await update_user(user_id, phone=phone, address=address)

    # Определяем способ оплаты для отображения
    payment_methods = {
        'card': '💳 Банковская карта',
        'sbp': '📱 СБП',
        'cash': '💵 Наличные при получении'
    }
    payment_text = payment_methods.get(payment, '💳 Банковская карта')

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
                        <span style="color: var(--gray);">Способ оплаты</span>
                        <span>{payment_text}</span>
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

                <div style="background: #dbeafe; color: #1e40af; padding: 16px; border-radius: var(--radius); margin-bottom: 32px;">
                    📞 Наш менеджер свяжется с вами в течение 15 минут для подтверждения заказа
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