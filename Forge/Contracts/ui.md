# UI Contract: OthelloMini
**Ethics-First Multi-Agent AI Life Intelligence Platform**

---

## 1. App Shell & Layout

### 1.1 Overall Structure
The application follows a **chat-first, transparency-on-demand** architecture. The primary interface is a clean, full-screen conversational view with optional expandable panels for advanced transparency and control.

**Core Layout Pattern:**
```
┌─────────────────────────────────────────────────────────┐
│  [Header Bar - Minimal]                        [☰ Menu] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                                                         │
│          Chat Interface (Primary)                       │
│          - User messages (right-aligned)                │
│          - FELLO responses (left-aligned)               │
│          - Inline consent cards                         │
│          - Action suggestions                           │
│                                                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  [Input Bar with Send]                                  │
└─────────────────────────────────────────────────────────┘
```

**With Transparency Panel (Optional):**
```
┌────────────────────────────┬────────────────────────────┐
│                            │                            │
│   Chat Interface           │   Transparency Panel       │
│   (Primary - 65%)          │   (Collapsible - 35%)      │
│                            │                            │
│                            │   - Agent Reasoning        │
│                            │   - Ethical Validation     │
│                            │   - Digital Shadow Insight │
│                            │                            │
└────────────────────────────┴────────────────────────────┘
```

### 1.2 Navigation Structure

**Primary Navigation (Hamburger Menu):**
- **Chat** (Home/Default) — Main conversation interface
- **Digital Shadow** — User psychological profile summary
- **Consent Dashboard** — Autonomy tier controls and action history
- **Settings** — Preferences, integrations, data controls
- **Help & Safety** — Documentation, safety controls, data export

**Navigation Behavior:**
- Hamburger menu slides in from left (mobile) or appears as overlay (desktop)
- Navigation preserves chat context when switching views
- Back button returns to chat from any secondary screen
- Menu closes automatically on selection (mobile)

### 1.3 Responsive Breakpoints
- **Mobile (< 640px):** Single-column, full-screen chat, collapsible panels as modal overlays
- **Tablet (640px - 1024px):** Chat + optional side panel (triggered by icon)
- **Desktop (> 1024px):** Chat with persistent side panel option, wider input area

---

## 2. Screens/Views

### 2.1 Chat Interface (Primary Screen)

**Purpose:** Core conversational interaction with FELLO, including inline consent prompts and action suggestions.

**Layout Elements:**
- **Header Bar:**
  - App logo/name (left)
  - Current autonomy tier indicator (subtle badge)
  - Transparency toggle button (eye icon)
  - Menu button (hamburger icon)
  
- **Message Stream:**
  - Scrollable chat history
  - User messages: right-aligned, distinct background
  - FELLO messages: left-aligned, conversational tone
  - Inline consent cards embedded in conversation flow
  - Action suggestion cards with approve/deny controls
  - Timestamps (subtle, on-demand hover)
  - Typing indicator during AI processing
  
- **Input Area:**
  - Multi-line text input (auto-expanding up to 4 lines)
  - Send button (paper plane icon)
  - Voice input button (optional Phase 2)
  - Attachment button (minimal, for future context sharing)

**Key Interactions:**
- Scroll to load history
- Tap consent card actions (Approve/Deny/Adjust)
- Long-press messages for context menu (copy, flag, request explanation)
- Pull-to-refresh for new context awareness

