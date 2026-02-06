import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Debugger from './pages/Debugger';
import Study from './pages/Study';
import Analysis from './pages/Analysis';
import './App.css';

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />
                    <Route path="/debugger" element={
                        <ProtectedRoute>
                            <Debugger />
                        </ProtectedRoute>
                    } />
                    <Route path="/study" element={
                        <ProtectedRoute>
                            <Study />
                        </ProtectedRoute>
                    } />
                    <Route path="/analysis" element={
                        <ProtectedRoute>
                            <Analysis />
                        </ProtectedRoute>
                    } />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;


