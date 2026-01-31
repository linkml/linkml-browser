window.searchSchema = {
  "title": "Sentiment Analysis Review",
  "description": "Review sentiment predictions with thumbs-up/down decisions",
  "searchPlaceholder": "Search text, labels, or domains...",
  "recordIdField": "id",
  "itemsPerPage": 50,
  "facetItemsToShow": 12,
  "customCss": ".results-grid { grid-template-columns: 1fr; }",
  "searchableFields": [
    "text",
    "predicted_label",
    "source_domain",
    "language",
    "model_version"
  ],
  "facets": [
    {
      "field": "predicted_label",
      "label": "Predicted Label",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "confidence_score",
      "label": "Confidence",
      "type": "integer"
    },
    {
      "field": "source_domain",
      "label": "Source",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "language",
      "label": "Language",
      "type": "string",
      "sortBy": "alphabetical"
    },
    {
      "field": "model_version",
      "label": "Model Version",
      "type": "string",
      "sortBy": "alphabetical"
    }
  ],
  "displayFields": [
    {
      "field": "text",
      "label": "Text",
      "type": "string",
      "primary": true
    },
    {
      "field": "predicted_label",
      "label": "Predicted",
      "type": "string",
      "decorators": [
        {
          "type": "thumbs",
          "field": "review_decision"
        }
      ]
    },
    {
      "field": "confidence_score",
      "label": "Confidence (0-100)",
      "type": "integer"
    },
    {
      "field": "model_version",
      "label": "Model",
      "type": "string"
    },
    {
      "field": "source_domain",
      "label": "Source",
      "type": "string"
    },
    {
      "field": "language",
      "label": "Lang",
      "type": "string"
    }
  ],
  "curationFields": [
    {
      "field": "review_notes",
      "label": "Reviewer Notes",
      "type": "textarea"
    }
  ],
  "curation": {
    "layout": "inline",
    "statusFacetLabel": "Evaluation Status",
    "sections": [
      {
        "label": "Notes",
        "fields": [
          "review_notes"
        ]
      }
    ]
  }
};
window.dispatchEvent(new Event('searchSchemaReady'));