{{
    config(
        materialized='view',
        tags=['staging', 'person']
    )
}}

-- Staging model for appointment_event (S2.1-full, per docs/36 §2.5).
-- Append-only event log; 纠错走 observation_revision 模式 (docs/36 §2.5).

SELECT
    ae.id                       AS event_id,
    ae.tenure_id,
    ae.event_type,
    ae.event_date,
    ae.document_url,
    ae.source_id,
    ae.person_id,
    ae.position_id,
    ae.geo_entity_id,
    ae.announcement_doc_id,
    ae.created_at
FROM {{ source('cegr', 'appointment_event') }} ae
