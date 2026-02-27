// ─── Core Types ──────────────────────────────────────────────

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'manager' | 'cashier' | 'warehouse';
  avatar_url?: string;
  is_active: boolean;
}

export interface Category {
  id: string;
  name: string;
  name_en?: string;
  parent_id?: string;
  image_url?: string;
  sort_order: number;
  is_active: boolean;
}

export interface Supplier {
  id: string;
  code: string;
  name: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  credit_days: number;
}

export interface Product {
  id: string;
  code: string;
  barcode?: string;
  qr_code?: string;
  name: string;
  name_en?: string;
  category_id?: string;
  supplier_id?: string;
  unit: string;
  unit_per_pack: number;
  cost_price: number;
  selling_price: number;
  min_selling_price?: number;
  tax_rate: number;
  description?: string;
  main_image_url?: string;
  min_stock_level: number;
  reorder_point: number;
  chemical_registration?: string;
  expiry_tracking: boolean;
  is_active: boolean;
  category?: Category;
  supplier?: Supplier;
}

export interface StockItem {
  stock_id: string;
  product_id: string;
  product_name: string;
  product_code: string;
  unit: string;
  quantity: number;
  reserved: number;
  available: number;
  min_stock_level: number;
  reorder_point: number;
  is_low: boolean;
}

export interface Customer {
  id: string;
  code: string;
  customer_type: string;
  name: string;
  phone?: string;
  email?: string;
  address?: string;
  district?: string;
  province?: string;
  farm_area_rai?: number;
  crop_types: string[];
  credit_limit: number;
  credit_balance: number;
  credit_days: number;
  credit_status: 'active' | 'overdue' | 'paid' | 'suspended';
  loyalty_points: number;
  total_purchases: number;
  is_active: boolean;
}

export interface CartItem {
  product: Product;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  discount_amount: number;
  tax_amount: number;
  total_amount: number;
}

export interface SalesOrder {
  id: string;
  order_number: string;
  customer_id?: string;
  customer?: Customer;
  order_date: string;
  status: 'draft' | 'pending' | 'completed' | 'cancelled' | 'refunded';
  subtotal: number;
  discount_percent: number;
  discount_amount: number;
  tax_amount: number;
  total_amount: number;
  paid_amount: number;
  change_amount: number;
  payment_method?: string;
  payment_status: 'pending' | 'confirmed' | 'failed' | 'refunded';
  is_credit_sale: boolean;
  credit_due_date?: string;
  items: SalesOrderItem[];
}

export interface SalesOrderItem {
  id: string;
  product_id: string;
  product?: Product;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  discount_amount: number;
  tax_rate: number;
  tax_amount: number;
  total_amount: number;
}

export interface PaymentTransaction {
  id: string;
  order_id: string;
  transaction_ref: string;
  payment_method: string;
  amount: number;
  status: string;
  qr_code_data?: string;
  qr_image?: string;
  confirmed_at?: string;
}

export interface DashboardStats {
  today: { order_count: number; total_sales: number };
  this_month: { order_count: number; total_sales: number };
  low_stock_products: number;
  total_outstanding_credit: number;
  overdue_customers: number;
}

export interface PurchaseOrder {
  id: string;
  po_number: string;
  supplier_id?: string;
  supplier?: Supplier;
  order_date: string;
  expected_date?: string;
  received_date?: string;
  status: string;
  total_amount: number;
  items: PurchaseOrderItem[];
}

export interface PurchaseOrderItem {
  id: string;
  product_id: string;
  product?: Product;
  ordered_quantity: number;
  received_quantity: number;
  unit_cost: number;
  total_cost: number;
  lot_number?: string;
  expiry_date?: string;
}
