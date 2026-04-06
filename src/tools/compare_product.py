import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.tools.init_db import get_connection

def compare_product(product_list: str) -> str:
    ids = [p.strip() for p in product_list.split(",")]
    placeholders = ",".join(["?" for _ in ids])

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id, name, price, specs, stock FROM products
        WHERE id IN ({placeholders})
    """, ids)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "Không tìm thấy sản phẩm nào để so sánh"

    header = f"{'Tên':<25} {'Giá':>12}  {'Tồn kho':<10}  Thông số"
    divider = "-" * 80
    lines = [header, divider]
    for id, name, price, specs, stock in rows:
        stock_str = f"Còn {stock}" if stock > 0 else "Hết hàng"
        lines.append(f"{name:<25} {price:>12,}đ  {stock_str:<10}  {specs}")

    return "\n".join(lines)

TOOL_SPEC = {
    "name": "compare_product",
    "description": "So sánh nhiều sản phẩm cùng lúc. Input: danh sách product_id cách nhau bởi dấu phẩy, ví dụ 'p001,p003'.",
    "func": compare_product
}
