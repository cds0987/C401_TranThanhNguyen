import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.tools.init_db import get_connection

def get_product_detail(product_id: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id.strip(),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return f"Không tìm thấy sản phẩm với id '{product_id}'"

    id, name, category, price, stock, specs = row
    stock_status = f"Còn {stock} sản phẩm" if stock > 0 else "Hết hàng"
    return (
        f"Tên: {name}\n"
        f"Danh mục: {category}\n"
        f"Giá: {price:,}đ\n"
        f"Thông số: {specs}\n"
        f"Tồn kho: {stock_status}"
    )

TOOL_SPEC = {
    "name": "get_product_detail",
    "description": "Xem thông tin chi tiết một sản phẩm theo ID. Input: product_id, ví dụ 'p001'.",
    "func": get_product_detail
}