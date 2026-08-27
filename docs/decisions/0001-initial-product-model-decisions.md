# ADR 0001: Initial product-model decisions

- Status: accepted
- Date: 2026-08-25

## Context and constraints

Phase 1 must create a backend data model without guessing later commercial rules.
The owner approved the Phase 0 recommendations in
[`../phase-0-implementation.md`](../phase-0-implementation.md).

## Decision

- Launch the public site as a catalog and partnership-inquiry experience; retail
  checkout is deferred.
- Display retail catalog prices in THB. Wholesale pricing is quote-only and is not
  publicly displayed.
- Launch in Thailand only.
- Model coffee variants with 250 g, 500 g, and 1 kg weights and whole-bean,
  espresso, or filter grind options where the product supports them.
- Track stock per purchasable variant. Do not offer backorders or preorders at
  launch.
- Treat B2B requests as staff-managed inquiries. Minimum quantities and
  account-specific pricing are not modeled until the B2B workflow is approved.
- Retail tax, delivery charges, shipping origin, delivery area, and refund terms
  do not apply to the catalog/inquiry launch. B2B terms are quoted by staff. These
  commercial rules must be finalized before Phase 4 checkout work begins.

## Alternatives considered

- Launch checkout alongside the catalog.
- Publish wholesale prices or model company-specific price lists immediately.
- Allow backorders, preorders, or sales outside Thailand.

## Consequences and follow-up work

Phase 1 can safely introduce catalog, variant, and inventory foundations. Phase 2
will collect partnership requirements but will not calculate quotes. Phase 4 must
not start until tax, shipping, delivery, and refund rules have been approved.
