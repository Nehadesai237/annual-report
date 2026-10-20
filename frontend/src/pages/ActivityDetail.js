import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiCalendar, FiTag, FiImage, FiCheckCircle, FiClock, FiXCircle, FiEdit, FiTrash2, FiDownload, FiEye, FiFileText, FiUser, FiAward, FiZap, FiUsers } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { api } from '../services/authService';
import { getImageUrl } from '../utils/imageUtils';

const ActivityDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [imageModal, setImageModal] = useState({ isOpen: false, image: null });
  const [groupMembersDetails, setGroupMembersDetails] = useState([]);

  useEffect(() => {
    if (id) {
      fetchActivity();
    }
  }, [id]);

  const fetchActivity = async () => {
    if (!id) {
      console.error('No activity ID provided');
      toast.error('Invalid activity ID');
      navigate('/activities');
      return;
    }
    
    try {
      setLoading(true);
      console.log('[ActivityDetail] Fetching activity with id:', id);
      console.log('[ActivityDetail] Current user:', user);
      
      const response = await api.get(`/api/v1/activities/${id}`);
      console.log('[ActivityDetail] Activity response:', response.data);
      console.log('[ActivityDetail] Activity images:', response.data?.images);
      
      if (response.data) {
        setActivity(response.data);
        // Fetch group members details if it's a group achievement
        if (response.data.achievement_type === 'group' && response.data.group_members && response.data.group_members.length > 0) {
          fetchGroupMembersDetails(response.data.group_members);
        }
      } else {
        throw new Error('No data in response');
      }
    } catch (error) {
      console.error('[ActivityDetail] Error fetching activity:', error);
      console.error('[ActivityDetail] Error status:', error.response?.status);
      console.error('[ActivityDetail] Error response data:', JSON.stringify(error.response?.data, null, 2));
      console.error('[ActivityDetail] Error message:', error.message);
      
      let errorMessage = 'Failed to fetch achievement details';
      
      if (error.response) {
        // Server responded with error
        errorMessage = error.response.data?.detail || 
                      error.response.data?.message || 
                      `Server error: ${error.response.status}`;
      } else if (error.request) {
        // Request made but no response
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        // Error setting up request
        errorMessage = error.message || 'Failed to fetch achievement details';
      }
      
      toast.error(errorMessage);
      
      // Don't navigate away immediately, let user see the error
      setTimeout(() => {
        navigate('/activities');
      }, 3000);
    } finally {
      setLoading(false);
    }
  };

  const getStatusInfo = (status) => {
    switch (status) {
      case 'accepted':
        return { 
          icon: FiCheckCircle, 
          color: 'bg-green-100 text-green-800 border-green-300', 
          borderColor: 'border-green-300', 
          bgColor: 'bg-green-50',
          gradient: 'from-green-500 to-emerald-600',
          badgeGradient: 'from-green-500 to-emerald-500'
        };
      case 'rejected':
        return { 
          icon: FiXCircle, 
          color: 'bg-red-100 text-red-800 border-red-300', 
          borderColor: 'border-red-300', 
          bgColor: 'bg-red-50',
          gradient: 'from-red-500 to-rose-600',
          badgeGradient: 'from-red-500 to-rose-500'
        };
      case 'pending':
        return { 
          icon: FiClock, 
          color: 'bg-yellow-100 text-yellow-800 border-yellow-300', 
          borderColor: 'border-yellow-300', 
          bgColor: 'bg-yellow-50',
          gradient: 'from-yellow-500 to-orange-600',
          badgeGradient: 'from-yellow-500 to-orange-500'
        };
      default:
        return { 
          icon: FiClock, 
          color: 'bg-gray-100 text-gray-800 border-gray-300', 
          borderColor: 'border-gray-300', 
          bgColor: 'bg-gray-50',
          gradient: 'from-gray-500 to-gray-600',
          badgeGradient: 'from-gray-500 to-gray-500'
        };
    }
  };

  const getTypeColor = (type) => {
    const colors = {
      social: { bg: 'bg-gradient-to-r from-orange-500 to-red-600', text: 'text-white', badge: 'from-orange-500 to-red-500' },
      sports: { bg: 'bg-gradient-to-r from-green-500 to-emerald-600', text: 'text-white', badge: 'from-green-500 to-emerald-500' },
      academic: { bg: 'bg-gradient-to-r from-purple-500 to-indigo-600', text: 'text-white', badge: 'from-purple-500 to-indigo-500' },
      cultural: { bg: 'bg-gradient-to-r from-pink-500 to-rose-600', text: 'text-white', badge: 'from-pink-500 to-rose-500' },
      technical: { bg: 'bg-gradient-to-r from-blue-500 to-indigo-600', text: 'text-white', badge: 'from-blue-500 to-indigo-500' }
    };
    return colors[type] || { bg: 'bg-gradient-to-r from-gray-500 to-gray-600', text: 'text-white', badge: 'from-gray-500 to-gray-500' };
  };

  const handleDelete = async () => {
    try {
      await api.delete(`/api/v1/activities/${id}`);
      toast.success('Achievement deleted successfully');
      navigate('/activities');
    } catch (error) {
      console.error('Error deleting activity:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete achievement');
    }
  };

  const handleEdit = () => {
    navigate(`/activities/${id}/edit`);
  };

  const openImageModal = (image) => {
    setImageModal({ isOpen: true, image });
  };

  const closeImageModal = () => {
    setImageModal({ isOpen: false, image: null });
  };

  const fetchGroupMembersDetails = async (memberIds) => {
    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('token');
      
      if (!token) return;
      
      const memberPromises = memberIds.map(async (memberId) => {
        try {
          const response = await api.get(`/api/v1/users/${memberId}`);
          return response.data;
        } catch (error) {
          console.error(`Error fetching user ${memberId}:`, error);
          return { id: memberId, name: 'Unknown User', department: 'N/A' };
        }
      });
      
      const members = await Promise.all(memberPromises);
      setGroupMembersDetails(members);
    } catch (error) {
      console.error('Error fetching group members:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/30">
        <div className="text-center">
          <div className="spinner mb-4"></div>
          <p className="text-gray-600 font-semibold text-lg">Loading achievement details...</p>
        </div>
      </div>
    );
  }

  if (!activity) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/30">
        <div className="text-center bg-white rounded-2xl shadow-2xl p-12 max-w-md border-2 border-gray-100">
          <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-red-100 to-rose-100 rounded-full flex items-center justify-center">
            <FiXCircle className="h-10 w-10 text-red-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Achievement Not Found</h2>
          <p className="text-gray-600 mb-8 leading-relaxed">
            The achievement you're looking for doesn't exist or you don't have permission to view it.
          </p>
          <button
            onClick={() => navigate('/activities')}
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
          >
            Back to Achievements
          </button>
        </div>
      </div>
    );
  }

  const statusInfo = getStatusInfo(activity.status);
  const StatusIcon = statusInfo.icon;
  const typeColor = getTypeColor(activity.type);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Modern Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/activities')}
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-6 transition-colors font-bold group"
          >
            <FiArrowLeft className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" />
            Back to Achievements
          </button>
          
          <div className="bg-white rounded-2xl shadow-xl border-2 border-gray-100 p-6 lg:p-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-4 flex-wrap">
                  <span className={`inline-flex items-center px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wide border-2 shadow-md ${statusInfo.color}`}>
                    <StatusIcon className="h-4 w-4 mr-2" />
                    {activity.status}
                  </span>
                  <span className={`inline-flex items-center px-4 py-2 rounded-full text-xs font-bold ${typeColor.bg} ${typeColor.text} shadow-md`}>
                    {activity.type}
                  </span>
                  {activity.achievement_type === 'group' ? (
                    <span className="inline-flex items-center px-4 py-2 rounded-full text-xs font-bold text-white bg-gradient-to-r from-purple-500 to-pink-600 shadow-md">
                      <FiUsers className="h-4 w-4 mr-2" />
                      Group Achievement
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-4 py-2 rounded-full text-xs font-bold text-white bg-gradient-to-r from-blue-500 to-indigo-600 shadow-md">
                      <FiUser className="h-4 w-4 mr-2" />
                      Individual Achievement
                    </span>
                  )}
                </div>
                <h1 className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                  {activity.title}
                </h1>
                <p className="text-gray-600 text-lg leading-relaxed">{activity.description}</p>
              </div>
              
              {/* Action Buttons */}
              {activity.status !== 'accepted' && (
                <div className="flex gap-3 flex-shrink-0">
                  <button
                    onClick={handleEdit}
                    className="inline-flex items-center px-6 py-3 bg-white border-2 border-blue-600 text-blue-600 font-bold rounded-xl shadow-lg hover:shadow-xl hover:bg-gradient-to-r hover:from-blue-600 hover:to-indigo-600 hover:text-white transition-all duration-200 transform hover:scale-105"
                  >
                    <FiEdit className="h-5 w-5 mr-2" />
                    Edit
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(true)}
                    className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-red-600 to-rose-600 text-white font-bold rounded-xl shadow-lg hover:shadow-xl hover:from-red-700 hover:to-rose-700 transition-all duration-200 transform hover:scale-105"
                  >
                    <FiTrash2 className="h-5 w-5 mr-2" />
                    Delete
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
          {/* Left Column - Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Images Gallery */}
            {activity.images && activity.images.length > 0 && (
              <div className="bg-white rounded-2xl shadow-xl border-2 border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
                  <h2 className="text-xl font-bold text-white flex items-center">
                    <FiImage className="h-6 w-6 mr-3" />
                    Achievement Photos ({activity.images.length})
                  </h2>
                </div>
                <div className="p-6">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {activity.images.map((image, index) => {
                      const imageUrl = getImageUrl(image);
                      return (
                        <div key={index} className="relative group">
                          <div className="aspect-square rounded-xl overflow-hidden bg-gray-100 border-2 border-gray-200 shadow-md hover:shadow-2xl transition-all duration-300 cursor-pointer transform hover:scale-105">
                            <img
                              src={imageUrl}
                              alt={`Achievement photo ${index + 1}`}
                              className="w-full h-full object-cover"
                              onClick={() => openImageModal(image)}
                              onError={(e) => {
                                console.error('Image load error:', imageUrl, image);
                                e.target.src = '/placeholder.jpg';
                              }}
                            />
                          </div>
                          {image.verdict && (
                            <div className={`absolute top-2 right-2 px-3 py-1.5 rounded-lg text-xs font-bold shadow-lg ${
                              image.verdict === 'normal' 
                                ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white' 
                                : 'bg-gradient-to-r from-red-500 to-rose-500 text-white'
                            }`}>
                              {image.verdict === 'normal' ? '✓ Verified' : '⚠ Unverified'}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Certificate Section */}
            {activity.has_certificate && activity.certificate_path && (
              <div className="bg-white rounded-2xl shadow-xl border-2 border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-yellow-500 to-orange-500 px-6 py-4">
                  <h2 className="text-xl font-bold text-white flex items-center">
                    <FiAward className="h-6 w-6 mr-3" />
                    Certificate
                    {activity.certificate_validated && (
                      <span className="ml-3 px-3 py-1 bg-white/20 backdrop-blur-sm text-white rounded-full text-xs font-bold border-2 border-white/30">
                        ✓ Verified
                      </span>
                    )}
                  </h2>
                </div>
                <div className="p-6">
                  <div className="flex items-center justify-between p-6 bg-gradient-to-r from-yellow-50 to-amber-50 rounded-xl border-2 border-yellow-200 mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center shadow-lg">
                        <FiFileText className="h-8 w-8 text-white" />
                      </div>
                      <div>
                        <p className="font-bold text-gray-900 text-lg">Official Certificate</p>
                        <p className="text-sm text-gray-600">Click to view or download</p>
                      </div>
                    </div>
                    <a
                      href={getImageUrl(activity.certificate_path)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-yellow-600 to-orange-600 text-white font-bold rounded-xl hover:from-yellow-700 hover:to-orange-700 transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
                    >
                      <FiDownload className="h-5 w-5 mr-2" />
                      Download
                    </a>
                  </div>
                  <div className="rounded-xl overflow-hidden border-2 border-gray-200 shadow-lg">
                    <a
                      href={getImageUrl(activity.certificate_path)}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <img
                        src={getImageUrl(activity.certificate_path)}
                        alt="Certificate"
                        className="w-full h-auto cursor-pointer hover:opacity-90 transition-opacity"
                      />
                    </a>
                  </div>
                </div>
              </div>
            )}

            {/* ML Analysis */}
            {activity.ml_analysis && (
              <div className="bg-white rounded-2xl shadow-xl border-2 border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
                  <h2 className="text-xl font-bold text-white flex items-center">
                    <FiZap className="h-6 w-6 mr-3" />
                    AI Verification Analysis
                  </h2>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200">
                      <span className="text-gray-700 font-bold text-lg">Confidence Score:</span>
                      <span className="text-blue-600 font-bold text-2xl">
                        {Math.round(activity.ml_analysis.confidence * 100)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center p-5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200">
                      <span className="text-gray-700 font-bold text-lg">AI Prediction:</span>
                      <span className="text-blue-600 font-bold text-xl capitalize">{activity.ml_analysis.prediction}</span>
                    </div>
                    <div className="flex justify-between items-center p-5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200">
                      <span className="text-gray-700 font-bold text-lg">Verification Status:</span>
                      <span className={`font-bold text-xl ${activity.ml_analysis.verified ? 'text-green-600' : 'text-red-600'}`}>
                        {activity.ml_analysis.verified ? '✓ Verified' : '✗ Not Verified'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Admin Comments */}
            {activity.admin_comments && (
              <div className="bg-white rounded-2xl shadow-xl border-2 border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4">
                  <h2 className="text-xl font-bold text-white flex items-center">
                    <FiUser className="h-6 w-6 mr-3" />
                    Admin Feedback
                  </h2>
                </div>
                <div className="p-6">
                  <div className={`p-6 ${statusInfo.bgColor} rounded-xl border-2 ${statusInfo.borderColor} shadow-md`}>
                    <p className="text-gray-800 leading-relaxed text-base font-medium">{activity.admin_comments}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Sidebar */}
          <div className="space-y-6">
            {/* Details Card */}
            <div className="bg-white rounded-2xl shadow-xl border-2 border-gray-100 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
                <h3 className="text-xl font-bold text-white">Details</h3>
              </div>
              <div className="p-6">
                <div className="space-y-5">
                  <div className="flex items-start space-x-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                      <FiCalendar className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-500 uppercase tracking-wide font-bold mb-1">Created</p>
                      <p className="font-bold text-gray-900">
                        {new Date(activity.created_at).toLocaleDateString('en-US', { 
                          month: 'long', 
                          day: 'numeric', 
                          year: 'numeric' 
                        })}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                      <FiTag className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-500 uppercase tracking-wide font-bold mb-1">Department</p>
                      <p className="font-bold text-gray-900">{activity.department}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                      <FiCalendar className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-500 uppercase tracking-wide font-bold mb-1">Year</p>
                      <p className="font-bold text-gray-900">{activity.year}</p>
                    </div>
                  </div>

                  {activity.images && activity.images.length > 0 && (
                    <div className="flex items-start space-x-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
                      <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                        <FiImage className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-gray-500 uppercase tracking-wide font-bold mb-1">Total Images</p>
                        <p className="font-bold text-gray-900">{activity.images.length}</p>
                      </div>
                    </div>
                  )}

                  {activity.achievement_type === 'group' && (
                    <div className="flex items-start space-x-4 p-4 bg-purple-50 rounded-xl border-2 border-purple-200">
                      <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                        <FiUsers className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-gray-500 uppercase tracking-wide font-bold mb-2">Team Members</p>
                        {groupMembersDetails.length > 0 ? (
                          <div className="space-y-2">
                            {groupMembersDetails.map((member) => (
                              <div key={member.id} className="flex items-center p-2 bg-white rounded-lg border border-purple-100">
                                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3 flex-shrink-0">
                                  {member.name?.charAt(0) || 'U'}
                                </div>
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-semibold text-gray-900 truncate">{member.name || 'Unknown User'}</p>
                                  <p className="text-xs text-gray-600 truncate">{member.department || 'N/A'}</p>
                                </div>
                              </div>
                            ))}
                            <div className="flex items-center p-2 bg-white rounded-lg border border-purple-100">
                              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3 flex-shrink-0">
                                {activity.user_name?.charAt(0) || 'U'}
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-semibold text-gray-900 truncate">{activity.user_name || 'Creator'}</p>
                                <p className="text-xs text-gray-600 truncate">{activity.department || 'N/A'} • Creator</p>
                              </div>
                            </div>
                          </div>
                        ) : activity.group_members && activity.group_members.length > 0 ? (
                          <p className="text-sm text-gray-600">Loading team members...</p>
                        ) : (
                          <p className="text-sm text-gray-600">No team members added</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Status Timeline */}
            <div className="bg-white rounded-2xl shadow-xl border-2 border-gray-100 overflow-hidden">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
                <h3 className="text-xl font-bold text-white">Status Timeline</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-4 h-4 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full shadow-md"></div>
                      <div className="w-0.5 h-8 bg-gradient-to-b from-blue-500 to-indigo-600 ml-1.5"></div>
                    </div>
                    <div className="flex-1 pb-4">
                      <p className="text-sm font-bold text-gray-900 mb-1">Submitted</p>
                      <p className="text-xs text-gray-500">
                        {new Date(activity.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  {activity.ml_checked_at && (
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0 mt-1">
                        <div className="w-4 h-4 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full shadow-md"></div>
                        {activity.admin_reviewed_at && (
                          <div className="w-0.5 h-8 bg-gradient-to-b from-indigo-500 to-purple-600 ml-1.5"></div>
                        )}
                      </div>
                      <div className="flex-1 pb-4">
                        <p className="text-sm font-bold text-gray-900 mb-1">ML Verified</p>
                        <p className="text-xs text-gray-500">
                          {new Date(activity.ml_checked_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  )}
                  {activity.admin_reviewed_at && (
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0 mt-1">
                        <div className={`w-4 h-4 rounded-full shadow-md bg-gradient-to-br ${
                          activity.status === 'accepted' ? 'from-green-500 to-emerald-600' : 
                          activity.status === 'rejected' ? 'from-red-500 to-rose-600' : 
                          'from-yellow-500 to-orange-600'
                        }`}></div>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-bold text-gray-900 mb-1">Admin Reviewed</p>
                        <p className="text-xs text-gray-500">
                          {new Date(activity.admin_reviewed_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Image Modal */}
      {imageModal.isOpen && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4" 
          onClick={closeImageModal}
        >
          <div className="relative max-w-5xl max-h-[90vh] w-full" onClick={(e) => e.stopPropagation()}>
            <img
              src={getImageUrl(imageModal.image)}
              alt="Full size"
              className="max-w-full max-h-[90vh] rounded-2xl shadow-2xl mx-auto"
            />
            <button
              onClick={closeImageModal}
              className="absolute top-4 right-4 bg-white rounded-full p-3 shadow-2xl hover:bg-gray-100 transition-all transform hover:scale-110"
            >
              <FiXCircle className="w-6 h-6 text-gray-600" />
            </button>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" 
          onClick={() => setShowDeleteConfirm(false)}
        >
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full border-2 border-gray-100" onClick={(e) => e.stopPropagation()}>
            <div className="w-16 h-16 mx-auto mb-6 bg-gradient-to-br from-red-100 to-rose-100 rounded-full flex items-center justify-center">
              <FiTrash2 className="h-8 w-8 text-red-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3 text-center">Confirm Deletion</h3>
            <p className="text-gray-600 mb-8 text-center leading-relaxed">
              Are you sure you want to delete this achievement? This action cannot be undone.
            </p>
            <div className="flex space-x-4">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 px-6 py-3 bg-gray-200 text-gray-800 font-bold rounded-xl hover:bg-gray-300 transition-all transform hover:scale-105"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowDeleteConfirm(false);
                  handleDelete();
                }}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-red-600 to-rose-600 text-white font-bold rounded-xl hover:from-red-700 hover:to-rose-700 transition-all transform hover:scale-105 shadow-lg"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityDetail;
