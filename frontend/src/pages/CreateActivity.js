import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FiUpload, FiX, FiFileText, FiLoader, FiArrowLeft, FiImage, FiAward, FiUsers, FiSearch, FiPlus, FiInfo, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import axios from 'axios';
import toast from 'react-hot-toast';

const CreateActivity = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'academic',
    year: new Date().getFullYear(),
    achievementType: 'individual',
    hasCertificate: false
  });
  const [files, setFiles] = useState([]);
  const [certificate, setCertificate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  
  // Group achievement state
  const [groupMembers, setGroupMembers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const searchTimeoutRef = useRef(null);
  const searchRef = useRef(null);

  const steps = [
    { id: 1, title: 'Basic Info', icon: FiFileText },
    { id: 2, title: 'Type', icon: FiUsers },
    { id: 3, title: 'Files', icon: FiImage },
    { id: 4, title: 'Review', icon: FiCheckCircle }
  ];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleFileSelect = (selectedFiles) => {
    const newFiles = Array.from(selectedFiles).filter(file => {
      if (!file.type.startsWith('image/')) {
        toast.error(`${file.name} is not an image file`);
        return false;
      }
      if (file.size > 10 * 1024 * 1024) {
        toast.error(`${file.name} is too large (max 10MB)`);
        return false;
      }
      return true;
    });

    setFiles(prev => [...prev, ...newFiles]);
  };

  const handleCertificateSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const isImage = file.type.startsWith('image/');
    const isPdf = file.type === 'application/pdf';

    if (!isImage && !isPdf) {
      toast.error('Certificate must be an image or PDF file');
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      toast.error('Certificate file is too large (max 15MB)');
      return;
    }

    setCertificate(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragActive(false);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const removeCertificate = () => {
    setCertificate(null);
  };

  // Load all students when component mounts or when achievement type changes to group
  useEffect(() => {
    if (formData.achievementType === 'group' && allUsers.length === 0) {
      loadAllStudents();
    }
  }, [formData.achievementType]);

  const loadAllStudents = async () => {
    try {
      setLoadingUsers(true);
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('token');
      
      if (!token) {
        console.error('No authentication token found');
        return;
      }
      
      const response = await axios.get(`${API_BASE_URL}/api/v1/users/all-students`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Filter out current user and ensure we have valid user objects
      const filtered = (response.data || []).filter(u => u && u.id && u.id !== user?.id);
      setAllUsers(filtered);
    } catch (error) {
      console.error('Error loading students:', error);
      if (error.response?.status !== 401) {
        toast.error('Failed to load students. Please try again.');
      }
    } finally {
      setLoadingUsers(false);
    }
  };

  // Filter users based on search query
  const handleSearchUsers = (query) => {
    if (!query || query.trim().length === 0) {
      setSearchResults([]);
      return;
    }

    const queryLower = query.toLowerCase().trim();
    
    // Filter allUsers based on name, email, or student_id
    const filtered = allUsers.filter(u => {
      const nameMatch = u.name?.toLowerCase().includes(queryLower);
      const emailMatch = u.email?.toLowerCase().includes(queryLower);
      const studentIdMatch = u.student_id?.toLowerCase().includes(queryLower);
      
      return nameMatch || emailMatch || studentIdMatch;
    }).slice(0, 10); // Limit to 10 results for display
    
    setSearchResults(filtered);
  };

  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    // Only search if we have users loaded
    if (allUsers.length > 0) {
    searchTimeoutRef.current = setTimeout(() => {
      if (searchQuery) {
        handleSearchUsers(searchQuery);
      } else {
        setSearchResults([]);
      }
      }, 200); // Reduced delay for better responsiveness
    }

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery, allUsers]);

  const addGroupMember = (user) => {
    if (groupMembers.some(m => m.id === user.id)) {
      toast.error('User already added');
      return;
    }
    setGroupMembers([...groupMembers, user]);
    setSearchQuery('');
    setSearchResults([]);
  };

  const removeGroupMember = (userId) => {
    setGroupMembers(groupMembers.filter(m => m.id !== userId));
  };

  const canProceed = (step) => {
    switch(step) {
      case 2:
        return formData.title.trim() && formData.description.trim();
      case 3:
        return formData.achievementType === 'individual' || groupMembers.length > 0;
      case 4:
        return files.length > 0 && (!formData.hasCertificate || certificate);
      default:
        return true;
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    
    if (!formData.title.trim()) {
      toast.error('Please enter a title');
      setCurrentStep(1);
      return;
    }
    
    if (!formData.description.trim()) {
      toast.error('Please enter a description');
      setCurrentStep(1);
      return;
    }
    
    if (files.length === 0) {
      toast.error('Please upload at least one image');
      setCurrentStep(3);
      return;
    }

    if (formData.achievementType === 'group' && groupMembers.length === 0) {
      toast.error('Please add at least one group member for group achievements');
      setCurrentStep(2);
      return;
    }

    if (formData.hasCertificate && !certificate) {
      toast.error('Please upload a certificate');
      setCurrentStep(3);
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        toast.error('Please login to create an activity');
        navigate('/login');
        return;
      }
      
      const formDataToSend = new FormData();
      
      formDataToSend.append('title', formData.title.trim());
      formDataToSend.append('description', formData.description.trim());
      formDataToSend.append('type', formData.type);
      formDataToSend.append('year', formData.year);
      formDataToSend.append('achievement_type', formData.achievementType);
      
      if (formData.achievementType === 'group' && groupMembers.length > 0) {
        const memberIds = groupMembers.map(m => m.id);
        formDataToSend.append('group_members', JSON.stringify(memberIds));
      }
      
      // Only set has_certificate to true if user toggled it AND provided a file
      formDataToSend.append('has_certificate', formData.hasCertificate && certificate ? 'true' : 'false');
      
      // Add files
      files.forEach(file => {
        formDataToSend.append('files', file);
      });

      // Add certificate if provided and hasCertificate is true
      if (formData.hasCertificate && certificate) {
        formDataToSend.append('certificate', certificate);
      }
      
      const response = await axios.post('http://localhost:8000/api/v1/activities/', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      });

      toast.success('Achievement submitted successfully!');
      // Navigate to activities page to see the new submission
      navigate('/activities');
    } catch (error) {
      console.error('Error:', error);
      
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        localStorage.removeItem('token');
        navigate('/login');
        return;
      }
      
      if (error.response?.data?.error?.code === 'CERTIFICATE_VALIDATION_FAILED') {
        const errorData = error.response.data.error;
        const details = errorData.details || {};
        
        let errorMessage = errorData.message || 'Certificate does not match your activity details';
        
        if (details.reason) {
          errorMessage = details.reason;
        }
        
        if (details.missing_keywords && details.missing_keywords.length > 0) {
          const missing = details.missing_keywords.slice(0, 5).join(', ');
          errorMessage += ` Missing keywords: ${missing}`;
        }
        
        toast.error(errorMessage, { 
          duration: 8000,
          style: {
            maxWidth: '600px',
            whiteSpace: 'pre-wrap'
          }
        });
      } else {
        const message = error.response?.data?.detail || error.response?.data?.error?.message || 'Failed to submit achievement';
        toast.error(message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/30 pb-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
        {/* Modern Header */}
        <div className="mb-6 sm:mb-8">
          <button
            onClick={() => navigate('/activities')}
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4 transition-colors font-medium group"
          >
            <FiArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" />
            Back to Achievements
          </button>
          
          <div>
            <div className="inline-block mb-3 sm:mb-4 px-3 sm:px-4 py-1.5 sm:py-2 bg-blue-100 rounded-full">
              <span className="text-xs sm:text-sm font-semibold text-blue-700">Share Achievement</span>
            </div>
            <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-2 sm:mb-3">
              Submit New <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Achievement</span>
            </h1>
            <p className="text-gray-600 text-base sm:text-lg">
              Share your accomplishment with the community
            </p>
          </div>
        </div>

        {/* Modern Progress Steps */}
        <div className="mb-6 sm:mb-8">
          <div className="flex items-center justify-between overflow-x-auto pb-2">
            {steps.map((step, index) => (
              <React.Fragment key={step.id}>
                <div className="flex flex-col items-center flex-1 relative z-10 min-w-0">
                  <div className={`w-12 h-12 sm:w-14 sm:h-14 rounded-full flex items-center justify-center border-3 transition-all duration-300 shadow-lg ${
                    currentStep >= step.id 
                      ? 'bg-gradient-to-br from-blue-600 to-indigo-600 border-blue-600 text-white scale-110' 
                      : 'bg-white border-gray-300 text-gray-400'
                  }`}>
                    <step.icon className="w-5 h-5 sm:w-6 sm:h-6" />
                  </div>
                  <span className={`text-[10px] sm:text-xs font-bold mt-2 sm:mt-3 text-center uppercase tracking-wide whitespace-nowrap ${
                    currentStep >= step.id ? 'text-gray-900' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </span>
                  {currentStep === step.id && (
                    <div className="absolute -bottom-2 w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`flex-1 h-1 mx-1 sm:mx-2 mb-6 transition-all duration-500 min-w-[20px] ${
                    currentStep > step.id ? 'bg-gradient-to-r from-blue-600 to-indigo-600' : 'bg-gray-300'
                  }`} />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Step 1: Basic Information */}
        {currentStep === 1 && (
          <div className="bg-white rounded-2xl border-2 border-gray-100 shadow-xl">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 sm:px-8 py-4 sticky top-0 z-10">
              <h2 className="text-xl font-bold text-white flex items-center">
                <FiFileText className="w-6 h-6 mr-3" />
                Basic Information
              </h2>
            </div>
            <div className="p-6 sm:p-8 max-h-[calc(100vh-350px)] overflow-y-auto">
              <div className="space-y-6">
                <div>
                  <label htmlFor="title" className="block text-sm font-bold text-gray-700 mb-2">
                    Achievement Title <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="title"
                    name="title"
                    required
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-base font-medium"
                    placeholder="Enter a clear, descriptive title"
                    value={formData.title}
                    onChange={handleChange}
                  />
                  <p className="text-xs text-gray-500 mt-2 flex items-center">
                    <FiInfo className="w-3 h-3 mr-1" />
                    Example: "First Prize in National Hackathon 2024"
                  </p>
                </div>

                <div>
                  <label htmlFor="description" className="block text-sm font-bold text-gray-700 mb-2">
                    Description <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    required
                    rows={5}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-base resize-none font-medium"
                    placeholder="Provide detailed information about your achievement, including context, outcomes, and impact"
                    value={formData.description}
                    onChange={handleChange}
                  />
                  <p className="text-xs text-gray-500 mt-2 flex items-center">
                    <FiInfo className="w-3 h-3 mr-1" />
                    Minimum 50 characters recommended
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="type" className="block text-sm font-bold text-gray-700 mb-2">
                      Category <span className="text-red-500">*</span>
                    </label>
                    <select
                      id="type"
                      name="type"
                      required
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-base bg-white font-medium"
                      value={formData.type}
                      onChange={handleChange}
                    >
                      <option value="academic">Academic Excellence</option>
                      <option value="technical">Technical Innovation</option>
                      <option value="cultural">Cultural & Arts</option>
                      <option value="sports">Sports & Fitness</option>
                      <option value="social">Social Service</option>
                    </select>
                  </div>
                  
                  <div>
                    <label htmlFor="year" className="block text-sm font-bold text-gray-700 mb-2">
                      Year <span className="text-red-500">*</span>
                    </label>
                    <select
                      id="year"
                      name="year"
                      required
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-base bg-white font-medium"
                      value={formData.year}
                      onChange={handleChange}
                    >
                      {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map(year => (
                        <option key={year} value={year}>{year}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Achievement Type */}
        {currentStep === 2 && (
          <div className="bg-white rounded-2xl border-2 border-gray-100 shadow-xl">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-4 sticky top-0 z-10">
              <h2 className="text-xl font-bold text-white flex items-center">
                <FiUsers className="w-6 h-6 mr-3" />
                Achievement Type
              </h2>
            </div>
            <div className="p-6 sm:p-8 max-h-[calc(100vh-350px)] overflow-y-auto">
              <p className="text-sm text-gray-600 mb-6">Select whether this is an individual or group achievement</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                <button
                  type="button"
                  onClick={() => {
                    setFormData({...formData, achievementType: 'individual'});
                    setGroupMembers([]);
                  }}
                  className={`p-6 rounded-xl border-3 transition-all text-left transform hover:scale-105 ${
                    formData.achievementType === 'individual'
                      ? 'border-blue-600 bg-blue-50 shadow-lg'
                      : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start">
                    <div className={`w-6 h-6 rounded-full border-3 flex items-center justify-center mt-0.5 mr-4 flex-shrink-0 transition-all ${
                      formData.achievementType === 'individual' ? 'border-blue-600 bg-blue-600' : 'border-gray-300'
                    }`}>
                      {formData.achievementType === 'individual' && (
                        <div className="w-2.5 h-2.5 bg-white rounded-full"></div>
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="font-bold text-gray-900 mb-1 text-lg">Individual Achievement</div>
                      <div className="text-sm text-gray-600">This achievement is solely yours</div>
                    </div>
                  </div>
                </button>
                
                <button
                  type="button"
                  onClick={() => setFormData({...formData, achievementType: 'group'})}
                  className={`p-6 rounded-xl border-3 transition-all text-left transform hover:scale-105 ${
                    formData.achievementType === 'group'
                      ? 'border-blue-600 bg-blue-50 shadow-lg'
                      : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start">
                    <div className={`w-6 h-6 rounded-full border-3 flex items-center justify-center mt-0.5 mr-4 flex-shrink-0 transition-all ${
                      formData.achievementType === 'group' ? 'border-blue-600 bg-blue-600' : 'border-gray-300'
                    }`}>
                      {formData.achievementType === 'group' && (
                        <div className="w-2.5 h-2.5 bg-white rounded-full"></div>
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="font-bold text-gray-900 mb-1 text-lg">Group Achievement</div>
                      <div className="text-sm text-gray-600">Completed with a team</div>
                    </div>
                  </div>
                </button>
              </div>

              {formData.achievementType === 'group' && (
                <div className="pt-6 border-t-2 border-gray-200 mt-6">
                  <label className="block text-sm font-bold text-gray-700 mb-4 flex items-center">
                    <FiUsers className="w-4 h-4 mr-2 text-blue-600" />
                    Add Team Members <span className="text-red-500 ml-1">*</span>
                  </label>
                  
                  <div className="relative mb-6">
                    {loadingUsers && allUsers.length === 0 && (
                      <div className="mb-3 text-sm text-gray-500 flex items-center">
                        <FiLoader className="h-4 w-4 mr-2 animate-spin" />
                        Loading students...
                      </div>
                    )}
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                        <FiSearch className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="text"
                        ref={searchRef}
                        className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-base font-medium"
                        placeholder="Search students by name, email, or student ID"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        disabled={loadingUsers && allUsers.length === 0}
                      />
                      
                      {searchQuery && searchResults.length === 0 && allUsers.length > 0 && (
                        <div className="absolute z-30 w-full mt-2 bg-white rounded-xl shadow-2xl border-2 border-gray-200 p-4 text-center text-gray-500">
                          No students found matching "{searchQuery}"
                        </div>
                      )}
                      
                      {searchResults.length > 0 && (
                        <div className="absolute z-30 w-full mt-2 bg-white rounded-xl shadow-2xl border-2 border-gray-200 max-h-64 overflow-y-auto">
                          {searchResults.map((result) => (
                            <div
                              key={result.id}
                              onClick={() => addGroupMember(result)}
                              className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0 transition-colors"
                            >
                              <div className="flex items-center">
                                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold mr-3 flex-shrink-0">
                                  {result.name?.charAt(0) || 'U'}
                                </div>
                                <div className="flex-1 min-w-0">
                                  <div className="font-semibold text-gray-900 truncate">{result.name || 'Unknown'}</div>
                                  <div className="text-sm text-gray-600 truncate">
                                    {result.department || ''}
                                    {result.student_id && ` • ${result.student_id}`}
                                  </div>
                                </div>
                                <FiPlus className="h-5 w-5 text-blue-600 flex-shrink-0" />
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {groupMembers.length > 0 && (
                    <div className="space-y-3 mt-6">
                      <p className="text-sm font-bold text-gray-700 mb-3">
                        Team Members ({groupMembers.length})
                      </p>
                      <div className="max-h-64 overflow-y-auto space-y-3 pr-2">
                        {groupMembers.map((member) => (
                          <div key={member.id} className="flex items-center justify-between p-4 bg-blue-50 rounded-xl border-2 border-blue-200">
                            <div className="flex items-center min-w-0 flex-1">
                              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold mr-3 flex-shrink-0">
                                {member.name?.charAt(0) || 'U'}
                              </div>
                              <div className="min-w-0 flex-1">
                                <div className="font-semibold text-gray-900 truncate">{member.name || 'Unknown'}</div>
                                <div className="text-sm text-gray-600 truncate">
                                  {member.department || ''}
                                  {member.student_id && ` • ${member.student_id}`}
                                </div>
                              </div>
                            </div>
                            <button
                              type="button"
                              onClick={() => removeGroupMember(member.id)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors flex-shrink-0 ml-2"
                              aria-label="Remove team member"
                            >
                              <FiX className="h-5 w-5" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {groupMembers.length === 0 && !loadingUsers && (
                    <div className="mt-4 p-4 bg-yellow-50 border-2 border-yellow-200 rounded-xl">
                      <div className="flex items-start">
                        <FiAlertCircle className="h-5 w-5 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-yellow-800">
                          <span className="font-semibold">Note:</span> Please add at least one team member to continue with a group achievement.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Upload Files */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl border-2 border-gray-100 shadow-xl">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 sm:px-8 py-4 sticky top-0 z-10">
                <h2 className="text-xl font-bold text-white flex items-center">
                  <FiImage className="w-6 h-6 mr-3" />
                  Upload Images
                </h2>
              </div>
              <div className="p-6 sm:p-8 max-h-[calc(100vh-500px)] overflow-y-auto">
                <p className="text-sm text-gray-600 mb-6">Add photos documenting your achievement <span className="text-red-500 font-bold">*</span></p>
                
                <div
                  className={`border-3 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
                    dragActive ? 'border-blue-500 bg-blue-50 scale-105' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                  }`}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                >
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
                    <FiUpload className="h-8 w-8 text-blue-600" />
                  </div>
                  <p className="text-lg font-bold text-gray-700 mb-2">Drag and drop images here</p>
                  <p className="text-sm text-gray-500 mb-4">or</p>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={(e) => handleFileSelect(e.target.files)}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="inline-flex items-center px-6 py-3 border-2 border-blue-600 text-base font-bold rounded-xl text-blue-600 bg-white hover:bg-blue-50 cursor-pointer transition-all transform hover:scale-105 shadow-md"
                  >
                    <FiUpload className="h-5 w-5 mr-2" />
                    Browse Files
                  </label>
                  <p className="text-xs text-gray-500 mt-4 flex items-center justify-center">
                    <FiInfo className="w-3 h-3 mr-1" />
                    Supported: JPG, PNG, GIF • Max: 10MB per file
                  </p>
                </div>

                {files.length > 0 && (
                  <div className="mt-6">
                    <p className="text-sm font-bold text-gray-700 mb-4">Selected Images ({files.length})</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {files.map((file, index) => (
                        <div key={index} className="relative group">
                          <div className="aspect-square rounded-xl overflow-hidden bg-gray-100 border-2 border-gray-200 shadow-md">
                            <img src={URL.createObjectURL(file)} alt="" className="w-full h-full object-cover" />
                          </div>
                          <button
                            type="button"
                            onClick={() => removeFile(index)}
                            className="absolute top-2 right-2 p-2 bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity shadow-lg hover:bg-red-700"
                          >
                            <FiX className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-white rounded-2xl border-2 border-gray-100 shadow-xl">
              <div className="bg-gradient-to-r from-yellow-500 to-orange-500 px-6 sm:px-8 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FiAward className="w-6 h-6 mr-3 text-white" />
                    <h2 className="text-xl font-bold text-white">Certificate Verification</h2>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.hasCertificate}
                      onChange={(e) => {
                        setFormData({...formData, hasCertificate: e.target.checked});
                        if (!e.target.checked) {
                          setCertificate(null);
                        }
                      }}
                      className="sr-only peer"
                    />
                    <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-yellow-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-yellow-600 shadow-lg"></div>
                  </label>
                </div>
              </div>
              <div className="p-6 sm:p-8">
                {formData.hasCertificate ? (
                  <div>
                    {!certificate ? (
                      <div className="border-3 border-dashed border-gray-300 rounded-xl p-8 text-center bg-gray-50">
                        <FiAward className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                        <input
                          type="file"
                          accept="image/*,.pdf"
                          onChange={handleCertificateSelect}
                          className="hidden"
                          id="certificate-upload"
                        />
                        <label
                          htmlFor="certificate-upload"
                          className="inline-flex items-center px-6 py-3 border-2 border-yellow-600 text-base font-bold rounded-xl text-yellow-600 bg-white hover:bg-yellow-50 cursor-pointer transition-all transform hover:scale-105 shadow-md"
                        >
                          <FiUpload className="h-5 w-5 mr-2" />
                          Upload Certificate
                        </label>
                        <p className="text-xs text-gray-500 mt-4 flex items-center justify-center">
                          <FiInfo className="w-3 h-3 mr-1" />
                          Image or PDF • Max: 15MB
                        </p>
                      </div>
                    ) : (
                      <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl border-2 border-yellow-200 p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center min-w-0 flex-1">
                            <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center mr-4 flex-shrink-0">
                              <FiFileText className="h-6 w-6 text-yellow-600" />
                            </div>
                            <div className="min-w-0">
                              <p className="font-bold text-gray-900 truncate">{certificate.name}</p>
                              <p className="text-sm text-gray-600">{(certificate.size / 1024 / 1024).toFixed(2)} MB</p>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={removeCertificate}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors flex-shrink-0 ml-2"
                          >
                            <FiX className="h-5 w-5" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <FiAward className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                    <p className="text-sm">Toggle the switch above to upload a certificate</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Review */}
        {currentStep === 4 && (
          <div className="bg-white rounded-2xl border-2 border-gray-100 shadow-xl">
            <div className="bg-gradient-to-r from-green-600 to-emerald-600 px-6 sm:px-8 py-4 sticky top-0 z-10">
              <h2 className="text-xl font-bold text-white flex items-center">
                <FiCheckCircle className="w-6 h-6 mr-3" />
                Review Your Submission
              </h2>
            </div>
            <div className="p-6 sm:p-8 max-h-[calc(100vh-350px)] overflow-y-auto">
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 rounded-xl p-4">
                    <h3 className="text-sm font-bold text-gray-500 mb-2 uppercase tracking-wide">Title</h3>
                    <p className="text-base font-semibold text-gray-900">{formData.title || 'Not provided'}</p>
                  </div>
                  <div className="bg-gray-50 rounded-xl p-4">
                    <h3 className="text-sm font-bold text-gray-500 mb-2 uppercase tracking-wide">Category</h3>
                    <p className="text-base font-semibold text-gray-900 capitalize">{formData.type}</p>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-xl p-4">
                  <h3 className="text-sm font-bold text-gray-500 mb-2 uppercase tracking-wide">Description</h3>
                  <p className="text-base text-gray-900 leading-relaxed">{formData.description || 'Not provided'}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 rounded-xl p-4">
                    <h3 className="text-sm font-bold text-gray-500 mb-2 uppercase tracking-wide">Year</h3>
                    <p className="text-base font-semibold text-gray-900">{formData.year}</p>
                  </div>
                  <div className="bg-gray-50 rounded-xl p-4">
                    <h3 className="text-sm font-bold text-gray-500 mb-2 uppercase tracking-wide">Type</h3>
                    <p className="text-base font-semibold text-gray-900 capitalize">{formData.achievementType}</p>
                  </div>
                </div>

                {groupMembers.length > 0 && (
                  <div className="bg-blue-50 rounded-xl p-4 border-2 border-blue-200">
                    <h3 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wide">Team Members ({groupMembers.length})</h3>
                    <div className="space-y-2">
                      {groupMembers.map(member => (
                        <div key={member.id} className="flex items-center p-3 bg-white rounded-lg">
                          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3">
                            {member.name?.charAt(0) || 'U'}
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-gray-900">{member.name || 'Unknown'}</p>
                            <p className="text-xs text-gray-600">{member.department || ''}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-gray-50 rounded-xl p-4">
                  <h3 className="text-sm font-bold text-gray-500 mb-2 uppercase tracking-wide">Attachments</h3>
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center">
                      <FiImage className="h-5 w-5 mr-2 text-blue-600" />
                      <p className="text-base font-semibold text-gray-900">{files.length} image(s)</p>
                    </div>
                    {certificate && (
                      <div className="flex items-center">
                        <FiAward className="h-5 w-5 mr-2 text-yellow-600" />
                        <p className="text-base font-semibold text-gray-900">1 certificate</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between mt-6 bg-white rounded-2xl shadow-lg p-4 sm:p-6 border-2 border-gray-100 sticky bottom-4 z-10">
          <button
            type="button"
            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
            disabled={currentStep === 1}
            className="px-4 sm:px-6 py-2.5 sm:py-3 text-gray-700 bg-white border-2 border-gray-300 rounded-xl hover:bg-gray-50 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed font-bold transition-all transform hover:scale-105 text-sm sm:text-base"
          >
            Previous
          </button>

          {currentStep < 4 ? (
            <button
              type="button"
              onClick={() => setCurrentStep(currentStep + 1)}
              disabled={!canProceed(currentStep + 1)}
              className="px-6 sm:px-8 py-2.5 sm:py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-bold transition-all transform hover:scale-105 shadow-lg text-sm sm:text-base"
            >
              Continue
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading}
              className="inline-flex items-center px-6 sm:px-8 py-2.5 sm:py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed font-bold transition-all transform hover:scale-105 shadow-lg text-sm sm:text-base"
            >
              {loading ? (
                <>
                  <FiLoader className="w-4 h-4 sm:w-5 sm:h-5 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <FiCheckCircle className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                  Submit Achievement
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CreateActivity;
