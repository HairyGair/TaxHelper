# User Flow Diagrams - UK Tax Helper

## Visual Flow Representations

### 1. Bulk Operations Flow

```mermaid
graph TD
    A[Transaction Review Page] --> B{Select Transactions}
    B --> C[Click Individual Checkbox]
    B --> D[Click Select All]
    B --> E[Click Select Similar]

    C --> F[Selection Counter Updates]
    D --> F
    E --> G[Similarity Modal]
    G --> H[Choose Criteria]
    H --> F

    F --> I[Floating Action Bar Appears]
    I --> J[Choose Bulk Action]
    J --> K[Confirmation Modal]
    K --> L{User Confirms?}
    L -->|Yes| M[Apply Action]
    L -->|No| I
    M --> N[Success Toast]
    N --> O[Selection Cleared]
    O --> A

    style A fill:#e1f5fe
    style M fill:#c8e6c9
    style N fill:#c8e6c9
```

### 2. Keyboard Navigation Flow

```mermaid
graph LR
    A[Any Page] -->|Press ?| B[Shortcuts Overlay]
    B -->|ESC| A
    B -->|Learn Shortcuts| C[Close Overlay]
    C --> D[Transaction Review]

    D -->|Arrow Keys| E[Navigate Transactions]
    D -->|B Key| F[Mark Business]
    D -->|P Key| G[Mark Personal]
    D -->|S Key| H[Save Transaction]
    D -->|/ Key| I[Focus Search]

    E --> J[Transaction Highlighted]
    F --> K[Category Updated]
    G --> K
    H --> L[Data Saved]
    I --> M[Search Active]

    K --> N[Visual Feedback]
    L --> N
    N --> D

    style B fill:#fff3e0
    style N fill:#c8e6c9
```

### 3. Smart Learning Flow

```mermaid
graph TD
    A[User Categorizes Transaction] --> B{Pattern Detection}
    B -->|No Pattern| C[Continue Normal Flow]
    B -->|Pattern Found| D[Check Threshold]

    D -->|< 3 Similar| C
    D -->|>= 3 Similar| E[Learning Modal Appears]

    E --> F[Show Pattern Details]
    F --> G{User Decision}

    G -->|Apply to All| H[Bulk Categorization]
    G -->|Apply to Selected| I[Partial Application]
    G -->|Create Rule| J[Save Rule]
    G -->|Skip| C

    H --> K[Update Transactions]
    I --> K
    J --> L[Rule Added to System]

    K --> M[Success Notification]
    L --> M
    M --> C

    C --> N[Next Transaction]

    style E fill:#f3e5f5
    style M fill:#c8e6c9
```

### 4. Progress Dashboard Interaction

```mermaid
graph TD
    A[Page Load] --> B[Dashboard Visible]
    B --> C[Show Progress Bar]
    C --> D[Display Statistics]

    D --> E{User Interaction}
    E -->|Click Expand| F[Expanded View]
    E -->|Continue Work| G[Update Progress]

    F --> H[Detailed Statistics]
    H --> I[Milestone List]
    I --> J{Click Minimize?}
    J -->|Yes| B
    J -->|No| F

    G --> K{Check Milestone}
    K -->|Not Reached| G
    K -->|25% Complete| L[Small Celebration]
    K -->|50% Complete| M[Confetti Animation]
    K -->|75% Complete| N[Trophy Display]
    K -->|100% Complete| O[Full Celebration]

    L --> G
    M --> G
    N --> G
    O --> P[Summary View]

    style M fill:#c8e6c9
    style O fill:#ffd54f
```

### 5. Search and Filter Flow

```mermaid
graph TD
    A[Transaction List] --> B[Search Box Always Visible]
    B --> C{User Action}

    C -->|Type in Search| D[Debounce 300ms]
    C -->|Click Filters| E[Open Filter Panel]
    C -->|Click Preset| F[Apply Saved Filter]

    D --> G[Execute Search]
    G --> H[Highlight Results]
    H --> I[Update Count]

    E --> J[Advanced Filters]
    J --> K{Select Filters}
    K -->|Date Range| L[Date Picker]
    K -->|Amount| M[Range Slider]
    K -->|Category| N[Checkboxes]

    L --> O[Add Filter Chip]
    M --> O
    N --> O

    O --> P[Update Results]
    F --> P
    P --> Q[Filtered List]

    Q --> R{Save as Preset?}
    R -->|Yes| S[Name Preset]
    R -->|No| Q
    S --> T[Preset Saved]

    style G fill:#e3f2fd
    style P fill:#c8e6c9
```

## Interaction State Diagrams

### Transaction Selection States

```
States:
┌─────────────┐     Select      ┌─────────────┐
│   Default   │ ─────────────> │  Selected   │
│ (Unchecked) │                │  (Checked)  │
└─────────────┘ <───────────── └─────────────┘
                   Deselect
       │                              │
       │ Hover                        │ Hover
       ▼                              ▼
┌─────────────┐                ┌─────────────┐
│   Hovered   │                │ Hover+Check │
│  (Outline)  │                │ (Highlight) │
└─────────────┘                └─────────────┘
```

