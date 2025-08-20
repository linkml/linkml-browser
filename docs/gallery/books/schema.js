const schema = {
  "title": "Book Catalog Browser",
  "description": "Browse and search through a curated collection of influential books across various genres",
  "searchPlaceholder": "Search by title, author, or description...",
  "searchableFields": ["title", "author", "description"],
  "facets": [
    {
      "field": "genre",
      "label": "Genre",
      "type": "array",
      "sortBy": "count"
    },
    {
      "field": "language",
      "label": "Language",
      "type": "string",
      "sortBy": "alphabetical"
    },
    {
      "field": "publicationYear",
      "label": "Publication Year",
      "type": "integer"
    },
    {
      "field": "rating",
      "label": "Rating",
      "type": "integer"
    }
  ],
  "displayFields": [
    {
      "field": "title",
      "label": "Title",
      "type": "string"
    },
    {
      "field": "author",
      "label": "Author",
      "type": "string"
    },
    {
      "field": "publicationYear",
      "label": "Year",
      "type": "integer"
    },
    {
      "field": "genre",
      "label": "Genres",
      "type": "array"
    },
    {
      "field": "publisher",
      "label": "Publisher",
      "type": "string"
    },
    {
      "field": "pages",
      "label": "Pages",
      "type": "integer"
    },
    {
      "field": "rating",
      "label": "Rating",
      "type": "number"
    },
    {
      "field": "language",
      "label": "Original Language",
      "type": "string"
    },
    {
      "field": "description",
      "label": "Description",
      "type": "string"
    }
  ]
};

window.searchSchema = schema;