import './Footer.css'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="footer-logo">OTIS</div>
            <p>AI-powered security fortress</p>
          </div>
          <div className="footer-links">
            <a href="https://github.com/Senpai-Sama7/Otis" target="_blank" rel="noopener noreferrer">GitHub</a>
            <a href="https://github.com/Senpai-Sama7/Otis/blob/main/docs" target="_blank" rel="noopener noreferrer">Documentation</a>
            <a href="https://github.com/Senpai-Sama7/Otis/blob/main/LICENSE" target="_blank" rel="noopener noreferrer">License</a>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 Otis Framework. MIT License.</p>
        </div>
      </div>
    </footer>
  )
}
