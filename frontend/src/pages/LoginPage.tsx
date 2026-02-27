import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { Leaf, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const mutation = useMutation({
    mutationFn: () => authApi.login(username, password),
    onSuccess: (res) => {
      const { access_token, user_id, username: uname, full_name, role } = res.data;
      login({ id: user_id, username: uname, full_name, role, email: '', is_active: true }, access_token);
      toast.success(`ยินดีต้อนรับ ${full_name}`);
      navigate('/');
    },
    onError: () => toast.error('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      toast.error('กรุณากรอกข้อมูลให้ครบ');
      return;
    }
    mutation.mutate();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-800 to-green-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-green-400 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <Leaf className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">AgriPOS</h1>
          <p className="text-green-300 mt-1">ระบบจัดการร้านค้าเกษตร</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-2xl p-8 space-y-5">
          <h2 className="text-xl font-semibold text-gray-700 text-center">เข้าสู่ระบบ</h2>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">ชื่อผู้ใช้</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="admin"
              className="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-green-500 focus:outline-none text-sm"
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">รหัสผ่าน</label>
            <div className="relative">
              <input
                type={showPw ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-green-500 focus:outline-none text-sm pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            {mutation.isPending ? 'กำลังเข้าสู่ระบบ...' : 'เข้าสู่ระบบ'}
          </button>
        </form>
      </div>
    </div>
  );
}
