import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main front-end interface"""
    return render_template('index.html')

@app.route('/api/sales-monitor', methods=['POST'])
def run_sales_monitor():
    """API endpoint to simulate Sales Monitor Agent for testing"""
    try:
        data = request.get_json()
        monitor_type = data.get('type', 'manual_check')
        
        # Simulate agent response based on type
        if monitor_type == 'manual_check':
            response_data = {
                'success': True,
                'classification': 'monitor',
                'priority': 'low',
                'messages': [
                    {
                        'role': 'assistant',
                        'content': 'Inventory Check Complete:\n\n✅ Total Items: 150\n✅ Low Stock Items: 3\n✅ Out of Stock: 0\n\nOverall inventory status is good. Consider restocking USB cables and wireless keyboards soon.'
                    }
                ]
            }
        elif monitor_type == 'low_stock':
            item_name = data.get('item_name', 'USB Cable')
            current_stock = data.get('current_stock', 5)
            reorder_level = data.get('reorder_level', 25)
            
            response_data = {
                'success': True,
                'classification': 'action_required',
                'priority': 'high',
                'messages': [
                    {
                        'role': 'assistant',
                        'content': f'⚠️ LOW STOCK ALERT for {item_name}\n\nCurrent Stock: {current_stock} units\nReorder Level: {reorder_level} units\nDeficit: {reorder_level - current_stock} units\n\n🚨 IMMEDIATE ACTION REQUIRED:\n• Place order for at least 50 units\n• Contact supplier immediately\n• Expected delivery: 3-5 business days'
                    }
                ]
            }
        elif monitor_type == 'sales_analytics':
            period = data.get('period', 'today')
            total_sales = data.get('total_sales', 2450.00)
            total_orders = data.get('total_orders', 15)
            avg_order = total_sales / total_orders if total_orders > 0 else 0
            
            response_data = {
                'success': True,
                'classification': 'monitor',
                'priority': 'medium',
                'messages': [
                    {
                        'role': 'assistant',
                        'content': f'📊 Sales Analytics - {period.title()}\n\n💰 Total Sales: ${total_sales:,.2f}\n📦 Total Orders: {total_orders}\n💵 Average Order Value: ${avg_order:.2f}\n\n🏆 Top Performers:\n• USB Cables: $450.00 (18%)\n• Wireless Keyboards: $380.00 (15%)\n• Gaming Mice: $320.00 (13%)\n\n📈 Performance vs. target: +12% above goal!'
                    }
                ]
            }
        else:
            return jsonify({'error': 'Invalid monitor type'}), 400
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error running Sales Monitor Agent: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Sales Monitor Frontend'})

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting Sales Monitor Frontend (Simple Version)...")
    print("📊 Access the interface at: http://localhost:5002")
    app.run(debug=True, host='127.0.0.1', port=5002) 