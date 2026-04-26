import sqlite3
import os

DB_PATH = "./data/ecommerce.db"

def create_database():
    """创建 SQLite 测试数据库并插入示例数据"""
    #确保目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 产品表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    # 2. 客户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            city TEXT NOT NULL
        )
    """)

    # 3. 订单表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    # 插入示例数据（如果表为空）
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO products (product_name, category, price) VALUES (?, ?, ?)",
            [
                ("机械键盘", "电脑配件", 299.00),
                ("无线鼠标", "电脑配件", 89.00),
                ("27寸显示器", "电脑配件", 1599.00),
                ("Python编程书", "图书", 79.00),
                ("机器学习实战", "图书", 108.00),
                ("降噪耳机", "影音设备", 499.00),
            ]
        )
        
        cursor.executemany(
            "INSERT INTO customers (customer_name, city) VALUES (?, ?)",
            [
                ("张三", "北京"),
                ("李四", "上海"),
                ("王五", "广州"),
                ("赵六", "深圳"),
            ]
        )
        
        cursor.executemany(
            "INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)",
            [
                (1, 1, 2, "2026-03-15"),
                (1, 2, 1, "2026-03-16"),
                (2, 3, 1, "2026-03-18"),
                (3, 4, 3, "2026-03-20"),
                (3, 5, 1, "2026-03-22"),
                (4, 6, 2, "2026-03-25"),
                (2, 1, 1, "2026-04-01"),
                (4, 3, 1, "2026-04-05"),
            ]
        )
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库已创建：{DB_PATH}")
    print("   - products 表：6 条记录")
    print("   - customers 表：4 条记录")
    print("   - orders 表：8 条记录")

if __name__ == "__main__":
    create_database()