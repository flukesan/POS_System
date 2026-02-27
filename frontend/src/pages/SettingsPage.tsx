import React from 'react';
import { Settings, Store, CreditCard, Printer, Bell } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">ตั้งค่าระบบ</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { icon: Store, title: 'ข้อมูลร้าน', desc: 'ชื่อ ที่อยู่ เบอร์โทร เลขผู้เสียภาษี' },
          { icon: CreditCard, title: 'ตั้งค่าชำระเงิน', desc: 'บัญชีธนาคาร PromptPay QR Code' },
          { icon: Printer, title: 'ตั้งค่าเครื่องพิมพ์', desc: 'ใบเสร็จ Thermal Printer' },
          { icon: Bell, title: 'การแจ้งเตือน', desc: 'สต๊อกต่ำ เครดิตเกินกำหนด' },
        ].map(({ icon: Icon, title, desc }) => (
          <button key={title} className="bg-white rounded-xl shadow-sm p-5 text-left hover:shadow-md transition-shadow flex items-center gap-4">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center shrink-0">
              <Icon className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">{title}</p>
              <p className="text-sm text-gray-400">{desc}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
