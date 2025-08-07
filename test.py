from extractor import extract_thesis

sample_post = """
Artificial Intelligence is transforming every industry. From healthcare to education, its influence is growing. 
However, concerns about ethics and bias remain. Responsible development is crucial to avoid unintended harm. 
Open source communities are leading the way in transparent AI development.
"""

thesis = extract_thesis(sample_post)

print("Thesis Sentences:")
for sentence in thesis:
    print("-", sentence)