**Visual Treatment:**
- Deep navy/charcoal background (#1A1F2E base)
- User messages: subtle elevated background (#2A3140)
- FELLO messages: slightly lighter background (#242938)
- High-contrast white text (#FFFFFF) for readability
- Soft teal (#4ECDC4) for consent prompts and affirmative actions
- Soft amber (#F7B731) for warnings or tier escalations

---

### 2.2 Digital Shadow Screen

**Purpose:** Transparent view into the AI's understanding of the user's psychological profile, tracked traits, and behavioral patterns.

**Layout Elements:**
- **Header:** "Your Digital Shadow" + last updated timestamp
- **Profile Summary Card:**
  - Key traits (top 5-7 identified characteristics)
  - Confidence indicators (subtle progress bars)
  - Dominant mood trends (last 7/30 days)
  
- **Sub-Agent Insights Sections:**
  - **Trait Tracker:** Personality dimensions, communication style
  - **Behavior Observer:** Routines, decision patterns, habits
  - **Aspiration Mapper:** Goals, values, priorities
  - **Mood Analyzer:** Emotional state trends, triggers
  
- **Data Controls:**
  - "Request Explanation" button per insight
  - "Correct This" option to flag inaccuracies
  - "Privacy Settings" link to control what's tracked

**Key Interactions:**
- Expand/collapse sections for detail
- Tap insight cards for deeper reasoning
- Edit or flag incorrect observations
- View historical changes (timeline mode)

**Visual Treatment:**
- Organized card layout with clear hierarchy
- Soft shadows for depth without clutter
- Iconography for each sub-agent (consistent with brand)
- Data visualization: simple bar charts, trend lines (minimal, not dashboard-heavy)

---

### 2.3 Consent Dashboard

**Purpose:** Central control for autonomy tiers, action approval history, and ethical boundary management.

**Layout Elements:**
- **Header:** "Consent & Autonomy"
- **Current Tier Selector:**
  - Four-tier radio/segmented control:
    - **Passive** (only responds when asked)
    - **Suggestive** (offers ideas, waits for approval)
    - **Active** (can nudge and remind with consent)
    - **Autonomous** (executes approved patterns without asking)
  - Description of each tier below selector
  
- **Pending Actions Card:**
  - List of actions awaiting user approval
  - Quick approve/deny controls
  - Countdown timers for time-sensitive suggestions
  
- **Action History:**
  - Scrollable list of past suggestions and approvals
  - Filters: All / Approved / Denied / Auto-executed
  - Timestamps and action outcomes
  
- **Ethical Override Settings:**
  - Toggle switches for specific boundaries (e.g., "Never schedule before 8 AM", "Always ask before social interventions")
  - Link to detailed safety settings

**Key Interactions:**
- Slide to change autonomy tier (with confirmation prompt)
- Swipe actions to approve/deny
- Tap history items for full context
- Toggle override switches with immediate feedback

**Visual Treatment:**
- Clear tier visualization (color-coded: green → yellow → amber → orange)
- Pending actions highlighted with soft pulsing border
- History items in chronological reverse order with distinct approved/denied states
- Large, touch-friendly controls

---

### 2.4 Settings Screen

**Purpose:** Configure app preferences, integrations, data management, and account settings.

**Layout Elements:**
- **Header:** "Settings"
- **Sections (Expandable Accordion):**
  - **Profile:** Name, avatar, contact preferences
  - **Integrations:** Calendar, email, wellness apps (Phase 2)
  - **Notifications:** Push, email, consent prompt alerts
  - **Privacy & Data:** Export data, delete account, tracking preferences
  - **Appearance:** Dark/light mode (default dark), font size
  - **About:** Version, terms, privacy policy, feedback

**Key Interactions:**
- Tap sections to expand
- Toggle switches for binary options
- Navigation to sub-screens for complex settings
- "Export My Data" triggers download
- "Delete Account" requires confirmation flow

**Visual Treatment:**
- Clean list layout with clear grouping
- Icons for each section
- Toggle switches and chevrons for navigation
- Destructive actions (delete) in red accent

---

### 2.5 Onboarding Flow (First-Time User)

**Purpose:** Welcome new users, establish initial consent tier, and gather baseline context for personalization.

**Screens:**
1. **Welcome Screen:**
   - Othello/FELLO branding
   - Tagline: "Your ethics-first AI life companion"
   - "Get Started" button
   
2. **Consent Introduction:**
   - Explanation of four-tier autonomy model
   - Visual diagram of tiers
   - "I understand" confirmation
   
3. **Initial Tier Selection:**
   - Choose starting tier (default: Suggestive)
   - Brief description of what to expect
   - "Continue" button
   
4. **Optional Context Gathering:**
   - "Tell me about yourself" open-ended input
   - Skip option clearly visible
   - "This helps me understand you better" explanation
   
5. **Ready Screen:**
   - "Your AI is ready"
   - "Start Chatting" button → Main Chat Interface

**Key Interactions:**
- Swipe or tap "Next" to progress
- Back button to review previous steps
- Skip option for optional screens
- Progress indicator at top (5 dots/steps)

**Visual Treatment:**
- Large, friendly illustrations
- Generous whitespace
- Clear primary CTA buttons
- Warm, welcoming tone in copy

---

## 3. Component List

### 3.1 Core Reusable Components

**MessageBubble**
- **Purpose:** Display chat messages from user or FELLO
- **Props:** `message` (text), `sender` (user/ai), `timestamp`, `status` (sending/sent/error)
- **Variants:** User (right-aligned, teal accent), FELLO (left-aligned, neutral)
- **States:** Default, sending (animated), error (red border)

**ConsentCard**
- **Purpose:** Inline consent prompt for actions requiring approval
- **Props:** `action` (description), `tier` (which tier triggered it), `onApprove`, `onDeny`, `onAdjust`
- **Layout:** Card with action description, tier badge, three-button row (Approve/Deny/Adjust)
- **Variants:** Standard, Urgent (amber border), Autonomous preview (green border)
- **States:** Pending, Approved (collapsed with checkmark), Denied (collapsed with X), Expired

**ActionSuggestionCard**
- **Purpose:** Proactive suggestion from RealityAgent
- **Props:** `suggestion` (text), `reasoning` (why), `impact` (expected outcome), `onAccept`, `onDismiss`, `onLearnMore`
- **Layout:** Card with suggestion headline, brief reasoning, "Why this?" expandable, action buttons
- **Variants:** Goal-related (teal accent), Routine (neutral), Mood intervention (amber accent)
- **States:** Active, Accepted (success feedback), Dismissed (fade out), Expanded (showing full reasoning)

**InsightCard**
- **Purpose:** Display Digital Shadow insights (traits, behaviors, aspirations)
- **Props:** `title`, `content`, `confidence` (0-1), `subAgent` (which agent detected), `onExplain`, `onFlag`
- **Layout:** Card with icon, title, content text, confidence bar, action links
- **Variants:** Trait, Behavior, Aspiration, Mood
- **States:** Default, Expanded (full detail), Flagged (sent for review)

**TierSelector**
- **Purpose:** Choose autonomy tier
- **Props:** `currentTier`, `onChange`, `showDescriptions` (bool)
- **Layout:** Segmented control or vertical radio list with descriptions
- **Variants:** Compact (segmented), Detailed (radio + descriptions)
- **States:** Passive, Suggestive, Active, Autonomous (each selectable)

**Button**
- **Purpose:** Primary interactive element
- **Props:** `label`, `variant`, `size`, `disabled`, `loading`, `onClick`
- **Variants:** Primary (teal), Secondary (outlined), Destructive (red), Ghost (text only)
- **Sizes:** Small, Medium, Large
- **States:** Default, Hover, Active, Disabled, Loading (spinner)

**IconButton**
- **Purpose:** Icon-only actions (menu, send, toggle)
- **Props:** `icon`, `label` (accessibility), `onClick`, `active`
- **Variants:** Default, Active (highlighted)
- **States:** Default, Hover, Active, Disabled

**ToggleSwitch**
- **Purpose:** Binary setting controls
- **Props:** `checked`, `onChange`, `label`, `disabled`
- **Variants:** Default (teal when on), Destructive (red when on, for dangerous settings)
- **States:** Off, On, Disabled

**ProgressBar**
- **Purpose:** Show confidence levels, loading states
- **Props:** `value` (0-1), `color`, `label`
- **Variants:** Linear, Circular (for mini indicators)
- **States:** Determinate, Indeterminate (animated)

**Modal**
- **Purpose:** Overlay dialogs for confirmations, details, settings
- **Props:** `title`, `content`, `actions` (button array), `onClose`
- **Variants:** Standard, Full-screen (mobile), Drawer (slide-in panel)
- **States:** Open, Closed, Animating

**TabBar** (Mobile Navigation)
- **Purpose:** Bottom navigation for primary sections (mobile only)
- **Props:** `tabs` (array of {label, icon, route}), `activeTab`
- **Layout:** Fixed bottom bar, 3-4 tabs with icons and labels
- **Variants:** Compact (icons only), Labeled (icon + text)
- **States:** Active tab highlighted

**LoadingSpinner**
- **Purpose:** Indicate processing/loading
- **Props:** `size`, `color`
- **Variants:** Small (inline), Medium (default), Large (full-screen overlay)
- **States:** Spinning animation

**TransparencyPanel**
- **Purpose:** Collapsible side panel for agent reasoning and ethical validation
- **Props:** `currentMessage`, `agentTrace`, `ethicalChecks`, `onClose`
- **Layout:** Vertical panel with sections: Reasoning, Validation, Digital Shadow Context
- **Variants:** Collapsed (icon only), Expanded (full panel)
- **States:** Hidden, Visible, Pinned

---

### 3.2 Specialized Components

**AutonomyTierBadge**
- **Purpose:** Visual indicator of current autonomy tier
- **Props:** `tier`
- **Variants:** Passive (gray), Suggestive (blue), Active (teal), Autonomous (amber)
- **States:** Static display

**EthicalValidationIndicator**
- **Purpose:** Show ethical check status on messages/actions
- **Props:** `status` (passed/flagged/overridden)
- **Variants:** Passed (green checkmark), Flagged (amber warning), Overridden (red shield)
- **States:** Default, Hover (shows detail tooltip)

**TypingIndicator**
- **Purpose:** Show FELLO is composing response
- **Layout:** Three animated dots
- **Variants:** Default (subtle animation)
- **States:** Animating

**MessageContextMenu**
- **Purpose:** Long-press/right-click actions on messages
- **Props:** `message`, `onCopy`, `onFlag`, `onExplain`, `onDelete`
- **Layout:** Floating menu with action list
- **Variants:** User message actions, FELLO message actions
- **States:** Open, Closed

**TimelineView**
- **Purpose:** Show historical changes in Digital Shadow
- **Props:** `events` (array of timestamped insights)
- **Layout:** Vertical timeline with nodes for events
- **Variants:** Compact, Detailed
- **States:** Default, Filtered

---

## 4. Visual Style

### 4.1 Color Palette

**Base Colors:**
- **Primary Background:** `#1A1F2E` (Deep navy/charcoal)
- **Secondary Background:** `#242938` (Slightly lighter for cards)
- **Elevated Background:** `#2A3140` (User messages, raised elements)
- **Surface:** `#343B4F` (Modals, overlays)

**Accent Colors:**
- **Primary Accent (Teal):** `#4ECDC4` (Consent prompts, affirmative actions, links)
- **Secondary Accent (Amber):** `#F7B731` (Warnings, tier escalations, urgent actions)
- **Success:** `#6BCF7F` (Approved actions, positive feedback)
- **Error/Destructive:** `#E74C3C` (Errors, denials, delete actions)

**Text Colors:**
- **Primary Text:** `#FFFFFF` (High contrast, main content)
- **Secondary Text:** `#B4B9C8` (Labels, metadata, timestamps)
- **Disabled Text:** `#6B7280` (Disabled controls, inactive elements)

**Tier-Specific Colors:**
- **Passive:** `#6B7280` (Gray)
- **Suggestive:** `#3B82F6` (Blue)
- **Active:** `#4ECDC4` (Teal)
- **Autonomous:** `#F7B731` (Amber)

### 4.2 Typography

**Font Family:**
- **Primary:** `Inter` (system fallback: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`)
- **Monospace (for technical details):** `JetBrains Mono` (fallback: `"Courier New", monospace`)

**Type Scale:**
- **H1 (Page Titles):** 32px / 2rem, weight 700, line-height 1.2
- **H2 (Section Titles):** 24px / 1.5rem, weight 600, line-height 1.3
- **H3 (Card Titles):** 18px / 1.125rem, weight 600, line-height 1.4
- **Body (Default):** 16px / 1rem, weight 400, line-height 1.6
- **Body Small:** 14px / 0.875rem, weight 400, line-height 1.5
- **Caption:** 12px / 0.75rem, weight 400, line-height 1.4
- **Button Text:** 16px / 1rem, weight 500, line-height 1.2

**Text Rendering:**
- Anti-aliasing: enabled for smooth rendering
- Letter-spacing: Default for body, -0.02em for headings
- Text color contrast ratio: minimum 4.5:1 for accessibility

### 4.3 Spacing & Layout

**Spacing Scale (8px base unit):**
- **xs:** 4px (0.25rem)
- **sm:** 8px (0.5rem)
- **md:** 16px (1rem)
- **lg:** 24px (1.5rem)
- **xl:** 32px (2rem)
- **2xl:** 48px (3rem)

**Component Spacing:**
- Message bubbles: 12px vertical margin between messages
- Card padding: 16px (mobile), 24px (desktop)
- Input padding: 12px vertical, 16px horizontal
- Section margins: 24px between major sections

**Border Radius:**
- **Small (buttons, badges):** 6px
- **Medium (cards, inputs):** 12px
- **Large (modals):** 16px
- **Message bubbles:** 16px (with tail optional)

**Shadows:**
- **Subtle (cards):** `0 2px 8px rgba(0, 0, 0, 0.12)`
- **Medium (modals):** `0 4px 16px rgba(0, 0, 0, 0.24)`
- **Strong (menus):** `0 8px 24px rgba(0, 0, 0, 0.36)`

### 4.4 Iconography

**Icon System:** Lucide Icons (or Heroicons as fallback)
- **Style:** Outlined/stroke-based for consistency
- **Size:** 20px default, 16px small, 24px large
- **Color:** Inherits from parent text color
- **Stroke width:** 2px

**Key Icons:**
- **Menu:** Hamburger (three horizontal lines)
- **Send:** Paper plane
- **Approve:** Checkmark in circle
- **Deny:** X in circle
- **Adjust:** Sliders
- **Transparency:** Eye
- **Settings:** Gear
- **Profile:** User circle
- **Shield:** Ethical validation
- **Brain:** Digital shadow/agent
- **Calendar:** Scheduling actions
- **Goal:** Target/flag

### 4.5 Animation & Transitions

**Duration Standards:**
- **Fast (micro-interactions):** 150ms (button hover, toggle)
- **Medium (component transitions):** 250ms (modal open, panel slide)
- **Slow (page transitions):** 400ms (navigation, screen change)

**Easing Functions:**
- **Standard:** `cubic-bezier(0.4, 0.0, 0.2, 1)` (ease-in-out)
- **Enter:** `cubic-bezier(0.0, 0.0, 0.2, 1)` (deceleration)
- **Exit:** `cubic-bezier(0.4, 0.0, 1, 1)` (acceleration)

**Key Animations:**
- **Message appear:** Fade + slide up (250ms)
- **Consent card enter:** Scale from 0.95 to 1.0 + fade (300ms)
- **Typing indicator:** Bounce animation on dots (1200ms loop)
- **Button press:** Scale to 0.98 (100ms)
- **Panel slide:** Slide from right/left + fade (300ms)
- **Success feedback:** Checkmark draw animation (400ms)

**Loading States:**
- Skeleton screens for initial loads (pulsing gradient)
- Spinner for in-progress actions (rotating circle)
- Progress bars for determinate processes

---

## 5. Key User Flows

### 5.1 First Conversation & Consent Approval

**User Goal:** Start using OthelloMini, experience consent-gated AI interaction

**Flow:**
1. **Entry:** User completes onboarding, lands on Chat Interface
2. **Initial Prompt:** FELLO sends welcome message: "Hi! I'm FELLO. How can I support you today?"
3. **User Input:** User types: "Help me plan my week"
4. **Processing:** Typing indicator appears (2-3 seconds)
5. **FELLO Response:** "I can help with that. To create a meaningful plan, I'd like to understand your priorities this week. What are your top 3 goals?"
6. **User Response:** User lists goals (e.g., "Finish project, exercise 3x, spend time with family")
7. **Processing:** Typing indicator (3-4 seconds, sub-agents analyzing)
8. **Consent Card Appears:** 
   - **Title:** "Suggested Action: Create Weekly Schedule"
   - **Description:** "I'd like to block time in your calendar for each goal. This requires calendar access."
   - **Tier Badge:** "Suggestive"
   - **Buttons:** [Approve] [Deny] [Adjust]
9. **User Decision:**
   - **If Approve:** Card collapses with success animation, FELLO proceeds to create schedule
   - **If Deny:** Card collapses, FELLO acknowledges and offers alternative
   - **If Adjust:** Modal opens with detailed settings (which goals to schedule, when to avoid, etc.)
10. **Outcome:** FELLO confirms action taken or pivots based on user choice
11. **Follow-up:** FELLO asks if user wants to see the schedule or discuss next steps

**Touchpoints:**
- Chat input/output
- ConsentCard component
- Typing indicator
- Success/denial feedback
- Optional transparency panel (if user toggles eye icon to see reasoning)

---

### 5.2 Reviewing and Adjusting Digital Shadow

**User Goal:** Understand what FELLO has learned about them, correct inaccuracies

**Flow:**
1. **Entry:** User navigates to Digital Shadow screen via hamburger menu
2. **Screen Loads:** Profile summary appears with key traits, loading animation completes
3. **User Scans:** User reads top traits: "Goal-oriented, prefers morning productivity, values family time"
4. **User Spots Inaccuracy:** One trait says "Prefers evening exercise" but user actually prefers morning
5. **User Taps:** Taps the incorrect trait card
6. **Detail Modal Opens:** Shows full reasoning: "Detected from conversation on [date] when you mentioned evening jog"
7. **User Action:** Taps "Correct This" button at bottom of modal
8. **Correction Interface:** Modal transitions to correction form:
   - **Question:** "What should this say instead?"
   - **Input:** Free-text field pre-filled with current trait
   - **User Edits:** Changes to "Prefers morning exercise"
   - **Optional Context:** "Why this correction?" field (user adds: "I only jog evenings when mornings are unavailable")
9. **User Confirms:** Taps "Submit Correction"
10. **Feedback:** Success message appears, modal closes, trait card updates in real-time
11. **Digital Shadow Updates:** Trait card now shows corrected information with "User-verified" badge
12. **Optional Next Step:** FELLO sends chat message acknowledging correction: "Thanks for that update! I've adjusted my understanding of your exercise preferences."

**Touchpoints:**
- Hamburger menu navigation
- Digital Shadow screen with InsightCard components
- Detail modal
- Correction form/modal
- Real-time update feedback
- Cross-screen context (chat notification)

---

### 5.3 Escalating Autonomy Tier & Experiencing Proactive Intervention

**User Goal:** Increase AI autonomy to get proactive routine support, then experience an autonomous action

**Flow:**
1. **Entry:** User navigates to Consent Dashboard via menu
2. **Current State:** Screen shows current tier as "Suggestive" with description
3. **User Intent:** User reads "Active" tier description: "Can nudge and remind with consent"
4. **User Action:** Taps "Active" tier selector
5. **Confirmation Modal:** Appears with warning:
   - **Title:** "Enable Active Mode?"
   - **Description:** "FELLO will proactively send reminders and nudges based on your goals and routines. You can always adjust or deny specific actions."
   - **Buttons:** [Enable Active Mode] [Cancel]
6. **User Confirms:** Taps "Enable Active Mode"
7. **Feedback:** Modal closes, tier selector updates with success animation, Active badge appears
8. **System Response:** Brief success message: "Active mode enabled. I'll now proactively support your goals."
9. **User Returns to Chat:** Navigates back to chat interface (via back button or menu)

**[Time passes — Next morning, 7:45 AM]**

10. **Proactive Notification:** FELLO sends unprompted message in chat (notification on device if app closed):
    - **Message:** "Good morning! You mentioned wanting to exercise 3x this week. You have a free hour at 8:00 AM. Should I set a reminder?"
11. **Inline Consent Card Appears:**
    - **Title:** "Suggested Action: Exercise Reminder"
    - **Description:** "Set reminder for 8:00 AM exercise session"
    - **Tier Badge:** "Active"
    - **Buttons:** [Yes, set it] [Not today] [Adjust time]
12. **User Response:** 
    - **If Yes:** Reminder is set, FELLO confirms with message and checkmark
    - **If Not today:** FELLO acknowledges, asks if different time works
    - **If Adjust time:** Time picker appears, user selects 8:30 AM instead
13. **Outcome:** Reminder is set (or not), FELLO continues monitoring for next intervention opportunity
14. **User Reflection:** User realizes Active mode is working as expected, feels supported without being overwhelmed

**Touchpoints:**
- Consent Dashboard screen
- TierSelector component
- Confirmation modal
- Tier badge update
- Proactive chat message (push notification)
- Inline ConsentCard in chat
- Time picker adjustment (optional)
- Success confirmation

---

## 6. Accessibility & Responsive Considerations

### 6.1 Accessibility (WCAG 2.1 AA Compliance)

**Color Contrast:**
- All text meets minimum 4.5:1 contrast ratio against background
- Interactive elements meet 3:1 contrast for UI components
- Focus states have visible 2px outline in teal accent color

**Keyboard Navigation:**
- All interactive elements are keyboard-accessible
- Logical tab order through components
- Escape key closes modals and menus
- Enter key submits forms and activates primary actions
- Arrow keys navigate lists and selectors

**Screen Reader Support:**
- Semantic HTML structure (nav, main, article, aside)
- ARIA labels for icon-only buttons
- ARIA live regions for dynamic content (new messages, consent cards)
- Alt text for all meaningful images/icons
- Descriptive link text (no "click here")

**Focus Management:**
- Focus trapped in modals when open
- Focus returns to triggering element on modal close
- Clear focus indicators on all interactive elements
- Skip-to-content link for keyboard users

**Text & Content:**
- Font sizes meet minimum 16px for body text
- Line height 1.5+ for readability
- Text is resizable up to 200% without breaking layout
- Clear error messages with recovery instructions

### 6.2 Responsive Behavior

**Mobile (<640px):**
- Single-column layout
- Full-screen chat interface
- Bottom navigation bar (optional: Chat, Shadow, Consent, Settings)
- Transparency panel as full-screen modal overlay
- Hamburger menu slides from left
- Large touch targets (minimum 44x44px)
- Swipe gestures for message actions
- Native keyboard input handling

**Tablet (640px-1024px):**
- Chat occupies 60-70% width
- Transparency panel as slide-in drawer (triggered by icon)
- Consent dashboard in modal or drawer
- Larger input area with multi-line support
- Side-by-side content in Digital Shadow screen
- Hover states for interactive elements

**Desktop (>1024px):**
- Chat occupies 65% width (max 800px)
- Transparency panel persistent option (35%, max 400px)
- Consent dashboard as dedicated screen with more detail
- Keyboard shortcuts available (e.g., Cmd+K for search, Cmd+Enter to send)
- Hover tooltips for additional context
- Wider spacing, larger cards
- Multi-column layout in Digital Shadow screen

**Touch vs. Mouse:**
- Touch: swipe gestures, long-press context menus, larger targets
- Mouse: hover states, right-click context menus, cursor changes

---

## 7. Component State Management

**Global State (App-Level):**
- Current autonomy tier
- User authentication status
- Digital Shadow data (cached)
- Chat history (recent messages)
- Pending actions count

**Local Component State:**
- Message input text
- Modal open/closed status
- Panel expanded/collapsed
- Form validation errors
- Loading/processing indicators

**State Persistence:**
- Autonomy tier: persisted to backend, synced on app launch
- Chat history: paginated, loaded on demand, cached locally
- User preferences: synced to backend, cached locally
- Consent decisions: immediately persisted to backend

---

## 8. Error & Empty States

### 8.1 Error States

**Network Error (Chat):**
- Message fails to send
- Red error indicator on message bubble
- "Retry" button appears
- Error message: "Couldn't send message. Check your connection and try again."

**Authentication Error:**
- Full-screen modal: "Session expired. Please log in again."
- "Log In" button redirects to auth flow
- Local state preserved for recovery after re-auth

**Consent Timeout:**
- Consent card expires after 24 hours (configurable)
- Card grays out with message: "This suggestion has expired."
- User can request fresh suggestion

**Digital Shadow Load Error:**
- Empty state illustration with message: "Couldn't load your digital shadow."
- "Try Again" button
- "Contact Support" link

### 8.2 Empty States

**First-Time Chat (No Messages):**
- Welcome illustration
- Suggested prompts: "Help me plan my day", "Tell me about my digital shadow", "What can you do?"
- Warm, inviting copy encouraging first interaction

**No Pending Actions (Consent Dashboard):**
- Illustration of checkmark
- Message: "All caught up! No actions pending your approval."
- Link to action history

**Digital Shadow Building (New User):**
- Illustration of brain with dots connecting
- Message: "I'm just getting to know you. Keep chatting with me to build your digital shadow."
- Progress indicator showing "X conversations analyzed"

**Empty Action History:**
- Message: "No actions yet. As I learn about you, I'll suggest ways to support your goals."

---

## 9. Performance & Loading Considerations

**Initial Load:**
- Skeleton screens for chat interface (< 200ms)
- Lazy load transparency panel components
- Defer non-critical JS until after first paint

**Chat Scrolling:**
- Virtualized list for long chat histories (render only visible messages)
- Load previous messages on scroll-to-top (pagination)
- Smooth scroll performance (60fps target)

**Image & Icon Loading:**
- SVG icons for fast rendering and scalability
- No heavy images in Phase 1 (icon-based UI)
- Lazy load user avatars if implemented

**Network Optimization:**
- Debounce typing indicators (only show after 500ms of AI processing)
- Optimistic UI updates (show sent message immediately, sync in background)
- WebSocket for real-time chat (fallback to polling)

**Cache Strategy:**
- Cache autonomy tier and user preferences locally
- Cache recent chat history (last 50 messages)
- Invalidate Digital Shadow cache every 6 hours or on manual refresh

---

## 10. Future Considerations (Phase 2+)

**Voice Interaction:**
- Voice input button in chat
- Voice feedback for hands-free mode
- Speech-to-text and text-to-speech integration

**Multi-Modal Context:**
- Photo/file attachment in chat
- Image analysis for context (e.g., receipt, screenshot)
- Calendar and email integrations with visual previews

**Advanced Visualizations:**
- Mood timeline chart (line graph over weeks/months)
- Goal progress dashboards
- Habit streak trackers

**Collaboration Features:**
- Share specific insights or suggestions with trusted contacts
- Family/team consent dashboards

**Wearable Integration:**
- Notifications on smartwatch
- Quick consent approvals from watch
- Biometric context (heart rate, activity) for mood analysis

**Internationalization:**
- Multi-language support
- RTL layout for Arabic, Hebrew
- Locale-specific date/time formatting

---

## Summary

The OthelloMini UI is designed as a **chat-first, transparency-on-demand interface** that prioritizes conversational interaction while providing clear, consent-gated control over AI autonomy. The visual style is calm, focused, and warm—using dark tones with strategic accent colors to guide attention to consent prompts and ethical boundaries. 

Core user flows center on **continuous conversation, informed consent, and transparent AI reasoning**, ensuring users feel empowered and in control at every step. The component architecture is modular and reusable, enabling rapid development and consistent user experience across screens.

This UI contract provides a complete blueprint for Phase 1 implementation, with clear extension points for Phase 2 features like voice interaction, advanced visualizations, and deeper integrations.