console.log("Loading BOOKS data");
const data = [
  {
    "id": "978-0-06-112008-4",
    "title": "To Kill a Mockingbird",
    "author": "Harper Lee",
    "publicationYear": 1960,
    "genre": ["Fiction", "Classic", "Historical Fiction"],
    "publisher": "J. B. Lippincott & Co.",
    "pages": 281,
    "rating": 4.8,
    "language": "English",
    "description": "A gripping portrayal of racial injustice and childhood innocence in the American South."
  },
  {
    "id": "978-0-452-28423-4",
    "title": "1984",
    "author": "George Orwell",
    "publicationYear": 1949,
    "genre": ["Fiction", "Dystopian", "Science Fiction", "Classic"],
    "publisher": "Secker & Warburg",
    "pages": 328,
    "rating": 4.7,
    "language": "English",
    "description": "A dystopian social science fiction novel and cautionary tale about totalitarianism."
  },
  {
    "id": "978-0-7432-7356-5",
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "publicationYear": 1925,
    "genre": ["Fiction", "Classic", "Romance"],
    "publisher": "Charles Scribner's Sons",
    "pages": 180,
    "rating": 4.5,
    "language": "English",
    "description": "A tragic story of Jay Gatsby's pursuit of the American Dream in Jazz Age New York."
  },
  {
    "id": "978-0-14-017739-8",
    "title": "One Hundred Years of Solitude",
    "author": "Gabriel García Márquez",
    "publicationYear": 1967,
    "genre": ["Fiction", "Magical Realism", "Classic"],
    "publisher": "Editorial Sudamericana",
    "pages": 417,
    "rating": 4.9,
    "language": "Spanish",
    "description": "A multi-generational story of the Buendía family in the mythical town of Macondo."
  },
  {
    "id": "978-0-385-33084-9",
    "title": "Beloved",
    "author": "Toni Morrison",
    "publicationYear": 1987,
    "genre": ["Fiction", "Historical Fiction", "Gothic"],
    "publisher": "Alfred A. Knopf",
    "pages": 324,
    "rating": 4.6,
    "language": "English",
    "description": "A powerful exploration of the trauma of slavery and its lasting effects."
  },
  {
    "id": "978-0-679-72276-1",
    "title": "The Stranger",
    "author": "Albert Camus",
    "publicationYear": 1942,
    "genre": ["Fiction", "Philosophical Fiction", "Classic"],
    "publisher": "Gallimard",
    "pages": 123,
    "rating": 4.4,
    "language": "French",
    "description": "An existentialist novel exploring themes of absurdity and alienation."
  },
  {
    "id": "978-0-553-21311-7",
    "title": "Dune",
    "author": "Frank Herbert",
    "publicationYear": 1965,
    "genre": ["Science Fiction", "Adventure", "Epic"],
    "publisher": "Chilton Books",
    "pages": 688,
    "rating": 4.8,
    "language": "English",
    "description": "An epic science fiction novel set on the desert planet Arrakis."
  },
  {
    "id": "978-0-439-13959-3",
    "title": "Harry Potter and the Philosopher's Stone",
    "author": "J.K. Rowling",
    "publicationYear": 1997,
    "genre": ["Fantasy", "Young Adult", "Adventure"],
    "publisher": "Bloomsbury",
    "pages": 223,
    "rating": 4.9,
    "language": "English",
    "description": "The first book in the magical Harry Potter series."
  },
  {
    "id": "978-0-307-27778-7",
    "title": "The Girl with the Dragon Tattoo",
    "author": "Stieg Larsson",
    "publicationYear": 2005,
    "genre": ["Mystery", "Thriller", "Crime"],
    "publisher": "Norstedts Förlag",
    "pages": 672,
    "rating": 4.5,
    "language": "Swedish",
    "description": "A gripping thriller combining murder mystery, family saga, and financial intrigue."
  },
  {
    "id": "978-1-101-90622-0",
    "title": "The Martian",
    "author": "Andy Weir",
    "publicationYear": 2014,
    "genre": ["Science Fiction", "Thriller", "Adventure"],
    "publisher": "Crown Publishing Group",
    "pages": 369,
    "rating": 4.7,
    "language": "English",
    "description": "A thrilling survival story of an astronaut stranded on Mars."
  },
  {
    "id": "978-0-385-53785-8",
    "title": "Where the Crawdads Sing",
    "author": "Delia Owens",
    "publicationYear": 2018,
    "genre": ["Fiction", "Mystery", "Romance"],
    "publisher": "G.P. Putnam's Sons",
    "pages": 368,
    "rating": 4.6,
    "language": "English",
    "description": "A coming-of-age murder mystery set in the marshes of North Carolina."
  },
  {
    "id": "978-0-06-231611-0",
    "title": "Sapiens: A Brief History of Humankind",
    "author": "Yuval Noah Harari",
    "publicationYear": 2011,
    "genre": ["Non-fiction", "History", "Science"],
    "publisher": "Harvill Secker",
    "pages": 443,
    "rating": 4.8,
    "language": "Hebrew",
    "description": "A sweeping narrative of human history from the Stone Age to the modern era."
  }
];

window.searchData = data;