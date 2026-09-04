# Data retention and privacy procedure

These initial operating periods assume BeanCo operates in Thailand. They minimize
optional personal data while retaining order and tax evidence conservatively. Thai
Revenue Department guidance says relevant VAT reports, invoices, and supporting records
must generally be retained for at least five years and may be required for up to seven;
BeanCo therefore uses seven years for order/payment evidence. The policy must be reviewed
by BeanCo's accountant or privacy adviser before launch.

| Record category | Retention period | End-of-period action |
| --- | --- | --- |
| Customer profile and saved addresses | While active; review after 24 months without login or order activity | Notify where practical, then delete optional profile/address data within 30 days unless a hold applies |
| Orders, inventory audit records, and payment-attempt metadata | 7 years after the end of the relevant fiscal year | Delete or irreversibly anonymize personal fields that are no longer legally required |
| Stripe webhook processing records | 90 days, except identifiers linked to retained payment evidence | Delete transient delivery/error details |
| Partnership/contact inquiries | 24 months after the last substantive contact | Delete unless the inquiry became a customer contract or a hold applies |
| Application and access logs | 30 days | Delete automatically; retain a restricted incident extract only when a documented hold applies |
| Database and media backups | 35 rolling days | Provider expiry must permanently remove the expired backup or version |
| Newsletter subscription data | Until unsubscribe or 24 months without engagement, whichever occurs first | Stop marketing immediately; remove profile data within 30 days and retain only the minimum suppression/consent evidence for 3 years |
| Superseded product media versions | 90 days | Permanently delete unless still referenced or held for an active incident |

Sources used for the initial policy are the [Thai Revenue Department's record-retention
guidance](https://www.rd.go.th/28312.html) and the [Thai PDPC government platform's
privacy guidance](https://gppc.pdpc.or.th/privacy-policy/), which describes deletion or
anonymization when personal data is no longer necessary. These sources do not replace
professional advice about BeanCo's exact tax registrations and processing activities.

## Operating rules

- Collect only fields required for fulfillment, payment linkage, communication consent,
  security, and accounting obligations.
- Never store raw card data or full Stripe event payloads.
- Restrict production/admin access by role and review it periodically.
- Keep logs query/body-free and ensure error reporting scrubs credentials and personal
  data before transmission.
- Pause deletion for an approved legal, fraud, dispute, or security hold and record the
  owner and reason.
- Verify backups expire consistently with this policy; deleting the primary row
  alone does not complete erasure.

## Access, correction, and deletion requests

1. Authenticate the requester without requesting unnecessary identity documents.
2. Record scope and deadline in the approved private case system
   (`TBD-before-launch`).
3. Export or correct only records linked to the verified customer.
4. Before deletion, separate legally required order/payment records from optional profile,
   address, newsletter, and inquiry data.
5. Execute an approved, reviewed procedure; never improvise deletion in Django Admin.
6. Verify results in the primary database, connected providers, and backup-expiry queue.
7. Respond through the approved channel without attaching unrelated customer data.
