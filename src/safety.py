def check_safety_risk(query):
    """
    Scans the user's message for crisis keywords.
    Returns a safe, hardcoded response if a risk is detected.
    Returns None if the message is safe.
    """
    crisis_keywords = [
        "suicide", "kill myself", "want to die", 
        "depression", "depressed", "panic attack", 
        "anxiety", "can't take it anymore", "hopeless"
    ]
    
    query_lower = query.lower()
    
    for word in crisis_keywords:
        if word in query_lower:
            return """
            🛑 **I am concerned about what you're sharing.**
            
            Please know that you are not alone. As an AI, I cannot provide the support you need right now, but there are people who can.
            
            **Campus Counseling Center:** (555) 010-2020 (Open 24/7)
            **National Crisis Lifeline:** 988
            
            Please reach out to one of these resources immediately. Your well-being is the most important thing.
            """
    
    return None