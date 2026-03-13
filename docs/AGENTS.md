# Agent Map

## Flow

Intake -> Research -> Scoring -> Notification -> Outreach -> Conversation -> Follow-up or Voice -> Pipeline

## Routing rules

- Score below 5: reject automatically and move to pipeline/lost handling.
- Score 5 to 7: notify rep and wait for approval.
- Score above 7: treat as approved/high-priority.
- Conversation intent ready_to_buy: route to pipeline.
- Conversation intent needs_call: route to voice.
- Otherwise: schedule follow-up.

## Agent responsibilities

- Intake: normalize channel payloads.
- Research: gather legitimacy signals with search.
- Scoring: compute numeric score and reasoning.
- Notification: alert rep over Telegram and wait for approval callbacks.
- Outreach: create first personalized reply.
- Conversation: track intent and sentiment.
- Follow-up: schedule sequence and stop when user re-engages.
- Voice: handle transfer logic and voice channel support.
- Pipeline: classify stage and estimate close probability.
