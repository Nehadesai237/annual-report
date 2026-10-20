import React, { useState, useEffect, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FiPlus, FiEye, FiEdit, FiTrash2, FiSearch, FiFilter, FiCalendar, FiTag, FiImage, FiCheckCircle, FiClock, FiXCircle, FiArrowRight, FiUsers, FiUser } from 'react-icons/fi';
import { api } from '../services/authService';
import toast from 'react-hot-toast';

const Activities = () => {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    type: '',
    status: '',
    year: '',
    search: ''
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showFilters, setShowFilters] = useState(false);

  const loadActivities = useCallback(async () => {
    if (!user?.id) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      
      // Filter out empty values from filters
      const cleanedFilters = Object.entries(filters).reduce((acc, [key, value]) => {
        if (value && value.trim() !== '') {
          acc[key] = value;
        }
        return acc;
      }, {});
      
      const params = new URLSearchParams({
        page: currentPage,
        size: 10,
        ...cleanedFilters
      });
      
      const response = await api.get(`/api/v1/activities?${params}`);
      
      // Filter out admin-created activities (events)
      // Include activities where user is the creator OR user is a group member
      const studentActivities = (response.data.activities || []).filter(
        activity => {
          if (activity.is_admin_created) return false;
          // User is the creator
          if (activity.user_id === user?.id) return true;
          // User is a group member
          if (activity.achievement_type === 'group' && 
              Array.isArray(activity.group_members) && 
              activity.group_members.includes(user?.id)) {
            return true;
          }
          return false;
        }
      );
      setActivities(studentActivities);
      setTotalPages(response.data.pages || 1);
    } catch (error) {
      console.error('Error loading activities:', error);
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        localStorage.removeItem('token');
        window.location.href = '/login';
      } else if (error.response?.status !== 401) {
        toast.error('Failed to load activities. Please try again.');
      }
      setActivities([]);
    } finally {
      setLoading(false);
    }
  }, [currentPage, filters, user?.id]);

  useEffect(() => {
    if (user?.id) {
      loadActivities();
    }
  }, [loadActivities, location.pathname, user?.id]);

  // Reload when component becomes visible (e.g., when navigating back from another page)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && user?.id) {
        loadActivities();
      }
    };

    const handleFocus = () => {
      if (user?.id) {
        loadActivities();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, [loadActivities, user?.id]);

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
    setCurrentPage(1);
  };

  const handleSearch = (e) => {
    setFilters({
      ...filters,
      search: e.target.value
    });
    setCurrentPage(1);
  };

  const deleteActivity = async (activityId) => {
    if (!window.confirm('Are you sure you want to delete this activity?')) {
      return;
    }

    try {
      await api.delete(`/api/v1/activities/${activityId}`);
      toast.success('Activity deleted successfully');
      loadActivities();
    } catch (error) {
      console.error('Error deleting activity:', error);
      const message = error.response?.data?.detail || 'Failed to delete activity';
      toast.error(message);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'status-pending',
      accepted: 'status-accepted',
      rejected: 'status-rejected'
    };
    return colors[status] || 'status-pending';
  };

  const getTypeColor = (type) => {
    const colors = {
      social: 'type-social',
      sports: 'type-sports',
      academic: 'type-academic',
      cultural: 'type-cultural',
      technical: 'type-technical'
    };
    return colors[type] || 'type-social';
  };

  const getStatusInfo = (status) => {
    switch (status) {
      case 'accepted':
        return { icon: FiCheckCircle, color: 'bg-green-100 text-green-800 border-green-200', bgColor: 'bg-green-50', textColor: 'text-green-700' };
      case 'rejected':
        return { icon: FiXCircle, color: 'bg-red-100 text-red-800 border-red-200', bgColor: 'bg-red-50', textColor: 'text-red-700' };
      case 'pending':
        return { icon: FiClock, color: 'bg-yellow-100 text-yellow-800 border-yellow-200', bgColor: 'bg-yellow-50', textColor: 'text-yellow-700' };
      default:
        return { icon: FiClock, color: 'bg-gray-100 text-gray-800 border-gray-200', bgColor: 'bg-gray-50', textColor: 'text-gray-700' };
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="text-center">
          <div className="spinner mb-4"></div>
          <p className="text-gray-600">Loading achievements...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        {/* Modern Header */}
        <div className="mb-8 lg:mb-12">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <div className="inline-block mb-4 px-4 py-2 bg-blue-100 rounded-full">
                <span className="text-sm font-semibold text-blue-700">My Portfolio</span>
              </div>
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-3">
                My <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Achievements</span>
              </h1>
              <p className="text-lg text-gray-600 max-w-2xl">
                Track and manage your accomplishments and their review status
              </p>
            </div>
            <Link
              to="/activities/create"
              className="inline-flex items-center px-6 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
            >
              <FiPlus className="h-5 w-5 mr-2" />
              Share New Achievement
            </Link>
          </div>
        </div>

        {/* Search and Filter Bar */}
        <div className="mb-6 flex flex-col md:flex-row gap-4">
          {/* Search Bar */}
          <div className="flex-1">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <FiSearch className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="w-full pl-12 pr-4 py-3.5 border-2 border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white"
                placeholder="Search your achievements..."
                value={filters.search}
                onChange={handleSearch}
              />
            </div>
          </div>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center justify-center px-5 py-3.5 bg-white border-2 border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:border-blue-300 transition-all text-gray-700 font-semibold"
          >
            <FiFilter className="h-5 w-5 mr-2" />
            Filters
            {Object.values(filters).filter(v => v && v !== filters.search).length > 0 && (
              <span className="ml-2 px-2.5 py-1 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-full text-xs font-bold">
                {Object.values(filters).filter(v => v && v !== filters.search).length}
              </span>
            )}
          </button>
        </div>

        {/* Collapsible Filters */}
        {showFilters && (
          <div className="mb-6 bg-white rounded-2xl shadow-lg p-6 lg:p-8 border border-gray-100 animate-in slide-in-from-top">
            <div className="flex items-center mb-6">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-2 rounded-lg mr-3">
                <FiFilter className="h-5 w-5 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Filter Achievements</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Category</label>
                <select
                  name="type"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white font-medium"
                  value={filters.type}
                  onChange={handleFilterChange}
                >
                  <option value="">All Categories</option>
                  <option value="academic">Academic Excellence</option>
                  <option value="technical">Technical Innovation</option>
                  <option value="cultural">Cultural & Arts</option>
                  <option value="sports">Sports & Fitness</option>
                  <option value="social">Social Service</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Status</label>
                <select
                  name="status"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white font-medium"
                  value={filters.status}
                  onChange={handleFilterChange}
                >
                  <option value="">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="accepted">Accepted</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Year</label>
                <select
                  name="year"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white font-medium"
                  value={filters.year}
                  onChange={handleFilterChange}
                >
                  <option value="">All Years</option>
                  <option value="2024">2024</option>
                  <option value="2023">2023</option>
                  <option value="2022">2022</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Activities Grid */}
        {activities.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {activities.map((activity) => {
              const statusInfo = getStatusInfo(activity.status);
              const StatusIcon = statusInfo.icon;
              
              const getTypeGradient = (type) => {
                const gradients = {
                  academic: 'from-purple-500 to-purple-600',
                  technical: 'from-blue-500 to-indigo-600',
                  cultural: 'from-pink-500 to-rose-600',
                  sports: 'from-green-500 to-emerald-600',
                  social: 'from-orange-500 to-red-600'
                };
                return gradients[type] || 'from-gray-500 to-gray-600';
              };
              
              return (
                <div
                  key={activity.id}
                  className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden border-2 border-gray-100 hover:border-blue-200 cursor-pointer group transform hover:-translate-y-1"
                  onClick={() => navigate(`/activities/${activity.id}`)}
                >
                  {/* Card Header with Gradient */}
                  <div className={`h-1.5 bg-gradient-to-r ${getTypeGradient(activity.type)}`}></div>
                  
                  <div className="p-6">
                    {/* Status and Type Badges */}
                    <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wide ${statusInfo.color} border-2 shadow-sm`}>
                          <StatusIcon className="h-3.5 w-3.5 mr-1.5" />
                          {activity.status}
                        </span>
                        {activity.achievement_type === 'group' ? (
                          <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold text-white bg-gradient-to-r from-purple-500 to-pink-600 shadow-md">
                            <FiUsers className="h-3.5 w-3.5 mr-1.5" />
                            Group Achievement
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold text-white bg-gradient-to-r from-blue-500 to-indigo-600 shadow-md">
                            <FiUser className="h-3.5 w-3.5 mr-1.5" />
                            Individual Achievement
                          </span>
                        )}
                      </div>
                      <span className={`px-3 py-1.5 rounded-full text-xs font-bold text-white bg-gradient-to-r ${getTypeGradient(activity.type)} shadow-md`}>
                        {activity.type}
                      </span>
                    </div>
                    
                    {/* Posted By / Group Info */}
                    {activity.achievement_type === 'group' && (
                      <div className="mb-4 p-3 bg-purple-50 rounded-xl border border-purple-200">
                        {activity.user_id === user?.id ? (
                          <div className="flex items-center text-sm text-purple-800">
                            <FiUser className="h-4 w-4 mr-2" />
                            <span className="font-semibold">You posted this group achievement</span>
                          </div>
                        ) : (
                          <div className="flex items-center text-sm text-purple-800">
                            <FiUser className="h-4 w-4 mr-2" />
                            <span className="font-semibold">Posted by: {activity.created_by_name || 'Team Member'}</span>
                          </div>
                        )}
                        {activity.group_members && activity.group_members.length > 0 && (
                          <div className="mt-2 pt-2 border-t border-purple-200">
                            <div className="flex items-center text-xs text-purple-700">
                              <FiUsers className="h-3.5 w-3.5 mr-1.5" />
                              <span className="font-medium">
                                {activity.group_members.length + 1} team member{activity.group_members.length !== 0 ? 's' : ''}
                              </span>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Title */}
                    <h3 className="text-xl font-bold text-gray-900 mb-3 line-clamp-2 group-hover:text-blue-600 transition-colors leading-tight">
                      {activity.title}
                    </h3>
                    
                    {/* Description */}
                    <p className="text-gray-600 text-sm mb-5 line-clamp-3 leading-relaxed">
                      {activity.description}
                    </p>
                    
                    {/* Metadata */}
                    <div className="space-y-2.5 mb-5">
                      <div className="flex items-center text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded-lg">
                        <FiCalendar className="h-4 w-4 mr-2 text-blue-600" />
                        <span className="font-medium">{new Date(activity.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                      </div>
                      <div className="flex items-center text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded-lg">
                        <FiTag className="h-4 w-4 mr-2 text-blue-600" />
                        <span className="font-medium">{activity.department} • Year {activity.year}</span>
                      </div>
                      {activity.images?.length > 0 && (
                        <div className="flex items-center text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded-lg">
                          <FiImage className="h-4 w-4 mr-2 text-blue-600" />
                          <span className="font-medium">{activity.images.length} Image{activity.images.length !== 1 ? 's' : ''}</span>
                        </div>
                      )}
                    </div>
                    
                    {/* Admin Comments */}
                    {activity.admin_comments && (
                      <div className={`mb-5 p-4 rounded-xl border-2 ${statusInfo.bgColor} ${statusInfo.color.includes('green') ? 'border-green-200' : statusInfo.color.includes('red') ? 'border-red-200' : 'border-yellow-200'}`}>
                        <p className="text-xs font-bold uppercase tracking-wide mb-2 text-gray-700">Admin Comments</p>
                        <p className="text-sm text-gray-700 leading-relaxed">{activity.admin_comments}</p>
                      </div>
                    )}
                    
                    {/* View Button */}
                    <div className="pt-4 border-t border-gray-200">
                      <div className="flex items-center justify-between">
                        <span className="text-blue-600 font-bold text-sm group-hover:text-blue-700 transition-colors">
                          View Details
                        </span>
                        <FiArrowRight className="h-5 w-5 text-blue-600 transform group-hover:translate-x-1 transition-transform" />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-xl p-12 lg:p-16 text-center border border-gray-100">
            <div className="max-w-md mx-auto">
              <div className="w-28 h-28 mx-auto mb-8 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center shadow-lg">
                <FiPlus className="h-14 w-14 text-blue-600" />
              </div>
              <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-3">No achievements yet</h3>
              <p className="text-gray-600 mb-10 text-lg leading-relaxed">
                Start showcasing your accomplishments by sharing your first achievement
              </p>
              <Link
                to="/activities/create"
                className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
              >
                <FiPlus className="h-5 w-5 mr-2" />
                Create First Achievement
              </Link>
            </div>
          </div>
        )}

        {/* Modern Pagination */}
        {totalPages > 1 && (
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="text-sm font-semibold text-gray-700">
                Page <span className="font-bold text-blue-600 text-lg">{currentPage}</span> of <span className="font-bold text-lg">{totalPages}</span>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="px-6 py-2.5 text-sm font-semibold text-gray-700 bg-white border-2 border-gray-300 rounded-xl hover:bg-gray-50 hover:border-blue-500 hover:text-blue-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:border-gray-300 disabled:hover:text-gray-700"
                >
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className="px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 rounded-xl shadow-md hover:shadow-lg transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Activities;
