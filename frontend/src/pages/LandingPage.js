import React, { useState, useEffect } from 'react';
import GuestNavbar from '../components/GuestNavbar';
import HeroSection from '../components/landing/HeroSection';
import AboutSection from '../components/landing/AboutSection';
import AchievementsSection from '../components/landing/AchievementsSection';
import EventsSection from '../components/landing/EventsSection';
import ActivitiesSection from '../components/landing/ActivitiesSection';
import TestimonialsSection from '../components/landing/TestimonialsSection';
import ContactSection from '../components/landing/ContactSection';
import Footer from '../components/landing/Footer';

const LandingPage = () => {
  const [isVisible, setIsVisible] = useState({});

  // Intersection Observer for animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(prev => ({ ...prev, [entry.target.id]: true }));
          }
        });
      },
      { threshold: 0.1 }
    );

    const elements = document.querySelectorAll('[data-animate]');
    elements.forEach(el => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-white">
      <GuestNavbar />
      <HeroSection isVisible={isVisible} scrollToSection={scrollToSection} />
      <AboutSection isVisible={isVisible} />
      <AchievementsSection isVisible={isVisible} />
      <EventsSection isVisible={isVisible} />
      <ActivitiesSection isVisible={isVisible} />
      <TestimonialsSection isVisible={isVisible} />
      <ContactSection isVisible={isVisible} />
      <Footer />
    </div>
  );
};

export default LandingPage;
