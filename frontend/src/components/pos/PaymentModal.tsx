import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { salesApi } from '../../services/api';
import { useCartStore } from '../../store/cartStore';
import { formatCurrency } from '../../utils/format';
import { X, Banknote, QrCode, CreditCard, Check, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

interface Props {
  onClose: () => void;
}

type PayMethod = 'cash' | 'qr_promptpay' | 'credit';

interface QRPaymentData {
  transaction_ref: string;
  amount: number;
  qr_data: string;
  qr_image: string;
}

export default function PaymentModal({ onClose }: Props) {
  const cartStore = useCartStore();
  const [method, setMethod] = useState<PayMethod>('cash');
  const [cashInput, setCashInput] = useState('');
  const [qrData, setQrData] = useState<QRPaymentData | null>(null);
  const [orderId, setOrderId] = useState<string | null>(null);
  const [orderCompleted, setOrderCompleted] = useState(false);
  const [confirmRef, setConfirmRef] = useState('');
  const total = cartStore.total();
  const change = method === 'cash' ? (parseFloat(cashInput) || 0) - total : 0;

  const createOrderMutation = useMutation({
    mutationFn: () =>
      salesApi.createOrder({
        customer_id: cartStore.customer?.id,
        items: cartStore.items.map((i) => ({
          product_id: i.product.id,
          quantity: i.quantity,
          unit_price: i.unit_price,
          discount_percent: i.discount_percent,
        })),
        discount_percent: cartStore.discountPercent,
        notes: cartStore.notes,
        is_credit_sale: cartStore.isCredit,
      }),
    onSuccess: (res) => setOrderId(res.data.order_id),
    onError: () => toast.error('ไม่สามารถสร้างออเดอร์ได้'),
  });

  const payMutation = useMutation({
    mutationFn: (oid: string) =>
      salesApi.initiatePayment({
        order_id: oid,
        payment_method: method,
        paid_amount: method === 'cash' ? parseFloat(cashInput) : undefined,
      }),
    onSuccess: (res) => {
      if (method === 'qr_promptpay') {
        setQrData(res.data);
      } else {
        setOrderCompleted(true);
        toast.success('ชำระเงินสำเร็จ!');
        cartStore.clearCart();
      }
    },
    onError: () => toast.error('เกิดข้อผิดพลาดในการชำระเงิน'),
  });

  const confirmMutation = useMutation({
    mutationFn: () =>
      salesApi.confirmPayment({
        transaction_ref: qrData!.transaction_ref,
        bank_reference: confirmRef || undefined,
      }),
    onSuccess: () => {
      setOrderCompleted(true);
      toast.success('ยืนยันการรับเงินสำเร็จ!');
      cartStore.clearCart();
    },
    onError: () => toast.error('ไม่สามารถยืนยันได้'),
  });

  const handleProceed = async () => {
    let oid = orderId;
    if (!oid) {
      const res = await createOrderMutation.mutateAsync();
      oid = res.data.order_id;
    }
    payMutation.mutate(oid!);
  };

  const QUICK_AMOUNTS = [20, 50, 100, 500, 1000];

  if (orderCompleted) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8 text-center max-w-sm w-full mx-4 shadow-2xl">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Check className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">ชำระเงินสำเร็จ</h2>
          <p className="text-gray-500 mb-1">ยอดชำระ: <span className="font-bold text-green-600">{formatCurrency(total)}</span></p>
          {method === 'cash' && change >= 0 && (
            <p className="text-gray-500 mb-4">เงินทอน: <span className="font-bold text-blue-600">{formatCurrency(change)}</span></p>
          )}
          <div className="flex gap-3">
            <button
              onClick={() => window.print()}
              className="flex-1 py-3 border border-gray-300 rounded-xl text-gray-600 hover:bg-gray-50"
            >
              พิมพ์ใบเสร็จ
            </button>
            <button
              onClick={onClose}
              className="flex-1 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 font-semibold"
            >
              รายการถัดไป
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-bold text-gray-800">ชำระเงิน</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Total */}
          <div className="bg-green-50 rounded-xl p-4 text-center">
            <p className="text-sm text-gray-500 mb-1">ยอดชำระทั้งหมด</p>
            <p className="text-4xl font-bold text-green-600">{formatCurrency(total)}</p>
            <p className="text-xs text-gray-400 mt-1">{cartStore.items.length} รายการ</p>
          </div>

          {/* Payment Method */}
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">เลือกวิธีชำระเงิน</p>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'cash', label: 'เงินสด', icon: Banknote },
                { id: 'qr_promptpay', label: 'QR พร้อมเพย์', icon: QrCode },
                { id: 'credit', label: 'เครดิต', icon: CreditCard, disabled: !cartStore.customer },
              ].map(({ id, label, icon: Icon, disabled }) => (
                <button
                  key={id}
                  disabled={disabled}
                  onClick={() => setMethod(id as PayMethod)}
                  className={`flex flex-col items-center gap-1.5 py-3 px-2 rounded-xl border-2 transition-all text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed ${
                    method === id
                      ? 'border-green-500 bg-green-50 text-green-700'
                      : 'border-gray-200 text-gray-600 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Cash Input */}
          {method === 'cash' && (
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-2">รับเงินมา (บาท)</label>
              <input
                type="number"
                value={cashInput}
                onChange={(e) => setCashInput(e.target.value)}
                placeholder="0.00"
                className="w-full text-2xl text-center border-2 rounded-xl py-3 font-bold focus:border-green-500 focus:outline-none"
                autoFocus
              />
              <div className="flex gap-2 mt-2 flex-wrap">
                {QUICK_AMOUNTS.filter(a => a >= total).map((a) => (
                  <button
                    key={a}
                    onClick={() => setCashInput(String(a))}
                    className="px-3 py-1.5 bg-gray-100 rounded-lg text-sm hover:bg-gray-200 font-medium"
                  >
                    {formatCurrency(a)}
                  </button>
                ))}
                <button
                  onClick={() => setCashInput(String(Math.ceil(total / 10) * 10))}
                  className="px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg text-sm hover:bg-blue-100 font-medium"
                >
                  ปัดขึ้น
                </button>
              </div>
              {cashInput && (
                <div className={`mt-3 text-center text-lg font-bold ${change >= 0 ? 'text-blue-600' : 'text-red-500'}`}>
                  {change >= 0 ? `เงินทอน: ${formatCurrency(change)}` : `ขาดอยู่: ${formatCurrency(Math.abs(change))}`}
                </div>
              )}
            </div>
          )}

          {/* QR Payment */}
          {method === 'qr_promptpay' && qrData && (
            <div className="text-center space-y-3">
              <p className="text-sm text-gray-600">สแกน QR เพื่อชำระเงิน {formatCurrency(qrData.amount)}</p>
              <img src={qrData.qr_image} alt="QR Payment" className="mx-auto w-52 h-52 border rounded-xl" />
              <p className="text-xs text-gray-400">อ้างอิง: {qrData.transaction_ref}</p>
              <div className="border-t pt-3">
                <p className="text-sm font-medium text-gray-700 mb-2">ยืนยันหลังรับเงิน</p>
                <input
                  type="text"
                  value={confirmRef}
                  onChange={(e) => setConfirmRef(e.target.value)}
                  placeholder="รหัสอ้างอิงธนาคาร (ถ้ามี)"
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:outline-none"
                />
                <button
                  onClick={() => confirmMutation.mutate()}
                  disabled={confirmMutation.isPending}
                  className="w-full mt-2 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {confirmMutation.isPending ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                  ยืนยันรับเงินแล้ว
                </button>
              </div>
            </div>
          )}

          {/* Credit */}
          {method === 'credit' && cartStore.customer && (
            <div className="bg-yellow-50 rounded-xl p-4 text-sm">
              <p className="font-medium text-gray-700">ลูกค้า: {cartStore.customer.name}</p>
              <p className="text-gray-500">วงเงินคงเหลือ: {formatCurrency(cartStore.customer.credit_limit - cartStore.customer.credit_balance)}</p>
              <p className="text-gray-500">กำหนดชำระ: {cartStore.customer.credit_days} วัน</p>
            </div>
          )}
        </div>

        {/* Footer */}
        {!(method === 'qr_promptpay' && qrData) && (
          <div className="p-6 border-t">
            <button
              onClick={handleProceed}
              disabled={
                payMutation.isPending ||
                createOrderMutation.isPending ||
                (method === 'cash' && (parseFloat(cashInput) || 0) < total)
              }
              className="w-full py-4 bg-green-600 text-white rounded-xl font-bold text-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {payMutation.isPending || createOrderMutation.isPending ? (
                <RefreshCw className="w-5 h-5 animate-spin" />
              ) : null}
              {method === 'cash' ? 'รับชำระเงิน' : method === 'qr_promptpay' ? 'สร้าง QR Code' : 'บันทึกเครดิต'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
