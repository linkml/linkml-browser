window.searchSchema = {
  "title": "MIxS Schema Browser",
  "description": "Browse LinkML schema elements",
  "searchPlaceholder": "Search elements...",
  "searchableFields": [
    "name",
    "title",
    "description",
    "aliases",
    "comments",
    "keywords",
    "permissible_values"
  ],
  "facets": [
    {
      "field": "type",
      "label": "Element Type",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "in_subset",
      "label": "Subset",
      "type": "array",
      "sortBy": "count"
    },
    {
      "field": "classes",
      "label": "Used By Class",
      "type": "array",
      "sortBy": "count"
    },
    {
      "field": "slots",
      "label": "Used By Slot",
      "type": "array",
      "sortBy": "count"
    },
    {
      "field": "range",
      "label": "Range",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "is_a",
      "label": "Parent",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "required",
      "label": "Required",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "multivalued",
      "label": "Multivalued",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "abstract",
      "label": "Abstract",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "mixin",
      "label": "Mixin",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "deprecated",
      "label": "Deprecated",
      "type": "string",
      "sortBy": "count"
    }
  ],
  "displayFields": [
    {
      "field": "name",
      "label": "Name",
      "type": "string"
    },
    {
      "field": "title",
      "label": "Title",
      "type": "string"
    },
    {
      "field": "description",
      "label": "Description",
      "type": "string"
    },
    {
      "field": "type",
      "label": "Type",
      "type": "string"
    },
    {
      "field": "range",
      "label": "Range",
      "type": "string"
    },
    {
      "field": "is_a",
      "label": "Parent",
      "type": "string"
    },
    {
      "field": "url",
      "label": "URI",
      "type": "url"
    },
    {
      "field": "classes",
      "label": "Used By",
      "type": "array"
    },
    {
      "field": "slots",
      "label": "Slots",
      "type": "array"
    },
    {
      "field": "mixins",
      "label": "Mixins",
      "type": "array"
    },
    {
      "field": "permissible_values",
      "label": "Values",
      "type": "array"
    },
    {
      "field": "in_subset",
      "label": "Subsets",
      "type": "array"
    },
    {
      "field": "aliases",
      "label": "Aliases",
      "type": "array"
    },
    {
      "field": "keywords",
      "label": "Keywords",
      "type": "array"
    },
    {
      "field": "mappings",
      "label": "Mappings",
      "type": "array"
    }
  ]
};
window.dispatchEvent(new Event('searchDataReady'));
