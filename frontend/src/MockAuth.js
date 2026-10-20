// Mock authentication for testing without backend
export const mockAuth = {
  login: async (email, password) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock successful login for admin
    if (email === 'admin@example.com' && password === 'password123') {
      const user = {
        id: '1',
        email: 'admin@example.com',
        name: 'Admin User',
        role: 'admin'
      };
      localStorage.setItem('token', 'mock_token_123');
      localStorage.setItem('user', JSON.stringify(user));
      return { success: true, user };
    }
    
    // Mock successful login for any other email/password
    if (email && password) {
      const user = {
        id: '2',
        email: email,
        name: email.split('@')[0],
        role: 'student'
      };
      localStorage.setItem('token', 'mock_token_456');
      localStorage.setItem('user', JSON.stringify(user));
      return { success: true, user };
    }
    
    return { success: false, error: 'Invalid credentials' };
  },
  
  register: async (userData) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock successful registration
    const user = {
      id: Date.now().toString(),
      email: userData.email,
      name: userData.name,
      role: userData.role || 'student'
    };
    localStorage.setItem('token', 'mock_token_789');
    localStorage.setItem('user', JSON.stringify(user));
    return { success: true, user };
  },
  
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};
