# Test Plan: [Feature Name]

## 1. Scope
**Testing**: [Feature A], [Feature B]
**Not Testing**: [Legacy Feature C]

## 2. Test Strategy
### Automated Tests
- [ ] Unit Tests (Pytest/Jest)
- [ ] Integration Tests (API checks)
- [ ] E2E Tests (Playwright/Selenium)

### Manual Verification
- [ ] UI/UX Walkthrough
- [ ] Edge Case Testing
- [ ] Cross-browser Compatibility

## 3. Test Cases
| ID | Description | Pre-conditions | Steps | Expected Result |
|----|-------------|----------------|-------|-----------------|
| TC-01 | Verify Login | Account exists | 1. Enter details 2. Click Login | Redirect to Home |
| TC-02 | Error Handling | Invalid data | 1. Enter bad data 2. Submit | Show Error Msg |

## 4. Environment
- **URL**: [Staging URL]
- **Users**: [Test User Credentials]
