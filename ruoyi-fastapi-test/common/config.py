import os


class Config:
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:80')
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:9099')
    admin_username = os.getenv('TEST_ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('TEST_ADMIN_PASSWORD', 'admin123')
    distribution_agent_username = os.getenv('DIST_TEST_AGENT_USERNAME')
    distribution_agent_password = os.getenv('DIST_TEST_AGENT_PASSWORD')
    distribution_customer_username = os.getenv('DIST_TEST_CUSTOMER_USERNAME')
    distribution_customer_password = os.getenv('DIST_TEST_CUSTOMER_PASSWORD')
