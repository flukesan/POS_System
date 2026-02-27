import React, { useState, useRef, useCallback } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { productApi, salesApi, customerApi } from '../../services/api';
import { useCartStore } from '../../store/cartStore';
import { Product, Customer } from '../../types';
import { formatCurrency } from '../../utils/format';
import CartPanel from './CartPanel';
import ProductGrid from './ProductGrid';
import PaymentModal from './PaymentModal';
import CustomerSearchModal from '../customer/CustomerSearchModal';
import QRScannerModal from './QRScannerModal';
import toast from 'react-hot-toast';
import { Search, ScanLine, UserPlus, ShoppingCart, Trash2 } from 'lucide-react';

export default function POSTerminal() {
  const [search, setSearch] = useState('');
  const [showPayment, setShowPayment] = useState(false);
  const [showCustomer, setShowCustomer] = useState(false);
  const [showScanner, setShowScanner] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const cartStore = useCartStore();
  const searchRef = useRef<HTMLInputElement>(null);

  const { data: products, isLoading } = useQuery({
    queryKey: ['products', search, categoryFilter],
    queryFn: () => productApi.list({ search, category_id: categoryFilter || undefined, limit: 60 }),
    select: (r) => r.data,
  });

  const scanMutation = useMutation({
    mutationFn: (code: string) => productApi.scan(code),
    onSuccess: (res) => {
      cartStore.addItem(res.data.product);
      toast.success(`เพิ่ม: ${res.data.product.name}`);
    },
    onError: () => toast.error('ไม่พบสินค้า'),
  });

  const handleScan = useCallback((code: string) => {
    setShowScanner(false);
    scanMutation.mutate(code);
  }, []);

  const handleCheckout = () => {
    if (cartStore.items.length === 0) {
      toast.error('กรุณาเพิ่มสินค้าก่อนชำระเงิน');
      return;
    }
    setShowPayment(true);
  };

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      {/* Left: Product Selection */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Search Bar */}
        <div className="bg-white shadow-sm px-4 py-3 flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              ref={searchRef}
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="ค้นหาสินค้า ชื่อ / รหัส / บาร์โค้ด..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:outline-none"
            />
          </div>
          <button
            onClick={() => setShowScanner(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
          >
            <ScanLine className="w-4 h-4" />
            สแกน QR/บาร์โค้ด
          </button>
        </div>

        {/* Products Grid */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-32 text-gray-400">กำลังโหลด...</div>
          ) : (
            <ProductGrid
              products={products || []}
              onSelect={(p) => {
                cartStore.addItem(p);
                toast.success(`เพิ่ม: ${p.name}`);
              }}
            />
          )}
        </div>
      </div>

      {/* Right: Cart Panel */}
      <div className="w-96 flex flex-col bg-white shadow-xl border-l">
        {/* Customer */}
        <div className="px-4 py-3 border-b bg-gray-50">
          <button
            onClick={() => setShowCustomer(true)}
            className="w-full flex items-center gap-2 px-3 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-green-500 hover:text-green-600 transition-colors text-sm"
          >
            <UserPlus className="w-4 h-4" />
            {cartStore.customer ? (
              <span className="font-medium text-gray-800">{cartStore.customer.name}</span>
            ) : (
              'เลือกลูกค้า (ไม่บังคับ)'
            )}
          </button>
        </div>

        {/* Cart Items */}
        <CartPanel />

        {/* Footer - Totals & Checkout */}
        <div className="p-4 border-t bg-gray-50">
          <div className="space-y-1 mb-3 text-sm">
            <div className="flex justify-between text-gray-600">
              <span>ยอดรวม</span>
              <span>{formatCurrency(cartStore.subtotal())}</span>
            </div>
            {cartStore.discountPercent > 0 && (
              <div className="flex justify-between text-red-500">
                <span>ส่วนลด ({cartStore.discountPercent}%)</span>
                <span>-{formatCurrency(cartStore.discountAmount())}</span>
              </div>
            )}
            <div className="flex justify-between text-gray-600">
              <span>ภาษี 7%</span>
              <span>{formatCurrency(cartStore.taxAmount())}</span>
            </div>
            <div className="flex justify-between text-lg font-bold text-gray-900 border-t pt-2">
              <span>ยอดชำระ</span>
              <span className="text-green-600">{formatCurrency(cartStore.total())}</span>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => cartStore.clearCart()}
              className="px-3 py-3 border border-red-300 text-red-500 rounded-lg hover:bg-red-50"
            >
              <Trash2 className="w-5 h-5" />
            </button>
            <button
              onClick={handleCheckout}
              disabled={cartStore.items.length === 0}
              className="flex-1 flex items-center justify-center gap-2 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-lg"
            >
              <ShoppingCart className="w-5 h-5" />
              ชำระเงิน
            </button>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showPayment && <PaymentModal onClose={() => setShowPayment(false)} />}
      {showCustomer && (
        <CustomerSearchModal
          onSelect={(c) => { cartStore.setCustomer(c); setShowCustomer(false); }}
          onClose={() => setShowCustomer(false)}
        />
      )}
      {showScanner && <QRScannerModal onScan={handleScan} onClose={() => setShowScanner(false)} />}
    </div>
  );
}
