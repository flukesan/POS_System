"""
API Client - communicates with FastAPI backend
"""
import requests
from typing import Optional, Dict, Any

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def _headers(self) -> Dict[str, str]:
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def _handle(self, resp: requests.Response) -> Any:
        if resp.status_code == 401:
            self.token = None
            raise APIError('กรุณาเข้าสู่ระบบใหม่', 401)
        if not resp.ok:
            try:
                body = resp.json()
                detail = body.get('detail', resp.text)
                msg = detail if isinstance(detail, str) else str(detail)
            except Exception:
                msg = resp.text or f'HTTP {resp.status_code}'
            raise APIError(f'[HTTP {resp.status_code}] {msg}', resp.status_code)
        return resp.json()

    def login(self, username: str, password: str) -> Dict:
        resp = self.session.post(
            f'{self.base_url}/auth/login',
            data={'username': username, 'password': password},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        data = self._handle(resp)
        self.token = data['access_token']
        return data

    def get(self, path: str, params: Dict = None) -> Any:
        resp = self.session.get(
            f'{self.base_url}{path}',
            params=params,
            headers=self._headers(),
        )
        return self._handle(resp)

    def post(self, path: str, data: Dict = None) -> Any:
        resp = self.session.post(
            f'{self.base_url}{path}',
            json=data,
            headers=self._headers(),
        )
        return self._handle(resp)

    def put(self, path: str, data: Dict = None) -> Any:
        resp = self.session.put(
            f'{self.base_url}{path}',
            json=data,
            headers=self._headers(),
        )
        return self._handle(resp)

    # ── Products ──────────────────────────────────────────
    def get_products(self, search='', limit=200):
        return self.get('/products', {'search': search, 'limit': limit})

    def get_product_by_code(self, code: str):
        return self.get('/products/scan', {'code': code})

    def create_product(self, data: Dict):
        return self.post('/products', data)

    def update_product(self, product_id: str, data: Dict):
        return self.put(f'/products/{product_id}', data)

    def get_categories(self):
        return self.get('/products/categories')

    # ── Stock ─────────────────────────────────────────────
    def get_stock(self, low_only=False):
        return self.get('/stock', {'low_stock_only': low_only})

    def get_low_stock_alerts(self):
        return self.get('/stock/alerts/low-stock')

    # ── Sales ─────────────────────────────────────────────
    def create_order(self, data: Dict):
        return self.post('/sales/orders', data)

    def initiate_payment(self, data: Dict):
        return self.post('/sales/payment/initiate', data)

    def confirm_payment(self, data: Dict):
        return self.post('/sales/payment/confirm', data)

    # ── Customers ─────────────────────────────────────────
    def get_customers(self, search='', limit=100):
        return self.get('/customers', {'search': search, 'limit': limit})

    def create_customer(self, data: Dict):
        return self.post('/customers', data)

    def update_customer(self, customer_id: str, data: Dict):
        return self.put(f'/customers/{customer_id}', data)

    def get_credit_summary(self, customer_id: str):
        return self.get(f'/customers/{customer_id}/credit-summary')

    # ── Reports ───────────────────────────────────────────
    def get_dashboard(self):
        return self.get('/reports/dashboard')

    def get_daily_sales(self):
        return self.get('/reports/sales/daily')

    def get_top_products(self):
        return self.get('/reports/sales/top-products')

    def get_settings(self):
        return self.get('/settings') if self._has_settings() else {}

    def _has_settings(self):
        return True
