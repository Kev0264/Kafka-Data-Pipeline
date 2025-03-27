from flask import Flask, render_template
import psycopg2
import os
from datetime import datetime, timedelta

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )


@app.route('/')
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get total sales
    cur.execute("SELECT COALESCE(SUM(total), 0) FROM orders")
    total_sales = float(cur.fetchone()[0])

    # Get today's sales
    today = datetime.now().date()
    cur.execute("""
    SELECT COALESCE(SUM(total_sales), 0), COALESCE(SUM(order_count), 0)
    FROM daily_sales WHERE date = %s
    """, (today,))
    today_result = cur.fetchone()
    today_sales = float(today_result[0])
    today_orders = int(today_result[1])

    # Get top products
    cur.execute("""
    SELECT product_name, SUM(quantity) as total_quantity, SUM(total) as total_revenue
    FROM orders
    GROUP BY product_name
    ORDER BY total_revenue DESC
    LIMIT 5
    """)
    top_products = cur.fetchall()

    # Sales trend (last 7 days)
    date_7_days_ago = today - timedelta(days=7)
    cur.execute("""
    SELECT date, total_sales, order_count
    FROM daily_sales
    WHERE date >= %s
    ORDER BY date
    """, (date_7_days_ago,))
    sales_trend = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('dashboard.html',
                           total_sales=total_sales,
                           today_sales=today_sales,
                           today_orders=today_orders,
                           top_products=top_products,
                           sales_trend=sales_trend)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
