import React, { createContext, useContext, useState } from 'react';

// Create a context for the app
const AppContext = createContext();

// Create a provider component
export const AppProvider = ({ children }) => {
  const [appState, setAppState] = useState({
    // Define your initial state here
    theme: 'light', // Example state
    language: 'en', // Example state
  });

  const toggleTheme = () => {
    setAppState((prevState) => ({
      ...prevState,
      theme: prevState.theme === 'light' ? 'dark' : 'light',
    }));
  };

  const setLanguage = (language) => {
    setAppState((prevState) => ({
      ...prevState,
      language,
    }));
  };

  return (
    <AppContext.Provider value={{ ...appState, toggleTheme, setLanguage }}>
      {children}
    </AppContext.Provider>
  );
};

// Create a custom hook to use the app context
export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
