window.searchSchema = {
  "title": "Palmer Penguins",
  "description": "Classic dataset of penguin measurements from Palmer Station, Antarctica",
  "searchPlaceholder": "Search penguins...",
  "searchableFields": ["id", "species", "island", "sex"],
  "facets": [
    {
      "field": "species",
      "label": "Species",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "island",
      "label": "Island",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "sex",
      "label": "Sex",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "year",
      "label": "Year",
      "type": "string",
      "sortBy": "alphabetical"
    },
    {
      "field": "body_mass_g",
      "label": "Body Mass (g)",
      "type": "integer",
      "sortBy": "count"
    },
    {
      "field": "flipper_length_mm",
      "label": "Flipper Length (mm)",
      "type": "integer",
      "sortBy": "count"
    },
    {
      "field": "bill_length_mm",
      "label": "Bill Length (mm)",
      "type": "integer",
      "sortBy": "count"
    },
    {
      "field": "bill_depth_mm",
      "label": "Bill Depth (mm)",
      "type": "integer",
      "sortBy": "count"
    }
  ],
  "displayFields": [
    {"field": "id", "label": "ID", "type": "string"},
    {"field": "species", "label": "Species", "type": "string"},
    {"field": "island", "label": "Island", "type": "string"},
    {"field": "sex", "label": "Sex", "type": "string"},
    {"field": "year", "label": "Year", "type": "string"},
    {"field": "bill_length_mm", "label": "Bill Length (mm)", "type": "string"},
    {"field": "bill_depth_mm", "label": "Bill Depth (mm)", "type": "string"},
    {"field": "flipper_length_mm", "label": "Flipper Length (mm)", "type": "string"},
    {"field": "body_mass_g", "label": "Body Mass (g)", "type": "string"}
  ]
};
window.dispatchEvent(new Event('searchDataReady'));
