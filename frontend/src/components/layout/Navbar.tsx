import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import HealthIndicator from './HealthIndicator';

const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/practice', label: 'Practice' },
  { path: '/arcade', label: 'Arcade' },
];

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="glassmorphism sticky top-0 z-50 mb-8">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center">
            <span className="text-2xl font-bold neon-text">HagXwon</span>
          </Link>
          
          <div className="flex items-center space-x-6">
            <div className="hidden md:flex space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`btn-futuristic ${
                    location.pathname === item.path ? 'neon-glow' : ''
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
            <HealthIndicator />
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
