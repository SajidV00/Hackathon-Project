# Release Notes - RC-2025-5

## New Features & Enhancements

### Payables: Invoice Dispute Process Improvements
- **Enhanced Supplier Portal Actions**: Implemented intuitive action options (View/Edit) for disputed invoices in Supplier Portal, enabling suppliers to efficiently manage invoice disputes through a streamlined interface. This enhancement improves supplier satisfaction and operational efficiency.

- **Document Flow Search Capabilities**: Added ability to search and view Disputed and Voided invoices in Document Flow, with enhanced visibility of high-level invoice details and linked documents. Access is intelligently controlled based on user roles and historical interactions.

- **Dispute UI Enhancements**: 
  - Improved the Dispute Destination Dialog Box with better field alignment and readability
  - Enhanced multi-selection display for dispute reasons
  - Optimized layout and spacing for improved user experience
  - Reorganized field positioning for better workflow

- **Email Notification System**: Implemented comprehensive email notifications for dispute-related actions:
  - Automated notifications for dispute submissions
  - Resolution notifications for void, amend, or reject actions
  - Customized email templates with direct document access
  - Role-based notification routing

### Taxes Module Modernization
- **Tax Management Interface**: Completely redesigned the tax management interface with modern Angular components, providing a more responsive and user-friendly experience.

- **Tax Code Administration**: Enhanced tax code management capabilities with improved validation and data consistency checks.

- **Withholding Tax Management**: Modernized withholding tax functionality with streamlined workflows and better data visualization.

### Multi-Unit ID Management
- **Business Unit Configuration**: Implemented sophisticated business unit management capabilities allowing administrators to:
  - Configure multiple business units from a central interface
  - Manage user access across different business units
  - Control role-based permissions at unit level

- **User Management Enhancements**: 
  - Improved user profile management across multiple business units
  - Enhanced access control mechanisms
  - Streamlined user authentication workflows

### System Health & Configuration
- **Health Check Improvements**: 
  - Added comprehensive health monitoring for Kafka UI
  - Enhanced system status reporting
  - Improved diagnostic capabilities

- **Configuration Management**: 
  - Implemented centralized configuration management
  - Enhanced property handling for accounting and budget APIs
  - Improved system reliability and maintainability

## RESOLUTION
1. Optimized query performance by improving sorting logic in paginated queries, reducing database load and improving response times.

2. Enhanced user experience by implementing proper validation for tax code updates and synchronization across the system.

3. Improved system stability by resolving authentication edge cases in multi-unit ID scenarios.

4. Enhanced data consistency by implementing proper handling of voided invoices in various system workflows.

5. Improved system reliability by implementing proper error handling and validation in the invoice dispute process.

6. Enhanced user interface responsiveness by optimizing component loading and data synchronization.

7. Improved system security by implementing proper access control validation in multi-unit ID scenarios.

8. Enhanced data integrity by implementing proper validation for accounting and budget-related operations.

## Technical Updates
- Upgraded various Angular components to improve system performance and maintainability
- Enhanced API documentation with improved examples and usage guidelines
- Implemented new health check endpoints for better system monitoring
- Updated configuration management system for improved reliability

For detailed technical documentation and implementation guides, please refer to the system documentation.