window.searchSchema = {
  "title": "Cell Ontology Browser",
  "description": "Browse cell types from the Cell Ontology (CL)",
  "searchPlaceholder": "Search...",
  "searchableFields": [
    "label",
    "definition",
    "subsets",
    "synonyms",
    "xrefs",
    "id"
  ],
  "facets": [
    {
      "field": "obsolete",
      "label": "Obsolete",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "definition",
      "label": "Definition",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "subsets",
      "label": "Subsets",
      "type": "array",
      "sortBy": "count"
    }
  ],
  "displayFields": [
    {
      "field": "definition",
      "label": "Definition",
      "type": "string"
    },
    {
      "field": "id",
      "label": "Id",
      "type": "string"
    },
    {
      "field": "label",
      "label": "Label",
      "type": "string"
    },
    {
      "field": "obsolete",
      "label": "Obsolete",
      "type": "string"
    },
    {
      "field": "subsets",
      "label": "Subsets",
      "type": "array"
    },
    {
      "field": "synonyms",
      "label": "Synonyms",
      "type": "array"
    },
    {
      "field": "xrefs",
      "label": "Xrefs",
      "type": "array"
    }
  ]
};
window.dispatchEvent(new Event('searchDataReady'));
