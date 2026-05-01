import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import TaskList from '../components/TaskList';
import TaskForm from '../components/TaskForm';
import TradeForm from '../components/TradeForm';
import { jwtDecode } from 'jwt-decode';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    
    try {
      const decoded = jwtDecode(token);
      setUser(decoded);
    } catch (err) {
      localStorage.removeItem('token');
      router.push('/login');
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  const handleTaskAdded = (newTask) => {
    setTasks((prev) => [newTask, ...prev]);
  };

  if (!user) return <div className="loading">Loading dashboard...</div>;

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-container">
          <h1 className="logo">System Dashboard</h1>
          <div className="nav-right">
            <span className="user-info">{user.sub || 'User'}</span>
            <button onClick={handleLogout} className="btn-secondary">Logout</button>
          </div>
        </div>
      </nav>

      <main className="main-content">
        <div className="grid-layout">
          <div className="col-left">
            <TaskForm onTaskAdded={handleTaskAdded} />
            <TaskList tasks={tasks} setTasks={setTasks} />
          </div>
          <div className="col-right">
            <TradeForm />
          </div>
        </div>
      </main>
    </div>
  );
}
