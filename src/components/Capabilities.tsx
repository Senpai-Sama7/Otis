import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'
import './Capabilities.css'

const capabilities = [
  { num: '01', title: 'Adversarial Attack Engine', desc: 'MDP-based multi-turn attack orchestration that adapts based on model feedback.', tags: ['Character obfuscation', 'Semantic preservation', 'Multi-turn chains'] },
  { num: '02', title: 'Threat Detection Pipeline', desc: 'Real-time analysis with pre/post-model inference security checks.', tags: ['6 specialized detectors', 'Tiered response', 'Anomaly detection'] },
  { num: '03', title: 'Compliance Framework', desc: 'NIST AI RMF implementation with MAP, MEASURE, MANAGE, and GOVERN functions.', tags: ['Risk quantification', 'Control implementation', 'Governance oversight'] }
]

export default function Capabilities() {
  const sectionRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('.capability-item', {
        scrollTrigger: { trigger: sectionRef.current, start: 'top 60%' },
        x: -100,
        opacity: 0,
        duration: 1,
        stagger: 0.3,
        ease: 'power3.out'
      })
    }, sectionRef)
    return () => ctx.revert()
  }, [])

  return (
    <section ref={sectionRef} className="capabilities">
      <div className="container">
        <span className="label">Core Capabilities</span>
        <h2 className="title">Three-layer security architecture</h2>
        <div className="capabilities-list">
          {capabilities.map((cap, i) => (
            <div key={i} className="capability-item glass-card">
              <div className="cap-number">{cap.num}</div>
              <div className="cap-content">
                <h3>{cap.title}</h3>
                <p>{cap.desc}</p>
                <div className="tags">
                  {cap.tags.map((tag, j) => (
                    <span key={j} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
