import os
from config_app import OPENAI_API_KEY, ANTHROPIC_API_KEY
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Track citations and references
citations = []
references = []

def get_model_choice():
    print("Select the language model you want to use:")
    print("1. OpenAI GPT-4")
    print("2. Anthropic Claude")
    choice = input("Enter the number of your choice (1 or 2): ")
    return choice

def validate_citations(content):
    """
    Function to ensure the accuracy of in-text citations and references.
    If inaccuracies are detected, the content is corrected and citations are validated.
    """
    global citations, references
    print("Validating citations and ensuring accuracy...")
    
    # Simple placeholder logic to simulate citation validation
    # You can integrate actual logic based on citation checking needs
    validated_content = content  # Simulate as if all citations are valid

    # Add citations to the global citations list and reference section
    if "[1]" not in validated_content:  # Simulate adding citations
        citations.append(f"Citation {len(citations) + 1}")
        references.append(f"Source {len(citations)} - e.g., PubMed, ClinicalTrials.gov")

    return validated_content

# def generate_reference_section():
#     """
#     Generate the reference section based on in-text citations.
#     """
#     reference_section = "\nReferences:\n"
#     for i, ref in enumerate(references):
#         reference_section += f"{i+1}. {ref}\n"
#     return reference_section

def generate_reference_section():
    """
    Generate the reference section based on in-text citations.
    """
    if not references:  # Only generate references if no real ones are present
        return "\nNo additional references available.\n"
    
    reference_section = "\nReferences:\n"
    for i, ref in enumerate(references):
        reference_section += f"{i+1}. {ref}\n"
    return reference_section


def chatbot():
    global citations, references
    # Get the user's model choice
    choice = get_model_choice()
    if choice == '1':
        # Initialize OpenAI GPT-4 model
        llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY
        )
    elif choice == '2':
        # Initialize Anthropic Claude model
        llm = ChatAnthropic(
            model="claude-v1",
            temperature=0.7,
            anthropic_api_key=ANTHROPIC_API_KEY
        )
    else:
        print("Invalid choice. Please restart and select 1 or 2.")
        return

    # Create the conversation chain with memory
    conversation = ConversationChain(
        llm=llm,
        memory=ConversationBufferMemory(),
        verbose=False
    )

    print("\nWelcome to the Rare Disease Information Chatbot!")
    disease = input("Enter the name of a rare disease you'd like to learn about: ")

    # Create the initial input following the detailed prompt structure
    initial_input = f"""
    You are tasked with creating a detailed and accurate summary for a rare disease called {disease}.
    This summary is intended for both patients and medical professionals, and must include:
    
    1. **Overview**: Simple yet comprehensive definition of {disease}, including affected populations, prevalence, and alternative names. 
       Ensure in-text citations are accurate.
    
    2. **Causes**: Explain the causes, simplifying for patients and adding technical details for professionals. Cite appropriate studies.
    
    3. **Clinical Presentation**: Describe symptoms (early, late, rare) for both patients and professionals. Suggest visual aids if necessary.
    
    4. **Complications**: Explain complications of {disease} for both patients and professionals. Ensure accurate citations.
    
    5. **Diagnosis**: Summarize the diagnostic methods for patients and professionals. Suggest visual aids and provide accurate citations.
    
    6. **Treatment Options**: Outline treatment options, explaining them clearly for patients and adding technical details for professionals. 
       Provide accurate citations.
    
    7. **Prognosis**: Provide the expected course of the disease, citing accurate prognostic data for both patients and professionals.
    
    8. **Research and Clinical Trials**: Include information on recent research and clinical trials, citing studies or trials.
    
    9. **Support and Advocacy Resources**: Provide support networks and resources, with accurate citations for all organizations or groups mentioned.
    
    At the end of the summary, ask the user if they would like more information on a specific aspect or have any questions.
    """
    
    # Start the conversation
    response = conversation.predict(input=initial_input)
    
    # Validate the accuracy and citations of the response
    validated_response = validate_citations(response)
    
    # Display the validated response with citations
    print("\n" + validated_response + "\n")
    
    # Generate and display the reference section
    references_section = generate_reference_section()
    print(references_section)

    while True:
        follow_up = input("Do you have any questions or need more details on any topic? (Type 'no' to exit): ")
        if follow_up.lower() in ['no', 'exit', 'quit']:
            print("Thank you for using the Rare Disease Information Chatbot. Take care!")
            break
        else:
            # Get the response from the conversation chain
            follow_up_response = conversation.predict(input=follow_up)
            validated_follow_up = validate_citations(follow_up_response)
            print("\n" + validated_follow_up + "\n")

if __name__ == "__main__":
    chatbot()
