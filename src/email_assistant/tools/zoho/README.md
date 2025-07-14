# Zoho Inventory Integration

This module provides integration with Zoho Inventory for the sales monitor agent.

## Setup

### 1. Zoho API Credentials

To use the Zoho Inventory API, you need to:

1. **Create a Zoho Developer Account**: Visit [Zoho API Console](https://api-console.zoho.com/)
2. **Create a New Application**: Choose "Self Client" application type
3. **Generate API Credentials**: Get your Client ID and Client Secret
4. **Set up OAuth**: Configure the OAuth flow to get access tokens

### 2. Environment Variables

Add the following to your `.env` file:

```bash
# Zoho Inventory API Configuration
ZOHO_ACCESS_TOKEN=your_access_token_here
ZOHO_ORGANIZATION_ID=your_organization_id_here
ZOHO_CLIENT_ID=your_client_id_here
ZOHO_CLIENT_SECRET=your_client_secret_here
```

### 3. OAuth Token Generation

The Zoho API uses OAuth 2.0 for authentication. You'll need to:

1. Generate an authorization code using the Zoho OAuth URL
2. Exchange the authorization code for an access token
3. Use the access token for API requests
4. Refresh the token when it expires

### 4. Organization ID

Your Organization ID can be found in your Zoho Inventory settings under "Organization" > "Organization Details".

## Available Tools

### fetch_inventory_tool
- **Purpose**: Fetch current inventory items
- **Parameters**: 
  - `category` (optional): Filter by product category
  - `low_stock_only` (bool): Only return items below reorder level
- **Returns**: Current inventory status with stock levels

### check_stock_levels_tool
- **Purpose**: Check stock levels and get alerts
- **Parameters**: 
  - `item_name` (optional): Specific item to check
- **Returns**: Stock level report with alerts for low stock items

### get_sales_analytics_tool
- **Purpose**: Get sales performance data
- **Parameters**: 
  - `period`: Time period ('today', 'week', 'month')
- **Returns**: Sales analytics including revenue, orders, and top-selling items

### create_order_tool
- **Purpose**: Create new sales orders
- **Parameters**: 
  - `item_name`: Product to order
  - `quantity`: Number of units
  - `customer_email`: Customer contact
  - `notes` (optional): Order notes
- **Returns**: Order confirmation with order ID

### update_inventory_tool
- **Purpose**: Update inventory quantities
- **Parameters**: 
  - `item_name`: Item to update
  - `new_quantity`: New stock quantity
  - `reason` (optional): Reason for adjustment
- **Returns**: Confirmation of inventory update

## Mock Data

For development and testing, the tools include mock data that simulates:
- Sample inventory items (Electronics, Accessories)
- Sales analytics data
- Low stock alerts

## Error Handling

The tools include robust error handling:
- Graceful fallback to mock data when API is unavailable
- Detailed error messages for troubleshooting
- Logging of API requests and errors

## Security Notes

- Never commit your API credentials to version control
- Use environment variables for all sensitive configuration
- Implement proper token refresh mechanisms for production use
- Consider using Zoho's webhook functionality for real-time updates 