### Modal Lifecycle

```
Trigger → Opening (Animation) → Open → User Interaction
                                  │
                                  ├─→ Confirm → Processing → Success → Closing
                                  │
                                  └─→ Cancel → Closing → Closed
```

### Filter Application Sequence

```
1. User Input
   └─> Validation
       └─> Processing Indicator
           └─> Apply Filter
               └─> Update URL State
                   └─> Fetch Filtered Data
                       └─> Update UI
                           └─> Show Results Count
                               └─> Ready for Next Action
```

## Error Recovery Flows

### Failed Bulk Operation

```mermaid
graph TD
    A[Bulk Action Initiated] --> B[Processing]
    B --> C{Success?}

    C -->|Yes| D[Update UI]
    C -->|No| E[Error Modal]

    E --> F[Show Error Details]
    F --> G{User Choice}

    G -->|Retry| B
    G -->|Cancel| H[Rollback Changes]
    G -->|Partial Apply| I[Apply to Valid Items]

    H --> J[Original State]
    I --> K[Partial Success Toast]
    D --> L[Success State]

    style E fill:#ffcdd2
    style K fill:#fff9c4
    style L fill:#c8e6c9
```

### Network Failure Handling

```mermaid
graph TD
    A[Action Triggered] --> B{Network Check}
    B -->|Online| C[Execute Action]
    B -->|Offline| D[Queue Action]

    C --> E{Response}
    E -->|Success| F[Update UI]
    E -->|Timeout| G[Retry Logic]
    E -->|Error| H[Error Handler]

    D --> I[Show Offline Badge]
    I --> J[Store in Local Queue]
    J --> K{Network Restored?}
    K -->|No| L[Keep in Queue]
    K -->|Yes| M[Sync Queue]

    G --> N{Retry Count}
    N -->|< 3| C
    N -->|>= 3| H

    M --> C
    H --> O[User Notification]

    style D fill:#fff3e0
    style H fill:#ffcdd2
```

## Mobile Gesture Flows

### Swipe Actions

```
Right Swipe (>50px):
Start ──→ Swipe ──→ Threshold ──→ Visual Feedback ──→ Select Item

Left Swipe (>50px):
Start ──→ Swipe ──→ Threshold ──→ Visual Feedback ──→ Deselect Item

Long Press (>500ms):
Touch ──→ Hold ──→ Haptic ──→ Context Menu ──→ Choose Action

Pull to Refresh:
Pull Down ──→ Loading Indicator ──→ Fetch Data ──→ Update List ──→ Hide Indicator
```

## Onboarding Journey Map

```mermaid
journey
    title First Time User Onboarding Journey
    section Landing
      See Welcome Modal: 5: User
      Choose Tour/Skip: 3: User
    section Feature Discovery
      Learn Bulk Select: 4: User
      Try Keyboard Shortcut: 3: User
      See Smart Suggestion: 5: User
      View Progress: 4: User
      Use Search: 5: User
    section Practice
      Select Multiple Items: 4: User
      Apply Bulk Action: 5: User
      Use Shortcut Key: 3: User
      Save Filter Preset: 4: User
    section Proficiency
      Complete First Batch: 5: User
      See Time Saved: 5: User
      Customize Settings: 4: User
      Achieve Flow State: 5: User
```

## State Machine Definitions

### Bulk Selection State Machine

```typescript
const bulkSelectionMachine = {
  initial: 'idle',
  states: {
    idle: {
      on: {
        SELECT_ITEM: 'selecting',
        SELECT_ALL: 'allSelected'
      }
    },
    selecting: {
      on: {
        SELECT_MORE: 'selecting',
        DESELECT_ITEM: 'selecting',
        CLEAR_ALL: 'idle',
        APPLY_ACTION: 'processing'
      }
    },
    allSelected: {
      on: {
        DESELECT_ITEM: 'selecting',
        CLEAR_ALL: 'idle',
        APPLY_ACTION: 'processing'
      }
    },
    processing: {
      on: {
        SUCCESS: 'complete',
        ERROR: 'error'
      }
    },
    complete: {
      on: {
        RESET: 'idle'
      }
    },
    error: {
      on: {
        RETRY: 'processing',
        CANCEL: 'selecting'
      }
    }
  }
};
```

### Search State Machine

```typescript
const searchStateMachine = {
  initial: 'idle',
  states: {
    idle: {
      on: {
        TYPE: 'debouncing'
      }
    },
    debouncing: {
      after: {
        300: 'searching'
      },
      on: {
        TYPE: 'debouncing',
        CLEAR: 'idle'
      }
    },
    searching: {
      on: {
        SUCCESS: 'results',
        ERROR: 'error',
        TYPE: 'debouncing'
      }
    },
    results: {
      on: {
        TYPE: 'debouncing',
        CLEAR: 'idle',
        FILTER: 'filtering'
      }
    },
    filtering: {
      on: {
        APPLY: 'searching',
        CANCEL: 'results'
      }
    },
    error: {
      on: {
        RETRY: 'searching',
        CLEAR: 'idle'
      }
    }
  }
};
```

---

END OF FLOW DIAGRAMS