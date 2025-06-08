# Sprint 6: Frontend UI Development - Q&A, History, Feedback & Finalization ✨

**Goal:** Complete the core frontend functionality by implementing the Q&A interface, displaying query history for a collection, allowing users to provide feedback on answers, and performing overall UI polish and frontend Docker finalization.

**Tasks for Coding Assistant (Copilot):**

1.  **Q&A Interface (`CollectionChatPage.jsx`):**
    * Develop UI components in `frontend/src/components/qa/`:
        * `ChatInput.jsx`: An input field for users to type their questions, and a submit button.
        * `MessageList.jsx`: A scrollable area to display the conversation (user questions and LLM answers).
        * `AnswerDisplay.jsx`: A component to render the LLM's answer, including clearly formatted cited sources (Article Title, page number(s)) extracted from the API response.
    * Integrate these into `CollectionChatPage.jsx`.
    * The page should display the name of the currently selected collection (from `AppContext`). If no collection is selected, prompt the user to select one (e.g., redirect to `ManageCollectionsPage` or show a message).
    * When a question is submitted from `ChatInput.jsx`:
        * Add the user's question to the `MessageList.jsx`.
        * Show a loading indicator for the answer.
        * Call the backend Q&A API (`qaApi.askQuestion(selectedCollection.id, questionText)`).
        * On response, display the LLM's answer (via `AnswerDisplay.jsx`) in the `MessageList.jsx`.
        * Handle API errors gracefully, displaying an error message in the chat or as a toast.
    * Manage chat conversation state (list of messages) within `CollectionChatPage.jsx` or a local context.
    * **TFD:** Write unit and integration tests (React Testing Library) for `ChatInput.jsx`, `AnswerDisplay.jsx`, `MessageList.jsx`, and `CollectionChatPage.jsx`. Test submitting questions, displaying answers with sources, and handling loading/error states. Mock API calls.
    * **Acceptance Criteria:** Users can select a collection, navigate to its chat page, ask questions, and see answers from the LLM (based on the selected collection's context) displayed in a chat-like interface. Citations are clearly shown. UI handles loading and errors. Tested.

2.  **Query History Display (within `CollectionChatPage.jsx` or a dedicated panel/tab):**
    * When `CollectionChatPage.jsx` loads for a selected collection, fetch its past Q&A history using `qaApi.getHistory(selectedCollection.id)`.
    * Display this history in a user-friendly way (e.g., a list of past Q&A pairs, perhaps a summary). This could be part of the initial view of `MessageList.jsx` or a separate toggleable panel.
    * History should be persistent across sessions for each collection as it's stored in the backend database.
    * (Optional UX enhancement: Allow users to click on a past question in the history to re-populate the chat input or re-run the query).
    * **TFD:** Write tests for fetching and displaying query history. Test scenarios with history and no history.
    * **Acceptance Criteria:** Query history for the selected collection is fetched from the backend and displayed to the user.

3.  **Answer Feedback UI (part of `AnswerDisplay.jsx` or alongside each answer in `MessageList.jsx`):**
    * For each LLM-generated answer, provide UI elements (e.g., thumbs up/down buttons).
    * When a feedback button is clicked:
        * Call the backend feedback API (`qaApi.submitFeedback(answerId, rating)`). The `answerId` (or `queryId` if feedback is on the whole Q&A pair) should be available from the Q&A API response.
        * Provide visual feedback that the rating was submitted (e.g., change button appearance, show a small "Thanks for your feedback!" message).
    * **TFD:** Write tests for the feedback UI components and their interaction with the mocked feedback API service.
    * **Acceptance Criteria:** Users can provide feedback (e.g., thumbs up/down) on answers. Feedback is sent to the backend. UI provides confirmation.

4.  **View Context (Optional Frontend Feature Implementation):**
    * If the Q&A API (`POST /collections/{collection_id}/qa`) was updated in Sprint 4 to return the `retrieved_context` chunks, implement a UI feature.
    * In `AnswerDisplay.jsx`, add a button or link (e.g., "View Context", "Show Sources Details").
    * When clicked, display the actual text of the retrieved context chunks that informed the answer (e.g., in a modal or an expandable section).
    * **TFD:** Write tests for this feature if implemented.
    * **Acceptance Criteria:** (If implemented) Users can optionally view the specific context chunks retrieved from the documents that were used to generate the answer.

5.  **UI Polish and Responsiveness:**
    * Refine the overall UI/UX for a clean, intuitive, and professional appearance across the entire application.
    * Ensure consistency in styling, typography, and interactive elements.
    * Check and improve basic responsiveness for common screen sizes (desktop, tablet).
    * Perform a quick accessibility check (e.g., keyboard navigation for main interactive elements, sufficient color contrast, use of ARIA attributes where appropriate for dynamic content).
    * **Acceptance Criteria:** The UI is polished, consistent, and reasonably responsive. Basic accessibility considerations are addressed.

6.  **Frontend Dockerfile Finalization:**
    * Ensure the `frontend/Dockerfile` correctly builds the React application for production (e.g., `npm run build` or `yarn build`).
    * Ensure it serves the static build artifacts efficiently (e.g., using Nginx).
    * Verify that `docker compose.yml` correctly builds and runs the frontend service, exposing the necessary port (e.g., port 80 or 3000 for development, but the Nginx in Docker usually serves on 80).
    * **Acceptance Criteria:** Frontend Docker build is optimized for serving a production version of the React app. `docker compose up` correctly serves the frontend.

**Deliverable for CEO (Sprint 6):** 💬

* A full demonstration of the complete web application, focusing on the new Q&A features:
    * Select a collection on the `ManageCollectionsPage`.
    * Navigate to the `CollectionChatPage` for that collection.
    * Show any existing query history displayed for the collection.
    * Ask new questions and receive answers from the LLM, with citations clearly displayed.
    * Demonstrate the "I don't know" response if a question is out of context for the selected collection.
    * Submit feedback (thumbs up/down) on an answer and show the UI confirmation.
    * (If implemented) Demonstrate the "View Context" feature.
* Walk through the polished UI, highlighting its ease of use, professional appearance, and responsiveness.
* Show that the frontend is being served correctly via Docker.
* Frontend test report summary.