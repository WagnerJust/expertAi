# Sprint 5: Frontend UI Development - PDF & Collection Management 🖥️

**Goal:** Develop the React UI components and integrate them into pages for managing PDF collections (CRUD), selecting an active collection, and adding new PDFs (via upload or URL) to a selected collection. Implement the UI trigger for manual re-indexing.

**Tasks for Coding Assistant (Copilot):**

1.  **Collection Management UI (`ManageCollectionsPage.jsx`):**
    * Develop UI components in `frontend/src/components/collections/`:
        * `CollectionList.jsx`: Displays a list of existing collections. Each item should allow selection, renaming, and deletion.
        * `CreateCollectionForm.jsx`: A form (e.g., a modal or inline form) to input a new collection name.
    * Integrate these components into `ManageCollectionsPage.jsx`.
    * Fetch collections on page load using `collectionApi.js` and display them.
    * Implement functionality:
        * **Create:** Submit form, call `collectionApi.createCollection()`, refresh list on success.
        * **Rename:** Provide UI (e.g., an edit icon next to collection name) to trigger a modal/inline edit, call `collectionApi.updateCollection()`, refresh list.
        * **Delete:** Provide UI (e.g., a delete icon), show a confirmation modal, call `collectionApi.deleteCollection()`, refresh list.
        * **Select Active Collection:** Clicking a collection in the list should update the `selectedCollection` in `AppContext` and perhaps visually highlight it. This selected collection will be used for Q&A and PDF additions.
    * **TFD:** Write unit and integration tests (using React Testing Library) for `CreateCollectionForm.jsx`, `CollectionList.jsx` (including item interactions like rename/delete triggers), and `ManageCollectionsPage.jsx` for overall data flow and state updates. Mock API calls.
    * **Acceptance Criteria:** Users can create, view, rename, and delete collections through the React UI. Users can select an active collection, and this selection is stored in global state. UI updates correctly after operations. All interactions are tested.

2.  **PDF Management UI (within `ManageCollectionsPage.jsx` or a dedicated section/modal linked from it):**
    * Develop UI components in `frontend/src/components/pdfs/`:
        * `PdfList.jsx`: Displays a list of PDF documents associated with the currently selected collection (fetch this if API endpoint exists, or manage display based on successful additions).
        * `UploadPdfForm.jsx`: A form with a file input (`<input type="file" accept=".pdf" />`) to select PDF files for upload.
        * `AddPdfByUrlForm.jsx`: A form with a text input for providing a public URL to a PDF.
    * Integrate these components into `ManageCollectionsPage.jsx`, ensuring they operate on the `selectedCollection` from `AppContext`.
    * Implement functionality:
        * **Display PDFs:** If an API endpoint `GET /collections/{collection_id}/pdfs` exists and is implemented, fetch and display PDFs for the selected collection. Otherwise, this list might dynamically update as PDFs are added in the current session.
        * **Upload PDF:** On form submission, get the file, call `pdfApi.uploadPdf(selectedCollection.id, fileData)`, show a loading indicator/progress (basic for now), and provide success/error feedback. Optionally refresh PDF list.
        * **Add PDF by URL:** On form submission, get the URL, call `pdfApi.addPdfByUrl(selectedCollection.id, url)`, show loading, provide feedback. Optionally refresh PDF list.
    * **TFD:** Write unit and integration tests for `UploadPdfForm.jsx`, `AddPdfByUrlForm.jsx`, and `PdfList.jsx`. Test form submissions, file handling (mocked), URL input, and interactions with mocked API services.
    * **Acceptance Criteria:** Users can upload PDF files to the selected collection through the UI. Users can add PDFs via URL to the selected collection through the UI. User feedback (loading, success, error) is provided. Tested.

3.  **Manual Re-indexing Trigger UI:**
    * On `ManageCollectionsPage.jsx`, for the selected collection (or each collection in the list), add a UI element (e.g., an "Update Index" or "Re-process" button).
    * This button, when clicked, should call the backend re-indexing API (`adminApi.reindexCollection(selectedCollection.id)`).
    * Provide user feedback during re-indexing (e.g., a loading spinner on the button, a global loading indicator, or a toast message like "Re-indexing started..."). Since re-indexing can be long, a simple "triggered" message is acceptable for now.
    * **TFD:** Write tests for the re-indexing trigger UI element, ensuring it calls the correct API service function when clicked for the selected collection.
    * **Acceptance Criteria:** A UI element exists to trigger manual re-indexing for the selected collection. It calls the correct backend API. Basic user feedback is provided.

4.  **UI Styling and Common Components:**
    * Develop or enhance basic common components in `frontend/src/components/common/` (e.g., `Button.jsx`, `Modal.jsx`, `Loader.jsx`, `InputField.jsx`, `ConfirmationModal.jsx`). Ensure they are reusable and customizable via props.
    * Apply consistent styling (using global CSS, CSS Modules, TailwindCSS, or a CSS-in-JS solution like Emotion/Styled Components, as chosen in Sprint 1 setup) for a clean, intuitive, and professional look across all new components and pages.
    * Focus on usability: clear visual hierarchy, appropriate spacing, readable fonts.
    * **Acceptance Criteria:** Common UI components are developed/enhanced and used consistently. Initial styling is applied to collection and PDF management features, providing a professional appearance.

5.  **Error Handling and User Feedback (Frontend):**
    * Implement robust user-friendly error messages for all API interactions (e.g., collection creation fails, PDF upload fails, URL is invalid, server error). Use toast notifications (e.g., `react-toastify`) or inline messages.
    * Display loading indicators (`Loader.jsx`) during API calls to provide feedback on ongoing operations.
    * Ensure `AppContext` or local component state manages `isLoading` and `error` states appropriately to drive the UI feedback.
    * **Acceptance Criteria:** Clear and user-friendly error messages and loading indicators are implemented for all collection and PDF management operations.

**Deliverable for CEO (Sprint 5):** 🖼️

* A live demonstration of the web application's collection and PDF management features:
    * **Collections:**
        * Show the `ManageCollectionsPage`.
        * Create a new collection.
        * Rename an existing collection.
        * Select a collection, making it the "active" one.
        * Delete a collection (with confirmation).
    * **PDFs (for the selected collection):**
        * Upload a PDF file.
        * Add a PDF via a public URL.
        * (If `PdfList.jsx` is implemented with fetching: show the list of PDFs in the selected collection).
    * **Re-indexing:**
        * Show the "Update Index" button for the selected collection and click it, demonstrating the call to the backend (network tab) and any UI feedback.
* Show how the UI responds to these actions, reflects changes (e.g., updated lists), and provides loading/error feedback.
* Briefly walk through the frontend code structure for these features (components, services, page).
* Frontend test report summary (e.g., Jest/Vitest coverage output).