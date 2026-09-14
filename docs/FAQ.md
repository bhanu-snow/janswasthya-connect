# FAQ — JanSwasthya + ServiceNow Architecture

## 1. Business & Architecture

### Q1. JanSwasthya ka main purpose kya hai?

JanSwasthya external healthcare systems ke saath integration aur reliable processing ke liye boundary provide karta hai.

ServiceNow operational workflow manage karta hai.

### Q2. ServiceNow ko directly provider system se integrate kyun nahi kiya?

Provider-specific integration logic ko ServiceNow workflow se tightly coupled hone se bachane ke liye JanSwasthya ko external integration boundary banaya gaya hai.

### Q3. JanSwasthya ServiceNow ka replacement hai?

Nahi.

ServiceNow operational workflow platform hai. JanSwasthya external integration aur processing layer hai.

### Q4. Project ka business use case kya hai?

Healthcare organization mein ServiceNow operational incidents/cases manage karta hai. JanSwasthya un cases ko external healthcare/provider systems tak reliably process karta hai.

### Q5. Microservices kyun use kiye?

Har component ko microservice banana objective nahi tha. Boundaries wahan rakhi gayi hain jahan responsibility, ownership, independent processing ya reliability requirements justify karti hain.

### Q6. Shared MariaDB kyun?

Current implementation MVP simplification ke liye shared MariaDB use karti hai. Logical responsibilities services ke beech separate hain. Isse production database-isolation architecture claim nahi kiya ja raha.

## 2. ServiceNow

### Q7. Incident kya hai?

Incident operational issue ko track karne aur service restore karne ke liye hota hai.

> Something is broken → Incident.

### Q8. Problem kya hai?

Problem recurring incidents ke underlying/root cause ko investigate karne ke liye hota hai.

> Why does this keep happening? → Problem.

### Q9. Change kya hai?

Change planned modification ko safely implement karne ke liye hota hai.

> How will we safely modify the environment? → Change.

### Q10. Incident, Problem aur Change ka relation kya hai?

```text
Incident
   |
   | recurring?
   v
Problem
   |
   | corrective modification
   v
Change
```

### Q11. CMDB kya karta hai?

CMDB configuration items (CIs) aur unke relationships ko manage karta hai.

### Q12. Kya Hospital ko CMDB CI banana chahiye?

Automatically nahi.

Hospital business entity hai. CI representation tab useful hai jab operational dependency, impact ya configuration-management value ho.

### Q13. Flow Designer kyun?

Flow Designer visual business workflows aur automation ke liye useful hai.

### Q14. Flow Designer vs Business Rule?

Flow Designer business workflow/orchestration ke liye useful hai.

Business Rule precise server-side record behavior ke liye useful hai.

### Q15. RESTMessageV2 kya hai?

ServiceNow se REST API call karne ki capability.

### Q16. IntegrationHub kyun use karein?

IntegrationHub reusable integration actions/connectors aur workflow-oriented integration capabilities provide karta hai. Enterprise reuse aur governance ke liye useful ho sakta hai.

### Q17. Har REST integration IntegrationHub se karni chahiye?

Nahi.

Simple custom REST call ke liye RESTMessageV2 sufficient ho sakta hai. Reusable managed integration capability chahiye to IntegrationHub better fit ho sakta hai.

## 3. Integration Architecture

### Q18. REST kyun use kiya?

Current ServiceNow → JanSwasthya boundary ke liye REST simple aur appropriate API interface hai.

### Q19. Async integration kyun?

Provider ya analytics service slow/down hone par ServiceNow operational workflow ko block nahi karna chahiye.

### Q20. Async Business Rule kyun?

Current MVP mein ServiceNow Incident event ke baad asynchronous server-side integration trigger karne ke liye use kiya gaya hai.

### Q21. Outbox Pattern kyun?

Database state aur event publication intent ko reliable transaction boundary mein rakhne ke liye.

```text
Transaction
   |
   +--> CaseReference
   +--> OutboxEvent
```

### Q22. Idempotency kyun?

Retry ke wajah se duplicate case creation se bachne ke liye.

### Q23. Payload hash kyun?

Same Idempotency-Key ke saath different payload ko silently accept karne se bachne ke liye.

### Q24. Correlation ID kyun?

ServiceNow → JanSwasthya → Worker → downstream systems ke across request trace karne ke liye.

### Q25. Retry kyun?

Temporary downstream failures recover karne ke liye.

### Q26. Dead Letter kyun?

Retry attempts exhaust hone ke baad failed work ko lose nahi karna chahiye. Dead-letter state investigation/reprocessing ke liye preserve karti hai.

### Q27. Provider aur Analytics ke liye separate events kyun?

Analytics failure ki wajah se Provider processing ko unnecessarily retry nahi karna chahiye.

```text
Case
 |
 +--> Provider Event
 |
 +--> Analytics Event
```

## 4. MID Server / SOAP / Kafka

### Q28. MID Server kya hai?

MID Server ServiceNow ko private/on-premise network resources tak reach karne mein help karta hai.

### Q29. Current project mein MID Server kyun nahi?

Current integration target HTTPS ke through reachable hai. Private/on-premise connectivity requirement current MVP mein nahi hai.

### Q30. Kafka kyun nahi use kiya?

