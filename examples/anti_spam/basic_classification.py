"""
Basic Anti-Spam Classification Example

This example demonstrates simple spam detection using the Otis anti-spam model
with security features enabled.
"""

from src.model.inference_engine import OtisInferenceEngine


def basic_spam_classification():
    """Basic example of spam classification with security features."""
    print("=== Basic Anti-Spam Classification ===\n")
    
    # Initialize the secure anti-spam engine
    engine = OtisInferenceEngine(
        model_name="Titeiiko/OTIS-Official-Spam-Model",  # Using mock for example
        blue_team_enabled=True,      # Enable threat detection
        red_team_monitoring=False    # Disable during normal operation
    )
    
    # Test emails to classify
    test_emails = [
        "Congratulations! You've won a prize. Click here to claim now!",
        "Hi team, just wanted to confirm Monday's meeting at 3pm.",
        "URGENT: Your account will be closed. Verify now at http://suspicious-link.com",
        "Your monthly statement is available in the secure portal."
    ]
    
    print("Classifying emails:\n")
    
    for i, email in enumerate(test_emails, 1):
        print(f"{i}. Email: {email[:50]}{'...' if len(email) > 50 else ''}")
        
        # Classify the email
        result = engine.predict(email)
        
        # Display results
        print(f"   Classification: {result['label']}")
        print(f"   Confidence: {result['score']:.3f}")
        
        # Check for security events
        if 'security_event_id' in result:
            print(f"   ⚠️  Security Alert: {result['security_event_id']}")
        
        print()


def batch_classification_example():
    """Example of batch processing multiple emails."""
    print("=== Batch Classification Example ===\n")
    
    engine = OtisInferenceEngine(
        model_name="Titeiiko/OTIS-Official-Spam-Model",
        blue_team_enabled=True
    )
    
    # Large batch of emails
    emails = [
        "Meeting reminder for tomorrow",
        "CONGRATULATIONS! You won %21%40%23 prize",
        "Project status update attached",
        "FREE MONEY! Click 𝟘 here fast",
        "Lunch scheduled for Friday",
        "Verify account IMMEDIATELY or closed",
        "Q4 budget proposal ready for review",
        "URGENT: Security breach detected"
    ]
    
    print(f"Processing {len(emails)} emails in batch...\n")
    
    # Process in batch
    results = engine.predict_batch(emails, batch_size=4)
    
    spam_count = 0
    legitimate_count = 0
    security_alerts = 0
    
    for i, (email, result) in enumerate(zip(emails, results)):
        print(f"{i+1}. {result['label']} ({result['score']:.3f}) - {email[:30]}...")
        
        if result['label'] == 'SPAM':
            spam_count += 1
        else:
            legitimate_count += 1
            
        if 'security_event_id' in result:
            security_alerts += 1
    
    print(f"\nResults: {spam_count} spam, {legitimate_count} legitimate")
    print(f"Security alerts triggered: {security_alerts}")


if __name__ == "__main__":
    basic_spam_classification()
    print("\n" + "="*50 + "\n")
    batch_classification_example()