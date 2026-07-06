# Security & Privacy Design

Privacy and security are key design requirements for the **English Memory Agent** to ensure that personal information is never stored or leaked.

## Security Controls

1. **Pre-Save Privacy Scan**:
   - Before any memory card is persisted to the local SQLite database, the input text is routed to the `privacy_scan` tool.
   - The scanner uses robust regular expressions to detect:
     - **Email addresses**: Standard RFC-compliant formats.
     - **Phone numbers**: International and national telephone numbers.
     - **API Keys / Passwords / Secrets**: Key/Value pattern mappings followed by alphanumeric strings.
     - **ID-like numbers**: Social Security Numbers (SSNs), Credit Card formats, and National ID cards.
     - **Home address-like text**: Common English street suffixes (Street, Avenue, Rd, etc.) and Chinese geographical patterns (省, 市, 区, 县, 路, 街).

2. **Save Control and Visual Warnings**:
   - If the privacy check detects PII, it returns `safe_to_save: False` along with a list of specific risks.
   - The Streamlit interface displays an explicit warning listing the detected risks, and the "Save Card" button is automatically disabled to prevent accidental storage.

3. **No Hardcoded API Keys**:
   - This project strictly isolates API keys from the codebase.
   - All credentials must be set locally inside the environment file `.env` (which is git-ignored).
   - `.env.example` is provided to define the expected parameters without exposing real keys.

4. **Local SQLite Persistence**:
   - All saved cards are stored locally in the user's workspace under `database/memory.db`.
   - No data is transmitted to external database servers, keeping your learning data private.

5. **User-Controlled Deletion**:
   - Users maintain full control over their memory library.
   - Any card can be permanently deleted by ID via the "Recent Cards" tab or card expands in the dashboard.

---

## Limitations of the Safety System

- **Regex-based Scanner**: The PII scanner is rule-based. While highly effective at catching structured formats (like emails, phone numbers, and IDs), it may not capture unstructured secrets or complex personal descriptions that do not trigger the regex patterns.
- **Local SQLite Security**: The database file `memory.db` is stored locally. It is not encrypted by default. Users must ensure that their filesystem has standard operating system security controls to prevent unauthorized local file access.

---

## Recommended Safe Usage

- Do not enter real credit card numbers, passwords, or personal credentials into the text area. Use placeholder text like `"John Doe"` or `"xxxx-xxxx-xxxx-xxxx"` when analyzing sentences containing references to sensitive data.
- Regularly review and clean up saved cards in the library.
