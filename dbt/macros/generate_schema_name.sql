{% macro generate_schema_name(custom_schema_name, node) -%}
    {#
      Custom schema name generation for CEGR.
      - If custom_schema_name is set (via +schema in dbt_project.yml), use it directly
        prefixed with the target schema (e.g., cegr_staging_staging).
      - For simplicity, we override to always use the target schema (cegr_staging)
        since all models are views and we want a flat schema.
    #}
    {{ target.schema }}
{%- endmacro %}
