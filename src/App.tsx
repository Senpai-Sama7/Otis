import { useEffect } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Hero from './components/Hero'
import About from './components/About'
import Capabilities from './components/Capabilities'
import Tech from './components/Tech'
import CTA from './components/CTA'
import Footer from './components/Footer'

gsap.registerPlugin(ScrollTrigger)

function App() {
  useEffect(() => {
    ScrollTrigger.refresh()
    return () => ScrollTrigger.getAll().forEach(t => t.kill())
  }, [])

  return (
    <div className="app">
      <Hero />
      <About />
      <Capabilities />
      <Tech />
      <CTA />
      <Footer />
    </div>
  )
}

export default App
