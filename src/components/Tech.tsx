import './Tech.css'

const tech = [
  { icon: '🤖', title: 'Transformer Models', desc: 'HuggingFace-based spam classification with attention mechanisms' },
  { icon: '🐍', title: 'Python Backend', desc: 'FastAPI inference server with security wrapping' },
  { icon: '☸️', title: 'Kubernetes', desc: 'Cloud-native deployment with pod security standards' },
  { icon: '🔄', title: 'CI/CD Pipeline', desc: 'GitHub Actions with automated security scanning' }
]

export default function Tech() {
  return (
    <section className="tech">
      <div className="container">
        <span className="label">Technology Stack</span>
        <h2 className="title">Production-ready infrastructure</h2>
        <div className="tech-grid asymmetric-grid">
          {tech.map((t, i) => (
            <div key={i} className={`glass-card ${i < 2 ? 'span-6' : 'span-6'}`}>
              <div className="tech-icon">{t.icon}</div>
              <h4>{t.title}</h4>
              <p>{t.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
