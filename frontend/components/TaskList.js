import React, { useEffect, useState } from 'react';
import api from '../utils/api';

const TaskList = ({ tasks, setTasks }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await api.get('/tasks');
      setTasks(response.data.data);
    } catch (err) {
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/tasks/${id}`);
      setTasks(tasks.filter(task => task.id !== id));
    } catch (err) {
      alert('Failed to delete task');
    }
  };

  const handleUpdateStatus = async (id, newStatus) => {
    try {
      await api.put(`/tasks/${id}`, { status: newStatus });
      setTasks(tasks.map(task => 
        task.id === id ? { ...task, status: newStatus } : task
      ));
    } catch (err) {
      alert('Failed to update task status');
    }
  };

  if (loading) return <div>Loading tasks...</div>;
  if (error) return <div className="alert-error">{error}</div>;

  return (
    <div className="card">
      <h3 className="section-title">Your Tasks</h3>
      {tasks.length === 0 ? (
        <p className="text-gray">No tasks yet.</p>
      ) : (
        <ul className="task-list">
          {tasks.map(task => (
            <li key={task.id} className="task-item">
              <div className="task-content">
                <h4>{task.title}</h4>
                <p>{task.description}</p>
                <span className={`badge ${task.status.toLowerCase()}`}>{task.status}</span>
              </div>
              <div className="task-actions">
                {task.status !== 'COMPLETED' && (
                  <button onClick={() => handleUpdateStatus(task.id, 'COMPLETED')} className="btn-success">
                    Complete
                  </button>
                )}
                <button onClick={() => handleDelete(task.id)} className="btn-danger">
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TaskList;
