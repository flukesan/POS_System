import { create } from 'zustand';
import { CartItem, Product, Customer } from '../types';

interface CartState {
  items: CartItem[];
  customer: Customer | null;
  discountPercent: number;
  isCredit: boolean;
  notes: string;

  // Computed
  subtotal: () => number;
  discountAmount: () => number;
  taxAmount: () => number;
  total: () => number;

  // Actions
  addItem: (product: Product, qty?: number) => void;
  removeItem: (productId: string) => void;
  updateQty: (productId: string, qty: number) => void;
  updateDiscount: (productId: string, discountPercent: number) => void;
  updateItemPrice: (productId: string, price: number) => void;
  setCustomer: (customer: Customer | null) => void;
  setOrderDiscount: (percent: number) => void;
  setCredit: (isCredit: boolean) => void;
  setNotes: (notes: string) => void;
  clearCart: () => void;
}

function calcItemAmounts(product: Product, qty: number, unitPrice: number, discountPct: number) {
  const discountAmt = unitPrice * qty * (discountPct / 100);
  const taxable = unitPrice * qty - discountAmt;
  const taxAmt = taxable * (product.tax_rate / 100);
  return {
    discount_amount: discountAmt,
    tax_amount: taxAmt,
    total_amount: taxable + taxAmt,
  };
}

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  customer: null,
  discountPercent: 0,
  isCredit: false,
  notes: '',

  subtotal: () => get().items.reduce((s, i) => s + i.unit_price * i.quantity - i.discount_amount, 0),
  discountAmount: () => get().subtotal() * (get().discountPercent / 100),
  taxAmount: () => get().items.reduce((s, i) => s + i.tax_amount, 0),
  total: () => get().subtotal() - get().discountAmount() + get().taxAmount(),

  addItem: (product, qty = 1) => {
    set((state) => {
      const existing = state.items.find((i) => i.product.id === product.id);
      if (existing) {
        return {
          items: state.items.map((i) =>
            i.product.id === product.id
              ? {
                  ...i,
                  quantity: i.quantity + qty,
                  ...calcItemAmounts(product, i.quantity + qty, i.unit_price, i.discount_percent),
                }
              : i
          ),
        };
      }
      const amounts = calcItemAmounts(product, qty, product.selling_price, 0);
      return {
        items: [
          ...state.items,
          {
            product,
            quantity: qty,
            unit_price: product.selling_price,
            discount_percent: 0,
            ...amounts,
          },
        ],
      };
    });
  },

  removeItem: (productId) =>
    set((state) => ({ items: state.items.filter((i) => i.product.id !== productId) })),

  updateQty: (productId, qty) =>
    set((state) => ({
      items: state.items.map((i) =>
        i.product.id === productId
          ? { ...i, quantity: qty, ...calcItemAmounts(i.product, qty, i.unit_price, i.discount_percent) }
          : i
      ),
    })),

  updateDiscount: (productId, discountPercent) =>
    set((state) => ({
      items: state.items.map((i) =>
        i.product.id === productId
          ? { ...i, discount_percent: discountPercent, ...calcItemAmounts(i.product, i.quantity, i.unit_price, discountPercent) }
          : i
      ),
    })),

  updateItemPrice: (productId, price) =>
    set((state) => ({
      items: state.items.map((i) =>
        i.product.id === productId
          ? { ...i, unit_price: price, ...calcItemAmounts(i.product, i.quantity, price, i.discount_percent) }
          : i
      ),
    })),

  setCustomer: (customer) => set({ customer }),
  setOrderDiscount: (percent) => set({ discountPercent: percent }),
  setCredit: (isCredit) => set({ isCredit }),
  setNotes: (notes) => set({ notes }),
  clearCart: () => set({ items: [], customer: null, discountPercent: 0, isCredit: false, notes: '' }),
}));
