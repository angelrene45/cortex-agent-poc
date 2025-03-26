# DASH_DB.DASH_SCHEMA


## Table: supply_chain (Supply Chain Data)
This table tracks the average shipping time of tire orders from different suppliers. It includes:
- The name of the vendor (supplier),
- And the average number of days it takes them to ship orders.

The purpose is to evaluate vendor performance, identify shipping delays, and support decisions to improve supply chain efficiency.


## Table: support_tickets (Customer Support Data)
This table captures data from customer service interactions, particularly around phone and internet services. It includes:

- Customer details (name, email),
- The type of service they’re using (e.g., Cellular, Business Internet),
- Their preferred contact method (email or text),
- And the full text of their support request (e.g., complaints, inquiries, or service changes).


The goal is to understand customer issues, track support trends, and enhance service quality through data analysis.


## Table: PARSED_PDFS
This table stores text extracted from PDF documents—specifically contracts and recycling policies from various vendors (e.g., Snowtires, City Motors, RubberWorks).

This enables downstream use in Cortex Search for tasks like:

- Finding contract clauses,
- Reviewing vendor terms,
- Accessing ESG/recycling policies directly via natural language search.



## Why Cortex Agents?

Cortex Agents simplify data access for business users by letting them ask questions in natural language instead of relying on rigid BI dashboards or waiting on data analysts. It’s like having a conversational interface for your data.

Under the hood it is a stateless REST API that unifies Cortex Search's hybrid search and Cortex Analyst's SQL generation (with 90%+ accuracy). It streamlines complex workflows by handling context retrieval, converting natural language to SQL via semantic models, and managing LLM orchestration and prompts.


## Questions 

### Support Tickets
- Can you show me a breakdown of customer support tickets by service type cellular vs business internet?

- How many unique customers have raised a support ticket with a 'Cellular' service type and have 'Email' as their contact preference?

- How many unique clients have raised a support ticket with a phone service type and have mail as their contact preference?

### Supply Chain (Cortext Analyst)
- What is the average shipping time for tires from Snowtires Automotive compared to average of our other suppliers?

### Cortex Search: Unstructured Data
- What are the payment terms for Snowtires?
- What's the latest, most effective way to recycle rubber tires?