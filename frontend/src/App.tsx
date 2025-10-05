import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import Hero from './components/ui/Hero';
import Features from './components/ui/Features';
import About from './components/ui/About';
import Contact from './components/ui/Contact';
import Register from './components/ui/Register';
import Login from './components/ui/Login';
import Account from './components/ui/Account';
import Dashboard from './components/ui/Dashboard';
import AddFriend from './components/ui/AddFriend';
import FriendRequests from './components/ui/FriendRequests';
import Leaderboard from './components/ui/Leaderboard';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Header />
          <Routes>
            <Route path="/" element={
              <main className="main-content">
                <Hero />
                <Features />
                <About />
                <Contact />
              </main>
            } />
            <Route path="/register" element={
              <main className="main-content">
                <Register />
              </main>
            } />
            <Route path="/login" element={
              <main className="main-content">
                <Login />
              </main>
            } />
            <Route path="/account" element={
              <main className="main-content">
                <Account />
              </main>
            } />
            <Route path="/dashboard" element={
              <main className="main-content">
                <Dashboard />
              </main>
            } />
            <Route path="/leaderboard" element={
              <main className="main-content">
                <Leaderboard />
              </main>
            } />
            <Route path="/add-friend" element={
              <main className="main-content">
                <AddFriend />
              </main>
            } />
            <Route path="/friend-requests" element={
              <main className="main-content">
                <FriendRequests />
              </main>
            } />
          </Routes>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
