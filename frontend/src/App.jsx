import { useState, useEffect } from 'react';
import { authUtils } from './utils/auth';
import LandingPage from './components/LandingPage';
import SignupPage from './components/Signup';
import LoginPage from './components/Login';
import DashboardPage from './components/Dashboard';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);

  // Check for existing session on app load
  useEffect(() => {
    if (authUtils.isAuthenticated()) {
      const savedToken = authUtils.getToken();
      const savedUsername = authUtils.getUser();
      
      setToken(savedToken);
      setUser(savedUsername);
      setCurrentPage('dashboard');
    }
  }, []);

  const handleNavigate = (page) => {
    setCurrentPage(page);
  };

  const handleLogin = (newToken, username) => {
    setToken(newToken);
    setUser(username);
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
  };

  return (
    <div className="font-sans">
      {currentPage === 'landing' && <LandingPage onNavigate={handleNavigate} />}
      {currentPage === 'signup' && <SignupPage onNavigate={handleNavigate} />}
      {currentPage === 'login' && <LoginPage onNavigate={handleNavigate} onLogin={handleLogin} />}
      {currentPage === 'dashboard' && <DashboardPage onNavigate={handleNavigate} user={user} onLogout={handleLogout} />}
    </div>
  );
}

export default App;