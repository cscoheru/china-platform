{% macro generate_schema_name(custom_schema_name, node) -%}
    {#
      CEGR custom schema name resolution (knife 664 update).

      Routes:
        - 'mart' models       → cegr_mart      (P2 mart, knife 663/665/666/669)
        - 'staging' models    → cegr_staging   (P1 legacy)
        - 'intermediate'      → cegr_staging   (P1 legacy)
        - no custom_schema    → target.schema  (target-specific override)

      Previous behavior (pre-664): all models forced into target.schema, ignoring
      +schema: mart / +schema: staging. This caused P2 mart_province_timeseries to
      land in cegr_staging instead of cegr_mart, breaking the 663 mart schema
      contract (mart must live in cegr_mart per docs/87 §3.2).

      Now: mart models route to cegr_mart (so knife 664+ FastAPI endpoints and
      future data tools query the correct schema). Existing staging/intermediate
      models continue to land in cegr_staging (P1 backward compat).

      Note: cegr_mart schema is created by P1 bootstrap; if missing, run
      `CREATE SCHEMA IF NOT EXISTS cegr_mart` before first dbt run.
    #}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- elif custom_schema_name == 'mart' -%}
        cegr_mart
    {%- else -%}
        cegr_{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}