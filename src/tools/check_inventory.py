import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.tools.init_db import get_connection

def check_inventory(product_id: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, stock FROM products WHERE id = ?", (product_id.strip(),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return f"Không tìm thấy sản phẩm với id '{product_id}'"

    name, stock = row
    if stock > 0:
        return f"{name}: Còn {stock} sản phẩm trong kho"
    return f"{name}: Hết hàng"

TOOL_SPEC = {
    "name": "check_inventory",
    "description": "Kiểm tra số lượng tồn kho của một sản phẩm. Input: product_id, ví dụ 'p001'.",
    "func": check_inventory
}
