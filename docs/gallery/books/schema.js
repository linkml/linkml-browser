window.searchSchema = {
  "title": "Books Browser",
  "description": "Browse and filter classic literature",
  "searchPlaceholder": "Search...",
  "searchableFields": [
    "publisher",
    "language",
    "author",
    "description",
    "id",
    "title",
    "genre"
  ],
  "facets": [
    {
      "field": "publisher",
      "label": "Publisher",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "language",
      "label": "Language",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "pages",
      "label": "Pages",
      "type": "integer",
      "sortBy": "count"
    },
    {
      "field": "rating",
      "label": "Rating",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "publication_year",
      "label": "Publication Year",
      "type": "integer",
      "sortBy": "count"
    },
    {
      "field": "author",
      "label": "Author",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "description",
      "label": "Description",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "id",
      "label": "Id",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "title",
      "label": "Title",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "genre",
      "label": "Genre",
      "type": "array",
      "sortBy": "count"
    }
  ],
  "displayFields": [
    {
      "field": "author",
      "label": "Author",
      "type": "string"
    },
    {
      "field": "description",
      "label": "Description",
      "type": "string"
    },
    {
      "field": "genre",
      "label": "Genre",
      "type": "array"
    },
    {
      "field": "id",
      "label": "Id",
      "type": "string"
    },
    {
      "field": "language",
      "label": "Language",
      "type": "string"
    },
    {
      "field": "pages",
      "label": "Pages",
      "type": "string"
    },
    {
      "field": "publication_year",
      "label": "Publication Year",
      "type": "string"
    },
    {
      "field": "publisher",
      "label": "Publisher",
      "type": "string"
    },
    {
      "field": "rating",
      "label": "Rating",
      "type": "string"
    },
    {
      "field": "title",
      "label": "Title",
      "type": "string"
    }
  ]
};
window.dispatchEvent(new Event('searchDataReady'));
