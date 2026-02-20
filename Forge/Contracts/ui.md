# OthelloMini UI/UX Contract

## 1. App Shell & Layout

### Overall Structure
The application uses a **single-page chat-first layout** optimized for focus and minimal distraction. The interface is built as a React SPA with three primary layout zones:

**Main Chat Area (Primary Zone)**
- Full-screen conversation interface occupying 100% viewport width on mobile, 70% on desktop
- Fixed header bar (48px height) with app branding "Othello" and hamburger menu icon
- Scrollable message list container (flex-grow: 1) with auto-scroll to latest message
- Fixed bottom input bar (64px height) with text input field and send button
- Dark navy background (#1a1f2e) with charcoal message bubbles (#2a2f3e)

**Collapsible Side Panel (Transparency Zone)**
- Desktop: 30% width panel, collapsed by default, slides in from right
- Mobile: Full-screen overlay modal activated by header menu icon
- Three collapsible accordion sections:
  - **Profile Summary**: Top 3 psychological traits, current consent tier badge
  - **Ethical Reasoning Log**: Recent Othello filtering decisions with timestamps
  - **Conversation Context**: Last 5 message summaries for transparency
- Soft charcoal background (#252a38) with subtle border separator
- Close button (X icon) in top-right corner

**Settings Modal (Secondary Zone)**
- Centered modal overlay (max-width 480px) with backdrop blur
- Accessed via gear icon in header bar or "Settings" link in side panel
- Contains consent tier controls and profile management options
- Dismissible via backdrop click or close button

### Navigation Pattern
- **No traditional navigation menu** — single-view chat interface
- Header hamburger toggles side panel (desktop) or full-screen menu (mobile)
- All secondary actions (settings, profile view) are modal overlays
- Back-to-chat always visible when modals/panels are open

### Responsive Breakpoints
- Mobile: < 768px (single column, full-width chat, overlay panels)
- Tablet: 768px - 1024px (chat 60%, collapsible sidebar 40%)
- Desktop: > 1024px (chat 70%, collapsible sidebar 30%)

---

## 2. Screens/Views

### 2.1 Chat View (Primary Screen)

**Purpose**: Core conversational interface for all user interactions with Othello/FELLO AI.

**Layout Elements**:
- **Message List**:
  - User messages: Right-aligned, soft teal bubble (#3a7a7c), white text
  - AI messages: Left-aligned, charcoal bubble (#2a2f3e), high-contrast white text
  - Timestamp below each message (small grey text, 12px)
  - Avatar icons: User (simple circle initial), AI (Othello icon)
  
- **Inline Suggestion Cards** (embedded in message flow):
  - Rendered immediately after relevant AI message
  - Card structure:
    - Header: Action title + consent tier badge (pill shape, color-coded)
    - Body: Brief description of suggested action (2-3 lines)
    - Expandable "Why this?" link → reveals ethical reasoning paragraph
    - Footer: Two buttons — "Approve" (teal), "Deny" (muted grey)
  - Visual hierarchy: Subtle elevation (box-shadow), 8px border-radius
  - State indicators: Approved (green checkmark + fade), Denied (red X + fade)

- **Input Bar**:
  - Multi-line text input (auto-expand up to 4 lines, then scroll)
  - Placeholder: "Talk to Othello..."
  - Send button: Teal circle with arrow icon, disabled when input empty
  - Character count (optional): Small grey text when approaching limit

**Key Interactions**:
- Type message → Enter/Send → message appears instantly (optimistic UI) → AI response streams in
- Click "Why this?" on suggestion → ethical reasoning expands inline with slide-down animation
- Approve suggestion → card updates with checkmark, fades to 50% opacity, confirmation toast appears
- Deny suggestion → card updates with X icon, fades out after 1s
- Scroll up to load conversation history (infinite scroll, 20 messages per page)

**Empty State**:
- First-time user sees welcome message from Othello with brief introduction
- Suggested conversation starters displayed as clickable chips (3-4 examples)

---

### 2.2 Profile Summary Panel (Side Panel Section)

**Purpose**: Provide transparency into user's digital shadow — what the AI knows and remembers.

**Content Blocks**:
1. **Current Consent Tier**:
   - Large badge with tier name (Passive/Suggestive/Active/Autonomous)
   - Color-coded: Passive (grey), Suggestive (teal), Active (amber), Autonomous (red)
   - One-line description of tier permissions
   - "Change Tier" link → opens Settings modal

2. **Top Psychological Traits** (3-5 items):
   - List format with trait name + confidence indicator (filled circles, 1-5)
   - Example: "Goal-oriented ●●●●○" 
   - Trait icons (optional): Small iconography for visual scanning
   - Last updated timestamp at bottom

3. **Behavioral Patterns** (2-3 items):
   - Brief bullet list of observed preferences
   - Example: "Prefers morning planning sessions"
   - Derived from conversation history (simplified for MVP)

**Interactions**:
- Expand/collapse each section with accordion animation
- Hover on trait → tooltip shows brief explanation
- "View Full Profile" link at bottom → future feature placeholder (disabled in MVP)

---

### 2.3 Ethical Reasoning Log (Side Panel Section)

**Purpose**: Show Othello's filtering decisions for transparency and trust-building.

**Layout**:
- Reverse chronological list (most recent first)
- Each entry contains:
  - Timestamp (relative: "2 min ago", "1 hour ago")
  - Suggested action title (truncated to 40 chars)
  - Othello's decision: "Approved for [tier]" or "Blocked" with reason
  - Expandable details: Full ethical reasoning text (2-4 sentences)

**Visual Design**:
- Compact card format (8px padding, subtle border)
- Approved entries: Teal left border accent
- Blocked entries: Amber left border accent
- Max 10 entries visible, "Load More" button at bottom

**Interactions**:
- Click entry to expand full reasoning
- Click suggestion title → scrolls to corresponding suggestion card in chat (if visible)

---

### 2.4 Settings Modal

**Purpose**: User control center for consent tier and profile management.

**Sections**:

1. **Consent Tier Selection** (top priority):
   - Header: "Set Your Autonomy Level"
   - Four large radio buttons (vertical stack on mobile, 2x2 grid on desktop):
     - **Passive**: "Observe only. Othello learns but never suggests actions."
     - **Suggestive**: "Gentle nudges. Othello suggests, you always decide."
     - **Active**: "Proactive help. Othello plans actions, you approve each one."
     - **Autonomous**: "Trusted autopilot. Pre-approved actions execute automatically." (amber warning icon)
   - Each option shows badge color and icon
   - Currently selected tier has teal border highlight
   - "Save Changes" button at bottom (primary teal button)

2. **Profile Management**:
   - "View Collected Data" button → expands JSON-like tree view of user profile (read-only)
   - "Clear Conversation History" button (destructive action, requires confirmation)
   - "Reset Profile" button (red, requires typed confirmation: "RESET")

3. **About**:
   - App version number
   - Link to "How Othello Works" (external docs)
   - Privacy statement snippet

**Interactions**:
- Change consent tier → immediate save on selection (no separate save button needed)
- Click destructive action → confirmation dialog slides down inline
- Close modal via X button, backdrop click, or ESC key

---

### 2.5 Conversation Context (Side Panel Section)

**Purpose**: Show recent conversation summary for context awareness.

**Content**:
- Last 5 conversation turns displayed as compact list:
  - User message preview (1 line, truncated)
  - AI response preview (1 line, truncated)
  - Timestamp (relative)
- "View Full History" link → scrolls chat view to top

**Design**:
- Minimal design: Small text (14px), grey on charcoal
- Hover effect: Slight brightness increase
- Click message → scrolls to that message in chat view

---

## 3. Component List

### Core Components

1. **ChatView**
   - Container component managing chat state
   - Props: `messages`, `onSendMessage`, `isLoading`
   - Children: MessageList, InputBar

2. **MessageList**
   - Scrollable container for messages and suggestion cards
   - Props: `messages`, `suggestions`, `onApprove`, `onDeny`
   - Auto-scroll behavior on new message

3. **MessageBubble**
   - Single message display (user or AI)
   - Props: `content`, `sender`, `timestamp`, `avatar`
   - Variants: `user`, `ai`

4. **SuggestionCard**
   - Inline action suggestion with consent controls
   - Props: `title`, `description`, `consentTier`, `ethicalReasoning`, `status`, `onApprove`, `onDeny`
   - States: `pending`, `approved`, `denied`
   - Expandable reasoning section

5. **InputBar**
   - Text input with send button
   - Props: `value`, `onChange`, `onSubmit`, `disabled`, `placeholder`
   - Auto-expand textarea (1-4 lines)

6. **SidePanel**
   - Collapsible side panel container
   - Props: `isOpen`, `onClose`, `sections`
   - Responsive: Sidebar (desktop) vs full-screen overlay (mobile)

7. **ProfileSummary**
   - User profile display component
   - Props: `consentTier`, `traits`, `patterns`
   - Includes consent tier badge and trait list

8. **EthicalReasoningLog**
   - List of Othello filtering decisions
   - Props: `entries`, `onLoadMore`
   - Expandable entry cards

9. **ConversationContext**
   - Recent message summary list
   - Props: `recentMessages`, `onMessageClick`

10. **SettingsModal**
    - Modal overlay for settings
    - Props: `isOpen`, `onClose`, `currentTier`, `onTierChange`
    - Sections: ConsentTierSelector, ProfileManagement

11. **ConsentTierSelector**
    - Radio button group for tier selection
    - Props: `selectedTier`, `onChange`
    - Four tier options with descriptions

12. **ConsentBadge**
    - Small pill-shaped tier indicator
    - Props: `tier` (Passive/Suggestive/Active/Autonomous)
    - Color-coded styling

13. **ConfirmationDialog**
    - Inline confirmation for destructive actions
    - Props: `message`, `confirmText`, `onConfirm`, `onCancel`, `requireTypedConfirmation`

14. **HeaderBar**
    - Top navigation with branding and menu
    - Props: `onMenuToggle`, `onSettingsClick`
    - Fixed position

15. **LoadingSpinner**
    - AI response loading indicator
    - Displayed in message list while waiting for response

### Utility Components

16. **Icon**
    - Reusable icon component
    - Props: `name`, `size`, `color`
    - Library: Lucide React or similar

17. **Button**
    - Styled button with variants
    - Props: `variant` (primary/secondary/destructive), `size`, `disabled`, `onClick`

18. **Card**
    - Generic card container
    - Props: `elevation`, `padding`, `borderRadius`

19. **Accordion**
    - Collapsible section container
    - Props: `title`, `isOpen`, `onToggle`, `children`

20. **Toast**
    - Temporary notification overlay
    - Props: `message`, `type` (success/error/info), `duration`
    - Auto-dismiss after timeout

---

## 4. Visual Style

### Color Palette

**Base Colors**:
- **Primary Background**: Deep Navy `#1a1f2e` — main app background
- **Secondary Background**: Charcoal `#2a2f3e` — message bubbles, cards
- **Tertiary Background**: Soft Charcoal `#252a38` — side panel, elevated surfaces

**Accent Colors**:
- **Primary Accent**: Soft Teal `#3a7a7c` — CTAs, user messages, approve actions
- **Warning Accent**: Muted Amber `#d4a05f` — warnings, Active tier, blocked suggestions
- **Danger Accent**: Soft Red `#c05555` — Autonomous tier, destructive actions
- **Success Accent**: Muted Green `#5a9f7c` — approved confirmations

**Text Colors**:
- **Primary Text**: High-contrast White `#f5f5f5` — main content
- **Secondary Text**: Light Grey `#b0b5c0` — timestamps, descriptions
- **Muted Text**: Medium Grey `#6b7280` — placeholders, disabled states

**Consent Tier Color-Coding**:
- Passive: Light Grey `#6b7280`
- Suggestive: Soft Teal `#3a7a7c`
- Active: Muted Amber `#d4a05f`
- Autonomous: Soft Red `#c05555`

### Typography

**Font Family**:
- **Primary**: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- Fallback to system fonts for performance
- Clean, highly legible sans-serif for conversational UI

**Type Scale**:
- **H1 (Headings)**: 24px, 600 weight, 1.3 line-height — modal titles
- **H2 (Subheadings)**: 18px, 600 weight, 1.4 line-height — section headers
- **Body (Default)**: 16px, 400 weight, 1.6 line-height — messages, descriptions
- **Small (Metadata)**: 14px, 400 weight, 1.5 line-height — timestamps, labels
- **Tiny (Captions)**: 12px, 400 weight, 1.4 line-height — hints, footnotes

**Text Styling**:
- Message content: Body size with comfortable line-height for readability
- Timestamps: Small size, secondary text color
- Button text: 15px, 500 weight, uppercase for primary CTAs, title-case for secondary
- Links: Underline on hover, teal color

### Spacing & Layout

**Base Unit**: 8px grid system

**Spacing Scale**:
- xs: 4px — tight spacing (icon margins)
- sm: 8px — compact spacing (card padding)
- md: 16px — default spacing (component margins)
- lg: 24px — generous spacing (section separation)
- xl: 32px — large spacing (modal padding)
- 2xl: 48px — extra-large spacing (view separation)

**Component Spacing**:
- Message bubbles: 12px vertical gap between messages
- Suggestion cards: 16px margin-top from message, 8px padding
- Side panel sections: 24px vertical gap
- Input bar: 16px padding

### Elevation & Shadows

**Shadow Levels**:
- **Level 1** (Subtle): `0 1px 3px rgba(0, 0, 0, 0.3)` — message bubbles
- **Level 2** (Moderate): `0 4px 12px rgba(0, 0, 0, 0.4)` — suggestion cards, modals
- **Level 3** (Strong): `0 8px 24px rgba(0, 0, 0, 0.5)` — floating panels, overlays

**Border Radius**:
- Small: 4px — badges, small chips
- Medium: 8px — buttons, message bubbles
- Large: 12px — cards, panels
- Extra-large: 16px — modals

### Interactive States

**Button States**:
- Default: Solid color with subtle shadow
- Hover: 10% brightness increase, slight shadow expansion
- Active/Pressed: 10% brightness decrease, shadow reduction
- Disabled: 40% opacity, no hover effects

**Card/Message Hover**:
- Subtle brightness increase (5%)
- Cursor change to pointer for interactive elements
- Smooth transition (150ms ease-in-out)

**Focus Indicators**:
- Keyboard navigation: 2px teal outline with 2px offset
- Input fields: Teal border highlight on focus
- Ensure WCAG 2.1 AA contrast ratios (4.5:1 minimum)

### Iconography

**Icon Library**: Lucide React (or Heroicons as alternative)

**Icon Usage**:
- Header menu: Hamburger icon (24px)
- Settings: Gear icon (20px)
- Close: X icon (20px)
- Send: Arrow-right icon (20px)
- Approve: Check icon (18px, teal)
- Deny: X icon (18px, grey)
- Expand: Chevron-down (16px)
- Collapse: Chevron-up (16px)
- Tier badges: Shield icons with fill color
- Loading: Spinner animation (24px)

**Icon Styling**:
- Stroke width: 2px (medium weight)
- Color: Match text color or accent color contextually
- Padding: 4px minimum touch target expansion

### Animation & Transitions

**Timing**:
- Fast: 150ms — hover effects, button states
- Medium: 250ms — panel slides, accordion expand/collapse
- Slow: 400ms — modal fade-in/out, page transitions

**Easing Functions**:
- Ease-in-out: Default for most transitions (smooth start and end)
- Ease-out: Element entering viewport (faster start)
- Ease-in: Element exiting viewport (faster end)

**Key Animations**:
- Message appear: Fade-in + slide-up (250ms ease-out)
- Suggestion card reveal: Scale-in from 0.95 to 1.0 + fade (300ms ease-out)
- Side panel open: Slide-in from right (300ms ease-in-out)
- Toast notification: Slide-down from top + fade (250ms ease-out), auto-dismiss after 3s
- Loading indicator: Continuous spin animation (1s linear infinite)

---

## 5. Key User Flows

### Flow 1: First Conversation with AI Suggestion

**Goal**: User sends first message, receives AI response with consent-gated suggestion, and approves it.

**Steps**:
1. **Landing** → User opens app, sees empty chat with welcome message from Othello
   - Welcome text: "Hi! I'm Othello, your ethics-first AI companion. Tell me what's on your mind."
   - Suggested starters displayed as chips: "Help me plan my day", "I need advice", "Tell me about yourself"

2. **User Input** → User types message: "I want to start exercising more"
   - Input field expands as user types
   - Send button activates (teal highlight)
   - User clicks Send or presses Enter

3. **Message Sent** → User message appears in chat (right-aligned teal bubble)
   - Optimistic UI: Message appears immediately
   - Loading indicator (three dots) appears below for AI response

4. **AI Response** → AI message streams in (left-aligned charcoal bubble)
   - Text: "That's a great goal! Building an exercise habit can boost both physical and mental health. Based on your schedule, I can help you plan specific workout times."
   - Message appears word-by-word (streaming effect) or all at once

5. **Suggestion Appears** → Suggestion card renders below AI message
   - Card displays:
     - Title: "Schedule morning workouts"
     - Consent tier badge: "Suggestive" (teal)
     - Description: "Add 30-minute workout slots to your calendar on Mon/Wed/Fri at 7 AM"
     - Collapsed "Why this?" link
     - Approve and Deny buttons

6. **User Explores Reasoning** → User clicks "Why this?" link
   - Ethical reasoning expands with slide-down animation:
     - "This suggestion aligns with your stated goal and respects your autonomy. Morning timing based on your typical schedule patterns. Requires your explicit approval before any action."
   - User reads reasoning

7. **User Approves** → User clicks "Approve" button
   - Button shows loading spinner briefly
   - Card updates: Checkmark appears, card fades to 50% opacity
   - Success toast appears at top: "Action approved! I'll help you get started."
   - AI sends follow-up message: "Great! Let's set up those workout times..."

**Alternative Path**: User clicks "Deny"
   - Card shows X icon, fades out after 1 second
   - AI acknowledges: "No problem. Let me know if you'd like to explore other approaches."

---

### Flow 2: Adjusting Consent Tier

**Goal**: User wants more proactive AI assistance and changes consent tier from Suggestive to Active.

**Steps**:
1. **Trigger** → User clicks hamburger menu icon in header
   - Side panel slides in from right (desktop) or full-screen overlay appears (mobile)
   - Profile Summary section displays current tier: "Suggestive" badge

2. **Navigate to Settings** → User clicks "Change Tier" link in Profile Summary
   - Settings modal fades in with backdrop blur
   - Consent Tier Selection section displayed at top

3. **Review Options** → User reads tier descriptions
   - Four radio options visible:
     - Passive (currently grey)
     - Suggestive (currently selected, teal border)
     - Active (amber badge visible)
     - Autonomous (red badge, warning icon)
   - User hovers over Active option, description highlights

4. **Select New Tier** → User clicks "Active" radio button
   - Active option now has teal border highlight
   - Brief tooltip appears: "Othello will proactively plan actions for your approval"

5. **Confirm Change** → Tier changes immediately (auto-save)
   - Success toast appears: "Consent tier updated to Active"
   - Profile Summary badge updates to "Active" (amber)
   - Modal remains open for additional changes

6. **Close Settings** → User clicks X button or backdrop
   - Modal fades out
   - Returns to chat view with side panel still open

7. **Observe Behavior Change** → User continues chatting
   - Next AI response includes more proactive suggestions:
     - "I've outlined a 4-week exercise progression plan. May I schedule these sessions?"
   - Suggestions now have "Active" tier badges

**Alternative Path**: User explores Autonomous tier but decides not to enable
   - Clicks Autonomous option
   - Warning dialog appears inline: "Autonomous tier allows pre-approved actions to execute automatically. Are you sure?"
   - User clicks "Cancel", returns to Active selection

---

### Flow 3: Reviewing Ethical Reasoning Log

**Goal**: User wants transparency into how Othello filters suggestions.

**Steps**:
1. **Open Side Panel** → User clicks hamburger menu icon
   - Side panel slides in, showing three accordion sections
   - Ethical Reasoning Log section is collapsed by default

2. **Expand Log Section** → User clicks "Ethical Reasoning Log" header
   - Section expands with accordion animation (250ms)
   - Shows list of 5 recent entries:
     - Entry 1: "Schedule morning workouts" — Approved for Suggestive (2 min ago)
     - Entry 2: "Send email to boss" — Blocked (10 min ago)
     - Entry 3: "Order groceries online" — Approved for Active (1 hour ago)
     - Etc.

3. **Investigate Blocked Suggestion** → User clicks Entry 2 to see why it was blocked
   - Entry expands to show full ethical reasoning:
     - "This action involves professional communication and was blocked because your current consent tier (Suggestive) does not permit automated messaging. To enable this, upgrade to Active tier and explicitly approve email actions."
   - User reads reasoning

4. **Cross-Reference Chat** → User clicks suggestion title "Send email to boss"
   - Side panel stays open
   - Chat view automatically scrolls to that conversation (if still visible in history)
   - Corresponding message and blocked suggestion card highlighted briefly (pulse animation)

5. **Review More Entries** → User scrolls down log
   - Clicks "Load More" button at bottom
   - Additional 5 entries load with fade-in animation

6. **Close Panel** → User clicks X button or clicks chat area
   - Side panel slides out
   - User returns to full-screen chat view

**Insight Gained**: User understands Othello's filtering logic and feels confident in transparency.

---

## Implementation Notes

### Accessibility
- All interactive elements must have minimum 44x44px touch targets
- Keyboard navigation: Tab order follows logical flow (chat input → suggestions → side panel)
- ARIA labels on icon buttons: "Open menu", "Send message", "Approve suggestion"
- Focus trap in modals: Tab cycles within modal, ESC closes
- Screen reader announcements: New messages, suggestion approvals, tier changes
- Color contrast: WCAG AA minimum (4.5:1 for text, 3:1 for UI components)

### Performance
- Message list virtualization for long conversations (only render visible messages)
- Lazy load side panel content (don't fetch logs until panel opened)
- Debounce text input (300ms) to avoid excessive re-renders
- Optimize bundle size: Code-split Settings modal, side panel components
- Image/icon optimization: Use SVG for icons, lazy load avatars

### Responsive Design
- Mobile-first approach: Design for 375px width minimum
- Breakpoint strategy: Single column (mobile) → side-by-side (desktop)
- Touch-friendly: 48px minimum button height, generous spacing
- Desktop enhancements: Hover states, keyboard shortcuts (e.g., CMD+K for settings)

### Error States
- Network error: Toast notification with retry button
- API error: Inline error message in chat ("Sorry, I couldn't process that. Please try again.")
- Empty states: Friendly messages ("No suggestions yet", "No conversation history")
- Failed suggestion approval: Error toast + suggestion card returns to pending state

### Loading States
- Initial app load: Full-screen skeleton loader with logo
- Message sending: Optimistic UI (show immediately, update on confirmation)
- AI response: Three-dot typing indicator in message list
- Side panel data: Skeleton placeholders in Profile Summary and Log sections
- Settings save: Brief spinner on consent tier radio buttons

---

**End of UI/UX Contract**