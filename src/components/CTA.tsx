import './CTA.css'

export default function CTA() {
  return (
    <section className="cta">
      <div className="container">
        <div className="cta-content glass">
          <h2 className="cta-title">Deploy enterprise security today</h2>
          <p className="cta-subtitle">Open source • Production ready • NIST compliant</p>
          <div className="cta-buttons">
            <a href="https://github.com/Senpai-Sama7/Otis" target="_blank" rel="noopener noreferrer" className="btn-primary">
              View on GitHub
            </a>
            <a href="https://github.com/Senpai-Sama7/Otis/blob/main/docs/USER_MANUAL.md" target="_blank" rel="noopener noreferrer" className="btn-secondary">
              Documentation
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
