# Database Overview: DASH_DB.DASH_SCHEMA

This database consolidates key data across three business areas: supply chain, customer support, and unstructured vendor documents.


## supply_chain (Supply Chain Data)

Tracks the average shipping time for tire orders from different vendors.
Purpose: Evaluate vendor performance, identify delays, and optimize supply chain efficiency.

### Questions 

- What is the average shipping time for tires from Snowtires Automotive compared to average of our other suppliers?


## support_tickets (Customer Support Data)

Captures customer interactions related to phone and internet services.
Includes:

- Customer details (name, email),
- The type of service they’re using (e.g., Cellular, Business Internet),
- Their preferred contact method (email or text),
- And the full text of their support request (e.g., complaints, inquiries, or service changes).

The goal is to understand customer issues, track support trends, and enhance service quality through data analysis.


### Questions 

- Can you show me a breakdown of customer support tickets by service type cellular vs business internet?

- How many unique customers have raised a support ticket with a Cellular service type and have Email as their contact preference?




## PARSED_PDFS (Vendor Document Text)
Stores extracted text from PDF documents like contracts and recycling policies from vendors.

Purpose: Search contract clauses, recycling policies using natural language.


### Questions 
- What are the payment terms for Snowtires?
- What's the latest, most effective way to recycle rubber tires?