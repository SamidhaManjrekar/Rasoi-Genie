import { useState, useEffect } from 'react';
import {
  ChefHat,
  Calendar,
  Utensils,
  ShoppingCart,
  Star,
  CheckCircle,
  Loader2,
  Settings,
} from 'lucide-react';
import { apiService } from '../services/api';
import { authUtils } from '../utils/auth';

function DashboardPage({ onNavigate, user, onLogout }) {
  const [loading, setLoading] = useState(true);
  const [protectedData, setProtectedData] = useState(null);
  const [hasPreferences, setHasPreferences] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = authUtils.getToken();
        if (token) {
          try {
            const data = await apiService.getProtectedData(token);
            setProtectedData(data);
          } catch (err) {
            console.log('Protected endpoint not available yet');
          }

          try {
            const preferences = await apiService.getPreferences(token);
            setHasPreferences(!!preferences);
          } catch (err) {
            setHasPreferences(false);
          }
        }
      } catch (err) {
        console.error('Failed to fetch data:', err);
        handleLogout();
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleLogout = () => {
    authUtils.clearAuth();
    onLogout();
    onNavigate('landing');
  };

  const handleSetupPreferences = () => {
    onNavigate('preferences');
  };

  const handleUpdatePreferences = () => {
    onNavigate('preferences', { isUpdate: true });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-orange-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <ChefHat className="h-8 w-8 text-orange-600" />
              <span className="text-2xl font-bold text-gray-800">MealPlanner</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">Welcome, {user}!</span>
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-red-600 font-medium transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Welcome back, {user}!</h1>
          <p className="text-xl text-gray-600 mb-8">Ready to plan some delicious meals?</p>

          {/* Status Card */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-8">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-green-800 font-medium">
                Successfully logged in! Your meal planning journey starts here.
              </span>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer">
              <Calendar className="h-12 w-12 text-orange-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Generate Menu</h3>
              <p className="text-gray-600 mb-4">Create your personalized weekly meal plan</p>
              <button className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors">
                Get Started
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer">
              <Utensils className="h-12 w-12 text-green-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">My Preferences</h3>
              <p className="text-gray-600 mb-4">
                {hasPreferences
                  ? 'Update your dietary preferences'
                  : 'Set up your dietary preferences'}
              </p>
              <button
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                onClick={hasPreferences ? handleUpdatePreferences : handleSetupPreferences}
              >
                {hasPreferences ? 'Update' : 'Set Up'}
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer">
              <ShoppingCart className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Grocery List</h3>
              <p className="text-gray-600 mb-4">View and download shopping list</p>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                View List
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer">
              <Star className="h-12 w-12 text-yellow-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Favorites</h3>
              <p className="text-gray-600 mb-4">Your saved recipes and meals</p>
              <button className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition-colors">
                View All
              </button>
            </div>
          </div>

          {/* Coming Soon Features */}
          <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Coming Soon Features</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
                <span className="text-gray-700">AI-powered menu generation</span>
              </div>
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
                <span className="text-gray-700">Recipe video recommendations</span>
              </div>
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
                <span className="text-gray-700">Nutritional analysis</span>
              </div>
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
                <span className="text-gray-700">Smart grocery optimization</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default DashboardPage;
