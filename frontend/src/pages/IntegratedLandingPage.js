import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import GuestNavbar from '../components/GuestNavbar';
import Navbar from '../components/Navbar';
import HeroSection from '../components/landing/HeroSection';
import AboutSection from '../components/landing/AboutSection';
import AchievementsSection from '../components/landing/AchievementsSection';
import EventsSection from '../components/landing/EventsSection';
import ActivitiesSection from '../components/landing/ActivitiesSection';
import TestimonialsSection from '../components/landing/TestimonialsSection';
import ContactSection from '../components/landing/ContactSection';
import Footer from '../components/landing/Footer';
import StudentDashboard from '../components/landing/StudentDashboard';

const IntegratedLandingPage = () => {
  const { user, loading } = useAuth();
  const [isVisible, setIsVisible] = useState({});

  // Intersection Observer for animations
  useEffect(() => {
    // Initialize all sections as visible to prevent blank screens
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.target.id) {
            setIsVisible(prev => ({ ...prev, [entry.target.id]: true }));
          }
        });
      },
      { threshold: 0.1, rootMargin: '50px' }
    );

    const elements = document.querySelectorAll('[data-animate]');
    elements.forEach(el => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Conditional Navbar - Guest or Authenticated */}
      {user ? <Navbar /> : <GuestNavbar />}
      
      {/* Hero Section with personalized content for students */}
      <HeroSection 
        isVisible={isVisible} 
        scrollToSection={scrollToSection} 
        user={user}
      />
      
      {/* Student Dashboard - Only show for authenticated students */}
      {user && user.role === 'student' && (
        <StudentDashboard isVisible={isVisible} />
      )}
      
      {/* Public sections - Professional sequence */}
      <AboutSection isVisible={isVisible} />
      <ActivitiesSection isVisible={isVisible} />
      <AchievementsSection isVisible={isVisible} />
      <EventsSection isVisible={isVisible} />
      <TestimonialsSection isVisible={isVisible} />
      <ContactSection isVisible={isVisible} />
      <Footer />
    </div>
  );
};

export default IntegratedLandingPage;