Current scale aur consumer model ke liye Outbox + Worker sufficient hai.

Kafka tab consider karna better hoga jab event volume, consumer count, replay ya streaming requirements justify karein.

### Q31. SOAP kyun nahi?

Current target REST API expose karta hai. SOAP tab relevant hoga jab target enterprise system SOAP-based ho.

### Q32. API Gateway/iPaaS kyun nahi?

Centralized API governance, routing, transformation, security ya multiple system integrations ki requirement ho to useful ho sakta hai. Current MVP mein extra complexity justified nahi hai.

## 5. Security

### Q33. Tenant ID request se lena safe hai?

Production mein client-provided tenant ID ko blindly trust nahi karna chahiye.

Better:

```text
Authentication
      |
      v
Authenticated Tenant
      |
      v
Authorization
```

Current MVP mein tenant handling simplified hai.

### Q34. OAuth2 ka role kya hai?

OAuth2 secure API authorization ke liye common mechanism hai.

### Q35. Kya current project production OAuth2 implementation hai?

Nahi.

Production-grade authentication/authorization hardening roadmap ka part hai.

### Q36. Cloudflare Quick Tunnel production ke liye suitable hai?

Development/testing ke liye useful hai. Production mein stable, authenticated aur controlled ingress architecture use karna chahiye.

## 6. Business Entity Model

### Q37. Hospital Group ko tenant kyun maana?

Hospital Group natural enterprise ownership boundary provide karta hai aur organization-level data isolation/authorization model mein useful hai.

### Q38. Hospital, Facility aur Department mein difference?

```text
Hospital Group       = enterprise ownership
Hospital             = healthcare organization/business unit
Facility             = physical/service location
Department           = operational unit
Healthcare Service   = delivered business service
```

### Q39. Healthcare Service aur CMDB CI same hain?

Nahi.

Healthcare Service business/service offering hai. CI technical/operational configuration item hai.

### Q40. Business master data aur CMDB ko alag kyun rakhna?

Dono ka purpose different hai. Master data business organization ko describe karta hai; CMDB operational configuration aur relationships ko describe karta hai.

## 7. Evidence

### Q41. Actually kya verify hua hai?

Real ServiceNow PDI Incident integration verify hui hai.

Incident:

`INC0010002_BHANU_ASYNC`

JanSwasthya integration boundary tak gaya aur HTTP `201` response ke saath CaseReference create hua.

### Q42. Kya sirf mock integration hai?

ServiceNow → JanSwasthya boundary real ServiceNow PDI ke saath verify hui hai.

Downstream provider ke liye repository mein Mock Provider System available hai.

Real ServiceNow integration aur simulated downstream provider ko clearly distinguish karna chahiye.

### Q43. Failure handling test hua hai?

Analytics failure scenario mein event retries ke baad dead-letter state tak gaya. Provider event independent processing path par raha.

## 8. Architecture Trade-offs

### Q44. Har cheez asynchronous kyun nahi?

Har interaction ko async banana bhi unnecessary complexity create kar sakta hai.

Immediate response required ho to synchronous REST appropriate ho sakta hai.

### Q45. Har integration ke liye middleware kyun nahi?

Middleware tab useful hai jab centralized governance, transformation, routing ya multiple-system integration ki clear requirement ho.

### Q46. Microservices everywhere kyun nahi?

Distributed systems operational complexity increase karte hain. Service boundary tab create karni chahiye jab clear architectural/business reason ho.

### Q47. OOTB ServiceNow functionality ko unnecessarily customize kyun nahi karna chahiye?

OOTB functionality maintainability aur upgrade compatibility improve kar sakti hai. Customization tab karni chahiye jab business requirement OOTB capability se adequately satisfy na ho.

## 9. Interview Positioning

### Q48. Is project ko interview mein kaise explain karein?

> "I designed a healthcare integration boundary around ServiceNow. ServiceNow manages the operational Incident lifecycle, while JanSwasthya handles external healthcare integration asynchronously. The design uses idempotency, correlation IDs, an outbox pattern, independent downstream events, retries and dead-letter persistence."

### Q49. Kafka kyun nahi lagaya?

> "Kafka was not required for the current scale and consumer model. We already have durable OutboxEvents and an integration worker with independent downstream processing. I would introduce Kafka when event volume, consumer count, replay or streaming requirements justify the additional operational complexity."

### Q50. MID Server kyun nahi?

> "The current integration target is reachable through HTTPS. MID Server becomes relevant when ServiceNow needs to communicate with private or on-premise systems that are not directly reachable from the ServiceNow environment."

### Q51. IntegrationHub kyun nahi?

> "IntegrationHub is useful for reusable managed integrations and workflow-oriented enterprise integration. For the current custom REST boundary, RESTMessageV2 is sufficient. I would choose IntegrationHub when reuse, connectors or enterprise integration governance provide clear value."

## 10. Production Question

### Q52. Production mein kya improve karoge?

Priority:

1. Authenticated tenant derivation
2. Production authentication/authorization
3. Secure ingress
4. Stronger secrets management
5. Exponential backoff
6. Observability and alerting
7. Reconciliation
8. Operational replay controls
9. Capacity/performance testing
10. Disaster recovery considerations

The MVP should be presented honestly: implemented capabilities and production hardening gaps should remain clearly separated.
