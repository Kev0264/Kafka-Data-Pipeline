from flask import Flask, render_template, Response
import psycopg2
import os
import json
from datetime import datetime, time, timedelta

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )


def get_dashboard_data():
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
    top_products = [{
        'name': row[0],
        'quantity': row[1],
        'revenue': float(row[2])
    } for row in cur.fetchall()]

    # Sales trend (last 7 days)
    date_7_days_ago = today - timedelta(days=7)
    cur.execute("""
    SELECT date, total_sales, order_count
    FROM daily_sales
    WHERE date >= %s
    ORDER BY date
    """, (date_7_days_ago,))
    sales_trend = [{
        'date': row[0].strftime('%Y-%m-%d'),
        'sales': float(row[1]),
        'orders': row[2]
    } for row in cur.fetchall()]

    cur.close()
    conn.close()

    return {
        'total_sales': total_sales,
        'today_sales': today_sales,
        'today_orders': today_orders,
        'top_products': top_products,
        'sales_trend': sales_trend
    }


@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/stream')
def stream():
    def event_stream():
        while True:
            try:
                data = get_dashboard_data()
                yield f"data: {json.dumps(data)}\n\n"
                time.sleep(5)
            except Exception as e:
                print(f"Error in stream: {str(e)}")
                time.sleep(1)

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={'Cache-Control': 'no-cache'}
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
