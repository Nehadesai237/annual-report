import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FaGraduationCap, 
  FaBars, 
  FaTimes, 
  FaTrophy, 
  FaAward, 
  FaRocket, 
  FaLightbulb,
  FaCalendarAlt,
  FaMapMarkerAlt,
  FaPhone,
  FaEnvelope,
  FaFacebook,
  FaTwitter,
  FaInstagram,
  FaLinkedin,
  FaBuilding,
  FaUsers,
  FaBook,
  FaChalkboardTeacher,
  FaUniversity,
  FaArrowRight,
  FaCheckCircle
} from 'react-icons/fa';
import axios from 'axios';
import { getImageUrl } from '../utils/imageUtils';

const HomePage = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [achievements, setAchievements] = useState([]);
  const [events, setEvents] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loadingAchievements, setLoadingAchievements] = useState(true);
  const [loadingEvents, setLoadingEvents] = useState(true);
  const [selectedDept, setSelectedDept] = useState('all');

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    loadAchievements();
    loadEvents();
    loadDepartments();
  }, [selectedDept]);

  const loadAchievements = async () => {
    try {
      setLoadingAchievements(true);
      const params = { page: 1, size: 50 };
      if (selectedDept !== 'all') {
        params.department = selectedDept;
      }
      
      const response = await axios.get(`${API_BASE_URL}/api/v1/activities/public`, { params });
      
      // Filter for approved student achievements (not admin-created)
      const studentAchievements = (response.data?.activities || [])
        .filter(activity => 
          activity.status === 'accepted' && 
          !activity.is_admin_created
        )
        .slice(0, 12);
      
      setAchievements(studentAchievements);
    } catch (error) {
      console.error('Error loading achievements:', error);
      setAchievements([]);
    } finally {
      setLoadingAchievements(false);
    }
  };

  const loadEvents = async () => {
    try {
      setLoadingEvents(true);
      const params = { page: 1, size: 50 };
      if (selectedDept !== 'all') {
        params.department = selectedDept;
      }
      
      const response = await axios.get(`${API_BASE_URL}/api/v1/events/public`, { params });
      setEvents(response.data?.events || []);
    } catch (error) {
      console.error('Error loading events:', error);
      setEvents([]);
    } finally {
      setLoadingEvents(false);
    }
  };

  const loadDepartments = async () => {
    try {
      // Extract unique departments from achievements and events
      const deptSet = new Set();
      achievements.forEach(a => {
        if (a.department) deptSet.add(a.department);
      });
      events.forEach(e => {
        if (e.department) deptSet.add(e.department);
      });
      
      // Add default departments if none found
      if (deptSet.size === 0) {
        deptSet.add('Computer Science');
        deptSet.add('Mechanical Engineering');
        deptSet.add('Electronics & Communication');
        deptSet.add('Civil Engineering');
        deptSet.add('Electrical Engineering');
        deptSet.add('Information Technology');
      }
      
      setDepartments(Array.from(deptSet).sort());
    } catch (error) {
      console.error('Error loading departments:', error);
      setDepartments(['Computer Science', 'Mechanical Engineering', 'Electronics & Communication']);
    }
  };

  useEffect(() => {
    loadDepartments();
  }, [achievements, events]);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  const getActivityTypeColor = (type) => {
    const colors = {
      academic: 'from-blue-500 to-indigo-600',
      technical: 'from-purple-500 to-pink-600',
      cultural: 'from-pink-500 to-rose-600',
      sports: 'from-green-500 to-emerald-600',
      social: 'from-orange-500 to-amber-600'
    };
    return colors[type?.toLowerCase()] || 'from-gray-500 to-gray-600';
  };

  const getActivityTypeIcon = (type) => {
    const icons = {
      academic: FaBook,
      technical: FaRocket,
      cultural: FaAward,
      sports: FaTrophy,
      social: FaUsers
    };
    return icons[type?.toLowerCase()] || FaGraduationCap;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'TBA';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        month: 'long', 
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return 'TBA';
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/95 backdrop-blur-md shadow-lg' 
          : 'bg-white/90 backdrop-blur-sm'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo */}
            <Link to="/" className="flex items-center group">
              <div className="flex items-center space-x-3">
                <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-2.5 rounded-xl shadow-lg group-hover:shadow-xl transition-shadow">
                  <FaGraduationCap className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 leading-tight">
                    TKIET Warananagar
                  </h1>
                  <p className="text-xs text-gray-500 font-medium">Excellence in Engineering Education</p>
                </div>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-1">
              <button 
                onClick={() => scrollToSection('home')} 
                className="px-4 py-2.5 rounded-lg text-sm font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200"
              >
                Home
              </button>
              <button 
                onClick={() => scrollToSection('about')} 
                className="px-4 py-2.5 rounded-lg text-sm font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200"
              >
                About
              </button>
              <button 
                onClick={() => scrollToSection('achievements')} 
                className="px-4 py-2.5 rounded-lg text-sm font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200"
              >
                Achievements
              </button>
              <button 
                onClick={() => scrollToSection('events')} 
                className="px-4 py-2.5 rounded-lg text-sm font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200"
              >
                Events
              </button>
              <button 
                onClick={() => scrollToSection('departments')} 
                className="px-4 py-2.5 rounded-lg text-sm font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200"
              >
                Departments
              </button>
              <button 
                onClick={() => scrollToSection('contact')} 
                className="px-4 py-2.5 rounded-lg text-sm font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200"
              >
                Contact
              </button>
            </div>

            {/* Auth Buttons */}
            <div className="hidden lg:flex items-center space-x-3">
              <Link 
                to="/login" 
                className="px-5 py-2.5 rounded-lg text-sm font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200"
              >
                Login
              </Link>
              <Link 
                to="/register" 
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-2.5 rounded-lg text-sm font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
              >
                Register
              </Link>
            </div>

            {/* Mobile menu button */}
            <div className="lg:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="p-2.5 rounded-lg text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all"
              >
                {isMenuOpen ? <FaTimes className="h-6 w-6" /> : <FaBars className="h-6 w-6" />}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {isMenuOpen && (
            <div className="lg:hidden border-t border-gray-200 bg-white/95 backdrop-blur-md">
              <div className="px-4 pt-4 pb-6 space-y-2">
                <button 
                  onClick={() => scrollToSection('home')} 
                  className="block w-full text-left px-4 py-3 rounded-lg text-base font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all"
                >
                  Home
                </button>
                <button 
                  onClick={() => scrollToSection('about')} 
                  className="block w-full text-left px-4 py-3 rounded-lg text-base font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all"
                >
                  About
                </button>
                <button 
                  onClick={() => scrollToSection('achievements')} 
                  className="block w-full text-left px-4 py-3 rounded-lg text-base font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all"
                >
                  Achievements
                </button>
                <button 
                  onClick={() => scrollToSection('events')} 
                  className="block w-full text-left px-4 py-3 rounded-lg text-base font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all"
                >
                  Events
                </button>
                <button 
                  onClick={() => scrollToSection('departments')} 
                  className="block w-full text-left px-4 py-3 rounded-lg text-base font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all"
                >
                  Departments
                </button>
                <button 
                  onClick={() => scrollToSection('contact')} 
                  className="block w-full text-left px-4 py-3 rounded-lg text-base font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all"
                >
                  Contact
                </button>
                <div className="border-t border-gray-200 pt-4 mt-4 space-y-2">
                  <Link 
                    to="/login" 
                    className="block w-full text-center px-4 py-3 rounded-lg text-base font-semibold text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-all"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Login
                  </Link>
                  <Link 
                    to="/register" 
                    className="block w-full text-center bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-4 py-3 rounded-lg text-base font-semibold shadow-lg transition-all"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Register
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="pt-20 pb-16 lg:pt-32 lg:pb-24 bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left">
              <div className="inline-block mb-4 px-4 py-2 bg-blue-100 rounded-full">
                <span className="text-sm font-semibold text-blue-700">Welcome to TKIET</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                Excellence in Engineering
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                  Education & Innovation
                </span>
              </h1>
              <p className="text-lg md:text-xl text-gray-600 mb-8 leading-relaxed">
                Empowering students with cutting-edge knowledge, practical skills, and opportunities to excel in the dynamic world of engineering.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Link
                  to="/register"
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-4 rounded-xl text-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center justify-center"
                >
                  Get Started <FaArrowRight className="ml-2" />
                </Link>
                <button
                  onClick={() => scrollToSection('about')}
                  className="bg-white border-2 border-gray-300 hover:border-blue-600 text-gray-700 hover:text-blue-600 px-8 py-4 rounded-xl text-lg font-semibold shadow-md hover:shadow-lg transform hover:scale-105 transition-all duration-200"
                >
                  Learn More
                </button>
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-3xl p-8 shadow-2xl">
                <div className="bg-white rounded-2xl p-8">
                  <div className="grid grid-cols-2 gap-6">
                    <div className="text-center">
                      <div className="text-4xl font-bold text-blue-600 mb-2">5000+</div>
                      <div className="text-sm text-gray-600">Students</div>
                    </div>
                    <div className="text-center">
                      <div className="text-4xl font-bold text-indigo-600 mb-2">200+</div>
                      <div className="text-sm text-gray-600">Faculty</div>
                    </div>
                    <div className="text-center">
                      <div className="text-4xl font-bold text-blue-600 mb-2">15+</div>
                      <div className="text-sm text-gray-600">Programs</div>
                    </div>
                    <div className="text-center">
                      <div className="text-4xl font-bold text-indigo-600 mb-2">100%</div>
                      <div className="text-sm text-gray-600">Placement</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-16 lg:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 lg:mb-16">
            <div className="inline-block mb-4 px-4 py-2 bg-indigo-100 rounded-full">
              <span className="text-sm font-semibold text-indigo-700">About Us</span>
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Shaping Future Engineers
            </h2>
            <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              TKIET Warananagar is committed to providing world-class engineering education with a focus on innovation, research, and industry collaboration.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 text-center hover:shadow-xl transition-all duration-300">
              <div className="bg-blue-600 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
                <FaUniversity className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Autonomous Status</h3>
              <p className="text-gray-600 leading-relaxed">
                Recognized as an autonomous institution, offering flexible curriculum and innovative teaching methodologies.
              </p>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-8 text-center hover:shadow-xl transition-all duration-300">
              <div className="bg-purple-600 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
                <FaChalkboardTeacher className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Expert Faculty</h3>
              <p className="text-gray-600 leading-relaxed">
                Experienced professors and industry experts dedicated to student success and academic excellence.
              </p>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-8 text-center hover:shadow-xl transition-all duration-300">
              <div className="bg-green-600 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
                <FaRocket className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Industry Connect</h3>
              <p className="text-gray-600 leading-relaxed">
                Strong partnerships with leading companies ensuring excellent placement opportunities and industry exposure.
              </p>
            </div>
          </div>

          <div className="mt-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl p-8 md:p-12 text-white">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-3xl font-bold mb-4">Our Mission</h3>
                <p className="text-lg leading-relaxed mb-6">
                  To provide quality engineering education that prepares students to become innovative professionals, ethical leaders, and responsible citizens contributing to society.
                </p>
                <h3 className="text-3xl font-bold mb-4">Our Vision</h3>
                <p className="text-lg leading-relaxed">
                  To be a premier institution of engineering education, recognized for excellence in teaching, research, and innovation.
                </p>
              </div>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <FaCheckCircle className="h-6 w-6 text-white flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="font-bold text-lg mb-1">State-of-the-Art Infrastructure</h4>
                    <p className="text-blue-100">Modern laboratories and facilities</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <FaCheckCircle className="h-6 w-6 text-white flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="font-bold text-lg mb-1">Research Opportunities</h4>
                    <p className="text-blue-100">Active research programs and projects</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <FaCheckCircle className="h-6 w-6 text-white flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="font-bold text-lg mb-1">Student Support</h4>
                    <p className="text-blue-100">Comprehensive support services</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <FaCheckCircle className="h-6 w-6 text-white flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="font-bold text-lg mb-1">Extracurricular Activities</h4>
                    <p className="text-blue-100">Vibrant campus life and clubs</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Achievements Section */}
      <section id="achievements" className="py-16 lg:py-24 bg-gradient-to-br from-gray-50 via-white to-blue-50/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 lg:mb-16">
            <div className="inline-block mb-4 px-4 py-2 bg-yellow-100 rounded-full">
              <span className="text-sm font-semibold text-yellow-700">Student Achievements</span>
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Celebrating Excellence
            </h2>
            <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed mb-8">
              Showcasing outstanding achievements by our students across various departments and disciplines.
            </p>

            {/* Department Filter */}
            <div className="flex flex-wrap justify-center gap-3 mb-8">
              <button
                onClick={() => setSelectedDept('all')}
                className={`px-6 py-2 rounded-full text-sm font-semibold transition-all duration-200 ${
                  selectedDept === 'all'
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-blue-50 border border-gray-200'
                }`}
              >
                All Departments
              </button>
              {departments.map((dept) => (
                <button
                  key={dept}
                  onClick={() => setSelectedDept(dept)}
                  className={`px-6 py-2 rounded-full text-sm font-semibold transition-all duration-200 ${
                    selectedDept === dept
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'bg-white text-gray-700 hover:bg-blue-50 border border-gray-200'
                  }`}
                >
                  {dept}
                </button>
              ))}
            </div>
          </div>

          {loadingAchievements ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
                  <div className="h-40 bg-gray-200 rounded-xl mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded mb-3 w-24"></div>
                  <div className="h-6 bg-gray-200 rounded mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          ) : achievements.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {achievements.map((achievement, index) => {
                const Icon = getActivityTypeIcon(achievement.type);
                return (
                  <div
                    key={achievement.id || index}
                    className="group bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border-2 border-gray-100 hover:border-blue-200"
                  >
                    {achievement.images && achievement.images.length > 0 && (
                      <div className="h-48 bg-gradient-to-br from-blue-500 to-indigo-600 relative overflow-hidden">
                        <img
                          src={getImageUrl(achievement.images[0])}
                          alt={achievement.title}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      </div>
                    )}
                    <div className="p-6">
                      <div className="flex items-center justify-between mb-3">
                        <div className={`bg-gradient-to-br ${getActivityTypeColor(achievement.type)} w-12 h-12 rounded-xl flex items-center justify-center shadow-lg`}>
                          <Icon className="h-6 w-6 text-white" />
                        </div>
                        <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">
                          {achievement.department || 'General'}
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-gray-900 mb-2 leading-tight line-clamp-2">
                        {achievement.title}
                      </h3>
                      <p className="text-sm text-gray-600 mb-4 leading-relaxed line-clamp-3">
                        {achievement.description}
                      </p>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500 capitalize">{achievement.type}</span>
                        <span className="text-gray-500 font-semibold">{achievement.year}</span>
                      </div>
                      {achievement.user_name && (
                        <div className="mt-3 pt-3 border-t border-gray-100">
                          <p className="text-xs text-gray-500">
                            By: <span className="font-semibold text-gray-700">{achievement.user_name}</span>
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12">
              <FaTrophy className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Achievements Available</h3>
              <p className="text-gray-600">
                {selectedDept !== 'all' 
                  ? `No achievements found for ${selectedDept}. Try selecting a different department.`
                  : 'Check back soon for student achievements!'}
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Events Section */}
      <section id="events" className="py-16 lg:py-24 bg-gradient-to-br from-white via-indigo-50/30 to-purple-50/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 lg:mb-16">
            <div className="inline-block mb-4 px-4 py-2 bg-indigo-100 rounded-full">
              <span className="text-sm font-semibold text-indigo-700">Events & Festivals</span>
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Upcoming Events
            </h2>
            <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed mb-8">
              Join us for exciting events, competitions, and celebrations throughout the year.
            </p>

            {/* Department Filter */}
            <div className="flex flex-wrap justify-center gap-3 mb-8">
              <button
                onClick={() => setSelectedDept('all')}
                className={`px-6 py-2 rounded-full text-sm font-semibold transition-all duration-200 ${
                  selectedDept === 'all'
                    ? 'bg-indigo-600 text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-indigo-50 border border-gray-200'
                }`}
              >
                All Departments
              </button>
              {departments.map((dept) => (
                <button
                  key={dept}
                  onClick={() => setSelectedDept(dept)}
                  className={`px-6 py-2 rounded-full text-sm font-semibold transition-all duration-200 ${
                    selectedDept === dept
                      ? 'bg-indigo-600 text-white shadow-lg'
                      : 'bg-white text-gray-700 hover:bg-indigo-50 border border-gray-200'
                  }`}
                >
                  {dept}
                </button>
              ))}
            </div>
          </div>

          {loadingEvents ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-white rounded-2xl shadow-lg overflow-hidden animate-pulse">
                  <div className="h-40 bg-gray-200"></div>
                  <div className="p-6">
                    <div className="h-4 bg-gray-200 rounded mb-4 w-20"></div>
                    <div className="h-5 bg-gray-200 rounded mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded mb-4"></div>
                    <div className="h-4 bg-gray-200 rounded w-32"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : events.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {events.map((event, index) => (
                <div
                  key={event.id || index}
                  className="group bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border-2 border-gray-100 hover:border-indigo-200"
                >
                  <div className={`h-40 bg-gradient-to-br ${getActivityTypeColor(event.type)} flex items-center justify-center relative overflow-hidden`}>
                    <div className="absolute inset-0 bg-black/10 group-hover:bg-black/20 transition-colors"></div>
                    <FaCalendarAlt className="h-16 w-16 text-white relative z-10 group-hover:scale-110 transition-transform" />
                    <div className="absolute top-3 right-3 bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full border border-white/30">
                      <span className="text-xs font-bold text-white capitalize">{event.type || 'Event'}</span>
                    </div>
                  </div>
                  <div className="p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-2 leading-tight group-hover:text-indigo-600 transition-colors line-clamp-2">
                      {event.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-4 leading-relaxed line-clamp-3">
                      {event.description}
                    </p>
                    {event.venue && (
                      <p className="text-xs text-gray-500 mb-2 flex items-center">
                        <FaMapMarkerAlt className="mr-1" />
                        {event.venue}
                      </p>
                    )}
                    {event.organizer && (
                      <p className="text-xs text-gray-500 mb-3">
                        <span className="font-semibold">Organizer:</span> {event.organizer}
                      </p>
                    )}
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center text-gray-500">
                        <FaCalendarAlt className="w-4 h-4 mr-2 text-indigo-600" />
                        {formatDate(event.activity_date || event.date)}
                      </div>
                      {event.attendees_count > 0 && (
                        <span className="text-xs text-gray-500">
                          {event.attendees_count} participants
                        </span>
                      )}
                    </div>
                    {event.department && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <span className="px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-semibold rounded-full">
                          {event.department}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <FaCalendarAlt className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Events Available</h3>
              <p className="text-gray-600">
                {selectedDept !== 'all' 
                  ? `No events found for ${selectedDept}. Try selecting a different department.`
                  : 'Check back soon for upcoming events!'}
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Departments Section */}
      <section id="departments" className="py-16 lg:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 lg:mb-16">
            <div className="inline-block mb-4 px-4 py-2 bg-green-100 rounded-full">
              <span className="text-sm font-semibold text-green-700">Academic Programs</span>
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Our Departments
            </h2>
            <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Explore our diverse range of engineering programs designed to meet industry demands.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {departments.length > 0 ? departments.map((dept, index) => (
              <div
                key={index}
                className="group bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-blue-200"
              >
                <div className="flex items-center space-x-4">
                  <div className="bg-blue-600 w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                    <FaBuilding className="h-7 w-7 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-1">{dept}</h3>
                    <p className="text-sm text-gray-600">Engineering Program</p>
                  </div>
                </div>
              </div>
            )) : (
              <>
                {['Computer Science', 'Mechanical Engineering', 'Electronics & Communication', 'Civil Engineering', 'Electrical Engineering', 'Information Technology'].map((dept, index) => (
                  <div
                    key={index}
                    className="group bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-blue-200"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="bg-blue-600 w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                        <FaBuilding className="h-7 w-7 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-gray-900 mb-1">{dept}</h3>
                        <p className="text-sm text-gray-600">Engineering Program</p>
                      </div>
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-16 lg:py-24 bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 lg:mb-16">
            <div className="inline-block mb-4 px-4 py-2 bg-blue-500/20 rounded-full border border-blue-400/30">
              <span className="text-sm font-semibold text-blue-200">Get in Touch</span>
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
              Contact Us
            </h2>
            <p className="text-lg md:text-xl text-blue-100 max-w-3xl mx-auto leading-relaxed">
              We'd love to hear from you. Reach out to us for any inquiries or information.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center hover:bg-white/20 transition-all duration-300">
              <div className="bg-blue-500 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
                <FaMapMarkerAlt className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2">Address</h3>
              <p className="text-blue-100 leading-relaxed">
                TKIET Warananagar<br />
                Kolhapur, Maharashtra<br />
                India
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center hover:bg-white/20 transition-all duration-300">
              <div className="bg-blue-500 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
                <FaPhone className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2">Phone</h3>
              <p className="text-blue-100">
                +91-XXX-XXXX-XXXX<br />
                +91-XXX-XXXX-XXXX
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center hover:bg-white/20 transition-all duration-300">
              <div className="bg-blue-500 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
                <FaEnvelope className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2">Email</h3>
              <p className="text-blue-100">
                info@tkiet.edu.in<br />
                contact@tkiet.edu.in
              </p>
            </div>
          </div>

          <div className="text-center">
            <div className="flex justify-center space-x-6">
              <a href="#" className="bg-white/10 hover:bg-white/20 w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 hover:scale-110">
                <FaFacebook className="h-6 w-6" />
              </a>
              <a href="#" className="bg-white/10 hover:bg-white/20 w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 hover:scale-110">
                <FaTwitter className="h-6 w-6" />
              </a>
              <a href="#" className="bg-white/10 hover:bg-white/20 w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 hover:scale-110">
                <FaInstagram className="h-6 w-6" />
              </a>
              <a href="#" className="bg-white/10 hover:bg-white/20 w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 hover:scale-110">
                <FaLinkedin className="h-6 w-6" />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-2 rounded-xl">
                  <FaGraduationCap className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">TKIET</h3>
                  <p className="text-xs text-gray-400">Warananagar</p>
                </div>
              </div>
              <p className="text-sm leading-relaxed">
                Excellence in Engineering Education and Innovation
              </p>
            </div>

            <div>
              <h4 className="text-white font-bold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <button onClick={() => scrollToSection('about')} className="hover:text-white transition-colors">
                    About Us
                  </button>
                </li>
                <li>
                  <button onClick={() => scrollToSection('achievements')} className="hover:text-white transition-colors">
                    Achievements
                  </button>
                </li>
                <li>
                  <button onClick={() => scrollToSection('events')} className="hover:text-white transition-colors">
                    Events
                  </button>
                </li>
                <li>
                  <button onClick={() => scrollToSection('departments')} className="hover:text-white transition-colors">
                    Departments
                  </button>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-bold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/login" className="hover:text-white transition-colors">
                    Student Login
                  </Link>
                </li>
                <li>
                  <Link to="/register" className="hover:text-white transition-colors">
                    Register
                  </Link>
                </li>
                <li>
                  <button onClick={() => scrollToSection('contact')} className="hover:text-white transition-colors">
                    Contact Us
                  </button>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-bold mb-4">Connect</h4>
              <div className="flex space-x-4">
                <a href="#" className="bg-gray-800 hover:bg-gray-700 w-10 h-10 rounded-full flex items-center justify-center transition-colors">
                  <FaFacebook className="h-5 w-5" />
                </a>
                <a href="#" className="bg-gray-800 hover:bg-gray-700 w-10 h-10 rounded-full flex items-center justify-center transition-colors">
                  <FaTwitter className="h-5 w-5" />
                </a>
                <a href="#" className="bg-gray-800 hover:bg-gray-700 w-10 h-10 rounded-full flex items-center justify-center transition-colors">
                  <FaInstagram className="h-5 w-5" />
                </a>
                <a href="#" className="bg-gray-800 hover:bg-gray-700 w-10 h-10 rounded-full flex items-center justify-center transition-colors">
                  <FaLinkedin className="h-5 w-5" />
                </a>
              </div>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>&copy; {new Date().getFullYear()} TKIET Warananagar. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;

