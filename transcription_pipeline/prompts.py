def generate_chunk_prompt(transcript):
    structure = f"""
  You are summarizing one chunk of a meeting transcript.

Rules:
- Do not guess names from speaker labels.
- Keep updates and action items attached only to the speaker explicitly associated with them.
- If a task owner is unclear, write 'unclear'.
- Preserve tangents only if they affect a decision, blocker, task, or meeting context.
- Do not invent missing context.
- Do not merge this chunk with previous chunks.
- Do not summarize away specific task details.
- Keep all concrete information from this chunk, including deadlines, blockers, decisions, tools, files, and task board changes.

Output:

1. Topics discussed in this chunk
- List the main topics covered.

2. Speaker updates
For each speaker mentioned:
- Speaker 1
    - Speaker label:
    - What they reported:
    - Blockers / concerns:
    - Relevant context:
- Speaker 2 (if exists)
    - Speaker label:
    - What they reported:
    - Blockers / concerns:
    - Relevant context:

3. Speaker-specific next tasks
For each task explicitly assigned:
-Task 1
    - Owner:
    - Task:
    - Deadline / timing (if present):
    - Confidence: high / medium / low

-Task 2 and up (if exist)
    - Owner:
    - Task:
    - Deadline / timing (if present):
    - Confidence: high / medium / low

4. Action board updates
For any task board / issue board / action board mentioned
- Task board item 1
    - Item:
    - Status change:
    - Owner, if explicit:
    - Notes:
- Task board item 2 and up (if exists)
    - Item:
    - Status change:
    - Owner, if explicit:
    - Notes:

5. Decisions and confirmations
- Decision 1
    - Decision:
    - Who confirmed it:
    - Impact:
- Decision 2 and up (if exists)
    - Decision:
    - Who confirmed it:
    - Impact:

6. Overall meeting notes
- Important discussion points that are not direct tasks.
- Include relevant tangents only if they affect understanding.


Following the structure above, summarize this chunk:

    {transcript}
    """

    return structure


def generate_final_prompt(chunks):
    structure = f"""
  You are summarizing one chunk of a meeting transcript.

Rules:
- Output valid JSON only.
- Do not include markdown.
- Do not include explanations outside the JSON.
- Do not guess names from speaker labels.
- Keep action items attached only to the person explicitly assigned.
- If a task owner is unclear, write "unclear."
- If a field has no information, use an empty array [] or "unclear".
- Preserve tangents only if they affect decisions, blockers, tasks, or meeting context.
- Do not lose concrete information from the transcript.


Return the summary using this exact JSON structure:

{{
  "meeting_overview": "<a short paragraph that summarizes the entire meeting concisely>"
  "topics_discussed": [
    {{
      "topic": "<main topic name>",
      "summary": "<short paragraph summary of this topic>",
      "key_details": [
        "<specific detail>",
        "<specific detail>"
      ]
    }}
  ],
  "speaker_updates": [
    {{
      "speaker": "<speaker label from transcript, e.g. SPEAKER_04>",
      "speaker_label": "<short functional label if explicit, otherwise 'unclear'>",
      "reported": [
        "<what this speaker reported>"
      ],
      "blockers_or_concerns": [
        "<blocker or concern, or empty array if none>"
      ],
      "relevant_context": [
        "<relevant context>"
      ]
    }}
  ],
  "speaker_specific_next_tasks": [
    {{
      "owner": "<speaker label, name if explicitly given, or 'unclear'>",
      "task": "<task explicitly assigned>",
      "deadline_or_timing": "<deadline/timing if present, otherwise 'unclear'>",
      "confidence": "<high | medium | low>"
    }}
  ],
  "action_board_updates": [
    {{
      "item": "<task board / issue board / action board item>",
      "status_change": "<status change>",
      "owner": "<owner if explicit, otherwise 'unclear'>",
      "source_chunks": [
        "<chunk_id>"
      ],
      "notes": [
        "<additional notes>"
      ]
    }}
  ],
  "decisions_and_confirmations": [
    {{
      "decision": "<decision made or confirmed>",
      "confirmed_by": "<speaker/person who confirmed it, otherwise 'unclear'>",
      "impact": "<impact of the decision>"
    }}
  ],
  "ambiguities": [
    {{
      "type": "<unclear_owner | unclear_deadline | conflicting_info | missing_context | other>",
      "description": "<what is ambiguous>",
      "related_speaker": "<speaker label or 'unclear'>",
      "related_topic": "<topic or 'unclear'>"
    }}
  ]
}}

The chunks that you will be given will be in this form {{Chunk 1: Summarization Text, Chunk 2: Summarization Text}}


Following the structure above, merge all chunks together:

{chunks}
  """
    
    return structure