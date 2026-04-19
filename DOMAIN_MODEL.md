# DOMAIN_MODEL.md

## Core entities

### Workspace
Top-level logical container

### Project
Scoped knowledge space for a specific customer/team/use case

### Conversation
Represents a call, chat, or ticket thread

Suggested fields:
- id
- project_id
- conversation_id_external
- channel (call/chat/ticket)
- agent_id
- customer_id
- started_at
- ended_at
- language
- raw_text
- normalized_text
- status
- created_at
- updated_at

### ConversationChunk
- id
- conversation_id
- chunk_index
- content
- char_start
- char_end
- token_estimate

### ComplianceCheck
- id
- conversation_id
- check_type
- result
- confidence
- evidence_chunk_id
- explanation

### Insight
- id
- conversation_id
- intent
- sentiment
- frustration_score
- escalation_risk
- churn_risk
- summary

### AskRun
- id
- project_id
- query
- answer
- status
- latency_ms
- retrieved_chunk_ids
- reranked_chunk_ids
- cited_chunk_ids
- created_at

### AskRunCitation
- id
- ask_run_id
- chunk_id
- source_filename
- snippet
- citation_order

### AskRunFeedback
- id
- ask_run_id
- rating
- comment
- created_at
