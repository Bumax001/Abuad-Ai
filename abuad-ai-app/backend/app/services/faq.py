# Small verified starter knowledge base.
# Replace/extend this with information extracted from official ABUAD documents.

FAQS = [
    {
        "keywords": ["location", "where is abuad", "where is afe babalola"],
        "answer": "Afe Babalola University (ABUAD) is located in Ado-Ekiti, Ekiti State, Nigeria."
    },
    {
        "keywords": ["founder", "who founded abuad"],
        "answer": "Afe Babalola University was founded by Aare Afe Babalola, SAN."
    },
    {
        "keywords": ["computer science", "computer science course"],
        "answer": "Computer Science is offered at ABUAD. For the current programme structure, entry requirements, and fees, use the latest official university documents or admissions office information."
    },
    {
        "keywords": ["school fees", "tuition", "fees"],
        "answer": "ABUAD fees vary by programme and student category. I should not guess the current amount; use the latest official fee schedule for your academic session."
    },
    {
        "keywords": ["admission", "apply", "application"],
        "answer": "Admission requirements depend on the entry route and programme. The current official admission guide should be used for exact requirements and deadlines."
    },
]

def faq_lookup(message: str) -> str | None:
    q = message.lower()
    for item in FAQS:
        if any(k in q for k in item["keywords"]):
            return item["answer"]
    return None
