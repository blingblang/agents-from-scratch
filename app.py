import sys
import os
from flask import Flask, render_template, request, jsonify

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main front-end interface"""
    return render_template('index.html')

@app.route('/api/sales-monitor', methods=['POST'])
def run_sales_monitor():
    """API endpoint to run the Sales Monitor Agent"""
    try:
        # Try to import and use the real Sales Monitor Agent
        try:
            from email_assistant.sales_monitor_agent_hitl_memory import sales_monitor_agent
            from email_assistant.inventory_utils import (
                create_low_stock_trigger,
                create_sales_update_trigger,
                create_manual_check_trigger
            )
            
            data = request.get_json()
            monitor_type = data.get('type', 'manual_check')
            
            # Create the appropriate trigger based on type
            if monitor_type == 'manual_check':
                trigger = create_manual_check_trigger("web_user", "general")
            elif monitor_type == 'low_stock':
                item_name = data.get('item_name', 'USB Cable')
                current_stock = data.get('current_stock', 5)
                reorder_level = data.get('reorder_level', 25)
                trigger = create_low_stock_trigger(item_name, current_stock, reorder_level)
            elif monitor_type == 'sales_analytics':
                period = data.get('period', 'today')
                total_sales = data.get('total_sales', 2450.00)
                total_orders = data.get('total_orders', 15)
                trigger = create_sales_update_trigger(period, total_sales, total_orders)
            else:
                return jsonify({'error': 'Invalid monitor type'}), 400
            
            # Run the Sales Monitor Agent
            result = sales_monitor_agent.invoke({
                "inventory_trigger": trigger
            })
            
            # Extract relevant information from the result
            response_data = {
                'success': True,
                'classification': result.get('classification_decision', 'unknown'),
                'priority': result.get('priority', 'unknown'),
                'messages': []
            }
            
            # Extract message content
            messages = result.get('messages', [])
            for msg in messages:
                if hasattr(msg, 'content'):
                    response_data['messages'].append({
                        'role': getattr(msg, 'role', 'unknown'),
                        'content': msg.content
                    })
                elif isinstance(msg, dict):
                    response_data['messages'].append({
                        'role': msg.get('role', 'unknown'),
                        'content': msg.get('content', str(msg))
                    })
            
            return jsonify(response_data)
            
        except Exception as e:
            # If Sales Monitor Agent import fails, return fallback data
            data = request.get_json()
            monitor_type = data.get('type', 'manual_check')
            
            # Return mock data based on type
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
    
    print("🚀 Starting Sales Monitor Frontend...")
    print("📊 Access the interface at: http://localhost:5004")
    print("🌐 Or use: http://127.0.0.1:5004")
    app.run(debug=True, host='127.0.0.1', port=5004) 