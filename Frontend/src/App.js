import React from 'react';
import { ConfigProvider, theme } from 'antd';
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import LandingPage from './components/landing_page/LandingPage';
import "./App.css"
import Login from './components/login/Login';
import Language from './components/language/Language';


const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/language",
    element: <Language />,
  }
]);

const App: React.FC = () => (
  <div className='w-[100vh] h-[100vh]'>
  <ConfigProvider
    theme={{
      // 1. Use dark algorithm
      algorithm: theme.lightAlgorithm,

    }}
  >
    <RouterProvider router={router} />
  </ConfigProvider>
  </div>
);

export default App;