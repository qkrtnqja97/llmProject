import React from "react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../../context/AuthContext";
import { CompanyProvider } from "../../context/CompanyContext";
import { ChatProvider } from "../../context/ChatContext";

interface AppProviderProps {
  children: React.ReactNode;
}

const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  return (
    <React.StrictMode>
      <BrowserRouter>
        <AuthProvider>
          <CompanyProvider>
            <ChatProvider>{children}</ChatProvider>
          </CompanyProvider>
        </AuthProvider>
      </BrowserRouter>
    </React.StrictMode>
  );
};

export default AppProvider;
