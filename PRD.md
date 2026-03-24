# PRD: Agentic Lead Generation and Scheduling for SMBs

---

## Problem Alignment

### Introduction and Opportunity

The rise of chatbots and agentic AI has reshaped how businesses engage with customers for sales and service delivery. While large enterprises rely on dedicated CRM software and catalog-driven platforms with integrated AI capabilities, the majority of SMBs in India continue to operate primarily through WhatsApp and phone calls. Both business owners and customers prefer simple, conversational communication over migration to complex interfaces.

This presents an opportunity to bring agentic capabilities directly into the communication channels SMBs already use without forcing them to adapt to heavy and unfamiliar systems.

---

### Existing Pain Points

- Fragmented processing where lead capture and fulfilment are handled separately.
- Leads are often lost during non-functioning hours and when the admin is away.
- N-number of repeated queries overwhelms the admin.
- Manual replies are slow without any structured follow-up strategy, whereas static auto replies do not capture customer context.

---

## Background and Evidence

### Current Market

- Globally, over **50M+ organizations** use instant messengers like WhatsApp as part of their CRM toolkit.
- This is further amplified in markets like India and Brazil where there are **550M+ WhatsApp users** (Source: Meta).
- ~**78% of Indian SMBs** (Source: HyperleapAI) use WhatsApp and phone calls to communicate with customers and generate leads.
- **65% of businesses report increased sales**.
- **72% of customers prefer instant chat over email** for business communication.

---

### Top Triggers for Businesses

1. Seamless CRM integration  
2. Automation and agentic control with unlimited conversation capacity  
3. 24/7 availability  
4. Better response speed affecting revenue and retention  

---

### Top Use Cases

1. Order tracking, product recommendations  
2. Appointment booking  
3. Enquiries and enrollment  
4. Returns, exchanges and product info  

---

## Solution Summary

### Product Overview

1. Custom-built agents that integrate with WhatsApp and phone calls to handle routine customer interactions  
2. Context-aware automation that understands target business workflows and executes tasks  
3. Seamless transition from agentic to manual support within the same conversation  
4. Lightweight and tailored for SMBs, requiring minimal setup and infrastructure  

---

## Core Functionalities (V1)

This version focuses on support, product/service overview, and autonomous appointment scheduling. Additional use cases will be added in future iterations.

1. **Lead Capture and Handling**  
   Agents handle first customer interaction over WhatsApp or calls, understand intent, and resolve general queries along with product/service catalog browsing.

2. **Structured Data Extraction**  
   Automatically converts conversations into structured customer data (name, requirement, etc., depending on use case).

3. **Intelligent Appointment Scheduling Agent**  
   Autonomously books appointments aligned with business availability and customer preferences.

4. **Smart Manual Triggers and Override**  
   Allows a business operator to step into the same conversation at any point and flags conversations requiring human intervention.

5. **Business Knowledge Configuration Layer**  
   Enables businesses to define context (services/products, FAQs, stock availability, policies) so the agent stays accurate and grounded.

---

### Additional

- **Insights and Analytics Layer**  
  Businesses can view metrics on leads converted, retention, sales, etc.

---

## Key Design Principles

1. Prioritize automation while allowing human override in critical scenarios with **0% compromise on customer experience**  
2. Focus on grounded AI agents with guardrails to minimize hallucinations  
3. Ensure complete trust and transparency where stakeholders know when AI vs humans are acting  

---

## Target Users (V1)

### User 1: Salon Client

- **Personality**: Organized, hates delays, values convenience  

**User Story:**

1. I want to engage quickly through WhatsApp so my schedule isn’t disrupted  
2. I want all information in one place without navigating complex apps/websites  
3. I prefer real-time appointment updates and cancellations  

---

### User 2: Salon Manager

- **Personality**: Customer-first, busy, open to automation but quality-conscious  

**User Story:**

1. I want initial customer interactions handled autonomously so no leads are missed  
2. I want customer data captured seamlessly without manual effort  
3. Repeated queries overwhelm me; I want automated FAQ handling  
4. I want full control to step into any conversation manually  
5. I should be able to modify services and pricing anytime  

---

## Non-Target Users

1. Large enterprises with dedicated CRM/ERP solutions  
2. Businesses with highly complex services requiring multi-step approvals and deep personalization  

---

## Definition of Success (V1)

1. High scheduling efficiency with no double bookings and minimal wait times  
2. Improved lead generation with reduced no-responses and accurate data capture  
3. Reduced operational effort in scheduling, follow-ups, and data entry  
4. Seamless human-AI collaboration with positive customer experience  
5. Ease of use for business owners  

---

## Risks & Open Questions

### Dependency Risks

1. Policy changes by external API providers (e.g., WhatsApp, Twilio) may cause disruptions  
2. Unreliable internet connectivity may interrupt AI interactions  
3. AI model updates or deprecations may lead to outages  

---

### Challenges

1. Normalizing business data and workflows to provide accurate context to the agentic system  
2. Ensuring hallucination-free and compliant AI  
3. Maintaining personalization with stateful interactions over time  
4. Ensuring data security and compliance with DPDP regulations  
5. Scaling performance as conversations and data grow  
