from langchain_community.utilities import SQLDatabase

DB_PATH = "./data/ecommerce.db"
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

# 查看数据库中有哪些表
print(f"✅ 数据库连接成功！")
print(f"  表列表：{db.get_usable_table_names()}")
print(f"  各表信息：")
for table in db.get_usable_table_names():
    print(f"    {table}: {db.get_table_info([table])[:200]}...")

# 在 text2sql.py 中追加
result = db.run("SELECT pr.product_name, SUM(o.quantity) AS total_sold FROM orders o JOIN products pr ON o.product_id = pr.product_id GROUP BY pr.product_name ORDER BY total_sold DESC")
print("\n📊 产品销售统计：")
print(result)