import { useState, useEffect } from 'react';
import { getUsers, createUser, updateUserRole, deleteUser } from '@services/userService';
import { FiEye, FiEyeOff } from "react-icons/fi";
import { HiPencilAlt, HiPlus, HiSearch } from 'react-icons/hi';
import { HiTrash } from 'react-icons/hi2';

export default function ManagerUser() {
  const [searchTerm, setSearchTerm] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Pagination state
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [total, setTotal] = useState(0);

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  // Form states - เพิ่ม role เริ่มต้นเป็น operator [แก้ไขบรรทัดที่ 34]
  const [formData, setFormData] = useState({ username: '', password: '', role: 'operator' });
  const [editRole, setEditRole] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // RBAC Logic [เพิ่มบรรทัดที่ 30-57]
  const currentUser = JSON.parse(localStorage.getItem('user')) || {};
  const currentUserRole = currentUser.role?.toLowerCase() || '';

  const getRank = (role) => {
    if (role === 'admin') return 3;
    if (role === 'supervisor') return 2;
    if (role === 'operator') return 1;
    return 0;
  };

  const canManageUser = (targetUser) => {
    const myRank = getRank(currentUserRole);
    const targetRank = getRank(targetUser.role?.toLowerCase());
    return myRank > targetRank; // คนที่ใหญ่กว่าเท่านั้นถึงจะจัดการคนต่ำกว่าได้
  };

  const getAvailableRoles = () => {
    if (currentUserRole === 'admin') {
      return [
        { value: 'admin', label: 'Admin' },
        { value: 'supervisor', label: 'Supervisor' },
        { value: 'operator', label: 'Operator' }
      ];
    }
    if (currentUserRole === 'supervisor') {
      return [{ value: 'operator', label: 'Operator' }]; // Supervisor สร้างได้แค่ Operator
    }
    return [];
  };

  // Fetch users
  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getUsers(page, limit, searchTerm);
      setUsers(data.users || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to Get users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchUsers();
    }, searchTerm ? 500 : 0);
    return () => clearTimeout(timer);
  }, [page, limit, searchTerm]);

  // Handle create user [แก้ไขบรรทัดที่ 84]
  const handleCreateUser = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      // ส่ง formData.role ไปด้วย
      await createUser(formData.username, formData.password, formData.role);
      setSuccess('User created successfully');
      setShowCreateModal(false);
      setFormData({ username: '', password: '', role: 'operator' });
      fetchUsers();
    } catch (err) {
      setError(err.message || 'Failed to create user');
    }
  };

  const handleUpdateRole = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    try {
      await updateUserRole(selectedUser.username, editRole);
      setSuccess('User role updated successfully');
      setShowEditModal(false);
      setSelectedUser(null);
      fetchUsers();
    } catch (err) {
      setError(err.message || 'Failed to update user role');
    }
  };

  const handleDeleteUser = async () => {
    setError(null);
    setSuccess(null);
    try {
      await deleteUser(selectedUser.username);
      setSuccess('User deleted successfully');
      setShowDeleteModal(false);
      setSelectedUser(null);
      fetchUsers();
    } catch (err) {
      setError(err.message || 'Failed to delete user');
    }
  };

  const openEditModal = (user) => {
    setSelectedUser(user);
    setEditRole(user.role);
    setShowEditModal(true);
  };

  const openDeleteModal = (user) => {
    setSelectedUser(user);
    setShowDeleteModal(true);
  };

  const totalPages = Math.ceil(total / limit);

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-page p-6 transition-colors duration-300">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-primary mb-2">User Management</h1>
            <p className="text-secondary">Manage your team members and their roles</p>
          </div>
          
          {/* ซ่อนปุ่ม Add New User ถ้าไม่ใช่ Admin/Supervisor [แก้ไขบรรทัดที่ 159] */}
          {(currentUserRole === 'admin' || currentUserRole === 'supervisor') && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="w-full flex flex-row items-center justify-center md:w-auto px-6 py-3 btn-primary"
            >
              <HiPlus className="w-5 h-5 mr-2" />
              Add New User
            </button>
          )}
        </div>

        {/* ... Success/Error/Search เหมือนเดิม ... */}
        {success && <div className="bg-green-500/10 border border-green-500/20 text-green-600 px-4 py-3 rounded-lg">{success}</div>}
        {error && <div className="bg-red-500/10 border border-red-500/20 text-red-600 px-4 py-3 rounded-lg">{error}</div>}
        <div className="glass-card rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <HiSearch className="w-5 h-5 text-secondary" />
            <input
              type="text"
              placeholder="Search users..."
              className="flex-1 bg-transparent border-none text-primary focus:outline-none"
              onChange={(e) => {setSearchTerm(e.target.value); setPage(1);}}
            />
          </div>
        </div>

        {/* Users Table */}
        <div className="glass-card rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            {loading ? (
              <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div></div>
            ) : (
              <table className="w-full">
                <thead className="bg-black/5 dark:bg-white/5 border-b border-border-color">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-accent uppercase">Username</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-accent uppercase">Role</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-accent uppercase hidden md:table-cell">Created At</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-accent uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-color">
                  {users.map((user) => (
                    <tr key={user.username} className="hover:bg-black/5 transition duration-150">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 rounded-full bg-slate-500 flex items-center justify-center text-white font-semibold">
                            {user.username.charAt(0).toUpperCase()}
                          </div>
                          <div className="ml-4 text-sm font-medium text-primary">{user.username}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                          user.role === 'admin' ? 'bg-purple-500/10 text-yellow-500' : 
                          user.role === 'supervisor' ? 'bg-blue-500/10 text-blue-500' : 'bg-green-500/10 text-green-500'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-secondary hidden md:table-cell">{formatDate(user.created_at)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        
                        {/* แสดงปุ่ม Actions เฉพาะเมื่อมีสิทธิ์จัดการ User นั้นได้ [แก้ไขบรรทัดที่ 208] */}
                        {canManageUser(user) ? (
                          <div className="flex items-center space-x-3">
                            <button onClick={() => openEditModal(user)} className="text-blue-500 hover:text-blue-700"><HiPencilAlt className="w-5 h-5" /></button>
                            <button onClick={() => openDeleteModal(user)} className="text-red-500 hover:text-red-700"><HiTrash className="w-5 h-5" /></button>
                          </div>
                        ) : (
                          <span className="text-gray-400 italic text-xs">Read Only</span>
                        )}

                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
          {/* ... Pagination เหมือนเดิม ... */}
        </div>
      </div>

      {/* Create User Modal [เพิ่มฟิลด์ Role บรรทัดที่ 279] */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card bg-white dark:bg-slate-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h2 className="text-2xl font-bold text-primary mb-4">Create New User</h2>
            <form onSubmit={handleCreateUser}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary mb-2">Username</label>
                  <input type="text" value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} className="w-full px-4 py-2 glass-input rounded-lg" required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary mb-2">Password</label>
                  <div className="relative">
                    <input type={showPassword ? "text" : "password"} value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} className="w-full px-4 py-2 glass-input rounded-lg" required />
                    <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-2.5 text-gray-400">{showPassword ? <FiEyeOff /> : <FiEye />}</button>
                  </div>
                </div>

                {/* ส่วนที่เพิ่มใหม่: เลือก Role ตอนสร้าง User */}
                <div>
                  <label className="block text-sm font-medium text-secondary mb-2">Role</label>
                  <select 
                    value={formData.role} 
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })} 
                    className="w-full px-4 py-2 glass-input rounded-lg text-black"
                  >
                    {getAvailableRoles().map(role => (
                      <option key={role.value} value={role.value}>{role.label}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button type="button" onClick={() => setShowCreateModal(false)} className="px-4 py-2 bg-gray-100 rounded-lg">Cancel</button>
                <button type="submit" className="px-4 py-2 btn-primary">Create User</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Role Modal [แก้ไขตัวเลือก Role บรรทัดที่ 335] */}
      {showEditModal && selectedUser && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card bg-white dark:bg-slate-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h2 className="text-2xl font-bold text-primary mb-4">Update User Role</h2>
            <p className="text-secondary mb-4">User: <span className="font-semibold text-primary">{selectedUser.username}</span></p>
            <form onSubmit={handleUpdateRole}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary mb-2">Role</label>
                  <select
                    value={editRole}
                    onChange={(e) => setEditRole(e.target.value)}
                    className="w-full px-4 py-2 glass-input rounded-lg text-black"
                    required
                  >
                    {/* กรองตัวเลือก Role ตามสิทธิ์ผู้ใช้ปัจจุบัน */}
                    {getAvailableRoles().map(role => (
                      <option key={role.value} value={role.value}>{role.label}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button type="button" onClick={() => setShowEditModal(false)} className="px-4 py-2 bg-gray-100 rounded-lg">Cancel</button>
                <button type="submit" className="px-4 py-2 btn-primary">Update Role</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation [เหมือนเดิม] */}
      {showDeleteModal && selectedUser && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card bg-white dark:bg-slate-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h2 className="text-2xl font-bold text-primary mb-4">Delete User</h2>
            <p className="text-secondary mb-6">Are you sure you want to delete <span className="font-semibold">{selectedUser.username}</span>?</p>
            <div className="flex justify-end space-x-3">
              <button onClick={() => setShowDeleteModal(false)} className="px-4 py-2 bg-gray-100 rounded-lg">Cancel</button>
              <button onClick={handleDeleteUser} className="px-4 py-2 bg-red-500 text-white rounded-lg">Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}