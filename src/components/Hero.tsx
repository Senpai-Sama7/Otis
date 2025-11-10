import { useEffect, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Sphere, MeshDistortMaterial } from '@react-three/drei'
import { gsap } from 'gsap'
import * as THREE from 'three'
import './Hero.css'

function AnimatedSphere() {
  const meshRef = useRef<THREE.Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.getElapsedTime() * 0.2
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.3
    }
  })

  return (
    <Sphere ref={meshRef} args={[1, 100, 200]} scale={2.5}>
      <MeshDistortMaterial
        color="#00f5ff"
        attach="material"
        distort={0.5}
        speed={2}
        roughness={0.2}
        metalness={0.8}
      />
    </Sphere>
  )
}

export default function Hero() {
  const titleRef = useRef<HTMLHeadingElement>(null)
  const subtitleRef = useRef<HTMLParagraphElement>(null)
  const statsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
    
    tl.from(titleRef.current, {
      y: 100,
      opacity: 0,
      duration: 1.2,
      delay: 0.3
    })
    .from(subtitleRef.current, {
      y: 50,
      opacity: 0,
      duration: 1
    }, '-=0.6')
    .from(statsRef.current?.children || [], {
      y: 30,
      opacity: 0,
      duration: 0.8,
      stagger: 0.15
    }, '-=0.4')
  }, [])

  return (
    <section className="hero">
      <div className="hero-canvas">
        <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <pointLight position={[-10, -10, -5]} intensity={0.5} color="#7b2cbf" />
          <AnimatedSphere />
          <OrbitControls enableZoom={false} enablePan={false} />
        </Canvas>
      </div>
      
      <div className="hero-overlay" />
      
      <div className="hero-content">
        <div className="hero-text">
          <h1 ref={titleRef} className="hero-title">
            <span className="line">AI-Powered</span>
            <span className="line gradient-text">Security Fortress</span>
          </h1>
          <p ref={subtitleRef} className="hero-subtitle">
            Red/Blue team adversarial defense against evolving spam threats
          </p>
        </div>
        
        <div ref={statsRef} className="hero-stats asymmetric-grid">
          <div className="stat-card glass-card span-4">
            <div className="stat-number gradient-text">96%</div>
            <div className="stat-label">Detection Accuracy</div>
          </div>
          <div className="stat-card glass-card span-4">
            <div className="stat-number gradient-text">&lt;15%</div>
            <div className="stat-label">Evasion Rate</div>
          </div>
          <div className="stat-card glass-card span-4">
            <div className="stat-number gradient-text">6</div>
            <div className="stat-label">Attack Vectors</div>
          </div>
        </div>
      </div>
      
      <div className="scroll-indicator">
        <span>Scroll</span>
        <div className="scroll-line" />
      </div>
    </section>
  )
}
