import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from database import DB_NAME
import base64

def generate_order_slip(order_id):
    """Generate HTML slip for printing"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get order details
    cursor.execute("""
        SELECT o.*, c.name, c.phone, c.address
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        WHERE o.id = ?
    """, (order_id,))
    
    order = cursor.fetchone()
    columns = [description[0] for description in cursor.description]
    order_dict = dict(zip(columns, order))
    
    # Get measurements
    cursor.execute("SELECT measurements FROM orders WHERE id = ?", (order_id,))
    measurements = cursor.fetchone()[0]
    
    conn.close()
    
    # Generate HTML slip
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Order Slip #{order_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }}
            .section {{ margin-bottom: 15px; }}
            .section-title {{ font-weight: bold; background-color: #f0f0f0; padding: 5px; }}
            .row {{ display: flex; justify-content: space-between; margin-bottom: 5px; }}
            .footer {{ margin-top: 30px; text-align: center; border-top: 1px solid #000; padding-top: 10px; }}
            @media print {{ 
                .no-print {{ display: none; }}
                body {{ margin: 0; padding: 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>AZAD TAILOR</h2>
            <h3>ORDER SLIP</h3>
            <p>Slip No: #{order_id} | Date: {order_dict['order_date']}</p>
        </div>
        
        <div class="section">
            <div class="section-title">Customer Details</div>
            <p><strong>Name:</strong> {order_dict['name']}</p>
            <p><strong>Phone:</strong> {order_dict['phone']}</p>
            <p><strong>Address:</strong> {order_dict['address']}</p>
        </div>
        
        <div class="section">
            <div class="section-title">Order Details</div>
            <div class="row">
                <span><strong>Delivery Date:</strong> {order_dict['delivery_date']}</span>
                <span><strong>Status:</strong> {order_dict['status']}</span>
            </div>
            <div class="row">
                <span><strong>Suits:</strong> {order_dict['suits']}</span>
                <span><strong>Total Bill:</strong> ₹{order_dict['total_bill']}</span>
            </div>
            <div class="row">
                <span><strong>Advance:</strong> ₹{order_dict['advance']}</span>
                <span><strong>Balance:</strong> ₹{order_dict['balance']}</span>
            </div>
        </div>
        
        {generate_measurements_html(measurements) if measurements else ''}
        
        <div class="footer">
            <p>Customer Signature: ___________________</p>
            <p>Tailor Signature: ___________________</p>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="no-print" style="margin-top: 20px;">
            <button onclick="window.print()">Print Slip</button>
        </div>
    </body>
    </html>
    """
    
    return html

def generate_measurements_html(measurements_json):
    import json
    try:
        measurements = json.loads(measurements_json)
        html = '<div class="section"><div class="section-title">Measurements</div>'
        
        for key, value in measurements.items():
            if value:  # Only show non-empty measurements
                html += f'<p><strong>{key.replace("_", " ").title()}:</strong> {value}"</p>'
        
        html += '</div>'
        return html
    except:
        return ""

