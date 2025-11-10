import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'
import './About.css'

const cards = [
  { icon: '🔴', title: 'Red Team Offensive', desc: 'Proactive adversarial testing with 6 attack vectors: character obfuscation, semantic shifting, prompt injection, multilingual mixing, encoding evasion, and homograph substitution.' },
  { icon: '🛡️', title: 'Blue Team Defense', desc: 'Real-time threat detection with automated remediation. Detects homographs, script mixing, encoding anomalies, injection patterns, and confidence anomalies.' },
  { icon: '📊', title: 'NIST Compliance', desc: 'Built-in AI Risk Management Framework compliance with full audit trails, governance controls, and risk assessment capabilities.' }
]

export default function About() {
  const sectionRef = useRef<HTMLElement>(null)
  const cardsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from(cardsRef.current?.children || [], {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 70%',
          toggleActions: 'play none none reverse'
        },
        y: 80,
        opacity: 0,
        duration: 1,
        stagger: 0.2,
        ease: 'power3.out'
      })
    }, sectionRef)

    return () => ctx.revert()
  }, [])

  return (
    <section ref={sectionRef} className="about">
      <div className="container">
        <span className="label">What is Otis?</span>
        <h2 className="title">Enterprise-grade AI framework for spam detection with adversarial defense</h2>
        <div ref={cardsRef} className="about-grid asymmetric-grid">
          {cards.map((card, i) => (
            <div key={i} className={`glass-card ${i === 0 ? 'span-5' : i === 1 ? 'span-7' : 'span-12'}`}>
              <div className="card-icon">{card.icon}</div>
              <h3>{card.title}</h3>
              <p>{card.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
