import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import Hero from './components/ui/Hero';
import Features from './components/ui/Features';
import About from './components/ui/About';
import Contact from './components/ui/Contact';
import './App.css';

function App() {
  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <Hero />
        <Features />
        <About />
        <Contact />
      </main>
      <Footer />
    </div>
  );
}

export default App;