def show_reports_page():
    st.title("📄 Reports & Export")
    
    tab1, tab2, tab3 = st.tabs(["Print Preview", "Data Export", "Sales Reports"])
    
    with tab1:
        st.subheader("🖨️ Print Order Slip")
        
        # Select order for printing
        conn = sqlite3.connect(DB_NAME)
        orders = pd.read_sql_query("""
            SELECT o.id, c.name, o.order_date 
            FROM orders o
            JOIN clients c ON o.client_id = c.id
            ORDER BY o.id DESC
            LIMIT 50
        """, conn)
        conn.close()
        
        if not orders.empty:
            order_options = {f"#{row['id']} - {row['name']} ({row['order_date']})": row['id'] 
                           for _, row in orders.iterrows()}
            
            selected_order = st.selectbox("Select Order to Print", list(order_options.keys()))
            
            if selected_order:
                order_id = order_options[selected_order]
                
                # Display preview
                st.subheader("Preview")
                html_slip = generate_order_slip(order_id)
                st.components.v1.html(html_slip, height=800, scrolling=True)
                
                # Download HTML
                st.download_button(
                    label="📥 Download Slip (HTML)",
                    data=html_slip,
                    file_name=f"order_slip_{order_id}.html",
                    mime="text/html"
                )
        else:
            st.info("No orders available for printing")
    
    with tab2:
        st.subheader("📤 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_type = st.selectbox(
                "Select Data to Export",
                ["Orders", "Clients", "Payments", "Complete Database"]
            )
            
            date_range = st.date_input(
                "Select Date Range",
                [datetime.now().date() - timedelta(days=30), datetime.now().date()]
            )
        
        with col2:
            format_type = st.selectbox("Export Format", ["CSV", "Excel"])
            
            if st.button("Generate Export", type="primary"):
                with st.spinner("Generating export..."):
                    data = export_data(export_type, date_range)
                    
                    if format_type == "CSV":
                        csv = data.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"{export_type.lower()}_export.csv",
                            mime="text/csv"
                        )
                    else:
                        # For Excel export
                        import io
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            data.to_excel(writer, index=False, sheet_name=export_type)
                        
                        st.download_button(
                            label="Download Excel",
                            data=output.getvalue(),
                            file_name=f"{export_type.lower()}_export.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
    
    with tab3:
        st.subheader("Sales Reports")
        
        report_type = st.selectbox(
            "Report Type",
            ["Daily Sales", "Monthly Sales", "Customer-wise", "Payment Collection"]
        )
        
        if st.button("Generate Report"):
            report_data = generate_sales_report(report_type)
            st.dataframe(report_data, use_container_width=True)

def export_data(data_type, date_range):
    conn = sqlite3.connect(DB_NAME)
    
    start_date, end_date = date_range
    
    if data_type == "Orders":
        query = f"""
        SELECT o.*, c.name as customer_name, c.phone
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
        """
    elif data_type == "Clients":
        query = "SELECT * FROM clients"
    elif data_type == "Payments":
        query = f"""
        SELECT p.*, c.name as customer_name
        FROM payments p
        JOIN orders o ON p.order_id = o.id
        JOIN clients c ON o.client_id = c.id
        WHERE p.payment_date BETWEEN '{start_date}' AND '{end_date}'
        """
    else:  # Complete Database
        # Get all tables
        query = """
        SELECT 'orders' as table_name, COUNT(*) as count FROM orders
        UNION ALL
        SELECT 'clients' as table_name, COUNT(*) as count FROM clients
        UNION ALL
        SELECT 'payments' as table_name, COUNT(*) as count FROM payments
        """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def generate_sales_report(report_type):
    conn = sqlite3.connect(DB_NAME)
    
    if report_type == "Daily Sales":
        query = """
        SELECT date(delivery_date) as date,
               COUNT(*) as orders_delivered,
               SUM(total_bill) as total_sales,
               SUM(advance) as total_advance,
               SUM(balance) as total_balance
        FROM orders
        WHERE status = 'Delivered'
        GROUP BY date(delivery_date)
        ORDER BY date DESC
        LIMIT 30
        """
    elif report_type == "Monthly Sales":
        query = """
        SELECT strftime('%Y-%m', delivery_date) as month,
               COUNT(*) as orders_delivered,
               SUM(total_bill) as total_sales
        FROM orders
        WHERE status = 'Delivered'
        GROUP BY strftime('%Y-%m', delivery_date)
        ORDER BY month DESC
        """
    elif report_type == "Customer-wise":
        query = """
        SELECT c.name,
               COUNT(o.id) as total_orders,
               SUM(o.total_bill) as total_spent,
               AVG(o.total_bill) as avg_order_value,
               MAX(o.order_date) as last_order_date
        FROM clients c
        JOIN orders o ON c.id = o.client_id
        GROUP BY c.id
        HAVING COUNT(o.id) > 0
        ORDER BY total_spent DESC
        """
    else:  # Payment Collection
        query = """
        SELECT date(p.payment_date) as date,
               c.name as customer,
               p.amount,
               p.payment_method,
               p.notes
        FROM payments p
        JOIN orders o ON p.order_id = o.id
        JOIN clients c ON o.client_id = c.id
        ORDER BY p.payment_date DESC
        LIMIT 100
        """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df
